import { ArrowLeft, Check, ChevronRight, Type, Heart, Leaf, Image } from 'lucide-react';
import { CurvaturePanel } from './CurvaturePanel';
import { ObjectActions, TextPanel, MotifsPanel, ImagePanel, TemplatesPanel } from './ObjectPanels';
import { LayersPanel } from './LayersPanel';

const titles = { curve: 'Wölbung', actions: 'Objektaktionen', edit: 'Text bearbeiten', motifs: 'Motive', image: 'Dein Bild', templates: 'Vorlagen', layers: 'Reihenfolge' };
export const ToolPanel = ({ editor, panel, setPanel }) => {
  const o = editor.selected;
  const Icon = { text: Type, heart: Heart, branch: Leaf, image: Image }[o?.type] || Type;
  return <aside className="tool-panel" data-testid="tool-panel" aria-label="Design-Werkzeuge">
    <div className="desktop-panel-intro"><span className="eyebrow" data-testid="design-eyebrow">GANZ NACH DEINEM GESCHMACK</span><h2 data-testid="design-heading">Dein Design<span>.</span></h2><p data-testid="design-description">Aus einer Idee wird dein Unikat.</p></div>
    {o && ['curve', 'actions', 'edit', 'layers'].includes(panel) && <button className="selected-object-card" data-testid="selected-object-card" onClick={() => setPanel('actions')}><span className="selected-object-icon"><Icon size={24} strokeWidth={1.3} /></span><span><small data-testid="selected-object-label">{o.type === 'text' ? 'TEXT AUSGEWÄHLT' : 'OBJEKT AUSGEWÄHLT'}</small><strong data-testid="selected-object-name">{o.name}</strong></span><ChevronRight size={16} /></button>}
    <div className="sheet-handle" aria-hidden="true" />
    <div className="panel-heading"><div>{['curve', 'edit', 'layers'].includes(panel) && <button className="panel-back" data-testid="panel-back" aria-label="Zurück zu den Objektaktionen" onClick={() => setPanel('actions')}><ArrowLeft size={19} /></button>}<h2 data-testid="panel-title">{panel === 'actions' && o ? (o.type === 'text' ? 'Text ausgewählt' : 'Objekt ausgewählt') : titles[panel]}</h2></div><button className="done-button" data-testid="panel-done" onClick={() => setPanel(null)}><Check size={15} /><span>Fertig</span></button></div>
    <div className="panel-content" data-testid="panel-content">
      {panel === 'curve' && <CurvaturePanel editor={editor} />}
      {panel === 'actions' && <ObjectActions editor={editor} setPanel={setPanel} />}
      {panel === 'edit' && <TextPanel editor={editor} />}
      {panel === 'layers' && <LayersPanel editor={editor} />}
      {panel === 'motifs' && <MotifsPanel editor={editor} setPanel={setPanel} />}
      {panel === 'image' && <ImagePanel editor={editor} setPanel={setPanel} />}
      {panel === 'templates' && <TemplatesPanel editor={editor} setPanel={setPanel} />}
    </div>
    <div className="panel-bottom-note" data-testid="autosave-note"><span />Dein Design wird auf diesem Gerät gespeichert.</div>
  </aside>;
};