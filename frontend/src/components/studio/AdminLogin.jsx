import { useState } from 'react';
import { LockKeyhole, LogIn } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { adminApi } from '@/lib/adminApi';

export const AdminLogin = ({ onLogin }) => {
  const [email, setEmail] = useState(''), [password, setPassword] = useState(''), [error, setError] = useState(''), [busy, setBusy] = useState(false);
  const submit = async e => { e.preventDefault(); setBusy(true); setError(''); try { onLogin(await adminApi('/auth/login', { method: 'POST', body: { email, password } })); } catch (err) { setError(err.message); } finally { setBusy(false); } };
  return <form className="admin-login" onSubmit={submit}><LockKeyhole size={28} /><p className="eyebrow">DEINE WERKSTATT</p><h1>Willkommen zurück.</h1><p>Verwaltung für ManuCreator</p><label htmlFor="admin-email">E-Mail<Input id="admin-email" type="email" autoComplete="username" value={email} onChange={e => setEmail(e.target.value)} required data-testid="admin-email" /></label><label htmlFor="admin-password">Passwort<Input id="admin-password" type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required data-testid="admin-password" /></label>{error && <p role="alert" className="studio-error" data-testid="admin-login-error">{error}</p>}<Button disabled={busy} type="submit" data-testid="admin-login-submit"><LogIn size={16} />{busy ? 'Wird angemeldet …' : 'Anmelden'}</Button></form>;
};