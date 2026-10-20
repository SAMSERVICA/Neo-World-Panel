from __future__ import annotations
import re

def qr_svg(data: str) -> str | None:
    if not data or len(data) > 1200:
        return None
    try:
        import qrcode
        from qrcode.image.svg import SvgPathImage
        qr = qrcode.QRCode(box_size=1, border=1, error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(data)
        qr.make(fit=True)
        svg = qr.make_image(image_factory=SvgPathImage).to_string().decode()
        return re.sub(r'(<svg[^>]*?)\s+width="[^"]*"\s+height="[^"]*"', r'\1', svg, count=1)
    except Exception:
        return None
