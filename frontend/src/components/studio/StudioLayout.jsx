import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { Link, NavLink, Outlet } from 'react-router-dom';
import { ArrowLeft, ShoppingBag, FlaskConical, RefreshCw, LoaderCircle } from 'lucide-react';
import { Toaster } from 'sonner';
import { studioApi } from '@/lib/studioApi';
import '@/styles/studio.css';

const Context = createContext(null);
export const useStudio = () => useContext(Context);

export const StudioLayout = () => {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState({ items: [], count: 0, total_cents: 0 });
  const [error, setError] = useState('');
  const [ready, setReady] = useState(false);
  const refreshCart = async () => { const data = await studioApi('/cart'); setCart(data); return data; };
  const load = useCallback(async () => {
    setError('');
    try { const [catalog, basket] = await Promise.all([studioApi('/products'), studioApi('/cart')]); setProducts(catalog.products); setCart(basket); setReady(true); }
    catch (err) { setError(err.message); }
  }, []);
  useEffect(() => { load(); }, [load]); // Initial guest/catalog load; not an AI call.
  return <Context.Provider value={{ products, cart, setCart, refreshCart }}><div className="studio-shell" data-testid="studio-shell">
    <header className="studio-header"><div className="studio-wrap studio-header-inner"><Link to="/" data-testid="studio-home" aria-label="Zur ManuCreator-Startseite"><img src="/images/logo.png" alt="ManuCreator" width="205" height="55" /></Link><nav aria-label="Gestaltungsbereich"><NavLink to="/gestalten" data-testid="studio-nav-design">Gestaltungsstudio</NavLink><Link to="/#leistungen" data-testid="studio-nav-materials">Materialien</Link></nav><Link className="studio-cart-link" to="/warenkorb" data-testid="studio-cart-link"><ShoppingBag size={18} /><span>Warenkorb</span><b data-testid="studio-cart-count">{cart.count}</b></Link></div></header>
    <div className="studio-test-banner" data-testid="studio-test-banner"><FlaskConical size={14} /><strong>Musterstudio</strong><span>Testprodukte & Beispielpreise · Keine Zahlung. Keine Fertigung.</span></div>
    {!ready ? <main className="studio-loading">{error ? <><p role="alert" data-testid="studio-load-error">{error}</p><button onClick={load} data-testid="studio-load-retry"><RefreshCw size={16} />Erneut versuchen</button></> : <><LoaderCircle className="loading-spin" size={24} /><p data-testid="studio-loading">Deine Werkbank wird vorbereitet …</p></>}</main> : <Outlet />}
    <footer className="studio-footer studio-wrap"><Link to="/" data-testid="studio-back-home"><ArrowLeft size={14} />Zurück zu ManuCreator</Link><p data-testid="studio-footer-note">Mit Ideen. Mit Präzision. Mit Herz.</p><nav><Link to="/impressum" data-testid="studio-imprint">Impressum</Link><Link to="/datenschutz" data-testid="studio-privacy">Datenschutz</Link><Link to="/agb" data-testid="studio-terms">AGB</Link></nav></footer>
    <Toaster position="bottom-right" richColors />
  </div></Context.Provider>;
};