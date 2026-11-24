#!/usr/bin/env python3
"""One-day world news image: Tuesday 24 November 2026.

Pure standard library. Draws a 1024x1024 front-page-style image with a
5x7 bitmap font and a hand-written PNG encoder (zlib + struct only).
Deterministic: no clock, no randomness, no network.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
NAVY = (13, 27, 46)
PANEL = (22, 40, 63)
PANEL2 = (28, 50, 78)
GOLD = (232, 184, 74)
WHITE = (245, 246, 248)
MUTED = (168, 188, 210)
RED = (214, 69, 65)
GREEN = (46, 160, 110)
BLUE = (66, 135, 214)
ORANGE = (232, 122, 42)
TEAL = (52, 168, 164)
PURPLE = (146, 110, 205)
DARK = (9, 18, 32)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, "1" = filled pixel.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    ":": ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    ";": ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    "\u2022": ("00000", "00100", "01110", "01110", "01110", "00100", "00000"),  # bullet
}
# Normalise curly / long punctuation to the ASCII glyphs above.
ALIASES = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
           "\u2013": "-", "\u2014": "-", "\u2026": ".", "\u00b7": "\u2022"}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap_text(s, max_w, scale):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d2 <= r * r:
                        self.set(xx, yy, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for t in range(thick):
                self.set(x0 + t, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def poly(self, pts, c):
        """Scanline fill of a simple polygon."""
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.set(x, y, c)

    def text(self, x, y, s, scale, c):
        s = "".join(ALIASES.get(ch, ch) for ch in s).upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, y, s, scale, c, cx=512):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)


# ---------------------------------------------------------------- icons
def icon_globe(cv, x, y, s):
    """Globe with a red crack: COP31, no deal."""
    cx, cy, r = x + 55, y + 55, 44
    cv.circle(cx, cy, r, BLUE)
    cv.circle(cx, cy, r, (20, 60, 110), fill=False)
    cv.circle(cx, cy, r - 3, (30, 90, 160))
    # land blobs
    cv.circle(cx - 14, cy - 12, 12, GREEN)
    cv.circle(cx + 16, cy + 10, 13, GREEN)
    cv.circle(cx + 18, cy - 18, 7, GREEN)
    # latitude / longitude lines
    cv.hline(cx - r + 6, cy, 2 * r - 12, BLUE)
    cv.vline(cx, cy - r + 4, 2 * r - 8, BLUE)
    # red crack across the globe
    cv.line(cx - 30, cy - 34, cx - 6, cy - 6, RED, 4)
    cv.line(cx - 6, cy - 6, cx + 12, cy + 8, RED, 4)
    cv.line(cx + 12, cy + 8, cx + 34, cy + 30, RED, 4)


def icon_chip(cv, x, y, s):
    """AI chip: Nvidia."""
    cv.rect(x + 22, y + 28, 66, 54, GREEN)
    cv.rect(x + 34, y + 40, 42, 30, NAVY)
    cv.text(x + 40, y + 48, "AI", 2, GREEN)
    for i in range(4):
        cv.rect(x + 30 + i * 15, y + 16, 6, 12, GREEN)
        cv.rect(x + 30 + i * 15, y + 82, 6, 12, GREEN)
        cv.rect(x + 10, y + 36 + i * 12, 12, 6, GREEN)
        cv.rect(x + 88, y + 36 + i * 12, 12, 6, GREEN)


def icon_fire(cv, x, y, s):
    """Factory with flames: Indonesia fire."""
    cv.rect(x + 14, y + 62, 82, 42, (90, 100, 116))
    cv.rect(x + 14, y + 50, 20, 14, (90, 100, 116))
    cv.rect(x + 40, y + 44, 16, 20, (90, 100, 116))
    cv.rect(x + 62, y + 56, 18, 8, (90, 100, 116))
    cv.poly([(x + 30, y + 62), (x + 44, y + 22), (x + 52, y + 40),
             (x + 62, y + 18), (x + 70, y + 62)], ORANGE)
    cv.poly([(x + 42, y + 62), (x + 50, y + 38), (x + 58, y + 62)], RED)
    cv.poly([(x + 78, y + 62), (x + 88, y + 34), (x + 96, y + 62)], ORANGE)


def icon_ship(cv, x, y, s):
    """Ship under a blast star: war at sea."""
    # explosion starburst
    cx, cy = x + 55, y + 26
    for ang in range(0, 360, 30):
        import math
        r1 = 10 if ang % 60 == 0 else 6
        x1 = cx + int(r1 * math.cos(math.radians(ang)))
        y1 = cy + int(r1 * math.sin(math.radians(ang)))
        x2 = cx + int(22 * math.cos(math.radians(ang)))
        y2 = cy + int(22 * math.sin(math.radians(ang)))
        cv.line(x1, y1, x2, y2, ORANGE, 3)
    cv.circle(cx, cy, 7, RED)
    # hull + mast
    cv.poly([(x + 12, y + 72), (x + 98, y + 72), (x + 88, y + 92),
             (x + 24, y + 92)], (150, 160, 175))
    cv.rect(x + 52, y + 44, 6, 28, (150, 160, 175))
    cv.poly([(x + 58, y + 46), (x + 58, y + 64), (x + 80, y + 64)], RED)
    # sea
    cv.hline(x + 8, y + 98, 94, BLUE)
    cv.hline(x + 16, y + 104, 78, BLUE)


def icon_chess(cv, x, y, s):
    """Chessboard with a crown: world championship."""
    bx, by = x + 16, y + 30
    for r in range(4):
        for c in range(4):
            if (r + c) % 2 == 0:
                cv.rect(bx + c * 20, by + r * 18, 20, 18, WHITE)
            else:
                cv.rect(bx + c * 20, by + r * 18, 20, 18, (60, 70, 88))
    # crown above the board
    cv.poly([(x + 38, y + 26), (x + 38, y + 10), (x + 48, y + 20),
             (x + 55, y + 8), (x + 62, y + 20), (x + 72, y + 10),
             (x + 72, y + 26)], GOLD)
    cv.rect(x + 38, y + 26, 34, 5, GOLD)


def icon_flags(cv, x, y, s):
    """Two flags side by side: India and Nepal."""
    # India: saffron / white / green with wheel
    fx, fy = x + 12, y + 34
    cv.rect(fx, fy, 40, 12, (255, 153, 51))
    cv.rect(fx, fy + 12, 40, 12, WHITE)
    cv.rect(fx, fy + 24, 40, 12, (19, 136, 8))
    cv.circle(fx + 20, fy + 18, 5, (0, 0, 128))
    # Nepal: crimson pennant with blue border
    nx, ny = x + 58, y + 30
    cv.poly([(nx, ny), (nx + 38, ny + 10), (nx, ny + 20)], (220, 20, 60))
    cv.poly([(nx, ny + 20), (nx + 30, ny + 28), (nx, ny + 40)], (220, 20, 60))
    cv.line(nx, ny, nx, ny + 40, (0, 0, 128), 3)


# ---------------------------------------------------------------- stories
# Headline (upper case), sub-line, accent colour, icon function.
STORIES = [
    ("COP31 COLLAPSES",
     "No climate pact in Antalya. First failed UN summit since 2009.",
     RED, icon_globe, "CLIMATE"),
    ("HUANG BACK AT NVIDIA",
     "Board reinstates CEO after scandal. Shares jump about 30%.",
     GREEN, icon_chip, "TECH"),
    ("24 DEAD IN FACTORY FIRE",
     "Candy plant blaze in Banten, Indonesia. About 30 still missing.",
     ORANGE, icon_fire, "ASIA"),
    ("WAR SPREADS AT SEA",
     "Russian ship hit off Libya. Kyiv region struck in drone attacks.",
     BLUE, icon_ship, "UKRAINE"),
    ("CHESS CROWN ON THE LINE",
     "Gukesh defends world title vs Sindarov. Play opens in Geneva.",
     PURPLE, icon_chess, "SPORT"),
    ("INDIA-NEPAL PACT",
     "Modi and PM Shah sign 8 deals. Rs 15,000 crore aid package.",
     TEAL, icon_flags, "DIPLOMACY"),
]

TICKER = ("ALSO: UK SANCTIONS MYANMAR GENERALS - INDIA-NZ TEST DRAWN "
          "- SUPERMOON TONIGHT")


def draw():
    cv = Canvas(W, H, NAVY)
    # header
    cv.rect(0, 0, W, 6, GOLD)
    cv.text_center(30, "24 NOVEMBER 2026", 7, WHITE)
    cv.text_center(96, "TUESDAY  -  THE WORLD IN ONE IMAGE", 2, GOLD)
    cv.hline(24, 138, W - 48, GOLD)
    cv.hline(24, 142, W - 48, GOLD)

    # story grid: 2 cols x 3 rows
    px, py, pw, ph, gap = 24, 160, 480, 248, 16
    for i, (head, sub, accent, icon, tag) in enumerate(STORIES):
        x = px + (i % 2) * (pw + gap)
        y = py + (i // 2) * (ph + gap)
        cv.rect(x, y, pw, ph, PANEL)
        cv.rect(x, y, pw, 5, accent)
        cv.rect(x, y + 5, 130, ph - 5, PANEL2)
        icon(cv, x + 10, y + 30, 1)
        # tag chip
        cv.rect(x + 142, y + 18, text_width(tag, 2) + 16, 22, accent)
        cv.text(x + 150, y + 23, tag, 2, WHITE)
        # headline, wrapped at scale 3
        lines = wrap_text(head, pw - 142 - 16, 3)
        ty = y + 52
        for ln in lines:
            cv.text(x + 142, ty, ln, 3, WHITE)
            ty += 26
        # sub-line, wrapped at scale 2
        sub_lines = wrap_text(sub, pw - 142 - 16, 2)
        ty += 6
        for ln in sub_lines:
            cv.text(x + 142, ty, ln, 2, MUTED)
            ty += 18

    # footer ticker
    cv.rect(0, 948, W, 76, DARK)
    cv.rect(0, 948, W, 3, GOLD)
    cv.text_center(972, TICKER, 2, GOLD)
    cv.text_center(1000, "SIX STORIES, ONE DAY  -  24 NOVEMBER 2026", 1, MUTED)
    return cv


# ---------------------------------------------------------------- PNG write
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    cv = draw()
    path = os.path.join(out_dir, "entry.png")
    n = write_png(cv, path)
    print(f"wrote {path} ({n} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
