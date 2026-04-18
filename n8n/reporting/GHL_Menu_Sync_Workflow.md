# GHL Executive Report Menu Sync

This workflow provisions the GHL sidebar entry for the executive report.

## Live Workflow

- Name: `LT - GHL Executive Report Menu Sync`
- n8n ID: `8YtaPmPnTXUkBDAd`
- Status: inactive provisioner

## Purpose

- Create or update the GHL `Executive Report` custom menu link.
- Point the menu item at the embedded report host.
- Keep the report entry repeatable instead of handling it as a one-off manual step.

## Invocation Contract

Required input:

- `agencyToken`: valid agency-scope HighLevel token

Optional input:

- `locationId`: defaults to `Zwz4relUXVPxx8uohnjV`
- `title`: defaults to `Executive Report`
- `url`: defaults to `https://reports.livetransparent.com/embed/executive?view=overview&range=30d&embed=1`
- `openMode`: defaults to `iframe`
- `userRole`: defaults to `all`
- `iconName`: defaults to `vr-cardboard`
- `iconFontFamily`: defaults to `fas`
- `menuId`: if present, the workflow updates an existing menu instead of creating a new one

## Notes

- The workflow uses the GHL custom menu API.
- The live custom menu record already exists in GHL.
- Keep this workflow as the preferred way to update or recreate the menu entry if the URL or labels change later.
