import requests

tokens = ['tTTo-nPpEN-Q', 'tehRbiDVYam3']

for token in tokens:
    try:
        r = requests.get(f'http://localhost:3000/api/data?token={token}')
        print(f"\n{token}:")
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            project = data.get('project', {})
            runs = data.get('runs', [])
            print(f"  Project: {project.get('token')}")
            print(f"  Runs: {len(runs)}")
            for idx, run in enumerate(runs):
                rc = run.get('records_count', 0)
                dr = len(run.get('data', []))
                print(f"    Run {idx}: {rc} total records, {dr} displayed")
                if dr > 0:
                    sample = run['data'][0]
                    print(f"      Sample: {sample['key']} = {sample['value'][:100]}...")
    except Exception as e:
        print(f"{token}: Error - {e}")
