"""
Convert a portrait image to braille-pattern Unicode art and output
SVG tspan elements for embedding in the terminal profile card.

Usage:
    python ascii_to_svg.py

Requires: Pillow (pip install Pillow)
"""
from pathlib import Path
from html import escape
import sys

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageEnhance, ImageFilter

# --- Configuration ---
INPUT = "assets/677.jpeg"
OUTPUT_TXT = "portrait_braille.txt"
OUTPUT_TSPAN = "portrait_tspan.txt"

# Target width in braille characters (each char = 2 px wide)
BRAILLE_WIDTH = 70

# Threshold: pixels darker than this become raised dots (0-255)
THRESHOLD = 128

# SVG placement
START_X = 30
START_Y = 55
LINE_HEIGHT = 6.7

# Braille dot bit positions: [row][col] -> bit value
BRAILLE_MAP = [
    [0x01, 0x08],
    [0x02, 0x10],
    [0x04, 0x20],
    [0x40, 0x80],
]
BRAILLE_BASE = 0x2800


def image_to_braille(image_path, width, threshold):
    img = Image.open(image_path).convert("L")
    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = img.filter(ImageFilter.SHARPEN)

    pixel_width = width * 2
    aspect = img.height / img.width
    pixel_height = (int(pixel_width * aspect) // 4) * 4
    img = img.resize((pixel_width, pixel_height), Image.LANCZOS)
    pixels = list(img.getdata())

    def dark(x, y):
        if x >= pixel_width or y >= pixel_height:
            return False
        return pixels[y * pixel_width + x] < threshold

    lines = []
    for cr in range(pixel_height // 4):
        line = ""
        for cc in range(width):
            code = 0
            px, py = cc * 2, cr * 4
            for r in range(4):
                for c in range(2):
                    if dark(px + c, py + r):
                        code |= BRAILLE_MAP[r][c]
            line += chr(BRAILLE_BASE + code)
        lines.append(line)
    return lines


if __name__ == "__main__":
    lines = image_to_braille(INPUT, BRAILLE_WIDTH, THRESHOLD)
    Path(OUTPUT_TXT).write_text("\n".join(lines), encoding="utf-8")

    y = START_Y
    svg = []
    for line in lines:
        svg.append(f'<tspan x="{START_X}" y="{y:.2f}" xml:space="preserve">{escape(line)}</tspan>')
        y += LINE_HEIGHT
    Path(OUTPUT_TSPAN).write_text("\n".join(svg), encoding="utf-8")

    print(f"Generated {len(svg)} tspans -> {OUTPUT_TSPAN}")
