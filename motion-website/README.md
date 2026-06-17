# KINETIK — Motion Studio Landing Page

A single-file, dependency-free motion-design studio landing page built with the
`ui-ux-pro-max` skill. Style direction: **Kinetic Brutalism** (dark canvas, acid
accent, oversized Archivo display type, Space Grotesk body).

## Run it

No build step. Just open the file:

```bash
# from this folder
python3 -m http.server 8000
# then visit http://localhost:8000
```

…or open `index.html` directly in a browser.

## Motion features

- Custom blend-mode cursor with hover scaling (pointer devices only)
- Scroll progress bar + sticky/blur navbar
- Hero line-reveal intro + scroll parallax & fade
- Infinite acid marquee (pauses on hover)
- IntersectionObserver scroll-reveal on every section
- Project cards: flood-inversion fill + subtle 3D tilt on hover
- Count-up stats when scrolled into view
- Magnetic primary CTA

## Accessibility

- Fully respects `prefers-reduced-motion` (all transforms/animations disabled,
  content shown immediately, custom cursor hidden)
- High-contrast palette (acid `#E4FF1A` / cyan on `#0A0A0A`)
- Semantic landmarks, keyboard-focusable links, responsive down to 375px

Replace the placeholder copy, links, and `hello@kinetik.studio` contact details
with real content before shipping.
