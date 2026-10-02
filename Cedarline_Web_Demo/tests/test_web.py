import sys,unittest
from pathlib import Path
from datetime import date
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from web_agent import run_agent
from tools import get_job_margin_report,get_overdue_invoices
from streamlit.testing.v1 import AppTest
class DemoTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  from build_database import main as build
  from load_invoices import main as load
  build();load()
 def test_dashboard(self):
  at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'streamlit_app.py')).run();self.assertFalse(at.exception)
  self.assertEqual(at.metric[0].value,'$8,500.00')
  at.sidebar.selectbox[0].set_value('North').run();self.assertFalse(at.exception);self.assertNotEqual(at.metric[0].value,'$8,500.00')
  at.date_input[0].set_value(date(2020,1,1)).run();self.assertEqual(at.metric[3].value,'$0.00')
 def test_evidence(self):
  r=get_job_margin_report();self.assertEqual(r['gross_profit_cents'],350000);self.assertEqual(r['gross_margin_percent'],41.18);self.assertEqual(len(r['incomplete_jobs']),1)
  self.assertEqual(get_overdue_invoices('2026-10-02')['overdue_invoice_count'],1)
 def test_orchestration(self):
  replies=iter([{'role':'assistant','tool_calls':[{'id':'a','type':'function','function':{'name':'get_job_margin_report','arguments':'{"branch_id":"All"}'}}]}, {'role':'assistant','content':'Mock answer'}])
  _,trace=run_agent('Margins','All','2026-10-02',lambda _:next(replies));self.assertEqual(trace[0]['result']['revenue_cents'],850000)
 def test_reject_unsupported(self):
  with self.assertRaises(RuntimeError):run_agent('Review','All','2026-10-02',lambda _: {'role':'assistant','content':'unsupported'})
 def test_reject_bad_arguments(self):
  replies=iter([{'role':'assistant','tool_calls':[{'id':'a','type':'function','function':{'name':'get_overdue_invoices','arguments':'{"as_of_date":"bad"}'}}]}, {'role':'assistant','content':'unsupported'}])
  with self.assertRaises(RuntimeError):run_agent('Review','All','2026-10-02',lambda _:next(replies))
