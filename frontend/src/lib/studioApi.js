const BASE = `${process.env.REACT_APP_BACKEND_URL}/api/studio`;
const KEY = 'manucreator-studio-guest-v1';
let sessionPromise;
const readSession = () => { try { return JSON.parse(localStorage.getItem(KEY) || 'null'); } catch { return null; } };
const detail = data => typeof data?.detail === 'string' ? data.detail : Array.isArray(data?.detail) ? 'Bitte überprüfe deine Angaben.' : 'Die Verbindung konnte nicht hergestellt werden. Bitte erneut versuchen.';

async function session(force = false) {
  const saved = readSession();
  if (!force && saved?.token && saved.until > Date.now() + 15000) return saved.token;
  if (sessionPromise) return sessionPromise;
  sessionPromise = (async () => {
    let response = await fetch(`${BASE}/session`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(saved?.refresh_token ? { refresh_token: saved.refresh_token } : {}) });
    if (response.status === 401 && saved) {
      localStorage.removeItem(KEY); localStorage.removeItem('manucreator-studio-design');
      response = await fetch(`${BASE}/session`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
    }
    const data = await response.json();
    if (!response.ok) throw new Error(detail(data));
    localStorage.setItem(KEY, JSON.stringify({ ...data, until: Date.now() + data.expires_in * 1000 }));
    return data.token;
  })().finally(() => { sessionPromise = null; });
  return sessionPromise;
}

export async function studioApi(path, { method = 'GET', body, blob = false, raw = false } = {}, retry = true) {
  const token = await session();
  const multipart = body instanceof FormData;
  const response = await fetch(`${BASE}${path}`, { method, headers: { Authorization: `Bearer ${token}`, ...(!multipart && body !== undefined ? { 'Content-Type': 'application/json' } : {}) }, body: body === undefined ? undefined : multipart ? body : JSON.stringify(body) });
  if (response.status === 401 && retry) { await session(true); return studioApi(path, { method, body, blob, raw }, false); }
  if (!response.ok) { const data = await response.json().catch(() => ({})); throw new Error(detail(data)); }
  return raw ? response : blob ? response.blob() : response.json();
}

export const price = cents => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(cents / 100);
export const emptyDesign = product_id => ({ product_id, template: 'text', text: 'Unser Lieblingsplatz', subtitle: 'Mit Liebe', font: 'classic', size: 'medium', position: 'center', asset_id: null, zoom: 1, focal_x: 0, focal_y: 0 });
export const configKey = design => JSON.stringify(design);
export const productImage = image => image?.startsWith('/api/') ? `${process.env.REACT_APP_BACKEND_URL}${image}` : image;