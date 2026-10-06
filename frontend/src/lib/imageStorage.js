import { newId } from './newId';

// Keep uploaded originals outside localStorage's small text quota.
const DATABASE = 'manucreator-assets';
const STORE = 'images';
function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DATABASE, 1);
    request.onupgradeneeded = () => request.result.createObjectStore(STORE);
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}
export async function storeImage(file) {
  const db = await openDatabase();
  const id = newId();
  try {
    await new Promise((resolve, reject) => {
      const transaction = db.transaction(STORE, 'readwrite');
      transaction.objectStore(STORE).put(file, id);
      transaction.oncomplete = resolve;
      transaction.onerror = () => reject(transaction.error);
      transaction.onabort = () => reject(transaction.error);
    });
    return { assetId: id, src: URL.createObjectURL(file) };
  } finally { db.close(); }
}
export async function loadImage(id) {
  const db = await openDatabase();
  try {
    const blob = await new Promise((resolve, reject) => {
      const request = db.transaction(STORE, 'readonly').objectStore(STORE).get(id);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    if (!blob) throw new Error('Bild nicht gefunden');
    return URL.createObjectURL(blob);
  } finally { db.close(); }
}