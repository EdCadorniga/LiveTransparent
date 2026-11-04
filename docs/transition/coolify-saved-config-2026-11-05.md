# Coolify saved-configuration read — 2026-11-05
Read via SSH channel-forwarded GETs to the Coolify panel api/v1.
Structural facts only (service names, image tags, networks, volumes, env NAMES).
No env values, compose dumps, credentials, or configuration changes. All requests were GET.

## Projects
- project `vw4sw40o4kkk800okwww0csg` name: automations; environments: []
## Applications
| kind | uuid | name | status | domains | destination |
|---|---|---|---|---|---|
| application | `vkrlibgdjdi4u6iz8hokue00` | Sample Landing Page Review | running:unknown | http://vkrlibgdjdi4u6iz8hokue00.89.117.21.29.sslip.io | None |
| application | `v3ud1lum1svamymuor21upog` | reports.livetransparent_server | running:unknown | https://reports.livetransparent.com | None |
| service | `uokgs4c04ko0s4scccg40cgg` | postgres-shared | running:healthy | None | None |
| service | `n44wksswcocwk88ogcog8c48` | n8n | running:unknown | None | None |

## Saved Compose structural facts

### service postgres-shared (`uokgs4c04ko0s4scccg40cgg`) — Coolify variable references (names): []
- service `postgres`
  - image: `postgres:17.7`
  - restart: unless-stopped; healthcheck present: True
  - networks: ['coolify-shared']
  - volumes: [{'binding': 'postgres_data:/var/lib/postgresql/data'}]
  - env NAMES: ['POSTGRES_DB', 'POSTGRES_PASSWORD', 'POSTGRES_USER']
  - depends_on: None; extra_hosts: None

### service n8n (`n44wksswcocwk88ogcog8c48`) — Coolify variable references (names): []
- service `n8n`
  - image: `n8nio/n8n:2.44.6`
  - restart: unless-stopped; healthcheck present: False
  - networks: ['coolify-shared']
  - volumes: [{'binding': 'n8n_data:/home/node/.n8n'}]
  - env NAMES: ['DB_CONNECTION_ACQUISITION_TIMEOUT_MS', 'DB_PING_INTERVAL_SECONDS', 'DB_PING_MAX_FAILURES_BEFORE_RECOVERY', 'DB_PING_TIMEOUT_MS', 'DB_POSTGRESDB_CONNECTION_TIMEOUT', 'DB_POSTGRESDB_IDLE_CONNECTION_TIMEOUT', 'DB_POSTGRESDB_MAX_CONNECTION_LIFETIME_MS', 'DB_POSTGRESDB_POOL_SIZE', 'DB_POSTGRESDB_STATEMENT_TIMEOUT', 'DB_RECOVERY_BACKOFF_MAX_MS', 'DB_RECOVERY_BACKOFF_MIN_MS', 'EXECUTIONS_TIMEOUT', 'EXECUTIONS_TIMEOUT_MAX', 'N8N_CONCURRENCY', 'N8N_CONCURRENCY_PRODUCTION_LIMIT', 'N8N_RUNNERS_AUTH_TOKEN', 'N8N_RUNNERS_BROKER_LISTEN_ADDRESS', 'N8N_RUNNERS_MODE', 'N8N_RUNNERS_TASK_REQUEST_TIMEOUT', 'N8N_RUNNERS_TASK_TIMEOUT', 'NODE_FUNCTION_ALLOW_BUILTIN', 'NODE_FUNCTION_ALLOW_EXTERNAL']
  - depends_on: None; extra_hosts: None
- service `n8n-runner`
  - image: `None`
  - restart: unless-stopped; healthcheck present: False
  - networks: ['coolify-shared']
  - volumes: []
  - env NAMES: ['N8N_RUNNERS_AUTH_TOKEN', 'N8N_RUNNERS_AUTO_SHUTDOWN_TIMEOUT', 'N8N_RUNNERS_MAX_CONCURRENCY', 'N8N_RUNNERS_TASK_BROKER_URI', 'N8N_RUNNERS_TASK_TIMEOUT', 'NODE_OPTIONS', 'NODE_PATH']
  - depends_on: ['n8n']; extra_hosts: None

