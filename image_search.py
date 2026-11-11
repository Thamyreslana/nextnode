"""
NextNode — Busca por imagem (comparação local, sem IA externa)

Como funciona
-------------
1. Preparação: corrige a rotação da foto (EXIF), troca transparência por
   fundo branco e corta as bordas lisas, para o produto ocupar a imagem toda.
2. "Impressões digitais" de cada imagem:
   - Estrutura (dHash): reduz a imagem para 17×16 em tons de cinza e anota,
     pixel a pixel, se ele é mais claro que o vizinho da direita. Isso gera
     256 bits que descrevem o desenho de claro/escuro do objeto e não mudam
     com tamanho, compressão ou brilho.
   - Cor: um histograma que conta quanto da imagem tem cada faixa de cor.
3. Comparação: a imagem enviada é comparada com as fotos do catálogo
   (static/images) e os produtos mais parecidos são devolvidos com uma nota.

Limitação
---------
O algoritmo compara APARÊNCIA, não "entende" o que é o objeto. Ele acerta
quando a foto enviada é parecida com a foto do catálogo (mesmo produto,
ângulo e fundo próximos). Foto da caixa ou da peça montada no PC tende a falhar.
"""

import os
import threading
from dataclasses import dataclass

from PIL import Image, ImageChops, ImageOps, UnidentifiedImageError

HASH_SIZE = 16                      # dHash de 16×16 = 256 bits
HASH_BITS = HASH_SIZE * HASH_SIZE
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "GIF", "BMP"}
MAX_PIXELS = 40_000_000             # protege contra imagens gigantes ("decompression bomb")

# Peso de cada impressão digital na nota final (somam 1)
STRUCTURE_WEIGHT = 0.6
COLOR_WEIGHT = 0.4

# Nota mínima (0 a 1) para um produto aparecer como "parecido".
# Calibrada com 288 testes em imagens sintéticas: com 0.60 o produto certo
# aparece em 96% dos casos. Se, com as suas fotos reais, aparecer muito
# resultado errado, aumente. Se a busca não achar o que deveria, diminua.
MIN_SCORE = 0.60


class InvalidImage(ValueError):
    """O arquivo enviado não é uma imagem que conseguimos usar."""


@dataclass(frozen=True)
class Fingerprint:
    dhash: int
    dhash_mirror: int     # versão espelhada: acha a foto mesmo se estiver invertida
    histogram: tuple


# ─── Leitura e preparação ──────────────────────────────────────────────────────

def open_image(source):
    """Abre e valida uma imagem a partir de um caminho ou de um arquivo enviado."""
    try:
        img = Image.open(source)
    except (UnidentifiedImageError, OSError):
        raise InvalidImage("Não consegui abrir esse arquivo como imagem.")

    if img.format not in ALLOWED_FORMATS:
        raise InvalidImage("Formato não suportado. Use JPG, PNG ou WEBP.")

    width, height = img.size
    if width * height > MAX_PIXELS:
        raise InvalidImage("Imagem com resolução grande demais.")

    try:
        img.load()
    except (OSError, Image.DecompressionBombError):
        raise InvalidImage("O arquivo de imagem está corrompido ou incompleto.")
    return img


