"""Read Gmail via the Hermes Google OAuth token (gmail.readonly scope), refreshing token if needed.
Usage: python gmail_read.py [--query STRING] [--max N] [--body]
Lists up to N messages matching query: id, date, subject, snippet.
With --body, each message also includes 'body' (full plaintext, decoded). No secrets printed.
"""
import os, sys, json, ssl, time, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

HH = r"C:\1_Ed's Active Work\AI\Hermes"
TOKEN = os.path.join(HH, "google_token.json")

def load_token():
    with open(TOKEN, encoding="utf-8") as f:
        return json.load(f)

def save_token(d):
    tmp = TOKEN+".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, TOKEN)

def refresh_if_needed(d):
    exp = d.get("expiry")
    if exp:
        try:
            e = datetime.fromisoformat(exp.replace("Z", "+00:00"))
            if e > datetime.now(timezone.utc):
                return d
        except Exception:
            pass
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token", "refresh_token": d["refresh_token"],
        "client_id": d["client_id"], "client_secret": d["client_secret"]}).encode()
    req = urllib.request.Request(d["token_uri"], data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as resp:
        j = json.loads(resp.read().decode())
    d = dict(d); d["token"] = j["access_token"]
    d["expiry"] = (datetime.now(timezone.utc) + timedelta(seconds=int(j.get("expires_in",3600))-60)).isoformat()
    save_token(d)
    return d

def api_get(path, tok):
    url = "https://gmail.googleapis.com/gmail/v1/" + path
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", "Bearer "+tok)
    with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as resp:
        return json.loads(resp.read().decode())

def extract_body(payload):
    """Walk Gmail payload parts and return the plaintext body (best effort)."""
    import base64
    parts = []
    def walk(p):
        mt = p.get("mimeType", "")
        b = p.get("body", {})
        if mt == "text/plain" and b.get("data"):
            try:
                parts.append(base64.urlsafe_b64decode(b["data"]).decode("utf-8", "ignore"))
            except Exception:
                pass
        for sp in p.get("parts", []) or []:
            walk(sp)
    walk(payload)
    return "\n".join(parts)


def main():
    args = sys.argv[1:]
    query = "from:me subject:[LiveTransparent]"
    maxn = 10
    with_body = False
    i = 0
    while i < len(args):
        if args[i] == "--query" and i+1 < len(args):
            query = args[i+1]; i += 2
        elif args[i] == "--max" and i+1 < len(args):
            maxn = int(args[i+1]); i += 2
        elif args[i] == "--body":
            with_body = True; i += 1
        else:
            i += 1
    d = load_token(); d = refresh_if_needed(d); tok = d["token"]
    q = urllib.parse.quote(query)
    res = api_get("users/me/messages?q=%s&maxResults=%d" % (q, maxn), tok)
    msgs = res.get("messages", [])
    out = []
    for m in msgs:
        fmt = "full" if with_body else "metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date"
        full = api_get("users/me/messages/%s?format=%s" % (m["id"], fmt), tok)
        hdrs = {h["name"].lower(): h["value"] for h in full.get("payload",{}).get("headers",[])}
        item = {
            "id": m["id"],
            "date": hdrs.get("date",""),
            "subject": hdrs.get("subject",""),
            "snippet": full.get("snippet","")[:200],
        }
        if with_body:
            item["body"] = extract_body(full.get("payload", {}))
        out.append(item)
    print(json.dumps(out))

if __name__ == "__main__":
    main()
