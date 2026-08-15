"""Geração de QR Code para a lista pública / comprovante individual."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import qrcode
from PIL import Image, ImageDraw, ImageFont


def make_qr_image(url: str, *, title: str = "Sinapesc — Lista REAP") -> Image.Image:
    qr = qrcode.QRCode(version=None, box_size=8, border=2, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#1A3358", back_color="white").convert("RGB")

    # Cartaz imprimível: título + QR + URL
    pad = 40
    title_h = 70
    url_h = 50
    width = max(qr_img.width + pad * 2, 480)
    height = title_h + qr_img.height + url_h + pad * 2
    poster = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(poster)

    try:
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_url = ImageFont.truetype("arial.ttf", 12)
    except OSError:
        font_title = ImageFont.load_default()
        font_url = ImageFont.load_default()

    draw.text((pad, pad), title, fill="#1A3358", font=font_title)
    draw.text((pad, pad + 28), "Aponte a câmera para ver os REAPs atualizados", fill="#5A6B7A", font=font_url)

    x = (width - qr_img.width) // 2
    y = title_h + pad
    poster.paste(qr_img, (x, y))

    # URL truncada se longa
    url_show = url if len(url) < 70 else url[:67] + "..."
    draw.text((pad, y + qr_img.height + 16), url_show, fill="#1F8A7A", font=font_url)
    return poster


def save_qr_png(url: str, path: str | Path, *, title: str = "Sinapesc — Lista REAP") -> Path:
    out = Path(path)
    img = make_qr_image(url, title=title)
    img.save(out, format="PNG")
    return out


def pil_to_tk(img: Image.Image, max_size: Tuple[int, int] = (280, 280)):
    """Converte PIL → PhotoImage (requer ImageTk)."""
    from PIL import ImageTk

    copy = img.copy()
    copy.thumbnail(max_size)
    return ImageTk.PhotoImage(copy)
