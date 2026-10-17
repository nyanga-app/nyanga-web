"""Renders the app's cats as transparent animated WebPs into public/img/ (cat-<name>-<mode>.webp).

Run with the app's Python from the app checkout, which this folder sits inside:
    QT_QPA_PLATFORM=offscreen ../.venv/bin/python scripts/render_cats.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
APP = HERE.parent
sys.path.insert(0, str(APP))

from PIL import Image
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

import loader

FPS, SECONDS, SCALE = 20, 2.4, 2  # 2x for sharp cats on high-DPI screens
CATS = {  # name: (make widget for a mode, size shown on the page)
    "reading": (lambda m, s: loader.CatLoader(lambda: m, s), (180, 144)),
    "happy": (lambda m, s: loader.CatLoader(lambda: m, s, celebrate=True), (180, 144)),
    "update": (lambda m, s: loader.MiniCat(lambda: m, s, painter=loader.paint_update_cat), (120, 102)),
}


def main() -> None:
    app = QApplication([])
    now = [0.0]
    loader.time.monotonic = lambda: now[0]  # the cats animate on this clock
    out = HERE / "public" / "img"
    for name, (make, (w, h)) in CATS.items():
        for mode in ("light", "dark"):
            widget = make(mode, (w * SCALE, h * SCALE))
            widget._t0 = 0.0
            frames = []
            for i in range(int(FPS * SECONDS)):
                now[0] = i / FPS
                img = QImage(w * SCALE, h * SCALE, QImage.Format_RGBA8888)
                img.fill(Qt.transparent)
                widget.render(img, QPoint(), renderFlags=widget.RenderFlag.DrawChildren)
                frames.append(Image.frombytes("RGBA", (img.width(), img.height()), bytes(img.constBits())))
            path = out / f"cat-{name}-{mode}.webp"
            frames[0].save(path, save_all=True, append_images=frames[1:], duration=1000 // FPS, loop=0,
                           lossless=False, quality=72, method=4)
            print(path.name, f"{path.stat().st_size // 1024} KB")
    app.quit()


if __name__ == "__main__":
    main()
