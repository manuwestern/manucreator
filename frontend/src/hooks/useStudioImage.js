import { useEffect,useState } from 'react';
import { studioApi } from '@/lib/studioApi';
import { withPreviewRetry } from '@/lib/previewRetry';
const images=new Map();
export const loadStudioImage = id => {
  if(!id)return Promise.resolve(null);
  if(!images.has(id)) {
    const entry={url:null,promise:null};
    entry.promise=withPreviewRetry(()=>studioApi(`/files/${id}`,{blob:true})).then(blob=>{entry.url=URL.createObjectURL(blob);return entry.url;}).catch(error=>{images.delete(id);throw error;});
    images.set(id,entry);
  }
  return images.get(id).promise;
};
export const useStudioImage = (id, retry=0) => {
  const [state,setState]=useState({id:null,url:null,error:null});
  useEffect(()=>{let alive=true;if(!id){setState({id:null,url:null,error:null});return;}
    setState({id,url:images.get(id)?.url||null,error:null});
    loadStudioImage(id).then(url=>{if(alive)setState({id,url,error:null});}).catch(e=>{if(alive)setState({id,url:null,error:e.message});});
    return()=>{alive=false;};
  },[id,retry]);
  return state.id===id ? state : {id,url:images.get(id)?.url||null,error:null};
};