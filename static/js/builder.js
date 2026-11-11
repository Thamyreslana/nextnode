/**
 * NextNode — Montador de PC
 * Escolha uma peça por categoria e o montador confere a compatibilidade:
 *   - soquete do processador × soquete da placa-mãe
 *   - tipo de memória (DDR4/DDR5) × placa-mãe
 *   - calor do processador × capacidade do cooler
 *   - consumo estimado × potência da fonte
 *
 * As funções de regra (checkBuild, estimatePower...) não mexem na tela,
 * então dá para testá-las sozinhas.
 */

import { icon } from "./icons.js";
import {
  formatCurrency, escapeHtml, roundMoney, showToast,
  readStorage, writeStorage, MAX_INSTALLMENTS,
} from "./utils.js";
import { addToCart, openCart } from "./cart.js";

export const SLOTS = [
  { id: "cpu",         label: "Processador",    lower: "processador" },
  { id: "motherboard", label: "Placa-mãe",      lower: "placa-mãe" },
  { id: "ram",         label: "Memória RAM",    lower: "memória RAM" },
  { id: "gpu",         label: "Placa de vídeo", lower: "placa de vídeo" },
  { id: "ssd",         label: "Armazenamento",  lower: "armazenamento" },
  { id: "cooler",      label: "Refrigeração",   lower: "refrigeração" },
  { id: "psu",         label: "Fonte",          lower: "fonte" },
  { id: "case",        label: "Gabinete",       lower: "gabinete" },
];

const BUILD_KEY = "nextnode_build";
const BASE_POWER = 75;   // placa-mãe, memória, SSD e fans (estimativa)
const PSU_MARGIN = 1.25; // folga de 25% para picos de consumo e envelhecimento da fonte

// ─── Regras (funções puras) ───────────────────────────────────────────────────

/** Consumo estimado em watts. */
export function estimatePower(parts) {
  const cpu = parts.cpu?.compat?.power ?? 0;
  const gpu = parts.gpu?.compat?.power ?? 0;
  return cpu + gpu + BASE_POWER;
}

/** Potência de fonte recomendada, arredondada para múltiplos de 50W. */
export function recommendedPsu(power) {
  return Math.ceil((power * PSU_MARGIN) / 50) * 50;
}

/**
 * Confere a build e devolve uma lista de mensagens.
 * @returns {{ level: "ok"|"warn"|"error"|"info", text: string }[]}
 */
export function checkBuild(parts) {
  const { cpu, motherboard: mb, ram, gpu, cooler, psu } = parts;
  const checks = [];

  if (cpu && mb) {
    const a = cpu.compat.socket;
    const b = mb.compat.socket;
    checks.push(
      a === b
        ? { level: "ok", text: `Processador e placa-mãe usam o mesmo soquete (${a}).` }
        : { level: "error", text: `O processador usa soquete ${a}, mas a placa-mãe é ${b}. Ele não encaixa.` }
    );
  }

  if (ram && mb) {
    const a = ram.compat.memory;
    const b = mb.compat.memory;
    checks.push(
      a === b
        ? { level: "ok", text: `Memória ${a} compatível com a placa-mãe.` }
        : { level: "error", text: `A memória é ${a}, mas a placa-mãe só aceita ${b}. Os encaixes são diferentes.` }
    );
  }

  if (cpu && cooler) {
    const heat = cpu.compat.power;
    const capacity = cooler.compat.max_tdp;
    checks.push(
      capacity >= heat
        ? { level: "ok", text: `O cooler dá conta do processador (${heat}W de ${capacity}W).` }
        : { level: "warn", text: `O processador pode chegar a ${heat}W e o cooler dissipa ${capacity}W. Ele vai esquentar e perder desempenho.` }
    );
  }

  if (psu && (cpu || gpu)) {
    const power = estimatePower(parts);
    const recommended = recommendedPsu(power);
    const watts = psu.compat.watts;
    if (watts < power) {
      checks.push({ level: "error", text: `A fonte de ${watts}W é menor que o consumo estimado (${power}W). O PC pode desligar sozinho.` });
    } else if (watts < recommended) {
      checks.push({ level: "warn", text: `A fonte de ${watts}W funciona, mas o ideal é ${recommended}W ou mais para ter folga.` });
    } else {
      checks.push({ level: "ok", text: `Fonte de ${watts}W com folga para o consumo estimado de ${power}W.` });
    }
  }

  const missing = SLOTS.filter((s) => !parts[s.id]).map((s) => s.lower);
  if (missing.length === SLOTS.length) {
    checks.push({ level: "info", text: "Escolha as peças ao lado. A compatibilidade é conferida a cada escolha." });
  } else if (missing.length) {
    checks.push({ level: "info", text: `Falta escolher: ${missing.join(", ")}.` });
  }

  return checks;
}

/**
 * Diz se um produto é compatível com as peças já escolhidas
 * (usado para marcar as opções incompatíveis nos selects).
 * @returns {string|null} motivo da incompatibilidade, ou null se for compatível
 */
export function incompatibilityReason(product, parts) {
  const c = product.compat || {};
  const { cpu, motherboard: mb, ram } = parts;
  switch (product.category) {
    case "cpu":
      return mb && c.socket !== mb.compat.socket ? `soquete ${c.socket}` : null;
    case "motherboard":
      if (cpu && c.socket !== cpu.compat.socket) return `soquete ${c.socket}`;
      if (ram && c.memory !== ram.compat.memory) return `só ${c.memory}`;
      return null;
    case "ram":
      return mb && c.memory !== mb.compat.memory ? c.memory : null;
    default:
      return null;
  }
}

// ─── Estado e tela ────────────────────────────────────────────────────────────

let catalog = [];
let parts = {};

