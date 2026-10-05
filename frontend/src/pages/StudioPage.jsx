import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Save, ShoppingBag, SquareDashed, RotateCcw, Maximize2, ShieldCheck, LoaderCircle, AlertCircle, Download, ArrowRight, Type, Undo2, Redo2 } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { useStudio } from '@/components/studio/StudioLayout';
import { BlankPicker } from '@/components/studio/BlankPicker';
import { DesignCanvas } from '@/components/studio/DesignCanvas';
import { LayerList } from '@/components/studio/LayerList';
import { LayerProperties } from '@/components/studio/LayerProperties';
import { LayerUpload } from '@/components/studio/LayerUpload';
import { TemplatePicker } from '@/components/studio/TemplatePicker';
import { TemplateFields } from '@/components/studio/TemplateFields';
import { ProductPreview } from '@/components/studio/ProductPreview';
import { DecorationPicker } from '@/components/studio/DecorationPicker';
import { configKey, emptyDesign, price, studioApi } from '@/lib/studioApi';
import { migrateDesign, newLayer, reframe, summarized } from '@/lib/studioLayers';
import { fitElement,imageFrame,isInside } from '@/lib/transformGeometry';
import '@/styles/studio-editor.css';
import '@/styles/studio-layers.css';
import '@/styles/studio-precision.css';
import '@/styles/studio-templates.css';
import '@/styles/studio-ornaments.css';

const LOCAL = 'manucreator-studio-design';
const stored = () => { try { return JSON.parse(localStorage.getItem(LOCAL)) || {}; } catch { return {}; } };

