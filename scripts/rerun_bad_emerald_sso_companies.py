import json
import sys
from typing import Any

import requests


API_BASE = "https://automations.livetransparent.com/api/v1"
API_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiI4NjFmYjY1NS1iMTc2LTRkNjMtYTRlZC0zY2M2NmUyNzk2NDIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiODQyYTM2NDctZjMwZi00NzcxLThkNmMtNjM5Mjg0YmQ0MWVkIiwiaWF0IjoxNzc0NTYwMzU3LCJleHAiOjE3ODIyODQ0MDB9."
    "bsrDA-as3_JNXSoBI5x-i7zeaXTf1yeC9nxhRzmPJf4"
)
WORKFLOW_ID = "GHVYyYmhfNiZ7bbN"
POSTGRES_CREDENTIAL = {"id": "pgAzUqpwOiGkGXzO", "name": "Postgres account"}

DEFAULT_COMPANY_KEYS = [
    "altasciences.com",
    "atb.com",
    "centriconsulting.com",
    "emeraldx.com",
    "firstcitizens.com",
    "hbkcpa.com",
    "mckimcreed.com",
    "roth.com",
    "weedmaps.com",
]


def sql_lit(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def request_json(method: str, path: str, **kwargs: Any) -> requests.Response:
    headers = kwargs.pop("headers", {})
    headers["X-N8N-API-KEY"] = API_KEY
    response = requests.request(method, f"{API_BASE}{path}", headers=headers, timeout=120, **kwargs)
    response.raise_for_status()
    return response


def build_reset_query(company_keys: list[str]) -> str:
    key_list = ", ".join(sql_lit(key) for key in company_keys)
    return f"""
DELETE FROM "Emerald_Company_Research_Cache"
WHERE company_domain_key IN ({key_list});

UPDATE "Emerald_Contacts"
SET
  emerald_exec_sso_ai_research = NULL,
  ghl_contact_sync_status = 'pending',
  ghl_contact_sync_error = NULL,
  company_research_snippet = NULL,
  company_operating_state = NULL,
  company_operating_market_note = NULL,
  company_cannabis_marketing_signal = NULL,
  company_research_confidence = NULL,
  company_research_source = NULL,
  company_research_last_verified_at = NULL
WHERE company_domain_key IN ({key_list});

SELECT
  company_domain_key,
  COUNT(*) AS reset_rows
FROM "Emerald_Contacts"
WHERE company_domain_key IN ({key_list})
GROUP BY company_domain_key
ORDER BY company_domain_key ASC;
""".strip()


def create_temp_workflow(query: str) -> dict[str, Any]:
    payload = {
        "name": "TMP - Reset Emerald SSO Bad Cache Rows",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "tmp-reset-emerald-sso-bad-cache-rows",
                    "responseMode": "onReceived",
                    "options": {},
                },
                "id": "reset_webhook",
                "name": "Reset Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [280, 300],
            },
            {
                "parameters": {
                    "operation": "executeQuery",
                    "query": query,
                    "options": {},
                },
                "id": "reset_rows",
                "name": "Reset Bad Cache Rows",
                "type": "n8n-nodes-base.postgres",
                "typeVersion": 2.6,
                "position": [520, 300],
                "credentials": {"postgres": POSTGRES_CREDENTIAL},
            },
        ],
        "connections": {
            "Reset Webhook": {
                "main": [[{"node": "Reset Bad Cache Rows", "type": "main", "index": 0}]]
            }
        },
        "settings": {},
    }
    return request_json("POST", "/workflows", json=payload).json()


def run_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "workflowData": {
            "id": workflow["id"],
            "name": workflow["name"],
            "nodes": workflow["nodes"],
            "connections": workflow["connections"],
            "settings": workflow.get("settings", {}),
        }
    }
    return request_json("POST", "/workflows/run", json=payload).json()


def delete_workflow(workflow_id: str) -> None:
    request_json("DELETE", f"/workflows/{workflow_id}")


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "create"
    company_keys = sys.argv[2:] if len(sys.argv) > 2 else DEFAULT_COMPANY_KEYS
    if mode == "create":
        query = build_reset_query(company_keys)
        temp_workflow = create_temp_workflow(query)
        print(json.dumps({"resetWorkflowId": temp_workflow["id"], "companies": company_keys}, indent=2))
        return
    if mode == "delete":
        delete_workflow(sys.argv[2])
        print(json.dumps({"deletedWorkflowId": sys.argv[2]}, indent=2))
        return
    raise SystemExit(f"Unsupported mode: {mode}")


if __name__ == "__main__":
    main()
