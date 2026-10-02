import { useRef } from 'react';
import { motion, useReducedMotion, useScroll, useTransform } from 'framer-motion';
import { Send, Gem, Leaf, Star, Truck, ArrowDown } from 'lucide-react';
import { Button } from '@/components/ui/button';

const promises = [[Gem, 'Präzise Qualität'], [Leaf, 'Bewusste Materialwahl'], [Star, 'Einzigartige Unikate'], [Truck, 'Auch für Unternehmen']];

export const Hero = ({ onRequest, onExamples }) => {
  const ref = useRef(null);
  const reduced = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end start'] });
  const y = useTransform(scrollYProgress, [0, 1], ['0%', '23%']);
  const scale = useTransform(scrollYProgress, [0, 1], [1.04, 1.16]);
  const rotateX = useTransform(scrollYProgress, [0, 1], [0, 5]);
  const textY = useTransform(scrollYProgress, [0, 1], [0, 65]);
  return (
    <section className="hero" id="start" ref={ref} data-testid="hero-section">
      <div className="hero-image-stage"><motion.img className="hero-image" src="/images/hero.jpg" alt="Individuell graviertes Metallschild, Kristall mit Bergmotiv und Messer mit Holzgriff in der ManuCreator-Werkstatt" fetchPriority="high" data-testid="hero-parallax-image" style={reduced ? {} : { y, scale, rotateX }} /></div>
      <div className="hero-shade" />
      <div className="wrap hero-inner">
        <motion.div className="hero-copy" style={reduced ? {} : { y: textY }} initial={reduced ? false : { opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}>
          <p className="eyebrow hero-eyebrow" data-testid="hero-eyebrow"><span />PERSONALISIERT. PRÄZISE. EINZIGARTIG.</p>
          <h1 data-testid="hero-heading"><span>Deine Idee.</span><br />Individuell gemacht.</h1>
          <p className="hero-subtitle" data-testid="hero-subtitle">Lasergravur, Zuschnitt & Textildruck</p>
          <p className="hero-description" data-testid="hero-description">Ob Einzelstück oder Kleinserie – ich setze deine Ideen<br className="desktop-break" /> mit modernster Lasertechnik in hochwertige Produkte um.</p>
          <div className="hero-actions"><Button className="pill" data-testid="hero-inquiry-button" onClick={onRequest}><Send size={16} fill="currentColor" />Jetzt unverbindlich anfragen</Button><Button className="pill pill-outline" data-testid="hero-examples-button" onClick={onExamples}>Beispiele ansehen<ArrowDown size={15} /></Button></div>
        </motion.div>
        <div className="hero-bottom"><div className="trust-strip">{promises.map(([Icon, label], i) => <div key={label} data-testid={`hero-trust-${i}`}><Icon strokeWidth={1.25} size={24} /><span>{label}</span></div>)}</div><a className="scroll-cue" href="#leistungen" aria-label="Leistungen entdecken" data-testid="scroll-discover"><span>ENTDECKEN</span><ArrowDown size={16} /></a></div>
      </div>
    </section>
  );
};