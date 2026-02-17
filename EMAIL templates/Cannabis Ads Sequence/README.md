# Cannabis Ads Email HTML Templates

This folder is the editable source of truth for sequence content and order.

## Cadence (Locked)
- `D0`, `D2`, `D5`, `D8`, `D12`

## Sequence Variants (A/B)

### Variant A - Top-to-Bottom in `Email Sequence.docx`
1. `01-cannabis-ads-1-v5.html` (`Cannabis Ads-1-V5`)
2. `03-cannabis-ads-1-v1.html` (`Cannabis Ads-1-V1`)
3. `02-cannabis-ads-3-v5.html` (`Cannabis Ads-3-V5`)
4. `05-cannabis-ads-4-v1.html` (`Cannabis Ads-4-V1`)
5. `04-cannabis-ads-5-v1.html` (`Cannabis Ads-5-V1`)

### Variant B - Apollo Strategic Order
1. `01-cannabis-ads-1-v5.html` (`Cannabis Ads-1-V5`)
2. `02-cannabis-ads-3-v5.html` (`Cannabis Ads-3-V5`)
3. `03-cannabis-ads-1-v1.html` (`Cannabis Ads-1-V1`)
4. `04-cannabis-ads-5-v1.html` (`Cannabis Ads-5-V1`)
5. `05-cannabis-ads-4-v1.html` (`Cannabis Ads-4-V1`)

## Live Link Targets Used in Templates
- Primary CTA (all 5 templates): `https://calendly.com/transparentecom/how-to-run-cannabis-ads-on-meta`
- Resource link (only email 5): `https://livetransparent.com/resources/`

## Local File to GHL Template Mapping
1. `01-cannabis-ads-1-v5.html` -> `01 - Cannabis Ads-1-V5 - Say Goodbye To Censored Cannabis Ads On Meta`
2. `02-cannabis-ads-3-v5.html` -> `02 - Cannabis Ads-3-V5 - Why Do Ad Agencies Suck`
3. `03-cannabis-ads-1-v1.html` -> `03 - Cannabis Ads-1-V1 - Breakthrough Alert`
4. `04-cannabis-ads-5-v1.html` -> `04 - Cannabis Ads-5-V1 - Let's Talk About Failure`
5. `05-cannabis-ads-4-v1.html` -> `05 - Cannabis Ads-4-V1 - Save $200k On EBITA`

## Link Hygiene Status
- `https://livetransparent.com/resources/`: reachable (web fetch check passed).
- Calendly link: present consistently in all templates; automated health-check from this environment is inconclusive due external TLS/bot restrictions, so final click validation should be done in browser before send.

## Editing Workflow
1. Edit the needed `.html` file in this folder.
2. Preserve CTA targets unless intentionally changing campaign destination.
3. Re-upload/update the corresponding GHL email template.
4. Re-run link check for every external `https://` URL before activating sequence.

## Template Build Notes
- All templates include inline CTA hyperlinks in body copy.
- All templates include a `Book a Meeting` button above signature.
- Footer logo uses embedded base64 from `livetransparent_logo.png`.
