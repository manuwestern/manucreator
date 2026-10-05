import { useEffect,useState } from 'react';
import { adminApi } from '@/lib/adminApi';
export const AdminAssetImage=({id,template=false,alt,testId})=>{
  const [url,setUrl]=useState(''),[error,setError]=useState('');
  useEffect(()=>{let alive=true,objectUrl;setError('');setUrl('');(template?adminApi(`/article-templates/${id}/preview`,{blob:true}):adminApi(`/decorations/${id}/sprite`)).then(result=>{if(template){objectUrl=URL.createObjectURL(result);if(alive)setUrl(objectUrl);}else if(alive)setUrl(result.image);}).catch(e=>{if(alive)setError(e.message);});return()=>{alive=false;if(objectUrl)URL.revokeObjectURL(objectUrl);};},[id,template]);
  return error?<p role="alert" data-testid={`${testId}-error`}>{error}</p>:url?<img src={url} alt={alt} data-testid={testId}/>:<span role="status" data-testid={`${testId}-loading`}>Vorschau lädt …</span>;
};