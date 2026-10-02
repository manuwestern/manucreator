import { useCallback, useRef, useState } from 'react';
import { motion, useReducedMotion, useScroll } from 'framer-motion';
import { Send, Gem, Leaf, Star, Truck, ArrowDown, Pause, Play, RotateCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { HeroFrameSequence } from './HeroFrameSequence';
import '@/styles/hero-video.css';

const promises = [[Gem, 'Präzise Qualität'], [Leaf, 'Bewusste Materialwahl'], [Star, 'Einzigartige Unikate'], [Truck, 'Auch für Unternehmen']];

export const Hero = ({ onRequest, onExamples }) => {
  const ref = useRef(null);
  const reduced = useReducedMotion();
  const [failed, setFailed] = useState(false);
  const [motionOverride, setMotionOverride] = useState(null);
  const onFailure = useCallback(() => setFailed(true), []);
  const animated = (motionOverride ?? !reduced) && !failed;
  const toggleMotion = () => { setMotionOverride(failed || !animated); setFailed(false); };
  const motionLabel = failed ? 'Animation erneut laden' : animated ? 'Bewegung ausschalten' : 'Bewegung einschalten';
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end end'] });
  return (
    <section className={`hero-scroll-track${animated ? '' : ' hero-scroll-track--static'}`} id="start" ref={ref} data-testid="hero-scroll-track">
    <div className="hero hero--video" data-testid="hero-section">
      <HeroFrameSequence progress={scrollYProgress} enabled={animated} onFailure={onFailure} />
      <div className="hero-shade" />
      <div className="wrap hero-inner">
        <motion.div className="hero-copy" initial={reduced ? false : { opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}>
          <p className="eyebrow hero-eyebrow" data-testid="hero-eyebrow"><span />PERSONALISIERT. PRÄZISE. EINZIGARTIG.</p>
          <h1 data-testid="hero-heading"><span>Deine Idee.</span><br />Individuell gemacht.</h1>
          <p className="hero-subtitle" data-testid="hero-subtitle">Lasergravur, Zuschnitt & Textildruck</p>
          <p className="hero-description" data-testid="hero-description">Ob Einzelstück oder Kleinserie – ich setze deine Ideen<br className="desktop-break" /> mit modernster Lasertechnik in hochwertige Produkte um.</p>
          <div className="hero-actions"><Button className="pill" data-testid="hero-inquiry-button" onClick={onRequest}><Send size={16} fill="currentColor" />Jetzt unverbindlich anfragen</Button><Button className="pill pill-outline" data-testid="hero-examples-button" onClick={onExamples}>Beispiele ansehen<ArrowDown size={15} /></Button></div>
        </motion.div>
        <div className="hero-bottom"><div className="trust-strip">{promises.map(([Icon, label], i) => <div key={label} data-testid={`hero-trust-${i}`}><Icon strokeWidth={1.25} size={24} /><span>{label}</span></div>)}</div><div className="hero-bottom-actions"><button className={`hero-motion-toggle${animated ? '' : ' is-static'}`} onClick={toggleMotion} data-testid="hero-motion-toggle" title={motionLabel} aria-label={motionLabel} aria-pressed={animated}>{failed ? <RotateCw size={15} /> : animated ? <Pause size={15} /> : <Play size={15} />}<span>{failed ? 'Erneut laden' : animated ? 'Bewegung aus' : 'Bewegung an'}</span></button><a className="scroll-cue" href="#leistungen" aria-label="Leistungen entdecken" data-testid="scroll-discover"><span>ENTDECKEN</span><ArrowDown size={16} /></a></div></div>
      </div>
      {animated && <motion.div className="hero-scroll-progress" style={{ scaleX: scrollYProgress }} aria-hidden="true" data-testid="hero-scroll-progress" />}
    </div>
    </section>
  );
};