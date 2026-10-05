import { LockKeyhole } from 'lucide-react';
import { ElementTools } from './ElementTools';
import { TextProperties } from './TextProperties';
import { ImageProperties } from './ImageProperties';
import { DecorationProperties } from './DecorationProperties';
import { ShapeProperties } from './ShapeProperties';

export const LayerProperties=props=>{
  const {element,product,update,disabled,onPending}=props;
  if(!element)return <div className="property-empty" data-testid="layer-no-selection">Wähle eine Ebene aus.</div>;
  return <section className="layer-properties"><div className="property-title"><h2 data-testid="layer-properties-heading">{element.kind==='text'?'Text & Schrift':element.kind==='shape'?'Formeigenschaften':element.kind==='decoration'?'Rahmen & Ornament':'Bild & Zuschnitt'}</h2>{element.locked&&<LockKeyhole size={15} data-testid="property-locked"/>}</div>{element.kind==='text'?<TextProperties element={element} product={product} update={update} disabled={disabled} onPending={onPending}/>:element.kind==='shape'?<ShapeProperties element={element} product={product} update={update} disabled={disabled}/>:element.kind==='decoration'?<DecorationProperties element={element} product={product} update={update} disabled={disabled}/>:<ImageProperties {...props}/>}<ElementTools element={element} product={product} update={update} disabled={disabled} hideSize={element.kind==='shape'}/></section>;
};