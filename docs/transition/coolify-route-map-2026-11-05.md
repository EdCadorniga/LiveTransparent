# Coolify/Traefik route map — 2026-11-05

Captured from running-container Docker labels only (`docker inspect … Config.Labels`),
supplemented by the generated proxy dynamic directory listing recorded in the ledger
note. Traefik `coolify-proxy` discovers routes via Docker labels; the dynamic directory
contains only `default_redirect_503.yaml` (catch-all 503, router priority −1000) and a
Caddyfile stub that imports `*.caddy` (unused when Traefik is the provider).
Nothing was changed.

| container | host rule | port | network pinning | priority/cert/gzip extras |
|---|---|---|---|---|
| `coolify` | — | — | — | — |
| `coolify-db` | — | — | — | — |
| `coolify-redis` | — | — | — | — |
| `coolify-sentinel` | — | — | — | — |
| `reports-livetransparent` | `Host(`reports.livetransparent.com`) && PathPrefix(`/`)` | 80 | — | traefik.http.middlewares.gzip.compress, traefik.http.routers.https-0-v3ud1lum1svamymuor21upog.middlewares, traefik.http.routers.https-0-v3ud1lum1svamymuor21upog.tls.certresolver |
| `n8n-runner-n44wksswcocwk88ogcog8c48` | — | — | — | — |
| `n8n-n44wksswcocwk88ogcog8c48` | `Host(`automations.livetransparent.com`)`, `Host(`automations.livetransparent.com`) && PathPrefix(`/`)` | 5678 | `coolify-shared` | traefik.http.middlewares.gzip-sse.compress.excludedcontenttypes, traefik.http.routers.https-0-n44wksswcocwk88ogcog8c48-n8n-5877.middlewares, traefik.http.routers.https-0-n44wksswcocwk88ogcog8c48-n8n-5877.tls.certresolver |
| `sales-navigator-media-sales-navigator-media-1` | `Host(`reports.livetransparent.com`) && PathPrefix(`/sales-navigator-attachments`)` | 8080 | `coolify-shared` | traefik.http.routers.sales-navigator-media.priority |
| `vkrlibgdjdi4u6iz8hokue00-200808650013` | `Host(`vkrlibgdjdi4u6iz8hokue00.89.117.21.29.sslip.io`) && PathPrefix(`/`)` | 80 | — | traefik.http.middlewares.gzip.compress, traefik.http.routers.http-0-vkrlibgdjdi4u6iz8hokue00.middlewares |
| `vkrlibgdjdi4u6iz8hokue00` | `Host(`vkrlibgdjdi4u6iz8hokue00.89.117.21.29.sslip.io`)` | 80 | — | traefik.http.routers.https-0-vkrlibgdjdi4u6iz8hokue00.tls.certresolver |
| `sample-landing-registry` | — | — | — | — |
| `postgres-uokgs4c04ko0s4scccg40cgg` | — | — | — | — |
| `coolify-proxy` | — | 8080 | — | — |

### Long-form label detail (all coolify-*/traefik-* labels, non-secret)

