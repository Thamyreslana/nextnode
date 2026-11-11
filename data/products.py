"""
NextNode - Dados de Produtos e Categorias
Catálogo fictício usado no projeto de estudo (preços e estoque não são reais).

Campos de cada produto:
- price            preço atual (à vista no cartão)
- original_price   só existe quando o produto está com desconto
- badge            selo de destaque; use com parcimônia (poucos produtos)
- compat           dados usados pelo montador de PC para checar compatibilidade:
    cpu         -> socket, power (consumo máximo em W)
    motherboard -> socket, memory (DDR4/DDR5)
    ram         -> memory
    gpu         -> power
    cooler      -> max_tdp (quanto calor o cooler dá conta, em W)
    psu         -> watts
"""

CATEGORIES = [
    {"id": "gpu",         "name": "Placas de Vídeo", "short": "GPU",       "description": "Processamento gráfico para jogos e criação"},
    {"id": "cpu",         "name": "Processadores",   "short": "CPU",       "description": "AMD AM5 e Intel LGA 1700"},
    {"id": "motherboard", "name": "Placas-mãe",      "short": "Placa-mãe", "description": "Define soquete e tipo de memória"},
    {"id": "ram",         "name": "Memórias RAM",    "short": "RAM",       "description": "Kits DDR4 e DDR5"},
    {"id": "ssd",         "name": "Armazenamento",   "short": "SSD",       "description": "SSDs NVMe PCIe 4.0"},
    {"id": "cooler",      "name": "Refrigeração",    "short": "Cooler",    "description": "Air coolers e water coolers"},
    {"id": "psu",         "name": "Fontes",          "short": "Fonte",     "description": "Certificadas 80 Plus"},
    {"id": "case",        "name": "Gabinetes",       "short": "Gabinete",  "description": "Mid e full tower"},
]

