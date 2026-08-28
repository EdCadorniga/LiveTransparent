# DNS Email Authentication Fix — LiveTransparent

**Requested by:** LiveTransparent
**Date:** 2026-08-21
**Domains affected:** `livetransparent.com`, `livetransparent.co`, `livetransparent.agency`, `livetransparent.org`
**Why:** Recipients are seeing Gmail's "This message might be dangerous / look-alike domain" warning on legitimate marketing email. Root cause is broken email authentication (SPF + DMARC). This fix restores SPF, DKIM, and DMARC so the domains authenticate properly.

---

## Summary of changes required

| Domain | SPF | DMARC | DKIM |
|--------|-----|-------|------|
| `livetransparent.com` | Replace — add missing includes | Already valid — optional `sp=none` | Add Mailgun + GHL selectors |
| `livetransparent.co` | **Fix duplicate records** → merge into one | **Fix duplicate records** → replace with one | Add Mailgun + GHL selectors |
| `livetransparent.agency` | **Fix duplicate records** → merge into one | **Fix duplicate records** → replace with one | Add Mailgun + GHL selectors |
| `livetransparent.org` | **Fix duplicate records** → merge into one | Replace with complete record | Add Mailgun + GHL selectors |

> **Critical rule:** A domain may have **only ONE** SPF record and **only ONE** DMARC record. Multiple records of the same type cause a permanent validation error (`permerror`), which makes SPF/DMARC fail for **all** mail from that domain — including legitimate sends.

---

## 1. SPF records (TXT type)

The current setup has **two** SPF records per domain on `.co`, `.agency`, and `.org`. Each must be reduced to a single merged record. Delete the old records and add the single merged record below.

### `livetransparent.com`
**Delete existing TXT:** `v=spf1 include:_spf.google.com ~all`

**Add (replace):**
```
v=spf1 include:_spf.google.com include:spf.leadconnectorhq.com include:mailgun.org ~all
```

### `livetransparent.co`
**Delete existing TXT records (both):**
- `v=spf1 include:_spf.google.com include:mailgun.org ~all`
- `v=spf1 include:spf.leadconnectorhq.com include:mailgun.org ~all`

**Add (replace):**
```
v=spf1 include:_spf.google.com include:spf.leadconnectorhq.com include:mailgun.org ~all
```

### `livetransparent.agency`
**Delete existing TXT records (both):**
- `v=spf1 include:_spf.google.com include:mailgun.org ~all`
- `v=spf1 include:spf.leadconnectorhq.com include:mailgun.org ~all`

**Add (replace):**
```
v=spf1 include:_spf.google.com include:spf.leadconnectorhq.com include:mailgun.org ~all
```

### `livetransparent.org`
**Delete existing TXT records (both):**
- `v=spf1 include:_spf.google.com include:mailgun.org ~all`
- `v=spf1 include:spf.leadconnectorhq.com include:mailgun.org ~all`

**Add (replace):**
```
v=spf1 include:_spf.google.com include:spf.leadconnectorhq.com include:mailgun.org ~all
```

> Do **not** delete unrelated TXT records on these domains (site verification and Klaviyo verification records must be kept).

---

## 2. DMARC records (TXT type at `_dmarc.<domain>`)

`.co` and `.agency` currently have **two** DMARC records each. Only one is allowed. Delete all existing DMARC records for each domain and add the single complete record below.

### `_dmarc.livetransparent.co`
**Delete existing DMARC records (both), then add:**
```
v=DMARC1; p=none; sp=none; pct=100; rua=mailto:dmarc-reports@livetransparent.co; ruf=mailto:dmarc-reports@livetransparent.co; fo=1; adkim=r; aspf=r
```

### `_dmarc.livetransparent.agency`
**Delete existing DMARC records (both), then add:**
```
v=DMARC1; p=none; sp=none; pct=100; rua=mailto:dmarc-reports@livetransparent.agency; ruf=mailto:dmarc-reports@livetransparent.agency; fo=1; adkim=r; aspf=r
```

### `_dmarc.livetransparent.org`
**Delete existing DMARC record, then add:**
```
v=DMARC1; p=none; sp=none; pct=100; rua=mailto:dmarc-reports@livetransparent.org; ruf=mailto:dmarc-reports@livetransparent.org; fo=1; adkim=r; aspf=r
```

### `_dmarc.livetransparent.com`
Current record is already valid and the most strict (`p=reject`). **No change required.** Optionally add `sp=none` for consistency:
```
v=DMARC1;p=reject;pct=100;rua=mailto:dmarc-reports@livetransparent.com;ruf=mailto:dmarc-reports@livetransparent.com;ri=86400;fo=1;sp=none
```

> Note: `p=none` on `.co`/`.agency`/`.org` is intentional — it monitors without rejecting mail while the fix is validated. Once confirmed working, the policy can be tightened later.

---

## 3. DKIM records (TXT type)

Only Google's DKIM selector (`google._domainkey`) is currently published. Google Workspace mail is covered, but **Mailgun and GHL (LeadConnector) sends are not DKIM-signed**, so they look unauthenticated.

### What needs to be added

For each domain, add **one TXT record per provider** using the selector and public key the provider displays:

| Provider | Selector hostname | Value source |
|----------|-------------------|--------------|
| Mailgun | `<selector>._domainkey.<domain>` (usually `smtp._domainkey.<domain>` or as shown in Mailgun) | Mailgun → Sending → Domain → DNS Records |
| GHL / LeadConnector | `<selector>._domainkey.<domain>` (as shown in GHL) | GHL → Settings → Email / Domains → DNS records |

The value will look like:
```
v=DKIM1; k=rsa; p=<public-key-base64>
```

**Action needed from the sending platforms:**
1. In **Mailgun**, open the domain settings for each of the four domains and copy the DKIM TXT record shown.
2. In **GHL (LeadConnector)**, open the email sending settings for each domain and copy the DKIM TXT record shown (GHL may name the selector, e.g. `scph0811._domainkey`).
3. Have the domain admin add these TXT records at the exact hostname and value provided by each platform.
4. Then click "Verify" in Mailgun / GHL to confirm the records are live.

---

## 4. Verification steps (after DNS changes propagate)

Wait 15–60 minutes for DNS propagation, then verify all domains:

1. **mxtoolbox SuperTool** — https://mxtoolbox.com/SuperTool.aspx
   - Run SPF check for each domain → must show **Pass** and exactly one record.
   - Run DMARC check for each domain → must show **Valid** and exactly one record.
2. **PowerShell (optional)** — confirm single records:
   ```powershell
   nslookup -type=TXT livetransparent.co
   nslookup -type=TXT _dmarc.livetransparent.co
   nslookup -type=TXT smtp._domainkey.livetransparent.co
   ```
3. **Send a test email** to a Gmail address from each sender and confirm no warning banner appears.

---

## Contact / owner

- **Requested by:** Ed (LiveTransparent)
- **POCs for DKIM values:** Mailgun dashboard and GHL/LeadConnector email settings (selector values must come from those platforms).
- If you have questions, contact Ed before making changes.
