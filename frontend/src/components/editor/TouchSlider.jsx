import { useRef } from 'react';
import { Slider } from '../ui/slider';

// Shared pointer mapping keeps the full 44px target usable at every canvas/viewport size.
export const TouchSlider = ({ value, min, max, step = 1, disabled, label, testId, onChange, onStart, onEnd }) => {
  const ref = useRef(null);
  const pointer = useRef(null);
  const end = () => { pointer.current = null; onEnd?.(); };
  const update = event => {
    const rect = ref.current.getBoundingClientRect();
    const fraction = (event.clientX - pointer.current.offset - rect.left - 22) / Math.max(1, rect.width - 44);
    const raw = min + fraction * (max - min);
    const snapped = Math.min(max, Math.max(min, min + Math.round((raw - min) / step) * step));
    onChange(Number(snapped.toFixed(3)));
  };
  const start = event => {
    event.preventDefault();
    if (disabled || pointer.current || (event.pointerType === 'mouse' && event.button !== 0)) return;
    const thumb = ref.current.querySelector('[role="slider"]');
    const bounds = thumb.getBoundingClientRect();
    const offset = thumb.contains(event.target) ? event.clientX - bounds.left - bounds.width / 2 : 0;
    thumb.focus(); pointer.current = { id: event.pointerId, offset };
    event.currentTarget.setPointerCapture(event.pointerId);
    onStart?.(); update(event);
  };
  const move = event => { event.preventDefault(); if (pointer.current?.id === event.pointerId) update(event); };
  const stop = event => {
    event.preventDefault();
    if (pointer.current?.id !== event.pointerId) return;
    if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId);
    end();
  };
  return <Slider ref={ref} className="curve-slider" min={min} max={max} step={step} value={[value]} disabled={disabled} thumbLabel={label} thumbTestId={`${testId}-thumb`} data-testid={testId} onPointerDown={start} onPointerMove={move} onPointerUp={stop} onPointerCancel={stop} onLostPointerCapture={() => { if (pointer.current) end(); }} onKeyDown={onStart} onKeyUp={onEnd} onBlur={end} onValueChange={([v]) => { onStart?.(); onChange(v); }} />;
};