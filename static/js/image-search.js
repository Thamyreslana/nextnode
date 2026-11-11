/**
 * NextNode — Busca por imagem
 * Janela onde a pessoa escolhe, arrasta ou cola uma imagem.
 * A comparação acontece no backend (image_search.py). Este módulo só
 * cuida da interface e entrega os resultados para quem chamou.
 */

import { searchByImage, fetchImageSearchStatus } from "./api.js";

const MAX_BYTES = 8 * 1024 * 1024;   // igual ao MAX_CONTENT_LENGTH do app.py
const ACCEPTED = ["image/jpeg", "image/png", "image/webp"];

let selectedFile = null;
let previewUrl = null;
let catalogHasPhotos = true;

/**
 * @param {{ onResults: (r: { results: {id:number, similarity:number}[], previewUrl: string, indexed: number, total: number }) => void }} opts
 */
export function initImageSearch({ onResults }) {
  const dialog   = document.getElementById("image-search-dialog");
  const openBtn  = document.getElementById("image-search-btn");
  const form     = document.getElementById("image-search-form");
  const input    = document.getElementById("image-input");
  const dropzone = document.getElementById("image-dropzone");
  const submit   = document.getElementById("image-search-submit");
  const change   = document.getElementById("image-search-change");
  if (!dialog || !openBtn || !form || !input || !dropzone || !submit) return;

  openBtn.addEventListener("click", () => {
    showError("");
    dialog.showModal();
    loadStatus();
  });

  // Fechar: botão X ou clique no fundo escuro
  dialog.addEventListener("click", (e) => {
    if (e.target === dialog || e.target.closest("[data-close-image-search]")) dialog.close();
  });

  input.addEventListener("change", () => {
    if (input.files[0]) selectFile(input.files[0]);
  });
  change?.addEventListener("click", () => input.click());

  // Arrastar e soltar
  ["dragenter", "dragover"].forEach((type) =>
    dropzone.addEventListener(type, (e) => {
      e.preventDefault();
      dropzone.classList.add("is-dragging");
    })
  );
  ["dragleave", "drop"].forEach((type) =>
    dropzone.addEventListener(type, () => dropzone.classList.remove("is-dragging"))
  );
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    const file = e.dataTransfer?.files?.[0];
    if (file) selectFile(file);
  });

  // Colar (Ctrl+V) uma imagem copiada, enquanto a janela estiver aberta
  document.addEventListener("paste", (e) => {
    if (!dialog.open) return;
    const file = [...(e.clipboardData?.files || [])].find((f) => f.type.startsWith("image/"));
    if (file) {
      e.preventDefault();
      selectFile(file);
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    const original = submit.innerHTML;
    submit.disabled = true;
    submit.textContent = "Comparando…";
    showError("");

    try {
      const data = await searchByImage(selectedFile);
      dialog.close();
      onResults({
        results: data.results,
        previewUrl,
        indexed: data.indexed,
        total: data.total_products,
      });
    } catch (err) {
      showError(err.message);
    } finally {
      submit.innerHTML = original;
      updateSubmit();
    }
  });
}

function selectFile(file) {
  if (!ACCEPTED.includes(file.type)) {
    showError("Formato não suportado. Use JPG, PNG ou WEBP.");
    return;
  }
  if (file.size > MAX_BYTES) {
    showError("Arquivo grande demais. O limite é 8 MB.");
    return;
  }

  showError("");
  selectedFile = file;

  // URL temporária só para mostrar a prévia; a anterior é liberada da memória
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = URL.createObjectURL(file);

  const preview = document.getElementById("image-preview");
  preview.src = previewUrl;
  preview.hidden = false;
  document.getElementById("image-dropzone").classList.add("has-image");
  document.getElementById("image-search-change").hidden = false;
  updateSubmit();
}

async function loadStatus() {
  const el = document.getElementById("image-search-status");
  if (!el) return;
  try {
    const s = await fetchImageSearchStatus();
    catalogHasPhotos = s.indexed > 0;
    el.textContent = catalogHasPhotos
      ? `A busca compara com os ${s.indexed} de ${s.total} produtos que já têm foto.`
      : "Nenhum produto tem foto cadastrada ainda. Adicione as fotos em static/images para a busca funcionar.";
    el.classList.toggle("field-error", !catalogHasPhotos);
  } catch {
    el.textContent = "";
  }
  updateSubmit();
}

function updateSubmit() {
  const submit = document.getElementById("image-search-submit");
  if (submit) submit.disabled = !selectedFile || !catalogHasPhotos;
}

function showError(message) {
  const el = document.getElementById("image-search-error");
  if (el) el.textContent = message;
}