#### `coolify`
- `io.coolify.cloudflared.version=2026.10.3`
- `io.coolify.nginx.version=1.31.8-r1`
- `io.coolify.node.version=24.22.1`
- `io.coolify.php-uv.version=0.3.0`
- `io.coolify.postgresql-client.version=18`
#### `coolify-db`
#### `coolify-redis`
#### `coolify-sentinel`
- `coolify.managed=true`
#### `reports-livetransparent`
- `coolify.applicationId=1`
- `coolify.environmentName=production`
- `coolify.managed=true`
- `coolify.name=v3ud1lum1svamymuor21upog`
- `coolify.projectName=automations`
- `coolify.pullRequestId=0`
- `coolify.resourceName=reportslivetransparent-server`
- `coolify.serviceName=reportslivetransparent-server`
- `coolify.type=application`
- `coolify.version=4.1.2`
- `traefik.enable=true`
- `traefik.http.middlewares.gzip.compress=true`
- `traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https`
- `traefik.http.routers.http-0-v3ud1lum1svamymuor21upog.entryPoints=http`
- `traefik.http.routers.http-0-v3ud1lum1svamymuor21upog.middlewares=redirect-to-https`
- `traefik.http.routers.http-0-v3ud1lum1svamymuor21upog.rule=Host(`reports.livetransparent.com`) && PathPrefix(`/`)`
- `traefik.http.routers.http-0-v3ud1lum1svamymuor21upog.service=http-0-v3ud1lum1svamymuor21upog`
- `traefik.http.routers.https-0-v3ud1lum1svamymuor21upog.entryPoints=https`
- `traefik.http.routers.https-0-v3ud1lum1svamymuor21upog.middlewares=gzip`
- `traefik.http.routers.https-0-v3ud1lum1svamymuor21upog.rule=Host(`reports.livetransparent.com`) && PathPrefix(`/`)`
- `traefik.http.routers.https-0-v3ud1lum1svamymuor21upog.service=https-0-v3ud1lum1svamymuor21upog`
- `traefik.http.routers.https-0-v3ud1lum1svamymuor21upog.tls=true`
- `traefik.http.routers.https-0-v3ud1lum1svamymuor21upog.tls.certresolver=letsencrypt`
- `traefik.http.services.http-0-v3ud1lum1svamymuor21upog.loadbalancer.server.port=80`
- `traefik.http.services.https-0-v3ud1lum1svamymuor21upog.loadbalancer.server.port=80`
#### `n8n-runner-n44wksswcocwk88ogcog8c48`
- `coolify.environmentName=production`
- `coolify.managed=true`
- `coolify.name=n8n-runner-n44wksswcocwk88ogcog8c48`
- `coolify.projectName=automations`
- `coolify.pullRequestId=0`
- `coolify.resourceName=n8n`
- `coolify.service.subName=n8n-runner`
- `coolify.service.subType=application`
- `coolify.service.subUuid=iwec4ddsdjxondjwpszwv6uv`
- `coolify.serviceName=n8n-runner`
- `coolify.serviceUuid=n44wksswcocwk88ogcog8c48`
- `coolify.type=service`
- `coolify.version=4.5.0`
#### `n8n-n44wksswcocwk88ogcog8c48`
- `coolify.environmentName=production`
- `coolify.managed=true`
- `coolify.name=n8n-n44wksswcocwk88ogcog8c48`
- `coolify.projectName=automations`
- `coolify.pullRequestId=0`
- `coolify.resourceName=n8n`
- `coolify.service.subName=n8n`
- `coolify.service.subType=application`
- `coolify.service.subUuid=sosc444cssg4w0o4ccwoc8sg`
- `coolify.serviceName=n8n`
- `coolify.serviceUuid=n44wksswcocwk88ogcog8c48`
- `coolify.type=service`
- `coolify.version=4.5.0`
- `traefik.docker.network=coolify-shared`
- `traefik.enable=true`
- `traefik.http.middlewares.gzip-sse.compress.excludedcontenttypes=text/event-stream`
- `traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https`
- `traefik.http.routers.http-0-n44wksswcocwk88ogcog8c48-n8n-5877.entryPoints=http`
- `traefik.http.routers.http-0-n44wksswcocwk88ogcog8c48-n8n-5877.middlewares=redirect-to-https`
- `traefik.http.routers.http-0-n44wksswcocwk88ogcog8c48-n8n-5877.rule=Host(`automations.livetransparent.com`) && PathPrefix(`/`)`
- `traefik.http.routers.https-0-n44wksswcocwk88ogcog8c48-n8n-5877.entryPoints=https`
- `traefik.http.routers.https-0-n44wksswcocwk88ogcog8c48-n8n-5877.middlewares=gzip-sse`
- `traefik.http.routers.https-0-n44wksswcocwk88ogcog8c48-n8n-5877.rule=Host(`automations.livetransparent.com`) && PathPrefix(`/`)`
- `traefik.http.routers.https-0-n44wksswcocwk88ogcog8c48-n8n-5877.tls=true`
- `traefik.http.routers.https-0-n44wksswcocwk88ogcog8c48-n8n-5877.tls.certresolver=letsencrypt`
- `traefik.http.routers.n8n-automations.entrypoints=https`
- `traefik.http.routers.n8n-automations.rule=Host(`automations.livetransparent.com`)`
- `traefik.http.routers.n8n-automations.service=n8n-automations`
- `traefik.http.routers.n8n-automations.tls=true`
- `traefik.http.services.n8n-automations.loadbalancer.server.port=5678`
#### `sales-navigator-media-sales-navigator-media-1`
- `traefik.docker.network=coolify-shared`
- `traefik.enable=true`
- `traefik.http.routers.sales-navigator-media.entrypoints=https`
- `traefik.http.routers.sales-navigator-media.priority=100`
- `traefik.http.routers.sales-navigator-media.rule=Host(`reports.livetransparent.com`) && PathPrefix(`/sales-navigator-attachments`)`
- `traefik.http.routers.sales-navigator-media.tls=true`
- `traefik.http.services.sales-navigator-media.loadbalancer.server.port=8080`
#### `vkrlibgdjdi4u6iz8hokue00-200808650013`
- `coolify.applicationId=2`
- `coolify.environmentName=production`
- `coolify.managed=true`
- `coolify.name=vkrlibgdjdi4u6iz8hokue00`
- `coolify.projectName=automations`
- `coolify.pullRequestId=0`
- `coolify.resourceName=sample-landing-page-review`
- `coolify.serviceName=sample-landing-page-review`
- `coolify.type=application`
- `coolify.version=4.3.23`
- `traefik.enable=true`
- `traefik.http.middlewares.gzip.compress=true`
- `traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https`
- `traefik.http.routers.http-0-vkrlibgdjdi4u6iz8hokue00.entryPoints=http`
- `traefik.http.routers.http-0-vkrlibgdjdi4u6iz8hokue00.middlewares=gzip`
- `traefik.http.routers.http-0-vkrlibgdjdi4u6iz8hokue00.rule=Host(`vkrlibgdjdi4u6iz8hokue00.89.117.21.29.sslip.io`) && PathPrefix(`/`)`
- `traefik.http.routers.http-0-vkrlibgdjdi4u6iz8hokue00.service=http-0-vkrlibgdjdi4u6iz8hokue00`
- `traefik.http.services.http-0-vkrlibgdjdi4u6iz8hokue00.loadbalancer.server.port=80`
#### `vkrlibgdjdi4u6iz8hokue00`
- `coolify.environmentName=production`
- `coolify.managed=true`
- `coolify.name=vkrlibgdjdi4u6iz8hokue00`
- `coolify.projectName=automations`
- `coolify.resourceName=Sample-Landing-Page-Review`
- `coolify.serviceName=sample-landing-page-review`
- `coolify.type=application`
- `traefik.enable=true`
- `traefik.http.routers.http-0-vkrlibgdjdi4u6iz8hokue00.entryPoints=http`
- `traefik.http.routers.http-0-vkrlibgdjdi4u6iz8hokue00.rule=Host(`vkrlibgdjdi4u6iz8hokue00.89.117.21.29.sslip.io`)`
- `traefik.http.routers.http-0-vkrlibgdjdi4u6iz8hokue00.service=http-0-vkrlibgdjdi4u6iz8hokue00`
- `traefik.http.routers.https-0-vkrlibgdjdi4u6iz8hokue00.entryPoints=https`
- `traefik.http.routers.https-0-vkrlibgdjdi4u6iz8hokue00.rule=Host(`vkrlibgdjdi4u6iz8hokue00.89.117.21.29.sslip.io`)`
- `traefik.http.routers.https-0-vkrlibgdjdi4u6iz8hokue00.tls=true`
- `traefik.http.routers.https-0-vkrlibgdjdi4u6iz8hokue00.tls.certresolver=letsencrypt`
- `traefik.http.services.http-0-vkrlibgdjdi4u6iz8hokue00.loadbalancer.server.port=80`
- `traefik.http.services.https-0-vkrlibgdjdi4u6iz8hokue00.loadbalancer.server.port=80`
#### `sample-landing-registry`
#### `postgres-uokgs4c04ko0s4scccg40cgg`
- `coolify.environmentName=production`
- `coolify.managed=true`
- `coolify.name=postgres-uokgs4c04ko0s4scccg40cgg`
- `coolify.projectName=automations`
- `coolify.pullRequestId=0`
- `coolify.resourceName=postgres-shared`
- `coolify.service.subId=1`
- `coolify.service.subName=postgres`
- `coolify.service.subType=database`
- `coolify.serviceId=1`
- `coolify.serviceName=postgres`
- `coolify.type=service`
- `coolify.version=4.1.2`
#### `coolify-proxy`
- `coolify.managed=true`
- `coolify.proxy=true`
- `traefik.enable=true`
- `traefik.http.routers.traefik.entrypoints=http`
- `traefik.http.routers.traefik.service=api@internal`
- `traefik.http.services.traefik.loadbalancer.server.port=8080`

