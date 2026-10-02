import { useEffect, useState } from 'react';

// The supplied clip has 241 frames at 24 fps. The web encode has a keyframe
// at EVERY frame, so both forward and reverse seeking avoid long GOP decoding.
const FPS = 24;

export const useScrollVideo = (videoRef, progress, enabled, onFailure) => {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !enabled) return;
    let raf = 0;
    let disposed = false;
    let loadTimeout;
    let desiredProgress = progress.get();
    setReady(false);
    video.muted = true;
    video.pause();

    const seek = () => {
      raf = 0;
      if (disposed || video.seeking || video.readyState < 1 || !Number.isFinite(video.duration)) return;
      const lastFrame = Math.max(0, Math.round(video.duration * FPS) - 1);
      const frame = Math.round(Math.min(1, Math.max(0, desiredProgress)) * lastFrame);
      const time = frame / FPS;
      if (Math.abs(video.currentTime - time) < 0.5 / FPS) return;
      try {
        // Keep the media paused: scroll position, not elapsed time, owns playback.
        video.currentTime = time;
      } catch {
        // Metadata/buffering may not yet permit a seek. loadeddata/canplay retry.
      }
    };
    const schedule = () => {
      if (!disposed && !raf) raf = requestAnimationFrame(seek);
    };
    const loaded = () => { if (!disposed) { clearTimeout(loadTimeout); setReady(true); schedule(); } };
    const failed = () => { if (!disposed) { clearTimeout(loadTimeout); setReady(false); onFailure(); } };
    const pause = () => video.pause();
    const unsubscribe = progress.on('change', value => { desiredProgress = value; schedule(); });
    video.addEventListener('loadedmetadata', schedule);
    video.addEventListener('loadeddata', loaded);
    video.addEventListener('canplay', loaded);
    // If direction changed while decoding, seek straight to the latest target.
    video.addEventListener('seeked', schedule);
    video.addEventListener('error', failed);
    video.addEventListener('play', pause);
    // Some browsers never emit a media error for a stalled/empty source list.
    // Never leave visitors stuck in an empty pinned sequence indefinitely.
    loadTimeout = setTimeout(() => { if (video.readyState < 2) failed(); }, 15000);
    if (video.readyState >= 2) loaded();
    schedule();

    return () => {
      disposed = true;
      clearTimeout(loadTimeout);
      cancelAnimationFrame(raf);
      unsubscribe();
      video.pause();
      video.removeEventListener('loadedmetadata', schedule);
      video.removeEventListener('loadeddata', loaded);
      video.removeEventListener('canplay', loaded);
      video.removeEventListener('seeked', schedule);
      video.removeEventListener('error', failed);
      video.removeEventListener('play', pause);
    };
  }, [videoRef, progress, enabled, onFailure]);

  return ready && enabled;
};