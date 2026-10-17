"""Copies the app's icon set (theme._ICONS) into src/lib/icons.ts, so the site uses the same icons.

Run from this folder inside the app checkout:
    ../.venv/bin/python scripts/export_icons.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE.parent))

import theme  # noqa: E402

icons = {name: svg.replace("COLOR", "currentColor") for name, svg in theme._ICONS.items()}
out = HERE / "src" / "lib" / "icons.ts"
out.write_text("// The app's icons (24x24, drawn in currentColor), copied from theme.py by scripts/export_icons.py.\n\n"
               f"export const ICONS: Record<string, string> = {json.dumps(icons, indent=2)};\n", encoding="utf-8")
print(f"{len(icons)} icons -> {out.relative_to(HERE)}")