function saveBuild() {
  const ids = Object.fromEntries(Object.entries(parts).map(([slot, p]) => [slot, p.id]));
  writeStorage(BUILD_KEY, ids);
}

function restoreBuild() {
  const ids = readStorage(BUILD_KEY, {});
  parts = {};
  for (const [slot, id] of Object.entries(ids || {})) {
    const product = catalog.find((p) => p.id === id && p.category === slot);
    if (product) parts[slot] = product;
  }
}

export function initBuilder(products) {
  catalog = products;
  restoreBuild();

  const slotsEl = document.getElementById("builder-slots");
  slotsEl?.addEventListener("change", (e) => {
    const select = e.target.closest("select[data-slot]");
    if (!select) return;
    const product = catalog.find((p) => p.id === Number(select.value));
    if (product) parts[select.dataset.slot] = product;
    else delete parts[select.dataset.slot];
    saveBuild();
    render();
  });

  document.getElementById("builder-summary")?.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-builder]");
    if (!btn) return;
    if (btn.dataset.builder === "clear") {
      parts = {};
      saveBuild();
      render();
    }
    if (btn.dataset.builder === "add") addBuildToCart();
  });

  render();
}

/** Coloca um produto no montador (ex.: botão "Usar no montador" do detalhe). */
export function setBuildPart(product) {
  parts[product.category] = product;
  saveBuild();
  render();
  const slot = SLOTS.find((s) => s.id === product.category);
  showToast(`${product.name} entrou no montador como ${slot?.lower ?? "peça"}.`, "success");
}

/** Substitui a build inteira (ex.: build sugerida do topo da página). */
export function loadBuild(products) {
  parts = {};
  products.forEach((p) => {
    const full = catalog.find((c) => c.id === p.id) || p;
    parts[full.category] = full;
  });
  saveBuild();
  render();
  document.getElementById("montador")?.scrollIntoView({ behavior: "smooth" });
}

function addBuildToCart() {
  const chosen = SLOTS.map((s) => parts[s.id]).filter(Boolean);
  chosen.forEach((p) => addToCart(p, { silent: true }));
  showToast(`${chosen.length} ${chosen.length === 1 ? "peça foi" : "peças foram"} para o carrinho.`, "success");
  openCart();
}

function render() {
  renderSlots();
  renderSummary();
}

function renderSlots() {
  const el = document.getElementById("builder-slots");
  if (!el) return;

  el.innerHTML = SLOTS.map((slot) => {
    const chosen = parts[slot.id];
    const options = catalog
      .filter((p) => p.category === slot.id)
      .sort((a, b) => a.price - b.price)
      .map((p) => {
        const reason = incompatibilityReason(p, parts);
        const label = `${p.name} · ${formatCurrency(p.pix_price)}${reason ? ` (incompatível: ${reason})` : ""}`;
        return `<option value="${p.id}" ${chosen?.id === p.id ? "selected" : ""}>${escapeHtml(label)}</option>`;
      })
      .join("");

    const problem = chosen && incompatibilityReason(chosen, parts);
    return `
      <div class="slot ${chosen ? "is-filled" : ""} ${problem ? "is-error" : ""}">
        <span class="slot-icon">${icon(slot.id, { size: 22 })}</span>
        <label class="slot-label" for="slot-${slot.id}">${slot.label}</label>
        <select id="slot-${slot.id}" class="select" data-slot="${slot.id}">
          <option value="">Escolher ${slot.lower}…</option>
          ${options}
        </select>
      </div>`;
  }).join("");
}

function renderSummary() {
  const el = document.getElementById("builder-summary");
  if (!el) return;

  const chosen = SLOTS.map((s) => parts[s.id]).filter(Boolean);
  const checks = checkBuild(parts);
  const hasError = checks.some((c) => c.level === "error");

  const total = roundMoney(chosen.reduce((s, p) => s + p.price, 0));
  const pix = roundMoney(chosen.reduce((s, p) => s + p.pix_price, 0));

  const power = estimatePower(parts);
  const psuWatts = parts.psu?.compat.watts;
  const meter = (parts.cpu || parts.gpu)
    ? `
      <div class="power">
        <div class="power-head">
          <span>${icon("bolt", { size: 16 })} Consumo estimado</span>
          <strong>${power}W</strong>
        </div>
        <div class="power-bar" role="img" aria-label="${psuWatts ? `${power}W de ${psuWatts}W da fonte` : `${power}W`}">
          <span style="width:${psuWatts ? Math.min(100, (power / psuWatts) * 100) : 0}%"></span>
        </div>
        <p class="note">${psuWatts ? `Fonte escolhida: ${psuWatts}W. ` : ""}Recomendado: ${recommendedPsu(power)}W ou mais.</p>
      </div>`
    : "";

  el.innerHTML = `
    <h3 class="summary-title">Resumo da build</h3>
    <ul class="checks">
      ${checks.map((c) => `<li class="check check-${c.level}">${icon(c.level, { size: 18 })}<span>${escapeHtml(c.text)}</span></li>`).join("")}
    </ul>
    ${meter}
    <div class="summary-total">
      <span>${chosen.length} de ${SLOTS.length} peças</span>
      <strong>${formatCurrency(pix)}</strong>
      <small>no Pix · ou ${formatCurrency(total)} em ${MAX_INSTALLMENTS}x de ${formatCurrency(total / MAX_INSTALLMENTS)}</small>
    </div>
    <button type="button" class="btn btn-primary btn-block" data-builder="add" ${chosen.length === 0 || hasError ? "disabled" : ""}>
      ${icon("cart", { size: 18 })} ${hasError ? "Resolva as incompatibilidades" : "Adicionar build ao carrinho"}
    </button>
    ${chosen.length ? `<button type="button" class="btn btn-link" data-builder="clear">Limpar montador</button>` : ""}`;
}
