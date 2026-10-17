"""Draws the link-preview card (public/img/card.png, 1200x630) and the phone icon
(public/apple-touch-icon.png, 180x180) from the app's own cat, colors and font.

Run from this folder inside the app checkout, after scripts/render_shots.py (the card shows
a slice of its Download page picture):

    QT_QPA_PLATFORM=offscreen ../.venv/bin/python scripts/render_card.py
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE.parent))

from PIL import Image  # noqa: E402
from PySide6.QtCore import QPoint, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QFont, QImage, QLinearGradient, QPainter, QPainterPath  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

import loader  # noqa: E402
import theme  # noqa: E402

W, H = 1200, 630


def font(px: int, weight: QFont.Weight) -> QFont:
    f = QFont(QApplication.font())
    f.setPixelSize(px)
    f.setWeight(weight)
    return f


def card() -> None:
    light = theme.PALETTES[theme.LIGHT]
    img = QImage(W, H, QImage.Format_ARGB32)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.SmoothPixmapTransform)
    g = QLinearGradient(0, 0, W, H)
    g.setColorAt(0, QColor("#fff0f6"))
    g.setColorAt(1, QColor("#ffd6e7"))
    p.fillRect(img.rect(), g)

    # A slice of the app, tilted a little, peeking in from the right.
    shot = QImage(str(HERE / "public" / "img" / "screenshot-light.webp"))
    if shot.isNull():  # Qt without WebP: go through Pillow
        pil = Image.open(HERE / "public" / "img" / "screenshot-light.webp").convert("RGBA")
        shot = QImage(pil.tobytes(), pil.width, pil.height, QImage.Format_RGBA8888).copy()
    shot = shot.scaledToWidth(760, Qt.SmoothTransformation)
    p.save()
    p.translate(640, 70)
    p.rotate(-4)
    clip = QPainterPath()
    clip.addRoundedRect(QRectF(0, 0, shot.width(), shot.height()), 22, 22)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(255, 92, 154, 40))
    p.drawRoundedRect(QRectF(6, 12, shot.width(), shot.height()), 22, 22)  # soft shadow
    p.setClipPath(clip)
    p.drawImage(0, 0, shot)
    p.restore()

    # The reading cat, drawn by the app's own code.
    cat = loader.CatLoader(lambda: theme.LIGHT, (300, 240))
    cat_img = QImage(300, 240, QImage.Format_ARGB32)
    cat_img.fill(Qt.transparent)
    cat.render(cat_img, QPoint(), renderFlags=cat.RenderFlag.DrawChildren)  # no window background
    p.drawImage(54, 40, cat_img)

    p.setPen(QColor(light["accent"]))
    p.setFont(font(112, QFont.Bold))
    p.drawText(QRectF(70, 270, 600, 130), Qt.AlignLeft | Qt.AlignVCenter, "Nyanga")
    p.setPen(QColor(light["text"]))
    p.setFont(font(34, QFont.DemiBold))
    p.drawText(QRectF(74, 410, 600, 60), Qt.AlignLeft | Qt.AlignVCenter, "a cozy manga downloader for Windows")
    p.setPen(QColor(light["muted"]))
    p.setFont(font(28, QFont.Medium))
    p.drawText(QRectF(76, 480, 560, 50), Qt.AlignLeft | Qt.AlignVCenter, "one file per volume · CBZ, PDF, EPUB")
    p.end()
    out = HERE / "public" / "img" / "card.png"
    img.save(str(out))
    print(out.name, f"{out.stat().st_size // 1024} KB")


def touch_icon() -> None:
    img = QImage(180, 180, QImage.Format_ARGB32)
    img.fill(QColor("#ff9cc6"))  # iOS rounds the corners itself and doesn't like transparency
    p = QPainter(img)
    p.drawPixmap(0, 0, theme._render(theme._APP_ICON, 180))
    p.end()
    out = HERE / "public" / "apple-touch-icon.png"
    img.save(str(out))
    print(out.name, f"{out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    app = QApplication([])
    app.setFont(theme.load_font())
    card()
    touch_icon()
