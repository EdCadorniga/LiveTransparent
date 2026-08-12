import os
import posixpath
import shlex

import paramiko


HOST = "89.117.21.29"
KEY = r"C:\Users\edmon\.ssh\local-upload"
LOCAL_DOCKERFILE = os.path.join(os.path.dirname(__file__), "..", "n8n", "runners", "Dockerfile")
LOCAL_RUNNER_CONFIG = os.path.join(os.path.dirname(__file__), "..", "n8n", "runners", "n8n-task-runners.json")
REMOTE_DIR = "/tmp/livetransparent-runner"
RUNNER_AUTH_TOKEN = os.environ.get("N8N_RUNNERS_AUTH_TOKEN", "")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "")

if not RUNNER_AUTH_TOKEN or not POSTGRES_PASSWORD:
    raise SystemExit("Set N8N_RUNNERS_AUTH_TOKEN and POSTGRES_PASSWORD before deploying the runner")


key = paramiko.Ed25519Key.from_private_key_file(KEY)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username="root", pkey=key)

client.exec_command(f"rm -rf {REMOTE_DIR} && mkdir -p {REMOTE_DIR}")[1].read()
sftp = client.open_sftp()
sftp.put(os.path.abspath(LOCAL_DOCKERFILE), posixpath.join(REMOTE_DIR, "Dockerfile"))
sftp.put(os.path.abspath(LOCAL_RUNNER_CONFIG), posixpath.join(REMOTE_DIR, "n8n-task-runners.json"))
sftp.close()

commands = [
    f"docker build --pull --progress=plain -t n8nio/runners-custom:latest {REMOTE_DIR}",
    "docker image inspect n8nio/runners-custom:latest --format '{{.Id}}'",
    "docker rm -f n8n-runner",
    f"docker run -d --name n8n-runner --restart unless-stopped --network coolify-shared -e N8N_RUNNERS_AUTH_TOKEN={shlex.quote(RUNNER_AUTH_TOKEN)} -e N8N_RUNNERS_TASK_BROKER_URI=http://n8n:5679 -e NODE_PATH=/opt/pg-node_modules -e NODE_FUNCTION_ALLOW_EXTERNAL='*' -e NODE_FUNCTION_ALLOW_BUILTIN='crypto,path,fs,net,tls' -v {REMOTE_DIR}/n8n-task-runners.json:/etc/n8n-task-runners.json n8nio/runners-custom:latest",
    "sleep 10; docker exec n8n-runner env NODE_PATH=/opt/pg-node_modules node -p 'typeof require(\"pg\").Client'",
    f"docker exec n8n-runner env NODE_PATH=/opt/pg-node_modules PGHOST=postgres PGPORT=5432 PGDATABASE=n8n PGUSER=postgres PGPASSWORD={shlex.quote(POSTGRES_PASSWORD)} node -e \"const {{Client}}=require('pg'); const c=new Client(); c.connect().then(()=>c.query('SELECT 1 AS ok')).then(r=>{{console.log('db-ok',r.rows[0].ok); return c.end()}}).catch(e=>{{console.error('db-fail',e.message); process.exit(1)}})\"",
    "docker exec n8n-runner sh -lc \"find /opt/runners/task-runner-javascript/node_modules -maxdepth 2 -name package.json -path '*/pg/package.json' -o -name package.json | head -20; ls -la /opt/runners/task-runner-javascript/node_modules/pg 2>&1; cat /opt/runners/task-runner-javascript/node_modules/pg/package.json 2>&1 | head -20\"",
    "docker exec n8n-runner sh -lc \"sed -n '1,150p' /opt/runners/task-runner-javascript/dist/js-task-runner/js-task-runner.js; sed -n '1,100p' /opt/runners/task-runner-javascript/dist/config/js-runner-config.js\"",
    "docker logs n8n-runner --since 30s 2>&1",
]

for command in commands:
    stdin, stdout, stderr = client.exec_command(command)
    print(f"$ {command}\n{stdout.read().decode().strip()}")
    error = stderr.read().decode().strip()
    if error:
        print(error)

client.close()
