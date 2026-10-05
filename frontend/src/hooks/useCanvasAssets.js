import { useCallback, useEffect, useState } from 'react';
import { productImage } from '@/lib/studioApi';
import { fonts } from '@/lib/studioLayers';
import { withPreviewRetry } from '@/lib/previewRetry';
import { loadCanvasFont } from '@/lib/canvasFontLoading';

export const useCanvasAssets = (image, assetUrl) => {
  const [state, setState] = useState({ blank: null, asset: null, error: '', loaded: false });
  const [attempt, setAttempt] = useState(0);
  const retry = useCallback(() => setAttempt(value => value + 1), []);
  useEffect(() => {
    let alive = true;
    setState({ blank: null, asset: null, error: '', loaded: false });
    const load = src => withPreviewRetry(() => new Promise((resolve, reject) => { if (!src) return resolve(null); const img = new Image(); img.crossOrigin = 'anonymous'; img.onload = () => resolve(img); img.onerror = () => reject(new Error('Das Bild konnte nicht geladen werden.')); img.src = src; }));
    Promise.all([load(productImage(image)), load(assetUrl), ...fonts.map(([, , f]) => loadCanvasFont(f))]).then(([blank, asset]) => { if (alive) setState({ blank, asset, error: '', loaded: true }); }).catch(() => { if (alive) setState({ blank: null, asset: null, error: 'Die Vorschau konnte nicht vollständig geladen werden.', loaded: false }); });
    return () => { alive = false; };
  }, [image, assetUrl, attempt]);
  return { ...state, retry };
};