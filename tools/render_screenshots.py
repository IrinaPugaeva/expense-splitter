#!/usr/bin/env python3
"""Create lightweight presentation previews for the README.

The application itself is server-rendered by Django. These previews are generated with
Pillow so repository screenshots can be refreshed without starting a browser.
"""
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1440, 900
BLUE = "#148bd2"
BLUE_DARK = "#0875b5"
PURPLE = "#8a43d5"
INK = "#273148"
MUTED = "#74809a"
LINE = "#dfe6f1"
PAGE = "#f4f8fc"
WHITE = "#ffffff"
GREEN = "#2b9f60"
RED = "#c63f4e"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(size, bold=False):
    return ImageFont.truetype(
        str(FONT_DIR / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), size
    )


def txt(draw, xy, value, size=18, colour=INK, bold=False, anchor=None):
    draw.text(xy, value, font=font(size, bold), fill=colour, anchor=anchor)


def box(draw, coords, fill=WHITE, outline=LINE, radius=14, width=1):
    draw.rounded_rectangle(coords, radius=radius, fill=fill, outline=outline, width=width)


def lines(draw, value, x, y, width=48, size=16, colour=MUTED, bold=False, step=25):
    for index, line in enumerate(wrap(value, width)):
        txt(draw, (x, y + index * step), line, size, colour, bold)


def shell(auth=True, active="groups"):
    image = Image.new("RGB", (W, H), PAGE)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, W, 64), fill=BLUE)
    txt(draw, (30, 32), "ExpenseMate", 21, WHITE, True, "lm")
    if auth:
        draw.ellipse((1342, 14, 1378, 50), fill=WHITE)
        txt(draw, (1360, 32), "I", 16, BLUE_DARK, True, "mm")
        txt(draw, (1327, 32), "Irina", 14, WHITE, False, "rm")
        draw.rectangle((0, 64, 220, H), fill=WHITE)
        nav = [("My groups", "groups"), ("Create group", "create"), ("My payments", "payments"), ("Profile", "profile"), ("Sign out", "logout")]
        txt(draw, (25, 95), "NAVIGATION", 11, BLUE_DARK, True)
        y = 120
        for label, key in nav:
            if key == active:
                box(draw, (17, y, 203, y + 42), fill="#e8f5fd", outline="#bfdef0", radius=8)
            txt(draw, (33, y + 21), label, 14, BLUE_DARK if key == active else "#65718a", key == active, "lm")
            y += 49
    return image, draw


def heading(draw, eyebrow, title, subtitle, action=None):
    txt(draw, (270, 105), eyebrow.upper(), 11, BLUE_DARK, True)
    txt(draw, (270, 137), title, 34, INK, True)
    txt(draw, (270, 187), subtitle, 15, MUTED)
    if action:
        box(draw, (1180, 132, 1375, 178), fill=PURPLE, outline=PURPLE, radius=9)
        txt(draw, (1277, 155), action, 13, WHITE, True, "mm")


def demo_card(draw, heading, values, x, y, width=350):
    """Draw one compact page-specific data card."""
    height = 50 + 25 * len(values)
    box(
        draw,
        (x, y, x + width, y + height),
        fill="#eef2f8",
        outline="#e1e7f0",
        radius=12,
    )
    txt(draw, (x + 18, y + 17), heading, 12, "#5d6982", True)
    for index, value in enumerate(values):
        txt(draw, (x + 18, y + 47 + index * 25), value, 11, "#4d3980")


def field(draw, x, y, label, value, width=390, error=None):
    txt(draw, (x, y), label.upper(), 11, "#4d5870", True)
    box(draw, (x, y + 22, x + width, y + 70), radius=8)
    txt(draw, (x + 14, y + 46), value, 14, "#596273", False, "lm")
    if error:
        txt(draw, (x, y + 80), error, 11, RED, True)


