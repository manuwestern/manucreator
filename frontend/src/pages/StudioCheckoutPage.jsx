import { useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, FlaskConical, Check, LoaderCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { useStudio } from '@/components/studio/StudioLayout';
import { price, studioApi } from '@/lib/studioApi';

export default function StudioCheckoutPage() {
  const { cart, refreshCart } = useStudio();
  const [form, setForm] = useState({ name: '', email: '', note: '', acknowledge_test: false });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const requestId = useRef(crypto.randomUUID());
  const lock = useRef(false);
  const navigate = useNavigate();
  const update = (key, value) => setForm(previous => ({ ...previous, [key]: value }));
  const submit = async event => {
    event.preventDefault();
    if (lock.current) return;
    if (!form.acknowledge_test) { setError('Bitte bestätige, dass dies nur eine Testbestellung ist.'); return; }
    lock.current = true; setBusy(true); setError('');
    try { const order = await studioApi('/orders', { method: 'POST', body: { ...form, request_id: requestId.current } }); await refreshCart(); navigate(`/testbestellung/${order.id}`, { replace: true }); }
    catch (err) { setError(err.message); } finally { setBusy(false); lock.current = false; }
  };
  if (!cart.items.length) return <main className="studio-wrap studio-empty-cart"><h1>Dein Test-Warenkorb ist leer.</h1><Button asChild><Link to="/gestalten" data-testid="checkout-empty-create">Ein Muster gestalten</Link></Button></main>;
  return <main className="studio-wrap studio-checkout"><div className="studio-page-heading"><div><p className="eyebrow">DER LETZTE TESTSCHRITT</p><h1 data-testid="checkout-title">Dein Entwurf. <em>Unverbindlich gespeichert.</em></h1><p>Keine Zahlungsdaten nötig. Bitte verwende für diesen Test möglichst Beispieldaten.</p></div><Link to="/warenkorb" className="studio-text-link" data-testid="checkout-back"><ArrowLeft size={15} />Zum Warenkorb</Link></div><div className="studio-cart-layout"><form className="studio-checkout-form" onSubmit={submit} data-testid="studio-checkout-form"><h2>Angaben zur Testbestellung</h2><button type="button" className="studio-text-link" onClick={() => setForm(previous => ({ ...previous, name: 'Max Muster', email: 'test@example.com' }))} data-testid="checkout-fill-test">Beispieldaten einsetzen</button><div className="studio-field"><label htmlFor="checkout-name">Name</label><Input id="checkout-name" value={form.name} minLength={2} maxLength={100} onChange={e => update('name', e.target.value)} required disabled={busy} autoComplete="off" data-testid="checkout-name" /></div><div className="studio-field"><label htmlFor="checkout-email">E-Mail-Adresse</label><Input id="checkout-email" type="email" value={form.email} maxLength={254} onChange={e => update('email', e.target.value)} required disabled={busy} autoComplete="off" data-testid="checkout-email" /></div><div className="studio-field"><label htmlFor="checkout-note">Hinweis zum Entwurf <small>optional</small></label><Textarea id="checkout-note" value={form.note} maxLength={500} onChange={e => update('note', e.target.value)} disabled={busy} data-testid="checkout-note" placeholder="Dieser Hinweis wird gespeichert, aber nicht an die KI übermittelt." /></div><div className="studio-checkout-ack"><Checkbox id="checkout-ack" checked={form.acknowledge_test} onCheckedChange={value => update('acknowledge_test', value === true)} disabled={busy} data-testid="checkout-ack" /><label htmlFor="checkout-ack">Ich weiß, dass dies ausschließlich ein Test ist. Es entstehen keine Zahlungspflicht, Bestellung zur Fertigung oder vertragliche Verpflichtung.</label></div><p className="studio-checkout-privacy">Die Testdaten werden in deinem Gastzugang gespeichert. Es wird keine Bestell-E-Mail versendet. <Link to="/datenschutz" target="_blank" data-testid="checkout-privacy">Datenschutz</Link></p>{error && <p role="alert" className="studio-error" data-testid="checkout-error">{error}</p>}<Button className="studio-add-cart" type="submit" disabled={busy} data-testid="checkout-submit">{busy ? <LoaderCircle className="loading-spin" size={17} /> : <Check size={17} />}Testbestellung speichern · 0,00 €</Button></form><aside className="studio-order-summary"><FlaskConical size={26} strokeWidth={1.5} /><h2>Ein sicherer Probelauf.</h2><dl><div><dt>Musterartikel</dt><dd data-testid="checkout-count">{cart.count}</dd></div><div><dt>Beispiel-Gesamtwert</dt><dd data-testid="checkout-total">{price(cart.total_cents)}</dd></div><div className="studio-zero-pay"><dt>Zahlbetrag</dt><dd>0,00 €</dd></div></dl><ul><li>Keine Zahlungsabwicklung</li><li>Keine automatische Fertigung</li><li>Originalmotiv und Gestaltungsparameter bleiben getrennt von der KI-Ansicht erhalten</li></ul></aside></div></main>;
}