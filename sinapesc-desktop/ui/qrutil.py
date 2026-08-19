"""QR Code com padrão visual único Sinapesc (estável + imprimível)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import qrcode
from PIL import Image, ImageDraw, ImageFont
from qrcode.constants import ERROR_CORRECT_H

from ui.theme import ORG_SHORT


def make_qr_image(
    url: str,
    *,
    title: str = "Sinapesc — REAP",
    subtitle: str = "Aponte a câmera · link permanente do sindicato",
) -> Image.Image:
    """
    Padrão visual único:
    - cores institucionais
    - moldura dourada
    - selo central SINAPESC
    O conteúdo (URL) deve ser estável para o QR impresso não mudar.
    """
    qr = qrcode.QRCode(
        version=None,
        box_size=10,
        border=2,
        error_correction=ERROR_CORRECT_H,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0A2F52", back_color="white").convert("RGB")

    # Selo central (logo SINAPESC — correção H aguenta o recorte)
    seal_size = max(48, qr_img.width // 5)
    seal = Image.new("RGB", (seal_size, seal_size), "white")
    try:
        from ui.brand import asset_path

        logo_path = asset_path("logo.png")
        if logo_path.exists():
            logo = Image.open(logo_path).convert("RGBA")
            inner = max(24, seal_size - 6)
            logo.thumbnail((inner, inner), Image.Resampling.LANCZOS)
            x = (seal_size - logo.width) // 2
            y = (seal_size - logo.height) // 2
            seal.paste(logo, (x, y), logo)
        else:
            raise FileNotFoundError(logo_path)
    except Exception:
        draw_seal = ImageDraw.Draw(seal)
        margin = 4
        draw_seal.rectangle(
            [margin, margin, seal_size - margin - 1, seal_size - margin - 1],
            outline="#C4A35A",
            width=3,
        )
        try:
            font_seal = ImageFont.truetype("arial.ttf", max(9, seal_size // 6))
        except OSError:
            font_seal = ImageFont.load_default()
        bbox = draw_seal.textbbox((0, 0), "S", font=font_seal)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw_seal.text(((seal_size - tw) / 2, (seal_size - th) / 2 - 2), "S", fill="#0A2F52", font=font_seal)

    pos = ((qr_img.width - seal_size) // 2, (qr_img.height - seal_size) // 2)
    qr_img.paste(seal, pos)

    pad = 36
    title_h = 72
    width = max(qr_img.width + pad * 2, 520)
    height = title_h + qr_img.height + pad * 2 + 20
    poster = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(poster)

    # Moldura dourada (padrão institucional)
    draw.rectangle([8, 8, width - 9, height - 9], outline="#C4A35A", width=3)
    draw.rectangle([14, 14, width - 15, height - 15], outline="#0A2F52", width=1)

    try:
        font_title = ImageFont.truetype("arialbd.ttf", 20)
        font_sub = ImageFont.truetype("arial.ttf", 11)
    except OSError:
        try:
            font_title = ImageFont.truetype("arial.ttf", 20)
            font_sub = ImageFont.truetype("arial.ttf", 11)
        except OSError:
            font_title = ImageFont.load_default()
            font_sub = font_title

    draw.text((pad, pad - 4), title, fill="#0A2F52", font=font_title)
    draw.text((pad, pad + 26), subtitle, fill="#5A7388", font=font_sub)
    draw.text((pad, pad + 44), ORG_SHORT.upper(), fill="#C4A35A", font=font_sub)

    x = (width - qr_img.width) // 2
    y = title_h + pad - 8
    poster.paste(qr_img, (x, y))
    return poster


def save_qr_png(url: str, path: str | Path, *, title: str = "Sinapesc — REAP", subtitle: str = "") -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img = make_qr_image(url, title=title, subtitle=subtitle or "Aponte a câmera · link permanente")
    img.save(out, format="PNG")
    return out


def pil_to_tk(img: Image.Image, max_size: Tuple[int, int] = (280, 280)):
    from PIL import ImageTk

    copy = img.copy()
    copy.thumbnail(max_size)
    return ImageTk.PhotoImage(copy)
