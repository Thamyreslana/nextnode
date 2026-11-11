# NextNode — Loja de peças para PC

Loja de hardware com backend Python (Flask) e frontend em JavaScript puro.
O diferencial é o **montador de PC**: enquanto a pessoa escolhe as peças, ele confere
se o processador encaixa na placa-mãe, se a memória é do tipo certo, se o cooler
dá conta do processador e se a fonte aguenta o conjunto.

> Projeto de estudo: produtos, preços, estoque e frete são fictícios.

## Funcionalidades

- **Montador de PC** com checagem de compatibilidade (soquete, DDR4/DDR5, cooler e fonte)
  e estimativa de consumo em watts
- **Build sugerida** no topo da página, que abre direto no montador
- **Preço no Pix** (5% de desconto) e **parcelamento** em até 10x sem juros
- **Ofertas relâmpago** com contagem regressiva real: o término é calculado no servidor
  e não volta ao início quando a página é recarregada
- **Catálogo** com filtro por categoria, faixa de preço, ordenação e busca por nome ou marca
- **Busca por imagem**: a pessoa envia, arrasta ou cola uma foto e o site mostra os
  produtos com aparência mais parecida (comparação local, sem IA externa)
- **Detalhe do produto** com especificações completas
- **Carrinho** salvo no navegador, com cálculo de frete (simulado) por CEP

## Rodando localmente

```bash
uv sync
uv run python app.py
```

Acesse: http://localhost:5000

## Ilustrações dos produtos

Todos os produtos têm uma **ilustração original** em SVG, desenhada por código a partir dos
dados do catálogo (ventoinhas, capacidade, potência, slots de memória...). Elas **não são
fotos** e não reproduzem logotipos nem o design exato dos fabricantes: servem só para
representar o tipo de peça. Por isso:

- cada SVG traz a marcação **"ILUSTRAÇÃO"** no canto;
- os cards mostram o selo **"Ilustração"**;
- o detalhe do produto avisa: *"Imagem meramente ilustrativa. A aparência real do produto pode ser diferente."*

Para gerar de novo (por exemplo, depois de adicionar um produto e o estilo dele em `STYLES`):

```bash
uv run python tools/gerar_ilustracoes.py
```

Os arquivos vão para `static/images/ilustracoes/`. A **busca por imagem** ignora as
ilustrações e compara só com fotos reais, porque comparar foto com desenho não funciona.

## Fotos dos produtos

A foto real, quando existe, tem prioridade sobre a ilustração.
Para usar fotos reais, salve os arquivos em `static/images/` com o nome definido no
campo `image` de cada produto em `data/products.py` (ex.: `gpu_rog_astral_5090.jpg`).
O backend detecta o arquivo sozinho. Use imagens que você tenha direito de usar,
como as dos kits de imprensa dos fabricantes.

Para ver quais produtos ainda estão sem foto, acesse `/api/search/image/status`.

## Como funciona a busca por imagem

O módulo `image_search.py` compara **aparência**, sem usar IA:

1. Prepara a imagem: corrige a rotação, troca transparência por fundo branco e
   corta as bordas lisas
2. Gera duas "impressões digitais": a **estrutura** (dHash de 256 bits, o desenho de
   claro e escuro) e as **cores** (histograma com 36 faixas)
3. Compara com as fotos do catálogo e devolve os produtos com nota acima de `MIN_SCORE`

Só os produtos **com foto** em `static/images/` entram na busca. A imagem enviada é
processada em memória e não é salva.

**Limitação:** funciona bem quando a foto enviada se parece com a do catálogo
(mesmo produto, ângulo e fundo próximos). Foto da caixa ou da peça montada no PC
tende a falhar, porque o algoritmo não "entende" o que é o objeto.

**Calibração:** em 288 testes com imagens sintéticas (reduzidas, cortadas, giradas,
comprimidas, espelhadas, desfocadas, com outro fundo), o produto certo ficou em 1º
lugar em 97% dos casos. Se com as fotos reais aparecerem muitos resultados errados,
aumente `MIN_SCORE` em `image_search.py`. Se a busca não achar o que deveria, diminua.

## Créditos das imagens

As fotos de produtos vêm das áreas de imprensa (press kits e press releases) dos
fabricantes. Todos os direitos sobre as imagens pertencem às respectivas marcas.
Este é um projeto de estudo, sem fins comerciais: confira e respeite os termos de
uso de cada fabricante antes de baixar.