PRODUCTS = [
    # ─── GPU ───────────────────────────────────────────────────────────────
    {
        "id": 1, "name": "ASUS ROG Astral GeForce RTX 5090", "brand": "ASUS", "category": "gpu",
        "price": 18999.99, "rating": 4.9, "reviews": 342, "stock": 8,
        "badge": "LANÇAMENTO", "featured": True, "image": "gpu_rog_astral_5090.jpg",
        "specs": {"VRAM": "32GB GDDR7", "Consumo": "575W", "Barramento": "PCIe 5.0"},
        "compat": {"power": 575},
        "description": "RTX 5090 com o cooler de quatro ventoinhas da linha ROG Astral. Pensada para 4K com ray tracing e para IA local. Exige fonte de 1000W ou mais.",
    },
    {
        "id": 2, "name": "AMD Radeon RX 9070 XT", "brand": "AMD", "category": "gpu",
        "price": 4299.99, "original_price": 4999.99, "rating": 4.7, "reviews": 218, "stock": 23,
        "badge": "MAIS VENDIDO", "featured": True, "image": "gpu_rx9070xt.jpg",
        "specs": {"VRAM": "16GB GDDR6", "Consumo": "304W", "Barramento": "PCIe 5.0"},
        "compat": {"power": 304},
        "description": "A escolha mais equilibrada para jogar em 1440p no alto. 16GB de VRAM dão folga para os próximos anos.",
    },
    {
        "id": 3, "name": "ASUS ROG Strix GeForce RTX 5070 Ti", "brand": "ASUS", "category": "gpu",
        "price": 8499.99, "original_price": 9299.99, "rating": 4.8, "reviews": 156, "stock": 15,
        "badge": None, "featured": False, "image": "gpu_rog_strix_5070ti.jpg",
        "specs": {"VRAM": "16GB GDDR7", "Consumo": "300W", "Barramento": "PCIe 5.0"},
        "compat": {"power": 300},
        "description": "Boa para 1440p e 4K com DLSS 4. Consumo parecido com a RX 9070 XT.",
    },
    {
        "id": 4, "name": "Intel Arc B580", "brand": "Intel", "category": "gpu",
        "price": 1799.99, "rating": 4.4, "reviews": 87, "stock": 41,
        "badge": None, "featured": False, "image": "gpu_arcb580.jpg",
        "specs": {"VRAM": "12GB GDDR6", "Consumo": "190W", "Barramento": "PCIe 4.0"},
        "compat": {"power": 190},
        "description": "Porta de entrada para 1080p. Tem 12GB de VRAM, mais do que outras placas da mesma faixa de preço.",
    },

    # ─── CPU ───────────────────────────────────────────────────────────────
    {
        "id": 5, "name": "AMD Ryzen 9 9950X", "brand": "AMD", "category": "cpu",
        "price": 3799.99, "rating": 4.9, "reviews": 201, "stock": 19,
        "badge": None, "featured": True, "image": "cpu_r99950x.jpg",
        "specs": {"Núcleos": "16C/32T", "Clock": "4.3 ~ 5.7 GHz", "Soquete": "AM5"},
        "compat": {"socket": "AM5", "power": 230},
        "description": "16 núcleos Zen 5. Mais indicado para quem edita vídeo, compila código ou faz streaming enquanto joga.",
    },
    {
        "id": 6, "name": "Intel Core i9-14900K", "brand": "Intel", "category": "cpu",
        "price": 2999.99, "original_price": 3499.99, "rating": 4.7, "reviews": 335, "stock": 27,
        "badge": None, "featured": False, "image": "cpu_i914900k.jpg",
        "specs": {"Núcleos": "24C/32T", "Clock": "3.2 ~ 6.0 GHz", "Soquete": "LGA 1700"},
        "compat": {"socket": "LGA 1700", "power": 253},
        "description": "Muito rápido em jogos e multitarefa, mas esquenta: peça um water cooler de 360mm.",
    },
    {
        "id": 7, "name": "AMD Ryzen 7 9700X", "brand": "AMD", "category": "cpu",
        "price": 1999.99, "rating": 4.8, "reviews": 178, "stock": 34,
        "badge": "CUSTO-BENEFÍCIO", "featured": False, "image": "cpu_r79700x.jpg",
        "specs": {"Núcleos": "8C/16T", "Clock": "3.8 ~ 5.5 GHz", "Soquete": "AM5"},
        "compat": {"socket": "AM5", "power": 88},
        "description": "8 núcleos com consumo baixo (65W). Esquenta pouco e roda bem com air cooler.",
    },
    {
        "id": 8, "name": "Intel Core i7-14700K", "brand": "Intel", "category": "cpu",
        "price": 2199.99, "original_price": 2599.99, "rating": 4.6, "reviews": 244, "stock": 22,
        "badge": None, "featured": False, "image": "cpu_i714700k.jpg",
        "specs": {"Núcleos": "20C/28T", "Clock": "3.4 ~ 5.6 GHz", "Soquete": "LGA 1700"},
        "compat": {"socket": "LGA 1700", "power": 253},
        "description": "Quase o desempenho do i9 por bem menos. Combina com placas-mãe Z790.",
    },

    # ─── RAM ───────────────────────────────────────────────────────────────
    {
        "id": 9, "name": "Corsair Dominator Titanium DDR5 32GB", "brand": "Corsair", "category": "ram",
        "price": 899.99, "original_price": 1099.99, "rating": 4.8, "reviews": 143, "stock": 56,
        "badge": None, "featured": False, "image": "ram_ddr5_32gb.jpg",
        "specs": {"Capacidade": "2×16GB", "Velocidade": "6400MHz", "Latência": "CL32"},
        "compat": {"memory": "DDR5"},
        "description": "Kit DDR5 rápido, com dissipador de alumínio e RGB.",
    },
    {
        "id": 10, "name": "Kingston FURY Beast DDR5 64GB", "brand": "Kingston", "category": "ram",
        "price": 1399.99, "rating": 4.7, "reviews": 89, "stock": 31,
        "badge": None, "featured": False, "image": "ram_fury_beast_ddr5_64gb.jpg",
        "specs": {"Capacidade": "2×32GB", "Velocidade": "6000MHz", "Latência": "CL30"},
        "compat": {"memory": "DDR5"},
        "description": "64GB com perfil EXPO para Ryzen. Indicado para edição de vídeo e máquinas virtuais.",
    },
    {
        "id": 11, "name": "Kingston Fury Beast DDR4 32GB", "brand": "Kingston", "category": "ram",
        "price": 399.99, "original_price": 499.99, "rating": 4.6, "reviews": 312, "stock": 78,
        "badge": None, "featured": False, "image": "ram_ddr4_32gb.jpg",
        "specs": {"Capacidade": "2×16GB", "Velocidade": "3600MHz", "Latência": "CL18"},
        "compat": {"memory": "DDR4"},
        "description": "DDR4 para quem está fazendo upgrade de uma plataforma mais antiga. Não encaixa em placas DDR5.",
    },
    {
        "id": 12, "name": "Corsair Vengeance DDR5 48GB", "brand": "Corsair", "category": "ram",
        "price": 699.99, "rating": 4.5, "reviews": 67, "stock": 45,
        "badge": None, "featured": False, "image": "ram_ddr5_48gb.jpg",
        "specs": {"Capacidade": "2×24GB", "Velocidade": "5600MHz", "Latência": "CL40"},
        "compat": {"memory": "DDR5"},
        "description": "48GB DDR5 sem pagar o preço de um kit de 64GB.",
    },

    # ─── SSD ───────────────────────────────────────────────────────────────
    {
        "id": 13, "name": "Samsung 990 Pro NVMe 2TB", "brand": "Samsung", "category": "ssd",
        "price": 799.99, "original_price": 999.99, "rating": 4.9, "reviews": 528, "stock": 63,
        "badge": "MAIS VENDIDO", "featured": True, "image": "ssd_990pro.jpg",
        "specs": {"Capacidade": "2TB", "Leitura": "7450 MB/s", "Escrita": "6900 MB/s"},
        "compat": {},
        "description": "Um dos SSDs PCIe 4.0 mais rápidos. 2TB comportam o sistema e uma boa biblioteca de jogos.",
    },
    {
        "id": 14, "name": "WD Black SN850X NVMe 2TB", "brand": "WD", "category": "ssd",
        "price": 749.99, "rating": 4.8, "reviews": 341, "stock": 47,
        "badge": None, "featured": False, "image": "ssd_sn850x.jpg",
        "specs": {"Capacidade": "2TB", "Leitura": "7300 MB/s", "Escrita": "6600 MB/s"},
        "compat": {},
        "description": "Desempenho muito próximo do 990 Pro, normalmente um pouco mais barato.",
    },
    {
        "id": 15, "name": "Seagate FireCuda 530 NVMe 4TB", "brand": "Seagate", "category": "ssd",
        "price": 1299.99, "rating": 4.7, "reviews": 112, "stock": 28,
        "badge": None, "featured": False, "image": "ssd_firecuda.jpg",
        "specs": {"Capacidade": "4TB", "Leitura": "7300 MB/s", "Escrita": "6900 MB/s"},
        "compat": {},
        "description": "4TB para quem não quer ficar desinstalando jogo para liberar espaço.",
    },
    {
        "id": 16, "name": "Kingston Fury Renegade NVMe 1TB", "brand": "Kingston", "category": "ssd",
        "price": 349.99, "original_price": 429.99, "rating": 4.6, "reviews": 198, "stock": 92,
        "badge": None, "featured": False, "image": "ssd_renegade.jpg",
        "specs": {"Capacidade": "1TB", "Leitura": "7300 MB/s", "Escrita": "6000 MB/s"},
        "compat": {},
        "description": "Velocidade de SSD topo de linha com 1TB, para quem tem orçamento mais curto.",
    },

    # ─── MOTHERBOARD ───────────────────────────────────────────────────────
    {
        "id": 17, "name": "ASUS ROG Maximus Z890 Apex", "brand": "ASUS", "category": "motherboard",
        "price": 4999.99, "rating": 4.9, "reviews": 78, "stock": 12,
        "badge": None, "featured": False, "image": "mb_rogmaximus.jpg",
        "specs": {"Soquete": "LGA 1851", "Chipset": "Z890", "Memória": "DDR5"},
        "compat": {"socket": "LGA 1851", "memory": "DDR5"},
        "description": "Placa para overclock extremo da plataforma Intel Core Ultra. Atenção: não aceita processadores Intel de 14ª geração.",
    },
    {
        "id": 18, "name": "ASUS ROG Crosshair X870E Extreme", "brand": "ASUS", "category": "motherboard",
        "price": 5299.99, "rating": 4.8, "reviews": 54, "stock": 9,
        "badge": None, "featured": False, "image": "mb_crosshair_x870e_extreme.jpg",
        "specs": {"Soquete": "AM5", "Chipset": "X870E", "Memória": "DDR5"},
        "compat": {"socket": "AM5", "memory": "DDR5"},
        "description": "Topo de linha AM5 com USB4 e Wi-Fi 7. Para Ryzen 7000 e 9000.",
    },
    {
        "id": 19, "name": "Gigabyte AORUS Master Z790", "brand": "Gigabyte", "category": "motherboard",
        "price": 2499.99, "rating": 4.7, "reviews": 134, "stock": 21,
        "badge": None, "featured": False, "image": "mb_aorus.jpg",
        "specs": {"Soquete": "LGA 1700", "Chipset": "Z790", "Memória": "DDR5"},
        "compat": {"socket": "LGA 1700", "memory": "DDR5"},
        "description": "VRM robusto para segurar o i9-14900K sem perder desempenho.",
    },
    {
        "id": 20, "name": "ASRock B650E Taichi Carrara", "brand": "ASRock", "category": "motherboard",
        "price": 1799.99, "original_price": 2199.99, "rating": 4.6, "reviews": 89, "stock": 33,
        "badge": None, "featured": False, "image": "mb_taichi.jpg",
        "specs": {"Soquete": "AM5", "Chipset": "B650E", "Memória": "DDR5"},
        "compat": {"socket": "AM5", "memory": "DDR5"},
        "description": "Chipset B650E com PCIe 5.0 na GPU e no SSD, por bem menos que uma X870E.",
    },

    # ─── COOLER ────────────────────────────────────────────────────────────
    {
        "id": 21, "name": "NZXT Kraken Elite 360 RGB", "brand": "NZXT", "category": "cooler",
        "price": 1299.99, "rating": 4.8, "reviews": 211, "stock": 26,
        "badge": None, "featured": True, "image": "cooler_kraken360.jpg",
        "specs": {"Tipo": "Water cooler", "Radiador": "360mm", "Fans": "3×120mm"},
        "compat": {"max_tdp": 300},
        "description": "Water cooler de 360mm com tela LCD na bomba. Dá conta de qualquer processador do catálogo.",
    },
    {
        "id": 22, "name": "Corsair iCUE H150i Elite Capellix", "brand": "Corsair", "category": "cooler",
        "price": 1099.99, "rating": 4.7, "reviews": 178, "stock": 34,
        "badge": None, "featured": False, "image": "cooler_h150i.jpg",
        "specs": {"Tipo": "Water cooler", "Radiador": "360mm", "Fans": "3×120mm"},
        "compat": {"max_tdp": 300},
        "description": "360mm com RGB controlado pelo iCUE.",
    },
    {
        "id": 23, "name": "be quiet! Dark Rock Pro 5", "brand": "be quiet!", "category": "cooler",
        "price": 499.99, "rating": 4.9, "reviews": 143, "stock": 48,
        "badge": "MAIS SILENCIOSO", "featured": False, "image": "cooler_darkrockpro5.jpg",
        "specs": {"Tipo": "Air cooler", "Dissipação": "270W", "Fans": "2×120mm"},
        "compat": {"max_tdp": 270},
        "description": "Air cooler de torre dupla, quase inaudível. Sem bomba, então tem menos peças que podem falhar.",
    },
    {
        "id": 24, "name": "DeepCool LT720 360mm", "brand": "DeepCool", "category": "cooler",
        "price": 699.99, "original_price": 849.99, "rating": 4.6, "reviews": 92, "stock": 39,
        "badge": None, "featured": False, "image": "cooler_deepcoollt720.jpg",
        "specs": {"Tipo": "Water cooler", "Radiador": "360mm", "Fans": "3×120mm"},
        "compat": {"max_tdp": 300},
        "description": "O water cooler de 360mm mais barato do catálogo.",
    },

    # ─── CASE ──────────────────────────────────────────────────────────────
    {
        "id": 25, "name": "Lian Li PC-O11 Dynamic EVO XL", "brand": "Lian Li", "category": "case",
        "price": 1299.99, "rating": 4.9, "reviews": 387, "stock": 18,
        "badge": None, "featured": True, "image": "case_o11.jpg",
        "specs": {"Formato": "Full Tower", "Vidro": "Frontal e lateral", "Radiador": "Até 420mm"},
        "compat": {},
        "description": "Vidro em dois lados e espaço para três radiadores. Feito para quem quer mostrar o PC.",
    },
    {
        "id": 26, "name": "Corsair 5000D Airflow", "brand": "Corsair", "category": "case",
        "price": 899.99, "rating": 4.8, "reviews": 256, "stock": 29,
        "badge": None, "featured": False, "image": "case_5000d.jpg",
        "specs": {"Formato": "Mid Tower", "Vidro": "Lateral", "Radiador": "Até 360mm"},
        "compat": {},
        "description": "Frente toda em tela para entrar bastante ar. Ótimo gerenciamento de cabos.",
    },
    {
        "id": 27, "name": "NZXT H9 Flow", "brand": "NZXT", "category": "case",
        "price": 1099.99, "rating": 4.7, "reviews": 134, "stock": 23,
        "badge": None, "featured": False, "image": "case_h9.jpg",
        "specs": {"Formato": "Mid Tower", "Vidro": "Frontal e lateral", "Radiador": "Até 360mm"},
        "compat": {},
        "description": "Visual de aquário com duas câmaras: os cabos e a fonte ficam escondidos atrás.",
    },
    {
        "id": 28, "name": "Fractal Design Torrent Compact", "brand": "Fractal", "category": "case",
        "price": 799.99, "original_price": 949.99, "rating": 4.8, "reviews": 198, "stock": 41,
        "badge": None, "featured": False, "image": "case_torrent.jpg",
        "specs": {"Formato": "Mid Tower", "Vidro": "Lateral", "Radiador": "Até 360mm"},
        "compat": {},
        "description": "Dois fans de 180mm na frente. Um dos gabinetes mais frescos da categoria.",
    },

    # ─── PSU ───────────────────────────────────────────────────────────────
    {
        "id": 29, "name": "Corsair HX1200i 1200W Platinum", "brand": "Corsair", "category": "psu",
        "price": 1799.99, "rating": 4.9, "reviews": 167, "stock": 21,
        "badge": None, "featured": False, "image": "psu_hx1200i.jpg",
        "specs": {"Potência": "1200W", "Eficiência": "80+ Platinum", "Modular": "Total"},
        "compat": {"watts": 1200},
        "description": "Potência de sobra para RTX 5090 com processador topo de linha.",
    },
    {
        "id": 30, "name": "EVGA SuperNOVA 1000 G7 Gold", "brand": "EVGA", "category": "psu",
        "price": 1099.99, "rating": 4.8, "reviews": 234, "stock": 38,
        "badge": None, "featured": False, "image": "psu_evga1000.jpg",
        "specs": {"Potência": "1000W", "Eficiência": "80+ Gold", "Modular": "Total"},
        "compat": {"watts": 1000},
        "description": "1000W com 10 anos de garantia do fabricante.",
    },
    {
        "id": 31, "name": "be quiet! Dark Power 13 1000W", "brand": "be quiet!", "category": "psu",
        "price": 1299.99, "rating": 4.9, "reviews": 89, "stock": 16,
        "badge": None, "featured": False, "image": "psu_darkpower13.jpg",
        "specs": {"Potência": "1000W", "Eficiência": "80+ Titanium", "Modular": "Total"},
        "compat": {"watts": 1000},
        "description": "Certificação Titanium: desperdiça menos energia e o fan quase não gira em uso leve.",
    },
    {
        "id": 32, "name": "Seasonic Focus GX-850 Gold", "brand": "Seasonic", "category": "psu",
        "price": 699.99, "original_price": 849.99, "rating": 4.7, "reviews": 312, "stock": 54,
        "badge": None, "featured": False, "image": "psu_focusgx850.jpg",
        "specs": {"Potência": "850W", "Eficiência": "80+ Gold", "Modular": "Total"},
        "compat": {"watts": 850},
        "description": "850W confiáveis. Suficiente para a maioria dos PCs com GPU de até 300W.",
    },
]

# Ofertas relâmpago: desconto extra sobre o preço atual.
# `window_hours` define de quanto em quanto tempo a oferta renova (ver app.py).
DEALS = [
    {"product_id": 1,  "extra_discount": 5,  "window_hours": 24},
    {"product_id": 5,  "extra_discount": 8,  "window_hours": 12},
    {"product_id": 13, "extra_discount": 10, "window_hours": 6},
    {"product_id": 25, "extra_discount": 7,  "window_hours": 48},
]

# Build sugerida que aparece no topo do site e pode ser aberta no montador.
FEATURED_BUILD = {
    "name": "PC para 1440p",
    "description": "Ryzen 7 + RX 9070 XT: roda os jogos atuais no alto em 1440p sem gastar com peças topo de linha.",
    "product_ids": [7, 20, 12, 2, 16, 24, 32, 28],
}
