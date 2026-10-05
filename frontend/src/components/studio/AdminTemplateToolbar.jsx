import { Type,ImagePlus,Stamp,Undo2,Redo2 } from 'lucide-react';
import { ShapePicker } from './ShapePicker';

export const AdminTemplateToolbar=({product,imageType,setImageType,disabled,count,onText,onImage,onDecoration,onShape,onUndo,onRedo,canUndo,canRedo})=><div className="admin-template-toolbar">
  <button title="Text hinzufügen" disabled={disabled||count>=12||!product.templates.includes('text')} onClick={onText} data-testid="admin-template-add-text"><Type size={17}/><span>Text</span></button>
  {product.templates.some(t=>t!=='text')&&<>
    <select aria-label="Kundenmotiv" value={imageType} onChange={e=>setImageType(e.target.value)} data-testid="admin-template-image-type">{product.templates.filter(t=>t!=='text').map(t=><option key={t} value={t}>{t==='photo'?'Foto':'Logo'}</option>)}</select>
    <button title="Bildfeld hinzufügen" disabled={disabled||count>=12} onClick={onImage} data-testid="admin-template-add-image"><ImagePlus size={17}/></button>
  </>}
  <button title="Eigene Dekoration hinzufügen" disabled={disabled||count>=12} onClick={onDecoration} data-testid="admin-template-add-decoration"><Stamp size={17}/><span>Motiv</span></button>
  <ShapePicker disabled={disabled||count>=12} onAdd={onShape}/>
  <button title="Rückgängig" aria-label="Rückgängig" disabled={disabled||!canUndo} onClick={onUndo} data-testid="admin-template-undo"><Undo2 size={17}/></button>
  <button title="Wiederholen" aria-label="Wiederholen" disabled={disabled||!canRedo} onClick={onRedo} data-testid="admin-template-redo"><Redo2 size={17}/></button>
</div>;