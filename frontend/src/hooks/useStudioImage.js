import { useEffect, useState } from 'react';
import { studioApi } from '@/lib/studioApi';

export const useStudioImage = id => {
  const [state, setState] = useState({ id: null, url: null, error: null });
  useEffect(() => {
    let alive = true, url;
    if (id) studioApi(`/files/${id}`, { blob: true }).then(blob => {
      url = URL.createObjectURL(blob);
      if (alive) setState({ id, url, error: null }); else URL.revokeObjectURL(url);
    }).catch(error => { if (alive) setState({ id, url: null, error: error.message }); });
    return () => { alive = false; if (url) URL.revokeObjectURL(url); };
  }, [id]);
  return state.id === id ? state : { url: null, error: null };
};