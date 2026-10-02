"""Bounded, read-only tool agent with an injectable model client."""
import json
from agent_local import INSTRUCTIONS, TOOLS, execute_tool

def run_agent(question, branch, report_date, request_model):
    if not question.strip() or len(question) > 1200:
        raise ValueError('Enter a question of 1–1200 characters.')
    messages = [{'role':'system','content':INSTRUCTIONS + '\nUse the selected branch and report date unless the question explicitly specifies another scope.'},
                {'role':'user','content':f'Selected branch: {branch}. Report date: {report_date}. Question: {question}'}]
    trace=[]
    for _ in range(5):
        message=request_model(messages)
        messages.append(message)
        calls=message.get('tool_calls') or []
        if not calls:
            if not trace or any('error' in item['result'] for item in trace):
                raise RuntimeError('No verified answer: tools were not successfully completed.')
            answer=message.get('content') or ''
            if not answer.strip(): raise RuntimeError('Model returned an empty answer.')
            return answer,trace
        for call in calls:
            if len(trace)>=5: raise RuntimeError('Tool-call limit reached.')
            fn=call['function']
            try: arguments=json.loads(fn['arguments']) if isinstance(fn['arguments'],str) else fn['arguments']
            except (ValueError,TypeError): arguments=None
            result=execute_tool(fn['name'],arguments)
            trace.append({'tool':fn['name'],'arguments':arguments,'result':result})
            messages.append({'role':'tool','tool_call_id':call['id'],'content':json.dumps(result)})
    raise RuntimeError('Model request limit reached.')
