import { useEffect,useRef,useState } from 'react';
import { Crop,Eraser,RotateCcw,LoaderCircle,Check,X,Columns2 } from 'lucide-react';
import { Dialog,DialogContent,DialogTitle,DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { useStudioImage,loadStudioImage } from '@/hooks/useStudioImage';
import { studioApi } from '@/lib/studioApi';
import { fullCrop } from '@/lib/studioLayers';
import { imageFrame } from '@/lib/transformGeometry';
import { CropDialog } from './CropDialog';

export const ImageProperties=({element,product,update,disabled,processing,onBusy,onError,candidate,onCandidate,onCompare,onAccept,onDiscard})=>{
  const [crop,setCrop]=useState(false),[capabilities,setCapabilities]=useState(null),[consentDialog,setConsentDialog]=useState(false),[consent,setConsent]=useState(false);
  const preview=useRef(),request=useRef(null),source=useStudioImage(element.asset_id),result=useStudioImage(candidate?.result?.id),[capError,setCapError]=useState('');
  useEffect(()=>{let alive=true;studioApi('/uploads/background-capabilities').then(v=>{if(alive)setCapabilities(v);}).catch(e=>{if(alive)setCapError(e.message);});return()=>{alive=false;};},[]);
  const start=async()=>{if(!consent)return;setConsentDialog(false);onBusy(true);onError('');if(!request.current)request.current=crypto.randomUUID();try{
    const result=await studioApi(`/uploads/${element.asset_id}/remove-background`,{method:'POST',body:{request_id:request.current,consent:true}});
    await loadStudioImage(result.id);onCandidate({elementId:element.id,result,showOriginal:false});
  }catch(e){onError(e.message);}finally{onBusy(false);}};
  const resetCrop=()=>{const img=preview.current;if(!img?.naturalWidth)return;const ratio=element.image_ratio||img.naturalWidth/img.naturalHeight;update(imageFrame({...element,crop:fullCrop()},ratio,product.area));};
  const display=candidate&&!candidate.showOriginal?result:source;
  return <><div className="image-layer-preview checkerboard">{display.url&&<img key={display.url} ref={preview} src={display.url} alt={candidate&&!candidate.showOriginal?'GPT-Ergebnis zur Prüfung':'Originales Bildmotiv'} data-testid="layer-image-preview"/>}</div>
    {candidate?<div className="cutout-review" data-testid="cutout-review"><div className="cutout-compare"><button aria-pressed={candidate.showOriginal} onClick={()=>onCompare(true)} data-testid="cutout-show-original"><Columns2 size={14}/>Original</button><button aria-pressed={!candidate.showOriginal} onClick={()=>onCompare(false)} data-testid="cutout-show-result">Ergebnis</button></div><p>Motivdetails bitte vergleichen. Änderungen durch GPT sind möglich.</p><Button onClick={onAccept} data-testid="cutout-accept"><Check size={15}/>Übernehmen</Button><button onClick={onDiscard} data-testid="cutout-discard"><X size={15}/>Verwerfen</button></div>:<fieldset disabled={disabled||element.locked} className="image-layer-actions"><button onClick={()=>setCrop(true)} disabled={!source.url} data-testid="image-crop"><Crop size={16}/>Zuschneiden</button><button onClick={()=>{request.current=null;setConsent(false);setConsentDialog(true);}} disabled={!source.url||!capabilities?.configured} data-testid="image-remove-background">{processing?<LoaderCircle className="loading-spin" size={16}/>:<Eraser size={16}/>}Hintergrund entfernen</button>
    {element.original_asset_id&&<button onClick={()=>update({asset_id:element.original_asset_id,original_asset_id:null})} data-testid="image-restore-original"><RotateCcw size={15}/>Original wiederherstellen</button>}
    <button onClick={resetCrop} disabled={!source.url||(element.crop.x===0&&element.crop.y===0&&element.crop.w===1&&element.crop.h===1)} data-testid="image-reset-crop"><RotateCcw size={15}/>Zuschnitt zurücksetzen</button></fieldset>}
    {processing&&<p role="status" className="property-status" data-testid="cutout-processing"><LoaderCircle size={14} className="loading-spin"/>OpenAI bearbeitet das Bild …</p>}
    {!capabilities?.configured&&<p className="integration-notice" data-testid="cutout-unconfigured">{capError||capabilities?.reason||'Freistellung wird geprüft …'}</p>}
    {source.error&&<p role="alert" data-testid="layer-image-error">{source.error}</p>}
    {crop&&source.url&&<CropDialog element={element} url={source.url} onClose={()=>setCrop(false)} onApply={(value,ratio)=>{update(imageFrame({...element,crop:value},1/ratio,product.area));setCrop(false);}}/>}
    <Dialog open={consentDialog} onOpenChange={setConsentDialog}><DialogContent data-testid="cutout-consent-dialog"><DialogTitle>Hintergrund mit GPT entfernen?</DialogTitle><DialogDescription>Dein Originalbild wird an OpenAI übertragen. Dabei können API-Nutzungskosten entstehen. GPT kann trotz Vorgaben auch Gesichter, Logos und Beschriftungen verändern. Du prüfst das Ergebnis vor der Übernahme.</DialogDescription><div className="upload-rights"><Checkbox id="cutout-consent" checked={consent} onCheckedChange={v=>setConsent(v===true)} data-testid="cutout-consent"/><label htmlFor="cutout-consent">Bildübertragung an OpenAI und mögliche API-Kosten bestätigen</label></div><Button disabled={!consent} onClick={start} data-testid="cutout-start">Freistellung starten</Button><Button variant="outline" onClick={()=>setConsentDialog(false)} data-testid="cutout-cancel">Abbrechen</Button></DialogContent></Dialog>
  </>;
};