export default function StudioPage() {
  const { products, setCart } = useStudio(), navigate = useNavigate(), [params] = useSearchParams();
  const restoreId = useRef(stored().draftId);
  const [design, setDesign] = useState(() => { const previous=stored().design;const raw = previous || emptyDesign(products[0]?.id || 'holzscheibe'); const p = products.find(p => p.id === raw.product_id) || products[0]; return p ? previous?reframe(migrateDesign(raw,p),p):{...raw,editor_mode:'free',elements:[newLayer('text',p,{text:'Dein Unikat'.slice(0,p.max_text)})]} : { ...raw, elements: [] }; });
  const [draft, setDraft] = useState(null), [selected, setSelected] = useState(()=>design.elements.at(-1)?.id||null), [history, setHistory] = useState([]), [future, setFuture] = useState([]);
  const [candidate,setCandidate]=useState(null),[textPending,setTextPending]=useState(false),[mobilePanel,setMobilePanel]=useState('properties');
  const [simpleInvalid,setSimpleInvalid]=useState(false),[largePreview,setLargePreview]=useState(false),[templateRevision,setTemplateRevision]=useState(0);
  const [guides, setGuides] = useState(true), [action, setAction] = useState(''), [error, setError] = useState(''), [canvasReady, setCanvasReady] = useState(false);
  const canvasRef = useRef(null), saving = useRef(null), operation = useRef({id:0,type:null}), product = products.find(p => p.id === design.product_id) || products[0], busy = !!action||!!candidate;
  const key = configKey(summarized(design)), active = design.elements.find(e => e.id === selected);
  const invalidElements=design.elements.filter(e=>!isInside(e,product?.area||{x:0,y:0,w:800,h:800})||(e.kind==='text'&&e.text.length>(product?.max_text||60))||(e.kind==='image'&&product&&!product.templates.includes(e.image_type))||(e.kind==='image'&&e.image_ratio>0&&Math.abs(e.w/e.h/(e.image_ratio*e.crop.w/e.crop.h)-1)>.012));
  const incomplete=design.elements.some(e=>e.kind==='image'&&(e.placeholder||!e.asset_id));
  const valid = !invalidElements.length&&!incomplete&&!simpleInvalid&&design.elements.some(e => !e.hidden && (e.kind === 'text' ? e.text.trim() : e.kind==='decoration'?e.ornament:e.asset_id));
  const simple=design.editor_mode==='simple'&&!!design.template_id;
  useEffect(() => { document.title = 'Dein Gestaltungsstudio · ManuCreator'; document.body.classList.add('precision-workspace');const resize=()=>document.documentElement.style.setProperty('--studio-vh',`${window.visualViewport?.height||window.innerHeight}px`);resize();window.visualViewport?.addEventListener('resize',resize);window.addEventListener('resize',resize);return()=>{document.body.classList.remove('precision-workspace');window.visualViewport?.removeEventListener('resize',resize);window.removeEventListener('resize',resize);}; }, []);
  useEffect(() => { localStorage.setItem(LOCAL, JSON.stringify({ design, draftId: draft?.key === key ? draft.id : null })); }, [design,draft,key]);
  useEffect(() => { if (selected&&!design.elements.some(e=>e.id===selected))setSelected(design.elements.at(-1)?.id||null); }, [design.elements, selected]);
  useEffect(() => {
    const id = params.get('draft') || restoreId.current; if (!id) return;
    let alive = true; setAction('loading');
    studioApi(`/drafts/${id}`).then(data => {
      if (!alive) return;
      const current = products.find(p => p.id === data.design.product_id);
      if (!current) { setError('Dieser Rohling ist archiviert. Bitte wähle einen verfügbaren Rohling.'); return; }
      const migrated = migrateDesign(data.design,current), changed = data.product_snapshot && data.product_snapshot.version !== current.version;
      const next = changed ? reframe(migrated,current) : migrated;
      setDesign(next); setSelected(next.elements[next.elements.length-1]?.id || null); setHistory([]); setFuture([]);
      setDraft(changed || !data.design.elements ? null : { ...data, key: configKey(summarized(next)) });
      if (changed) setError('Der Rohling wurde aktualisiert. Deine Inhalte bleiben unverändert. Bitte die Gravurgrenzen prüfen und vor dem Abschluss erneut speichern.');
    }).catch(e => { if (alive) setError(e.message); }).finally(() => { if (alive) setAction(''); });
    return () => { alive = false; };
  }, [params,products]);
  const commit = next => { setHistory(old => [...old.slice(-29),design]); setFuture([]); setDesign(next); setError(''); };
  const updateElement = (id, changes) => commit({ ...design, elements: design.elements.map(e => e.id === id ? { ...e,...changes } : e) });
  const naturalSize=useCallback((id,w,h)=>{setDesign(old=>{const element=old.elements.find(e=>e.id===id);if(!element||element.kind!=='image'||element.image_ratio>0)return old;return{...old,elements:old.elements.map(e=>e.id===id?{...e,image_ratio:w/h}:e)};});},[]);
  const select=id=>{if(busy||textPending||simple)return;setSelected(id);if(id)setMobilePanel('properties');};
  const addText = () => { const e = newLayer('text',product); commit({ ...design,elements:[...design.elements,e] }); setSelected(e.id); };
  const addDecoration=item=>{
    if(design.elements.length>=12)return;
    const a=product.area,w=Math.min(a.w*.78,a.h*.78*item.ratio),h=w/item.ratio;
    const e=fitElement(newLayer('decoration',product,{ornament:item.id,field_label:item.name,stroke_width:Math.min(1.5,h*.12),x:a.x+(a.w-w)/2,y:a.y+(a.h-h)/2,w,h}),a);
    if(!isInside(e,a,0)){setError('Diese Dekoration passt nicht in die freigegebene Fläche.');return;}
    commit({...design,elements:[e,...design.elements]});setSelected(e.id);setMobilePanel('properties');
  };
  const addImage = asset => { const base = newLayer('image',product,{ asset_id:asset.id,image_ratio:asset.width/asset.height }); const e=imageFrame(base,asset.width/asset.height,product.area);commit({ ...design,elements:[e,...design.elements] }); setSelected(e.id);setMobilePanel('properties'); };
  const reorder = (id, shift) => { const elements = [...design.elements], index = elements.findIndex(e => e.id === id); if (index+shift<0 || index+shift>=elements.length) return; [elements[index],elements[index+shift]]=[elements[index+shift],elements[index]]; commit({ ...design,elements }); };
  const duplicate = id => { const e=design.elements.find(e=>e.id===id); const copy={...fitElement({...e,x:e.x+10,y:e.y+10},product.area),id:crypto.randomUUID(),locked:false}; commit({...design,elements:[...design.elements,copy]});setSelected(copy.id); };
  const remove = id => { commit({ ...design,elements:design.elements.filter(e=>e.id!==id) }); setSelected(null); };
  const undo = () => { if (!history.length) return;setFuture(old=>[design,...old]);setDesign(history[history.length-1]);setHistory(old=>old.slice(0,-1));setError(''); };
  const redo = () => { if (!future.length) return;setHistory(old=>[...old,design]);setDesign(future[0]);setFuture(old=>old.slice(1));setError(''); };
  const save = async () => {
    if (draft?.key===key && draft.product_snapshot?.version===product.version) return draft;
    if (saving.current?.key===key) return saving.current.promise;
    const promise=studioApi('/drafts',{method:'POST',body:summarized(design)}).then(result=>{const saved={...result,key};setDraft(saved);return saved;});
    saving.current={key,promise};
    try{return await promise;}finally{if(saving.current?.promise===promise)saving.current=null;}
  };
  const run = async type => {
    if(operation.current.type==='cart'||(operation.current.type==='save'&&type==='save'))return;
    const id=operation.current.id+1;operation.current={id,type};setAction(type);setError('');
    try{const saved=await save();if(type==='cart'){setCart(await studioApi('/cart',{method:'POST',body:{draft_id:saved.id,quantity:1}}));navigate('/warenkorb');}else if(operation.current.id===id)toast.success('Dein Entwurf ist gespeichert.');}
    catch(e){if(operation.current.id===id)setError(e.message);}
    finally{if(operation.current.id===id){operation.current={id,type:null};setAction('');}}
  };
  const download = () => { try {const a=document.createElement('a');a.download=`ManuCreator-${product.id}-Entwurf.png`;a.href=canvasRef.current.toDataURL();a.click();}catch{setError('Die Vorschau lädt noch. Bitte erneut versuchen.');} };
  if (!product) return <main className="studio-loading"><p data-testid="studio-no-products">Aktuell sind keine Rohlinge verfügbar.</p></main>;
  const viewDesign=candidate&&!candidate.showOriginal?{...design,elements:design.elements.map(e=>e.id===candidate.elementId?{...e,asset_id:candidate.result.id}:e)}:design;
  const editBusy=busy||textPending;
  return <main className={`precision-editor ${simple?'simple-editor':''}`} data-testid="precision-editor" data-editor-mode={simple?'simple':'free'}><div className="precision-topbar"><div className="workspace-title"><span className="eyebrow">MANUCREATOR STUDIO</span><h1 data-testid="studio-title">Dein Unikat.</h1></div><BlankPicker products={products} product={product} onSelect={p=>{commit(reframe(design,p));setDraft(null);}} disabled={editBusy}/><TemplatePicker product={product} hasDesign={design.elements.length>0} disabled={editBusy} onApply={next=>{commit(next);setSelected(next.elements[0]?.id||null);setMobilePanel('properties');setTemplateRevision(v=>v+1);setSimpleInvalid(false);}}/><span className="editor-live-label" data-testid="studio-preview-mode"><span/>{simple?'Einfach gestalten':'Frei gestalten'}</span></div>
    <div className="precision-workarea" data-mobile-panel={simple?'properties':mobilePanel}><aside className="precision-layers" data-testid="workspace-layers">{!simple&&<LayerList elements={design.elements} selected={selected} onSelect={select} updateElement={updateElement} reorder={reorder} duplicate={duplicate} remove={remove} disabled={editBusy}/>}</aside>
      <section className="precision-canvas" data-testid="workspace-canvas"><div className="editor-toolbar">{!simple&&<><button className="editor-add-button" title="Text hinzufügen" aria-label="Text hinzufügen" onClick={()=>{addText();setMobilePanel('properties');}} disabled={editBusy||design.elements.length>=12} data-testid="add-text-layer"><Type size={16}/><span>Text hinzufügen</span></button>{product.templates.some(t=>t!=='text')&&<LayerUpload disabled={editBusy||design.elements.length>=12} onUpload={addImage} onBusy={v=>setAction(v?'upload':'')} onError={setError}/>}<DecorationPicker disabled={editBusy||design.elements.length>=12} onAdd={addDecoration}/></>}{simple&&<span className="simple-toolbar-label" data-testid="simple-mode-label">Deine Vorlage · feste Gestaltung</span>}<div className="editor-history"><button onClick={undo} disabled={editBusy||!history.length} title="Rückgängig" aria-label="Rückgängig" data-testid="design-undo"><Undo2 size={17}/></button><button onClick={redo} disabled={editBusy||!future.length} title="Wiederholen" aria-label="Wiederholen" data-testid="design-redo"><Redo2 size={17}/></button></div></div>
      <div className="studio-stage"><DesignCanvas product={product} design={viewDesign} guides={guides} canvasRef={canvasRef} updateElement={updateElement} selected={simple?null:selected} onSelect={select} disabled={editBusy||simple} onReady={setCanvasReady} onNaturalSize={naturalSize}/>{action==='processing'&&<div className="canvas-processing" role="status" data-testid="canvas-processing"><LoaderCircle size={14} className="loading-spin"/>Freistellung läuft …</div>}<div className="studio-preview-tools"><button onClick={()=>setGuides(v=>!v)} aria-pressed={guides} title="Gravurfläche ein-/ausblenden" data-testid="toggle-guides"><SquareDashed size={16}/><span>Gravurfläche</span></button>{!simple&&<button onClick={()=>{const next={...emptyDesign(product.id),editor_mode:'free',elements:[newLayer('text',product,{text:'Dein Unikat'.slice(0,product.max_text)})]};commit(next);setSelected(next.elements[0].id);}} disabled={editBusy} title="Zurücksetzen" aria-label="Gestaltung zurücksetzen" data-testid="studio-reset"><RotateCcw size={16}/></button>}<button onClick={()=>setLargePreview(true)} disabled={editBusy||!canvasReady} title="Große Produktvorschau" aria-label="Produktvorschau öffnen" data-testid="product-preview-open"><Maximize2 size={16}/></button><button onClick={download} disabled={editBusy||!canvasReady||!valid} title="Vorschau herunterladen" aria-label="Vorschau herunterladen" data-testid="studio-download"><Download size={16}/></button></div></div><div className="studio-preview-caption"><span><ShieldCheck size={12}/>{invalidElements.length?'Gravurgrenzen prüfen':'Innerhalb deiner Gravurfläche'}</span><span data-testid="studio-area-size">{product.area_mm} · {product.area.shape==='circle'?'Kreis':'Rechteck'}</span></div></section>
      <div className="mobile-workspace-tabs" role="tablist" aria-label="Werkzeuge">{simple?<span data-testid="mobile-simple-label">Deine Inhalte</span>:<><button role="tab" aria-selected={mobilePanel==='layers'} onClick={()=>setMobilePanel('layers')} data-testid="mobile-tab-layers">Ebenen · {design.elements.length}</button><button role="tab" aria-selected={mobilePanel==='properties'} onClick={()=>setMobilePanel('properties')} data-testid="mobile-tab-properties">Eigenschaften</button></>}</div>
      <aside className="precision-properties" data-testid="workspace-properties">{simple?<TemplateFields key={`${design.template_id}-${templateRevision}`} design={design} product={product} updateElement={updateElement} disabled={busy} onPending={setTextPending} onInvalid={setSimpleInvalid} onFree={()=>{commit({...design,editor_mode:'free'});setSimpleInvalid(false);setMobilePanel('properties');}}/>:<LayerProperties key={active?.id||'none'} element={active} product={product} update={changes=>updateElement(active.id,changes)} disabled={busy} processing={action==='processing'} onPending={setTextPending} onBusy={v=>setAction(v?'processing':'')} onError={setError} candidate={candidate} onCandidate={setCandidate} onCompare={showOriginal=>setCandidate(old=>({...old,showOriginal}))} onAccept={()=>{updateElement(candidate.elementId,{asset_id:candidate.result.id,original_asset_id:candidate.result.original_id});setCandidate(null);}} onDiscard={()=>setCandidate(null)}/>}</aside>
    </div>{invalidElements.length>0&&<div className="precision-error" role="alert" data-testid="studio-invalid-design"><AlertCircle size={15}/><span>{invalidElements.length} Element(e) benötigen eine Korrektur von Größe, Position, Textlänge oder Bildformat. Originalinhalte bleiben erhalten; der Abschluss ist bis zur Korrektur gesperrt.{simple?' Bitte eine passende Vorlage wählen oder frei bearbeiten.':''}</span></div>}{incomplete&&<div className="precision-incomplete" data-testid="studio-incomplete-design">Bitte den Bildplatzhalter durch dein eigenes Foto oder Logo ersetzen.</div>}{error&&<div className="precision-error" role="alert" data-testid="studio-error"><AlertCircle size={15}/><span>{error}</span><button onClick={()=>setError('')} aria-label="Meldung schließen" data-testid="studio-error-dismiss">×</button></div>}{largePreview&&<ProductPreview product={product} design={viewDesign} onClose={()=>setLargePreview(false)}/>}
    <div className="precision-footer"><span className="save-state" data-testid="studio-save-status">{textPending?'Text wird gesetzt …':draft?.key===key?'Gespeichert':'Nicht gespeichert'}</span><Button variant="outline" onClick={()=>run('save')} disabled={editBusy||!valid||!canvasReady} data-testid="studio-save">{action==='save'?<LoaderCircle className="loading-spin" size={15}/>:<Save size={15}/>}<span>Speichern</span></Button><div className="precision-price"><strong data-testid="studio-example-price">{price(product.price_cents)}</strong><small>Beispielpreis · Testmodus</small></div><Button onClick={()=>run('cart')} disabled={(editBusy&&action!=='save')||!!candidate||textPending||!valid||!canvasReady} data-testid="studio-add-cart">{action==='cart'?<LoaderCircle className="loading-spin" size={15}/>:<ShoppingBag size={15}/>}<span>Test-Warenkorb</span><ArrowRight size={14}/></Button></div>
  </main>;
}