# Emerald Contacts Data Audit

**Date:** 2026-05-14

## Executive Summary

| Issue | Count |
|-------|-------|
| Cross-bucket duplicates (same email in multiple role buckets) | **50** contacts |
| DNC + active bucket conflicts | **9** contacts (marked Do Not Contact but also in mso_executive or sso_executive) |
| Shared phone numbers (2+ contacts share same number) | **2,247** numbers affecting **~16k** contacts |
| Contacts moved to review file (phone-only shared/invalid) | **4,705** rows |
| Contacts without any phone number (deduped file) | **7,085** / 19,649 (36%) |
| Contacts without usable phone (no-phone + review file) | **11,790** / 24,354 (**48%**) |
| Bucket tag counts: sso_executive 7,603 / mso_executive 4,027 / marketing 2,363 / finance 892 / retail_sales 730 / DNC 909 | **16,524** total in v5 tagging file |

**Data sources:**
- `ghl_v5_tagging_import_email_only.csv` — 16,524 rows, email+tag buckets for GHL tagging
- `emerald-contacts.ghl.csv` — 27,320 rows, full source data (pre-dedup)
- `emerald-contacts.dedup.ghl.csv` — 19,649 rows, deduped GHL-safe import
- `emerald-contacts.dedup.review-shared-phone.csv` — 4,705 rows, phone-only shared/invalid flagged

---

## 1. Cross-Bucket Duplicates (Same Email in Multiple Buckets)

**50 unique emails** appear in 2+ different role buckets. These are contacts assigned to multiple categories (MSO executive, SSO executive, marketing, finance, retail sales, or Do Not Contact).

| Email | Name | Buckets | Rows |
|-------|------|---------|------|
| bj@cookiesre.com | | Do Not Contact, mso_executive | 5 |
| phvesq@gmail.com | | mso_executive, sso_executive | 5 |
| queen@soldistro.com | | mso_executive, sso_executive | 3 |
| gdinla@proton.me | | sso_executive, sso_finance | 3 |
| thebabyloncompany@gmail.com | | mso_executive, sso_executive | 3 |
| altaherbllc@gmail.com | | mso_executive, sso_executive | 3 |
| sveta@citrushill.org | | mso_executive, sso_executive | 3 |
| mike@arcadewellness.org | | mso_executive, mso_finance | 3 |
| nick@highlinedistro.com | | mso_executive, sso_executive | 3 |
| jmendonca@tokenfarmsinc.com | | mso_executive, mso_marketing | 2 |
| joey@theflowery.co | | Do Not Contact, mso_executive | 2 |
| john@novafarms.com | | Do Not Contact, mso_executive | 2 |
| karen.duval@crescolabs.com | | mso_executive, mso_retail_sales | 2 |
| kelsey@thefirestation.com | | mso_executive, mso_marketing | 2 |
| michael.bang@calyxpeak.com | | mso_executive, mso_finance | 2 |
| 17325muskratinc@gmail.com | | sso_executive, sso_finance | 2 |
| jeff@simplysolventless.ca | | mso_executive, mso_marketing | 2 |
| richard@710labs.com | | Do Not Contact, mso_executive | 2 |
| samiy1827@gmail.com | | mso_executive, mso_finance | 2 |
| shivvers@shivvers.com | | sso_executive, sso_marketing | 2 |
| smithunlimited@gmail.com | | mso_retail_sales, sso_finance | 2 |
| soufyan@edenenterprises.com | | Do Not Contact, mso_executive | 2 |
| theloadedbowl420@gmail.com | | sso_executive, sso_finance | 2 |
| tony@sensibrands.ca | | mso_executive, mso_marketing | 2 |
| nate@jettyextracts.com | | Do Not Contact, mso_executive | 2 |
| home4u4life@gmail.com | | mso_executive, sso_finance | 2 |
| greenlifealaska@gmail.com | | mso_executive, sso_executive | 2 |
| triphoffman@bodyandmind.com | | mso_executive, mso_retail_sales | 2 |
| adam@hgremedies.com | | Do Not Contact, sso_executive | 2 |
| akoudijs@hennep.com | | sso_executive, sso_retail_sales | 2 |
| allyfeiler@gmail.com | | mso_executive, sso_executive | 2 |
| andrew@missiondispensaries.com | | mso_executive, mso_marketing | 2 |
| andrew@mockingbird-holdings.com | | sso_executive, sso_finance | 2 |
| bradpalmer@cannacruz.com | | sso_executive, sso_finance | 2 |
| brandon@goldenbarn.com | | sso_executive, sso_marketing | 2 |
| cantodiemllc@gmail.com | | mso_executive, mso_marketing | 2 |
| caren.woodson@kivaconfections.com | | Do Not Contact, mso_executive | 2 |
| hciventures@gmail.com | | sso_executive, sso_finance | 2 |
| chris@levelblends.com | | Do Not Contact, mso_executive | 2 |
| complianceleadership@ethoscannabis.com | | Do Not Contact, mso_executive | 2 |
| cristyearanguiz@gmail.com | | mso_executive, sso_executive | 2 |
| dan@riversidecompany.com | | sso_executive, sso_marketing | 2 |
| daniel@capeanncannabis.com | | sso_executive, sso_retail_sales | 2 |
| daniel@greenwayvegas.com | | mso_executive, sso_executive | 2 |
| dankulchin@yahoo.com | | sso_executive, sso_finance | 2 |
| david@luckyleaf.co | | mso_executive, mso_retail_sales | 2 |
| dcarr@blossommj.com | | mso_executive, sso_executive | 2 |
| exhalence@yahoo.com | | sso_executive, sso_finance | 2 |
| collectivemindsca@gmail.com | | mso_executive, sso_executive | 2 |
| william@bloomnetwork.io | | Do Not Contact, sso_executive | 2 |

