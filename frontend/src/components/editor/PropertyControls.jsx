import { useEffect, useRef, useState } from 'react';
import { Minus, Plus, LockKeyhole, UnlockKeyhole } from 'lucide-react';
import { TouchSlider } from './TouchSlider';
import { isShape, normalizeRotation } from './editorCatalog';

const NumericValue = ({ value, min, id, label, editor, onChange }) => {
  const [draft, setDraft] = useState(String(Number(value.toFixed(1))));
  const editing = useRef(false);
  useEffect(() => { if (!editing.current) setDraft(String(Number(value.toFixed(1)))); }, [value]);
  return <input type="number" inputMode="decimal" step="any" min={min} aria-label={`${label} eingeben`} data-testid={`${id}-input`} value={draft} disabled={editor.selected?.locked} onFocus={() => { editing.current = true; editor.begin(); }} onChange={e => { setDraft(e.target.value); const next = Number(e.target.value); if (e.target.value !== '' && Number.isFinite(next) && next >= min) onChange(next, false); }} onBlur={() => { editing.current = false; setDraft(String(Number(value.toFixed(1)))); editor.end(); }} onKeyDown={e => { if (e.key === 'Enter') e.currentTarget.blur(); }} />;
};

export const PropertyRange = ({ editor, label, id, value, min, max, step = 1, buttonStep = step, unit = '', onChange, unbounded = false }) => {
  const [sliderMax, setSliderMax] = useState(Math.max(max, value * 1.5));
  const sliding = useRef(false);
  useEffect(() => { if (!sliding.current && unbounded) setSliderMax(Math.max(max, value * 1.5)); }, [value, max, unbounded]);
  const disabled = editor.selected?.locked;
  const change = (v, record) => onChange(Number(Math.min(unbounded ? Infinity : max, Math.max(min, v)).toFixed(3)), record);
  const start = () => { sliding.current = true; editor.begin(); };
  const end = () => { sliding.current = false; editor.end(); if (unbounded) setSliderMax(Math.max(max, value * 1.5)); };
  return <div className="property-range" data-testid={`${id}-control`}>
    <div className="property-label"><span data-testid={`${id}-label`}>{label}</span>{unbounded ? <span className="numeric-property"><NumericValue value={value} min={min} id={id} label={label} editor={editor} onChange={change} /><span>{unit}</span></span> : <output data-testid={`${id}-value`}>{Number(value.toFixed(1)).toLocaleString('de-DE')}<span> {unit}</span></output>}</div>
    <div className="curve-slider-row"><button className="step-button" data-testid={`${id}-decrease`} aria-label={`${label} verringern`} disabled={disabled || value <= min} onClick={() => change(value - buttonStep, true)}><Minus size={18} /></button><TouchSlider testId={`${id}-slider`} label={`${label}${unit ? ` in ${unit}` : ''}`} value={value} min={min} max={unbounded ? sliderMax : max} step={step} disabled={disabled} onStart={start} onEnd={end} onChange={v => change(v, false)} /><button className="step-button" data-testid={`${id}-increase`} aria-label={`${label} erhöhen`} disabled={disabled || (!unbounded && value >= max)} onClick={() => change(value + buttonStep, true)}><Plus size={18} /></button></div>
  </div>;
};

