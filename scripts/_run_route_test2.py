#!/usr/bin/env python3
"""Test routing on server with correct venv"""
import paramiko

HOST = "47.101.68.210"
PORT = 22
USER = "root"
PASSWORD = "jovial888@"

TEST_SCRIPT = """
cd ~/SpatialMind && ~/SpatialMind/venv/bin/python -c "
import sys
sys.path.insert(0, '/root/SpatialMind')
from agent.graph import app

base = {
    'session_id': 'route-p0',
    'data_path': '',
    'data_type': 'unknown',
    'adata_cache_key': 'session_route_p0',
    'analysis_plan': [],
    'current_step': '',
    'completed_steps': [],
    'step_params': {},
    'figures': {},
    'step_results': {},
    'explanations': {},
    'skill_outputs': {},
    'error_message': None,
    'retry_count': 0,
    'max_retries': 2,
    'is_complete': False,
    'request_type': 'unknown',
    'messages': [],
}

def run(text, idx):
    s = dict(base)
    s['user_input'] = text
    r = app.invoke(s, config={'configurable': {'thread_id': 'route-p0-'+str(idx)}})
    print('='*60)
    print(text)
    print('request_type:', r.get('request_type'))
    print('analysis_plan:', r.get('analysis_plan'))
    print('is_complete:', r.get('is_complete'))
    msgs = [m for m in r.get('messages', []) if m.get('role') == 'assistant']
    print('assistant:', msgs[-1]['content'][:120] if msgs else '')

run('什么是转录组？', 1)
run('什么是空间转录组？', 2)
run('执行完整分析', 3)
print('DONE')
"
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, PORT, USER, PASSWORD, timeout=15)

stdin, stdout, stderr = client.exec_command(TEST_SCRIPT, timeout=120)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode("utf-8", errors="replace").strip()
err = stderr.read().decode("utf-8", errors="replace").strip()

print(out)
if err:
    print("STDERR:", err[:500])
print("Exit:", exit_code)
client.close()
