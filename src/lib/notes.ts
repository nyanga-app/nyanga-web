// Release notes in plain words, shared by the build (releases.ts) and the browser fallback,
// which fetches from GitHub itself when the build couldn't.

export const REPO = "nyanga-app/nyanga-app";
export const API = `https://api.github.com/repos/${REPO}/releases?per_page=100`;
export const RELEASES_PAGE = `https://github.com/${REPO}/releases/latest`;

export interface Item {
  kind: "breaking" | "feat" | "fix" | "perf";
  area: string;
  title: string;
  detail: string;
}

export interface Release {
  version: string;
  date: string; // the UTC day
  time?: string; // the exact UTC moment (newer notes), so browsers can show their own day
  items: Item[];
}

export interface Latest {
  version: string;
  date: string;
  url: string; // the installer
  size: number;
  linux?: { url: string; size: number }; // the AppImage, from the same release
  deb?: { url: string; size: number; name: string }; // packages for Ubuntu/Debian and Fedora/openSUSE,
  rpm?: { url: string; size: number; name: string }; // from releases since they were added
}

export interface GhAsset {
  name: string;
  size: number;
  browser_download_url: string;
}

export interface GhRelease {
  tag_name: string;
  published_at: string;
  body: string | null;
  assets: GhAsset[];
}

export const SECTIONS: [Item["kind"], string][] = [
  ["breaking", "Heads up: this works a bit differently"],
  ["feat", "✦ New things"],
  ["fix", "✓ Fixed"],
  ["perf", "✿ Faster"],
];

const HEADINGS: Record<string, Item["kind"]> = { "Breaking changes": "breaking", New: "feat", Fixes: "fix", Faster: "perf" };

const capital = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

/** A release's notes from its markdown body (made by the app's scripts/next_version.py). */
export function parseBody(body: string): Item[] {
  const items: Item[] = [];
  let kind: Item["kind"] | undefined;
  for (const line of body.split(/\r?\n/)) { // the release workflow runs on Windows: \r\n
    const heading = line.match(/^###\s+(.+?)\s*$/);
    if (heading) kind = HEADINGS[heading[1]];
    const bullet = line.match(/^- (?:([a-z]+): )?(.+)$/);
    if (bullet && kind) items.push({ kind, area: capital(bullet[1] ?? ""), title: capital(bullet[2]), detail: "" });
  }
  return items;
}

/** Every release with changes worth showing, newest first, from GitHub's release list. */
export function fromGitHub(all: GhRelease[]): Release[] {
  return all
    .map((r) => ({
      version: r.tag_name.replace(/^v/, ""),
      date: r.published_at.slice(0, 10),
      time: r.published_at,
      items: parseBody(r.body ?? ""),
    }))
    .filter((r) => r.items.length);
}

export function latestOf(all: GhRelease[]): Latest | null {
  for (const r of all) {
    const exe = r.assets.find((a) => a.name.toLowerCase().endsWith(".exe") && a.name.toLowerCase().includes("setup"));
    if (!exe) continue;
    const image = r.assets.find((a) => a.name.toLowerCase().endsWith(".appimage"));
    const pkg = (ext: string) => {
      const a = r.assets.find((a) => a.name.toLowerCase().endsWith(ext));
      return a && { url: a.browser_download_url, size: a.size, name: a.name };
    };
    return {
      version: r.tag_name.replace(/^v/, ""),
      date: r.published_at.slice(0, 10),
      url: exe.browser_download_url,
      size: exe.size,
      linux: image && { url: image.browser_download_url, size: image.size },
      deb: pkg(".deb"),
      rpm: pkg(".rpm"),
    };
  }
  return null;
}

export const formatSize = (bytes: number) => `${(bytes / 1024 / 1024).toFixed(0)} MB`;

export function formatDate(iso: string): string {
  return new Date(`${iso}T12:00:00Z`).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric", timeZone: "UTC" });
}

/** Swaps each release's UTC day (from the build) for the visitor's own day. */
export function localDates(root: ParentNode): void {
  for (const el of root.querySelectorAll<HTMLTimeElement>("time[data-local]")) {
    const when = new Date(el.dateTime);
    if (!isNaN(when.getTime())) {
      el.textContent = when.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
    }
  }
}
