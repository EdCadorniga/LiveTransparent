# Website Admin Handoff

This handoff covers the remaining website-side updates for the hero form and the legal pages.

## Files To Use

- `Forms for GHL/hero-inline-embed.html`
- `Forms for GHL/hero-popup-embed.html`
- `Forms for GHL/hero-ghl-form-custom.css`
- `Forms for GHL/HERO_POPUP_RESPONSIVE_OVERRIDES.css`
- `Forms for GHL/Transparent_eCom_Legal_Policies.docx`

## What Has Already Updated In GHL

The live GHL form itself is already updated and rendering the latest styling inside the iframe:

- corrected headings and field styling
- consistent placeholder styling
- corrected button text visibility and alignment
- desktop max width is now `600px`
- tablet max width is now `480px`
- privacy / terms links inside the form should use:
  - `https://livetransparent.com/terms`
  - `https://livetransparent.com/privacy-policy/`

The website admin should still keep the packaged CSS files with the handoff so the current styling and popup behavior are documented exactly.

## What The Website Admin Still Needs To Do

1. Replace the homepage inline hero embed with:
   - `Forms for GHL/hero-inline-embed.html`
   - current approved homepage iframe uses inline width control:
     - `style="width:100%;max-width:600px;height:100%;border:none;border-radius:3px;margin:0 auto"`
   - current approved homepage embed settings:
     - `data-layout="{'id':'INLINE'}"`
     - `data-trigger-type="alwaysShow"`
     - `data-activation-type="alwaysActivated"`
     - `data-deactivation-type="neverDeactivate"`
     - `data-height="802"`
2. Replace the popup embed with:
   - `Forms for GHL/hero-popup-embed.html`
   - current approved popup iframe uses inline width control:
     - `style="display:none;width:100%;max-width:600px;height:100%;border:none;border-radius:3px;margin:0 auto"`
   - current approved popup trigger settings:
     - `data-trigger-type="showAfter"`
     - `data-trigger-value="8"`
     - `data-activation-type="activateOnVisit"`
     - `data-activation-value="3"`
     - `data-deactivation-type="leadCollected"`
   - if the popup shows visible scrollbars after embed replacement, also load:
     - `Forms for GHL/HERO_POPUP_RESPONSIVE_OVERRIDES.css`
   - popup wrapper / iframe should render with `overflow: hidden` so no visible popup scrollbars appear
3. Keep the Hero form custom CSS on file using:
   - `Forms for GHL/hero-ghl-form-custom.css`
4. Use the legal policy document as the canonical legal handoff artifact:
   - `Forms for GHL/Transparent_eCom_Legal_Policies.docx`
5. In GHL, set the Hero form consent checkbox to required if submit-time enforcement is desired.

## Live State Verified On 2026-03-24

Verified in Playwright on the live site:

- Homepage:
  - inline iframe exists as `inline-kxrHpS9bX16nzkIbr2py`
  - popup iframe exists as `popup-kxrHpS9bX16nzkIbr2py`
- Inline hero form:
  - currently rendered at about `367x888` on desktop
  - current live `data-height` observed: `981`
- Popup form:
  - currently rendered at about `405x888` on desktop
  - current live `data-height` observed: `925`
  - older popup trigger/settings still appeared live during verification
- Privacy page:
  - legal page content is now handed off through the canonical legal doc
- Terms page:
  - legal page content is now handed off through the canonical legal doc

## Intent Of The Updated Embed Snippets

- The inline embed is constrained to a tighter, cleaner hero width and height.
- The homepage inline embed now uses the approved inline iframe style directly in the embed snippet with `max-width:600px`.
- The popup embed uses:
  - `showAfter`
  - `8`
  - `activateOnVisit`
  - `3`
  - `leadCollected`
- The popup embed now uses the approved inline iframe style directly in the embed snippet.
- The popup no-scrollbar safeguard is documented in `HERO_POPUP_RESPONSIVE_OVERRIDES.css`.
- The final GHL form styling is documented in `hero-ghl-form-custom.css`.

## Publish Checklist

- Replace homepage inline embed
- Replace popup embed
- Keep `hero-ghl-form-custom.css` with the handoff package for the final form styling record
- If popup scrollbars appear, apply `HERO_POPUP_RESPONSIVE_OVERRIDES.css`
- Test homepage on desktop, tablet, and mobile
- Test popup open / close / submit behavior
- Confirm popup opens without visible scrollbars
- Optional: have final legal language reviewed internally before publishing
