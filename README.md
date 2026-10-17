# nyanga-web

The Nyanga website: a landing page with the download button, install help, and a What's new
page. Built with [Astro](https://astro.build) as a plain static site, hosted on Cloudflare Pages.

## Running it

```sh
npm install
npm run dev      # http://localhost:4321, reloads as you edit
npm run build    # the finished site in dist/
```

## Where things come from

- **The download button and What's new** are filled in when the site builds, from the app's
  GitHub releases (`src/lib/releases.ts`). The newest release's installer becomes the button;
  `whats_new.json` (attached to each release by the app's release workflow) becomes the What's
  new page, with the release notes as a fallback. If GitHub can't be reached the site still
  builds, with the button pointing at the releases page.
- **Colors** match the app's light and dark palettes in `theme.py`, and the page follows the
  visitor's system theme.
- **The cats** (`public/img/cat-*.webp`) are rendered from the app's own drawing code:
  `QT_QPA_PLATFORM=offscreen ../.venv/bin/python scripts/render_cats.py`, run from this folder
  inside the app checkout.
- **The screenshots** (`public/img/screenshot-*.png`) are the real app showing a made-up manga
  with our cat as its cover, so the site shows no one else's art.
- **The font** is Fredoka (`public/fonts/`, SIL Open Font License).

## Deploying

Cloudflare (Workers with static assets) builds this repo on every push: build command
`npm run build`, deploy command `npx wrangler deploy`, which serves `dist/` as set in
`wrangler.jsonc`. Setting a `GITHUB_TOKEN` environment variable there avoids GitHub's rate limit for
anonymous requests.
