from io import BytesIO
from typing import Any, cast

from aiogram.types import BufferedInputFile
from PIL import Image
from qrcode import ERROR_CORRECT_H, QRCode  # type: ignore[attr-defined]

from src.core.constants import ASSETS_DIR


class QrCodeService:
    def create(self, data: str, filename: str = "qr_code.png") -> BufferedInputFile:
        qr: Any = QRCode(
            version=1,
            error_correction=ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        qr_img_raw = qr.make_image(fill_color="black", back_color="white")
        if hasattr(qr_img_raw, "get_image"):
            qr_img = cast(Image.Image, qr_img_raw.get_image())
        else:
            qr_img = cast(Image.Image, qr_img_raw)
        qr_img = qr_img.convert("RGB")

        logo_path = ASSETS_DIR / "logo.png"
        if logo_path.exists():
            logo = Image.open(logo_path).convert("RGBA")
            qr_width, qr_height = qr_img.size
            logo_size = int(qr_width * 0.2)
            logo = logo.resize((logo_size, logo_size), resample=Image.Resampling.LANCZOS)
            pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
            qr_img.paste(logo, pos, mask=logo)

        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        return BufferedInputFile(file=buffer.getvalue(), filename=filename)
