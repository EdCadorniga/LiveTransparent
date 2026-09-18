import paramiko, time
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
    print(f"EXIT {status}")
    if r: print(r[:1000])
    if err: print("ERR:", err[:1000])
    return status

# Patch pg-protocol messages.js - replace this.name = name with Object.defineProperty
patch_cmd = (
    "docker exec -u 0 n8n-runner sh -c "
    "'sed -i \"s/this\\.name = name;/try { Object.defineProperty(this, \\\"name\\\", { value: name, configurable: true }); } catch(e) { this.name = this.constructor.name; }/\" "
    "/opt/pg-node_modules/pg-protocol/dist/messages.js'"
)
run(patch_cmd)

# Verify the fix
run("docker exec -u 0 n8n-runner sh -c 'grep -n \"Object.defineProperty\" /opt/pg-node_modules/pg-protocol/dist/messages.js | head -3'")

# Restart runner
time.sleep(1)
run("docker restart n8n-runner")
time.sleep(5)
run("docker logs n8n-runner --tail 3")

client.close()