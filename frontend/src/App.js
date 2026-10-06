import { useState } from 'react';
import { Type, ImagePlus, Shapes, PanelsTopLeft, Layers, CheckCircle2, CircleHelp, ChevronRight, Undo2, Redo2, Maximize, Minimize, Eye, Leaf, Move, ArrowLeft, Download, Check, Loader2 } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './components/ui/dialog';
import { Toaster, toast } from './components/ui/sonner';
import { ToolPanel } from './components/editor/ToolPanel';
import { EngravingCanvas } from './components/editor/EngravingCanvas';
import { useEditor } from './hooks/useEditor';
import './App.css';

const tools = [['edit', 'Text', Type], ['image', 'Bild', ImagePlus], ['motifs', 'Motive', Shapes], ['templates', 'Vorlagen', PanelsTopLeft], ['layers', 'Ebenen', Layers]];

function App() {
  const editor = useEditor();
  const [panel, setPanel] = useState(() => editor.selected?.type === 'text' ? 'curve' : 'actions');
  const [expanded, setExpanded] = useState(false);
  const [modal, setModal] = useState(null);
  const [downloading, setDownloading] = useState(false);
  const openTool = tool => {
    setExpanded(false);
    if (tool === 'edit' && editor.selected?.type !== 'text') {
      const text = editor.objects.find(o => o.type === 'text');
      if (text) editor.select(text.id);
    }
    setPanel(tool);
  };
  const exportDesign = async () => {
    setDownloading(true);
    try {
      const svg = document.querySelector('[data-testid="preview-canvas"]').cloneNode(true);
      svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg'); svg.setAttribute('width', '1600'); svg.setAttribute('height', '1600');
      for (const image of svg.querySelectorAll('image')) {
        const source = image.getAttribute('href');
        if (source && !source.startsWith('data:')) {
          const blob = await (await fetch(source)).blob();
          const data = await new Promise((resolve, reject) => { const reader = new FileReader(); reader.onload = () => resolve(reader.result); reader.onerror = reject; reader.readAsDataURL(blob); });
          image.setAttribute('href', data);
        }
      }
      const blob = new Blob([new XMLSerializer().serializeToString(svg)], { type: 'image/svg+xml;charset=utf-8' });
      const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = 'mein-manucreator-unikat.svg'; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
      toast.success('Dein Design wurde heruntergeladen.');
    } catch (_) { toast.error('Das Herunterladen hat nicht geklappt. Bitte versuche es erneut.'); }
    finally { setDownloading(false); }
  };
  return <div className={`editor-app ${panel && !expanded ? 'is-editing' : ''} ${expanded ? 'is-expanded' : ''}`} data-testid="editor-app">
    <header className="app-header"><div className="brand-lockup"><span className="wordmark" data-testid="brand-logo">ManuCreator</span><span className="brand-tagline" data-testid="brand-tagline">DAS WIRD DEIN UNIKAT.</span></div><div className="header-center" data-testid="studio-label"><span />Dein kleines Kreativstudio</div><div className="header-right"><span className="save-status" data-testid="save-status" title="Lokal auf diesem Gerät gespeichert">{editor.saveState === 'saved' ? <CheckCircle2 size={17} /> : editor.saveState === 'saving' ? <Loader2 size={16} className="spin" /> : <CircleHelp size={17} />}<span>{editor.saveState === 'saved' ? 'Gespeichert' : editor.saveState === 'saving' ? 'Speichert …' : 'Nicht gespeichert'}</span></span><button className="header-help" data-testid="help-button" aria-label="Hilfe öffnen" onClick={() => setModal('help')}><CircleHelp size={20} /></button></div></header>
    <div className="editor-body">
      <nav className="tool-navigation" aria-label="Gestaltungswerkzeuge" data-testid="tool-navigation"><span className="nav-caption" data-testid="tools-label">GESTALTEN</span>{tools.map(([id, name, Icon]) => <button className={`nav-tool ${(panel === id || (id === 'edit' && ['curve', 'actions'].includes(panel) && editor.selected?.type === 'text')) ? 'active' : ''}`} key={id} data-testid={`nav-${id}`} onClick={() => openTool(id)} aria-pressed={panel === id}><Icon size={23} strokeWidth={1.5} /><span>{name}</span></button>)}<div className="nav-bottom-mark"><Leaf size={23} strokeWidth={1.2} /></div></nav>
      <main className="workspace" data-testid="workspace">
        <button className="product-bar" data-testid="product-details-button" onClick={() => setModal('product')}><span className="product-thumbnail"><img src="/images/wood-slice.webp" alt="Naturbelassene Holzscheibe" /></span><span className="product-info"><strong data-testid="product-name">Holzscheibe</strong><span data-testid="product-material">Birkenholz <span className="dot">·</span> Ø 22 cm</span></span><span className="product-natural" data-testid="natural-product-badge"><Leaf size={14} />Ein Stück Natur</span><span className="product-details-text">Produktdetails</span><ChevronRight size={18} /></button>
        <section className="canvas-workspace" data-testid="canvas-workspace">
          <div className="canvas-toolbar"><div className="history-buttons"><button className="canvas-button" data-testid="undo-button" aria-label="Rückgängig" title="Rückgängig" disabled={!editor.canUndo} onClick={editor.undo}><Undo2 size={20} /></button><button className="canvas-button" data-testid="redo-button" aria-label="Wiederholen" title="Wiederholen" disabled={!editor.canRedo} onClick={editor.redo}><Redo2 size={20} /></button></div><span className="canvas-kicker" data-testid="canvas-kicker">DEINE IDEE NIMMT FORM AN</span><button className="canvas-button expand-button" data-testid="expand-button" aria-label={expanded ? 'Zur Bearbeitung zurückkehren' : 'Arbeitsfläche vergrößern'} title={expanded ? 'Zur Bearbeitung' : 'Arbeitsfläche vergrößern'} onClick={() => setExpanded(!expanded)}>{expanded ? <Minimize size={20} /> : <Maximize size={20} />}</button></div>
          <EngravingCanvas editor={editor} onSelect={o => { if (!panel || (panel === 'curve' && o.type !== 'text')) { setPanel('actions'); setExpanded(false); } }} />
          <div className="canvas-caption" data-testid="canvas-caption"><span><Move size={14} />Elemente direkt auf dem Holz verschieben</span><span className="size-label">Ø 22 cm <span>·</span> Originalgröße angepasst</span></div>
        </section>
      </main>
      {panel && !expanded ? <ToolPanel editor={editor} panel={panel} setPanel={setPanel} /> : !expanded && <aside className="resting-panel" data-testid="resting-panel"><span className="eyebrow">VON DIR. FÜR IMMER.</span><h2>Sieht nach dir aus.</h2><p>Dein Unikat ist so persönlich wie die Geschichte dahinter.</p><button className="outline-button" data-testid="continue-editing" onClick={() => setPanel('actions')}><ArrowLeft size={17} />Weiter gestalten</button><div className="resting-illustration"><Leaf size={75} strokeWidth={.7} /></div><p className="small-note">Noch ein letzter Blick?<br />Entdecke dein Design in der Vorschau.</p></aside>}
    </div>
    <footer className="app-footer" data-testid="app-footer"><div className="footer-promise" data-testid="footer-promise"><span className="promise-icon"><Leaf size={21} strokeWidth={1.3} /></span><div><strong>Von Natur aus einzigartig.</strong><span>Mit deinen Ideen wird es persönlich.</span></div></div><div className="checkout-summary"><div className="price-block"><span className="price" data-testid="product-price">24,90 <span>€</span></span><span className="price-note" data-testid="price-note">Beispielpreis · Testmodus</span></div><button className="preview-button" data-testid="preview-button" onClick={() => setModal('preview')}><Eye size={20} /><span>Vorschau</span><ChevronRight size={17} /></button></div></footer>
    <Dialog open={!!modal} onOpenChange={open => { if (!open) setModal(null); }}><DialogContent className={`editor-dialog ${modal === 'preview' ? 'preview-dialog' : ''}`} data-testid={`${modal || 'closed'}-dialog`}><DialogHeader><DialogTitle data-testid="dialog-title">{modal === 'preview' ? 'Dein ganz persönliches Unikat.' : modal === 'product' ? 'Ein Stück Natur für deine Ideen.' : 'Alles im Griff. Mit einem Fingertipp.'}</DialogTitle><DialogDescription data-testid="dialog-description">{modal === 'preview' ? 'So sieht deine Gestaltung aus – ohne Hilfslinien.' : modal === 'product' ? 'Holzscheibe · Birkenholz · Ø 22 cm' : 'Ein paar kleine Tipps für dein großes Unikat.'}</DialogDescription></DialogHeader>
      {modal === 'preview' && <><div className="preview-stage"><EngravingCanvas editor={editor} preview /></div><p className="small-note" data-testid="preview-natural-note">Holz ist ein Naturprodukt. Maserung, Farbe und Form können variieren.</p><button className="preview-button download-button" data-testid="download-design" disabled={downloading} onClick={exportDesign}>{downloading ? <Loader2 size={18} /> : <Download size={18} />}Design herunterladen</button></>}
      {modal === 'product' && <div className="product-dialog-content"><img src="/images/wood-slice.webp" alt="Holzscheibe mit natürlicher Rinde" /><p data-testid="product-description">Eine natürliche Holzscheibe mit charaktervoller Rinde. Gestalte sie mit deinen Worten, einem Motiv oder deinem eigenen Bild.</p><div className="product-facts" data-testid="product-facts"><span>Material<strong>Birkenholz</strong></span><span>Durchmesser<strong>ca. 22 cm</strong></span><span>Oberfläche<strong>Naturbelassen</strong></span></div></div>}
      {modal === 'help' && <div className="help-content" data-testid="help-content">{[['1', 'Auswählen & verschieben', 'Tippe auf einen Text oder ein Motiv. Verschiebe es direkt auf dem Holz; die Eckpunkte ändern die Größe.'], ['2', 'Worten eine Form geben', 'Unter Wölbung kannst du den großen Regler ziehen oder mit Plus und Minus feinjustieren.'], ['3', 'Alles an seinem Platz', 'Unter Ebenen änderst du die Reihenfolge, blendest Elemente aus oder sperrst sie.'], ['4', 'Dein Design bleibt bei dir', 'Deine Gestaltung wird in diesem Browser gespeichert. Lade sie in der Vorschau als SVG herunter.']].map(([n, title, text]) => <div key={n}><span>{n}</span><section><h3>{title}</h3><p>{text}</p></section></div>)}<button className="outline-button" data-testid="help-close" onClick={() => setModal(null)}><Check size={17} />Alles klar, los geht’s</button></div>}
    </DialogContent></Dialog>
    <Toaster position="top-center" theme="light" />
  </div>;
}

export default App;