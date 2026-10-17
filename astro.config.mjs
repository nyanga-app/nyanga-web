import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

// `site` is the site's public address: canonical links, the sitemap, robots.txt and link
// previews all come from it. Change it here when the site moves to its own domain.
export default defineConfig({
  site: "https://nyanga-web.nyanga.workers.dev",
  integrations: [sitemap({ filter: (page) => !page.includes("/404") })],
});
