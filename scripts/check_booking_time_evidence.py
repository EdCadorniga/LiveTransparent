from repair_v1_facts_sql import sql_read
print(sql_read("SELECT appointment_id,calendar_id,start_at,payload_json->>'dateAdded' AS date_added,payload_json->>'createdAt' AS created_at FROM lt_exec_v1_appointment_facts WHERE (start_at AT TIME ZONE 'America/Los_Angeles')::date BETWEEN '2026-10-04' AND '2026-10-10';"))
