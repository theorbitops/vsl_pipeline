// Serviço de busca de VSLs
// AGORA: chama a API real do FastAPI em http://localhost:8000/api/search

export async function searchVsls(term) {
  const query = term.trim();

  if (!query) {
    return [];
  }

  const url = `http://localhost:8000/api/search?q=${encodeURIComponent(query)}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Erro ao buscar VSLs: ${response.status}`);
  }

  const data = await response.json();

  // Garantimos que sempre retornamos um array
  return Array.isArray(data.results) ? data.results : [];
}
