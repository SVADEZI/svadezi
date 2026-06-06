# SVADEZI — Shopify Product Page

A high-converting product page modeled on CaratLane's PDP structure, tuned for
SVADEZI's **925 sterling silver + natural crystal** story.

## What's included

| File | Use it for |
|------|-----------|
| `product-page/index.html` | **Preview / prototype.** Open in any browser to see the full design. Self-contained (no build step). Great for sharing mockups or pasting into a Shopify *Page* (use inline-style version if the editor strips CSS). |
| `sections/svadezi-product.liquid` | **The real thing.** A Shopify Online Store 2.0 section that pulls live product data (images, price, variants, description) and is editable in the theme editor. |

## Features built in
- Image gallery with thumbnails (on-white / zoom / on-model / video / scale slots)
- Transparent **price breakup** (CaratLane-style) — *HTML preview only*
- Variant selector + quantity
- Add to Bag / Buy Now + Wishlist
- Delivery promise + **pincode check** + **COD** line
- Trust badge row: BIS Hallmarked · Anti-Tarnish · Nickel-Free · Certificate
- Tabs: Description · Specifications · **Crystal & Care** · Shipping & Returns · Reviews
- Photo reviews + "Complete the look" cross-sell
- **Sticky add-to-cart bar** on mobile

## How to install the Liquid section in a real store
1. Shopify Admin → **Online Store → Themes → ⋯ → Edit code**
2. **Sections → Add a new section**, name it `svadezi-product`
3. Paste the contents of `sections/svadezi-product.liquid`, **Save**
4. Back in the theme: **Customize → (a product template) → Add section → "SVADEZI Product"**
5. Edit brand color, badges, crystal text, and shipping copy right in the editor.

## Notes
- The HTML preview uses **gradient placeholders** where product photos go — replace with real images (ideally including one **on-model** shot and one **scale reference**).
- The price-breakup table in the preview is illustrative; Shopify doesn't expose a
  metal/stone breakdown natively, so it's hardcoded in the HTML and omitted from the
  Liquid section. Add a metafield if you want it live.
