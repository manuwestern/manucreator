import { Pencil, Copy, Layers, LockKeyhole, UnlockKeyhole, Trash2, Move, Plus, ImagePlus, Heart, Leaf } from 'lucide-react';
import { toast } from 'sonner';
import { CurveIcon } from './CurvaturePanel';
import { initialObjects } from '../../hooks/useEditor';

export const ObjectActions = ({ editor, setPanel }) => {
  const o = editor.selected;
  if (!o) return <div className="empty-panel" data-testid="empty-selection"><Move size={30} /><h3>Dein nächster Feinschliff</h3><p>Wähle ein Element auf dem Holz oder füge etwas Neues hinzu.</p><button className="outline-button" data-testid="add-first-text" onClick={() => { editor.add('text', { text: 'Dein Text', curve: 0 }); setPanel('edit'); }}><Plus size={18} />Text hinzufügen</button></div>;
  const actions = [
    ['edit', 'Bearbeiten', Pencil, () => setPanel('edit'), o.type !== 'text' || o.locked],
    ['curve', 'Wölbung', null, () => setPanel('curve'), o.type !== 'text' || o.locked],
    ['duplicate', 'Duplizieren', Copy, editor.duplicate, false],
    ['arrange', 'Anordnen', Layers, () => setPanel('layers'), false],
    ['lock', o.locked ? 'Entsperren' : 'Sperren', o.locked ? UnlockKeyhole : LockKeyhole, () => editor.patchObject(o.id, { locked: !o.locked }), false],
    ['delete', 'Löschen', Trash2, () => { const snapshot = editor.objects; editor.remove(); toast('Element gelöscht', { action: { label: 'Rückgängig', onClick: () => { editor.update(snapshot); editor.select(o.id); } } }); }, o.locked],
  ];
  return <div data-testid="object-actions"><div className="action-grid">{actions.map(([id, label, Icon, click, disabled]) => <button className={`object-action ${id === 'delete' ? 'danger' : ''}`} key={id} data-testid={`action-${id}`} onClick={click} disabled={disabled}>{Icon ? <Icon size={25} strokeWidth={1.5} /> : <CurveIcon direction={1} />}<span>{label}</span></button>)}</div><p className="movement-hint" data-testid="movement-hint"><Move size={16} />Verschieben: direkt auf dem Holz</p></div>;
};

export const TextPanel = ({ editor }) => {
  const o = editor.selected;
  return <div className="text-panel" data-testid="text-panel">
    <p className="panel-description" data-testid="text-description">Worte, die bleiben.</p>
    {o?.type === 'text' && <><label htmlFor="engraving-input">Dein Text</label><textarea id="engraving-input" data-testid="engraving-input" value={o.text} disabled={o.locked} maxLength={40} onFocus={editor.begin} onBlur={editor.end} onChange={e => { editor.begin(); editor.patchObject(o.id, { text: e.target.value, name: e.target.value || 'Text' }, false); }} rows={2} /><div className="character-count" data-testid="text-character-count">{o.text.length} / 40 Zeichen</div><label htmlFor="font-select">Schriftart</label><select id="font-select" data-testid="font-select" value={o.font || 'Cormorant Garamond'} disabled={o.locked} onChange={e => editor.patchObject(o.id, { font: e.target.value })}><option>Cormorant Garamond</option><option>Georgia</option><option>DM Sans</option><option>Italianno</option></select></>}
    <button className="outline-button" data-testid="add-text" onClick={() => editor.add('text', { text: 'Dein Text', curve: 0, font: 'Cormorant Garamond' })}><Plus size={18} />Neuen Text hinzufügen</button>
  </div>;
};

export const MotifsPanel = ({ editor, setPanel }) => <div data-testid="motifs-panel"><p className="panel-description" data-testid="motifs-description">Kleine Details. Ganz viel Persönlichkeit.</p><div className="motif-grid">{[['heart', 'Herz', Heart], ['branch', 'Zweig', Leaf]].map(([type, name, Icon]) => <button key={type} className="motif-tile" data-testid={`add-motif-${type}`} onClick={() => { editor.add(type); setPanel('actions'); }}><Icon size={38} strokeWidth={1.3} /><span>{name}</span><Plus size={15} /></button>)}</div></div>;

export const ImagePanel = ({ editor, setPanel }) => {
  const upload = e => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type)) { toast.error('Bitte wähle ein PNG-, JPG- oder WebP-Bild.'); return; }
    if (file.size > 2 * 1024 * 1024) { toast.error('Dein Bild darf maximal 2 MB groß sein.'); return; }
    const reader = new FileReader(); reader.onload = () => { editor.add('image', { src: reader.result, name: file.name }); setPanel('actions'); }; reader.onerror = () => toast.error('Das Bild konnte nicht gelesen werden.'); reader.readAsDataURL(file);
  };
  return <div data-testid="image-panel"><p className="panel-description" data-testid="image-description">Deine Zeichnung. Dein ganz eigenes Design.</p><label className="upload-area" data-testid="image-upload-area"><ImagePlus size={34} strokeWidth={1.3} /><strong>Bild auswählen</strong><span>PNG, JPG oder WebP · bis 2 MB</span><input data-testid="image-upload-input" type="file" accept="image/png,image/jpeg,image/webp" onChange={upload} /></label><p className="small-note" data-testid="image-note">Für ein klares Ergebnis eignen sich einfache Motive mit transparentem Hintergrund.</p></div>;
};

export const TemplatesPanel = ({ editor, setPanel }) => <div data-testid="templates-panel"><p className="panel-description" data-testid="templates-description">Ein Anfang für dein ganz persönliches Unikat.</p><div className="template-list">{[['Dein Unikat', 'Der Klassiker', 'Mit Herz & Zweig'], ['Für immer', 'Lieblingsmenschen', 'Für die besonderen Momente'], ['Willkommen', 'Zuhause', 'Ein persönlicher Empfang']].map(([text, title, subtitle]) => <button className="template-tile" data-testid={`template-${text.replace(' ', '-').toLowerCase()}`} key={text} onClick={() => { editor.update(initialObjects.map(o => o.type === 'text' ? { ...o, text, name: text } : { ...o })); editor.select('text'); setPanel('curve'); toast('Vorlage übernommen', { description: 'Dein vorheriges Design kannst du rückgängig machen.' }); }}><span className="template-thumb"><Heart size={13} /><span>{text}</span><Leaf size={17} /></span><span><strong>{title}</strong><small>{subtitle}</small></span></button>)}</div></div>;