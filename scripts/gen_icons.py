#!/usr/bin/env python3
"""Regenerate the W1 identity: app icon, menu-bar templates and web favicons.

Single source of truth for the mark so every surface is reproducible instead of hand-cropped.
Draws with CoreGraphics through pyobjc (already a dependency via rumps) — no extra packages,
no Chrome, no Pillow.

    python scripts/gen_icons.py

The mark is three identical parallelograms: a vertical left side of length V, a 45-degree slant
of run S, stepped horizontally by S + GAP. It was reconstructed as clean geometry from the
supplied raster artwork, so it stays crisp at every size instead of being an upscaled JPEG.

Produces:
  assets/W1.icns                     app icon (dark tile, white mark), all sizes 16..1024
  assets/menubar/idle.png            template image, outline — the resting menu-bar state
  assets/menubar/active.png          template image, solid  — shown while recording
  web/public/favicon.svg             dark tile + white mark, vector
  web/public/favicon-32.png          raster fallbacks for browsers that ignore SVG favicons
  web/public/favicon-192.png
  web/public/apple-touch-icon.png    180px, home-screen icon
  web/public/w1-mark.svg             bare mark, inherits currentColor (for in-page use)
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

try:
    import Quartz
    from Foundation import NSURL
except ImportError:  # pragma: no cover - dev-only script
    sys.exit("gen_icons.py needs pyobjc (install the 'macos' extra: pip install -e '.[macos]')")

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PUBLIC = ROOT / "web" / "public"

# --- mark geometry -----------------------------------------------------------------------
S = 183.0   # 45-degree slant run (also each shape's horizontal extent)
V = 183.0   # vertical side
GAP = 8.0   # gap between shapes; wider than the source art so it survives favicon sizes
MW = 2 * (S + GAP) + S   # total mark width
MH = S + V               # total mark height

SHAPES = [
    [(x, 0.0), (x + S, S), (x + S, S + V), (x, V)]
    for x in (i * (S + GAP) for i in range(3))
]

TILE_BG = (0.07, 0.07, 0.08, 1.0)   # near-black, reads on light and dark wallpapers
TILE_FG = (1.0, 1.0, 1.0, 1.0)


def _ctx(size: int):
    """Bitmap context with a top-left origin, so the geometry above reads naturally."""
    ctx = Quartz.CGBitmapContextCreate(
        None, size, size, 8, size * 4, Quartz.CGColorSpaceCreateDeviceRGB(),
        Quartz.kCGImageAlphaPremultipliedFirst | Quartz.kCGBitmapByteOrder32Little,
    )
    Quartz.CGContextTranslateCTM(ctx, 0, size)
    Quartz.CGContextScaleCTM(ctx, 1, -1)
    Quartz.CGContextSetShouldAntialias(ctx, True)
    Quartz.CGContextSetInterpolationQuality(ctx, Quartz.kCGInterpolationHigh)
    return ctx


def _save(ctx, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dest = Quartz.CGImageDestinationCreateWithURL(
        NSURL.fileURLWithPath_(str(path)), "public.png", 1, None
    )
    Quartz.CGImageDestinationAddImage(dest, Quartz.CGBitmapContextCreateImage(ctx), None)
    Quartz.CGImageDestinationFinalize(dest)


def _mark_paths(ctx, ox: float, oy: float, scale: float):
    for pts in SHAPES:
        Quartz.CGContextBeginPath(ctx)
        for i, (px, py) in enumerate(pts):
            x, y = ox + px * scale, oy + py * scale
            if i == 0:
                Quartz.CGContextMoveToPoint(ctx, x, y)
            else:
                Quartz.CGContextAddLineToPoint(ctx, x, y)
        Quartz.CGContextClosePath(ctx)
        yield


def _rounded_rect(ctx, x, y, w, h, r) -> None:
    Quartz.CGContextBeginPath(ctx)
    Quartz.CGContextMoveToPoint(ctx, x + r, y)
    Quartz.CGContextAddArcToPoint(ctx, x + w, y, x + w, y + h, r)
    Quartz.CGContextAddArcToPoint(ctx, x + w, y + h, x, y + h, r)
    Quartz.CGContextAddArcToPoint(ctx, x, y + h, x, y, r)
    Quartz.CGContextAddArcToPoint(ctx, x, y, x + w, y, r)
    Quartz.CGContextClosePath(ctx)


def tile(path: Path, size: int, mark_frac: float = 0.60) -> None:
    """Rounded-tile app icon: Apple's 824/1024 art box and Big Sur corner radius."""
    ctx = _ctx(size)
    pad = size * 0.0977
    box = size - 2 * pad
    Quartz.CGContextSaveGState(ctx)
    Quartz.CGContextSetShadowWithColor(
        ctx, Quartz.CGSizeMake(0, size * 0.012), size * 0.022,
        Quartz.CGColorCreateGenericRGB(0, 0, 0, 0.22),
    )
    _rounded_rect(ctx, pad, pad, box, box, box * 0.2246)
    Quartz.CGContextSetFillColorWithColor(ctx, Quartz.CGColorCreateGenericRGB(*TILE_BG))
    Quartz.CGContextFillPath(ctx)
    Quartz.CGContextRestoreGState(ctx)

    Quartz.CGContextSetFillColorWithColor(ctx, Quartz.CGColorCreateGenericRGB(*TILE_FG))
    scale = (box * mark_frac) / MW
    for _ in _mark_paths(ctx, (size - MW * scale) / 2, (size - MH * scale) / 2, scale):
        Quartz.CGContextFillPath(ctx)
    _save(ctx, path)


