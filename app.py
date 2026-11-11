"""
NextNode — Backend Flask
API REST da loja de hardware.
"""

import math
import os
import re
import sys
import time
from datetime import datetime, timezone

# Garante que o pacote `data` seja encontrado mesmo rodando de outra pasta.
# Precisa vir ANTES do import de `data.*`.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
from data.products import PRODUCTS, CATEGORIES, DEALS, FEATURED_BUILD
from data.shipping import SHIPPING_REGIONS, FREE_SHIPPING_FROM
from image_search import ImageIndex, InvalidImage

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024   # uploads de até 8 MB
CORS(app)

IMAGES_DIR = os.path.join(BASE_DIR, "static", "images")
image_index = ImageIndex(IMAGES_DIR, PRODUCTS)
PIX_DISCOUNT = 0.05        # 5% de desconto pagando no Pix
MAX_INSTALLMENTS = 10      # até 10x sem juros no cartão
EMAIL_RE = re.compile(r"^[^@\s<>\"']+@[^@\s<>\"']+\.[^@\s<>\"']+$")

PRODUCTS_BY_ID = {p["id"]: p for p in PRODUCTS}

SORTERS = {
    "price_asc":  (lambda p: p["price"], False),
    "price_desc": (lambda p: p["price"], True),
    "rating":     (lambda p: (p["rating"], p["reviews"]), True),
    "discount":   (lambda p: p["discount"], True),
}


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _money(value):
    """Arredonda para centavos."""
    return round(value + 1e-9, 2)


def _image_url(filename):
    """URL da foto do produto, ou None se ela ainda não foi adicionada.
    Sem foto, o frontend mostra uma ilustração da categoria."""
    if filename and os.path.isfile(os.path.join(IMAGES_DIR, filename)):
        return f"/static/images/{filename}"
    return None


def _illustration_url(filename):
    """URL da ilustração do produto (gerada por tools/gerar_ilustracoes.py), ou None.
    Usada quando ainda não há foto real."""
    if not filename:
        return None
    svg = os.path.splitext(filename)[0] + ".svg"
    if os.path.isfile(os.path.join(IMAGES_DIR, "ilustracoes", svg)):
        return f"/static/images/ilustracoes/{svg}"
    return None


def _payment(price):
    """Formas de pagamento calculadas a partir do preço."""
    return {
        "pix_price": _money(price * (1 - PIX_DISCOUNT)),
        "installments": {
            "count": MAX_INSTALLMENTS,
            "value": _money(price / MAX_INSTALLMENTS),
        },
    }


def _serialize(product):
    """Devolve uma cópia do produto com campos calculados."""
    p = product.copy()
    original = p.get("original_price") or p["price"]
    p["original_price"] = original
    p["discount"] = round((original - p["price"]) / original * 100) if original > p["price"] else 0
    p["image_url"] = _image_url(p.get("image"))
    p["illustration_url"] = _illustration_url(p.get("image"))
    p.update(_payment(p["price"]))
    return p


def _deal_ends_at(window_hours, now=None):
    """Fim da oferta atual.

    As ofertas renovam em janelas fixas (ex.: a cada 6h, contadas a partir
    da meia-noite UTC). Assim o horário de término é o mesmo para todo mundo
    e não volta ao início quando a página é recarregada.
    """
    window = window_hours * 3600
    now = time.time() if now is None else now
    end = (math.floor(now / window) + 1) * window
    return datetime.fromtimestamp(end, tz=timezone.utc).isoformat().replace("+00:00", "Z")


# ─── Rotas de Páginas ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ─── API de Categorias ─────────────────────────────────────────────────────────

@app.route("/api/categories")
def get_categories():
    """Retorna as categorias com a quantidade de produtos de cada uma."""
    categories = [
        {**c, "count": sum(1 for p in PRODUCTS if p["category"] == c["id"])}
        for c in CATEGORIES
    ]
    return jsonify({"categories": categories, "total": len(categories)})


# ─── API de Produtos ───────────────────────────────────────────────────────────

@app.route("/api/products")
def get_products():
    """
    Retorna lista de produtos com suporte a filtros.
    Query params:
      - category: slug da categoria (ex: gpu, cpu)
      - search: busca no nome e na marca (sem diferenciar maiúsculas)
      - featured: 'true' para só os destaques
      - min_price / max_price: faixa de preço
      - sort: price_asc | price_desc | rating | discount
      - limit: quantidade máxima de resultados
    """
    products = [_serialize(p) for p in PRODUCTS]

    category = request.args.get("category")
    if category:
        products = [p for p in products if p["category"] == category]

    search = request.args.get("search", "").strip().lower()
    if search:
        products = [p for p in products if search in f"{p['name']} {p['brand']}".lower()]

    if request.args.get("featured") == "true":
        products = [p for p in products if p.get("featured")]

    min_price = request.args.get("min_price", type=float)
    if min_price is not None:
        products = [p for p in products if p["price"] >= min_price]

    max_price = request.args.get("max_price", type=float)
    if max_price is not None:
        products = [p for p in products if p["price"] <= max_price]

    sort = request.args.get("sort")
    if sort in SORTERS:
        key, reverse = SORTERS[sort]
        products.sort(key=key, reverse=reverse)

    limit = request.args.get("limit", type=int)
    if limit:
        products = products[:limit]

    return jsonify({"products": products, "total": len(products)})


