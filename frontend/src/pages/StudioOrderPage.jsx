import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Check, ArrowRight, Download, LoaderCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { PrivateImage } from '@/components/studio/PrivateImage';
import { studioApi, price } from '@/lib/studioApi';
import { downloadLegalText } from '@/lib/legalDownloads';

export default function StudioOrderPage() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => { let active = true; studioApi(`/orders/${id}`).then(result => { if (active) setOrder(result); }).catch(err => { if (active) setError(err.message); }); return () => { active = false; }; }, [id]);
  if (error) return <main className="studio-wrap studio-empty-cart"><p role="alert" data-testid="order-error">{error}</p><Link to="/gestalten">Zurück zum Gestalten</Link></main>;
  if (!order) return <main className="studio-loading"><LoaderCircle className="loading-spin" />Testbeleg wird geladen …</main>;
  const download = () => downloadLegalText(`${order.reference}-Testbeleg.txt`, `MANUCREATOR · TESTBELEG\n${order.reference}\nKeine Zahlung, kein verbindlicher Kauf, keine Fertigung.\n\n${order.customer.name}\n${order.customer.email}\n\n${order.items.map(item => `${item.quantity} × ${item.product_name}\n${item.draft.design.elements ? item.draft.design.elements.filter(e=>e.kind==='text'&&!e.hidden).map(e=>e.text).join('\n') : item.draft.design.text}\nEntwurfs-ID: ${item.draft.id}\n`).join('\n')}\nBeispiel-Gesamtwert: ${price(order.example_total_cents)}\nZahlbetrag: 0,00 €\n\nHinweis: ${order.customer.note || '–'}\nMaße und Materialeignung sind nicht für die Fertigung freigegeben.`);
  return <main className="studio-wrap studio-order-page"><div className="studio-order-success"><span className="studio-success-icon"><Check size={31} /></span><p className="eyebrow">DEIN MUSTER IST GESPEICHERT.</p><h1 data-testid="order-success-title">Eine Idee zum <em>Festhalten.</em></h1><p data-testid="order-success-description">Deine Testbestellung wurde gespeichert. Es erfolgt keine Zahlung, keine automatische E-Mail und keine Fertigung.</p><span className="studio-order-reference" data-testid="order-reference">{order.reference}</span><div><Button asChild><Link to="/gestalten" data-testid="order-continue">Weiter gestalten<ArrowRight size={16} /></Link></Button><Button variant="outline" onClick={download} data-testid="order-download"><Download size={16} />Testbeleg herunterladen</Button></div></div><div className="studio-order-grid">{order.items.map(item => <article key={item.id} className="studio-order-card"><PrivateImage id={item.draft.render_id} alt={`Gespeicherter Entwurf: ${item.product_name}`} testId={`order-image-${item.id}`} /><div><h2>{item.product_name}</h2><p>{item.draft.design.text || 'Eigenes Motiv'}</p><span>{item.quantity} Stück · Musterentwurf</span></div></article>)}</div></main>;
}