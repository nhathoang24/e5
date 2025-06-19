# scripts/delete_completed_runs.py
import os
import http.client
import json

token = os.getenv('GITHUB_TOKEN')
repo = os.getenv('GITHUB_REPOSITORY')

headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'gh-actions-cleaner'
}

def request(method, url):
    conn = http.client.HTTPSConnection('api.github.com')
    conn.request(method, url, headers=headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return json.loads(data.decode()) if data else {}

def delete_workflow_run(run_id):
    del_url = f'/repos/{repo}/actions/runs/{run_id}'
    conn = http.client.HTTPSConnection('api.github.com')
    conn.request('DELETE', del_url, headers=headers)
    res = conn.getresponse()
    print(f"🗑️ Deleting run {run_id} → {res.status} {res.reason}")
    conn.close()

def get_all_completed_runs():
    runs = []
    page = 1
    while True:
        url = f'/repos/{repo}/actions/runs?per_page=100&page={page}'
        data = request('GET', url).get('workflow_runs', [])
        if not data:
            break
        for run in data:
            if run['status'] == 'completed':
                runs.append(run)
        page += 1
    return runs

def main():
    completed_runs = get_all_completed_runs()
    print(f"🔎 Found {len(completed_runs)} completed runs")

    # Sort theo ngày mới nhất → cũ nhất
    completed_runs.sort(key=lambda r: r['created_at'], reverse=True)

    # Giữ lại 5 cái mới nhất
    keep_latest = 5
    runs_to_delete = completed_runs[keep_latest:]

    print(f"📌 Keeping {keep_latest}, deleting {len(runs_to_delete)} old runs...")
    for run in runs_to_delete:
        run_id = run['id']
        print(f"⏳ Run #{run_id} ({run['conclusion']}) @ {run['created_at']}")
        delete_workflow_run(run_id)

if __name__ == "__main__":
    main()