export const AppearanceControls = ({ editor }) => {
  const o = editor.selected;
  const isText = o.type === 'text';
  const supportsFill = isText || (isShape(o) && o.type !== 'line') || o.type === 'heart';
  const outlined = isText ? !!o.outline : !o.filled;
  const showStroke = o.type !== 'image' && (!isText || outlined);
  return <section className="appearance-controls" data-testid="appearance-controls">
    {supportsFill && <><span className="property-section-label" data-testid="appearance-label">Darstellung</span><div className="appearance-options" role="group" aria-label="Darstellung"><button data-testid="appearance-filled" className={!outlined ? 'active' : ''} disabled={o.locked} aria-pressed={!outlined} onClick={() => editor.patchObject(o.id, isText ? { outline: false } : { filled: true })}><span className="style-sample filled" aria-hidden="true">{isText ? 'Aa' : '●'}</span>Gefüllt</button><button data-testid="appearance-outline" className={outlined ? 'active' : ''} disabled={o.locked} aria-pressed={outlined} onClick={() => editor.patchObject(o.id, isText ? { outline: true } : { filled: false })}><span className="style-sample outline" aria-hidden="true">{isText ? 'Aa' : '○'}</span>Nur Umriss</button></div></>}
    {showStroke && <PropertyRange editor={editor} id="stroke-width" label={isText ? 'Umrissstärke' : 'Strichstärke'} value={o.strokeWidthMm ?? (isText ? .4 : o.type === 'branch' ? .88 : o.type === 'heart' ? 1.25 : 1)} min={.2} max={6} step={.1} unit="mm" onChange={(v, record) => editor.patchObject(o.id, { strokeWidthMm: v }, record)} />}
  </section>;
};

export const PropertiesPanel = ({ editor }) => {
  const o = editor.selected;
  if (!o) return <p data-testid="properties-empty">Wähle zuerst ein Element auf dem Holz aus.</p>;
  const patch = (data, record = true) => editor.patchObject(o.id, data, record);
  const dimension = (key, value, record) => {
    const data = { [key]: value };
    if (o.type === 'circle') { data.widthMm = value; data.heightMm = value; }
    else if (o.type !== 'line' && o.lockAspect !== false) {
      const other = key === 'widthMm' ? 'heightMm' : 'widthMm';
      const factor = Math.max(.5 / Math.min(o.widthMm, o.heightMm), value / o[key]);
      data[key] = Number((o[key] * factor).toFixed(2)); data[other] = Number((o[other] * factor).toFixed(2));
    }
    patch(data, record);
  };
  return <div className="properties-panel" data-testid="properties-panel">
    <AppearanceControls editor={editor} />
    <section className="geometry-controls" data-testid="geometry-controls">
      {isShape(o) ? <>
        <PropertyRange editor={editor} id="object-width" label={o.type === 'line' ? 'Länge' : o.type === 'circle' ? 'Durchmesser' : 'Breite'} value={o.widthMm} min={.5} max={170} unbounded unit="mm" onChange={(v, record) => dimension('widthMm', v, record)} />
        {!['line', 'circle'].includes(o.type) && <><PropertyRange editor={editor} id="object-height" label="Höhe" value={o.heightMm} min={.5} max={170} unbounded unit="mm" onChange={(v, record) => dimension('heightMm', v, record)} /><button className={`aspect-lock ${o.lockAspect !== false ? 'active' : ''}`} data-testid="aspect-lock" aria-pressed={o.lockAspect !== false} disabled={o.locked} onClick={() => patch({ lockAspect: o.lockAspect === false })}>{o.lockAspect !== false ? <LockKeyhole size={16} /> : <UnlockKeyhole size={16} />}Proportionen beibehalten</button></>}
      </> : <PropertyRange editor={editor} id="object-size" label="Größe" value={(o.scale || 1) * 100} min={1} max={160} unbounded step={1} buttonStep={5} unit="%" onChange={(v, record) => patch({ scale: v / 100 }, record)} />}
      <PropertyRange editor={editor} id="object-rotation" label="Drehung" value={o.rotation === 180 ? 180 : normalizeRotation(o.rotation || 0)} min={-180} max={180} buttonStep={5} unit="°" onChange={(v, record) => patch({ rotation: v }, record)} />
    </section>
    <p className="property-footnote" data-testid="properties-hint">Beliebig vergrößern, auch per Werteingabe. Außerhalb des gestrichelten Gravurbereichs wird dein Motiv abgeschnitten.</p>
  </div>;
};