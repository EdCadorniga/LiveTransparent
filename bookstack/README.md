# BookStack on Coolify

## What this provides
- Internal knowledgebase service using BookStack.
- Separate MariaDB container.
- Traefik HTTPS routing over `coolify-shared` network.

## Files
- `bookstack/docker-compose.yml`
- `bookstack/.env.example`

## Deploy in Coolify
1. Create a new service using Docker Compose from this repo.
2. Set compose path to: `bookstack/docker-compose.yml`.
3. Add environment variables from `bookstack/.env.example`.
4. Set `BOOKSTACK_HOST` and `BOOKSTACK_APP_URL` to your chosen KB domain.
5. Generate secrets:
   - `BOOKSTACK_APP_KEY`: `echo "base64:$(openssl rand -base64 32)"`
   - strong values for DB passwords.
6. Deploy service.

## First login
- BookStack default login:
  - Email: `admin@admin.com`
  - Password: `password`
- Change admin credentials immediately after first login.

## Internal-only access (recommended)
Use one of:
1. Cloudflare Access policy on KB hostname.
2. Coolify/Traefik auth middleware.
3. Private network + VPN-only ingress.

## Notes
- Keep `APP_URL` equal to the public URL used to access BookStack.
- If URL changes later, update `BOOKSTACK_APP_URL` and redeploy.
