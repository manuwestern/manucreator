import { useEffect, useRef, useState } from 'react';
export const useCanvasSize = () => {
  const ref = useRef(null), [size, setSize] = useState(400);
  useEffect(() => { const observer = new ResizeObserver(entries => setSize(Math.max(1, Math.min(entries[0].contentRect.width, 640)))); if (ref.current) observer.observe(ref.current); return () => observer.disconnect(); }, []);
  return [ref, size];
};