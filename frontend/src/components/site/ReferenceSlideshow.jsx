import { useMemo, useState } from 'react';
import { ArrowLeft, ArrowRight, Pause, Play } from 'lucide-react';
import { Carousel, CarouselContent, CarouselItem } from '@/components/ui/carousel';
import { Button } from '@/components/ui/button';
import { useReferenceSlideshow } from '@/hooks/useReferenceSlideshow';
import { referencesFor } from '@/data/serviceReferences';
import { ReferenceImage } from './ReferenceImage';
import '@/styles/reference-slideshow.css';

export const ReferenceSlideshow = ({ service }) => {
  const photos = useMemo(() => referencesFor(service), [service]);
  const [api, setApi] = useState(null);
  const slideshow = useReferenceSlideshow(api, photos.length);
  const multiple = photos.length > 1;
  const options = useMemo(() => ({ loop: multiple, duration: 28, watchFocus: false }), [multiple]);
  const current = photos[slideshow.selected] || photos[0];

  return <Carousel className="reference-gallery" opts={options} setApi={setApi} aria-label={`Bildreferenzen: ${service.name}`} aria-roledescription="Bildergalerie" tabIndex={0} data-testid="reference-slideshow" data-category={service.id} data-playing={slideshow.playing} onKeyDownCapture={slideshow.onKeyDown}
    onPointerEnter={event => { if (event.pointerType === 'mouse') slideshow.setHovered(true); }}
    onPointerLeave={() => slideshow.setHovered(false)}
    onFocusCapture={event => { if (!event.target.closest('[data-autoplay-toggle]')) slideshow.stop(); }}>
    <div className="reference-topline"><span className="eyebrow" data-testid="reference-heading">EINBLICKE INS MATERIAL</span><span data-testid="reference-count">{photos.length} {multiple ? 'Motive' : 'Motiv'}</span></div>
    <div className="reference-stage"><CarouselContent className="ml-0 reference-track" data-testid="reference-track">{photos.map((photo, i) => <CarouselItem className="pl-0 reference-slide" key={photo.id} aria-roledescription="Bild" aria-label={`${i + 1} von ${photos.length}: ${photo.title}`} aria-hidden={i !== slideshow.selected} data-active={i === slideshow.selected} data-testid={`reference-slide-${service.id}-${photo.id}`}><ReferenceImage photo={photo} active={i === slideshow.selected} serviceId={service.id} /></CarouselItem>)}</CarouselContent></div>
    <div className="reference-toolbar"><div className="reference-caption" aria-live={slideshow.playing ? 'off' : 'polite'} aria-atomic="true"><p data-testid="reference-caption">{current.title}</p><span data-testid="reference-counter">{String(slideshow.selected + 1).padStart(2, '0')} / {String(photos.length).padStart(2, '0')}</span></div>{multiple && <div className="reference-controls">
      <Button variant="ghost" size="icon" className="reference-control" disabled={!api} onClick={slideshow.previous} aria-label="Vorheriges Bild" title="Vorheriges Bild" data-testid="reference-previous"><ArrowLeft size={17} /></Button>
      <Button variant="ghost" size="icon" className="reference-control" onClick={slideshow.toggle} aria-label={slideshow.playing ? 'Slideshow pausieren' : 'Slideshow starten'} aria-pressed={slideshow.playing} title={slideshow.playing ? 'Automatischen Bildwechsel pausieren' : 'Automatischen Bildwechsel starten'} data-autoplay-toggle="true" data-testid="reference-autoplay-toggle">{slideshow.playing ? <Pause size={15} /> : <Play size={15} />}</Button>
      <Button variant="ghost" size="icon" className="reference-control" disabled={!api} onClick={slideshow.next} aria-label="Nächstes Bild" title="Nächstes Bild" data-testid="reference-next"><ArrowRight size={17} /></Button>
    </div>}</div>
    {multiple && <div className="reference-thumbnails" role="group" aria-label="Bild auswählen" data-testid="reference-thumbnails">{photos.map((photo, i) => <button key={photo.id} className={`reference-thumbnail${i === slideshow.selected ? ' is-selected' : ''}`} onClick={() => slideshow.goTo(i)} aria-label={`${photo.title} anzeigen`} aria-pressed={i === slideshow.selected} title={photo.title} data-testid={`reference-thumbnail-${service.id}-${photo.id}`}><img src={photo.thumbnail} alt="" draggable="false" data-testid={`reference-thumb-image-${service.id}-${photo.id}`} /></button>)}</div>}
  </Carousel>;
};