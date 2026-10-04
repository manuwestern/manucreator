import { useEffect, useState } from 'react';
import { productImage } from '@/lib/studioApi';
import { fonts } from '@/lib/studioLayers';

export const useCanvasAssets = (image, assetUrl) => {
  const [state, setState] = useState({ blank: null, asset: null, error: '', loaded: false });
  useEffect(() => {
    let alive = true;
    setState({ blank: null, asset: null, error: '', loaded: false });
    const load = src => new Promise((resolve, reject) => { if (!src) return resolve(null); const img = new Image(); img.crossOrigin = 'anonymous'; img.onload = () => resolve(img); img.onerror = () => reject(new Error('Das Bild konnte nicht geladen werden.')); img.src = src; });
    Promise.all([load(productImage(image)), load(assetUrl), ...fonts.map(([, , f]) => document.fonts.load(`32px ${f}`))]).then(([blank, asset]) => { if (alive) setState({ blank, asset, error: '', loaded: true }); }).catch(e => { if (alive) setState({ blank: null, asset: null, error: e.message, loaded: false }); });
    return () => { alive = false; };
  }, [image, assetUrl]);
  return state;
};