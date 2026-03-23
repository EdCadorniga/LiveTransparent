# Footer Form Handoff (Website Admin)

Use this file as the replacement footer form:

- `Forms for GHL/footer-form-replacement.html`

What it does:
- Submits form data to  
  `https://automations.livetransparent.com/webhook/lt-form-footer-intake`
- Sends these fields:
  - `full_name`
  - `email`
  - `phone`
  - `message`

Notes:
- Keep field `name` attributes exactly as-is.
- Keep the form `action` URL exactly as-is.
- Keep logo image source as `../livetransparent_logo.png` (or replace with the production logo URL/path).
