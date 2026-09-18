import paramiko


key = paramiko.Ed25519Key.from_private_key_file(r"C:\Users\edmon\.ssh\local-upload")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("89.117.21.29", username="root", pkey=key)

commands = [
    "docker ps --format '{{.Names}} {{.Image}} {{.Status}}'",
    "curl -sS -o /dev/null -w 'n8n-local:%{http_code}\\n' http://127.0.0.1:5678/",
    "docker logs n8n-runner --since 30m",
    "docker logs coolify-proxy --since 30m",
    "docker inspect n8n-runner --format '{{json .NetworkSettings.Networks}}'",
    "docker inspect n8n-n44wksswcocwk88ogcog8c48 --format '{{range $name, $net := .NetworkSettings.Networks}}{{printf \"%s %s %s\\n\" $name $net.IPAddress $net.NetworkID}}{{end}}'",
    "docker logs n8n-n44wksswcocwk88ogcog8c48 --since 5m 2>&1 | grep -E 'ready|accessible|error|Error|timeout|decrypt' | tail -80",
    "docker inspect n8n-n44wksswcocwk88ogcog8c48 --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -E 'N8N_ENCRYPTION_KEY|DB_TYPE|DB_POSTGRES|N8N_RUNNERS' | sed -E 's/^(N8N_ENCRYPTION_KEY|DB_POSTGRESDB_PASSWORD)=.*/\\1=<redacted>/'",
    "docker inspect n8n-runner --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -E 'NODE_PATH|N8N_RUNNERS|NODE_FUNCTION'",
    "docker exec n8n-runner sh -lc 'cat /etc/n8n-task-runners.json | sed -n \"1,45p\"'",
    "docker exec n8n-runner sh -lc 'sed -n \"1,130p\" /opt/runners/task-runner-javascript/dist/js-task-runner/require-resolver.js'",
    "find /data/coolify/services -maxdepth 3 -type f \\( -name 'docker-compose.yml' -o -name '.env' \\) 2>/dev/null | while read f; do grep -Hn 'N8N_ENCRYPTION_KEY' \"$f\" 2>/dev/null | sed -E 's/(N8N_ENCRYPTION_KEY=).*/\\1<redacted>/'; done",
    "docker inspect reports-livetransparent --format '{{range $name, $net := .NetworkSettings.Networks}}{{printf \"%s %s %s\\n\" $name $net.IPAddress $net.NetworkID}}{{end}}'",
    "docker exec reports-livetransparent sh -lc 'grep -Rni proxy_pass /etc/nginx 2>/dev/null || true'",
    "docker exec reports-livetransparent sh -lc 'wget -S -O- -T 30 http://n8n:5678/webhook/lt-report-executive-summary?view=overview%26range=30d 2>&1'",
    "docker logs n8n-n44wksswcocwk88ogcog8c48 --since 3m 2>&1 | tail -100",
]

for command in commands:
    _, stdout, stderr = client.exec_command(command)
    print(f"$ {command}\n{stdout.read().decode().strip()}")
    error = stderr.read().decode().strip()
    if error:
        print(error)

client.close()
