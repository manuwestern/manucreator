const BASE = `${process.env.REACT_APP_BACKEND_URL}/api/admin`;
let refreshing;
export async function adminApi(path, { method = 'GET', body, blob = false } = {}, retry = true) {
  const multipart = body instanceof FormData;
  const response = await fetch(BASE + path, { method, credentials: 'include', headers: !multipart && body !== undefined ? { 'Content-Type': 'application/json' } : {}, body: body === undefined ? undefined : multipart ? body : JSON.stringify(body) });
  if (response.status === 401 && retry && !path.startsWith('/auth/login')) {
    if (!refreshing) refreshing = fetch(BASE + '/auth/refresh', { method: 'POST', credentials: 'include' }).finally(() => { refreshing = null; });
    const fresh = await refreshing;
    if (fresh.ok) return adminApi(path, { method, body, blob }, false);
  }
  if(response.ok&&blob)return response.blob();
  const data = await response.json();
  if (!response.ok) { const error = new Error(typeof data.detail === 'string' ? data.detail : 'Bitte prüfe deine Eingaben und die Gravurfläche.'); error.status = response.status; throw error; }
  return data;
}