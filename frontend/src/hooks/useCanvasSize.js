import { useEffect, useRef, useState } from 'react';
export const useCanvasSize = (fitHeight = false) => {
  const ref = useRef(null), [size, setSize] = useState(400);
  useEffect(() => { const observer = new ResizeObserver(entries => setSize(Math.max(1, Math.min(entries[0].contentRect.width, fitHeight ? entries[0].contentRect.height : 640, 800)))); if (ref.current) observer.observe(ref.current); return () => observer.disconnect(); }, [fitHeight]);
  return [ref, size];
};