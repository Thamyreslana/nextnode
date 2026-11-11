/**
 * NextNode — API Client
 * Funções JavaScript para consumir a API Flask do backend.
 */

const API_BASE = "";   // mesmo origin, Flask serve tudo

/**
 * Requisição genérica com tratamento de erro.
 * @param {string} endpoint
 * @param {RequestInit} [options]
 */
async function apiFetch(endpoint, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || err.message || `HTTP ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`[NextNode API] Erro em ${endpoint}:`, error.message);
    throw error;
  }
}

/** Busca todas as categorias (com a contagem de produtos) */
export async function fetchCategories() {
  const data = await apiFetch("/api/categories");
  return data.categories;
}

/**
 * Busca produtos com filtros opcionais.
 * @param {{ category?: string, search?: string, featured?: boolean,
 *           minPrice?: number, maxPrice?: number, sort?: string, limit?: number }} filters
 */
export async function fetchProducts(filters = {}) {
  const params = new URLSearchParams();
  if (filters.category) params.set("category", filters.category);
  if (filters.search)   params.set("search", filters.search);
  if (filters.featured) params.set("featured", "true");
  if (filters.minPrice != null) params.set("min_price", filters.minPrice);
  if (filters.maxPrice != null) params.set("max_price", filters.maxPrice);
  if (filters.sort)     params.set("sort", filters.sort);
  if (filters.limit)    params.set("limit", filters.limit);

  const query = params.toString() ? `?${params}` : "";
  const data  = await apiFetch(`/api/products${query}`);
  return data.products;
}

/**
 * Busca um produto específico por ID.
 * @param {number} id
 */
export async function fetchProduct(id) {
  return await apiFetch(`/api/products/${id}`);
}

/** Busca produtos em destaque */
export async function fetchFeatured() {
  const data = await apiFetch("/api/featured");
  return data.products;
}

/** Busca a build sugerida (peças + total) */
export async function fetchFeaturedBuild() {
  return await apiFetch("/api/builds/featured");
}

/** Busca as ofertas relâmpago */
export async function fetchDeals() {
  const data = await apiFetch("/api/deals");
  return data.deals;
}

/**
 * Calcula o frete (simulado) para um CEP.
 * @param {string} cep
 * @param {number} subtotal
 */
export async function fetchShipping(cep, subtotal) {
  return await apiFetch("/api/shipping", {
    method: "POST",
    body: JSON.stringify({ cep, subtotal }),
  });
}

/** Quantos produtos já têm foto para a busca por imagem */
export async function fetchImageSearchStatus() {
  return await apiFetch("/api/search/image/status");
}

/**
 * Envia uma imagem e recebe os produtos mais parecidos.
 * Usa FormData (multipart) em vez de JSON, por isso não passa pelo apiFetch:
 * o navegador precisa montar o cabeçalho Content-Type sozinho.
 * @param {File|Blob} file
 */
export async function searchByImage(file) {
  const body = new FormData();
  body.append("image", file, file.name || "imagem");
  const res = await fetch(`${API_BASE}/api/search/image`, { method: "POST", body });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

/**
 * Cadastra e-mail na newsletter.
 * @param {string} email
 */
export async function subscribeNewsletter(email) {
  return await apiFetch("/api/newsletter", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}
