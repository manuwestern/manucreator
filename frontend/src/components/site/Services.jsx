import { ArrowUpRight } from 'lucide-react';
import { services } from '@/data/services';
import { Reveal } from './Reveal';

export const Services = ({ onSelect }) => (
  <section className="services-section" id="leistungen" data-testid="services-section">
    <div className="wrap">
      <Reveal className="section-heading"><p className="eyebrow section-eyebrow" data-testid="services-eyebrow">MEINE LEISTUNGEN</p><h2 data-testid="services-heading">Vielfältige Möglichkeiten – ein Ergebnis: <span>etwas Besonderes.</span></h2><p data-testid="services-description">Verschiedene Materialien. Unzählige Ideen. Präzise umgesetzt.</p></Reveal>
      <div className="services-grid">{services.map((service, i) => <Reveal key={service.id} delay={(i % 3) * 0.07}><button className={`service-card service-${service.id}`} onClick={() => onSelect(service)} data-testid={`service-card-${service.id}`} aria-label={`${service.name} entdecken`}><img src={service.image} alt={service.alt} loading="lazy" width="418" height="420" /><div className="card-shade" /><span className="service-index" aria-hidden="true">0{i + 1}</span><div className="service-content"><span className="service-eyebrow" data-testid={`service-eyebrow-${service.id}`}>{service.eyebrow}</span><h3 data-testid={`service-title-${service.id}`}>{service.name}</h3><p data-testid={`service-description-${service.id}`}>{service.description}</p></div><span className="service-arrow"><ArrowUpRight size={24} strokeWidth={1.25} /></span></button></Reveal>)}</div>
    </div>
  </section>
);