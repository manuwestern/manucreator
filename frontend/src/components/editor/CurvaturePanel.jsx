import { useRef } from 'react';
import { Minus, Plus, RotateCcw, Info } from 'lucide-react';
import { Slider } from '../ui/slider';

export const CurveIcon = ({ direction = 0 }) => <svg viewBox="0 0 80 52" width="72" height="46" aria-hidden="true"><path id={`example-curve-${direction}`} d={`M12 32 Q40 ${32 - direction * 25} 68 32`} fill="none" /><text fontFamily="Cormorant Garamond, Georgia, serif" fontSize="30" fill="currentColor" textAnchor="middle"><textPath href={`#example-curve-${direction}`} startOffset="50%">Aa</textPath></text><path d={`M12 39 Q40 ${39 - direction * 24} 68 39`} stroke="currentColor" strokeWidth="1.4" fill="none" /></svg>;

export const CurvaturePanel = ({ editor }) => {
  const sliderRef = useRef(null);
  const pointerActive = useRef(false);
  const pointerOffset = useRef(0);
  const o = editor.selected;
  const value = o?.curve || 0;
  const setValue = (v, record = true) => editor.patchObject(o.id, { curve: Math.max(-180, Math.min(180, v)) }, record);
  const endInteraction = () => { pointerActive.current = false; editor.end(); };
  const updatePointer = event => {
    const rect = sliderRef.current.getBoundingClientRect();
    // Use the actual travel of the 44px thumb, not the outside edges of the track.
    const fraction = (event.clientX - pointerOffset.current - rect.left - 22) / Math.max(1, rect.width - 44);
    setValue(Math.round(fraction * 360 - 180), false);
  };
  const startPointer = event => {
    event.preventDefault();
    if (o.locked) return;
    const thumb = sliderRef.current.querySelector('[role="slider"]');
    const bounds = thumb.getBoundingClientRect();
    pointerOffset.current = thumb.contains(event.target) ? event.clientX - bounds.left - bounds.width / 2 : 0;
    thumb.focus();
    pointerActive.current = true;
    event.currentTarget.setPointerCapture(event.pointerId);
    editor.begin(); updatePointer(event);
  };
  const movePointer = event => {
    event.preventDefault();
    if (pointerActive.current) updatePointer(event);
  };
  const stopPointer = event => {
    event.preventDefault();
    if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId);
    endInteraction();
  };
  if (!o || o.type !== 'text') return <p data-testid="curve-no-selection">Wähle einen Text auf deiner Holzscheibe aus.</p>;
  return <div className="curvature-panel" data-testid="curvature-panel">
    <p className="panel-description" data-testid="curve-description">Gib deinen Worten eine schöne Form.</p>
    <div className="curve-presets" data-testid="curve-presets">
      {[[-1, 'Nach unten', 'down'], [0, 'Gerade', 'straight'], [1, 'Nach oben', 'up']].map(([dir, label, id]) => <button key={id} className={`curve-preset ${Math.sign(value) === dir ? 'active' : ''}`} aria-pressed={Math.sign(value) === dir} disabled={o.locked} data-testid={`curve-${id}`} onClick={() => setValue(dir * Math.max(35, Math.abs(value)))}><CurveIcon direction={dir} /><span>{label}</span></button>)}
    </div>
    <div className="range-label"><label id="curve-label" data-testid="curve-label">Bogen</label><output data-testid="curve-value" aria-live="polite">{value > 0 ? '+' : ''}{value}<span>°</span></output></div>
    <div className="curve-slider-row">
      <button className="step-button" data-testid="curve-decrease" aria-label="Bogen um 5 Grad verringern" disabled={value <= -180 || o.locked} onClick={() => setValue(value - 5)}><Minus size={20} /></button>
      <Slider ref={sliderRef} className="curve-slider" min={-180} max={180} step={1} value={[value]} disabled={o.locked} thumbLabel="Bogen in Grad" thumbTestId="curve-slider-thumb" data-testid="curve-slider" onPointerDown={startPointer} onPointerMove={movePointer} onPointerUp={stopPointer} onPointerCancel={stopPointer} onKeyDown={editor.begin} onKeyUp={editor.end} onBlur={endInteraction} onValueChange={([v]) => { editor.begin(); setValue(v, false); }} />
      <button className="step-button" data-testid="curve-increase" aria-label="Bogen um 5 Grad erhöhen" disabled={value >= 180 || o.locked} onClick={() => setValue(value + 5)}><Plus size={20} /></button>
    </div>
    <div className="range-ticks" aria-hidden="true" data-testid="curve-scale"><span>−180°</span><span>0°</span><span>+180°</span></div>
    <button className="outline-button reset-curve" data-testid="curve-reset" disabled={o.locked} onClick={() => setValue(0)}><RotateCcw size={16} />Wölbung zurücksetzen</button>
    <div className="tip-card" data-testid="curve-tip"><Info size={17} /><p>Ein kleiner Bogen, eine große Wirkung.<br /><span>Deine Änderungen siehst du direkt auf dem Holz.</span></p></div>
  </div>;
};