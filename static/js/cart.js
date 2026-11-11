/**
 * NextNode — Cart Module
 * Carrinho de compras com persistência via LocalStorage,
 * total no Pix, parcelamento e cálculo de frete por CEP.
 */

import {
  formatCurrency, escapeHtml, roundMoney, showToast,
  readStorage, writeStorage, PIX_DISCOUNT, MAX_INSTALLMENTS,
} from "./utils.js";
import { icon, productVisual } from "./icons.js";
import { fetchShipping } from "./api.js";

const CART_KEY = "nextnode_cart";

// Frete fica só em memória: depende do CEP e do subtotal do momento
const shipping = { cep: "", result: null, selected: "economico", forSubtotal: null, loading: false };

// ─── Estado ───────────────────────────────────────────────────────────────────

function loadCart() {
  const items = readStorage(CART_KEY, []);
  if (!Array.isArray(items)) return [];
  return items
    .filter((i) => i && i.id != null && Number.isFinite(i.price))
    .map((i) => ({
      ...i,
      // Itens salvos por versões antigas do site não tinham `key` nem `pix_price`
      key: i.key || String(i.id),
      pix_price: Number.isFinite(i.pix_price) ? i.pix_price : roundMoney(i.price * (1 - PIX_DISCOUNT)),
    }));
}

function saveCart(items) {
  writeStorage(CART_KEY, items);
}

// ─── Operações ────────────────────────────────────────────────────────────────

export function getCart() {
  return loadCart();
}

export function getCartTotals(cart = loadCart()) {
  const count    = cart.reduce((s, i) => s + i.quantity, 0);
  const subtotal = roundMoney(cart.reduce((s, i) => s + i.price * i.quantity, 0));
  const pix      = roundMoney(cart.reduce((s, i) => s + i.pix_price * i.quantity, 0));
  return { count, subtotal, pix };
}

/**
 * Adiciona produto ao carrinho ou incrementa a quantidade.
 * A `key` separa o mesmo produto com preços diferentes
 * (ex.: preço normal × preço de oferta), para um não sobrescrever o outro.
 * @param {{ id, key?, name, brand?, price, pix_price?, image_url?, category }} product
 * @param {{ quantity?: number, silent?: boolean }} [opts]
 */
export function addToCart(product, { quantity = 1, silent = false } = {}) {
  const cart = loadCart();
  const key = product.key || String(product.id);
  const existing = cart.find((i) => i.key === key);
  if (existing) {
    existing.quantity += quantity;
  } else {
    cart.push({
      key,
      id:        product.id,
      name:      product.name,
      brand:     product.brand || "",
      price:     product.price,
      pix_price: product.pix_price ?? roundMoney(product.price * (1 - PIX_DISCOUNT)),
      image_url: product.image_url || null,
      illustration_url: product.illustration_url || null,
      category:  product.category,
      quantity,
    });
  }
  saveCart(cart);
  updateCartUI();
  if (!silent) showToast(`${product.name} foi para o carrinho.`, "success");
  return cart;
}

/** Remove um item do carrinho. */
export function removeFromCart(key) {
  const cart = loadCart().filter((i) => i.key !== String(key));
  saveCart(cart);
  updateCartUI();
  return cart;
}

/**
 * Altera a quantidade de um item.
 * @param {string} key
 * @param {number} delta — positivo para aumentar, negativo para diminuir
 */
export function changeQuantity(key, delta) {
  const cart = loadCart();
  const item = cart.find((i) => i.key === String(key));
  if (!item) return cart;
  item.quantity += delta;
  if (item.quantity <= 0) return removeFromCart(key);
  saveCart(cart);
  updateCartUI();
  return cart;
}

export function clearCart() {
  saveCart([]);
  updateCartUI();
}

// ─── Painel do carrinho ───────────────────────────────────────────────────────

export function openCart() {
  document.getElementById("cart-sidebar")?.classList.add("open");
  document.getElementById("cart-overlay")?.classList.add("open");
  document.getElementById("cart-sidebar")?.setAttribute("aria-hidden", "false");
  document.body.classList.add("no-scroll");
  document.getElementById("cart-close")?.focus();
}

export function closeCart() {
  document.getElementById("cart-sidebar")?.classList.remove("open");
  document.getElementById("cart-overlay")?.classList.remove("open");
  document.getElementById("cart-sidebar")?.setAttribute("aria-hidden", "true");
  document.body.classList.remove("no-scroll");
}

export function initCart() {
  document.getElementById("cart-btn")?.addEventListener("click", openCart);
  document.getElementById("cart-close")?.addEventListener("click", closeCart);
  document.getElementById("cart-overlay")?.addEventListener("click", closeCart);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeCart();
  });

  // Botões dos itens: um único listener para a lista toda (event delegation)
  document.getElementById("cart-items")?.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-action]");
    if (!btn) return;
    const { action, key } = btn.dataset;
    if (action === "inc") changeQuantity(key, +1);
    if (action === "dec") changeQuantity(key, -1);
    if (action === "remove") removeFromCart(key);
  });

  document.getElementById("cart-clear")?.addEventListener("click", clearCart);
  document.getElementById("cart-checkout")?.addEventListener("click", () => {
    showToast("O checkout não faz parte deste projeto de estudo.", "info");
  });

  // CEP: máscara 00000-000 e cálculo do frete
  const cepInput = document.getElementById("cep-input");
  cepInput?.addEventListener("input", () => {
    const digits = cepInput.value.replace(/\D/g, "").slice(0, 8);
    cepInput.value = digits.length > 5 ? `${digits.slice(0, 5)}-${digits.slice(5)}` : digits;
  });
  document.getElementById("cep-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    shipping.cep = cepInput.value;
    shipping.result = null;
    requestShipping();
  });

  document.getElementById("shipping-result")?.addEventListener("change", (e) => {
    if (e.target.name === "shipping-option") {
      shipping.selected = e.target.value;
      renderSummary(loadCart());
    }
  });

  updateCartUI();
}

