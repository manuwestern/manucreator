import { useEffect, useState } from 'react';
import { fontWeight, isShape, MM_TO_UNITS } from './editorCatalog';
import { ImageArtwork } from './ImageArtwork';

export const Branch = ({ strokeWidth = 2.4 }) => <g fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
  <path d="M-95 23 Q-30-12 94-17 M-62 9 Q-62-15-75-22 M-38 0 Q-31-25-17-37 M-7-7 Q4-35 25-45 M26-13 Q44-33 62-38 M50-16 Q68-8 79 6 M16-12 Q28 11 40 21 M-18-5 Q-13 19 4 29 M-48 5 Q-41 29-23 37" />
  <path d="M-75-22 Q-51-20-62 9 Q-78-2-75-22 M-17-37 Q-14-16-38 0 Q-38-23-17-37 M25-45 Q24-20-7-7 Q3-33 25-45 M62-38 Q56-17 26-13 Q43-35 62-38 M94-17 Q81-30 66-17 Q78-9 94-17 M79 6 Q59 8 50-16 Q75-10 79 6 M40 21 Q14 19 16-12 Q38 0 40 21 M4 29 Q-23 17-18-5 Q1 9 4 29 M-23 37 Q-45 36-48 5 Q-25 21-23 37" />
</g>;

export const textWidth = o => Math.min(360, Math.max(100, (o.text || ' ').length * 26));
const strokeWidth = o => (o.strokeWidthMm ?? (o.type === 'text' ? .4 : o.type === 'branch' ? .88 : o.type === 'heart' ? 1.25 : 1)) * MM_TO_UNITS / (o.scale || 1);

const ShapeArtwork = ({ object: o, prefix }) => {
  const w = o.widthMm * MM_TO_UNITS, h = o.heightMm * MM_TO_UNITS;
  const style = { fill: o.filled ? 'currentColor' : 'none', stroke: 'currentColor', strokeWidth: strokeWidth(o), strokeLinejoin: 'round', strokeLinecap: 'round', 'data-testid': `${prefix}shape-artwork-${o.id}` };
  if (o.type === 'line') return <line {...style} x1={-w / 2} y1={0} x2={w / 2} y2={0} />;
  if (o.type === 'circle') return <circle {...style} r={w / 2} />;
  if (o.type === 'rectangle') return <rect {...style} x={-w / 2} y={-h / 2} width={w} height={h} />;
  if (o.type === 'triangle') return <polygon {...style} points={`0,${-h / 2} ${w / 2},${h / 2} ${-w / 2},${h / 2}`} />;
  const points = Array.from({ length: 10 }, (_, i) => {
    const angle = -Math.PI / 2 + i * Math.PI / 5, radius = i % 2 ? .43 : 1;
    return `${Math.cos(angle) * w / 2 * radius},${Math.sin(angle) * h / 2 * radius}`;
  }).join(' ');
  return <polygon {...style} points={points} />;
};

const TextArtwork = ({ object: o, prefix }) => {
  const [fontRevision, setFontRevision] = useState(0);
  useEffect(() => {
    const ready = () => setFontRevision(n => n + 1);
    document.fonts.addEventListener('loadingdone', ready);
    return () => document.fonts.removeEventListener('loadingdone', ready);
  }, []);
  const width = textWidth(o), family = o.font || 'Cormorant Garamond', weight = fontWeight(family);
  // Measure the chosen face, so wider Google fonts and long strings never lose end letters.
  const context = document.createElement('canvas').getContext('2d');
  context.font = `${weight} 57px "${family}"`;
  const fontSize = Math.min(57, 57 * (width - 20) / Math.max(1, context.measureText(o.text || ' ').width));
  const pathId = `${prefix}arc-${o.id}`;
  return <>
    <defs><path id={pathId} d={`M${-width / 2} 16 Q0 ${16 - (o.curve || 0) * .8} ${width / 2} 16`} /></defs>
    <text fontFamily={family} fontSize={fontSize} fontWeight={weight} fill={o.outline ? 'none' : 'currentColor'} stroke={o.outline ? 'currentColor' : 'none'} strokeWidth={o.outline ? strokeWidth(o) : 0} strokeLinejoin="round" textAnchor="middle" data-font-revision={fontRevision} data-testid={`${prefix}engraving-text-${o.id}`}><textPath href={`#${pathId}`} startOffset="50%">{o.text}</textPath></text>
  </>;
};

export const ObjectArtwork = ({ object: o, preview = false }) => {
  const prefix = preview ? 'preview-' : '';
  if (isShape(o)) return <ShapeArtwork object={o} prefix={prefix} />;
  if (o.type === 'heart') return <path d="M0 21 C-5 10-28-7-18-20 C-10-29-1-17 0-10 C4-27 17-29 21-18 C27-5 8 11 0 21Z" fill={o.filled ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth={strokeWidth(o)} strokeLinejoin="round" />;
  if (o.type === 'branch') return <Branch strokeWidth={strokeWidth(o)} />;
  if (o.type === 'image') return <ImageArtwork object={o} preview={preview} />;
  return <TextArtwork object={o} prefix={prefix} />;
};

export function objectBounds(o) {
  const pad = 7 + strokeWidth(o) / 2;
  if (isShape(o)) {
    const w = o.widthMm * MM_TO_UNITS, h = o.type === 'circle' ? w : o.heightMm * MM_TO_UNITS;
    return { x: -w / 2 - pad, y: -h / 2 - pad, w: w + 2 * pad, h: h + 2 * pad };
  }
  if (o.type === 'text') { const width = textWidth(o); return { x: -width / 2 - pad, y: -48 - Math.max(0, o.curve || 0) * .4 - pad / 2, w: width + 2 * pad, h: 72 + Math.abs(o.curve || 0) * .4 + pad }; }
  if (o.type === 'heart') return { x: -29, y: -32, w: 58, h: 62 };
  if (o.type === 'image') return { x: -90, y: -90, w: 180, h: 180 };
  return { x: -103, y: -52, w: 206, h: 96 };
}