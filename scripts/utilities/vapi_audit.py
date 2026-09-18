import paramiko

k = paramiko.Ed25519Key.from_private_key_file(r'C:\Users\edmon\.ssh\local-upload')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('89.117.21.29', username='root', pkey=k)

commands = [
    # Check running containers
    "docker ps --format '{{.Names}} {{.Image}} {{.Status}}' | grep n8n",
    # Check runner logs for errors
    "docker logs n8n-runner --since 5m 2>&1 | tail -5",
    # Check n8n logs for workflow activations
    "docker logs n8n-n44wksswcocwk88ogcog8c48 --since 5m 2>&1 | grep -i 'activ\\|error' | tail -5",
    # Check database tables
    "docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d n8n -t -A -c \"SELECT count(*) as contacts FROM emerging_pool_contacts;\"",
    "docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d n8n -t -A -c \"SELECT count(*) as raw_contacts FROM report_raw_ghl_contacts;\"",
    "docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d n8n -t -A -c \"SELECT count(*) as queue FROM voice_call_queue;\"",
    "docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d n8n -t -A -c \"SELECT id, name, active, substring(nodes::text from 1 for 500) FROM workflow_entity WHERE id = 'osIJOgBmWITF5Yuv';\"",
    "docker exec postgres-uokgs4c04ko0s4scccg40cgg psql -U postgres -d n8n -t -A -c \"SELECT id, name, active, substring(nodes::text from 1 for 500) FROM workflow_entity WHERE id IN ('r7UjWLndmc6EqEUW','fx4UvKUWbqJEY3LK','PUCfTZBANSPcgS0c');\"",
    "docker exec n8n-runner sh -lc \"id; pwd; find /opt/runners/task-runner-javascript -maxdepth 3 -type d | head -80\"",
    "docker exec n8n-n44wksswcocwk88ogcog8c48 sh -lc \"find /usr/local/lib/node_modules/n8n/node_modules -path '*/node_modules/pg' -o -path '*/node_modules/pg-types' -o -path '*/node_modules/pg-pool' -o -path '*/node_modules/pg-protocol' -o -path '*/node_modules/pg-connection-string' -o -path '*/node_modules/pgpass'\"",
    "docker exec n8n-runner node -e \"try { const pg=require('pg'); console.log('pg-ok', typeof pg.Client) } catch(e) { console.log('pg-fail', e.message) }\"",
    "docker exec n8n-runner sh -lc \"ls -la /opt/runners/task-runner-javascript/node_modules | head -40; find /opt/runners/task-runner-javascript -maxdepth 2 -type f -name 'package*.json' -print -exec sed -n '1,120p' {} \\;\"",
    "docker exec n8n-runner sh -lc \"node -p 'process.execPath'; node -p 'require.resolve(\\\"module-details-from-path\\\")'\"",
    "docker exec n8n-n44wksswcocwk88ogcog8c48 sh -lc \"readlink -f /usr/local/lib/node_modules/n8n/node_modules/.pnpm/pg@8.21.0_pg-native@3.8.0/node_modules/pg; find /usr/local/lib/node_modules/n8n/node_modules/.pnpm/pg@8.21.0_pg-native@3.8.0/node_modules/pg/node_modules -maxdepth 1 -type l -printf '%f -> %l\\n'\"",
]

for cmd in commands:
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode().strip()
    if out: print(out)
c.close()
