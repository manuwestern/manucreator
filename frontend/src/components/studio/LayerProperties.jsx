import { useRef, useState } from 'react';
import { Crop, Eraser, RotateCcw, LoaderCircle } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { useStudioImage } from '@/hooks/useStudioImage';
import { studioApi } from '@/lib/studioApi';
import { fonts, fullCrop } from '@/lib/studioLayers';
import { constrain } from '@/lib/studioGeometry';
import { CropDialog } from './CropDialog';
import { ElementTools } from './ElementTools';

export const LayerProperties = ({ element, product, update, disabled, onBusy, onError }) => {
  const [crop, setCrop] = useState(false), [processing, setProcessing] = useState(false), preview = useRef();
  const asset = useStudioImage(element?.kind === 'image' ? element.asset_id : null);
  if (!element) return <p className="layer-empty-selection" data-testid="layer-no-selection">Keine Ebene ausgewählt.</p>;
  const removeBackground = async () => {
    setProcessing(true); onBusy(true); onError('');
    try { const result = await studioApi(`/uploads/${element.asset_id}/remove-background`, { method: 'POST' }); update({ asset_id: result.id, original_asset_id: result.original_id }); }
    catch (e) { onError(e.message); }
    finally { setProcessing(false); onBusy(false); }
  };
  const resetCrop = () => { const image = preview.current; if (!image?.naturalWidth) return; update({ crop: fullCrop(), ...constrain({ ...element, h: element.w * image.naturalHeight / image.naturalWidth }, product.area) }); };
  return <section className="layer-properties"><h2>{element.kind === 'text' ? 'Dein Text' : 'Dein Motiv'}</h2><fieldset disabled={disabled || element.locked}>
    {element.kind === 'text' ? <><label htmlFor="layer-text">Text <span data-testid="layer-text-count">{element.text.length}/{product.max_text}</span><Input id="layer-text" value={element.text} maxLength={product.max_text} onChange={e => update({ text: e.target.value })} data-testid="layer-text" /></label><label htmlFor="layer-font">Schrift<select id="layer-font" value={element.font} onChange={e => update({ font: e.target.value })} data-testid="layer-font">{fonts.map(([id,label,family]) => <option key={id} value={id} style={{ fontFamily: family }}>{label}</option>)}</select></label><div className="font-example" style={{ fontFamily: fonts.find(([id]) => id === element.font)?.[2] }} data-testid="font-example">Aa · Dein Unikat</div></> : <>
      <div className="image-layer-preview checkerboard">{asset.url && <img ref={preview} src={asset.url} alt="Ausgewähltes Bildmotiv" data-testid="layer-image-preview" />}</div>
      {asset.error && <p role="alert" data-testid="layer-image-error">{asset.error}</p>}
      <div className="image-layer-actions"><button onClick={() => setCrop(true)} disabled={!asset.url || disabled || element.locked} data-testid="image-crop"><Crop size={16} />Zuschneiden</button><button onClick={removeBackground} disabled={!asset.url || disabled || element.locked || !!element.original_asset_id} data-testid="image-remove-background">{processing ? <LoaderCircle className="loading-spin" size={16} /> : <Eraser size={16} />}{processing ? 'Wird freigestellt …' : 'Hintergrund entfernen'}</button>
      {element.original_asset_id && <button onClick={() => update({ asset_id: element.original_asset_id, original_asset_id: null })} data-testid="image-restore-original"><RotateCcw size={15} />Original wiederherstellen</button>}
      <button onClick={resetCrop} disabled={!asset.url || (element.crop.x === 0 && element.crop.y === 0 && element.crop.w === 1 && element.crop.h === 1)} data-testid="image-reset-crop"><RotateCcw size={15} />Zuschnitt zurücksetzen</button></div>
      <p className="image-processing-note" data-testid="image-processing-note">Freistellung auf Wunsch mit lokalem KI-Modell. Keine externe KI-Übertragung. Feine Kanten können Nacharbeit brauchen.</p>
    </>}
    </fieldset><ElementTools element={element} product={product} update={update} disabled={disabled} />
    {crop && asset.url && <CropDialog element={element} url={asset.url} onClose={() => setCrop(false)} onApply={(value, aspect) => { update({ crop: value, ...constrain({ ...element, h: element.w * aspect }, product.area) }); setCrop(false); }} />}
  </section>;
};