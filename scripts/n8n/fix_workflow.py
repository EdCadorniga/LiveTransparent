import paramiko, json

k = paramiko.Ed25519Key.from_private_key_file(r'C:\Users\edmon\.ssh\local-upload')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('89.117.21.29', username='root', pkey=k)

# Get the workflow JSON
stdin, stdout, stderr = c.exec_command("docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d n8n -t -A -c \"SELECT nodes::text FROM workflow_entity WHERE id = 'osIJOgBmWITF5Yuv';\"")
nodes_json = stdout.read().decode().strip()
nodes = json.loads(nodes_json)

# Find and fix the Build SQL - Upsert Raw Leads Code node
for node in nodes:
    if node.get('name') == 'Build SQL - Upsert Raw Leads':
        old_js = node['parameters']['jsCode']
        # Fix the esc function to handle JSON properly
        new_js = old_js.replace(
            "function esc(v) {\n  if (v === null || v === undefined) return 'NULL';\n  return \"'\" + String(v).replace(/\\\\/g, '\\\\\\\\').replace(/'/g, \"''\") + \"'\";\n}",
            "function esc(v) {\n  if (v === null || v === undefined) return 'NULL';\n  return \"'\" + String(v).replace(/\\\\/g, '\\\\\\\\').replace(/'/g, \"''\") + \"'\";\n}\nfunction escJson(v) {\n  try {\n    const s = typeof v === 'string' ? v : JSON.stringify(v || {});\n    return esc(s);\n  } catch (e) { return esc('{}'); }\n}"
        )
        new_js = new_js.replace(
            "${esc(JSON.stringify(d.payload_json || {}))}::jsonb",
            "${escJson(d.payload_json)}::jsonb"
        ).replace(
            "${esc(JSON.stringify(d.dimensions_json || {}))}::jsonb",
            "${escJson(d.dimensions_json)}::jsonb"
        ).replace(
            "${esc(JSON.stringify(d.metrics_json || {}))}::jsonb",
            "${escJson(d.metrics_json)}::jsonb"
        )
        node['parameters']['jsCode'] = new_js
        print(f"Fixed {node['name']}")
        break

# Write the updated nodes back
nodes_json = json.dumps(nodes)

# Update via n8n REST API
cmd = f"""docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d n8n -c "UPDATE workflow_entity SET nodes = '{nodes_json.replace(chr(39), chr(39)+chr(39))}' WHERE id = 'osIJOgBmWITF5Yuv';\""""
stdin, stdout, stderr = c.exec_command(cmd)
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print(f"UPDATE: {out}")
if err: print(f"ERR: {err}")

# Also need to update the active version
cmd2 = f"""docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d n8n -c "UPDATE workflow_published_version SET nodes = '{nodes_json.replace(chr(39), chr(39)+chr(39))}' WHERE id = '64139619-eff5-4354-89cf-d5ce63e1a1a5';\""""
stdin, stdout, stderr = c.exec_command(cmd2)
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print(f"UPDATE version: {out}")
if err: print(f"ERR: {err}")

c.close()