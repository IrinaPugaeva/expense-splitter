#!/usr/bin/env python3
"""Generate presentation-style ExpenseMate screenshots without a browser."""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "screenshots"
OUTPUT.mkdir(parents=True, exist_ok=True)

W, H = 1440, 900
BLUE = "#148bd2"
BLUE_DARK = "#0875b5"
PURPLE = "#9a5adf"
PURPLE_DARK = "#7f3dcc"
GREEN = "#2fbf71"
RED = "#d94452"
INK = "#273148"
MUTED = "#74809a"
LINE = "#e5eaf3"
PAGE = "#f4f8fc"
WHITE = "#ffffff"

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(str(FONT_DIR / name), size)


def text(draw: ImageDraw.ImageDraw, xy, value: str, size=24, color=INK, bold=False, anchor=None):
    draw.text(xy, value, fill=color, font=font(size, bold), anchor=anchor)


def rounded(draw, box, radius=16, fill=WHITE, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def wrap(draw, value: str, max_width: int, size=22, bold=False):
    words = value.split()
    lines, current = [], ""
    f = font(size, bold)
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=f)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def topbar(draw, authenticated=False):
    draw.rectangle((0, 0, W, 64), fill=BLUE)
    text(draw, (32, 32), "ExpenseMate", 21, WHITE, True, "lm")
    if authenticated:
        draw.ellipse((1337, 14, 1373, 50), fill=WHITE)
        text(draw, (1355, 32), "I", 17, BLUE_DARK, True, "mm")
        text(draw, (1325, 32), "Irina", 15, WHITE, False, "rm")


def sidebar(draw, active: str):
    draw.rectangle((0, 64, 220, H), fill=WHITE)
    draw.line((220, 64, 220, H), fill=LINE, width=1)
    text(draw, (24, 98), "NAVIGATION", 12, BLUE_DARK, True)
    items = [("My groups", "groups"), ("Create group", "create"), ("Profile · later", "profile"), ("Sign out", "logout")]
    y = 128
    for label, key in items:
        if key == active:
            rounded(draw, (18, y, 202, y + 44), 9, "#e6f5fe", "#bfe5fa")
            color, bold = BLUE_DARK, True
        else:
            color, bold = ("#a0a8b8", False) if key == "profile" else ("#66718a", False)
        text(draw, (34, y + 22), label, 15, color, bold, "lm")
        y += 52


def card(draw, box, radius=16):
    # subtle shadow
    shadow = (box[0] + 5, box[1] + 7, box[2] + 5, box[3] + 7)
    rounded(draw, shadow, radius, "#e9eef5")
    rounded(draw, box, radius, WHITE, LINE)


def login(error=False):
    img = Image.new("RGB", (W, H), "#f5f7fb")
    draw = ImageDraw.Draw(img)
    topbar(draw)
    # soft background shapes
    draw.ellipse((-180, 160, 520, 860), fill="#eff8fd")
    draw.ellipse((900, 90, 1540, 760), fill="#f3edfb")

    text(draw, (128, 255), "SHARED EXPENSE MANAGEMENT", 13, BLUE_DARK, True)
    lines = ["Shared expenses", "made simple"]
    y = 292
    for line in lines:
        text(draw, (128, y), line, 56, PURPLE, True)
        y += 66
    subtitle = "Create groups, split expenses and track shares in one clear place."
    for line in wrap(draw, subtitle, 530, 21):
        text(draw, (128, y + 10), line, 21, "#58657d")
        y += 32
    pills = ["Responsive web app", "Role-based groups", "Simple local demo"]
    x = 128
    for p in pills:
        w = draw.textbbox((0, 0), p, font=font(13, True))[2] + 30
        rounded(draw, (x, 550, x + w, 586), 18, WHITE, "#dde5f0")
        text(draw, (x + 15, 568), p, 13, "#66718a", True, "lm")
        x += w + 10

    box = (870, 150, 1282, 760)
    card(draw, box, 18)
    text(draw, (910, 190), "WELCOME BACK", 12, BLUE_DARK, True)
    text(draw, (910, 224), "Sign in", 31, INK, True)
    text(draw, (910, 268), "Use the demo account or your registered", 14, MUTED)
    text(draw, (910, 291), "ExpenseMate account.", 14, MUTED)

    y = 330
    if error:
        rounded(draw, (910, y, 1242, y + 54), 9, "#fff1f2", "#f3b8bd")
        text(draw, (926, y + 17), "Invalid email or password.", 14, "#a52a36", True)
        text(draw, (926, y + 36), "Please try again.", 14, "#a52a36", True)
        y += 76

    text(draw, (910, y), "EMAIL", 12, "#4a556d", True)
    rounded(draw, (910, y + 24, 1242, y + 72), 8, WHITE, "#d9e0eb")
    text(draw, (924, y + 48), "irina@torrens.edu.au", 15, INK, False, "lm")
    y += 96
    text(draw, (910, y), "PASSWORD", 12, "#4a556d", True)
    rounded(draw, (910, y + 24, 1242, y + 72), 8, WHITE, "#d9e0eb")
    text(draw, (924, y + 48), "••••••••••••••", 17, INK, False, "lm")
    y += 94
    rounded(draw, (910, y, 1242, y + 48), 8, PURPLE_DARK)
    text(draw, (1076, y + 24), "SIGN IN", 14, WHITE, True, "mm")
    y += 60
    rounded(draw, (910, y, 1242, y + 46), 8, "#ffffff", "#cfd7e5")
    text(draw, (1076, y + 23), "CREATE ACCOUNT — LATER", 13, "#9aa3b3", True, "mm")
    y += 72
    rounded(draw, (910, y, 1242, y + 86), 10, "#f5f8fc")
    text(draw, (926, y + 18), "DEMO ACCOUNT", 11, "#5e6980", True)
    text(draw, (926, y + 42), "irina@torrens.edu.au", 13, "#4d3980")
    text(draw, (926, y + 64), "ExpenseMate123!", 13, "#4d3980")
    return img


