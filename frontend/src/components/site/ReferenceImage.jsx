import { useState } from 'react';
import { ImageOff, RotateCw } from 'lucide-react';

export const ReferenceImage = ({ photo, active, serviceId }) => {
  const [failed, setFailed] = useState(false);
  const [retry, setRetry] = useState(0);
  return <div className="reference-image-wrap">
    <img
      src={`${photo.src}${retry ? `?retry=${retry}` : ''}`}
      alt={photo.alt}
      draggable="false"
      loading="eager"
      onLoad={() => setFailed(false)}
      onError={() => setFailed(true)}
      className={failed ? 'reference-image-failed' : ''}
      data-testid={active ? 'service-detail-image' : `reference-image-${serviceId}-${photo.id}`}
    />
    {failed && <div className="reference-image-error" role={active ? 'status' : undefined} data-testid={`reference-error-${serviceId}-${photo.id}`}><ImageOff size={23} strokeWidth={1.3} /><p>Dieses Bild konnte nicht geladen werden.</p><button type="button" tabIndex={active ? 0 : -1} onClick={() => { setFailed(false); setRetry(value => value + 1); }} data-testid={`reference-retry-${serviceId}-${photo.id}`}><RotateCw size={13} />Erneut laden</button></div>}
  </div>;
};