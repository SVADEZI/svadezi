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

---

# Ring Story — iOS-safe scroll-scrub animation

`sections/ring-story.liquid` recreates Apple-style scroll animations (AirPods /
MacBook pages) by scrubbing an **image sequence** on `<canvas>` — **not** a
`<video>`. Video `currentTime` scrubbing is fundamentally unreliable on iOS Safari
(async seeking, dropped seeks, decode suspension, Low-Power-Mode autoplay blocks),
which is why the canvas goes blank on iPhone. Image sequences sidestep all of it
and render identically on iOS, Android, and desktop.

## 1. Export frames from your video
```bash
# ~120 frames, 1280px wide, good-quality JPGs. Tune fps to land on your frame count.
ffmpeg -i ring.mp4 -vf "scale=1280:-1,fps=24" -q:v 4 ring_%04d.jpg
```
- Aim for **60–150 frames**. More = smoother but heavier (~120 JPGs @1280px ≈ 3–6 MB total).
- `%04d` = 4-digit zero padding → `ring_0001.jpg`. Keep this consistent with the
  `frame_pad` setting.

## 2. Host the frames
Upload all JPGs to **Shopify Admin → Settings → Files** (served from Shopify's CDN).
They'll share a base URL like:
```
https://cdn.shopify.com/s/files/1/XXXX/YYYY/files/ring_0001.jpg
```
Copy everything **before the number** → that's your `frame_base_url`
(`https://cdn.shopify.com/s/files/1/XXXX/YYYY/files/ring_`).

> Don't bulk-upload frames into theme `assets/` — you'll hit theme file limits and
> clutter the theme. Files + CDN is the right home for a frame sequence.

## 3. Install the section
1. **Edit code → Sections → Add a new section** → name it `ring-story` → paste
   `sections/ring-story.liquid`, Save.
2. **Customize** → add the **Ring Story** section to a page.
3. Fill in the settings:
   - **Frame base URL** — from step 2
   - **File extension** — `.jpg`
   - **Number of frames** — e.g. `120`
   - **Zero-padding digits** — `4` (matches `%04d`)
   - **First frame number** — `1`
   - **Poster / fallback image** — upload one frame (e.g. frame 1) so the canvas
     shows instantly while the sequence loads
   - **Scroll length (vh)** — `300` (higher = slower, more cinematic scrub)

## How it stays bulletproof
- **Poster frame** paints immediately → canvas is never blank.
- **Chunked lazy-loading** → frames load in batches during idle time; the nearest
  already-loaded frame is shown until the exact one arrives (no flicker/blank).
- **No video** → no autoplay gesture, no decode suspension, no async `seeked` race.
- DPR-aware "cover" rendering, throttled to one paint per animation frame.