def login(error=False):
    image, draw = shell(auth=False)
    draw.ellipse((-250, 150, 500, 900), fill="#ecf7fd")
    draw.ellipse((980, 80, 1600, 720), fill="#f3ecfb")
    txt(draw, (120, 250), "SHARED EXPENSE MANAGEMENT", 12, BLUE_DARK, True)
    txt(draw, (120, 295), "Shared expenses", 50, PURPLE, True)
    txt(draw, (120, 355), "made simple", 50, PURPLE, True)
    lines(draw, "Create groups, split expenses and track shares in one clear place.", 120, 435, 50, 18, "#59657c")
    box(draw, (820, 115, 1285, 850), radius=18)
    txt(draw, (860, 160), "WELCOME BACK", 12, BLUE_DARK, True)
    txt(draw, (860, 200), "Sign in", 31, INK, True)
    txt(draw, (860, 245), "Use a demo account or your registered account.", 14, MUTED)
    y = 290
    if error:
        box(draw, (860, y, 1245, y + 52), fill="#fff1f2", outline="#efb6bd", radius=8)
        txt(draw, (878, y + 26), "Invalid credentials.", 13, RED, True, "lm")
        y += 72
    field(draw, 860, y, "Email", "irina@test.com", 385)
    field(draw, 860, y + 105, "Password", "••••••••••••", 385)
    box(draw, (860, y + 220, 1245, y + 270), fill=PURPLE, outline=PURPLE, radius=8)
    txt(draw, (1052, y + 245), "SIGN IN", 14, WHITE, True, "mm")
    txt(draw, (860, y + 295), "Create account", 12, BLUE_DARK, True)
    txt(draw, (1245, y + 295), "Forgot password?", 12, BLUE_DARK, True, "rm")
    demo_card(draw, "Demo account", ["irina@test.com", "Password1234"], 860, y + 330, 385)
    return image


def groups_page():
    image, draw = shell(True, "groups")
    heading(draw, "Workspace", "My groups", "Open a group, create one, or respond to an invitation.", "+ CREATE GROUP")
    box(draw, (270, 230, 1008, 770))
    txt(draw, (300, 263), "GROUPS I BELONG TO", 11, BLUE_DARK, True)
    txt(draw, (300, 296), "Your shared spaces", 21, INK, True)
    y = 345
    for initial, title, desc, role in [
        ("F", "Flatmates", "Shared household costs", "Admin"),
        ("G", "Grocery", "Weekly food and household shopping", "Admin"),
        ("S", "Summer trip", "Shared travel expenses", "Admin"),
    ]:
        box(draw, (300, y, 978, y + 116), radius=11)
        box(draw, (322, y + 25, 368, y + 71), fill="#e8efff", outline="#e8efff", radius=12)
        txt(draw, (345, y + 48), initial, 18, PURPLE, True, "mm")
        txt(draw, (390, y + 25), title, 18, INK, True)
        txt(draw, (390, y + 55), desc, 13, MUTED)
        txt(draw, (390, y + 83), "4 members · Equal split", 11, "#8c96aa")
        box(draw, (882, y + 40, 952, y + 72), fill="#fff4d9", outline="#fff4d9", radius=16)
        txt(draw, (917, y + 56), role, 11, "#946600", True, "mm")
        y += 130
    box(draw, (1032, 230, 1380, 520))
    txt(draw, (1060, 264), "PENDING INVITATIONS", 11, BLUE_DARK, True)
    txt(draw, (1060, 297), "Groups waiting for you", 20, INK, True)
    box(draw, (1060, 340, 1350, 454), radius=10)
    txt(draw, (1080, 365), "Online shopping", 16, INK, True)
    txt(draw, (1080, 393), "Invited by Jobaida", 12, MUTED)
    box(draw, (1080, 414, 1154, 446), fill="#e5f8ed", outline="#e5f8ed", radius=7)
    txt(draw, (1117, 430), "ACCEPT", 10, GREEN, True, "mm")
    box(draw, (1163, 414, 1240, 446), fill=WHITE, outline="#edbdc3", radius=7)
    txt(draw, (1201, 430), "DECLINE", 10, RED, True, "mm")
    demo_card(draw, "Demo groups", ["Flatmates", "Grocery", "Summer trip"], 1032, 545, 348)
    return image


