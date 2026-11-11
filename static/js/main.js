/**
 * NextNode — Main Application
 * Orquestra o frontend: catálogo, ofertas, build sugerida,
 * detalhe do produto, busca e newsletter.
 */

import {
  fetchCategories,
  fetchProducts,
  fetchProduct,
  fetchDeals,
  fetchFeaturedBuild,
  subscribeNewsletter,
} from "./api.js";
import { initCart, addToCart } from "./cart.js";
import { initBuilder, loadBuild, setBuildPart } from "./builder.js";
import { initImageSearch } from "./image-search.js";
import { icon, hydrateIcons, productVisual } from "./icons.js";
import { formatCurrency, escapeHtml, showToast, MAX_INSTALLMENTS } from "./utils.js";

// ─── Estado ───────────────────────────────────────────────────────────────────

let allProducts = [];
let categories  = [];
let deals       = [];
let featuredBuild = null;

const filters = { category: "all", search: "", price: "all", sort: "relevance" };

// Resultado da busca por imagem. Enquanto existir, o catálogo mostra
// só os produtos parecidos, do mais para o menos parecido.
let imageSearch = null;   // { results: [{id, similarity}], previewUrl, indexed, total }

const PRICE_RANGES = {
  all:          [0, Infinity],
  "ate-1000":   [0, 1000],
  "1000-3000":  [1000, 3000],
  "acima-3000": [3000, Infinity],
};

const SORTERS = {
  relevance:  null,
  price_asc:  (a, b) => a.price - b.price,
  price_desc: (a, b) => b.price - a.price,
  rating:     (a, b) => b.rating - a.rating || b.reviews - a.reviews,
  discount:   (a, b) => b.discount - a.discount,
};

const byId = (id) => allProducts.find((p) => p.id === Number(id));
const categoryOf = (slug) => categories.find((c) => c.id === slug);

// ─── Init ─────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", async () => {
  hydrateIcons();
  initHeader();
  initMobileMenu();
  initCart();
  initGlobalActions();

  const [cats, products, dealList, build] = await Promise.all([
    fetchCategories().catch(() => []),
    fetchProducts().catch(() => []),
    fetchDeals().catch(() => []),
    fetchFeaturedBuild().catch(() => null),
  ]);
  categories = cats;
  allProducts = products;
  deals = dealList;
  featuredBuild = build;

  if (!allProducts.length) {
    showToast("Não foi possível carregar os produtos. O servidor está rodando?", "error");
  }

  renderCategories();
  renderFeaturedBuild();
  renderDeals();
  initCatalogControls();
  renderCatalog();
  initBuilder(allProducts);
  initSearch();
  initImageSearch({ onResults: showImageResults });
  document.getElementById("image-banner-clear")?.addEventListener("click", () => {
    clearImageSearch();
    renderCatalog();
  });
  initNewsletter();
  initProductDialog();
  startDealTimers();
});

// ─── Header e menu mobile ─────────────────────────────────────────────────────

function initHeader() {
  const header = document.querySelector(".site-header");
  const onScroll = () => header?.classList.toggle("scrolled", window.scrollY > 8);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}

function initMobileMenu() {
  const toggle  = document.getElementById("mobile-menu-btn");
  const navMenu = document.getElementById("nav-links");
  if (!toggle || !navMenu) return;

  const setOpen = (open) => {
    navMenu.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
    toggle.innerHTML = icon(open ? "x" : "menu", { size: 22 });
  };

  toggle.addEventListener("click", () => setOpen(!navMenu.classList.contains("open")));
  navMenu.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setOpen(false)));
}

// ─── Ações por atributo data-* (um listener para a página toda) ───────────────

function initGlobalActions() {
  document.addEventListener("click", (e) => {
    const target = e.target.closest("[data-add], [data-add-deal], [data-open], [data-load-build], [data-filter-category]");
    if (!target) return;

    if (target.dataset.add) {
      const product = byId(target.dataset.add);
      if (product) addToCart(product);
    } else if (target.dataset.addDeal) {
      addDealToCart(Number(target.dataset.addDeal));
    } else if (target.dataset.open) {
      openProduct(Number(target.dataset.open));
    } else if (target.dataset.loadBuild !== undefined && featuredBuild) {
      loadBuild(featuredBuild.products);
      showToast(`Build "${featuredBuild.name}" carregada no montador.`, "success");
    } else if (target.dataset.filterCategory) {
      e.preventDefault();
      setCategory(target.dataset.filterCategory);
      document.getElementById("produtos")?.scrollIntoView({ behavior: "smooth" });
    }
  });
}

