// Release info, fetched from GitHub when the site builds (the app's release workflow
// triggers a rebuild, so the download button always points at the newest installer).

export const REPO = "nyanga-app/nyanga-app";
export const RELEASES_PAGE = `https://github.com/${REPO}/releases/latest`;

export interface Item {
  kind: "breaking" | "feat" | "fix" | "perf";
  area: string;
  title: string;
  detail: string;
}

export interface Release {
  version: string;
  date: string;
  items: Item[];
}

export interface Latest {
  version: string;
  date: string;
  url: string; // the installer
  size: number;
}

interface GhAsset {
  name: string;
  size: number;
  browser_download_url: string;
}

interface GhRelease {
  tag_name: string;
  published_at: string;
  body: string | null;
  assets: GhAsset[];
}

const API = `https://api.github.com/repos/${REPO}/releases?per_page=100`;
const BASE = { Accept: "application/vnd.github+json", "User-Agent": "nyanga-web" };

let cached: Promise<GhRelease[]> | undefined;

async function fetchReleases(): Promise<GhRelease[]> {
  let token = process.env.GITHUB_TOKEN?.trim();
  try {
    let res = await fetch(API, { headers: token ? { ...BASE, Authorization: `Bearer ${token}` } : BASE });
    if (res.status === 401 && token) {
      console.warn("[releases] GitHub rejected GITHUB_TOKEN (401); trying without it");
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

const isInstaller = (a: GhAsset) => a.name.toLowerCase().endsWith(".exe") && a.name.toLowerCase().includes("setup");

export async function latest(): Promise<Latest | null> {
  for (const r of await releases()) {
    const exe = r.assets.find(isInstaller);
    if (exe) {
      return { version: r.tag_name.replace(/^v/, ""), date: r.published_at.slice(0, 10), url: exe.browser_download_url, size: exe.size };
    }
  }
  return null;
}

const SECTIONS: Record<string, Item["kind"]> = { "Breaking changes": "breaking", New: "feat", Fixes: "fix", Faster: "perf" };

/** A release's notes from its markdown body, for releases made before whats_new.json was attached. */
function parseBody(body: string): Item[] {
  const items: Item[] = [];
  let kind: Item["kind"] | undefined;
  for (const line of body.split(/\r?\n/)) { // the release workflow runs on Windows: \r\n
    const heading = line.match(/^###\s+(.+?)\s*$/);
    if (heading) kind = SECTIONS[heading[1]];
    const bullet = line.match(/^- (?:([a-z]+): )?(.+)$/);
    if (bullet && kind) {
      const [, scope = "", text] = bullet;
      items.push({ kind, area: scope && scope[0].toUpperCase() + scope.slice(1), title: text[0].toUpperCase() + text.slice(1), detail: "" });
    }
  }
  return items;
}

/** Every release's changes in plain words, newest first, like the app's What's new window. */
export async function history(): Promise<Release[]> {
  const all = await releases();
  // Newer releases carry whats_new.json (with an explanation per change) covering every version.
  const notes = all.flatMap((r) => r.assets).find((a) => a.name === "whats_new.json");
  if (notes) {
    try {
      const res = await fetch(notes.browser_download_url);
      if (res.ok) return ((await res.json()) as Release[]).filter((r) => r.items.length);
    } catch {
      // fall back to the release bodies below
    }
  }
  return all
    .map((r) => ({ version: r.tag_name.replace(/^v/, ""), date: r.published_at.slice(0, 10), items: parseBody(r.body ?? "") }))
    .filter((r) => r.items.length);
}

export function formatSize(bytes: number): string {
  return `${(bytes / 1024 / 1024).toFixed(0)} MB`;
}

export function formatDate(iso: string): string {
  return new Date(`${iso}T12:00:00Z`).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric", timeZone: "UTC" });
}
