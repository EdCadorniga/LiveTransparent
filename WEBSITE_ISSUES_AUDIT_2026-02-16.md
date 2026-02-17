# Website Issues Audit (2026-02-16)

Source: Live Browser MCP review of `https://livetransparent.com/` and key linked pages.

## Critical

1. `/apply` page appears broken/stuck
- URL: `https://livetransparent.com/apply/`
- Observed: Header/footer render, but main application content does not visibly load; a loader state remains.
- Impact: Primary conversion path may be blocked.

## High

1. `Contact` nav link is unreliable on inner pages
- Example: `https://livetransparent.com/clients/`
- Observed: Nav item points to `#contact`; on tested inner pages this does not move to a clear contact section.
- Impact: Contact-intent users may fail to reach a form/CTA.

2. Footer email icon link is invalid
- Observed on multiple pages: link target is `mailto:` with no email address.
- Impact: Lost direct email inquiries.

## Medium

1. Compliance page URL inconsistency
- Observed: `https://livetransparent.com/compliance-ad-accounts` resolves to `https://livetransparent.com/compliance-ad-account/`
- Impact: Potential canonical/link consistency and analytics attribution issues.

2. Stale campaign parameter in Calendly links
- Observed examples include `month=2025-07` in CTA URLs.
- Impact: Outdated tracking context and possible user confusion.

## Low

1. Footer copyright year not current
- Observed: `© 2025` while audit date is 2026-02-16.

2. Some image alt text appears generic/non-descriptive
- Examples seen in resource listings: `image1`, `unnamed`.
- Impact: Reduced accessibility and weaker SEO metadata quality.

## SEO

1. Missing meta descriptions on key pages
- `https://livetransparent.com/apply/`
- `https://livetransparent.com/resources/`
- `https://livetransparent.com/clients/`
- `https://livetransparent.com/compliance-ad-account/`
- Impact: Weaker SERP snippet control and lower click-through potential.

2. Canonical/internal URL consistency issue
- Observed: `https://livetransparent.com/compliance-ad-accounts` resolves to `https://livetransparent.com/compliance-ad-account/`.
- Impact: Internal linking inconsistency and noisier analytics/SEO signals if both forms are used internally.

3. Generic image alt text in resource/blog listings
- Examples: `image1`, `unnamed`.
- Impact: Reduced image SEO relevance and accessibility quality.

4. Outdated campaign parameter in CTA links
- Example in live CTA URLs: `month=2025-07`.
- Impact: Tracking hygiene issue and potential user trust/clarity friction.

## Technical SEO Checks (Verified)

1. `robots.txt` is present and crawl-permissive
- URL: `https://livetransparent.com/robots.txt`
- Includes sitemap reference.

2. XML sitemap index is present
- URL: `https://livetransparent.com/sitemap_index.xml`
- Includes post/page/category/author sitemap entries.

## Pages Reviewed

- `https://livetransparent.com/`
- `https://livetransparent.com/apply/`
- `https://livetransparent.com/resources/`
- `https://livetransparent.com/clients/`
- `https://livetransparent.com/cannabis-marketing-in-2025-whats-working-and-whats-not/`
- `https://livetransparent.com/compliance-ad-accounts`
