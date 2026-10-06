import { Loader2 } from 'lucide-react';

export const CutoutStage = ({ object, pending, compareOriginal }) => {
  const cutout = !compareOriginal && object?.backgroundRemoved;
  const source = cutout ? object?.cutoutSrc : object?.src;
  return <div className="cutout-stage checkerboard" data-testid="cutout-stage" aria-label="Freistellung auf transparentem Hintergrund">
    {source ? <img className="cutout-stage-image" src={source} alt={cutout ? 'Freigestelltes Motiv auf transparentem Hintergrund' : 'Unverändertes Originalfoto'} data-testid="cutout-stage-image" data-view={cutout ? 'cutout' : 'original'} /> : <span className="cutout-loading" data-testid="cutout-loading"><Loader2 size={22} className="spin" />Bild wird geladen …</span>}
    {pending && <div className="cutout-processing-overlay" data-testid="cutout-processing-overlay"><span><Loader2 size={19} className="spin" />Motiv wird erkannt …</span></div>}
    <span className="cutout-stage-caption" data-testid="cutout-stage-caption">{cutout ? 'Transparenzvorschau' : 'Original'}</span>
  </div>;
};