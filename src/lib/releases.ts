// Release info, fetched from GitHub while the site builds. If GitHub won't answer, pages
// render a fallback and the visitor's browser fetches it instead (see notes.ts).

import { API, fromGitHub, latestOf, type GhRelease, type Latest, type Release } from "./notes";

export { REPO, RELEASES_PAGE, formatDate, formatSize } from "./notes";

const BASE = { Accept: "application/vnd.github+json", "User-Agent": "nyanga-web" };

let cached: Promise<GhRelease[]> | undefined;

async function fetchReleases(): Promise<GhRelease[]> {
  let token = process.env.GITHUB_TOKEN?.trim();
  try {
    let res = await fetch(API, { headers: token ? { ...BASE, Authorization: `Bearer ${token}` } : BASE });
    if ((res.status === 401 || res.status === 403) && token) {
      console.warn(`[releases] GitHub refused GITHUB_TOKEN (${res.status}); trying without it`);
      res = await fetch(API, { headers: BASE });
      token = undefined;
    }
    if (!res.ok) {
      console.warn(`[releases] GitHub said ${res.status}: ${(await res.text()).slice(0, 200)}`);
      return [];
    }
    const found = (await res.json()) as GhRelease[];
    console.log(`[releases] ${found.length} releases from GitHub${token ? " (with token)" : ""}`);
    return found;
  } catch (e) {
    console.warn(`[releases] couldn't reach GitHub: ${e}`);
    return [];
  }
}

/** Every release, newest first; empty when GitHub can't be reached (the site still builds). */
function releases(): Promise<GhRelease[]> {
  cached ??= fetchReleases();
  return cached;
}

export async function latest(): Promise<Latest | null> {
  return latestOf(await releases());
}

/** Every release's changes in plain words, newest first, like the app's What's new window. */
export async function history(): Promise<Release[]> {
  const all = await releases();
  // Newer releases carry whats_new.json (with an explanation per change) covering every version.
  const notes = all.flatMap((r) => r.assets).find((a) => a.name === "whats_new.json");
  if (notes) {
    try {
      const res = await fetch(notes.browser_download_url, { headers: { "User-Agent": "nyanga-web" } });
      if (res.ok) return ((await res.json()) as Release[]).filter((r) => r.items.length);
    } catch {
      // fall back to the release bodies below
    }
  }
  return fromGitHub(all);
}