def create_group():
    image, draw = shell(True, "create")
    heading(draw, "Group operations · US004", "Create group", "After saving, you become the Group Admin.")
    box(draw, (270, 230, 960, 765))
    field(draw, 305, 275, "Group title", "Flatmates 2", 620)
    field(draw, 305, 380, "Category", "Household", 290)
    field(draw, 635, 380, "Default split", "Equal split", 290)
    field(draw, 305, 485, "Description", "Shared costs", 620)
    box(draw, (305, 625, 465, 673), fill=PURPLE, outline=PURPLE, radius=8)
    txt(draw, (385, 649), "CREATE GROUP", 12, WHITE, True, "mm")
    box(draw, (995, 230, 1378, 565))
    box(draw, (1035, 270, 1090, 325), fill="#e6f8ed", outline="#e6f8ed", radius=28)
    txt(draw, (1062, 297), "A", 21, GREEN, True, "mm")
    txt(draw, (1035, 360), "YOUR ROLE", 11, BLUE_DARK, True)
    txt(draw, (1035, 395), "Group Admin", 25, INK, True)
    lines(draw, "You will be added as the first member and assigned the Admin role automatically.", 1035, 438, 34, 15, MUTED)
    txt(draw, (1035, 525), "Future: direct payments, cloud hosting, email delivery.", 11, MUTED)
    demo_card(draw, "Demo group", ["Title: Flatmates 2", "Description: Shared costs"], 995, 590, 383)
    return image


def group_dashboard():
    image, draw = shell(True, "groups")
    heading(draw, "Group dashboard · US008", "Flatmates", "Shared household costs", "+ ADD EXPENSE")
    box(draw, (270, 230, 1005, 770))
    txt(draw, (300, 267), "RECENT EXPENSES", 11, BLUE_DARK, True)
    y = 315
    for title, meta, amount, status in [
        ("Dinner", "Paid by Irina · due in 3 days", "AUD 60.00", "Open"),
        ("Electricity bill", "Paid by Samesh · overdue", "AUD 160.40", "Overdue"),
        ("Internet", "Paid by Jobaida", "AUD 79.00", "Settled"),
    ]:
        box(draw, (300, y, 975, y + 92), radius=10)
        txt(draw, (322, y + 24), title, 16, INK, True)
        txt(draw, (322, y + 53), meta, 12, MUTED)
        txt(draw, (950, y + 25), amount, 14, INK, True, "rm")
        txt(draw, (950, y + 55), status, 11, GREEN if status == "Settled" else RED if status == "Overdue" else "#966800", True, "rm")
        y += 108
    box(draw, (1030, 230, 1380, 580))
    txt(draw, (1060, 267), "GROUP MEMBERS", 11, BLUE_DARK, True)
    for index, (name, role) in enumerate([("Irina", "Admin"), ("Nicolas", "Member"), ("Jobaida", "Member"), ("Samesh", "Member")]):
        yy = 310 + index * 55
        draw.ellipse((1060, yy, 1094, yy + 34), fill="#e9f6fd")
        txt(draw, (1077, yy + 17), name[0], 12, BLUE_DARK, True, "mm")
        txt(draw, (1110, yy + 17), name, 13, INK, True, "lm")
        txt(draw, (1348, yy + 17), role, 11, MUTED, False, "rm")
    demo_card(draw, "Demo group", ["Flatmates", "Check members, roles and expenses"], 1030, 605, 350)
    return image


def add_expense():
    image, draw = shell(True, "groups")
    heading(draw, "Expense management · US009–US012", "Flatmates — add expense", "Choose payer, participants, and split method.")
    box(draw, (270, 230, 940, 790))
    field(draw, 305, 270, "Title", "Demo lunch", 285)
    field(draw, 620, 270, "Amount (AUD)", "60.00", 285)
    field(draw, 305, 370, "Date", "2026-08-10", 285)
    field(draw, 620, 370, "Category", "Food", 285)
    field(draw, 305, 470, "Paid by", "Irina", 285)
    field(draw, 620, 470, "Due date", "2026-08-13", 285)
    field(draw, 305, 570, "Description", "Lunch after class", 600)
    box(draw, (305, 690, 465, 738), fill=PURPLE, outline=PURPLE, radius=8)
    txt(draw, (385, 714), "SAVE EXPENSE", 12, WHITE, True, "mm")
    box(draw, (970, 230, 1380, 650))
    txt(draw, (1000, 270), "SPLIT SETUP", 11, BLUE_DARK, True)
    field(draw, 1000, 300, "Split method", "Equal", 340)
    txt(draw, (1000, 405), "PARTICIPANTS", 11, "#4d5870", True)
    for index, name in enumerate(["Irina", "Nicolas", "Jobaida", "Samesh"]):
        yy = 438 + index * 43
        draw.rectangle((1002, yy, 1020, yy + 18), outline=BLUE_DARK, width=2)
        if name != "Samesh":
            draw.line((1006, yy + 9, 1011, yy + 14), fill=GREEN, width=2)
            draw.line((1011, yy + 14, 1018, yy + 4), fill=GREEN, width=2)
        txt(draw, (1034, yy + 9), name, 13, INK, False, "lm")
    demo_card(draw, "Demo expense", ["Title: Demo lunch", "Amount: AUD 60.00", "Payer: Irina · 3 participants"], 970, 675, 410)
    return image