def groups_page():
    img = Image.new("RGB", (W, H), PAGE)
    draw = ImageDraw.Draw(img)
    topbar(draw, True)
    sidebar(draw, "groups")

    text(draw, (268, 114), "WORKSPACE", 12, BLUE_DARK, True)
    text(draw, (268, 145), "My groups", 36, INK, True)
    text(draw, (268, 194), "Create a group or open one where you are already a member.", 16, MUTED)
    rounded(draw, (1178, 132, 1376, 180), 9, PURPLE_DARK)
    text(draw, (1277, 156), "+  CREATE GROUP", 13, WHITE, True, "mm")

    main = (268, 236, 1015, 776)
    side = (1040, 236, 1376, 776)
    card(draw, main)
    card(draw, side)
    text(draw, (298, 270), "GROUPS I BELONG TO", 12, BLUE_DARK, True)
    text(draw, (298, 300), "Your shared spaces", 23, INK, True)
    draw.line((298, 338, 985, 338), fill=LINE, width=1)
    rounded(draw, (936, 269, 975, 308), 20, "#edf8ff")
    text(draw, (955, 288), "2", 14, BLUE_DARK, True, "mm")

    def group_card(y, initial, title_value, desc, meta):
        rounded(draw, (296, y, 986, y + 138), 12, WHITE, LINE)
        rounded(draw, (318, y + 28, 366, y + 76), 12, "#e8efff")
        text(draw, (342, y + 52), initial, 20, PURPLE_DARK, True, "mm")
        text(draw, (388, y + 26), title_value, 20, INK, True)
        text(draw, (388, y + 58), desc, 14, MUTED)
        text(draw, (388, y + 91), meta, 12, "#8993a7")
        rounded(draw, (884, y + 48, 960, y + 80), 16, "#fff3d5")
        text(draw, (922, y + 64), "Admin", 12, "#9a6500", True, "mm")

    group_card(360, "G", "Grocery", "Weekly food and household shopping", "4 members   ·   Household   ·   Equal split")
    group_card(516, "S", "Summer trip", "Shared travel expenses", "3 members   ·   Travel   ·   Equal split")

    text(draw, (1070, 270), "STARTER SCOPE", 12, BLUE_DARK, True)
    text(draw, (1070, 300), "Implemented now", 23, INK, True)
    checks = [
        "Email and password login",
        "Invalid-login error handling",
        "Create a new expense group",
        "Automatic Group Admin role",
        "Required and 100-character title validation",
    ]
    y = 352
    for value in checks:
        draw.ellipse((1070, y, 1090, y + 20), fill="#e8f9ef")
        text(draw, (1080, y + 10), "✓", 12, "#168348", True, "mm")
        for i, line in enumerate(wrap(draw, value, 246, 14)):
            text(draw, (1104, y + i * 20 + 1), line, 14, "#566179")
        y += 60 if len(wrap(draw, value, 246, 14)) > 1 else 43
    rounded(draw, (1070, 631, 1346, 739), 10, "#faf7ff")
    note = "Expenses, invitations, PayID and payments are intentionally reserved for later iterations."
    yy = 651
    for line in wrap(draw, note, 242, 13):
        text(draw, (1086, yy), line, 13, "#76658f")
        yy += 21
    return img


