import { useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Save, ShoppingBag, SquareDashed, RotateCcw, Check, ShieldCheck, Info, LoaderCircle, AlertCircle, Download, ArrowRight, Type, Undo2, Redo2 } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { useStudio } from '@/components/studio/StudioLayout';
import { ProductPicker } from '@/components/studio/ProductPicker';
import { DesignCanvas } from '@/components/studio/DesignCanvas';
import { LayerList } from '@/components/studio/LayerList';
import { LayerProperties } from '@/components/studio/LayerProperties';
import { LayerUpload } from '@/components/studio/LayerUpload';
import { configKey, emptyDesign, price, studioApi } from '@/lib/studioApi';
import { migrateDesign, newLayer, reframe, summarized } from '@/lib/studioLayers';
import { constrain } from '@/lib/studioGeometry';
import '@/styles/studio-editor.css';
import '@/styles/studio-layers.css';

const LOCAL = 'manucreator-studio-design';
const stored = () => { try { return JSON.parse(localStorage.getItem(LOCAL)) || {}; } catch { return {}; } };

export default function StudioPage() {
  const { products, setCart } = useStudio(), navigate = useNavigate(), [params] = useSearchParams();
  const restoreId = useRef(stored().draftId);
  const [design, setDesign] = useState(() => { const raw = stored().design || emptyDesign(products[0]?.id || 'holzscheibe'); const p = products.find(p => p.id === raw.product_id) || products[0]; return p ? reframe(migrateDesign(raw,p),p) : { ...raw, elements: [] }; });
  const [draft, setDraft] = useState(null), [selected, setSelected] = useState(null), [history, setHistory] = useState([]), [future, setFuture] = useState([]);
  const [guides, setGuides] = useState(true), [action, setAction] = useState(''), [error, setError] = useState(''), [canvasReady, setCanvasReady] = useState(false);
  const canvasRef = useRef(null), product = products.find(p => p.id === design.product_id) || products[0], busy = !!action;
  const key = configKey(summarized(design)), active = design.elements.find(e => e.id === selected);
  const valid = design.elements.some(e => !e.hidden && (e.kind === 'text' ? e.text.trim() : e.asset_id));
  useEffect(() => { document.title = 'Dein Gestaltungsstudio · ManuCreator'; }, []);
  useEffect(() => { localStorage.setItem(LOCAL, JSON.stringify({ design, draftId: draft?.key === key ? draft.id : null })); }, [design,draft,key]);
  useEffect(() => { if (!selected && design.elements.length) setSelected(design.elements[design.elements.length-1].id); }, [design.elements, selected]);
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
      if (changed) setError('Der Rohling wurde aktualisiert. Bitte prüfe die Gravurfläche und speichere deinen Entwurf erneut.');
    }).catch(e => { if (alive) setError(e.message); }).finally(() => { if (alive) setAction(''); });
    return () => { alive = false; };
  }, [params,products]);
  const commit = next => { setHistory(old => [...old.slice(-29),design]); setFuture([]); setDesign(next); setError(''); };
  const updateElement = (id, changes) => commit({ ...design, elements: design.elements.map(e => e.id === id ? { ...e,...changes } : e) });
  const addText = () => { const e = newLayer('text',product); commit({ ...design,elements:[...design.elements,e] }); setSelected(e.id); };
  const addImage = asset => { const e = newLayer('image',product,{ asset_id:asset.id }); Object.assign(e,constrain({ ...e,h:e.w*asset.height/asset.width },product.area)); commit({ ...design,elements:[e,...design.elements] }); setSelected(e.id); };
  const reorder = (id, shift) => { const elements = [...design.elements], index = elements.findIndex(e => e.id === id); if (index+shift<0 || index+shift>=elements.length) return; [elements[index],elements[index+shift]]=[elements[index+shift],elements[index]]; commit({ ...design,elements }); };
  const duplicate = id => { const e=design.elements.find(e=>e.id===id); const copy={...e,id:crypto.randomUUID(),locked:false,...constrain({...e,x:e.x+10,y:e.y+10},product.area)}; commit({...design,elements:[...design.elements,copy]});setSelected(copy.id); };
  const remove = id => { commit({ ...design,elements:design.elements.filter(e=>e.id!==id) }); setSelected(null); };
  const undo = () => { if (!history.length) return;setFuture(old=>[design,...old]);setDesign(history[history.length-1]);setHistory(old=>old.slice(0,-1));setError(''); };
  const redo = () => { if (!future.length) return;setHistory(old=>[...old,design]);setDesign(future[0]);setFuture(old=>old.slice(1));setError(''); };
  const save = async () => { if (draft?.key===key && draft.product_snapshot?.version===product.version) return draft; const result=await studioApi('/drafts',{method:'POST',body:summarized(design)});const saved={...result,key};setDraft(saved);return saved; };
  const run = async type => {setAction(type);setError('');try{const saved=await save();if(type==='cart'){setCart(await studioApi('/cart',{method:'POST',body:{draft_id:saved.id,quantity:1}}));navigate('/warenkorb');}else toast.success('Dein Entwurf ist gespeichert.');}catch(e){setError(e.message);}finally{setAction('');}};
  const download = () => { try {const a=document.createElement('a');a.download=`ManuCreator-${product.id}-Entwurf.png`;a.href=canvasRef.current.toDataURL();a.click();}catch{setError('Die Vorschau lädt noch. Bitte erneut versuchen.');} };
  if (!product) return <main className="studio-loading"><p data-testid="studio-no-products">Aktuell sind keine Rohlinge verfügbar.</p></main>;
  return <main className="studio-main studio-wrap"><div className="studio-page-heading"><div><p className="eyebrow">DEINE IDEENWERKSTATT</p><h1 data-testid="studio-title">Aus einem Rohling wird <em>dein Unikat.</em></h1><p data-testid="studio-description">Dein Motiv. Deine Worte. Dein Lieblingsstück.</p></div><div className="studio-steps" data-testid="studio-step-indicator"><span className="active">01 Gestalten</span><i/><span>02 Warenkorb</span><i/><span>03 Testabschluss</span></div></div><div className="studio-workspace layered-workspace">
    <ProductPicker products={products} current={product.id} onSelect={p=>{commit(reframe(design,p));setDraft(null);}} disabled={busy}/>
    <section className="studio-preview" aria-label="Produktvorschau"><div className="studio-preview-heading"><div><span className="studio-material" data-testid="selected-material">{product.material}{product.is_sample?' · Muster':''}</span><h2 data-testid="selected-product-name">{product.name}</h2></div><span className="editor-live-label" data-testid="studio-preview-mode"><span/>Direktvorschau</span></div><div className="editor-toolbar"><button className="editor-add-button" onClick={addText} disabled={busy || design.elements.length>=12} data-testid="add-text-layer"><Type size={16}/>Text hinzufügen</button>{product.templates.some(t=>t!=='text') && <LayerUpload disabled={busy || design.elements.length>=12} onUpload={addImage} onBusy={v=>setAction(v?'upload':'')} onError={setError}/>}<div className="editor-history"><button onClick={undo} disabled={busy || !history.length} title="Rückgängig" aria-label="Rückgängig" data-testid="design-undo"><Undo2 size={17}/></button><button onClick={redo} disabled={busy || !future.length} title="Wiederholen" aria-label="Wiederholen" data-testid="design-redo"><Redo2 size={17}/></button></div></div>
    <div className="studio-stage"><div className="studio-stage-badges"><span data-testid="studio-canvas-badge">DEIN ENTWURF</span><span data-testid="studio-sample-dimensions">{product.dimensions}</span></div><DesignCanvas product={product} design={design} guides={guides} canvasRef={canvasRef} updateElement={updateElement} selected={selected} onSelect={setSelected} disabled={busy} onReady={setCanvasReady}/><div className="studio-preview-tools"><button onClick={()=>setGuides(v=>!v)} aria-pressed={guides} title="Gravurfläche ein-/ausblenden" data-testid="toggle-guides"><SquareDashed size={16}/><span>Gravurfläche</span></button><button onClick={()=>{const next=migrateDesign({...emptyDesign(product.id),text:'Dein Unikat'.slice(0,product.max_text),subtitle:''},product);commit(next);setSelected(next.elements[0].id);}} disabled={busy} title="Zurücksetzen" aria-label="Gestaltung zurücksetzen" data-testid="studio-reset"><RotateCcw size={16}/></button><button onClick={download} disabled={busy || !canvasReady} title="Vorschau herunterladen" aria-label="Vorschau herunterladen" data-testid="studio-download"><Download size={16}/></button></div></div><div className="studio-preview-caption"><span><Check size={14}/>Freie Gestaltung · feste Gravurgrenzen</span><span data-testid="studio-area-size">{product.area_mm} · {product.area.shape==='circle'?'Kreis':'Rechteck'}</span></div><div className="editor-bottom-actions"><Button variant="outline" onClick={()=>run('save')} disabled={busy || !valid} data-testid="studio-save">{action==='save'?<LoaderCircle className="loading-spin" size={15}/>:<Save size={15}/>}Entwurf speichern</Button><span data-testid="studio-save-status">{draft?.key===key?'Gespeichert':'Noch nicht gespeichert'}</span></div></section>
    <aside className="studio-right-column"><LayerList elements={design.elements} selected={selected} onSelect={setSelected} updateElement={updateElement} reorder={reorder} duplicate={duplicate} remove={remove} disabled={busy}/><LayerProperties key={active?.id || 'none'} element={active} product={product} update={changes=>updateElement(active.id,changes)} disabled={busy} onBusy={v=>setAction(v?'processing':'')} onError={setError}/><div className="studio-price"><span>Beispielpreis pro Stück<small>Testmodus · keine Zahlung</small></span><strong data-testid="studio-example-price">{price(product.price_cents)}</strong></div><Button className="studio-add-cart" onClick={()=>run('cart')} disabled={busy || !valid} data-testid="studio-add-cart">{action==='cart'?<LoaderCircle className="loading-spin" size={17}/>:<ShoppingBag size={17}/>}In den Test-Warenkorb<ArrowRight size={16}/></Button><div className="studio-production-note" data-testid="studio-production-note"><ShieldCheck size={18}/><p>Maße, Details und Materialeignung werden vor einer echten Fertigung gesondert geprüft.</p></div></aside>
  </div>{error && <div className="studio-error" role="alert" data-testid="studio-error"><AlertCircle size={18}/>{error}</div>}<div className="studio-reassurance"><span><Check size={15}/>Originalbilder bleiben erhalten</span><span><ShieldCheck size={15}/>Eigene Bilder nur in deinem Gastzugang</span><span><Info size={15}/>Kein Kauf und keine Fertigung im Testmodus</span></div></main>;
}