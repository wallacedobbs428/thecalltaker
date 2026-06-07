# Brand Icon / Favicon QA - 2026-06-07

## Objective

Remove generic phone-icon branding from favicon/social identity and replace it with a clean temporary TCT mark.

## Files Updated

- `website/favicon.svg`
- `website/favicon.ico`
- `website/favicon-16x16.png`
- `website/favicon-32x32.png`
- `website/favicon-48x48.png`
- `website/favicon-64x64.png`
- `website/favicon-96x96.png`
- `website/favicon-128x128.png`
- `website/favicon-180x180.png`
- `website/favicon-192x192.png`
- `website/favicon-512x512.png`
- `website/apple-touch-icon.png`
- `website/site.webmanifest`

## QA Result

PASS_WITH_NOTES

## Findings

- The old favicon SVG used a generic phone handset mark.
- The new favicon system uses a dark/green TCT monogram.
- Apple touch icon and favicon PNG sizes were regenerated.
- Browser manifest now references the 192 and 512 icon sizes.
- Header/footer `logo-icon` SVGs still contain phone SVG source on some pages, but they are hidden by shared CSS on the current buyer-path layout. Visible brand icon issue is fixed at favicon/social level.

## Recommendation

Future brand cleanup should replace hidden inline logo SVG source with the TCT mark across all templates, but it is not blocking Stage 1 buyer-path proof because it is not visible.