**Notable cross-bucket patterns:**
- `mso_executive + sso_executive` — most common (same person in both MSO and SSO executive lists)
- `mso_executive + mso_finance` or `mso_executive + mso_marketing` — person wears multiple hats at same company
- `Do Not Contact + mso_executive` — 9 contacts flagged both as DNC and active (needs resolution)

---

## 2. Shared Phone Numbers

**2,247 unique phone numbers** are shared by 2+ contacts. Most are corporate switchboards where many employees share the same main line.

### Top shared numbers (company main lines)

| Phone | Contacts | Example Companies |
|-------|----------|-------------------|
| +1 877 303 0741 | 114 | Data enrichment source tag (peopledatalabs — flagged as non-phone in source data) |
| +1 781 451 0117 | 70 | Likely corporate switchboard |
| +1 319 355 8843 | 56 | Likely corporate switchboard |
| +1 312 338 7860 | 56 | Likely corporate switchboard |
| +1 614 407 3111 | 41 | Cresco Labs main line |
| +1 415 672 4450 | 40 | Caliva main line |
| +1 800 332 8383 | 38 | General corporate line |
| +1 212 697 1000 | 36 | NYC-area company line |
| +1 860 999 3470 | 36 | Likely corporate switchboard |
| +1 312 929 0993 | 36 | Likely corporate switchboard |
| +1 855 790 8169 | 35 | Cresco Labs related |
| +1 707 599 0610 | 33 | Cresco Labs / Sunnyside related |
| +1 800 432 2558 | 33 | Caliva related |
| +1 212 460 1900 | 32 | Columbia Care main line |
| +1 800 484 0303 | 32 | Cresco Labs related |
| +1 860 717 9333 | 31 | General corporate line |
| +1 800 268 4623 | 31 | Dispensary chain line |
| +1 860 246 4673 | 28 | General corporate line |
| +1 740 672 3706 | 27 | Likely corporate switchboard |
| +1 514 843 3632 | 27 | Canadian company line |

**16,139 distinct contacts** have a phone number that's also associated with another contact. The build script already flagged 4,705 rows into `emerald-contacts.dedup.review-shared-phone.csv` as `phone_only_shared_or_invalid`.

---

## 3. Contacts Without Phone Numbers

### In deduped file (`emerald-contacts.dedup.ghl.csv` — 19,649 rows)

| Source File | Total | No Phone | % |
|-------------|-------|----------|---|
| Cannabis-Retail-MSO-Executive-1 | 3,564 | 1,870 | 52.5% |
| Cannabis-Retail-MSO-Executive-2 | 4,202 | 2,663 | **63.4%** |
| Cannabis-Retail-MSO-Marketing-1 | 717 | 321 | 44.8% |
| Cannabis-Retail-SSO-Executive-1 | 7,154 | 2,606 | 36.4% |
| Cannabis-Retail-SSO-Executive-2 | 9,255 | 3,731 | 40.3% |
| Cannabis-Retail-SSO-Marketing-1 | 2,428 | 1,098 | 45.2% |
| **Total** | **27,320** | **12,289** | **45.0%** |

### Field coverage in deduped file

| Coverage | Count |
|----------|-------|
| Has phone (Phone or Corporate_Phone) | 12,564 |
| Has email | 16,250 |
| Has both phone and email | 9,165 |
| No phone at all (deduped file only) | 7,085 |
| Review file (phone-only shared/invalid) | 4,705 |
| **Total without usable phone** | **11,790 / 24,354 (48.4%)** |

---

## 4. Tag Bucket Distribution (v5 tagging file — 16,524 rows)

| Bucket | Count |
|--------|-------|
| sso_executive | 7,603 |
| mso_executive | 4,027 |
| sso_marketing | 1,723 |
| Do Not Contact | 909 |
| mso_marketing | 640 |
| sso_finance | 595 |
| sso_retail_sales | 410 |
| mso_retail_sales | 320 |
| mso_finance | 297 |
| **Total** | **16,524** |

---

## 5. Original Source File Summary

| Metric | Value |
|--------|-------|
| Source rows (6 files) | 33,561 |
| Importable rows | 27,320 |
| Skipped (missing email + phone) | 6,241 |
| Deduped before phone safety filter | 24,354 |
| Deduped GHL-safe import | 19,649 |
| Moved to review (shared/invalid phone) | 4,705 |
| Deduplication collisions resolved | 2,966 |

---

## Key Takeaways

1. **50 cross-bucket dupes** need dedup resolution — decide which bucket takes priority for each
2. **9 DNC + active bucket conflicts** need resolution (contacts marked Do Not Contact but also in an active bucket)
3. **48% lack usable phone numbers** — MSO-Executive-2 is worst at 63.4% no-phone; enrichment needed if SMS outreach required
4. **~16k contacts share phones** with others — largely corporate switchboards, flagged appropriately in the review file
