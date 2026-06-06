// ============================================================
// LabManager — camada de API: fetch + autenticação via sessão
// ============================================================

function getCsrfToken() {
  const m = document.cookie.match(/csrftoken=([^;]+)/);
  return m ? m[1] : "";
}

async function apiFetch(url, options = {}) {
  const headers = { "Content-Type": "application/json", "X-CSRFToken": getCsrfToken(), ...(options.headers || {}) };
  const res = await fetch(url, { credentials: "include", ...options, headers });
  if (!res.ok) {
    let detail = "Erro na requisição.";
    try {
      const body = await res.json();
      detail = body.detail || (Array.isArray(body.non_field_errors) ? body.non_field_errors[0] : null) || detail;
    } catch (_) {}
    throw new Error(detail);
  }
  return res.json();
}

async function apiLogin(email, password) {
  try {
    // Primeiro garante que o cookie CSRF existe
    await fetch("/api/auth/csrf/", { credentials: "include" });
    const data = await apiFetch("/api/auth/login/", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    return { ok: true, role: data.role, user: data.user };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

async function apiLogout() {
  try {
    await apiFetch("/api/auth/logout/", { method: "POST" });
  } catch (_) {}
}

async function apiMe() {
  return apiFetch("/api/auth/me/");
}

async function apiFetchInit() {
  const data = await apiFetch("/api/init/");

  // Sobrescreve os globais com dados reais vindos do servidor.
  // Os componentes já lêem essas variáveis globais; não precisam ser reescritos.
  Object.assign(window, {
    CATEGORIAS: data.categorias,
    UNIDADES: data.unidades,
    LOCALIZACOES: data.localizacoes,
    ITENS: data.itens,
    EQUIPAMENTOS: data.equipamentos,
    ESTOQUE: data.estoque,
    MOVIMENTACOES: data.movimentacoes,
    REQUISICOES: data.requisicoes,
    RESERVAS: data.reservas,
    ORDENS: data.ordens,
    MANUTENCOES: data.manutencoes,
    INVENTARIOS: data.inventarios,
    INVENTARIO_LINHAS: data.inventario_linhas,
    AUDITORIA: data.auditoria,
  });

  // Recomputa campos derivados no estoque (espelha data.jsx)
  window.ESTOQUE.forEach((e) => {
    e.livre = parseFloat(e.livre);
    e.abaixoAlerta = e.abaixoAlerta;
  });
  window.INVENTARIO_LINHAS.forEach((l) => {
    l.diff = l.diff !== null ? Number(l.diff) : null;
  });

  return data;
}

async function apiAprovarRequisicao(id) {
  return apiFetch(`/api/requisicoes/${id}/aprovar/`, { method: "POST" });
}

async function apiRejeitarRequisicao(id, obs) {
  return apiFetch(`/api/requisicoes/${id}/rejeitar/`, {
    method: "POST",
    body: JSON.stringify({ obs: obs || "" }),
  });
}

async function apiAtenderRequisicaoItem(reqId, itemId) {
  return apiFetch(`/api/requisicoes/${reqId}/atender/`, {
    method: "POST",
    body: JSON.stringify({ item_id: itemId }),
  });
}

async function apiConfirmarReserva(id) {
  return apiFetch(`/api/reservas/${id}/confirmar/`, { method: "POST" });
}

Object.assign(window, {
  API: {
    login: apiLogin,
    logout: apiLogout,
    me: apiMe,
    fetchInit: apiFetchInit,
    aprovarRequisicao: apiAprovarRequisicao,
    rejeitarRequisicao: apiRejeitarRequisicao,
    atenderRequisicaoItem: apiAtenderRequisicaoItem,
    confirmarReserva: apiConfirmarReserva,
    fetch: apiFetch,
  },
});
