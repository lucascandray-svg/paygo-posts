#!/usr/bin/env python3
"""Convierte una lámina 1080x1350 en una Historia 1080x1920 (lámina centrada sobre el mismo color de fondo).

Uso:
    python3 historia.py lamina.png salida.png
"""
import sys
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
lienzo = Image.new("RGB", (1080, 1920), im.getpixel((5, 5)))
lienzo.paste(im, (0, (1920 - im.height) // 2))
lienzo.save(dst, optimize=True)
