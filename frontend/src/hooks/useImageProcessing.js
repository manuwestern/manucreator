import { useEffect, useRef, useState } from 'react';
import { toast } from 'sonner';
import { storeImage } from '../lib/imageStorage';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const useImageProcessing = editor => {
  const [jobs, setJobs] = useState({});
  const tasks = useRef(new Map());
  const mounted = useRef(true);
  useEffect(() => {
    mounted.current = true;
    const active = tasks.current;
    return () => { mounted.current = false; active.forEach(job => { job.cancelled = true; job.controller.abort(); clearTimeout(job.timer); }); };
  }, []);
  const cancel = id => {
    const job = tasks.current.get(id);
    if (job) { job.cancelled = true; job.controller.abort(); clearTimeout(job.timer); tasks.current.delete(id); }
    if (mounted.current) setJobs(previous => ({ ...previous, [id]: { pending: false, error: null } }));
  };
  const removeBackground = async id => {
    const object = editor.getObject(id);
    if (!object || object.type !== 'image' || object.locked || !object.src || tasks.current.has(id)) return;
    if (object.cutoutSrc) {
      editor.patchObject(id, { backgroundRemoved: true, imageView: 'engraving' });
      setJobs(previous => ({ ...previous, [id]: { pending: false, error: null } }));
      return;
    }
    const job = { controller: new AbortController(), cancelled: false };
    tasks.current.set(id, job);
    setJobs(previous => ({ ...previous, [id]: { pending: true, error: null } }));
    job.timer = setTimeout(() => job.controller.abort(), 45000);
    try {
      if (!BACKEND_URL) throw new Error('Die Bildverarbeitung ist noch nicht eingerichtet.');
      const original = await (await fetch(object.src, { signal: job.controller.signal })).blob();
      const form = new FormData(); form.append('image', original, object.name || 'foto.png');
      const response = await fetch(`${BACKEND_URL}/api/images/remove-background`, { method: 'POST', body: form, signal: job.controller.signal });
      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(typeof body?.detail === 'string' ? body.detail : 'Der Hintergrund konnte nicht entfernt werden. Bitte versuche es erneut.');
      }
      const cutout = await response.blob();
      if (job.cancelled || !mounted.current || !editor.getObject(id)) return;
      let asset;
      try { asset = await storeImage(cutout); }
      catch (_) { throw new Error('Die Freistellung konnte nicht auf diesem Gerät gespeichert werden. Bitte prüfe den verfügbaren Speicherplatz.'); }
      const currentObject = editor.getObject(id);
      if (job.cancelled || !mounted.current || !currentObject || currentObject.locked) {
        URL.revokeObjectURL(asset.src);
        return;
      }
      editor.patchObject(id, { cutoutAssetId: asset.assetId, cutoutSrc: asset.src, backgroundRemoved: true, imageView: 'engraving' });
      toast.success('Hintergrund entfernt. Dein Original bleibt erhalten.');
      setJobs(previous => ({ ...previous, [id]: { pending: false, error: null } }));
    } catch (error) {
      if (job.cancelled || !mounted.current) return;
      const message = error.name === 'AbortError' ? 'Die Freistellung hat zu lange gedauert. Bitte versuche es erneut.' : error instanceof TypeError ? 'Keine Verbindung zur Bildverarbeitung. Dein Original bleibt unverändert; bitte versuche es erneut.' : error.message;
      setJobs(previous => ({ ...previous, [id]: { pending: false, error: message } }));
    } finally {
      clearTimeout(job.timer);
      if (tasks.current.get(id) === job) {
        tasks.current.delete(id);
        if (mounted.current) setJobs(previous => ({ ...previous, [id]: { ...previous[id], pending: false } }));
      }
    }
  };
  const reset = id => { cancel(id); if (!editor.getObject(id)?.locked) editor.patchObject(id, { backgroundRemoved: false, imageView: 'engraving' }); };
  return { jobs, removeBackground, cancel, reset };
};