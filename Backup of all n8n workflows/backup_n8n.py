import json
import os
import re
import concurrent.futures
import urllib.request

# Config
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4NjFmYjY1NS1iMTc2LTRkNjMtYTRlZC0zY2M2NmUyNzk2NDIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiM2IwNmJhMDMtY2U4NS00NDhmLWJhMWEtYzQwZTJkZDUxMDAxIiwiaWF0IjoxNzc2MzMzMzIxLCJleHAiOjE3ODQwOTg4MDB9.-3ukTjTeQgZgag24KkbBlqDqlvw0d9fH-2v3_VtgMlc"
BASE_URL = "https://automations.livetransparent.com"
BACKUP_DIR = r"C:\Users\edmon\OneDrive\Documents\Projects\LiveTransparent\Backup of all n8n workflows"

WORKFLOW_IDS = [
    "T28iLcm4Hszo19MG", "kVCTmy1m8fEyP6Q7", "8USvJkRlKzbj6Fu1", "FQE90HDUilFVdASY", "5nYzp9DgQUopzWhR",
    "6lp8sIS3YMB1t9Ri", "J4B0n0QeSeOeqAci", "OowP3sAd8c9paSKf", "SmMf8QIfysuxQJbG", "RSfLF7LU0rDC4jAI",
    "RTV5jUiTt05lad07", "U7c6byTLXAMgcS75", "WmKAhG7mIaXonNsh", "WuxgTa0EEL1mb2SA", "YaWizRnw7XmkcvZH",
    "3kjsIUeoEQFx26cC", "MI91SutAbAj3QSXp", "NTpQnMrpjzusPXHX", "lQTW0QPwBcf3o7j8", "AEi1VCzkLvaYFr4U",
    "IyBKMkpYQ7pa0C8V", "GHVYyYmhfNiZ7bbN", "WYyZ7HoZWnCcQDYN", "XiOTlG36vmOTnL01", "p1RkRjjPMoVhSz0I",
    "dMDbLSzPSSrHo1wK", "Bukc0mgOD2r7V6ED", "EUeOiRttoVLQ9zF9", "3XHThUiUSNa4sTb9", "Y0TU7Il71JswxOBp",
    "aYT5oHcgmBALzHy5", "gwaEpWDpTIwsafi8", "M5mXcDTFSko6EdHb", "osIJOgBmWITF5Yuv", "8UXlpoMJnQ229AuG",
    "EhAiGey2o7UJT1cv", "Zt8p2aYtIuY0HK18", "Q3Ivnwe4z2Y3cD7A", "aomO3Z4AXJIgEvvN", "3gXztCnBEN6sGINb"
]

os.makedirs(BACKUP_DIR, exist_ok=True)

def sanitize_filename(name):
    return re.sub(r'[^\w\-\.]', '_', name)

def backup_workflow(wid):
    url = f"{BASE_URL}/api/v1/workflows/{wid}"
    req = urllib.request.Request(url, headers={
        "X-N8N-API-KEY": API_KEY,
        "Accept": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return (wid, False, str(e))
    
    # Public API returns workflow directly; MCP returns it nested under 'workflow'
    workflow = data.get("workflow") if isinstance(data.get("workflow"), dict) else data
    
    if not workflow:
        return (wid, False, "No workflow data in response")
    
    if not workflow.get("active", False):
        return (wid, False, "Workflow is not active")
    if workflow.get("isArchived", False):
        return (wid, False, "Workflow is archived")
    
    name = workflow.get("name", "unnamed")
    safe_name = sanitize_filename(name)
    filename = f"{wid}__{safe_name}.json"
    filepath = os.path.join(BACKUP_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)
    
    return (wid, True, filename)

def main():
    backed_up = []
    errors = []
    
    for i in range(0, len(WORKFLOW_IDS), 10):
        batch = WORKFLOW_IDS[i:i+10]
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            batch_results = list(executor.map(backup_workflow, batch))
        
        for wid, success, detail in batch_results:
            if success:
                backed_up.append(detail)
            else:
                errors.append(f"{wid}: {detail}")
    
    print(f"BACKUP_COMPLETE")
    print(f"TOTAL_BACKED_UP:{len(backed_up)}")
    print(f"TOTAL_ERRORS:{len(errors)}")
    for f in backed_up:
        print(f"FILE:{f}")
    for e in errors:
        print(f"ERROR:{e}")

if __name__ == "__main__":
    main()
