"""Reusable LinkedIn carousel PDF generator — clean white style."""

from fpdf import FPDF
from PIL import Image

# Constants
W, H = 1080, 1080
MARGIN = 80
CONTENT_W = W - 2 * MARGIN

# Colors — clean white background
BG = (255, 255, 255)
BG_ALT = (245, 247, 250)
ACCENT = (42, 157, 143)         # teal
TEXT = (15, 23, 42)             # near-black
TEXT_LIGHT = (100, 116, 139)    # slate-500
ORANGE = (231, 111, 81)
TABLE_HD = (30, 41, 59)        # dark header
WHITE = (255, 255, 255)


class CarouselPDF(FPDF):
    def __init__(self):
        super().__init__(unit="pt", format=(W, H))
        self.set_auto_page_break(auto=False)
        self.add_font("Inter", "", "/System/Library/Fonts/Helvetica.ttc")
        self.add_font("Inter", "B", "/System/Library/Fonts/HelveticaNeue.ttc")

    def bg(self):
        self.set_fill_color(*BG)
        self.rect(0, 0, W, H, "F")

    def title_text(self, y, text, size=52, color=TEXT):
        self.set_font("Inter", "B", size)
        self.set_text_color(*color)
        self.set_xy(MARGIN, y)
        self.multi_cell(CONTENT_W, size * 1.3, text, align="L")
        return self.get_y()

    def body_text(self, y, text, size=32, color=TEXT_LIGHT):
        self.set_font("Inter", "", size)
        self.set_text_color(*color)
        self.set_xy(MARGIN, y)
        self.multi_cell(CONTENT_W, size * 1.5, text, align="L")
        return self.get_y()

    def accent_line(self, y, width=120):
        self.set_fill_color(*ACCENT)
        self.rect(MARGIN, y, width, 4, "F")
        return y + 25

    def tag(self, y, text):
        self.set_font("Inter", "B", 24)
        self.set_text_color(*ACCENT)
        self.set_xy(MARGIN, y)
        self.cell(0, 30, text.upper())
        return y + 40

    def footer_text(self, text="Dquan's LLM Notes"):
        self.set_font("Inter", "", 20)
        self.set_text_color(*TEXT_LIGHT)
        self.set_xy(MARGIN, H - 80)
        self.cell(CONTENT_W, 24, text, align="L")

    def table(self, y, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [CONTENT_W / len(headers)] * len(headers)
        row_h = 44

        # Header
        self.set_font("Inter", "B", 21)
        self.set_fill_color(*TABLE_HD)
        self.set_text_color(*WHITE)
        x = MARGIN
        for i, h in enumerate(headers):
            self.set_xy(x, y)
            self.cell(col_widths[i], row_h, h, border=0, fill=True, align="C")
            x += col_widths[i]
        y += row_h

        # Rows
        self.set_font("Inter", "", 20)
        for ri, row in enumerate(rows):
            bg_color = BG_ALT if ri % 2 == 0 else BG
            self.set_fill_color(*bg_color)
            self.set_text_color(*TEXT)
            x = MARGIN
            for i, cell in enumerate(row):
                self.set_xy(x, y)
                self.cell(col_widths[i], row_h, str(cell), border=0, fill=True, align="C")
                x += col_widths[i]
            y += row_h
        return y

    def bullet(self, y, text, size=30):
        self.set_font("Inter", "B", size)
        self.set_text_color(*ACCENT)
        self.set_xy(MARGIN, y)
        self.cell(30, size * 1.5, ">")
        self.set_font("Inter", "", size)
        self.set_text_color(*TEXT)
        self.set_xy(MARGIN + 35, y)
        self.multi_cell(CONTENT_W - 35, size * 1.5, text, align="L")
        return self.get_y() + 5

    def stat_box(self, y, label, value, color=ACCENT):
        box_w = CONTENT_W
        box_h = 100
        self.set_fill_color(*color)
        self.rect(MARGIN, y, box_w, box_h, "F")
        self.set_font("Inter", "B", 48)
        self.set_text_color(*WHITE)
        self.set_xy(MARGIN + 20, y + 10)
        self.cell(box_w - 40, 50, value, align="L")
        self.set_font("Inter", "", 24)
        self.set_xy(MARGIN + 20, y + 55)
        self.cell(box_w - 40, 30, label, align="L")
        return y + box_h + 20

    def add_image_centered(self, y, img_path, max_w=None, max_h=None):
        if max_w is None:
            max_w = CONTENT_W
        if max_h is None:
            max_h = 400
        img = Image.open(img_path)
        iw, ih = img.size
        ratio = min(max_w / iw, max_h / ih)
        draw_w = iw * ratio
        draw_h = ih * ratio
        x = MARGIN + (CONTENT_W - draw_w) / 2
        self.image(img_path, x, y, draw_w, draw_h)
        return y + draw_h + 20

    def slide_start(self):
        """Start a new slide with white background."""
        self.add_page()
        self.bg()
