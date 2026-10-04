import { useCallback,useEffect,useRef,useState } from 'react';
import { Crop,ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { getTextPreview } from '@/lib/textPreview';
import { isInside,imageFrame } from '@/lib/transformGeometry';
import { fullCrop } from '@/lib/studioLayers';
import { useStudioImage } from '@/hooks/useStudioImage';
import { LayerUpload } from './LayerUpload';
import { CropDialog } from './CropDialog';

const SimpleText=({element:e,product,onChange,onState,disabled})=>{
  const [text,setText]=useState(e.text),[error,setError]=useState('');const seq=useRef(0),timer=useRef();
  useEffect(()=>{setText(e.text);setError('');onState(e.id,{pending:false,error:false});},[e.text,e.id,onState]);
  useEffect(()=>{const ref=seq,t=timer;return()=>{ref.current++;clearTimeout(t.current);onState(e.id,{pending:false,error:false});};},[e.id,onState]);
  const edit=value=>{setText(value);setError('');const version=++seq.current;clearTimeout(timer.current);onState(e.id,{pending:true,error:false});timer.current=setTimeout(async()=>{try{
    if(value.length>product.max_text)throw new Error(`Höchstens ${product.max_text} Zeichen. Bitte kürzen; es wird nichts abgeschnitten.`);
    if(!value){if(version===seq.current){onChange({...e,text:''});onState(e.id,{pending:false,error:false});}return;}
    const rendered=await getTextPreview({...e,text:value});if(version!==seq.current)return;
    const slot=e.template_slot,next={...e,text:value,w:rendered.width,h:rendered.height,x:slot.x+(slot.w-rendered.width)/2,y:slot.y+(slot.h-rendered.height)/2};
    if(value&&(rendered.width>slot.w+.05||rendered.height>slot.h+.05||!isInside(next,product.area,0)))throw new Error('Der Text ist für dieses Vorlagenfeld zu lang. Bitte kürzen oder bewusst frei bearbeiten.');
    onChange(next);onState(e.id,{pending:false,error:false});
  }catch(err){if(version===seq.current){setError(err.message);onState(e.id,{pending:false,error:true});}}},160);};
  return <div className="simple-text-field"><label htmlFor={`simple-${e.id}`}>{e.field_label||'Text'}<Input id={`simple-${e.id}`} value={text} onChange={event=>edit(event.target.value)} disabled={disabled} data-testid={`template-field-${e.template_field}`}/></label>{error&&<p role="alert" className="property-error" data-testid={`template-field-error-${e.template_field}`}>{error}</p>}</div>;
};
const SimpleImage=({element:e,product,onChange,onState,disabled})=>{
  const asset=useStudioImage(e.asset_id),[crop,setCrop]=useState(false),[error,setError]=useState('');
  return <div className="simple-image-field"><p>{e.field_label||'Dein Motiv'}</p>{asset.url?<img src={asset.url} alt="Eigenes Motiv" data-testid={`template-image-${e.template_field}`}/>:<div className="template-placeholder-note" data-testid={`template-placeholder-${e.template_field}`}>{e.image_type==='logo'?'Eigenes Logo fehlt noch':'Eigenes Foto fehlt noch'}</div>}<LayerUpload label={e.image_type==='logo'?'Logo ersetzen':'Bild ersetzen'} disabled={disabled} onBusy={pending=>onState(e.id,{pending,error:false})} onError={setError} onUpload={image=>{const next=imageFrame({...e,...e.template_slot,asset_id:image.id,original_asset_id:null,image_ratio:image.width/image.height,crop:fullCrop(),placeholder:false},image.width/image.height,product.area);onChange(next);}}/>{asset.url&&<button className="simple-crop-button" disabled={disabled} onClick={()=>setCrop(true)} data-testid={`template-crop-${e.template_field}`}><Crop size={14}/>Bild zuschneiden</button>}{error&&<p className="property-error" role="alert" data-testid={`template-image-error-${e.template_field}`}>{error}</p>}{crop&&asset.url&&<CropDialog element={e} url={asset.url} onClose={()=>setCrop(false)} onApply={(value,ratio)=>{onChange(imageFrame({...e,...e.template_slot,crop:value},1/ratio,product.area));setCrop(false);}}/>}</div>;
};
export const TemplateFields=({design,product,updateElement,disabled,onPending,onInvalid,onFree})=>{
  const [states,setStates]=useState({});
  const state=useCallback((id,value)=>setStates(old=>old[id]?.pending===value.pending&&old[id]?.error===value.error?old:{...old,[id]:value}),[]);
  useEffect(()=>{onPending(Object.values(states).some(s=>s.pending));onInvalid(Object.values(states).some(s=>s.error));},[states,onPending,onInvalid]);
  useEffect(()=>()=>{onPending(false);onInvalid(false);},[onPending,onInvalid]);
  return <section className="template-fields" data-testid="template-simple-fields"><div className="simple-mode-heading"><span>DEINE INHALTE</span><h2>Persönlich gemacht.</h2></div>{design.elements.map(e=>e.kind==='text'?<SimpleText key={e.id} element={e} product={product} disabled={disabled} onState={state} onChange={next=>updateElement(e.id,next)}/>:<SimpleImage key={e.id} element={e} product={product} disabled={disabled} onState={state} onChange={next=>updateElement(e.id,next)}/>)}<Button variant="outline" onClick={onFree} disabled={disabled||Object.values(states).some(s=>s.pending)} data-testid="template-free-edit">Frei bearbeiten<ArrowRight size={15}/></Button></section>;
};