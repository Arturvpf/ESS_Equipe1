const BASE_URL = "http://localhost:8000";

async function request(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...options.headers };

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (res.status === 204) return null;

  const body = await res.json().catch(() => ({ detail: "Erro desconhecido" }));
  if (!res.ok) throw new Error(body.detail || "Erro na requisição");
  return body;
}

export const api = {
  get:    (path)        => request(path),
  post:   (path, body)  => request(path, { method: "POST",   body: JSON.stringify(body) }),
  put:    (path, body)  => request(path, { method: "PUT",    body: JSON.stringify(body) }),
  patch:  (path, body)  => request(path, { method: "PATCH",  body: JSON.stringify(body) }),
  delete: (path)        => request(path, { method: "DELETE" }),
};