async function requestShipping() {
  const { subtotal } = getCartTotals();
  if (!shipping.cep || subtotal === 0) return;
  shipping.loading = true;
  shipping.forSubtotal = subtotal;
  renderShipping();
  try {
    shipping.result = await fetchShipping(shipping.cep, subtotal);
    shipping.error = "";
  } catch (err) {
    shipping.result = null;
    shipping.error = err.message;
  } finally {
    shipping.loading = false;
    renderShipping();
    renderSummary(loadCart());
  }
}

export function updateCartUI() {
  const cart = loadCart();
  const { count, subtotal } = getCartTotals(cart);

  const badge = document.getElementById("cart-badge");
  if (badge) {
    badge.textContent = count;
    badge.hidden = count === 0;
  }
  const btn = document.getElementById("cart-btn");
  btn?.setAttribute("aria-label", count ? `Abrir carrinho, ${count} ${count === 1 ? "item" : "itens"}` : "Abrir carrinho, vazio");

  renderItems(cart);

  // O frete depende do subtotal (frete grátis acima de R$ 500): recalcula se mudou
  if (shipping.cep && subtotal > 0 && subtotal !== shipping.forSubtotal && !shipping.loading) {
    requestShipping();
  }
  renderShipping();
  renderSummary(cart);
}

function renderItems(cart) {
  const listEl = document.getElementById("cart-items");
  const footer = document.getElementById("cart-footer");
  if (!listEl) return;
  if (footer) footer.hidden = cart.length === 0;

  if (cart.length === 0) {
    listEl.innerHTML = `
      <div class="cart-empty">
        ${icon("cart", { size: 32 })}
        <p>Seu carrinho está vazio.</p>
        <a href="#montador" class="btn btn-ghost btn-sm" data-close-cart>Montar um PC</a>
      </div>`;
    listEl.querySelector("[data-close-cart]")?.addEventListener("click", closeCart);
    return;
  }

  listEl.innerHTML = cart
    .map((item) => {
      const isDeal = item.key.startsWith("deal-");
      return `
      <div class="cart-item">
        <div class="cart-item-media">${productVisual(item, { size: 28 })}</div>
        <div class="cart-item-info">
          <span class="cart-item-name">${escapeHtml(item.name)}</span>
          ${isDeal ? `<span class="tag tag-deal">Oferta relâmpago</span>` : ""}
          <span class="cart-item-price">${formatCurrency(item.pix_price * item.quantity)} <small>no Pix</small></span>
          <div class="qty">
            <button type="button" class="qty-btn" data-action="dec" data-key="${escapeHtml(item.key)}" aria-label="Diminuir quantidade">${icon("minus", { size: 16 })}</button>
            <span class="qty-value" aria-label="Quantidade">${item.quantity}</span>
            <button type="button" class="qty-btn" data-action="inc" data-key="${escapeHtml(item.key)}" aria-label="Aumentar quantidade">${icon("plus", { size: 16 })}</button>
            <button type="button" class="qty-remove" data-action="remove" data-key="${escapeHtml(item.key)}" aria-label="Remover ${escapeHtml(item.name)}">${icon("trash", { size: 16 })}</button>
          </div>
        </div>
      </div>`;
    })
    .join("");
}

function renderShipping() {
  const el = document.getElementById("shipping-result");
  if (!el) return;

  if (shipping.loading) {
    el.innerHTML = `<p class="muted">Calculando frete…</p>`;
    return;
  }
  if (shipping.error) {
    el.innerHTML = `<p class="field-error">${escapeHtml(shipping.error)}</p>`;
    return;
  }
  const r = shipping.result;
  if (!r) {
    el.innerHTML = "";
    return;
  }

  el.innerHTML = `
    <p class="shipping-region">${icon("truck", { size: 16 })} Entrega para ${escapeHtml(r.cep)} · ${escapeHtml(r.region)}</p>
    <div class="shipping-options" role="radiogroup" aria-label="Opções de frete">
      ${r.options
        .map(
          (o) => `
        <label class="shipping-option">
          <input type="radio" name="shipping-option" value="${o.id}" ${o.id === shipping.selected ? "checked" : ""}>
          <span>${escapeHtml(o.name)} <small>até ${o.days} ${o.days === 1 ? "dia útil" : "dias úteis"}</small></span>
          <strong>${o.price === 0 ? "Grátis" : formatCurrency(o.price)}</strong>
        </label>`
        )
        .join("")}
    </div>
    <p class="note">Frete simulado para fins de estudo.</p>`;
}

function selectedShippingPrice() {
  const option = shipping.result?.options.find((o) => o.id === shipping.selected);
  return option ? option.price : null;
}

function renderSummary(cart) {
  const { subtotal, pix } = getCartTotals(cart);
  const freight = selectedShippingPrice();
  const extra = freight ?? 0;

  const set = (id, text) => {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  };
  set("cart-subtotal", formatCurrency(subtotal));
  set("cart-shipping", freight == null ? "Informe o CEP" : freight === 0 ? "Grátis" : formatCurrency(freight));
  set("cart-total-pix", formatCurrency(pix + extra));
  const cardTotal = subtotal + extra;
  set(
    "cart-installments",
    `ou ${formatCurrency(cardTotal)} no cartão em até ${MAX_INSTALLMENTS}x de ${formatCurrency(cardTotal / MAX_INSTALLMENTS)} sem juros`
  );
}
