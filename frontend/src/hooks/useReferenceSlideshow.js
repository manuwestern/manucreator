import { useCallback, useEffect, useRef, useState } from 'react';
import { useReducedMotion } from 'framer-motion';

export const SLIDE_INTERVAL = 5000;

export const useReferenceSlideshow = (api, count) => {
  const reduced = useReducedMotion();
  const [selected, setSelected] = useState(0);
  const [playing, setPlaying] = useState(count > 1 && !reduced);
  const [hovered, setHovered] = useState(false);
  const [activityVersion, setActivityVersion] = useState(0);
  const activePage = useRef(!document.hidden && document.hasFocus());
  const timer = useRef(null);
  const stop = useCallback(() => setPlaying(false), []);

  useEffect(() => { if (reduced) setPlaying(false); }, [reduced]);
  useEffect(() => {
    const update = active => {
      activePage.current = active;
      if (!active) window.clearTimeout(timer.current);
      // An epoch also handles blur/focus batched into one React render.
      setActivityVersion(value => value + 1);
    };
    const checkVisibility = () => update(!document.hidden && document.hasFocus());
    const suspend = () => update(false);
    document.addEventListener('visibilitychange', checkVisibility);
    window.addEventListener('blur', suspend);
    window.addEventListener('focus', checkVisibility);
    window.addEventListener('pagehide', suspend);
    window.addEventListener('pageshow', checkVisibility);
    return () => {
      window.clearTimeout(timer.current);
      document.removeEventListener('visibilitychange', checkVisibility);
      window.removeEventListener('blur', suspend);
      window.removeEventListener('focus', checkVisibility);
      window.removeEventListener('pagehide', suspend);
      window.removeEventListener('pageshow', checkVisibility);
    };
  }, []);
  useEffect(() => {
    if (!api) return;
    const update = () => setSelected(api.selectedScrollSnap());
    update();
    api.on('select', update).on('reInit', update).on('pointerDown', stop);
    return () => { api.off('select', update).off('reInit', update).off('pointerDown', stop); };
  }, [api, stop]);
  useEffect(() => {
    if (!api || count < 2 || !playing || hovered || !activePage.current) return;
    timer.current = window.setTimeout(() => {
      if (activePage.current && !document.hidden && document.hasFocus()) api.scrollNext(Boolean(reduced));
    }, SLIDE_INTERVAL);
    return () => window.clearTimeout(timer.current);
  }, [api, count, selected, playing, hovered, activityVersion, reduced]);

  const goTo = index => { stop(); api?.scrollTo(index, Boolean(reduced)); };
  const previous = () => { stop(); api?.scrollPrev(Boolean(reduced)); };
  const next = () => { stop(); api?.scrollNext(Boolean(reduced)); };
  const onKeyDown = event => {
    if (count < 2) return;
    if (event.key === 'ArrowLeft') { event.preventDefault(); previous(); }
    if (event.key === 'ArrowRight') { event.preventDefault(); next(); }
    if (event.key === 'Home') { event.preventDefault(); goTo(0); }
    if (event.key === 'End') { event.preventDefault(); goTo(count - 1); }
  };
  return { selected, playing, hovered, reduced, stop, goTo, previous, next, onKeyDown, setHovered, toggle: () => setPlaying(value => !value) };
};