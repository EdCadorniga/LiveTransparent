# GHL Reports Custom Menu Payload

This file captures the exact custom menu link payload we want to create for the embedded report entry point.

## Intended Menu

- Title: `Executive Report`
- URL: `https://reports.livetransparent.com/embed/executive?view=overview&range=30d&embed=1`
- Open mode: embedded iframe
- Sidebar scope: sub-account / location only
- Visibility: all roles
- Target location: `Zwz4relUXVPxx8uohnjV`

## Payload Shape

```json
{
  "Version": "2021-07-28",
  "requestBody": {
    "icon": {
      "name": "vr-cardboard",
      "fontFamily": "fas"
    },
    "locations": ["Zwz4relUXVPxx8uohnjV"],
    "openMode": "iframe",
    "showOnCompany": false,
    "showOnLocation": true,
    "showToAllLocations": false,
    "title": "Executive Report",
    "url": "https://reports.livetransparent.com/embed/executive?view=overview&range=30d&embed=1",
    "userRole": "all"
  }
}
```

## Notes

- The custom menu API is agency-scoped.
- The current location-level PIT is not sufficient to finish creation.
- Once agency-scope menu management access is available, this payload should be enough to create the sidebar entry with the embedded report target.
