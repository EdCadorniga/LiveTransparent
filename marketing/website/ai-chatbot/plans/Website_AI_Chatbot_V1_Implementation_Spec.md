# Website AI Chatbot V1 Implementation Spec

## Objective
Build a custom website chatbot backed by n8n that answers only approved FAQ/service questions, captures lead details, and routes qualified conversations into the existing Cameron booking path that produces `SQL` and `Sales -> Discovery Scheduled`.

## Locked Rules
- The website widget is custom, not a GHL-native chat widget.
- The `Book a Call` action is always visible.
- The bot can answer up to `3` questions before a hard gate.
- After the visitor successfully books on the approved calendar, the bot can answer up to `2` more questions.
- A booking click alone does not unlock the extra answers; the booking must be confirmed.
- The bot must not reveal trade secrets, internal processes, or unsupported claims.

## Required Lead Capture
- Required:
  - `first_name`
  - `last_name`
  - `email`
  - `phone`
- Optional:
  - promotions consent checkbox

## Approved Booking Path
- Primary booking calendar: `SrtXcFVyea7pFl3nTiIK`
- Canonical direct booking URL: `https://api.leadconnectorhq.com/widget/booking/SrtXcFVyea7pFl3nTiIK`
- Website `Book a Call` / `Book a Demo` CTAs should open this GHL widget directly or embed it. Do not put the legacy hero form or Calendly embed in front of it.
- Reuse the already verified downstream booking flow that:
  - adds tag `SQL`
  - moves or creates the opportunity in `Sales -> Discovery Scheduled`

## Initial Architecture
### Widget
- Floating website chat launcher
- Message list and input composer
- Always-visible booking CTA
- Lead-capture step after the 3-question gate
- Booking confirmation polling/status step

### Default Greeting and Starter Buttons
- Default greeting:
  - `Hi, I’m the LiveTransparent assistant. I can help with common questions about our services, who we work with, and getting you booked with Cameron.`
- Starter buttons:
  - `Book a Call`
  - `Services`
  - `Who We Help`
  - `Paid Ads`
  - `Pricing`
  - `Why Us?`
- Internal button intent mapping:
  - `Book a Call` -> immediate booking CTA
  - `Services` -> `What services do you offer?`
  - `Who We Help` -> `Who do you work best with?`
  - `Paid Ads` -> `Can you help with compliant paid ads for regulated brands?`
  - `Pricing` -> `How does your pricing work?`
  - `Why Us?` -> `What makes LiveTransparent different from other agencies?`

### n8n
- One primary chatbot workflow with webhook endpoints for:
  - session start
  - inbound message
  - lead capture
  - booking status check
- Child logic/modules for:
  - session state
  - retrieval
  - LLM response generation
  - GHL contact upsert
  - transcript logging

### Infrastructure
- Keep the existing `postgres/` service for transactional chatbot data.
- Add a separate `Qdrant` service in Coolify for vector retrieval.
- Prefer internal Coolify network communication between `n8n`, `postgres`, and `qdrant`.
- Do not modify the current Postgres service to support `pgvector` in v1.

### Storage and Retrieval
- Use the existing Postgres service for:
  - chat sessions
  - question-count and booking-gate state
  - messages/transcripts
  - lead-capture audit records
  - optional booking confirmation cache
- Use Qdrant for:
  - approved FAQ embeddings
  - approved service-detail embeddings
  - approved document chunk embeddings
- Retrieval flow:
  - query Qdrant for the top approved chunks
  - pass only a small, filtered result set into the LLM
  - never expose broad internal docs or process material
- Keep chatbot business rules in Postgres-backed workflow state, not only in AI memory nodes.

## LLM Recommendation
- Default API recommendation for this build: OpenRouter with paid-primary fallback routing.
- Keep provider configuration env-driven so the model vendor can be swapped later.
- Do not hardcode API keys in workflow JSON or widget files.
- The chatbot should use a narrow toolset rather than a broad autonomous agent pattern:
  - retrieve approved content from Qdrant
  - save lead details
  - check booking status
  - return the approved booking link
- Approved production LLM stack:
  - Primary: `deepseek/deepseek-v3.2`
  - Secondary: `qwen/qwen3.5-9b`
  - No free fallback in the initial production setup
- Free-model routing can be revisited later, but it is not part of the default v1 production design.
- Expected chatbot spend should remain comfortably below the current `$1.50/day` target under normal FAQ and gated-booking usage, but model pricing should still be re-verified at implementation time.

## Prompt Requirements
- Answer only from approved FAQ/service content and explicitly allowed business facts.
- Refuse unsupported, internal, speculative, or secret-seeking questions.
- Redirect off-scope or high-intent visitors to booking with Cameron.
- Keep answers concise and commercial, not operational.

## Deliverables To Keep In This Workspace
- `plans/`: specs, prompts, rollout notes
- `n8n-workflow/`: workflow JSON, env notes, import/export docs
- `qdrant/`: Coolify deployment assets, env template, and service notes
- `widget/`: JS/CSS/embed assets for the site
- `knowledgebase/`: approved FAQ and future RAG source files
- `artifacts/`: screenshots, sample payloads, test transcripts
- `tests/`: scenario checklists and QA runs
