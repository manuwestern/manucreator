import { useState } from 'react';
import { ChevronDown,Check } from 'lucide-react';
import { Dialog,DialogContent,DialogTitle,DialogDescription } from '@/components/ui/dialog';
import { price,productImage } from '@/lib/studioApi';

export const BlankPicker=({products,product,onSelect,disabled})=>{
  const [open,setOpen]=useState(false);
  return <><button className="blank-picker-trigger" onClick={()=>setOpen(true)} disabled={disabled} data-testid="blank-picker-open"><img src={productImage(product.image)} alt=""/><span><strong data-testid="selected-product-name">{product.name}</strong><small data-testid="selected-material">{product.material} · {product.dimensions}</small></span><ChevronDown size={17}/></button><Dialog open={open} onOpenChange={setOpen}><DialogContent className="blank-picker-dialog" data-testid="blank-picker-dialog"><DialogTitle>Dein Rohling</DialogTitle><DialogDescription>Freigegebene Gravurflächen · Testprodukte und Beispielpreise</DialogDescription><div className="blank-picker-options">{products.map(p=><button key={p.id} onClick={()=>{onSelect(p);setOpen(false);}} aria-pressed={p.id===product.id} data-testid={`product-${p.id}`}><img src={productImage(p.image)} alt={p.name}/><span><strong>{p.name}</strong><small>{p.material} · {p.area_mm}</small><b>{price(p.price_cents)}</b></span>{p.id===product.id&&<Check size={17}/>}</button>)}</div></DialogContent></Dialog></>;
};