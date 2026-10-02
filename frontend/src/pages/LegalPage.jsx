import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, ArrowUpRight, Download, Printer, FileText, Info } from 'lucide-react';
import { legalDate, legalNavigation, company } from '@/data/legal/company';
import { withdrawalForm } from '@/data/legal/withdrawal';
import { documentAsText, downloadLegalText } from '@/lib/legalDownloads';
import { LegalSection } from '@/components/legal/LegalSection';
import '@/styles/legal.css';

export default function LegalPage({ document }) {
  useEffect(() => {
    const previous = window.document.title;
    window.document.title = `${document.title} · ManuCreator`;
    return () => { window.document.title = previous; };
  }, [document.title]);
  return <div className="legal-page" data-testid={`legal-page-${document.key}`}>
    <header className="legal-header"><div className="legal-wrap legal-header-inner">
      <Link to="/" data-testid="legal-home-logo" aria-label="ManuCreator – Startseite"><img src="/images/logo.png" alt="ManuCreator – Ideen. Laser. Unikate." width="205" height="55" /></Link>
      <Link to="/" className="legal-home-link" data-testid="legal-back-home"><ArrowLeft size={16} />Zur Startseite</Link>
    </div></header>
    <main className="legal-wrap legal-main">
      <nav className="legal-tabs" aria-label="Rechtliche Informationen">{legalNavigation.map(item => <Link to={item.path} className={item.key === document.key ? 'active' : ''} aria-current={item.key === document.key ? 'page' : undefined} key={item.key} data-testid={`legal-tab-${item.key}`}>{item.label}</Link>)}</nav>
      <div className="legal-heading"><p className="eyebrow" data-testid="legal-eyebrow">MANUCREATOR · RECHTLICHES</p><h1 data-testid="legal-title">{document.title}</h1><p data-testid="legal-subtitle">{document.subtitle}</p><div className="legal-meta"><span data-testid="legal-date">Stand: {legalDate}</span><span data-testid="legal-draft-status">Entwurf zur Prüfung</span></div></div>
      <div className="legal-toolbar"><button onClick={() => window.print()} data-testid="legal-print" title="Drucken oder als PDF speichern"><Printer size={16} />Drucken / PDF</button><button onClick={() => downloadLegalText(`ManuCreator-${document.key}-Entwurf.txt`, documentAsText(document))} data-testid="legal-download"><Download size={16} />Text herunterladen</button>{document.key === 'withdrawal' && <button onClick={() => downloadLegalText('ManuCreator-Muster-Widerrufsformular.txt', withdrawalForm)} data-testid="withdrawal-form-download"><FileText size={16} />Musterformular</button>}</div>
      <aside className="legal-draft-notice" data-testid="legal-draft-notice"><Info size={18} /><p>{document.note}</p></aside>
      <div className="legal-document-layout"><aside className="legal-toc"><p className="eyebrow" data-testid="legal-toc-title">AUF DIESER SEITE</p><nav aria-label="Inhaltsverzeichnis">{document.sections.map(section => <a href={`#${section.id}`} key={section.id} data-testid={`legal-toc-${section.id}`}>{section.title}</a>)}</nav></aside><article className="legal-article">{document.sections.map(section => <LegalSection key={section.id} section={section} documentKey={document.key} />)}</article></div>
      <div className="legal-contact"><p data-testid="legal-contact-label">Fragen oder ein Anliegen?</p><a href={`mailto:${company.email}`} data-testid="legal-contact-email">{company.email}<ArrowUpRight size={18} /></a></div>
    </main>
    <footer className="legal-page-footer"><div className="legal-wrap"><p data-testid="legal-copyright">© {new Date().getFullYear()} ManuCreator · Manuel Bayer</p><nav aria-label="Rechtliche Fußnavigation">{legalNavigation.map(item => <Link key={item.key} to={item.path} data-testid={`legal-footer-${item.key}`}>{item.label}</Link>)}</nav></div></footer>
  </div>;
}