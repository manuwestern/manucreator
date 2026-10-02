import { useEffect, useState } from 'react';
import { Menu, X, Send, ArrowUpRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

const links = [['Leistungen', '#leistungen'], ['Beispiele', 'examples'], ['Ablauf', '#ablauf'], ['Über mich', 'about'], ['Kontakt', '#kontakt']];
export const Logo = ({ footer = false }) => <a href="#start" className="brand" aria-label="ManuCreator – zur Startseite" data-testid={`${footer ? 'footer' : 'header'}-logo`}><img src="/images/logo.png" alt="ManuCreator – Ideen. Laser. Unikate." width="291" height="78" /></a>;

export const Header = ({ onRequest, onContent }) => {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  useEffect(() => {
    const scroll = () => setScrolled(window.scrollY > 25);
    scroll(); window.addEventListener('scroll', scroll, { passive: true });
    const escape = e => { if (e.key === 'Escape') setMenuOpen(false); };
    window.addEventListener('keydown', escape);
    return () => { window.removeEventListener('scroll', scroll); window.removeEventListener('keydown', escape); };
  }, []);
  const activate = target => { setMenuOpen(false); onContent({ type: target }); };
  return (
    <header className={`site-header ${scrolled ? 'scrolled' : ''} ${menuOpen ? 'menu-open' : ''}`} data-testid="site-header">
      <div className="header-inner wrap">
        <Logo />
        <nav className="desktop-nav" aria-label="Hauptnavigation">
          {links.map(([label, target]) => target[0] === '#' ? <a key={target} href={target} data-testid={`nav-${target.slice(1)}`}>{label}</a> : <button key={target} onClick={() => activate(target)} data-testid={`nav-${target}`}>{label}</button>)}
        </nav>
        <Button className="pill header-cta" onClick={onRequest} data-testid="header-inquiry-button"><Send size={15} fill="currentColor" />Anfrage starten<ArrowUpRight className="cta-arrow" /></Button>
        <button className="mobile-toggle" data-testid="mobile-menu-toggle" aria-label={menuOpen ? 'Menü schließen' : 'Menü öffnen'} aria-expanded={menuOpen} aria-controls="mobile-menu" onClick={() => setMenuOpen(!menuOpen)}>{menuOpen ? <X /> : <Menu />}</button>
      </div>
      {menuOpen && <nav className="mobile-nav" id="mobile-menu" aria-label="Mobile Navigation" data-testid="mobile-navigation">{links.map(([label, target]) => target[0] === '#' ? <a key={target} href={target} onClick={() => setMenuOpen(false)} data-testid={`mobile-nav-${target.slice(1)}`}>{label}<ArrowUpRight size={18} /></a> : <button key={target} onClick={() => activate(target)} data-testid={`mobile-nav-${target}`}>{label}<ArrowUpRight size={18} /></button>)}<Button className="pill" onClick={() => { setMenuOpen(false); onRequest(); }} data-testid="mobile-inquiry-button"><Send size={16} />Anfrage starten</Button></nav>}
    </header>
  );
};

export const Footer = ({ onContent }) => (
  <footer className="site-footer">
    <div className="wrap">
      <div className="footer-main">
        <Logo footer />
        <nav aria-label="Fußnavigation"><a href="#leistungen" data-testid="footer-services">Leistungen</a><button onClick={() => onContent({ type: 'examples' })} data-testid="footer-examples">Beispiele</button><button onClick={() => onContent({ type: 'about' })} data-testid="footer-about">Über mich</button><a href="#kontakt" data-testid="footer-contact">Kontakt</a></nav>
        <div className="footer-signoff" data-testid="footer-tagline"><span>Mit Ideen. Mit Präzision. Mit Herz.</span><span>Kreativität in Materialform.</span></div>
      </div>
      <div className="footer-bottom"><p data-testid="copyright">© {new Date().getFullYear()} ManuCreator — Alle Rechte vorbehalten.</p><div><button data-testid="footer-imprint" onClick={() => onContent({ type: 'imprint' })}>Impressum</button><button data-testid="footer-privacy" onClick={() => onContent({ type: 'privacy' })}>Datenschutz</button><a href="#start" data-testid="back-to-top" aria-label="Zurück nach oben"><ArrowUpRight size={17} /></a></div></div>
    </div>
  </footer>
);