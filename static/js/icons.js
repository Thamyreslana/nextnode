/**
 * NextNode — Ícones
 * Conjunto pequeno de ícones em SVG (traço de 24×24, no estilo do Lucide).
 * Ficam aqui no projeto para o site não depender de CDN nem de emojis,
 * que mudam de aparência em cada sistema operacional.
 */

import { escapeHtml } from "./utils.js";

const PATHS = {
  // Interface
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  cart: '<circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>',
  menu: '<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>',
  x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  plus: '<path d="M5 12h14"/><path d="M12 5v14"/>',
  minus: '<path d="M5 12h14"/>',
  trash: '<path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
  arrow: '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
  star: '<path d="M12 2.5l2.94 5.96 6.56.95-4.75 4.63 1.12 6.54L12 17.5l-5.87 3.08 1.12-6.54L2.5 9.41l6.56-.95z"/>',
  truck: '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.62l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
  pix: '<path d="m12 3 9 9-9 9-9-9z"/><path d="m8 12 4-4 4 4-4 4z"/>',
  card: '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  ok: '<circle cx="12" cy="12" r="9"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
  warn: '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
  error: '<circle cx="12" cy="12" r="9"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
  mail: '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
  bolt: '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
  image: '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.09-3.09a2 2 0 0 0-2.82 0L6 21"/>',
  upload: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',

  // Categorias
  gpu: '<rect x="2" y="6" width="20" height="11" rx="1.5"/><circle cx="8" cy="11.5" r="2.5"/><circle cx="16" cy="11.5" r="2.5"/><path d="M5 17v3"/><path d="M9 17v2"/><path d="M13 17v2"/>',
  cpu: '<rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6" rx="1"/><path d="M9 2v3"/><path d="M15 2v3"/><path d="M9 19v3"/><path d="M15 19v3"/><path d="M2 9h3"/><path d="M2 15h3"/><path d="M19 9h3"/><path d="M19 15h3"/>',
  motherboard: '<rect x="3" y="3" width="18" height="18" rx="2"/><rect x="7" y="7" width="5" height="5" rx="0.5"/><path d="M15 7h2"/><path d="M15 10h2"/><path d="M7 16h10"/><path d="M7 19h6"/>',
  ram: '<path d="M2 7a1 1 0 0 1 1-1h18a1 1 0 0 1 1 1v3a2 2 0 0 0 0 4v3a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-3a2 2 0 0 0 0-4z"/><path d="M6 10v4"/><path d="M10 10v4"/><path d="M14 10v4"/><path d="M18 10v4"/>',
  ssd: '<rect x="3" y="7" width="18" height="10" rx="1.5"/><path d="M7 7v10"/><circle cx="17" cy="12" r="1"/><path d="M10 11h4"/><path d="M10 13h3"/>',
  cooler: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="1.5"/><path d="M12 10.5c0-3 1-5 3.5-5.5"/><path d="M13.5 12c3 0 5 1 5.5 3.5"/><path d="M12 13.5c0 3-1 5-3.5 5.5"/><path d="M10.5 12c-3 0-5-1-5.5-3.5"/>',
  psu: '<rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="9" cy="12" r="4"/><path d="M9 10v4"/><path d="M7 12h4"/><path d="M16 9h3"/><path d="M16 12h3"/><path d="M16 15h3"/>',
  case: '<rect x="6" y="2" width="12" height="20" rx="1.5"/><path d="M9 5.5h6"/><circle cx="12" cy="14" r="3"/><path d="M12 11v.01"/>',
};

/**
 * Devolve o SVG de um ícone como string.
 * @param {string} name
 * @param {{ size?: number, className?: string, filled?: boolean }} [opts]
 */
export function icon(name, { size = 20, className = "", filled = false } = {}) {
  const body = PATHS[name] || PATHS.info;
  const fill = filled ? "currentColor" : "none";
  return `<svg class="icon ${className}" width="${size}" height="${size}" viewBox="0 0 24 24" fill="${fill}" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${body}</svg>`;
}

/** Troca todo elemento com data-icon="nome" pelo SVG correspondente. */
export function hydrateIcons(root = document) {
  root.querySelectorAll("[data-icon]").forEach((el) => {
    el.innerHTML = icon(el.dataset.icon, { size: Number(el.dataset.size) || 20 });
    el.removeAttribute("data-icon");
  });
}

/**
 * Imagem do produto, nesta ordem de preferência:
 *   1. foto real (static/images)
 *   2. ilustração gerada (static/images/ilustracoes), com o selo "Ilustração"
 *   3. ícone da categoria com a marca
 */
export function productVisual(product, { size = 56 } = {}) {
  if (product.image_url) {
    return `<img src="${escapeHtml(product.image_url)}" alt="${escapeHtml(product.name)}" loading="lazy" class="product-photo">`;
  }
  if (product.illustration_url) {
    return `
      <div class="product-illus">
        <img src="${escapeHtml(product.illustration_url)}" alt="Ilustração de ${escapeHtml(product.name)}" loading="lazy" class="product-illustration">
        <span class="illus-tag">Ilustração</span>
      </div>`;
  }
  return `
    <div class="product-art" data-category="${escapeHtml(product.category)}">
      ${icon(product.category, { size })}
      <span class="product-art-brand">${escapeHtml(product.brand || "")}</span>
    </div>`;
}
