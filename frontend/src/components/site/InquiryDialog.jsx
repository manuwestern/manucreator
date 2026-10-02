import { useEffect, useRef, useState } from 'react';
import { Check, ArrowRight, Send, LoaderCircle, ShieldCheck, AlertCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { InquiryFields } from './InquiryFields';

const emptyForm = material => ({ name: '', email: '', material, quantity: 1, message: '', website: '' });
const apiUrl = process.env.REACT_APP_BACKEND_URL;

export const InquiryDialog = ({ material, onClose }) => {
  const [form, setForm] = useState(emptyForm('offen'));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [receipt, setReceipt] = useState(null);
  const requestId = useRef(null);
  const submitting = useRef(false);
  useEffect(() => {
    if (material !== null) { setForm(emptyForm(material)); setReceipt(null); setError(''); requestId.current = crypto.randomUUID(); }
  }, [material]);
  const update = (key, value) => setForm(old => ({ ...old, [key]: value }));
  const submit = async e => {
    e.preventDefault();
    if (submitting.current) return;
    const reject = (message, field) => { setError(message); e.currentTarget.querySelector(`#inquiry-${field}`)?.focus(); };
    if (form.name.trim().length < 2) { reject('Bitte gib deinen Namen mit mindestens 2 Zeichen ein.', 'name'); return; }
    if (!form.email.trim() || !e.currentTarget.querySelector('#inquiry-email').validity.valid) { reject('Bitte gib eine gültige E-Mail-Adresse ein.', 'email'); return; }
    if (!Number.isInteger(Number(form.quantity)) || Number(form.quantity) < 1 || Number(form.quantity) > 100000) { reject('Bitte wähle eine ganze Stückzahl zwischen 1 und 100.000.', 'quantity'); return; }
    if (form.message.trim().length < 10) { reject('Erzähl mir bitte etwas mehr über deine Idee – mindestens 10 Zeichen.', 'message'); return; }
    submitting.current = true; setBusy(true); setError('');
    try {
      const response = await fetch(`${apiUrl}/api/inquiries`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...form, quantity: Number(form.quantity), request_id: requestId.current }), signal: AbortSignal.timeout(20000) });
      const data = await response.json();
      if (!response.ok) throw new Error(response.status === 422 ? 'Bitte überprüfe deine Angaben und deine E-Mail-Adresse.' : typeof data.detail === 'string' ? data.detail : 'Deine Anfrage konnte gerade nicht gespeichert werden. Bitte versuche es noch einmal.');
      setReceipt(data);
    } catch (err) { setError(err.name === 'TypeError' || err.name === 'TimeoutError' ? 'Die Verbindung wurde unterbrochen. Deine Eingaben bleiben erhalten – bitte versuche es noch einmal.' : err.message); }
    finally { submitting.current = false; setBusy(false); }
  };
  return (
    <Dialog open={material !== null} onOpenChange={open => { if (!open && !busy) onClose(); }}>
      <DialogContent className={`inquiry-dialog ${receipt ? 'success-dialog' : ''}`} data-testid="inquiry-dialog" onPointerDownOutside={e => { if (busy) e.preventDefault(); }}>
        {receipt ? <div className="success-content"><div className="success-icon"><Check size={31} strokeWidth={1.5} /></div><p className="eyebrow" data-testid="inquiry-success-eyebrow">DER ERSTE SCHRITT IST GEMACHT.</p><DialogTitle data-testid="inquiry-success-title">Deine Idee ist angekommen.</DialogTitle><DialogDescription data-testid="inquiry-success-description">Deine Anfrage wurde erfolgreich gespeichert.<br />Vielen Dank für dein Vertrauen in ManuCreator.</DialogDescription><p className="receipt" data-testid="inquiry-receipt">Deine Referenz: <strong>{receipt.id.slice(0, 8).toUpperCase()}</strong></p><Button className="pill" onClick={onClose} data-testid="inquiry-success-close">Zurück zur Inspiration<ArrowRight size={16} /></Button></div> : <>
          <div className="inquiry-heading"><p className="eyebrow" data-testid="inquiry-eyebrow">LASS UNS ETWAS BESONDERES SCHAFFEN.</p><DialogTitle data-testid="inquiry-title">Alles beginnt mit deiner Idee.</DialogTitle><DialogDescription data-testid="inquiry-description">Erzähl mir, was du dir vorstellst. Ganz unverbindlich.</DialogDescription></div>
          <form onSubmit={submit} noValidate data-testid="inquiry-form"><InquiryFields form={form} update={update} disabled={busy} /><p className="inquiry-nonbinding" data-testid="inquiry-nonbinding">Dies ist keine Bestellung. Ein Vertrag entsteht erst durch eine ausdrückliche Auftragsbestätigung von ManuCreator.</p>{error && <div className="form-error" role="alert" data-testid="inquiry-error"><AlertCircle size={18} /><span>{error}</span></div>}<Button className="pill submit-button" type="submit" disabled={busy} data-testid="inquiry-submit">{busy ? <LoaderCircle className="loading-spin" size={17} /> : <Send size={16} fill="currentColor" />}{busy ? 'Wird gespeichert …' : 'Anfrage unverbindlich senden'}{!busy && <ArrowRight size={16} />}</Button><p className="form-reassurance" data-testid="inquiry-reassurance"><ShieldCheck size={14} />Unverbindlich. Persönlich. Mit Liebe zum Detail.</p></form>
        </>}
      </DialogContent>
    </Dialog>
  );
};