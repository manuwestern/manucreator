import { downloadFrameSheet } from './frameDownloads';

export const HERO_FRAMES = 241;
export const FRAMES_PER_SHEET = 8;
const SHEETS = Math.ceil(HERO_FRAMES / FRAMES_PER_SHEET);
const COLUMNS = 4;

// Keep compressed sheets, not 241 decoded images, in memory. Only three sheets
// are decoded at once (~28 MB desktop), and requests prioritize the scroll target.
export const createFrameLoader = (mobile, onAvailable, onFailure) => {
  const width = mobile ? 552 : 736;
  const height = mobile ? 300 : 400;
  const variant = mobile ? 'mobile' : 'desktop';
  const blobs = new Map();
  const decoded = new Map();
  const loading = new Map();
  const decoding = new Set();
  const failures = new Map();
  const objectUrls = new Set();
  const controller = new AbortController();
  let target = 0;
  let disposed = false;

  const decode = index => {
    if (disposed || decoded.has(index) || decoding.has(index) || !blobs.has(index)) return;
    decoding.add(index);
    const url = URL.createObjectURL(blobs.get(index));
    objectUrls.add(url);
    const image = new Image();
    const release = () => { URL.revokeObjectURL(url); objectUrls.delete(url); decoding.delete(index); };
    image.onload = () => {
      release();
      if (disposed) return;
      decoded.set(index, image);
      while (decoded.size > 3) {
        const oldest = [...decoded.keys()].find(key => key !== target);
        decoded.delete(oldest);
      }
      onAvailable();
    };
    image.onerror = () => { release(); if (!disposed && index === target) onFailure(); };
    image.src = url;
  };

  const request = index => {
    const task = downloadFrameSheet(`/media/hero-sequence/${variant}-${String(index).padStart(2, '0')}.webp`, controller.signal)
      .then(blob => {
        if (disposed) return;
        blobs.set(index, blob);
        if (Math.abs(index - target) <= 1) decode(index);
      })
      .catch(error => {
        if (disposed || error.name === 'AbortError') return;
        failures.set(index, (failures.get(index) || 0) + 1);
        if (index === target && failures.get(index) >= 2) onFailure();
      })
      .finally(() => { loading.delete(index); if (!disposed) pump(); });
    loading.set(index, task);
  };

  const pump = () => {
    if (disposed) return;
    const priorities = [...new Set([target, target + 1, target - 1, ...Array.from({ length: SHEETS }, (_, i) => i)])];
    for (const index of priorities) {
      if (index < 0 || index >= SHEETS || blobs.has(index) || loading.has(index) || (failures.get(index) || 0) >= 2) continue;
      // A freshly requested scroll target can bypass the two background requests.
      if (loading.size >= 2 && (index !== target || loading.size >= 3)) break;
      request(index);
    }
  };

  return {
    width,
    height,
    setTarget(frame) {
      target = Math.floor(frame / FRAMES_PER_SHEET);
      if ((failures.get(target) || 0) >= 2) { onFailure(); return; }
      decode(target);
      pump();
    },
    draw(context, frame) {
      const sheet = Math.floor(frame / FRAMES_PER_SHEET);
      const image = decoded.get(sheet);
      if (!image) return false;
      decoded.delete(sheet);
      decoded.set(sheet, image);
      const tile = frame % FRAMES_PER_SHEET;
      context.drawImage(image, (tile % COLUMNS) * width, Math.floor(tile / COLUMNS) * height, width, height, 0, 0, width, height);
      return true;
    },
    dispose() {
      disposed = true;
      controller.abort();
      objectUrls.forEach(url => URL.revokeObjectURL(url));
      objectUrls.clear(); blobs.clear(); decoded.clear();
    },
  };
};