// ─── Categorias ───────────────────────────────────────────────────────────────

function renderCategories() {
  const el = document.getElementById("category-strip");
  if (!el) return;
  el.innerHTML = categories
    .map(
      (c) => `
      <button type="button" class="category" data-filter-category="${c.id}">
        <span class="category-icon">${icon(c.id, { size: 26 })}</span>
        <span class="category-name">${escapeHtml(c.name)}</span>
        <span class="category-count">${c.count} ${c.count === 1 ? "produto" : "produtos"}</span>
      </button>`
    )
    .join("");
}

// ─── Build sugerida (hero) ────────────────────────────────────────────────────

function renderFeaturedBuild() {
  const el = document.getElementById("featured-build");
  if (!el || !featuredBuild) return;
  const b = featuredBuild;

  el.innerHTML = `
    <div class="build-card-head">
      <span class="eyebrow">Build sugerida</span>
      <h2 class="build-card-title">${escapeHtml(b.name)}</h2>
      <p class="build-card-desc">${escapeHtml(b.description)}</p>
    </div>
    <ul class="build-list">
      ${b.products
        .map(
          (p) => `
        <li>
          <span class="build-list-icon">${icon(p.category, { size: 18 })}</span>
          <button type="button" class="build-list-name" data-open="${p.id}">${escapeHtml(p.name)}</button>
          <span class="build-list-price">${formatCurrency(p.pix_price)}</span>
        </li>`
        )
        .join("")}
    </ul>
    <div class="build-card-foot">
      <div>
        <strong class="price-big">${formatCurrency(b.pix_price)}</strong>
        <span class="muted">no Pix · ou ${b.installments.count}x de ${formatCurrency(b.installments.value)}</span>
      </div>
      <button type="button" class="btn btn-primary" data-load-build>
        Abrir no montador ${icon("arrow", { size: 18 })}
      </button>
    </div>`;
}

// ─── Ofertas relâmpago ────────────────────────────────────────────────────────

function renderDeals() {
  const el = document.getElementById("deals-grid");
  if (!el) return;
  if (!deals.length) {
    el.innerHTML = `<p class="muted">Nenhuma oferta ativa agora.</p>`;
    return;
  }

  el.innerHTML = deals
    .map((d) => {
      const p = d.product;
      return `
      <article class="deal">
        <button type="button" class="deal-media" data-open="${p.id}" aria-label="Ver detalhes de ${escapeHtml(p.name)}">
          ${productVisual(p, { size: 48 })}
        </button>
        <div class="deal-body">
          <p class="deal-timer">${icon("clock", { size: 16 })} termina em <time data-ends-at="${d.ends_at}">--:--:--</time></p>
          <h3 class="deal-name">${escapeHtml(p.name)}</h3>
          <div class="price">
            <span class="price-old">${formatCurrency(p.original_price)}</span>
            <span class="tag tag-deal">-${d.total_discount}%</span>
            <strong class="price-pix">${formatCurrency(d.pix_price)}</strong>
            <span class="price-note">no Pix · ou ${formatCurrency(d.deal_price)} em ${d.installments.count}x</span>
          </div>
          <button type="button" class="btn btn-deal btn-sm" data-add-deal="${p.id}">
            ${icon("cart", { size: 16 })} Comprar na oferta
          </button>
        </div>
      </article>`;
    })
    .join("");
}

function addDealToCart(productId) {
  const deal = deals.find((d) => d.product.id === productId);
  if (!deal) return;
  addToCart({
    ...deal.product,
    key: `deal-${productId}`,
    price: deal.deal_price,
    pix_price: deal.pix_price,
  });
}

