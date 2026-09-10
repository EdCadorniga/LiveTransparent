# Transparent eCom — Landing Page (Coolify-deployable)

A single-page marketing site for Transparent eCom (regulated-industries ad management),
built as a self-contained static site deployable on your Coolify instance — same
Dockerfile/nginx pattern as `reports/`.

**Status: NOT DEPLOYED. Build only.** Deploy + DNS are gated on Ed's approval.

## Contents

- `index.html` — the landing page (all markup, CSS, JS inline; no build step, no external deps)
- `nginx.conf` — static nginx config (gzip, sane caching)
- `Dockerfile` — nginx:1.27-alpine image, same base as `reports/`
- `assets/` — `logo.png` (from `images/livetransparent_logo.png`), press logos from the Home Page Images set

## What this page does

- ONE offer (regulated-ads compliance agency) — the "Insight Stream" SaaS material from the
  old GHL page is intentionally dropped; it was template debris and split the message.
- CTAs wired to configurable destinations (book / apply) with tracking events.
- Opt-in lead form that POSTs to a configurable endpoint (GHL form or n8n webhook).
- Pixel data: Meta Pixel, TikTok Pixel, GA4, and Google Ads conversion tracking — all in one
  `LT_CONFIG` block, consent-gated by default.
- No placeholder testimonials: the proof section is HIDDEN until real ones are configured.

## Configure before launch (edit `LT_CONFIG` at the top of index.html)

| Key | What | Where to get it |
|---|---|---|
| `META_PIXEL_ID` | Meta/Facebook Pixel ID | Events Manager → your pixel |
| `TIKTOK_PIXEL_ID` | TikTok Pixel ID | TikTok Ads Manager → Assets → Pixel |
| `GA4_MEASUREMENT_ID` | GA4 stream ID | GA4 → Admin → Data Streams |
| `GOOGLE_ADS_ID` / `GOOGLE_ADS_LABEL` | Google Ads conversion ID + label | Ads → Conversions → your conversion |
| `BOOKING_URL` | "Book a Demo" CTA | your GHL calendar / booking link |
| `APPLY_URL` | "Apply Now" CTA | your GHL application funnel link |
| `FORMS_ENDPOINT` | lead form POST target | GHL form submission URL or n8n webhook |
| `TESTIMONIALS` | real quotes array `{quote,name,role}` | "Real Stories from Real Brands We've Grown" images in marketing/website assets (transcribe the quotes) |

Events fired: PageView, ViewContent, BookDemo (CTA), StartApplication (CTA),
Lead + CompleteRegistration (form success), plus GA4 `dataLayer` events.

Consent: `CONSENT_REQUIRED: true` gates all pixels behind the on-page banner
(compliance-first). Set false if you want pixels always-on.

## Check before launch (placeholders to replace)

- Press strip (`adweek-1.png`, `Cannabis-Media-Council-Logo-1-1.png`) — confirm these are
  still current/permitted and that "As featured in / memberships" is accurate.
- Footer legal links (`#` + `data-missing` attribute) — need real Privacy/Terms/Contact URLs.
- `© 2026 <legal entity name>` — confirm legal name ("Transparent eCom" assumed).
- OG `og:url` uses `https://livetransparent.com/` — update to final domain.
- FAQ answers are accurate and approved by the team.

## Deploy to Coolify (for review — NOT executed)

Same flow as `reports/`:

1. Coolify → New Resource → Dockerfile.
2. Point it at this repo (branch of your choice) with Dockerfile path `landing/Dockerfile`
   (or `Dockerfile` if this becomes the repo root).
3. Set the domain (e.g. `www.livetransparent.com` and/or `livetransparent.com`).
4. Let Coolify build; its deploy webhook / auto-deploy will rebuild on push.
5. Point DNS at the Coolify VPS (same as reports.livetransparent.com).
6. Verify: `curl -I https://<domain>/` → 200; check Meta Pixel Helper / GA4 debug view.

Decisions still needed from Ed before any deploy:

- Final domain / subdomain to serve this page on
- Whether it replaces the GHL-hosted funnel page (`go.livetransparent.com/landing-page-page-6310`)
  or lives alongside it (traffic split)
- Pixel IDs + CTA/form URLs (above)
- Green-light to commit, push, and deploy