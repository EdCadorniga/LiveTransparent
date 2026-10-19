from repair_v1_facts_sql import sql_read
print(sql_read("SELECT column_name,data_type FROM information_schema.columns WHERE table_name='execution_entity' ORDER BY ordinal_position;",database='n8n'))