/** Um único timer atualiza todos os contadores das ofertas. */
function startDealTimers() {
  let reloading = false;

  const tick = async () => {
    const now = Date.now();
    let expired = false;
    document.querySelectorAll("[data-ends-at]").forEach((el) => {
      const left = Math.max(0, Math.floor((Date.parse(el.dataset.endsAt) - now) / 1000));
      if (left === 0) expired = true;
      const h = Math.floor(left / 3600);
      const m = Math.floor((left % 3600) / 60);
      const s = left % 60;
      el.textContent = [h, m, s].map((n) => String(n).padStart(2, "0")).join(":");
    });

    // Quando uma oferta acaba, busca as novas no servidor
    if (expired && !reloading) {
      reloading = true;
      deals = await fetchDeals().catch(() => deals);
      renderDeals();
      reloading = false;
    }
  };

  tick();
  setInterval(tick, 1000);
}

// ─── Catálogo ─────────────────────────────────────────────────────────────────

function initCatalogControls() {
  const chips = document.getElementById("category-chips");
  if (chips) {
    chips.innerHTML =
      `<button type="button" class="chip" data-chip="all" aria-pressed="true">Todos</button>` +
      categories
        .map((c) => `<button type="button" class="chip" data-chip="${c.id}" aria-pressed="false">${escapeHtml(c.short)}</button>`)
        .join("");
    chips.addEventListener("click", (e) => {
      const chip = e.target.closest("[data-chip]");
      if (chip) setCategory(chip.dataset.chip);
    });
  }

  document.getElementById("price-filter")?.addEventListener("change", (e) => {
    filters.price = e.target.value;
    clearImageSearch();
    renderCatalog();
  });
  document.getElementById("sort-select")?.addEventListener("change", (e) => {
    filters.sort = e.target.value;
    clearImageSearch();
    renderCatalog();
  });
}

function setCategory(slug) {
  filters.category = slug;
  clearImageSearch();
  document.querySelectorAll("#category-chips [data-chip]").forEach((chip) => {
    chip.setAttribute("aria-pressed", String(chip.dataset.chip === slug));
  });
  renderCatalog();
}

function resetFilters() {
  filters.search = "";
  filters.price = "all";
  const search = document.getElementById("search-input");
  if (search) search.value = "";
  const price = document.getElementById("price-filter");
  if (price) price.value = "all";
  setCategory("all");
}

function filteredProducts() {
  if (imageSearch) {
    return imageSearch.results
      .map((r) => {
        const product = byId(r.id);
        return product ? { ...product, similarity: r.similarity } : null;
      })
      .filter(Boolean);
  }

  const [min, max] = PRICE_RANGES[filters.price] || PRICE_RANGES.all;
  const query = filters.search.toLowerCase();

  const list = allProducts.filter(
    (p) =>
      (filters.category === "all" || p.category === filters.category) &&
      p.price >= min &&
      p.price < max &&
      (!query || `${p.name} ${p.brand}`.toLowerCase().includes(query))
  );

  const sorter = SORTERS[filters.sort];
  return sorter ? [...list].sort(sorter) : list;
}

function renderCatalog() {
  const grid = document.getElementById("products-grid");
  const count = document.getElementById("results-count");
  if (!grid) return;

  const products = filteredProducts();
  if (count) count.textContent = `${products.length} ${products.length === 1 ? "produto" : "produtos"}`;
  renderImageBanner(products.length);

  if (imageSearch && products.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <p>Nenhum produto do catálogo ficou parecido o bastante com essa imagem.</p>
        <p class="note">A busca compara a aparência com as fotos cadastradas. Ela funciona melhor
        com fotos de frente, com o produto inteiro e fundo liso, parecidas com as do catálogo.</p>
        <button type="button" class="btn btn-ghost" id="image-try-again">Tentar outra imagem</button>
      </div>`;
    document.getElementById("image-try-again")?.addEventListener("click", () =>
      document.getElementById("image-search-btn")?.click()
    );
    return;
  }

  if (products.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <p>Nenhum produto com esses filtros.</p>
        <button type="button" class="btn btn-ghost" id="reset-filters">Limpar filtros</button>
      </div>`;
    document.getElementById("reset-filters")?.addEventListener("click", resetFilters);
    return;
  }

  grid.innerHTML = products.map(productCard).join("");
}

