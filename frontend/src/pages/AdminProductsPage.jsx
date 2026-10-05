import { useCallback, useEffect, useRef, useState } from 'react';
import { Link,useParams,useNavigate,useLocation } from 'react-router-dom';
import { Archive, ArrowUpRight, LogOut, Pencil, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogTitle } from '@/components/ui/dialog';
import { AdminLogin } from '@/components/studio/AdminLogin';
import { BlankForm } from '@/components/studio/BlankForm';
import { AdminDecorationLibrary } from '@/components/studio/AdminDecorationLibrary';
import { AdminTemplateEditor } from '@/components/studio/AdminTemplateEditor';
import { adminApi } from '@/lib/adminApi';
import { price, productImage } from '@/lib/studioApi';
import '@/styles/studio.css';
import '@/styles/studio-editor.css';
import '@/styles/studio-layers.css';
import '@/styles/studio-precision.css';
import '@/styles/studio-templates.css';
import '@/styles/studio-ornaments.css';
import '@/styles/studio-admin-templates.css';

export default function AdminProductsPage() {
  const {productId,templateId}=useParams(),navigate=useNavigate(),location=useLocation();
  const [user, setUser] = useState(null), [ready, setReady] = useState(false), [products, setProducts] = useState([]), [editing, setEditing] = useState(undefined);
  const [error, setError] = useState(''), [notice, setNotice] = useState(''), [archive, setArchive] = useState(null), [busy, setBusy] = useState(false), revision = useRef(0);
  useEffect(() => { document.title = 'Rohlingverwaltung · ManuCreator'; adminApi('/auth/me').then(setUser).catch(e => { if (e.status !== 401) setError(e.message); }).finally(() => setReady(true)); }, []);
  const load = useCallback(async () => { const current = ++revision.current; try { const data = await adminApi('/products'); if (current === revision.current) setProducts(data); } catch(e) { if (current !== revision.current) return; setError(e.message); if (e.status === 401) setUser(null); } }, []);
  useEffect(() => { if (user) load(); }, [user, load]);
  const mergeProduct = product => { revision.current++; setProducts(items => items.some(item => item.id === product.id) ? items.map(item => item.id === product.id ? product : item) : [...items, product]); setError(''); };
  const saved = product => { mergeProduct(product); setEditing(undefined); setNotice('Artikel und Gravurfläche gespeichert.'); if(!productId)navigate(`/verwaltung/artikel/${product.id}`); };
  const archiveProduct = async () => { setBusy(true); try { const product = await adminApi(`/products/${archive.id}`, { method: 'DELETE' }); mergeProduct(product); setArchive(null); setNotice('Rohling archiviert. Gespeicherte Entwürfe bleiben erhalten.'); } catch(e) { setError(e.message); } finally { setBusy(false); } };
  const logout = async () => { try { await adminApi('/auth/logout', { method: 'POST' }); revision.current++; setUser(null); setEditing(undefined); setProducts([]); } catch(e) { setError(e.message); } };
  const current=products.find(p=>p.id===productId);
  return <div className="studio-shell admin-shell"><header className="studio-header"><div className="studio-wrap studio-header-inner"><Link to="/" data-testid="admin-home"><img src="/images/logo.png" alt="ManuCreator"/></Link><div className="admin-header-links">{user&&<><Link to="/verwaltung" data-testid="admin-nav-products">Artikel</Link><Link to="/verwaltung/dekorationen" data-testid="admin-nav-decorations">Dekorationen</Link></>}<Link to="/gestalten" data-testid="admin-open-studio">Studio<ArrowUpRight size={16}/></Link>{user && <button onClick={logout} data-testid="admin-logout"><LogOut size={16}/>Abmelden</button>}</div></div></header>
    <main className="studio-wrap admin-main">{error && <p role="alert" className="studio-error" data-testid="admin-error">{error}</p>}{!ready ? <p data-testid="admin-loading">Anmeldung wird geprüft …</p> : !user ? <AdminLogin onLogin={value => { setUser(value); setError(''); }}/> : location.pathname==='/verwaltung/dekorationen'?<AdminDecorationLibrary/>:productId?current?templateId?<AdminTemplateEditor key={templateId} product={current} identity={templateId}/>:<><BlankForm key={current.id} product={current} onClose={()=>navigate('/verwaltung')} onSaved={saved}/>{notice&&<p role="status" className="admin-notice" data-testid="admin-article-saved">{notice}</p>}</>:<p data-testid="admin-product-loading">Artikel wird geladen …</p>:editing !== undefined ? <BlankForm key={editing?.id || 'new'} product={editing} onClose={() => setEditing(undefined)} onSaved={saved}/> : <>
      <div className="admin-section-heading"><div><p className="eyebrow">DEINE WERKSTATT</p><h1>Rohlinge & Möglichkeiten.</h1></div><Button onClick={() => { setEditing(null); setNotice(''); }} data-testid="admin-new-product"><Plus size={17}/>Neuer Rohling</Button></div>{notice && <p role="status" className="admin-notice" data-testid="admin-notice">{notice}</p>}
      <div className="admin-products">{products.map(product => <article key={product.id} className="admin-product" data-testid={`admin-product-${product.id}`}><img src={productImage(product.image)} alt={product.name}/><div className="admin-product-info"><span className={product.active ? 'status-active' : 'status-archived'} data-testid={`admin-status-${product.id}`}>{product.active ? 'Im Studio sichtbar' : 'Archiviert'}</span><h2>{product.name}</h2><p>{product.material} · {product.dimensions}</p><p data-testid={`admin-bounds-${product.id}`}>{product.area.shape === 'circle' ? 'Kreis' : 'Rechteck'} · {product.area_mm}</p><strong data-testid={`admin-price-${product.id}`}>{price(product.price_cents)} <small>Beispielpreis</small></strong><div className="admin-product-actions"><button onClick={() => navigate(`/verwaltung/artikel/${product.id}`)} data-testid={`admin-edit-${product.id}`}><Pencil size={15}/>Bearbeiten</button>{product.active && <button onClick={() => setArchive(product)} title="Archivieren" aria-label={`${product.name} archivieren`} data-testid={`admin-archive-${product.id}`}><Archive size={16}/></button>}</div></div></article>)}</div>
    </>}</main><Dialog open={!!archive} onOpenChange={open => { if (!open && !busy) setArchive(null); }}><DialogContent data-testid="archive-confirm"><DialogTitle>Rohling archivieren?</DialogTitle><DialogDescription>{archive?.name} wird aus der Auswahl entfernt. Bereits gespeicherte Entwürfe und Testbestellungen bleiben erhalten.</DialogDescription><Button onClick={archiveProduct} disabled={busy} data-testid="archive-confirm-submit">Archivieren</Button><Button variant="outline" onClick={() => setArchive(null)} disabled={busy} data-testid="archive-cancel">Abbrechen</Button></DialogContent></Dialog></div>;
}