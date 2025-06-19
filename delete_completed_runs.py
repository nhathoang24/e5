# scripts/delete_completed_runs.py
import os
import http.client
import json

token = os.getenv('GITHUB_TOKEN')
repo = os.getenv('GITHUB_REPOSITORY')
headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'workflow-cleaner'
}

def request(method, url):
    conn = http.client.HTTPSConnection('api.github.com')
    conn.request(method, url, headers=headers)
    resp = conn.getresponse()
    data = resp.read()
    conn.close()
    return json.loads(data.decode()) if data else {}

runs = request('GET', f'/repos/{repo}/actions/runs?per_page=10').get('workflow_runs', [])
for run in runs:
    if run['status'] == 'completed' and run['conclusion'] == 'success':
        run_id = run['id']
        print(f'🗑️ Deleting run {run_id}...')
        request('DELETE', f'/repos/{repo}/actions/runs/{run_id}')
