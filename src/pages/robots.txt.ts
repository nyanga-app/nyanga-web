import type { APIRoute } from "astro";

// Everyone may look around; the sitemap lists every page. Follows `site` in astro.config.mjs.
export const GET: APIRoute = ({ site }) =>
  new Response(`User-agent: *\nAllow: /\n\nSitemap: ${new URL("sitemap-index.xml", site)}\n`, {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
