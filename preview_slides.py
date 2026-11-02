"""Rough PNG preview of the generated pptx, for layout checking without PowerPoint.

Not a faithful renderer: it draws filled shapes, images and wrapped text with
approximate metrics. Enough to catch overflow and overlap.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER
from pptx.enum.text import PP_ALIGN

PRS = Presentation("content/gaapo_outputs_v2/GAAPO_case_study_slides.pptx")
OUT = Path("/tmp/slide_preview")
OUT.mkdir(exist_ok=True)
S = 120  # px per inch

REG = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
ITAL = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"


def font(size_pt, bold=False, italic=False):
    path = BOLD if bold else (ITAL if italic else REG)
    return ImageFont.truetype(path, max(6, int(size_pt / 72 * S)))


def colour(fill, default=None):
    try:
        rgb = fill.fore_color.rgb
        return (rgb[0], rgb[1], rgb[2])
    except Exception:
        return default


for n, slide in enumerate(PRS.slides, 1):
    img = Image.new("RGB", (int(13.333 * S), int(7.5 * S)), "white")
    d = ImageDraw.Draw(img)
    try:
        bg = slide.background.fill
        img.paste(Image.new("RGB", img.size, colour(bg, (255, 255, 255))), (0, 0))
    except Exception:
        pass

    for sh in slide.shapes:
        x, y = sh.left / 914400 * S, sh.top / 914400 * S
        w, h = sh.width / 914400 * S, sh.height / 914400 * S

        if sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
            pic = Image.open(sh.image.blob and __import__("io").BytesIO(sh.image.blob))
            pic = pic.convert("RGB").resize((int(w), int(h)), Image.LANCZOS)
            img.paste(pic, (int(x), int(y)))
            continue

        if sh.shape_type == MSO_SHAPE_TYPE.TABLE:
            tw, th = w / len(sh.table.columns), h / len(sh.table.rows)
            for r, row in enumerate(sh.table.rows):
                for c, cell in enumerate(row.cells):
                    cx, cy = x + c * tw, y + r * th
                    fill = colour(cell.fill, (255, 255, 255))
                    d.rectangle([cx, cy, cx + tw, cy + th], fill=fill,
                                outline=(210, 215, 222))
                    txt = cell.text_frame.text
                    size = cell.text_frame.paragraphs[0].runs[0].font.size.pt
                    bold = bool(cell.text_frame.paragraphs[0].runs[0].font.bold)
                    fcol = (255, 255, 255) if r == 0 else (27, 39, 51)
                    tw_txt = d.textlength(txt, font=font(size, bold))
                    d.text((cx + (tw - tw_txt) / 2, cy + th / 2 - size * S / 150),
                           txt, font=font(size, bold), fill=fcol)
            continue

        # filled autoshapes (cards, bars)
        if sh.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
            fill = colour(sh.fill, None)
            if fill and fill != (255, 255, 255):
                d.rectangle([x, y, x + w, y + h], fill=fill)

        if not sh.has_text_frame or not sh.text_frame.text.strip():
            continue

        cy = y
        for p in sh.text_frame.paragraphs:
            run = p.runs[0] if p.runs else None
            if run is None:
                cy += 8
                continue
            size = run.font.size.pt if run.font.size else 18
            bold = bool(run.font.bold)
            ital = bool(run.font.italic)
            fcol = (run.font.color.rgb[0], run.font.color.rgb[1], run.font.color.rgb[2]) \
                if run.font.color and run.font.color.rgb else (27, 39, 51)
            f = font(size, bold, ital)
            line_h = size / 72 * S * 1.25
            words = p.text.split(" ")
            line = ""
            for word in words:
                trial = (line + " " + word).strip()
                if d.textlength(trial, font=f) > w and line:
                    d.text((x, cy), line, font=f, fill=fcol)
                    cy += line_h
                    line = word
                else:
                    line = trial
            if line:
                d.text((x, cy), line, font=f, fill=fcol)
                cy += line_h
            cy += size / 72 * S * 0.35

    img.save(OUT / f"slide{n:02d}.png")
print("wrote", len(PRS.slides), "previews to", OUT)
