/**
 * NextNode — Utilitários compartilhados entre os módulos.
 */

// Precisam bater com PIX_DISCOUNT e MAX_INSTALLMENTS do app.py
export const PIX_DISCOUNT = 0.05;
export const MAX_INSTALLMENTS = 10;

const BRL = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

export function formatCurrency(value) {
  return BRL.format(value);
}

export function roundMoney(value) {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

/**
 * Escapa texto antes de colocá-lo dentro de HTML montado com template string.
 * Sem isso, um "<" vindo dos dados viraria uma tag de verdade.
 */
export function escapeHtml(value) {
  const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
  return String(value ?? "").replace(/[&<>"']/g, (c) => map[c]);
}

/** Lê do localStorage sem quebrar quando ele está bloqueado (aba anônima etc.). */
export function readStorage(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export function writeStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* sem armazenamento disponível: segue só em memória */
  }
}

/**
 * Mostra um aviso temporário no canto da tela.
 * Usa textContent, nunca innerHTML: a mensagem pode ter texto do usuário.
 * @param {string} message
 * @param {"info"|"success"|"error"} [type]
 */
export function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.setAttribute("role", type === "error" ? "alert" : "status");

  const text = document.createElement("span");
  text.textContent = message;

  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.textContent = "×";
  closeBtn.setAttribute("aria-label", "Fechar aviso");
  closeBtn.addEventListener("click", () => toast.remove());

  toast.append(text, closeBtn);
  container.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add("show"));
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