> **Situação atual:** nenhuma foto foi adicionada ainda. Os produtos aparecem com
> as ilustrações originais do projeto (ver "Ilustrações dos produtos"), que não
> precisam de crédito a terceiros. Ao salvar uma foto em `static/images/`, marque-a
> como "em uso" na tabela.

| Marca | Produtos no catálogo | Crédito | Onde baixar (fonte oficial) | Fonte |
|-------|----------------------|---------|-----------------------------|:-----:|
| AMD | RX 9070 XT, Ryzen 9 9950X, Ryzen 7 9700X | © Advanced Micro Devices, Inc. | [Newsroom AMD: lançamento RDNA 4](https://newsroom.amd.com/news/amd-unveils-next-generation-amd-rdna-4-architectu/) (botão "Download image"; siga as notas de licença do arquivo). Ryzen 9000: Media Library do newsroom | ✅ GPU · 🔎 CPU |
| Intel | Arc B580, Core i9-14900K, Core i7-14700K | © Intel Corporation | [Intel lança placas Arc série B](https://newsroom.intel.com/pt/client-computing/intel-lanca-placas-graficas-arc-serie-b) (link para o press kit). 14ª geração: não encontrado | ✅ GPU · 🔎 CPU |
| Samsung | 990 Pro NVMe 2TB | © Samsung Electronics | [Samsung Newsroom: lançamento do 990 PRO](https://news.samsung.com/us/samsung-unveils-high-performance-990-pro-series-ssds-optimized-gaming-creative-applications) (Press Kit) | ✅ |
| DeepCool | LT720 360mm | © DeepCool | [Press release da série LT](https://uk.deepcool.com/company/pressroom/newsrelease/2022/16647.shtml) (links "High-Resolution Product Images") | ✅ |
| Seasonic | Focus GX-850 | © Sea Sonic Electronics | [Lançamento da Focus GX (2024)](https://seasonic.com/news/sea-sonic-to-launch-the-new-focus-gx-2024-series/) | ✅ |
| EVGA | SuperNOVA 1000 G7 | © EVGA Corporation | [Press release #440](https://www.evga.com/about/pressrelease/?id=440) (só imagem de cabeçalho) | ⚠️ |
| Fractal Design | Torrent Compact | © Fractal Design | [Notícia de lançamento](https://www.fractal-design.com/news/streamlined-airflow-in-new-torrents/) (imagem da notícia, sem press kit) | ⚠️ |
| Lian Li | O11 Dynamic EVO XL | © LIAN LI | [Página do produto](https://lian-li.com/?p=125777) (sem press kit encontrado) | ⚠️ |
| Kingston | FURY Beast DDR5 64GB | © Kingston Technology | [Release da FURY Beast DDR5](https://www.kingston.com/en/company/press/article/64844) (link direto para a imagem do módulo) | ✅ |
| Kingston | Fury Beast DDR4, Fury Renegade NVMe | © Kingston Technology | Os releases indicam a press room da Kingston: [lançamento Kingston FURY](https://www.kingston.com/br/company/press/article/63105), [Renegade com dissipador](https://kingston.com/en/company/press/article/67775) | 🔎 |
| Corsair | Dominator Titanium, Vengeance DDR5, H150i, 5000D, HX1200i | © CORSAIR | Cada press release do newsroom da Corsair traz o link das imagens (às vezes com senha informada no próprio release). Releases destes produtos não encontrados | 🔎 |
| ASUS | ROG Astral RTX 5090, ROG Strix RTX 5070 Ti | © ASUSTeK Computer Inc. | [Álbum de imprensa ASUS da série RTX 50](https://press.asus.com/media/photos/159/albums/881/) (PNGs da ROG Astral RTX 5090 e da ROG Strix RTX 5070 Ti) | ✅ |
| ASUS | ROG Crosshair X870E Extreme | © ASUSTeK Computer Inc. | [Press release da Crosshair X870E Extreme e Apex](https://press.asus.com/news/press-releases/rog-crosshair-x870e-extreme-apex-motherboards-reveal) (confira se há imagens para download) | 🔎 |
| ASUS | ROG Maximus Z890 Apex | © ASUSTeK Computer Inc. | [Media kit ASUS ROG (CES 2025)](https://press.asus.com/media/media-kit/2025-ces-rog-media-kit/) | 🔎 |
| Gigabyte | AORUS Master Z790 | © GIGABYTE | [Press kit Computex 2026](https://www.gigabyte.com/press/media-kit/computex-2026-GIGABYTE-aorus-press-kit) (não cobre a Z790) | 🔎 |
| ASRock | B650E Taichi Carrara | © ASRock | [Notícias ASRock](https://www.asrock.com/news/index.us.asp) | 🔎 |
| be quiet! | Dark Rock Pro 5, Dark Power 13 | © be quiet! | Páginas de imprensa por produto em bequiet.com (pacotes ZIP). Procure pelo nome do produto | 🔎 |
| NZXT | Kraken Elite 360, H9 Flow | © NZXT | [Arquivo de press releases](https://nzxt.com/blogs/news/tagged/press-releases?page=1) | 🔎 |
| Western Digital | WD Black SN850X | © Western Digital | [Press release de 2022](https://www.westerndigital.com/company/newsroom/press-releases/2022/2022-05-09-western-digital-expands-wd-black-ssd-portfolio) (a linha WD_BLACK passou para a SanDisk) | 🔎 |
| Seagate | FireCuda 530 | © Seagate Technology | Os releases citam um press kit, mas não foi encontrado para o 530 | 🔎 |

**Legenda:** ✅ imagem oficial para download encontrada · ⚠️ só imagem publicada em
página ou notícia · 🔎 a marca tem área de imprensa, mas o produto não foi encontrado.

GeForce é marca registrada da NVIDIA Corporation. As placas de vídeo do catálogo são
versões da ASUS, porque a NVIDIA não mantém uma biblioteca central de imagens. Produtos
da MSI (que exige permissão por escrito para usar imagens) e da G.Skill (sem fonte
oficial encontrada) foram retirados do catálogo.

## Deploy no Render.com

O projeto já está configurado via `render.yaml`.

1. Faça push deste repositório para o GitHub
2. No [Render](https://render.com), clique em **New +** → **Web Service**
3. Conecte o repositório. As configurações são lidas do `render.yaml`
4. Clique em **Create Web Service**

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.14 + Flask |
| Imagens | Pillow |
| API | REST JSON |
| Frontend | HTML + CSS + JavaScript (ES Modules, sem framework) |
| Servidor de produção | Gunicorn |
| Fontes | Barlow, Barlow Condensed e Orbitron (logo) |

## API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/categories` | Categorias com a quantidade de produtos |
| GET | `/api/products` | Produtos. Filtros: `category`, `search`, `featured`, `min_price`, `max_price`, `sort`, `limit` |
| GET | `/api/products/<id>` | Produto por ID |
| GET | `/api/featured` | Produtos em destaque |
| GET | `/api/builds/featured` | Build sugerida com total |
| GET | `/api/deals` | Ofertas relâmpago com horário de término (`ends_at`) |
| POST | `/api/search/image` | Busca por imagem. `multipart/form-data` com o campo `image` (JPG, PNG ou WEBP, até 8 MB) |
| GET | `/api/search/image/status` | Quantos produtos têm foto e quais arquivos estão faltando |
| POST | `/api/shipping` | Frete simulado. Corpo: `{"cep": "01310-100", "subtotal": 1200}` |
| POST | `/api/newsletter` | Cadastro de e-mail (simulado) |

## Estrutura

```
nextnode/
├── app.py                 # Backend Flask (rotas da API)
├── image_search.py        # Busca por imagem (impressões digitais e comparação)
├── tools/
│   └── gerar_ilustracoes.py  # Gera as ilustrações SVG dos produtos
├── data/
│   ├── products.py        # 32 produtos, 8 categorias, ofertas e build sugerida
│   └── shipping.py        # Tabela de frete por região do CEP (simulada)
├── static/
│   ├── css/style.css
│   └── js/
│       ├── main.js        # Orquestra a página (catálogo, ofertas, detalhe)
│       ├── builder.js     # Montador de PC e regras de compatibilidade
│       ├── cart.js        # Carrinho, frete e totais
│       ├── image-search.js # Janela da busca por imagem
│       ├── api.js         # Cliente da API
│       ├── icons.js       # Ícones SVG
│       └── utils.js       # Formatação, toasts e armazenamento
└── templates/
    └── index.html
```
