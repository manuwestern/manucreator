import { useEffect, useRef, useState } from 'react';
import { SHAPES, OBJECT_ICONS, shapeDefaults } from '../components/editor/editorCatalog';
import { loadImage } from '../lib/imageStorage';
import { toast } from 'sonner';
import { newId } from '../lib/newId';

export const initialObjects = [
  { id: 'branch', type: 'branch', name: 'Zweig', x: 300, y: 405, scale: 1, rotation: 0, visible: true, locked: false },
  { id: 'text', type: 'text', name: 'Dein Unikat', text: 'Dein Unikat', curve: 35, font: 'Cormorant Garamond', x: 300, y: 304, scale: 1, rotation: 0, visible: true, locked: false },
  { id: 'heart', type: 'heart', name: 'Herz', x: 300, y: 184, scale: 1, rotation: 0, visible: true, locked: false },
];
const STORAGE_KEY = 'manucreator-design-v1';
const imageFields = [['assetId', 'src'], ['cutoutAssetId', 'cutoutSrc']];
function restore() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (Array.isArray(saved) && saved.every(o => o.id && Object.hasOwn(OBJECT_ICONS, o.type))) return saved.map(o => ({ ...shapeDefaults(o.type), ...o }));
  } catch (_) { /* A fresh design remains available when browser storage is unavailable. */ }
  return initialObjects;
}

export const useEditor = () => {
  const [objects, setObjects] = useState(restore);
  const [selectedId, setSelectedId] = useState(() => objects.find(o => o.type === 'text')?.id || objects[0]?.id || null);
  const [past, setPast] = useState([]);
  const [future, setFuture] = useState([]);
  const [saveState, setSaveState] = useState('saved');
  const current = useRef(objects);
  const gesture = useRef(null);
  current.current = objects;
  useEffect(() => {
    let cancelled = false;
    const assets = [...new Set(current.current.flatMap(o => imageFields.map(([asset]) => o[asset]).filter(Boolean)))];
    assets.forEach(async id => {
      try {
        const src = await loadImage(id);
        if (cancelled) { URL.revokeObjectURL(src); return; }
        setObjects(previous => previous.map(o => {
          const patch = Object.fromEntries(imageFields.filter(([asset]) => o[asset] === id).map(([, source]) => [source, src]));
          return Object.keys(patch).length ? { ...o, ...patch } : o;
        }));
      } catch (_) { if (!cancelled) toast.error('Ein gespeichertes Bild konnte nicht geladen werden. Bitte lade es erneut hoch.'); }
    });
    return () => { cancelled = true; };
  }, []);
  useEffect(() => {
    setSaveState('saving');
    const timeout = setTimeout(() => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(objects.map(o => {
          const saved = { ...o };
          imageFields.forEach(([asset, source]) => { if (o[asset]) delete saved[source]; });
          return saved;
        })));
        setSaveState('saved');
      }
      catch (_) { setSaveState('unavailable'); }
    }, 650);
    return () => clearTimeout(timeout);
  }, [objects]);
  const update = (updater, record = true) => {
    const old = current.current;
    const next = typeof updater === 'function' ? updater(old) : updater;
    if (JSON.stringify(old) === JSON.stringify(next)) return;
    if (record) { setPast(p => [...p.slice(-49), old]); setFuture([]); }
    current.current = next;
    setObjects(next);
  };
  const begin = () => { if (!gesture.current) gesture.current = current.current; };
  const end = () => {
    if (gesture.current && JSON.stringify(gesture.current) !== JSON.stringify(current.current)) {
      const snapshot = gesture.current;
      setPast(p => [...p.slice(-49), snapshot]); setFuture([]);
    }
    gesture.current = null;
  };
  const patchObject = (id, patch, record = true) => update(old => old.map(o => o.id === id ? { ...o, ...patch } : o), record);
  const undo = () => {
    if (!past.length) return;
    const prev = past[past.length - 1];
    const old = current.current;
    setFuture(f => [old, ...f]); setPast(p => p.slice(0, -1));
    current.current = prev; setObjects(prev);
  };
  const redo = () => {
    if (!future.length) return;
    const next = future[0];
    const old = current.current;
    setPast(p => [...p, old]); setFuture(f => f.slice(1));
    current.current = next; setObjects(next);
  };
  const add = (type, extra = {}) => {
    const item = { id: `${type}-${newId()}`, type, name: SHAPES.find(s => s.type === type)?.label || { text: 'Dein Text', heart: 'Herz', branch: 'Zweig', image: 'Mein Bild' }[type], x: 300, y: 300, scale: 1, rotation: 0, visible: true, locked: false, ...shapeDefaults(type), ...extra };
    update(old => [...old, item]); setSelectedId(item.id); return item.id;
  };
  const duplicate = () => {
    const source = current.current.find(o => o.id === selectedId);
    if (source) add(source.type, { ...source, id: `${source.type}-${newId()}`, name: `${source.name} Kopie`, x: source.x + 15, y: source.y + 20, locked: false });
  };
  const remove = () => { update(old => old.filter(o => o.id !== selectedId)); setSelectedId(null); };
  const reorder = (id, target) => update(old => {
    const list = [...old]; const index = list.findIndex(o => o.id === id);
    if (index < 0) return old;
    const [item] = list.splice(index, 1);
    list.splice(Math.max(0, Math.min(target, list.length)), 0, item); return list;
  });
  const getObject = id => current.current.find(o => o.id === id);
  return { objects, selectedId, select: setSelectedId, selected: objects.find(o => o.id === selectedId), getObject, saveState, update, patchObject, begin, end, undo, redo, canUndo: !!past.length, canRedo: !!future.length, add, duplicate, remove, reorder };
};