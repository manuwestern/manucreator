import { CheckCircle2, ChevronRight, Eye, Flame, ImageIcon, Loader2, RotateCcw, ScanLine, SlidersHorizontal, WandSparkles } from 'lucide-react';

export const ImageEditingPanel = ({ editor, processing, setPanel }) => {
  const o = editor.selected;
  if (o?.type !== 'image') return <p data-testid="image-edit-empty">Wähle ein Bild auf dem Holz aus.</p>;
  const original = o.imageView === 'original';
  const job = processing.jobs[o.id];
  const openCutout = () => { setPanel('cutout'); if (!o.backgroundRemoved) processing.removeBackground(o.id); };
  return <div className="image-edit-panel" data-testid="image-edit-panel">
    <p className="panel-description" data-testid="image-edit-description">Dein Foto wird automatisch zur Holzgravur.</p>
    <div className="image-mode-toggle" role="group" aria-label="Bildansicht">
      <button data-testid="image-view-original" aria-pressed={original} disabled={o.locked || !o.src} className={original ? 'active' : ''} onClick={() => editor.patchObject(o.id, { imageView: 'original' }, false)}><ImageIcon size={17} />Original</button>
      <button data-testid="image-view-engraving" aria-pressed={!original} disabled={o.locked} className={!original ? 'active' : ''} onClick={() => editor.patchObject(o.id, { imageView: 'engraving' }, false)}><Flame size={17} />Gravur</button>
    </div>
    <div className="engraving-info" data-testid="image-engraving-info">{original ? <Eye size={17} /> : <CheckCircle2 size={17} />}<div><strong>{original ? 'Original zum Vergleichen' : 'Automatische Gravur aktiv'}</strong><p>{original ? 'Vorschau und Export bleiben als Holzgravur.' : 'Natürliche Brauntöne. Die Holzstruktur bleibt sichtbar.'}</p></div></div>
    <button className="image-tool-card primary" data-testid="image-remove-background" disabled={o.locked || !o.src || job?.pending} onClick={openCutout}>{job?.pending ? <Loader2 size={23} className="spin" /> : <WandSparkles size={23} />}<span><strong>{job?.pending ? 'Wird freigestellt …' : o.backgroundRemoved ? 'Freistellung ansehen' : 'Hintergrund entfernen'}</strong><small>{o.backgroundRemoved ? 'Motiv ohne Hintergrund' : 'Motiv automatisch freistellen'}</small></span><ChevronRight size={18} /></button>
    <button className="image-tool-card" data-testid="image-properties-open" disabled={o.locked} onClick={() => setPanel('properties')}><SlidersHorizontal size={21} /><span><strong>Größe & Drehung</strong><small>Dein Bild auf dem Holz ausrichten</small></span><ChevronRight size={18} /></button>
    {job?.error && <p className="image-processing-error" role="alert" data-testid="image-edit-error">{job.error}</p>}
    <p className="image-preservation-note" data-testid="image-preservation-note"><ScanLine size={15} />Dein Original bleibt immer erhalten.</p>
  </div>;
};

export const CutoutPanel = ({ editor, processing, setPanel, compareOriginal, setCompareOriginal }) => {
  const o = editor.selected;
  if (o?.type !== 'image') return <p data-testid="cutout-empty">Wähle zuerst ein Bild aus.</p>;
  const job = processing.jobs[o.id] || {};
  const ready = !!o.backgroundRemoved && !!o.cutoutSrc;
  return <div className="cutout-panel" data-testid="cutout-panel">
    <div className={`cutout-status ${ready ? 'complete' : ''}`} data-testid="cutout-status" aria-live="polite">{job.pending ? <Loader2 size={20} className="spin" /> : ready ? <CheckCircle2 size={20} /> : <ScanLine size={20} />}<div><strong>{job.pending ? 'Hintergrund wird entfernt …' : ready ? 'Dein Motiv ist freigestellt.' : 'Nur dein Motiv. Ohne Hintergrund.'}</strong><p>{job.pending ? 'Einen Moment – dein Original bleibt unverändert.' : ready ? 'Das Schachbrett zeigt transparente Bereiche.' : 'Ein Fingertipp genügt. Wir erkennen das Hauptmotiv.'}</p></div></div>
    {job.error && <p className="image-processing-error" role="alert" data-testid="cutout-error">{job.error}</p>}
    {job.pending ? <button className="outline-button cutout-wide-button" data-testid="cutout-cancel" onClick={() => processing.cancel(o.id)}>Abbrechen</button> : ready ? <button className="preview-button cutout-wide-button" data-testid="cutout-back-to-wood" onClick={() => setPanel('photo')}><Flame size={18} />Auf Holz ansehen</button> : <button className="preview-button cutout-wide-button" data-testid="cutout-automatic" disabled={o.locked || !o.src} onClick={() => { setCompareOriginal(false); processing.removeBackground(o.id); }}><WandSparkles size={18} />{job.error ? 'Erneut versuchen' : 'Automatisch freistellen'}</button>}
    <div className="cutout-secondary-actions"><button className={`outline-button ${compareOriginal ? 'selected' : ''}`} data-testid="cutout-compare-original" disabled={!ready || job.pending} aria-pressed={compareOriginal} onClick={() => setCompareOriginal(!compareOriginal)}><Eye size={17} />{compareOriginal ? 'Freistellung ansehen' : 'Original ansehen'}</button><button className="outline-button" data-testid="cutout-reset" disabled={o.locked || !ready || job.pending} onClick={() => { processing.reset(o.id); setCompareOriginal(false); }}><RotateCcw size={16} />Freistellung zurücksetzen</button></div>
    <p className="property-footnote" data-testid="cutout-quality-note">Am besten klappt es mit einem klar erkennbaren Hauptmotiv. Feine Haare und ähnliche Hintergrundfarben können das Ergebnis beeinflussen.</p>
  </div>;
};