// ─── Busca por imagem: integração com o catálogo ──────────────────────────────

function showImageResults(result) {
  imageSearch = result;
  // Os filtros de texto/categoria não se aplicam à busca por imagem
  filters.category = "all";
  filters.search = "";
  const search = document.getElementById("search-input");
  if (search) search.value = "";
  document.querySelectorAll("#category-chips [data-chip]").forEach((chip) => {
    chip.setAttribute("aria-pressed", String(chip.dataset.chip === "all"));
  });
  renderCatalog();
  document.getElementById("produtos")?.scrollIntoView({ behavior: "smooth" });
}

function clearImageSearch() {
  imageSearch = null;
}

function renderImageBanner(found) {
  const banner = document.getElementById("image-banner");
  if (!banner) return;
  banner.hidden = !imageSearch;
  if (!imageSearch) return;

  const thumb = document.getElementById("image-banner-thumb");
  if (thumb && imageSearch.previewUrl) thumb.src = imageSearch.previewUrl;

  document.getElementById("image-banner-title").textContent = found
    ? `${found} ${found === 1 ? "produto parecido" : "produtos parecidos"} com a sua imagem`
    : "Busca por imagem";
  document.getElementById("image-banner-note").textContent =
    `Comparado com os ${imageSearch.indexed} de ${imageSearch.total} produtos que têm foto.`;
}

function productCard(p) {
  const cat = categoryOf(p.category);
  const specs = Object.values(p.specs).slice(0, 2).join(" · ");
  return `
  <article class="product-card">
    <button type="button" class="product-media" data-open="${p.id}" aria-label="Ver detalhes de ${escapeHtml(p.name)}">
      ${productVisual(p)}
      ${p.badge ? `<span class="tag tag-badge">${escapeHtml(p.badge)}</span>` : ""}
      ${p.similarity != null ? `<span class="tag tag-match">${p.similarity}% parecido</span>` : ""}
    </button>
    <div class="product-body">
      <p class="product-meta">${escapeHtml(p.brand)} · ${escapeHtml(cat?.short ?? p.category)}</p>
      <h3 class="product-name"><button type="button" data-open="${p.id}">${escapeHtml(p.name)}</button></h3>
      <p class="product-specs">${escapeHtml(specs)}</p>
      <p class="rating">${icon("star", { size: 14, filled: true })} ${p.rating.toFixed(1)} <span>(${p.reviews} avaliações)</span></p>
      <div class="price">
        ${p.discount ? `<span class="price-old">${formatCurrency(p.original_price)}</span><span class="tag tag-off">-${p.discount}%</span>` : ""}
        <strong class="price-pix">${formatCurrency(p.pix_price)}</strong>
        <span class="price-note">no Pix · ou ${MAX_INSTALLMENTS}x de ${formatCurrency(p.installments.value)}</span>
      </div>
      ${p.stock <= 10 ? `<p class="stock-low">Restam ${p.stock} unidades</p>` : ""}
      <button type="button" class="btn btn-primary btn-sm btn-block" data-add="${p.id}">
        ${icon("cart", { size: 16 })} Adicionar ao carrinho
      </button>
    </div>
  </article>`;
}

// ─── Busca ────────────────────────────────────────────────────────────────────

function initSearch() {
  const form = document.getElementById("search-form");
  const input = document.getElementById("search-input");
  if (!input) return;

  let debounce;
  input.addEventListener("input", () => {
    clearTimeout(debounce);
    debounce = setTimeout(() => {
      filters.search = input.value.trim();
      clearImageSearch();
      renderCatalog();
    }, 250);
  });

  // Enter leva até os resultados
  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    filters.search = input.value.trim();
    clearImageSearch();
    renderCatalog();
    document.getElementById("produtos")?.scrollIntoView({ behavior: "smooth" });
  });
}

// ─── Detalhe do produto (dialog) ──────────────────────────────────────────────