### Observations (2026-11-05)
- `reports.livetransparent.com` HTTP service points at the reports container's own nginx (port 80),
  which then proxies the known API/report paths onward (see `reports/nginx.conf`); the
  `/sales-navigator-attachments/*` path is instead served by the
  `sales-navigator-media-*` container (router priority 100 beats the reports catch-approach).
- `automations.livetransparent.com` HTTP service points at n8n port 5678 with a `gzip-sse`
  middleware on the HTTPS router and `traefik.docker.network=coolify-shared` pinning.
- Two containers share the same host rule for the sample landing page preview
  (`vkrlibgdjdi4u6iz8hokue00-200808650013` and `vkrlibgdjdi4u6iz8hokue00` on the
  `vkrlibgdjdi4u6iz8hokue00.89.117.21.29.sslip.io` host); both have `traefik.enable=true`,
  so request routing between them for the http entrypoint is ambiguous — record as an
  owner decision/check (preview-only impact, not a live product domain).
- `sample-landing-registry` runs without any proxy route.
- Internal Coolify components (`coolify`, `coolify-db`, `coolify-redis`, `coolify-proxy`,
  `coolify-sentinel`, `postgres-shared`, `n8n`/`n8n-runner` UI) do not expose HTTP via
  this proxy (`postgres`/redis DBs listen internally only; n8n's DB and the runner
  communicate over the Docker networks documented earlier).
- TLS 4.1.2/4.5.0 Coolify versions are recorded on labels; no upgrade authorized.
