import { useEffect, useState } from 'react';
import { createFrameLoader, HERO_FRAMES } from '@/lib/heroFrames';

export const useHeroFrames = (canvasRef, progress, enabled, onFailure) => {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !enabled) { setReady(false); return; }
    const context = canvas.getContext('2d', { alpha: false });
    if (!context) { onFailure(); return; }
    let active = true;
    let raf = 0;
    let hasFrame = false;
    let frame = 0;
    setReady(false);
    const paint = () => {
      raf = 0;
      if (!active) return;
      if (loader.draw(context, frame)) {
        canvas.dataset.frame = String(frame);
        if (!hasFrame) { hasFrame = true; setReady(true); }
      }
    };
    const schedule = () => { if (active && !raf) raf = requestAnimationFrame(paint); };
    const loader = createFrameLoader(window.matchMedia('(max-width: 700px)').matches, schedule, onFailure);
    canvas.width = loader.width;
    canvas.height = loader.height;
    const update = value => {
      frame = Math.round(Math.min(1, Math.max(0, value)) * (HERO_FRAMES - 1));
      canvas.dataset.targetFrame = String(frame);
      loader.setTarget(frame);
      schedule();
    };
    const unsubscribe = progress.on('change', update);
    update(progress.get());

    return () => {
      active = false;
      unsubscribe();
      cancelAnimationFrame(raf);
      loader.dispose();
    };
  }, [canvasRef, progress, enabled, onFailure]);

  return ready && enabled;
};