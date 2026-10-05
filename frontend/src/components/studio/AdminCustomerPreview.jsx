import { useState } from 'react';
import { Dialog,DialogContent,DialogTitle,DialogDescription } from '@/components/ui/dialog';
import { DesignCanvas } from './DesignCanvas';
import { TemplateFields } from './TemplateFields';

export const AdminCustomerPreview=({design,product,onClose})=>{
  const [preview,setPreview]=useState(design),[pending,setPending]=useState(false),[invalid,setInvalid]=useState(false);
  return <Dialog open onOpenChange={v=>{if(!v)onClose();}}><DialogContent className="admin-customer-preview" data-testid="admin-customer-preview"><DialogTitle>Kundenvorschau · {product.name}</DialogTitle><DialogDescription>{design.allow_free_edit?'Freie Bearbeitung zusätzlich erlaubt':'Nur freigegebene Kundenfelder'}</DialogDescription><div className="admin-preview-layout"><div className="admin-preview-canvas"><DesignCanvas product={product} design={preview} guides={false} readOnly adminMode/></div><div className="admin-preview-fields"><TemplateFields design={preview} product={product} updateElement={(id,changes)=>setPreview(old=>({...old,elements:old.elements.map(e=>e.id===id?{...e,...changes}:e)}))} onPending={setPending} onInvalid={setInvalid} showFree={false} adminPreview/>{(pending||invalid)&&<p data-testid="admin-preview-field-status">{pending?'Vorschau wird aktualisiert …':'Bitte Eingaben prüfen.'}</p>}</div></div></DialogContent></Dialog>;
};