def normalize(img):
    """Deixa a imagem num formato padrão antes de comparar."""
    img = ImageOps.exif_transpose(img)  # foto de celular "deitada"

    if img.mode in ("RGBA", "LA", "PA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        background.alpha_composite(rgba)
        img = background

    img = img.convert("RGB")
    img.thumbnail((512, 512))  # imagens menores = comparação mais rápida
    return _trim_background(img)


def _trim_background(img, tolerance=28):
    """Corta as bordas que têm a mesma cor do canto (fundo liso)."""
    background = Image.new("RGB", img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, background).convert("L")
    mask = diff.point(lambda v: 255 if v > tolerance else 0)
    box = mask.getbbox()
    if not box:
        return img

    # Só corta se sobrar uma área razoável (evita cortar demais por causa de ruído)
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    if box_area < 0.05 * img.width * img.height:
        return img
    return img.crop(box)


# ─── Impressões digitais ───────────────────────────────────────────────────────

def _dhash(img):
    gray = img.convert("L").resize((HASH_SIZE + 1, HASH_SIZE), Image.Resampling.LANCZOS)
    px = gray.tobytes()
    row = HASH_SIZE + 1
    bits = 0
    for y in range(HASH_SIZE):
        for x in range(HASH_SIZE):
            left = px[y * row + x]
            right = px[y * row + x + 1]
            bits = (bits << 1) | (1 if left > right else 0)
    return bits


def _color_histogram(img):
    """36 faixas: 8 matizes × 2 saturações × 2 brilhos + 4 tons de cinza."""
    hsv = img.resize((64, 64)).convert("HSV").tobytes()
    bins = [0] * 36
    for i in range(0, len(hsv), 3):
        h, s, v = hsv[i], hsv[i + 1], hsv[i + 2]
        if s < 50 or v < 40:
            # Pouca saturação ou muito escuro: a matiz não importa, conta como cinza
            bins[32 + min(3, v // 64)] += 1
        else:
            bins[(h * 8 // 256) * 4 + (s >= 150) * 2 + (v >= 150)] += 1
    total = sum(bins) or 1
    return tuple(b / total for b in bins)


def fingerprint(img):
    return Fingerprint(
        dhash=_dhash(img),
        dhash_mirror=_dhash(ImageOps.mirror(img)),
        histogram=_color_histogram(img),
    )


def similarity(query, item):
    """Nota de 0 a 1 entre duas impressões digitais."""
    distance = min(
        bin(query.dhash ^ item.dhash).count("1"),
        bin(query.dhash_mirror ^ item.dhash).count("1"),
    )
    # Duas imagens sem relação nenhuma coincidem em ~50% dos bits por acaso,
    # então 50% vira nota 0 e 100% vira nota 1.
    structure = max(0.0, (1 - distance / HASH_BITS - 0.5) / 0.5)

    # Interseção de histogramas: quanto da distribuição de cores as duas têm em comum
    color = sum(min(a, b) for a, b in zip(query.histogram, item.histogram))

    return STRUCTURE_WEIGHT * structure + COLOR_WEIGHT * color


# ─── Índice do catálogo ────────────────────────────────────────────────────────

class ImageIndex:
    """Guarda as impressões digitais das fotos do catálogo.

    O índice é recalculado sozinho quando uma foto é adicionada, trocada
    ou removida de static/images (comparando a data de modificação).
    """

    def __init__(self, images_dir, products):
        self.images_dir = images_dir
        self.products = products
        self._entries = []          # [(produto, Fingerprint)]
        self._invalid = []          # arquivos que existem mas não abriram
        self._signature = None
        self._lock = threading.Lock()

    def _photo_path(self, product):
        name = product.get("image")
        return os.path.join(self.images_dir, name) if name else None

    def _current_signature(self):
        signature = []
        for p in self.products:
            path = self._photo_path(p)
            if path and os.path.isfile(path):
                signature.append((p["id"], os.path.getmtime(path)))
        return tuple(signature)

    def refresh(self):
        signature = self._current_signature()
        if signature == self._signature:
            return
        with self._lock:
            if signature == self._signature:
                return
            by_id = {p["id"]: p for p in self.products}
            entries, invalid = [], []
            for product_id, _ in signature:
                product = by_id[product_id]
                try:
                    with open(self._photo_path(product), "rb") as f:
                        entries.append((product, fingerprint(normalize(open_image(f)))))
                except (InvalidImage, OSError):
                    invalid.append(product["image"])
            self._entries, self._invalid, self._signature = entries, invalid, signature

    def status(self):
        self.refresh()
        indexed = {p["id"] for p, _ in self._entries}
        return {
            "indexed": len(indexed),
            "total": len(self.products),
            "missing": [p["image"] for p in self.products if p["id"] not in indexed and p["image"] not in self._invalid],
            "invalid": list(self._invalid),
        }

    def search(self, source, limit=6, min_score=MIN_SCORE):
        """Devolve [(produto, nota)] dos produtos mais parecidos com a imagem."""
        self.refresh()
        query = fingerprint(normalize(open_image(source)))
        scored = [(product, similarity(query, fp)) for product, fp in self._entries]
        scored.sort(key=lambda item: item[1], reverse=True)
        return [(p, s) for p, s in scored if s >= min_score][:limit]
