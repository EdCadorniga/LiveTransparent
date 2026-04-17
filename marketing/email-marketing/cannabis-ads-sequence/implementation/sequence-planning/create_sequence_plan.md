Below are prompt templates you can use with your GHL MCP to reliably **plan, validate, and then create** sequences (and the supporting assets) without guessing. Theyre written to force: required inputs, deterministic outputs, and idempotent behavior.

---

## 1) Inventory what the MCP can actually do (capability probe)

```text
You are connected to the GoHighLevel MCP.

List the exact tools/endpoints you expose that relate to:
- sequences/campaigns (create, update, list, get)
- sequence steps/events (create, update, list, delete)
- email templates (create, update, list, get)
- SMS templates (create, update, list, get)
- workflows (create/update/enroll) if sequences are triggered via workflows
- location/sub-account context switching

For each tool: show name, required parameters, optional parameters, and an example payload.
Do not create anything. Output as JSON.
```

---

## 2) Define a Sequence Build Spec (one source of truth)

```text
Create a Sequence Build Spec for GHL that is sufficient to create a full sequence end-to-end.

Inputs:
- location_id: {{LOCATION_ID}}
- sequence_name: {{NAME}}
- from_name: {{FROM_NAME}}
- from_email: {{FROM_EMAIL}}
- reply_to: {{REPLY_TO}}
- timezone: {{TZ}}
- sending_domain: {{SENDING_DOMAIN}}
- stop_on_reply: true
- stop_on_bounce: true
- max_emails_per_day: {{N}}
- business_context: {{CONTEXT}}
- audience_definition: {{AUDIENCE}}
- compliance_notes: {{COMPLIANCE}}

Sequence steps required (draft):
1) email (delay 0)
2) wait {{HOURS_1}} hours
3) email
4) wait {{HOURS_2}} hours
5) email

For each email: provide subject, preview text, plain-text body, and HTML body.
Return:
- build_spec JSON with stable IDs for each step (e.g., step_key)
- validation rules (required fields + constraints)
Do not call any MCP tools yet.
```

---

## 3) Preflight validation against the live account (no writes)

```text
Using the GHL MCP, perform a preflight check for this build spec:

{{PASTE_BUILD_SPEC_JSON}}

Checks:
- location exists and is accessible
- sending domain is verified for {{SENDING_DOMAIN}} (or detect how to check)
- from_email is allowed/supported
- required assets exist or will be created (templates, etc.)
- naming collisions: detect if a sequence with the same name already exists in this location
- identify any fields that are not supported by available MCP tools

Return:
- preflight_report JSON
- a deterministic execution_plan (ordered list of tool calls) for creation
Do not create or update anything.
```

---

## 4) Create sequence + steps (idempotent, safe reruns)

```text
Execute the creation plan from the preflight report.

Rules:
- Idempotent: if the sequence already exists (same name), do not create a duplicate.
- If it exists, update it to match the build spec (diff-based).
- Ensure step order matches build_spec step_key ordering.
- Use stable identifiers where possible; if platform returns IDs, store them in the final output mapping.

Return:
- created_or_updated: true/false
- sequence_id
- step_id_map: { step_key: step_id }
- any warnings or partial failures with exact API/tool error payloads
Proceed with tool calls now.
```

---

## 5) Dry-run diff mode (recommended before writes)

```text
Given this build spec:

{{PASTE_BUILD_SPEC_JSON}}

And the existing live sequence (if present), produce a diff-only plan:
- what will be created
- what will be updated
- what will be deleted (avoid deletions unless explicitly required)

Output:
- diff JSON
- execution_plan JSON
Do not call any create/update/delete tools.
```

---

## 6) Add enrollment trigger via workflow (if thats how you enroll)

```text
Create or update a workflow that enrolls contacts into the sequence:

Inputs:
- location_id: {{LOCATION_ID}}
- workflow_name: "Enroll into {{SEQUENCE_NAME}}"
- trigger: {{TRIGGER_TYPE}} (e.g., tag added, pipeline stage changed, form submitted)
- trigger_filter: {{FILTERS}}
- action: enroll contact into sequence_id {{SEQUENCE_ID}}
- guardrails:
  - do not enroll if contact is already active in this sequence
  - do not enroll if DND = true
  - do not enroll if missing email

Return workflow_id and validation output.
Proceed with tool calls now.
```

---

## 7) Verification prompt (confirm its really correct)

```text
Verify the created sequence matches the build spec exactly:

{{PASTE_BUILD_SPEC_JSON}}

Fetch:
- sequence details
- all steps/events
- template bodies (if referenced)
- stop conditions / settings where available

Return:
- verification_report JSON with pass/fail per field
- any mismatches with exact paths (e.g., steps[2].subject)
No writes.
```

---

## 8) Prompt for reusable Sequence Factory (bulk creation)

```text
You are a sequence factory for GHL MCP.

Goal: create N sequences using the same structure but different copy and audiences.

Inputs:
- location_id: {{LOCATION_ID}}
- base_structure: {{PASTE_BASE_STRUCTURE_JSON}}
- variants: [
  { name, audience_definition, step_copy_overrides },
  ...
]

For each variant:
- generate build_spec
- preflight (no writes)
- produce execution_plan (no writes)

Return a single JSON array of {variant_name, build_spec, preflight_report, execution_plan}.
```

---

### Practical tip (to avoid MCP ambiguity)

If your MCP tool names arent stable, use this prefix in every prompt:

```text
If any required tool/parameter is uncertain or missing, STOP and return:
{ "missing": [...], "need_from_user": [...] }
Do not guess.
```

If you paste your MCPs tool list (from prompt #1), I can tailor these prompts to your exact function names and required parameters so you can run them verbatim.
