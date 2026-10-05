import { useEffect,useState } from 'react';
import { LayoutTemplate,ArrowLeft,LoaderCircle,Search } from 'lucide-react';
import { Dialog,DialogContent,DialogTitle,DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { studioApi,productImage } from '@/lib/studioApi';
import '@/styles/studio-controls-fixes.css';

export const TemplatePicker=({product,hasDesign,disabled,onApply})=>{
  const [open,setOpen]=useState(false),[items,setItems]=useState(null),[chosen,setChosen]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState(''),[search,setSearch]=useState('');
  useEffect(()=>{if(!open)return;let alive=true;setItems(null);setError('');studioApi(`/templates?product_id=${encodeURIComponent(product.id)}`).then(data=>{if(alive)setItems(data.items);}).catch(e=>{if(alive)setError(e.message);});return()=>{alive=false;};},[open,product.id]);
  const apply=async item=>{setBusy(true);setError('');try{const design=await studioApi(item.own?`/article-templates/${item.id}/apply`:`/templates/${item.id}/apply`,{method:'POST',...(item.own?{}:{body:{product_id:product.id}})});onApply(design);setOpen(false);setChosen(null);}catch(e){setError(e.message);}finally{setBusy(false);}};
  const filtered=(items||[]).filter(i=>i.name.toLocaleLowerCase('de').includes(search.toLocaleLowerCase('de')));
  return <>
    <button className="template-picker-trigger" disabled={disabled} onClick={()=>{setOpen(true);setChosen(null);setSearch('');}} data-testid="template-picker-open"><LayoutTemplate size={17}/><span>Vorlagen</span></button>
    <Dialog open={open} onOpenChange={v=>{if(!busy)setOpen(v);}}><DialogContent className="template-picker-dialog" data-testid="template-picker-dialog">
      <DialogTitle>{chosen?'Gestaltung ersetzen?':'Deine Vorlage'}</DialogTitle>
      <DialogDescription>{chosen?'Die aktuelle Gestaltung wird ersetzt. Rückgängig stellt den bisherigen Entwurf wieder her.':`${product.name} · ${product.material}`}</DialogDescription>
      {chosen?<div className="template-confirm">
        <img src={productImage(chosen.preview)} alt={chosen.name} data-testid="template-confirm-preview"/>
        <strong data-testid="template-confirm-name">{chosen.name}</strong>
        <Button disabled={busy} onClick={()=>apply(chosen)} data-testid="template-confirm-replace">{busy&&<LoaderCircle size={15} className="loading-spin"/>}Gestaltung ersetzen</Button>
        <Button variant="outline" disabled={busy} onClick={()=>setChosen(null)} data-testid="template-confirm-cancel"><ArrowLeft size={14}/>Zurück</Button>
      </div>:<>
        <div className="template-filters"><label className="template-search"><Search size={16}/><input type="search" placeholder="Vorlage suchen …" aria-label="Vorlagennamen suchen" value={search} onChange={e=>setSearch(e.target.value)} data-testid="template-search"/></label><p data-testid="template-result-count">{items?`${filtered.length} passende Vorlagen`:'Vorlagen laden …'}</p></div>
        <div className="template-options" data-testid="template-results">
          {items?filtered.length?filtered.map(item=><button key={item.id} onClick={()=>hasDesign?setChosen(item):apply(item)} disabled={busy} data-testid={`template-${item.id}`}>
            <div className="template-card-image" data-testid={`template-image-frame-${item.id}`}><img loading="lazy" src={productImage(item.preview)} alt={`${item.name} auf ${product.name}`} data-testid={`template-preview-${item.id}`}/></div>
            <div className="template-card-meta"><span>{item.own?'Artikelvorlage':'Schlichte Grundvorlage'}</span><strong>{item.name}</strong></div>
          </button>):<p data-testid="templates-empty">Keine passende Vorlage. Du kannst deinen Artikel frei gestalten.</p>:<p role="status" data-testid="templates-loading">Vorlagen werden vorbereitet …</p>}
        </div>
      </>}
      {error&&<p className="property-error" role="alert" data-testid="template-error">{error}</p>}
    </DialogContent></Dialog>
  </>;
};