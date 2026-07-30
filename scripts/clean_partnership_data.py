"""
Partnership Marketing Data Preparation
======================================
Reads the Email and LinkedIn partnership CSVs, merges/deduplicates contacts,
fixes data issues, excludes entries with wrong company names, and outputs
a single master JSON ready for GHL import.

Usage: python scripts/clean_partnership_data.py [--output master.json]
"""

import csv, json, re, sys, os, collections
from pathlib import Path

PARTNERSHIP_DIR = Path(__file__).resolve().parent.parent / "Partnership Marketing"
EMAIL_CSV = PARTNERSHIP_DIR / "Content Partnerships - Email - Consolidated List.csv"
LINKEDIN_CSV = PARTNERSHIP_DIR / "Content Partnerships - Linkedln - Consolidated List.csv"
DEFAULT_OUTPUT = PARTNERSHIP_DIR / "partnership_master.json"

# ─── Exclusions ──────────────────────────────────────────────────────────────
# Entries to skip entirely (wrong company name per email domain verification).
# Keyed on first_name|last_name (lowercase), with optional email to be precise.

EXCLUDE_FROM_BOTH = {
    # Same list in both email + LinkedIn CSVs:
    "jake|litke",         # MediaJel, not DailyStory
    "rick|kiley",         # SoHo Experiential, not MediaJel
    "rob|howard",         # DailyStory, not Partner Name
    "darcel|duncan",      # Emerald X, not SoHo Experiential
    "john|marshall",      # NECANN, not CWCBExpo
    "mac|haddow",         # AKA, not ATACH
    "david|schachter",    # Springbig, not AKA
    "lisa|buffo",         # Cannabis Marketing Assoc, not CBT
    "kim|jage",           # LinkedIn URL wrong (sal-vassallo)
    "alan|brochstein",    # LinkedIn URL wrong (marcshepard duplicate)
    "tony|lange",         # GIE Media (though CBT is owned by GIE, exclude per user)
}

# Email-only entries with wrong company
EXCLUDE_FROM_EMAIL_ONLY = {
    "michael|bronstein",  # ATACH, not NCIA
    "christine|ianuzzi",  # Leading Edge Expositions, not Springbig
}

# ─── Company name corrections (email domain → correct company) ───────────────
COMPANY_CORRECTIONS = {
    "dailystory.com": "DailyStory",
    "mediajel.com": "MediaJel",
    "sohoexp.com": "SoHo Experiential",
    "necann.com": "NECANN",
    "cannabismarketingassociation.com": "Cannabis Marketing Association",
    "cannabisindustry.org": "National Cannabis Industry Association (NCIA)",
    "gie.net": "GIE Media",
    "emeraldx.com": "Emerald X",
    "springbig.com": "Springbig",
    "americankratom.org": "American Kratom Association (AKA)",
    "atach.org": "American Trade Association of Cannabis & Hemp (ATACH)",
    "leexpos.com": "Leading Edge Expositions",
}

# ─── Helpers ─────────────────────────────────────────────────────────────────

def name_key(first, last):
    return f"{first.strip().lower()}|{last.strip().lower()}"

def clean(v):
    return str(v or "").strip().strip(",")

def extract_email_domain(email):
    """Return domain from email, or empty string."""
    email = clean(email)
    if "@" in email:
        return email.split("@")[-1].lower()
    return ""

def get_display_name(first, last, company, email):
    """Resolve a display name. If first name is empty or '-', use company name."""
    fn = clean(first)
    ln = clean(last)
    domain = extract_email_domain(email)
    co = clean(company)

    if fn and fn != "-":
        # Normal name – keep as-is
        return fn, ln, co
    # No name – use company name as first_name
    # If company is also generic, try domain-based correction
    if COMPANY_CORRECTIONS.get(domain):
        co = COMPANY_CORRECTIONS[domain]
    if not co or co == "-":
        co = domain or "Unknown"
    return co, "", co

def is_excluded(fn, ln, email, source_list):
    """Check if this entry should be excluded."""
    key = name_key(fn, ln)
    # Noelle Skodzinski: exclude comcast.net, KEEP gie.net for email campaign
    if key == "noelle|skodzinski":
        em = clean(email).lower()
        if "comcast.net" in em:
            return True  # exclude comcast.net only
        return False  # keep gie.net
    # Noelle's LinkedIn entry (appears in both lists) — keep for LinkedIn
    if source_list == "email" and key in EXCLUDE_FROM_EMAIL_ONLY:
        return True
    if key in EXCLUDE_FROM_BOTH:
        return True
    return False

def normalize_linkedin_url(url):
    """Normalize LinkedIn URL to canonical https://www.linkedin.com/in/<slug>"""
    url = clean(url)
    if not url:
        return ""
    # Strip ?skipRedirect=true or trailing params
    url = re.sub(r'\?.*$', '', url)
    url = re.sub(r'/+$', '', url)
    url = url.replace("http://", "https://")
    if "linkedin.com" not in url:
        return url
    return url

# ─── Read CSVs ───────────────────────────────────────────────────────────────

def read_csv(path):
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

email_rows = read_csv(EMAIL_CSV)
li_rows = read_csv(LINKEDIN_CSV)

print(f"Read {len(email_rows)} email entries, {len(li_rows)} LinkedIn entries")

# ─── Build intermediate records ──────────────────────────────────────────────

# Intermediate: { name_key: { emails: [], linkedin_urls: [], companies: [], titles: [] } }
contacts = {}

