FROM node:22-bookworm-slim AS pg-dependencies

WORKDIR /tmp/pg

# Install a self-contained npm tree. Copying n8n's pnpm store leaves broken
# symlinks and does not satisfy the task runner's dependency resolver.
RUN npm install --omit=dev --no-package-lock --no-save pg@8.21.0

FROM n8nio/runners:latest

USER root

# Keep the npm tree isolated from the runner's pnpm tree. NODE_PATH below makes
# it available to Code node `require()` calls from any working directory.
COPY --from=pg-dependencies /tmp/pg/node_modules /opt/pg-node_modules

USER runner
