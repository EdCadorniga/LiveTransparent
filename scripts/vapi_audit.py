import paramiko

k = paramiko.Ed25519Key.from_private_key_file(r'C:\Users\edmon\.ssh\local-upload')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('89.117.21.29', username='root', pkey=k)

commands = [
    # Find pg module in n8n's node_modules
    "docker exec n8n-n44wksswcocwk88ogcog8c48 find /usr/local/lib/node_modules/n8n -name 'pg' -type d -maxdepth 5 2>/dev/null | head -5",
    # Try requiring pg from n8n's path
    "docker exec n8n-n44wksswcocwk88ogcog8c48 node -e \"try { const pg = require('/usr/local/lib/node_modules/n8n/node_modules/pg'); console.log('found pg at: ' + typeof pg.Client); } catch(e) { console.log('not found: ' + e.message); }\"",
    # Check n8n task runner env
    "docker inspect n8n-n44wksswcocwk88ogcog8c48 --format '{{range .Config.Env}}{{println .}}{{end}}' 2>&1 | grep -i RUNNER",
]

for cmd in commands:
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    print(f"CMD: {cmd[:100]}")
    print(f"OUT: {out}")
    if err: print(f"ERR: {err}")
    print()

c.close()
