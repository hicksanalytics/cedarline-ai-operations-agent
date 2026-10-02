import os
import sys
import time
import threading
from pathlib import Path
from datetime import date
import streamlit as st

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from build_database import main as build
from load_invoices import main as load
from tools import get_job_margin_report, get_overdue_invoices
from web_agent import run_agent
from agent_local import TOOLS

st.set_page_config(page_title='Cedarline | Hicks Analytics',page_icon='🌿',layout='wide')
@st.cache_resource
def initialize():
    build();load()
    return {'lock':threading.Lock(),'count':0,'window':time.monotonic()}
budget=initialize()
def setting(name,default=''):
    try:return st.secrets.get(name,os.getenv(name,default))
    except st.errors.StreamlitSecretNotFoundError:return os.getenv(name,default)
def money(cents):return f'${cents/100:,.2f}'

st.caption('HICKS ANALYTICS  /  AI OPERATIONS DEMO')
st.title('Meet Cedarline’s operations analyst')
st.write('Explore job profitability and collection priorities, then ask an AI analyst to investigate the evidence.')
st.info('Fictional HVAC business • Synthetic training data • Read-only demonstration')
with st.sidebar:
    st.header('Explore the business')
    branch=st.selectbox('Profitability branch',['All','North','East','South'])
    report_date=st.date_input('Collections report date',date(2026,10,2))
    st.caption('Branch selection filters profitability. Collections cover all branches. Invoice balances are current sample balances; historical payment timing is unavailable.')
    st.link_button('Hicks Analytics','https://hicksanalytics.com')
    st.link_button('View project on GitHub','https://github.com/hicksanalytics/cedarline-ai-operations-agent')
margins=get_job_margin_report(None if branch=='All' else branch)
invoices=get_overdue_invoices(report_date.isoformat())
cols=st.columns(4)
for col,label,value in zip(cols,['Completed-job revenue','Gross profit','Gross margin','Overdue balance'],[money(margins['revenue_cents']),money(margins['gross_profit_cents']),f"{margins['gross_margin_percent']}%" if margins['gross_margin_percent'] is not None else 'N/A',money(invoices['total_overdue_balance_cents'])]):col.metric(label,value)
st.caption('Gross margin includes labor and materials, excludes overhead, and has no approved company-wide target. The 30% threshold applies to individual job review.')
analysis,evidence,about=st.tabs(['Ask the analyst','Business evidence','About this project'])
with analysis:
    api_key=setting('AI_API_KEY');model=setting('AI_MODEL');base_url=setting('AI_BASE_URL')
    enabled=bool(api_key and model and base_url)
    if not enabled:st.warning('Live AI is awaiting model configuration. The business dashboard and evidence are fully interactive; no AI answer is simulated.')
    sample=st.selectbox('Try a business question',['Review profitability and overdue invoices. Link any shared job IDs and disclose missing data.','Which completed jobs need margin investigation?','Which invoices are overdue, and how much is outstanding?'])
    with st.form('ask'):
        question=st.text_area('Your question',sample,max_chars=1200)
        submitted=st.form_submit_button('Ask Cedarline',disabled=not enabled)
    if submitted:
        with budget['lock']:
            if time.monotonic()-budget['window']>3600:budget.update(count=0,window=time.monotonic())
            allowed=budget['count']<20 and st.session_state.get('requests',0)<5
            if allowed:budget['count']+=1;st.session_state['requests']=st.session_state.get('requests',0)+1
        if not allowed:st.error('Demo request limit reached. Please explore the business evidence.')
        else:
            try:
                from openai import OpenAI
                client=OpenAI(api_key=api_key,base_url=base_url,timeout=30,max_retries=0)
                def request(messages):
                    return client.chat.completions.create(model=model,messages=messages,tools=TOOLS,max_tokens=1000).choices[0].message.model_dump(exclude_none=True)
                with st.spinner('Querying business tools…'):
                    answer,trace=run_agent(question,branch,report_date.isoformat(),request)
                st.session_state['result']=(question,branch,report_date.isoformat(),answer,trace)
            except Exception:
                st.error('The analyst could not complete a verified response. Check the evidence tab or try again later.')
    if 'result' in st.session_state:
        q,b,d,a,t=st.session_state['result']
        st.caption(f'Last answer • profitability branch {b} • report date {d}')
        st.write(q);st.markdown(a)
        st.caption('AI-generated interpretation. Verify the figures against the tool evidence below.')
        with st.expander('Inspect tool calls and source results'):st.json(t)
with evidence:
    st.subheader('Jobs requiring investigation')
    if margins['margin_investigations']:st.dataframe(margins['margin_investigations'],hide_index=True)
    else:st.write('No job investigation flags in this selection.')
    st.subheader('Missing financial data')
    if margins['incomplete_jobs']:st.dataframe(margins['incomplete_jobs'],hide_index=True)
    else:st.write('No incomplete completed jobs in this selection.')
    st.subheader('Overdue invoices — all branches')
    if invoices['invoices']:st.dataframe(invoices['invoices'],hide_index=True)
    else:st.write('No overdue invoices for this report date.')
    st.caption('Money fields in source tables are integer cents. An invoice is overdue when due before the report date with a positive unpaid balance.')
    with st.expander('Full calculation evidence'):st.json({'profitability':margins,'collections':invoices})
with about:
    st.write('Built by Ben Hicks, Hicks Analytics. Python and SQLite calculate financial facts; the model chooses approved read-only tools and interprets results. The web interface exposes the evidence.')
    st.write('Demonstrated skills: SQL modeling, integer-cents calculations, tool calling, argument validation, missing-data handling, and transparent AI workflows.')
    st.write('Limitations: small fictional dataset; no overhead or payment history; no causal analysis; no customer contact details; no record updates or message sending. AI explanations can be wrong.')
    st.write('Request caps: five questions per session and twenty per hour per running server. These are demo controls, not durable billing controls; configure provider-side quotas before public launch.')
