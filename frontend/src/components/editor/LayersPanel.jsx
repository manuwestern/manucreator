import { GripVertical, Eye, EyeOff, LockKeyhole, UnlockKeyhole, ArrowUpToLine, ArrowDownToLine, ArrowUp, ArrowDown } from 'lucide-react';
import { OBJECT_ICONS } from './editorCatalog';

export const LayersPanel = ({ editor }) => {
  const selected = editor.selected;
  const index = editor.objects.findIndex(o => o.id === selected?.id);
  const n = editor.objects.length;
  return <div data-testid="layers-panel">
    <p className="panel-description" data-testid="layers-description">Oben liegt vorne. Alles an seinem Platz.</p>
    <div className="layer-end-label" data-testid="layers-front-label">Vorne</div>
    <div className="layer-list">{[...editor.objects].reverse().map(o => {
      const Icon = OBJECT_ICONS[o.type];
      return <div className={`layer-row ${o.id === selected?.id ? 'selected' : ''} ${!o.visible ? 'invisible-layer' : ''}`} key={o.id} data-testid={`layer-${o.id}`} draggable onDragStart={e => e.dataTransfer.setData('text/plain', o.id)} onDragOver={e => e.preventDefault()} onDrop={e => { e.preventDefault(); const id = e.dataTransfer.getData('text/plain'); if (editor.objects.some(obj => obj.id === id)) editor.reorder(id, editor.objects.findIndex(obj => obj.id === o.id)); }}>
        <GripVertical className="grip" size={17} /><button className="layer-select" data-testid={`select-layer-${o.id}`} onClick={() => editor.select(o.id)} aria-pressed={o.id === selected?.id}><span className={`layer-type ${o.type}`}><Icon size={23} strokeWidth={1.4} /></span><span>{o.name}</span></button>
        <button className="icon-button layer-control" aria-label={`${o.name} ${o.visible ? 'ausblenden' : 'einblenden'}`} data-testid={`visibility-${o.id}`} onClick={() => editor.patchObject(o.id, { visible: !o.visible })}>{o.visible ? <Eye size={18} /> : <EyeOff size={18} />}</button>
        <button className="icon-button layer-control" aria-label={`${o.name} ${o.locked ? 'entsperren' : 'sperren'}`} data-testid={`lock-${o.id}`} onClick={() => editor.patchObject(o.id, { locked: !o.locked })}>{o.locked ? <LockKeyhole size={17} /> : <UnlockKeyhole size={17} />}</button>
      </div>;
    })}</div>
    {!n && <p className="small-note" data-testid="layers-empty">Dein Design ist noch leer. Füge Text oder ein Motiv hinzu.</p>}
    <div className="layer-end-label" data-testid="layers-back-label">Hinten</div>
    <div className="layer-actions">{[
      ['forward', 'Eine Ebene vor', ArrowUp, index + 1, index === n - 1], ['front', 'Ganz nach vorne', ArrowUpToLine, n - 1, index === n - 1],
      ['backward', 'Eine Ebene zurück', ArrowDown, index - 1, index === 0], ['back', 'Ganz nach hinten', ArrowDownToLine, 0, index === 0],
    ].map(([id, label, Icon, target, disabled]) => <button key={id} className="outline-button" data-testid={`layer-${id}`} disabled={!selected || disabled} onClick={() => editor.reorder(selected.id, target)}><Icon size={18} /><span>{label}</span></button>)}</div>
  </div>;
};