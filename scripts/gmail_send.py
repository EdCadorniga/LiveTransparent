"""Send an email via Gmail API using Hermes Google OAuth token, refreshing the access token if expired.
Usage: python gmail_send.py "To: a@b\r\nSubject: X\r\n\r\nBody"   (or --stdin)
Refreshes token via refresh_token grant when expired. Prints SENT_OK id=... on success.
No secrets printed."""
import os, sys, json, base64, ssl, time, urllib.request, urllib.parse

HH = r"C:\1_Ed's Active Work\AI\Hermes"
TOKEN = os.path.join(HH, "google_token.json")

def load_token():
    with open(TOKEN, encoding="utf-8") as f:
        return json.load(f)

def save_token(d):
    tmp = TOKEN + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, TOKEN)

def refresh_if_needed(d):
    exp = d.get("expiry")
    if exp:
        try:
            from datetime import datetime, timezone
            e = datetime.fromisoformat(exp.replace("Z","+00:00"))
            if e > datetime.now(timezone.utc):
                return d, False
        except Exception:
            pass
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": d["refresh_token"],
        "client_id": d["client_id"],
        "client_secret": d["client_secret"],
    }).encode()
    req = urllib.request.Request(d["token_uri"], data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as resp:
        j = json.loads(resp.read().decode())
    if "access_token" not in j:
        raise RuntimeError("refresh failed: " + json.dumps(j)[:300])
    d = dict(d)
    d["token"] = j["access_token"]
    from datetime import datetime, timedelta, timezone
    d["expiry"] = (datetime.now(timezone.utc) + timedelta(seconds=int(j.get("expires_in", 3600))-60)).isoformat()
    save_token(d)
    return d, True

def main():
    raw = sys.stdin.read() if len(sys.argv) < 2 or sys.argv[1] == "--stdin" else sys.argv[1]
    d = load_token()
    d, refreshed = refresh_if_needed(d)
    tok = d["token"]
    raw_b64 = base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")
    body = json.dumps({"raw": raw_b64}).encode("utf-8")
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", "Bearer " + tok)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as resp:
            out = json.loads(resp.read().decode("utf-8"))
            print("SENT_OK id=" + out.get("id","") + (" refreshed=1" if refreshed else ""))
    except urllib.error.HTTPError as e:
        print("HTTPERR", e.code, e.read().decode("utf-8")[:500]); sys.exit(3)

if __name__ == "__main__":
    main()