# Process Email CSV
for r in email_rows:
    fn = clean(r.get("First Name", ""))
    ln = clean(r.get("Last Name", ""))
    email = clean(r.get("Email", ""))
    co = clean(r.get("Company Name", ""))
    title = clean(r.get("Title", ""))
    domain = extract_email_domain(email)

    if is_excluded(fn, ln, email, "email"):
        print(f"  EXCLUDE email: {fn} {ln} ({co}) email={email}")
        continue

    # Apply company correction from domain
    if COMPANY_CORRECTIONS.get(domain):
        co = COMPANY_CORRECTIONS[domain]

    display_fn, display_ln, display_co = get_display_name(fn, ln, co, email)

    key = name_key(display_fn, display_ln)
    if key not in contacts:
        contacts[key] = {"first": display_fn, "last": display_ln, "emails": [], "li_urls": [], "companies": [], "titles": [], "tags": set()}
    c = contacts[key]
    if email:
        c["emails"].append(email)
    if co:
        c["companies"].append(co)
    if title:
        c["titles"].append(title)
    c["tags"].add("partner_candidate_email")

# Process LinkedIn CSV
for r in li_rows:
    fn = clean(r.get("First Name", ""))
    ln = clean(r.get("Last Name", ""))
    co = clean(r.get("Company Name", ""))
    title = clean(r.get("Title", ""))
    li_url = normalize_linkedin_url(r.get("Person Linkedin Url", ""))

    if is_excluded(fn, ln, "", "linkedin"):
        print(f"  EXCLUDE linkedin: {fn} {ln} ({co}) url={li_url}")
        continue

    display_fn, display_ln, display_co = get_display_name(fn, ln, co, "")
    key = name_key(display_fn, display_ln)
    if key not in contacts:
        contacts[key] = {"first": display_fn, "last": display_ln, "emails": [], "li_urls": [], "companies": [], "titles": [], "tags": set()}
    c = contacts[key]
    if li_url:
        c["li_urls"].append(li_url)
    if co:
        c["companies"].append(co)
    if title:
        c["titles"].append(title)
    c["tags"].add("partner_candidate_linkedin")

# ─── Resolve duplicates → final list ─────────────────────────────────────────

master = []
for key, c in sorted(contacts.items()):
    # Deduplicate
    emails = sorted(set(c["emails"]))
    li_urls = sorted(set(c["li_urls"]))
    companies = sorted(set(c["companies"]))
    titles = sorted(set(c["titles"]))
    tags = sorted(c["tags"])

    # Pick primary email: first personal-looking one
    primary_email = ""
    for e in emails:
        if e and e != "-":
            primary_email = e
            break

    # Pick primary LinkedIn URL
    primary_li_url = li_urls[0] if li_urls else ""

    # Pick primary company: prefer domain-corrected company, then LinkedIn-validated
    primary_company = ""
    domain = extract_email_domain(primary_email)
    corrected = COMPANY_CORRECTIONS.get(domain, "")
    if corrected and any(corrected.lower() in co.lower() or co.lower() in corrected.lower() for co in companies):
        primary_company = corrected
    elif companies:
        primary_company = companies[0]

    # Pick primary title
    primary_title = titles[0] if titles else ""

    contact = {
        "first_name": c["first"],
        "last_name": c["last"],
        "email": primary_email,
        "company_name": primary_company,
        "title": primary_title,
        "linkedin_url": primary_li_url,
        "all_emails": emails,
        "all_linkedin_urls": li_urls,
        "all_companies": companies,
        "all_titles": titles,
        "tags": tags,
        "has_email": "partner_candidate_email" in tags,
        "has_linkedin": "partner_candidate_linkedin" in tags,
    }
    master.append(contact)

# ─── Stats ───────────────────────────────────────────────────────────────────

email_count = sum(1 for c in master if c["has_email"])
li_count = sum(1 for c in master if c["has_linkedin"])
both_count = sum(1 for c in master if c["has_email"] and c["has_linkedin"])
li_only = sum(1 for c in master if c["has_linkedin"] and not c["has_email"])
email_only = sum(1 for c in master if c["has_email"] and not c["has_linkedin"])

print(f"\n=== MASTER LIST: {len(master)} unique contacts ===")
print(f"  Email only:    {email_only}")
print(f"  LinkedIn only: {li_only}")
print(f"  Both:          {both_count}")
print(f"  Total email candidates:    {email_count}")
print(f"  Total LinkedIn candidates: {li_count}")

# ─── Output ──────────────────────────────────────────────────────────────────

output_path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--output" else str(DEFAULT_OUTPUT)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(master, f, indent=2, ensure_ascii=False)

print(f"\nWritten to {output_path}")

# ─── Print preview ──────────────────────────────────────────────────────────

print(f"\n=== FIRST 5 CONTACTS (preview) ===")
for c in master[:5]:
    print(f"  {c['first_name']} {c['last_name']}")
    print(f"    email: {c['email']}  |  company: {c['company_name']}")
    print(f"    tags: {c['tags']}")
    print(f"    li_url: {c['linkedin_url']}")

print(f"\n=== LINKEDIN-ONLY (no email) ===")
for c in master:
    if c["has_linkedin"] and not c["has_email"]:
        print(f"  {c['first_name']} {c['last_name']}  ({c['company_name']})")
        print(f"    li_url: {c['linkedin_url']}")
