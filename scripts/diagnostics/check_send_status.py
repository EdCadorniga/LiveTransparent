import paramiko, base64
from pathlib import Path

key = paramiko.Ed25519Key.from_private_key_file(str(Path(r'C:\Users\edmon\.ssh\local-upload')))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('89.117.21.29', username='root', pkey=key, timeout=30)

def run(cmd):
    _, o, e = client.exec_command(cmd)
    r = o.read().decode().strip()
    err = e.read().decode().strip()
    status = o.channel.recv_exit_status()
    if status:
        print(f"EXIT {status}: {err[:500] if err else r[:500]}")
        return ""
    print(r[:2000] if r else err[:500] or "no output")
    return r

containers = run("docker ps --format '{{.Names}}\t{{.Image}}' | grep -i postgres")
pg = next(row.split("\t")[0] for row in containers.strip().splitlines() if row.split("\t")[0].startswith("postgres-"))
run(f"docker exec {pg} env | grep POSTGRES_USER=")
run(f"docker exec {pg} psql -U postgres -d n8n -Atc \"SELECT status, COUNT(1) FROM instagram_company_dm_send_log WHERE workflow_run_id LIKE 'sender:%' GROUP BY status ORDER BY status;\"")
run(f"docker exec {pg} psql -U postgres -d n8n -Atc \"SELECT status, COUNT(1) FROM instagram_company_dm_send_log WHERE workflow_run_id LIKE 'instagram_sender:%' GROUP BY status ORDER BY status;\"")

client.close()