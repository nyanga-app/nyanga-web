"""Renders the app pictures for the site into public/img/, in light and dark, from the real app.

Everything shown is made up: invented manga titles with covers drawn here (shapes, the title
and our cat), so the site shows no one else's art. Nothing touches the network or your own
settings and library. Run from this folder inside the app checkout:

    QT_QPA_PLATFORM=offscreen ../.venv/bin/python scripts/render_shots.py

Writes screenshot-<mode>.webp (the whole Download page) and shot-<name>-<mode>.webp crops:
search, files, library, phone and whatsnew.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

os.environ["QT_SCALE_FACTOR"] = "2"  # sharp on high-DPI screens
HERE = Path(__file__).resolve().parent.parent
APP = HERE.parent
OUT = HERE / "public" / "img"
sys.path.insert(0, str(APP))
DATA = Path(tempfile.mkdtemp())

import paths  # noqa: E402

paths.DATA = paths.CONFIG = DATA

from PIL import Image  # noqa: E402
from PySide6.QtCore import QBuffer, QEvent, QPoint, QPointF, QRect, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QFont, QImage, QLinearGradient, QPainter, QPainterPath, QPen  # noqa: E402
from PySide6.QtWidgets import QApplication, QPushButton, QWidget  # noqa: E402

import core  # noqa: E402
import gui  # noqa: E402
import theme  # noqa: E402

VERSION = "1.4.0"
gui.__version__ = VERSION
core.estimate_chapter_bytes = lambda site, chapters: 9_400_000
gui.LibraryPage._check_for_new = lambda self, entries: None  # no network

# ---------------------------------------------------------------- made-up covers


def _cover(title: str, top: str, bottom: str, motif: str) -> bytes:
    """A 300x430 cover: a gradient, a simple motif and the title."""
    img = QImage(300, 430, QImage.Format_ARGB32)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    g = QLinearGradient(0, 0, 300, 430)
    g.setColorAt(0, QColor(top))
    g.setColorAt(1, QColor(bottom))
    p.fillRect(img.rect(), g)
    white = QColor(255, 255, 255, 235)
    p.setPen(Qt.NoPen)
    p.setBrush(white)
    if motif == "cat":
        p.drawPixmap(60, 110, theme._render(theme._APP_ICON, 180))
    elif motif == "moon":
        moon = QPainterPath()
        moon.addEllipse(QPointF(150, 190), 78, 78)
        bite = QPainterPath()
        bite.addEllipse(QPointF(188, 160), 70, 70)
        p.drawPath(moon.subtracted(bite))
        for x, y, r in ((70, 90, 6), (236, 250, 5), (210, 80, 4), (90, 280, 4)):
            p.drawEllipse(QPointF(x, y), r, r)
    elif motif == "sun":
        p.drawEllipse(QPointF(150, 190), 62, 62)
        p.setPen(QColor(255, 255, 255, 200))
        for i in range(12):
            p.save()
            p.translate(150, 190)
            p.rotate(i * 30)
            p.drawRoundedRect(QRectF(-5, -112, 10, 30), 5, 5)
            p.restore()
    elif motif == "cup":
        p.drawRoundedRect(QRectF(85, 170, 110, 90), 18, 18)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(255, 255, 255, 235), 12, Qt.SolidLine, Qt.RoundCap))
        p.drawEllipse(QPointF(205, 210), 22, 22)
        for x in (115, 150, 180):
            p.drawArc(QRectF(x - 10, 105, 20, 50), 90 * 16, 180 * 16)
    elif motif == "lantern":
        for x, y in ((90, 150), (210, 130), (150, 230)):
            p.drawRoundedRect(QRectF(x - 34, y - 44, 68, 88), 30, 30)
            p.drawRect(QRectF(x - 18, y - 54, 36, 10))
    elif motif == "waves":
        for i, y in enumerate((150, 200, 250)):
            path = QPainterPath(QPointF(20, y))
            for k in range(4):
                path.quadTo(QPointF(55 + k * 70, y - 26), QPointF(90 + k * 70, y))
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255, 255, 255, 235 - i * 50), 12, Qt.SolidLine, Qt.RoundCap))
            p.drawPath(path)
    p.setPen(QColor("#ffffff"))
    font = QFont(QApplication.font())
    font.setPixelSize(32)
    font.setBold(True)
    p.setFont(font)
    p.drawText(QRectF(14, 320, 272, 96), Qt.AlignCenter | Qt.TextWordWrap, title)
    p.end()
    buf = QBuffer()
    buf.open(QBuffer.WriteOnly)
    img.save(buf, "PNG")
    return bytes(buf.data())


MANGA = [  # title, status, latest, author, cover colors, motif
    ("Cozy Cat Diaries", "Ongoing", "Ch. 48", "Mochi Hana", ("#ffd6e7", "#ff8fbf"), "cat"),
    ("Moonlit Bakery", "Ongoing", "Ch. 31", "Rin Takase", ("#9fa8ff", "#5b5fc7"), "moon"),
    ("Starfruit Summer", "Completed", "Ch. 62", "Aoi Mizuno", ("#ffd27a", "#ff8a5c"), "sun"),
    ("Tea for Two Ghosts", "Ongoing", "Ch. 19", "Kei Arata", ("#b6e3c6", "#4f9e7a"), "cup"),
    ("Paper Lantern Street", "Completed", "Ch. 40", "Yuzu Kino", ("#ffb199", "#d9486f"), "lantern"),
    ("Seaglass Letters", "Ongoing", "Ch. 25", "Nao Shirase", ("#9ee6f0", "#3f8fbf"), "waves"),
]


class Site:
    """A stand-in for a real site: just enough for the pages."""
    name = "fanfox.net"

    def __init__(self, key: str = "example:cozy-cat-diaries"):
        self.key = key
        self.title_url = "https://example.com/cozy-cat-diaries"


# ---------------------------------------------------------------- helpers


def settle() -> None:
    """Lets Qt finish removing old widgets and laying out new ones."""
    QApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    QApplication.processEvents()


def crop(window: QWidget, widgets: list[QWidget], name: str, mode: str, pad: int = 18) -> None:
    """Saves the part of the window around `widgets` (with a little page around it)."""
    rect = QRect()
    for w in widgets:
        rect = rect.united(QRect(w.mapTo(window, QPoint(0, 0)), w.size()))
    rect = rect.adjusted(-pad, -pad, pad, pad).intersected(window.rect())
    save(window.grab(rect), f"shot-{name}-{mode}")


def save(pixmap, stem: str) -> None:
    img = pixmap.toImage().convertToFormat(QImage.Format_RGBA8888)
    pil = Image.frombytes("RGBA", (img.width(), img.height()), bytes(img.constBits())).convert("RGB")
    path = OUT / f"{stem}.webp"
    pil.save(path, quality=90, method=6)
    print(f"{path.name}  {pil.width}x{pil.height}  {path.stat().st_size // 1024} KB")


def window(mode: str, size: tuple[int, int]) -> gui.MainWindow:
    (DATA / "settings.json").write_text(json.dumps({
        "download_dir": r"C:\Users\you\Downloads\Manga", "theme": mode, "seen_version": VERSION,
        "default_format": "epub"}))
    w = gui.MainWindow()
    w.findChild(QPushButton, "version").hide()  # it would go out of date
    w.resize(*size)
    w.show()
    QApplication.processEvents()
    return w


def manga_info(i: int = 0) -> core.MangaInfo:
    title, status, *_ , colors, motif = MANGA[i]
    chapters = [core.Chapter(float(n), (n - 1) // 6 + 1 if n <= 42 else core.NO_VOLUME, f"https://example.com/{n}")
                for n in range(1, 49)]
    return core.MangaInfo(title, chapters, COVERS[i], status, ["Slice of life", "Comedy", "Cats", "Wholesome"])


# ---------------------------------------------------------------- the pictures


def download_page(mode: str) -> None:
    w = window(mode, (1120, 840))
    w.download._on_fetched(Site(), manga_info())
    QApplication.processEvents()
    save(w.grab(), f"screenshot-{mode}")
    w.close()


def search(mode: str) -> None:
    w = window(mode, (1120, 840))
    page = w.download
    results = [core.SearchResult(t, f"https://example.com/{i}", f"cover:{i}", s, latest, a)
               for i, (t, s, latest, a, _, _) in enumerate(MANGA)]
    for i in range(len(MANGA)):
        page.cover_cache[f"cover:{i}"] = COVERS[i]
    page.search_site = core.SITES[0]
    page.query.setText("cozy")
    page._on_searched(page.search_id, core.SITES[0], "cozy", 1, results, 1)
    settle()
    crop(w, [page.results_card], "search", mode)
    w.close()


def files(mode: str) -> None:
    w = window(mode, (1120, 980))
    page = w.download
    page._on_fetched(Site(), manga_info())
    page._add_to_library()
    rows = list(range(len(page.groups)))
    page.fractions = {r: 0.0 for r in rows}
    page.states = {r: core.QUEUED for r in rows}
    folder = DATA / "Manga" / "Cozy Cat Diaries"
    folder.mkdir(parents=True, exist_ok=True)
    for r in rows:
        bar = page._bar(r)
        bar.setFormat(core.QUEUED)
    for r in (0, 1):
        path = folder / f"Cozy Cat Diaries - Vol. 0{r + 1}.epub"
        path.touch()
        page._on_status(r, core.DONE, 1.0, str(path))
    page._on_status(2, core.BUILDING, 0.92, "Making the EPUB")
    page._on_status(3, core.DOWNLOADING, 0.58, "page 61 of 104")
    page.bar_cat.start()
    settle()
    page._status("Downloading… 44%", "2 of 8 files done")
    crop(w, [page.files_card, page.status_lbl.parentWidget()], "files", mode)
    w.close()


def library(mode: str) -> None:
    hist_file = DATA / "library" / "history.json"
    hist_file.unlink(missing_ok=True)
    w = window(mode, (1120, 900))
    h = w.history
    folder = DATA / "Manga"
    for i, done, total, new, pending in ((0, 48, 48, 2, 0), (1, 18, 31, 0, 6), (2, 62, 62, 0, 0)):
        title = MANGA[i][0]
        key = f"example:{i}"
        h.remember(key, f"https://example.com/{i}", title, total, MANGA[i][1], COVERS[i])
        (folder / title).mkdir(parents=True, exist_ok=True)
        f = folder / title / f"{title} - Vol. 01.epub"
        f.touch()
        chapters = [str(n) for n in range(1, total + 1)]
        h.start_run(key, chapters[:done + pending], "epub", 6, str(folder))
        h.file_done(key, chapters[:done], str(f))
        h.mark_seen(key, chapters)
        h.data[key]["new_chapters"] = new
        h.data[key]["last_download"] = time.time() - (i + 1) * 86400 * (2 if i else 1)
    h.save()
    w.show_page(1)  # refreshes the library
    settle()
    cards = [w.library.list.itemAt(i).widget() for i in range(w.library.list.count())]
    crop(w, cards, "library", mode)
    w.close()


def send_to_phone(mode: str) -> None:
    import phone
    phone.Share.start = lambda self: setattr(self, "url", "http://192.168.1.20:8765/nyanga/") or self.url  # no server
    w = window(mode, (1120, 840))
    title = MANGA[1][0]
    folder = DATA / "Phone" / title
    folder.mkdir(parents=True, exist_ok=True)
    files = []
    for v in range(1, 7):
        f = folder / f"{title} - Vol. {v:02d}.epub"
        with f.open("wb") as fh:
            fh.truncate(38_000_000 + v * 2_700_000)  # sparse: the size shows, nothing is written
        files.append(f)
    cover = DATA / "phone-cover.img"
    cover.write_bytes(COVERS[1])
    d = gui.SendToPhone(w, w.settings, title, files, cover, ticked=set(files[:4]))
    d.show()
    QApplication.processEvents()
    d._on_event("visit", -1, 0, 0, "iPhone")
    for i in (0, 1):
        d._on_event("done", i, 1, 1, "iPhone")
    d._on_event("progress", 2, 62, 100, "iPhone")
    QApplication.processEvents()
    save(d.grab(), f"shot-phone-{mode}")
    d.close()
    w.close()


def whats_new(mode: str) -> None:
    w = window(mode, (1120, 840))
    notes = [{"version": VERSION, "date": "2026-10-17", "items": [
        {"kind": "feat", "area": "", "title": "Show what's new after an update",
         "detail": "The first time Nyanga opens after an update, a little window lists what changed "
                   "since the version you had before. Click the version at the bottom left to read it again."},
        {"kind": "fix", "area": "Library", "title": "Keep download progress when a manga is removed",
         "detail": "Removing a manga with downloaded files asks whether to keep or delete them."},
    ]}]
    d = gui.WhatsNew(w, notes, f"Nyanga just updated to version {VERSION}. Here's what changed ♥")
    d.show()
    QApplication.processEvents()
    save(d.grab(), f"shot-whatsnew-{mode}")
    d.close()
    w.close()


def main() -> None:
    global COVERS
    app = QApplication(["nyanga"])
    app.setFont(theme.load_font())
    COVERS = [_cover(t, *colors, motif) for t, _, _, _, colors, motif in MANGA]
    for mode in ("light", "dark"):
        for render in (download_page, search, files, library, send_to_phone, whats_new):
            render(mode)
    app.quit()


COVERS: list[bytes] = []

if __name__ == "__main__":
    main()
