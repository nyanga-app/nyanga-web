<p align="center">
  <img src="public/img/icon.svg" width="96" alt="The Nyanga cat">
</p>

<h1 align="center">nyanga-web</h1>

<p align="center">
  <b>the cozy little home page for Nyanga ✧</b><br>
  <i>where friends come to meet the cat and grab the app</i><br>
  <a href="https://nyanga-web.nyanga.workers.dev">nyanga-web.nyanga.workers.dev</a>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="public/img/cat-reading-dark.webp">
    <img src="public/img/cat-reading-light.webp" width="180" alt="The Nyanga cat reading a book">
  </picture>
</p>

---

## ♡ What's on it

- 🏠 **The home page**: a big pink **Download for Windows ♡** button that always points at the
  newest installer, a peek at the app, what it does, the cats, and gentle install steps that
  walk you past the "Windows protected your PC" box.
- ✨ **What's new**: every update in plain words, newest first, just like the app's own window.
- 🐾 **A 404 page**, so even lost visitors get a cat.
- 🌙 **Light and dark**, following your system, in the same colors as the app.

## 🧶 Playing with it

```sh
npm install
npm run dev      # http://localhost:4321, refreshes as you edit
npm run build    # the finished site lands in dist/
```

It's an [Astro](https://astro.build) site that comes out as plain HTML and CSS, so it's tiny and
quick. The pages live in `src/pages/`, the shared header and footer in `src/layouts/Base.astro`.

## 🎀 Where everything comes from

- **The download button and What's new** are filled in while the site builds, from the app's
  GitHub releases (`src/lib/releases.ts`). Each release carries `whats_new.json`, the same
  notes the app shows; older releases fall back to their release notes. If GitHub won't
  answer, the site still builds with fallbacks. Lines
  starting with `[releases]` in the build log say what happened, and visitors' browsers then
  fetch the newest version and the notes themselves (`src/lib/notes.ts`).
- **The colors** are the app's light and dark palettes from `theme.py`.
- **The cats** (`public/img/cat-*.webp`) are drawn by the app's own code, so they match it
  perfectly. To redraw them, from this folder inside the app checkout:

  ```sh
  QT_QPA_PLATFORM=offscreen ../.venv/bin/python scripts/render_cats.py
  ```

- **The app pictures** (`public/img/screenshot-*.webp`, `shot-*.webp`) are the real app,
  rendered offscreen with made-up manga (*Cozy Cat Diaries*, *Moonlit Bakery*…) whose covers are
  drawn by the script itself. No one else's art on the site ✿ Redraw them whenever the app's
  look changes:

  ```sh
  QT_QPA_PLATFORM=offscreen ../.venv/bin/python scripts/render_shots.py
  ```

- **The icons** are the app's own (`src/lib/icons.ts`, used through `src/components/Icon.astro`),
  copied from `theme.py` by `../.venv/bin/python scripts/export_icons.py`. The site has no emoji
  on purpose: the app's icons, the cats and a few ✧ ♡ are its whole look.
- **The link-preview card** (`public/img/card.png`) and the phone icon
  (`public/apple-touch-icon.png`) come from `scripts/render_card.py`. Run it after
  `render_shots.py`, since the card shows a slice of the app.
- **The font** is Fredoka as WOFF2 (`public/fonts/`, SIL Open Font License).

## 🔎 Being found

Every page has a title and description, a canonical link and link-preview tags (`Base.astro`);
the home page also tells search engines it's a free Windows app (JSON-LD). The sitemap and
`robots.txt` are made by the build. All of it follows `site` in `astro.config.mjs`.

While the site still lives on `workers.dev`, every page says `noindex`, so search engines
leave it alone until it has a proper home. Pointing `site` at the real domain lifts it.

When the site moves to its own domain: add it under the Cloudflare project's Domains &
Routes, change `site` in `astro.config.mjs` (and the link at the top of this file), push, and
add the new address in Google Search Console with its sitemap.

## 🚀 Going live

Every push to `main` is built and published by Cloudflare (Workers with static assets):

| Step | What runs |
|------|-----------|
| Build | `npm run build` |
| Deploy | `npx wrangler deploy`, which serves `dist/` as set in `wrangler.jsonc` |

A `GITHUB_TOKEN` build variable in Cloudflare (a read-only token for public repos) keeps GitHub
from rate-limiting the builds. It's optional; without it the site still works.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="public/img/cat-happy-dark.webp">
    <img src="public/img/cat-happy-light.webp" width="150" alt="A happy cat hopping with hearts">
  </picture><br>
  <sub>made with ♡ and a lot of cat naps</sub>
</p>