def create_page(error=False):
    img = Image.new("RGB", (W, H), PAGE)
    draw = ImageDraw.Draw(img)
    topbar(draw, True)
    sidebar(draw, "create")
    text(draw, (268, 114), "GROUP OPERATIONS · US004", 12, BLUE_DARK, True)
    text(draw, (268, 145), "Create group", 36, INK, True)
    text(draw, (268, 194), "After saving, you become the Group Admin for this group.", 16, MUTED)

    form_box = (268, 236, 980, 810)
    info_box = (1005, 236, 1376, 610)
    card(draw, form_box)
    card(draw, info_box)

    x1, x2 = 300, 948
    y = 276
    text(draw, (x1, y), "GROUP TITLE *", 12, "#4a556d", True)
    rounded(draw, (x1, y + 24, x2, y + 72), 8, WHITE, "#d9e0eb")
    if not error:
        text(draw, (x1 + 14, y + 48), "Flatmates", 15, INK, False, "lm")
    text(draw, (x1, y + 82), "Required. Maximum 100 characters.", 12, "#8a95aa")
    if error:
        text(draw, (x1, y + 103), "Group title is required.", 13, RED, True)
        offset = 24
    else:
        offset = 0
    y += 132 + offset
    text(draw, (x1, y), "CATEGORY", 12, "#4a556d", True)
    text(draw, (635, y), "DEFAULT SPLIT", 12, "#4a556d", True)
    rounded(draw, (x1, y + 24, 612, y + 72), 8, WHITE, "#d9e0eb")
    rounded(draw, (635, y + 24, x2, y + 72), 8, WHITE, "#d9e0eb")
    text(draw, (x1 + 14, y + 48), "Household", 15, INK, False, "lm")
    text(draw, (649, y + 48), "Equal split", 15, INK, False, "lm")
    text(draw, (588, y + 48), "⌄", 17, MUTED, False, "mm")
    text(draw, (924, y + 48), "⌄", 17, MUTED, False, "mm")
    y += 108
    text(draw, (x1, y), "DESCRIPTION", 12, "#4a556d", True)
    rounded(draw, (x1, y + 24, x2, y + 150), 8, WHITE, "#d9e0eb")
    text(draw, (x1 + 14, y + 44), "Shared household expenses", 15, INK)
    text(draw, (x1, y + 160), "Optional. Add a short explanation of what the group is for.", 12, "#8a95aa")
    y += 205
    rounded(draw, (x1, y, x1 + 175, y + 48), 8, PURPLE_DARK)
    text(draw, (x1 + 88, y + 24), "CREATE GROUP", 13, WHITE, True, "mm")
    rounded(draw, (x1 + 190, y, x1 + 300, y + 48), 8, WHITE, "#cfd7e5")
    text(draw, (x1 + 245, y + 24), "CANCEL", 13, "#66718a", True, "mm")

    draw.ellipse((1035, 272, 1083, 320), fill="#e8f8ef")
    text(draw, (1059, 296), "A", 18, "#19884d", True, "mm")
    text(draw, (1035, 348), "YOUR ROLE", 12, BLUE_DARK, True)
    text(draw, (1035, 380), "Group Admin", 25, INK, True)
    p = "You will be added as the first member and assigned the Admin role automatically."
    yy = 425
    for line in wrap(draw, p, 300, 15):
        text(draw, (1035, yy), line, 15, "#68738a")
        yy += 24
    draw.line((1035, 514, 1345, 514), fill=LINE, width=1)
    p2 = "Later versions can add invitations, member removal, expense editing and group deletion."
    yy = 540
    for line in wrap(draw, p2, 300, 13):
        text(draw, (1035, yy), line, 13, MUTED)
        yy += 21
    return img


def main():
    images = {
        "login.png": login(False),
        "invalid-login.png": login(True),
        "my-groups.png": groups_page(),
        "create-group.png": create_page(False),
        "invalid-group.png": create_page(True),
    }
    for name, image in images.items():
        path = OUTPUT / name
        image.save(path, optimize=True)
        print(f"Rendered {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