def expense_detail():
    image, draw = shell(True, "groups")
    heading(draw, "Expense details · US014–US016", "Flatmates — Dinner", "Paid by Irina · due in 3 days")
    box(draw, (270, 230, 1005, 770))
    for index, (label, value) in enumerate([("TOTAL", "AUD 60.00"), ("CATEGORY", "Food"), ("SPLIT", "Equal")]):
        x = 300 + index * 220
        box(draw, (x, 270, x + 190, 345), fill="#f7f9fc", outline="#f7f9fc", radius=9)
        txt(draw, (x + 16, 288), label, 10, MUTED, True)
        txt(draw, (x + 16, 315), value, 17, INK, True)
    txt(draw, (300, 390), "PARTICIPANTS AND SHARES", 11, BLUE_DARK, True)
    for index, (name, meta, amount, status) in enumerate([
        ("Irina", "Payer", "20.00", "Paid"),
        ("Nicolas", "Owes Irina", "20.00", "Unpaid"),
        ("Jobaida", "Owes Irina", "20.00", "Paid"),
    ]):
        y = 430 + index * 90
        box(draw, (300, y, 975, y + 72), radius=9)
        txt(draw, (325, y + 22), name, 15, INK, True)
        txt(draw, (325, y + 48), meta, 11, MUTED)
        txt(draw, (820, y + 35), "AUD " + amount, 13, INK, True, "rm")
        txt(draw, (945, y + 35), status, 11, GREEN if status == "Paid" else "#946600", True, "rm")
    box(draw, (1030, 230, 1380, 590), fill="#f5fff8")
    txt(draw, (1060, 270), "MY PAYMENT", 11, BLUE_DARK, True)
    txt(draw, (1060, 310), "AUD 20.00", 27, INK, True)
    txt(draw, (1060, 355), "PAYER PAYID", 10, MUTED, True)
    txt(draw, (1060, 385), "irina@payid.bank", 14, "#285f43")
    box(draw, (1060, 420, 1170, 458), fill="#e5f8ed", outline="#e5f8ed", radius=7)
    txt(draw, (1115, 439), "COPY PAYID", 10, GREEN, True, "mm")
    box(draw, (1060, 475, 1328, 523), fill=PURPLE, outline=PURPLE, radius=8)
    txt(draw, (1194, 499), "MARK AS PAID", 12, WHITE, True, "mm")
    demo_card(draw, "Demo payment", ["Login: nicolas@test.com", "PayID: irina@payid.bank", "Click Copy PayID"], 1030, 615, 350)
    return image


def payments():
    image, draw = shell(True, "payments")
    heading(draw, "Payment flow · US015–US017", "My payments", "View paid, unpaid, due-tomorrow, and overdue shares.")
    box(draw, (270, 230, 1005, 700))
    y = 285
    for title, meta, amount, status in [
        ("Water bill", "Flatmates · due tomorrow", "AUD 40.00", "Payment due tomorrow"),
        ("Electricity bill", "Flatmates · due 5 days ago", "AUD 40.10", "Overdue"),
        ("Internet", "Flatmates · paid", "AUD 19.75", "Paid"),
    ]:
        box(draw, (300, y, 975, y + 92), radius=10)
        txt(draw, (325, y + 25), title, 16, INK, True)
        txt(draw, (325, y + 55), meta, 12, MUTED)
        txt(draw, (950, y + 26), amount, 14, INK, True, "rm")
        txt(draw, (950, y + 57), status, 10, GREEN if status == "Paid" else RED if status == "Overdue" else "#946600", True, "rm")
        y += 108
    demo_card(draw, "Demo statuses", ["Water bill: due tomorrow", "Electricity bill: overdue", "Internet: paid"], 1030, 230, 350)
    return image


SCREENS = {
    "login.png": login(False),
    "invalid-login.png": login(True),
    "my-groups.png": groups_page(),
    "create-group.png": create_group(),
    "group-dashboard.png": group_dashboard(),
    "add-expense.png": add_expense(),
    "expense-detail.png": expense_detail(),
    "my-payments.png": payments(),
}

for filename, image in SCREENS.items():
    image.save(OUT / filename)
    print(OUT / filename)
