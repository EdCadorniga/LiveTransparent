-- Voice agent queue + transcript schema (v1)

create table if not exists voice_call_queue (
  queue_id uuid primary key,
  contact_id text not null,
  phone_e164 text not null,
  campaign_id text not null,
  lead_timezone text,
  status text not null default 'pending',
  dnc boolean not null default false,
  max_attempts integer not null default 3,
  attempt_count integer not null default 0,
  last_attempt_at timestamptz,
  next_attempt_at timestamptz,
  locked_at timestamptz,
  lock_owner text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_voice_call_queue_status_next_attempt
  on voice_call_queue(status, next_attempt_at);

create table if not exists voice_call_attempt (
  call_id uuid primary key,
  queue_id uuid not null references voice_call_queue(queue_id),
  contact_id text not null,
  provider_call_id text,
  idempotency_key text not null unique,
  started_at timestamptz not null default now(),
  ended_at timestamptz,
  disposition text not null,
  qualified_intent_fit boolean not null default false,
  booking_attempted boolean not null default false,
  booking_result text not null default 'not_attempted',
  handoff_required boolean not null default false,
  handoff_reason text,
  summary text,
  transcript_url text,
  recording_url text,
  created_at timestamptz not null default now()
);

create index if not exists idx_voice_call_attempt_queue_id
  on voice_call_attempt(queue_id);

create table if not exists voice_call_transcript_turn (
  turn_id bigserial primary key,
  call_id uuid not null references voice_call_attempt(call_id) on delete cascade,
  turn_index integer not null,
  speaker text not null,
  utterance text not null,
  timestamp_utc timestamptz not null,
  created_at timestamptz not null default now()
);

create unique index if not exists idx_voice_call_transcript_turn_unique
  on voice_call_transcript_turn(call_id, turn_index);
