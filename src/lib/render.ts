// The What's new list as HTML, used by the page at build time and by the browser fallback.

import { SECTIONS, formatDate, type Release } from "./notes";

const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);

export function releasesHtml(releases: Release[]): string {
  return releases
    .map((r, i) => {
      const sections = SECTIONS.map(([kind, heading]) => {
        const items = r.items.filter((it) => it.kind === kind);
        if (!items.length) return "";
        const lis = items
          .map((it) => `<li class="note">
  <div class="note-title"><span>${esc(it.title)}</span>${it.area ? `<span class="chip">${esc(it.area)}</span>` : ""}</div>
  ${it.detail ? `<p>${esc(it.detail)}</p>` : ""}
</li>`)
          .join("");
        return `<section><h3>${esc(heading)}</h3><ul>${lis}</ul></section>`;
      }).join("");
      return `<article class="release">
  <header>
    <h2>Version ${esc(r.version)}</h2>${i === 0 ? '<span class="chip latest">latest</span>' : ""}
    <time datetime="${esc(r.time ?? r.date)}"${r.time ? " data-local" : ""}>${formatDate(r.date)}</time>
  </header>${sections}
</article>`;
    })
    .join("");
}
