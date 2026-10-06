import { useState } from 'react';
import { Check, Search, X } from 'lucide-react';
import { FONTS, fontSlug } from './editorCatalog';

export const FontPicker = ({ editor }) => {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('Alle');
  const o = editor.selected;
  const fonts = FONTS.filter(f => (category === 'Alle' || f.category === category) && f.name.toLowerCase().includes(search.toLowerCase()));
  if (o?.type !== 'text') return <p data-testid="fonts-empty">Wähle einen Text aus, um seine Schrift zu ändern.</p>;
  return <div className="font-picker" data-testid="font-picker">
    <p className="panel-description" data-testid="font-description">Deine Worte, direkt in jeder Schrift. Antippen und vergleichen.</p>
    <div className="font-search"><Search size={17} /><input aria-label="Schrift suchen" data-testid="font-search" placeholder="Schrift suchen …" value={search} onChange={e => setSearch(e.target.value)} />{search && <button aria-label="Suche leeren" data-testid="font-search-clear" onClick={() => setSearch('')}><X size={16} /></button>}</div>
    <div className="font-categories" role="group" aria-label="Schriftkategorien">{['Alle', 'Klar', 'Klassisch', 'Handschrift'].map(c => <button data-testid={`font-category-${c.toLowerCase()}`} key={c} className={c === category ? 'active' : ''} aria-pressed={c === category} onClick={() => setCategory(c)}>{c}</button>)}</div>
    <div className="font-options" role="group" aria-label="Schrift auswählen">{fonts.map(font => <button key={font.name} data-testid={`font-option-${fontSlug(font.name)}`} className={`font-option ${o.font === font.name ? 'active' : ''}`} aria-pressed={o.font === font.name} disabled={o.locked} onClick={() => editor.patchObject(o.id, { font: font.name })}><span className="font-option-meta"><span data-testid={`font-name-${fontSlug(font.name)}`}>{font.name}</span>{o.font === font.name ? <Check size={15} /> : <span>{font.category}</span>}</span><span className="font-sample" data-testid={`font-sample-${fontSlug(font.name)}`} style={{ fontFamily: `"${font.name}"`, fontWeight: font.weight }}>{o.text.trim() || 'Dein Unikat'}</span></button>)}</div>
    {!fonts.length && <p className="small-note" data-testid="font-no-results">Keine passende Schrift. Versuche einen anderen Namen oder die Kategorie „Alle“.</p>}
  </div>;
};