@app.route("/api/products/<int:product_id>")
def get_product(product_id):
    """Retorna um produto específico por ID."""
    product = PRODUCTS_BY_ID.get(product_id)
    if not product:
        abort(404, description=f"Produto {product_id} não encontrado.")
    return jsonify(_serialize(product))


# ─── API de Busca por Imagem ───────────────────────────────────────────────────

@app.route("/api/search/image/status")
def image_search_status():
    """Quantos produtos já têm foto em static/images (só esses entram na busca)."""
    return jsonify(image_index.status())


@app.route("/api/search/image", methods=["POST"])
def search_by_image():
    """
    Recebe uma imagem (multipart/form-data, campo `image`) e devolve os
    produtos com foto mais parecida. A imagem é processada em memória e
    não é salva no servidor.
    """
    upload = request.files.get("image")
    if not upload or not upload.filename:
        return jsonify({"error": "Envie uma imagem no campo 'image'."}), 400

    status = image_index.status()
    if status["indexed"] == 0:
        return jsonify({
            "error": "Nenhum produto tem foto cadastrada ainda, então não há com o que comparar.",
            **status,
        }), 409

    try:
        matches = image_index.search(upload.stream)
    except InvalidImage as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "results": [
            {"id": p["id"], "similarity": round(score * 100), "product": _serialize(p)}
            for p, score in matches
        ],
        "indexed": status["indexed"],
        "total_products": status["total"],
    })


# ─── API de Destaques e Build Sugerida ─────────────────────────────────────────

@app.route("/api/featured")
def get_featured():
    """Retorna os produtos em destaque (featured=True)."""
    featured = [_serialize(p) for p in PRODUCTS if p.get("featured")]
    return jsonify({"products": featured, "total": len(featured)})


@app.route("/api/builds/featured")
def get_featured_build():
    """Retorna a build sugerida, com as peças e o total."""
    parts = [_serialize(PRODUCTS_BY_ID[i]) for i in FEATURED_BUILD["product_ids"]]
    total = _money(sum(p["price"] for p in parts))
    return jsonify({
        "name": FEATURED_BUILD["name"],
        "description": FEATURED_BUILD["description"],
        "products": parts,
        "total": total,
        **_payment(total),
    })


# ─── API de Ofertas ────────────────────────────────────────────────────────────

@app.route("/api/deals")
def get_deals():
    """
    Retorna as ofertas relâmpago: desconto extra sobre o preço atual
    e o horário (UTC) em que a oferta termina.
    """
    deals_response = []
    for deal in DEALS:
        product = PRODUCTS_BY_ID.get(deal["product_id"])
        if not product:
            continue
        p = _serialize(product)
        deal_price = _money(p["price"] * (1 - deal["extra_discount"] / 100))
        total_discount = round((p["original_price"] - deal_price) / p["original_price"] * 100)
        deals_response.append({
            **deal,
            "product": p,
            "deal_price": deal_price,
            "total_discount": total_discount,
            "ends_at": _deal_ends_at(deal["window_hours"]),
            **_payment(deal_price),
        })
    return jsonify({"deals": deals_response, "total": len(deals_response)})


# ─── API de Frete (simulado) ───────────────────────────────────────────────────

@app.route("/api/shipping", methods=["POST"])
def shipping():
    """Calcula o frete a partir do CEP e do subtotal do carrinho (simulação)."""
    data = request.get_json(silent=True) or {}
    cep = re.sub(r"\D", "", str(data.get("cep") or ""))
    if len(cep) != 8:
        return jsonify({"error": "CEP inválido. Digite os 8 números."}), 400

    try:
        subtotal = max(0.0, float(data.get("subtotal") or 0))
    except (TypeError, ValueError):
        subtotal = 0.0

    region = SHIPPING_REGIONS[int(cep[0])]
    free = subtotal >= FREE_SHIPPING_FROM
    options = [
        {
            "id": "economico",
            "name": "Econômico",
            "price": 0.0 if free else region["price"],
            "days": region["days"],
        },
        {
            "id": "expresso",
            "name": "Expresso",
            "price": _money(region["price"] * 1.8),
            "days": max(1, region["days"] // 2),
        },
    ]
    return jsonify({
        "cep": f"{cep[:5]}-{cep[5:]}",
        "region": region["name"],
        "free_shipping": free,
        "free_shipping_from": FREE_SHIPPING_FROM,
        "options": options,
        "simulated": True,
    })


# ─── API de Newsletter ─────────────────────────────────────────────────────────

@app.route("/api/newsletter", methods=["POST"])
def newsletter():
    """Registra e-mail na newsletter (simulado)."""
    data = request.get_json(silent=True) or {}
    email = str(data.get("email") or "").strip()
    if not EMAIL_RE.match(email):
        return jsonify({"success": False, "message": "E-mail inválido."}), 400
    return jsonify({
        "success": True,
        "message": f"Pronto! {email} vai receber as próximas ofertas.",
    })


# ─── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": e.description}), 404


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Arquivo grande demais. O limite é 8 MB."}), 413


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Erro interno do servidor."}), 500


# ─── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Servidor de desenvolvimento: só escuta na própria máquina (127.0.0.1).
    # O modo debug expõe um console Python no navegador, então nunca deve
    # ficar aberto para a rede. Para desligar: FLASK_DEBUG=0
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug, host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
