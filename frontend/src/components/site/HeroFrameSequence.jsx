import { useRef } from 'react';
import { useHeroFrames } from '@/hooks/useHeroFrames';

const POSTER = '/images/hero-video-poster.webp';

export const HeroFrameSequence = ({ progress, enabled, onFailure }) => {
  const canvasRef = useRef(null);
  const ready = useHeroFrames(canvasRef, progress, enabled, onFailure);
  return (
    <div className="hero-video-stage" data-testid="hero-video-stage" data-state={enabled ? (ready ? 'ready' : 'loading') : 'static'}>
      <img className="hero-video-poster" src={POSTER} alt="Graviertes ManuCreator-Metallschild, Kristall mit Berglandschaft und Holzstift auf einer Werkbank" width="736" height="400" fetchPriority="high" data-testid="hero-video-poster" />
      {enabled && <canvas
        ref={canvasRef}
        className={`hero-frame-canvas${ready ? ' is-ready' : ''}`}
        width="736"
        height="400"
        aria-hidden="true"
        data-testid="hero-frame-canvas"
      />}
    </div>
  );
};