function initProductDialog() {
  const dialog = document.getElementById("product-dialog");
  if (!dialog) return;

  dialog.addEventListener("click", (e) => {
    // Clique fora do conteúdo (no fundo escuro) fecha
    if (e.target === dialog || e.target.closest("[data-close-dialog]")) dialog.close();

    const useBtn = e.target.closest("[data-use-in-builder]");
    if (useBtn) {
      const product = byId(useBtn.dataset.useInBuilder);
      if (product) {
        setBuildPart(product);
        dialog.close();
        document.getElementById("montador")?.scrollIntoView({ behavior: "smooth" });
      }
    }
  });
}

async function openProduct(id) {
  const dialog = document.getElementById("product-dialog");
  const content = document.getElementById("dialog-content");
  if (!dialog || !content) return;

  content.innerHTML = `<p class="muted dialog-loading">Carregando…</p>`;
  if (!dialog.open) dialog.showModal();

  let p;
  try {
    p = await fetchProduct(id);
  } catch {
    content.innerHTML = `<p class="field-error dialog-loading">Não foi possível carregar o produto.</p>`;
    return;
  }

  const cat = categoryOf(p.category);
  const inBuilder = ["cpu", "motherboard", "ram", "gpu", "ssd", "cooler", "psu", "case"].includes(p.category);

  content.innerHTML = `
    <button type="button" class="dialog-close" data-close-dialog aria-label="Fechar">${icon("x", { size: 22 })}</button>
    <div class="dialog-media">
      ${productVisual(p, { size: 96 })}
      ${!p.image_url && p.illustration_url
        ? `<p class="illus-note">Imagem meramente ilustrativa. A aparência real do produto pode ser diferente.</p>`
        : ""}
    </div>
    <div class="dialog-info">
      <p class="product-meta">${escapeHtml(p.brand)} · ${escapeHtml(cat?.name ?? p.category)}</p>
      <h2 class="dialog-title" id="dialog-title">${escapeHtml(p.name)}</h2>
      <p class="rating">${icon("star", { size: 14, filled: true })} ${p.rating.toFixed(1)} <span>(${p.reviews} avaliações)</span></p>
      <p class="dialog-desc">${escapeHtml(p.description)}</p>

      <dl class="specs">
        ${Object.entries(p.specs).map(([k, v]) => `<div><dt>${escapeHtml(k)}</dt><dd>${escapeHtml(v)}</dd></div>`).join("")}
      </dl>

      <div class="price price-lg">
        ${p.discount ? `<span class="price-old">${formatCurrency(p.original_price)}</span><span class="tag tag-off">-${p.discount}%</span>` : ""}
        <strong class="price-pix">${formatCurrency(p.pix_price)}</strong>
        <span class="price-note">${icon("pix", { size: 14 })} no Pix (5% de desconto)</span>
        <span class="price-note">${icon("card", { size: 14 })} ou ${formatCurrency(p.price)} em até ${p.installments.count}x de ${formatCurrency(p.installments.value)} sem juros</span>
      </div>
      <p class="${p.stock <= 10 ? "stock-low" : "muted"}">${p.stock <= 10 ? `Restam ${p.stock} unidades` : `${p.stock} unidades em estoque`}</p>

      <div class="dialog-actions">
        <button type="button" class="btn btn-primary" data-add="${p.id}">${icon("cart", { size: 18 })} Adicionar ao carrinho</button>
        ${inBuilder ? `<button type="button" class="btn btn-ghost" data-use-in-builder="${p.id}">Usar no montador</button>` : ""}
      </div>
    </div>`;
}

// ─── Newsletter ───────────────────────────────────────────────────────────────

function initNewsletter() {
  const form = document.getElementById("newsletter-form");
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = form.querySelector("input[type=email]");
    const btn   = form.querySelector("button[type=submit]");
    const msgEl = document.getElementById("newsletter-msg");

    btn.disabled    = true;
    btn.textContent = "Enviando…";

    try {
      const res = await subscribeNewsletter(input.value);
      if (msgEl) { msgEl.textContent = res.message; msgEl.className = "newsletter-msg success"; }
      input.value = "";
    } catch (err) {
      if (msgEl) { msgEl.textContent = "Confira o e-mail e tente de novo."; msgEl.className = "newsletter-msg error"; }
    } finally {
      btn.disabled    = false;
      btn.textContent = "Quero receber";
    }
  });
}
