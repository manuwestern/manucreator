import { Plus, ChevronRight, SlidersHorizontal } from 'lucide-react';
import { fontWeight } from './editorCatalog';

export const TextPanel = ({ editor, setPanel }) => {
  const o = editor.selected;
  return <div className="text-panel" data-testid="text-panel">
    <p className="panel-description" data-testid="text-description">Worte, die bleiben.</p>
    {o?.type === 'text' && <>
      <label htmlFor="engraving-input" data-testid="engraving-input-label">Dein Text</label>
      <textarea id="engraving-input" data-testid="engraving-input" value={o.text} disabled={o.locked} maxLength={40} onFocus={editor.begin} onBlur={editor.end} onChange={e => { editor.begin(); editor.patchObject(o.id, { text: e.target.value.replace(/\s*\n\s*/g, ' '), name: e.target.value || 'Text' }, false); }} rows={2} />
      <div className="character-count" data-testid="text-character-count">{o.text.length} / 40 Zeichen</div>
      <button className="text-setting-row font-setting" data-testid="font-picker-open" disabled={o.locked} onClick={() => setPanel('fonts')}><span><small>Schriftart</small><strong data-testid="current-font-name">{o.font || 'Cormorant Garamond'}</strong><span className="current-font-preview" data-testid="current-font-preview" style={{ fontFamily: `"${o.font || 'Cormorant Garamond'}"`, fontWeight: fontWeight(o.font) }}>{o.text || 'Dein Unikat'}</span></span><ChevronRight size={19} /></button>
      <button className="text-setting-row" data-testid="text-properties-open" disabled={o.locked} onClick={() => setPanel('properties')}><SlidersHorizontal size={20} /><span><strong>Stil & Größe</strong><small data-testid="text-style-summary">{o.outline ? 'Nur Umriss' : 'Gefüllt'} · {Math.round((o.scale || 1) * 100)} % · Drehung</small></span><ChevronRight size={19} /></button>
    </>}
    <button className="outline-button" data-testid="add-text" onClick={() => editor.add('text', { text: 'Dein Text', curve: 0, font: 'Cormorant Garamond' })}><Plus size={18} />Neuen Text hinzufügen</button>
  </div>;
};