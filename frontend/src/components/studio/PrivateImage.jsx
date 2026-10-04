import { ImageOff, LoaderCircle } from 'lucide-react';
import { useStudioImage } from '@/hooks/useStudioImage';

export const PrivateImage = ({ id, alt, testId }) => {
  const { url, error } = useStudioImage(id);
  return url ? <img src={url} alt={alt} data-testid={testId} /> : <div className="studio-private-placeholder" role="img" aria-label={error || 'Vorschau wird geladen'}>{error ? <ImageOff size={22} /> : <LoaderCircle className="loading-spin" size={22} />}</div>;
};