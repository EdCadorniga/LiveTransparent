# Coolify Host Inventory — 2026-11-04

**Source:** read-only SSH queries to the Coolify VPS; commands list Docker metadata only.
**Boundary:** no container environment, service secrets, Compose contents, or application data were read.
**Docker server version:** 29.6.2

## Compose projects

| Project | Status | Compose file(s) |
|---|---|---|
| coolify-proxy | running(1) | /data/coolify/proxy/docker-compose.yml |
| n44wksswcocwk88ogcog8c48 | running(2) | /data/coolify/services/n44wksswcocwk88ogcog8c48/docker-compose.yml |
| sales-navigator-media | running(1) | /srv/livetransparent/sales-navigator-media/docker-compose.yml |
| source | running(3) | /data/coolify/source/docker-compose.yml,/data/coolify/source/docker-compose.prod.yml |
| uokgs4c04ko0s4scccg40cgg | running(1) | /data/coolify/services/uokgs4c04ko0s4scccg40cgg/docker-compose.yml |
| v3ud1lum1svamymuor21upog | running(1) | /data/coolify/applications/v3ud1lum1svamymuor21upog/docker-compose.yaml |
| vkrlibgdjdi4u6iz8hokue00 | running(1) | /artifacts/otslcb42ud0plok31ajdrman/docker-compose.yaml |

## Containers

| Name | Image | Status | Ports |
|---|---|---|---|
| coolify | coollabsio/coolify:4.6.0 | Up 13 hours (healthy) | 8000/tcp, 8443/tcp, 0.0.0.0:6001-6002->6001-6002/tcp, [::]:6001-6002->6001-6002/tcp, 9000/tcp, 0.0.0.0:8000->8080/tcp, [::]:8000->8080/tcp |
| coolify-db | postgres:15-alpine | Up 13 hours (healthy) | 5432/tcp |
| coolify-redis | redis:7-alpine | Up 13 hours (healthy) | 6379/tcp |
| hca8 | mcr.microsoft.com/playwright:v1.48.2-jammy | Exited (0) 5 days ago |  |
| hca7 | mcr.microsoft.com/playwright:v1.48.2-jammy | Exited (0) 5 days ago |  |
| hca6 | mcr.microsoft.com/playwright:v1.48.2-jammy | Exited (0) 5 days ago |  |
| hca5 | mcr.microsoft.com/playwright:v1.48.2-jammy | Exited (0) 5 days ago |  |
| hca4 | mcr.microsoft.com/playwright:v1.48.2-jammy | Exited (0) 5 days ago |  |
| hca3 | mcr.microsoft.com/playwright:v1.48.2-jammy | Exited (0) 5 days ago |  |
| hca2 | mcr.microsoft.com/playwright:v1.48.2-jammy | Exited (0) 5 days ago |  |
| hcm1 | mcr.microsoft.com/playwright:v1.48.2-jammy | Exited (0) 5 days ago |  |
| coolify-sentinel | coollabsio/sentinel:1.1.3 | Up 6 days (healthy) |  |
| reports-livetransparent | v3ud1lum1svamymuor21upog:executive-v1-20261019-opportunity-actions | Up 9 days | 80/tcp |
| n8n-runner-n44wksswcocwk88ogcog8c48 | n44wksswcocwk88ogcog8c48-n8n-runner | Up 9 days | 5680/tcp |
| n8n-n44wksswcocwk88ogcog8c48 | n8nio/n8n:2.44.6 | Up 9 days | 5678/tcp |
| sales-navigator-media-sales-navigator-media-1 | sales-navigator-media-sales-navigator-media | Up 2 weeks | 8080/tcp |
| vkrlibgdjdi4u6iz8hokue00-200808650013 | localhost:5000/livetransparent-sample-landing:review | Up 2 weeks | 80/tcp |
| vkrlibgdjdi4u6iz8hokue00 | localhost:5000/livetransparent-sample-landing:review | Up 2 weeks | 80/tcp |
| sample-landing-registry | registry:2 | Up 2 weeks | 127.0.0.1:5000->5000/tcp |
| postgres-uokgs4c04ko0s4scccg40cgg | postgres:17.7 | Up 2 weeks (healthy) | 5432/tcp |
| coolify-proxy | traefik:v3.6.11 | Up 2 weeks (healthy) | 0.0.0.0:80->80/tcp, [::]:80->80/tcp, 0.0.0.0:443->443/tcp, [::]:443->443/tcp, 0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp, 0.0.0.0:443->443/udp, [::]:443->443/udp |

## Networks

| Name | Driver | Scope |
|---|---|---|
| bridge | bridge | local |
| coolify | bridge | local |
| coolify-shared | bridge | local |
| host | host | local |
| n44wksswcocwk88ogcog8c48 | bridge | local |
| none | null | local |
| source_default | bridge | local |
| uokgs4c04ko0s4scccg40cgg | bridge | local |

## Volumes

| Name | Driver |
|---|---|
| 7663d54ed0c4a742f05bb16afc779dec68f1261611b9c7c303fe114ed11f8e26 | local |
| coolify-db | local |
| coolify-redis | local |
| n8n_data | local |
| n44wksswcocwk88ogcog8c48_n8n-data | local |
| uokgs4c04ko0s4scccg40cgg_postgres-data | local |

## Limitations

- This Docker snapshot is not a complete Coolify project/service configuration audit.
- Saved and generated Compose drift, volume-to-service ownership, domains, health-check definitions, backups, and restore procedures remain to be verified.
- Exited Playwright helper containers and the review landing-page stack are listed as observed; no cleanup or lifecycle change was made.
