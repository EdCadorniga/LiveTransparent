from repair_v1_facts_sql import sql_read
print(sql_read("SELECT COUNT(*),MIN(\"createdAt\"),MAX(\"createdAt\") FROM execution_entity WHERE \"workflowId\"='1diZyFmTqWQUEny3' AND mode='webhook' AND \"createdAt\">='2026-10-04T07:00:00Z';",database='n8n'))
