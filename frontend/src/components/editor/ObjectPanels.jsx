import { useState } from 'react';
import { Pencil, Copy, Layers, LockKeyhole, UnlockKeyhole, Trash2, Move, Plus, ImagePlus, Heart, Leaf, SlidersHorizontal, ScanLine } from 'lucide-react';
import { toast } from 'sonner';
import { CurveIcon } from './CurvaturePanel';
import { initialObjects } from '../../hooks/useEditor';
import { SHAPES } from './editorCatalog';
import { storeImage } from '../../lib/imageStorage';

export const ObjectActions = ({ editor, setPanel }) => {
  const o = editor.selected;
  if (!o) return <div className="empty-panel" data-testid="empty-selection"><Move size={30} /><h3>Dein nächster Feinschliff</h3><p>Wähle ein Element auf dem Holz oder füge etwas Neues hinzu.</p><button className="outline-button" data-testid="add-first-text" onClick={() => { editor.add('text', { text: 'Dein Text', curve: 0 }); setPanel('edit'); }}><Plus size={18} />Text hinzufügen</button></div>;
  const actions = [
    ['edit', 'Bearbeiten', Pencil, () => setPanel(o.type === 'text' ? 'edit' : o.type === 'image' ? 'photo' : 'properties'), o.locked],
    [o.type === 'text' ? 'curve' : o.type === 'image' ? 'background' : 'properties', o.type === 'text' ? 'Wölbung' : o.type === 'image' ? 'Freistellen' : 'Stil & Größe', o.type === 'text' ? null : o.type === 'image' ? ScanLine : SlidersHorizontal, () => setPanel(o.type === 'text' ? 'curve' : o.type === 'image' ? 'cutout' : 'properties'), o.locked],
    ['duplicate', 'Duplizieren', Copy, editor.duplicate, false],
    ['arrange', 'Anordnen', Layers, () => setPanel('layers'), false],
    ['lock', o.locked ? 'Entsperren' : 'Sperren', o.locked ? UnlockKeyhole : LockKeyhole, () => editor.patchObject(o.id, { locked: !o.locked }), false],
    ['delete', 'Löschen', Trash2, () => { const snapshot = editor.objects; editor.remove(); toast('Element gelöscht', { action: { label: 'Rückgängig', onClick: () => { editor.update(snapshot); editor.select(o.id); } } }); }, o.locked],
  ];
  return <div data-testid="object-actions"><div className="action-grid">{actions.map(([id, label, Icon, click, disabled]) => <button className={`object-action ${id === 'delete' ? 'danger' : ''}`} key={id} data-testid={`action-${id}`} onClick={click} disabled={disabled}>{Icon ? <Icon size={25} strokeWidth={1.5} /> : <CurveIcon direction={1} />}<span>{label}</span></button>)}</div><p className="movement-hint" data-testid="movement-hint"><Move size={16} />Verschieben: direkt auf dem Holz</p></div>;
};

export const MotifsPanel = ({ editor, setPanel }) => {
  const [tab, setTab] = useState('shapes');
  return <div data-testid="motifs-panel"><p className="panel-description" data-testid="motifs-description">Eine klare Form. Deine persönliche Note.</p>
    <div className="element-tabs" role="group" aria-label="Elementart"><button data-testid="elements-shapes-tab" aria-pressed={tab === 'shapes'} className={tab === 'shapes' ? 'active' : ''} onClick={() => setTab('shapes')}>Grundformen</button><button data-testid="elements-motifs-tab" aria-pressed={tab === 'motifs'} className={tab === 'motifs' ? 'active' : ''} onClick={() => setTab('motifs')}>Naturmotive</button></div>
    {tab === 'shapes' ? <div className="shape-grid">{SHAPES.map(({ type, label, icon: Icon }) => <button key={type} className="shape-tile" data-testid={`add-shape-${type}`} onClick={() => { editor.add(type, { y: 345 }); setPanel('properties'); }}><Icon size={29} strokeWidth={1.4} /><span>{label}</span><Plus size={12} className="shape-add-mark" /></button>)}</div> : <div className="motif-grid">{[['heart', 'Herz', Heart], ['branch', 'Zweig', Leaf]].map(([type, name, Icon]) => <button key={type} className="motif-tile" data-testid={`add-motif-${type}`} onClick={() => { editor.add(type); setPanel('actions'); }}><Icon size={38} strokeWidth={1.3} /><span>{name}</span><Plus size={15} /></button>)}</div>}
    <p className="property-footnote" data-testid="elements-hint">Antippen zum Hinzufügen. Größe, Strichstärke und Drehung kannst du danach anpassen.</p>
  </div>;
};

export const ImagePanel = ({ editor, setPanel }) => {
  const [uploading, setUploading] = useState(false);
  const upload = async e => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type)) { toast.error('Bitte wähle ein PNG-, JPG- oder WebP-Bild.'); return; }
    if (file.size > 10 * 1024 * 1024) { toast.error('Dein Bild darf maximal 10 MB groß sein.'); e.target.value = ''; return; }
    setUploading(true);
    try {
      const probe = await createImageBitmap(file); probe.close();
      const asset = await storeImage(file);
      editor.add('image', { ...asset, name: file.name, imageView: 'engraving', scale: 2.3 }); setPanel('photo');
    } catch (_) { toast.error('Das Bild konnte nicht geöffnet oder auf diesem Gerät gespeichert werden. Bitte wähle eine gültige PNG-, JPG- oder WebP-Datei.'); }
    finally { setUploading(false); }
  };
  return <div data-testid="image-panel"><p className="panel-description" data-testid="image-description">Deine Zeichnung. Dein ganz eigenes Design.</p><label className="upload-area" data-testid="image-upload-area"><ImagePlus size={34} strokeWidth={1.3} /><strong data-testid="image-upload-status">{uploading ? 'Bild wird geladen …' : 'Bild auswählen'}</strong><span data-testid="image-upload-limit">PNG, JPG oder WebP · bis 10 MB</span><input data-testid="image-upload-input" type="file" accept="image/png,image/jpeg,image/webp" disabled={uploading} onChange={upload} /></label><p className="small-note" data-testid="image-note">Für ein klares Ergebnis eignen sich einfache Motive mit transparentem Hintergrund.</p></div>;
};

export const TemplatesPanel = ({ editor, setPanel }) => <div data-testid="templates-panel"><p className="panel-description" data-testid="templates-description">Ein Anfang für dein ganz persönliches Unikat.</p><div className="template-list">{[['Dein Unikat', 'Der Klassiker', 'Mit Herz & Zweig'], ['Für immer', 'Lieblingsmenschen', 'Für die besonderen Momente'], ['Willkommen', 'Zuhause', 'Ein persönlicher Empfang']].map(([text, title, subtitle]) => <button className="template-tile" data-testid={`template-${text.replace(' ', '-').toLowerCase()}`} key={text} onClick={() => { editor.update(initialObjects.map(o => o.type === 'text' ? { ...o, text, name: text } : { ...o })); editor.select('text'); setPanel('curve'); toast('Vorlage übernommen', { description: 'Dein vorheriges Design kannst du rückgängig machen.' }); }}><span className="template-thumb"><Heart size={13} /><span>{text}</span><Leaf size={17} /></span><span><strong>{title}</strong><small>{subtitle}</small></span></button>)}</div></div>;