def menubar(path: Path, size: int, *, filled: bool) -> None:
    """Template image — pure black plus alpha; AppKit recolours it for the current menu bar."""
    ctx = _ctx(size)
    black = Quartz.CGColorCreateGenericRGB(0, 0, 0, 1)
    Quartz.CGContextSetFillColorWithColor(ctx, black)
    Quartz.CGContextSetStrokeColorWithColor(ctx, black)
    Quartz.CGContextSetLineWidth(ctx, max(1.0, size * 0.055))
    Quartz.CGContextSetLineJoin(ctx, Quartz.kCGLineJoinMiter)
    scale = (size * 0.86) / MW
    for _ in _mark_paths(ctx, (size - MW * scale) / 2, (size - MH * scale) / 2, scale):
        Quartz.CGContextFillPath(ctx) if filled else Quartz.CGContextStrokePath(ctx)
    _save(ctx, path)


def _svg_mark(ox: float, oy: float, scale: float, fmt: str = "{:.1f}") -> str:
    f = fmt.format
    return " ".join(
        "M{},{} L{},{} L{},{} L{},{} Z".format(
            f(ox + pts[0][0] * scale), f(oy + pts[0][1] * scale),
            f(ox + pts[1][0] * scale), f(oy + pts[1][1] * scale),
            f(ox + pts[2][0] * scale), f(oy + pts[2][1] * scale),
            f(ox + pts[3][0] * scale), f(oy + pts[3][1] * scale),
        )
        for pts in SHAPES
    )


def write_svgs() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (PUBLIC / "w1-mark.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MW:g} {MH:g}" '
        f'role="img" aria-label="W1">\n'
        f'  <path d="{_svg_mark(0, 0, 1, "{:g}")}" fill="currentColor"/>\n</svg>\n'
    )
    box, frac = 512.0, 0.62
    scale = (box * frac) / MW
    ox, oy = (box - MW * scale) / 2, (box - MH * scale) / 2
    (PUBLIC / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">\n'
        f'  <rect width="512" height="512" rx="{box * 0.2246:.0f}" ry="{box * 0.2246:.0f}" '
        'fill="#121214"/>\n'
        f'  <path d="{_svg_mark(ox, oy, scale)}" fill="#ffffff"/>\n</svg>\n'
    )


def build_icns() -> None:
    iconset = ASSETS / "W1.iconset"
    if iconset.exists():
        shutil.rmtree(iconset)
    iconset.mkdir(parents=True)
    # (pixel size, iconset names) — @2x entries are byte-identical to their 1x counterpart.
    for px, names in [
        (16, ["icon_16x16.png"]),
        (32, ["icon_16x16@2x.png", "icon_32x32.png"]),
        (64, ["icon_32x32@2x.png"]),
        (128, ["icon_128x128.png"]),
        (256, ["icon_128x128@2x.png", "icon_256x256.png"]),
        (512, ["icon_256x256@2x.png", "icon_512x512.png"]),
        (1024, ["icon_512x512@2x.png"]),
    ]:
        tile(iconset / names[0], px)
        for extra in names[1:]:
            shutil.copyfile(iconset / names[0], iconset / extra)
    subprocess.run(
        ["iconutil", "-c", "icns", str(iconset), "-o", str(ASSETS / "W1.icns")], check=True
    )
    shutil.rmtree(iconset)


def main() -> int:
    build_icns()
    menubar(ASSETS / "menubar" / "idle.png", 48, filled=False)
    menubar(ASSETS / "menubar" / "active.png", 48, filled=True)
    write_svgs()
    tile(PUBLIC / "favicon-32.png", 32)
    tile(PUBLIC / "favicon-192.png", 192)
    tile(PUBLIC / "apple-touch-icon.png", 180)
    print(f"wrote {ASSETS / 'W1.icns'}, menu-bar templates and {PUBLIC}/favicon*")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