## Application/deployment detail fields (source-of-deploy evidence)
- Sample Landing Page Review (`vkrlibgdjdi4u6iz8hokue00`): {"build_pack": "dockerimage", "docker_compose_location": "/docker-compose.yaml", "status": "running:unknown", "updated_at": "2026-11-04T17:50:37.000000Z", "git_repository": "coollabsio/coolify", "git_branch": "main", "git_commit_sha": "HEAD"}
- reports.livetransparent_server (`v3ud1lum1svamymuor21upog`): {"build_pack": "dockerfile", "docker_compose_location": "/docker-compose.yaml", "dockerfile_location": "/Dockerfile", "status": "running:unknown", "updated_at": "2026-11-04T17:50:37.000000Z", "git_repository": "EdCadorniga/LiveTransparent", "git_branch": "main", "git_commit_sha": "HEAD"}

## Repository Compose comparison facts (local parse of tracked `n8n/docker-compose.yml`)
- repo service `n8n`
  - image: `n8nio/n8n:2.44.6`; build: False
  - restart: unless-stopped; healthcheck present: False
  - networks: ['coolify-shared']
  - volumes: [{'binding': 'n8n_data:/home/node/.n8n'}]
  - env NAMES: ['DB_CONNECTION_ACQUISITION_TIMEOUT_MS', 'DB_PING_INTERVAL_SECONDS', 'DB_PING_MAX_FAILURES_BEFORE_RECOVERY', 'DB_PING_TIMEOUT_MS', 'DB_POSTGRESDB_CONNECTION_TIMEOUT', 'DB_POSTGRESDB_IDLE_CONNECTION_TIMEOUT', 'DB_POSTGRESDB_MAX_CONNECTION_LIFETIME_MS', 'DB_POSTGRESDB_POOL_SIZE', 'DB_POSTGRESDB_STATEMENT_TIMEOUT', 'DB_RECOVERY_BACKOFF_MAX_MS', 'DB_RECOVERY_BACKOFF_MIN_MS', 'EXECUTIONS_TIMEOUT', 'EXECUTIONS_TIMEOUT_MAX', 'N8N_CONCURRENCY', 'N8N_CONCURRENCY_PRODUCTION_LIMIT', 'N8N_RUNNERS_AUTH_TOKEN', 'N8N_RUNNERS_BROKER_LISTEN_ADDRESS', 'N8N_RUNNERS_MODE', 'N8N_RUNNERS_TASK_REQUEST_TIMEOUT', 'N8N_RUNNERS_TASK_TIMEOUT', 'NODE_FUNCTION_ALLOW_BUILTIN', 'NODE_FUNCTION_ALLOW_EXTERNAL']
- repo service `n8n-runner`
  - image: `None`; build: True
  - restart: unless-stopped; healthcheck present: False
  - networks: ['coolify-shared']
  - volumes: []
  - env NAMES: ['N8N_RUNNERS_AUTH_TOKEN', 'N8N_RUNNERS_AUTO_SHUTDOWN_TIMEOUT', 'N8N_RUNNERS_MAX_CONCURRENCY', 'N8N_RUNNERS_TASK_BROKER_URI', 'N8N_RUNNERS_TASK_TIMEOUT', 'NODE_OPTIONS', 'NODE_PATH']

**Saved vs repo summary (read from the facts above by the reviewer):** the saved n8n service shows image `n8nio/n8n:2.44.6`, network `coolify-shared`, volume `n8n_data:/home/node/.n8n`, no `extra_hosts`; the saved `n8n-runner` carries no image key (built from a build context) with `depends_on: [n8n]`. Any difference against the repo file above is recorded here at review time; both sets contain no secret values.

## Backup configuration probes
- GET /backups: dict keys ['docs', 'message']
- GET /instance/backups: dict keys ['docs', 'message']
- GET /backups/scheduled: dict keys ['docs', 'message']
- GET /teams: list of 1; first row keys: ['avatar_path', 'avatar_s3_storage_id', 'avatar_storage_type', 'created_at', 'description', 'id', 'is_build_server_fallback_enabled', 'is_mcp_server_enabled', 'is_two_factor_required', 'name', 'personal_team', 'show_boarding', 'updated_at']

## Panel version
- GET /utility/version: {"message": "Not found.", "docs": "https://coolify.io/docs"}
- GET /version: failed: http 200 non-json
- GET /ping: {"message": "Not found.", "docs": "https://coolify.io/docs"}
- read failed or unexpected shape: {'message': 'Not found.', 'docs': 'https://coolify.io/docs'}

**Open acceptance gaps (unchanged):** restore has never been tested; scheduled backup governance, off-host copies, and saved-vs-generated-vs-repo drift are recorded for owner review, not resolved.
