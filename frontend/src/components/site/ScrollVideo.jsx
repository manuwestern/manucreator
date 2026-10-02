import { useRef } from 'react';
import { useScrollVideo } from '@/hooks/useScrollVideo';

const POSTER = '/images/hero-video-poster.webp';

export const ScrollVideo = ({ progress, enabled, onFailure }) => {
  const videoRef = useRef(null);
  const ready = useScrollVideo(videoRef, progress, enabled, onFailure);
  return (
    <div className="hero-video-stage" data-testid="hero-video-stage" data-state={enabled ? (ready ? 'ready' : 'loading') : 'static'}>
      <img className="hero-video-poster" src={POSTER} alt="Graviertes ManuCreator-Metallschild, Kristall mit Berglandschaft und Holzstift auf einer Werkbank" width="736" height="400" fetchPriority="high" data-testid="hero-video-poster" />
      {enabled && <video
        ref={videoRef}
        className={`hero-scroll-video${ready ? ' is-ready' : ''}`}
        poster={POSTER}
        width="736"
        height="400"
        preload="auto"
        muted
        playsInline
        disablePictureInPicture
        disableRemotePlayback
        aria-hidden="true"
        tabIndex={-1}
        data-testid="hero-scroll-video"
      >
        <source src="/media/hero-scroll.mp4" type="video/mp4" />
        <source src="/media/hero-scroll.webm" type="video/webm" onError={onFailure} />
      </video>}
    </div>
  );
};