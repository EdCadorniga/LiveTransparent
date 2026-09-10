# Sample Landing Page Preview Deployment

**Date:** 2026-09-10

## Scope

The isolated `Sample Landing Page/` prototype was deployed for review only. No production website, CRM, GHL workflow, campaign, sender, tracking system, or booking integration was changed.

## Deployment Target

- Coolify host: `89.117.21.29`
- Coolify project/environment: `automations` / `production`
- Coolify application: `Sample Landing Page Review`
- Application UUID: `vkrlibgdjdi4u6iz8hokue00`
- Preview hostname: `vkrlibgdjdi4u6iz8hokue00.89.117.21.29.sslip.io`
- Review URL: `http://vkrlibgdjdi4u6iz8hokue00.89.117.21.29.sslip.io/`
- Image: `localhost:5000/livetransparent-sample-landing:review`
- Container: `vkrlibgdjdi4u6iz8hokue00`
- Container network: `coolify`
- Exposed container port: `80`

## Actual Deployment Sequence

1. Built the static Nginx image locally as `livetransparent-sample-landing:review`.
2. Loaded the image onto the VPS.
3. Created a temporary Docker Registry v2 container named `sample-landing-registry`, bound to VPS loopback port `5000`.
4. Tagged and pushed the image as `localhost:5000/livetransparent-sample-landing:review`.
5. Created the separate Coolify application and generated the `sslip.io` hostname.
6. The normal Coolify deployment failed before container startup because the original unqualified image was not pullable:

   ```text
   pull access denied for livetransparent-sample-landing
   ```

7. Updated the Coolify application record to reference the registry-backed image. The Coolify UI became unresponsive while saving/deploying, so the final container was started manually on the Coolify Docker network.
8. Added the required Coolify metadata and Traefik routing labels for the generated hostname.

This is therefore a manual Docker start using Coolify infrastructure and proxy routing, not a fully successful Coolify-managed deployment. The Coolify application record remains marked `exited`/without a recognized deployed container and should be reconciled before relying on Coolify stop, redeploy, or rollback controls.

## Verification

- Container state: running.
- Preview HTTP response: `200`.
- Page title and page content: verified.
- CSS, JavaScript, logo, poster, case-study image, SVG, favicon, and video: loaded successfully.
- Console errors: none.
- Unexpected network requests: none observed; requests stayed on the preview hostname.
- Mobile viewport: verified at approximately `390px`; no horizontal overflow.
- HTTPS: not verified successfully; the generated preview returned `503`/certificate failure. The documented review URL is HTTP only.

## Cleanup / Follow-up

- Keep the temporary registry while the review preview is needed.
- Reconcile the Coolify application state and perform a genuine Coolify-managed redeploy before treating this as a repeatable deployment procedure.
- Remove the temporary registry and review container after approval or when the preview is no longer needed.
- Do not add the GHL booking widget, production tracking, or lead capture until the page copy and structure are approved.
