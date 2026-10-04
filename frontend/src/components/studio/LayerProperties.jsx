import { LockKeyhole } from 'lucide-react';
import { ElementTools } from './ElementTools';
import { TextProperties } from './TextProperties';
import { ImageProperties } from './ImageProperties';

export const LayerProperties=props=>{
  const {element,product,update,disabled,onPending}=props;
  if(!element)return <div className="property-empty" data-testid="layer-no-selection">Wähle eine Ebene aus.</div>;
  return <section className="layer-properties"><div className="property-title"><h2>{element.kind==='text'?'Text & Schrift':'Bild & Zuschnitt'}</h2>{element.locked&&<LockKeyhole size={15} data-testid="property-locked"/>}</div>{element.kind==='text'?<TextProperties element={element} product={product} update={update} disabled={disabled} onPending={onPending}/>:<ImageProperties {...props}/>}<ElementTools element={element} product={product} update={update} disabled={disabled}/></section>;
};