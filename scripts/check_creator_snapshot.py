from repair_v1_facts_sql import sql_read
print(sql_read("SELECT DISTINCT payload_json->'internalSource' FROM report_raw_ghl_opportunities WHERE source_key='48gqEAcG7b5mMjrJSX5C';"))
