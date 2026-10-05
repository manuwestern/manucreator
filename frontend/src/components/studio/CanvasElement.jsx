import { useEffect,useMemo,useRef,useState } from 'react';
import { Group,Rect,Text,Image as KImage } from 'react-konva';
import { useStudioImage } from '@/hooks/useStudioImage';
import { fontSize } from '@/lib/studioGeometry';
import { familyFor } from '@/lib/studioLayers';
import { isInside } from '@/lib/transformGeometry';
import { getElementPreview,visualKey } from '@/lib/textPreview';
import { scaleDetails } from '@/lib/transformGeometry';

export const CanvasElement=({element:e,product,disabled,nodeRef,onSelect,onChange,onLoadState,onNaturalSize,toModel,toScreen})=>{
  const lastValid=useRef(null);
  const asset=useStudioImage(e.kind==='image'?e.asset_id:null),[loaded,setLoaded]=useState({key:'',image:null}),[textResult,setTextResult]=useState(null),[textError,setTextError]=useState('');
  const textKey=visualKey(e);
  useEffect(()=>{let alive=true;if(e.kind==='decoration'||(e.kind==='text'&&e.font_size>0)){setTextError('');getElementPreview(e).then(result=>{if(alive)setTextResult({...result,key:textKey});}).catch(err=>{if(alive)setTextError(err.message);});}return()=>{alive=false;};},[e.kind,e.font_size,textKey,e]);
  const source=e.kind==='image'?asset.url:textResult?.key===textKey?textResult.image:null;
  useEffect(()=>{let alive=true;if(source){const image=new window.Image();image.onload=()=>{if(alive){setLoaded({key:source,image});if(e.kind==='image')onNaturalSize?.(e.id,image.width,image.height);}};image.src=source;}return()=>{alive=false;};},[source,e.id,e.kind,onNaturalSize]);
  const image=loaded.key===source?loaded.image:null;
  const renderKey=e.kind==='image'?e.asset_id:textKey;
  useEffect(()=>{onLoadState(e.id,renderKey,e.hidden||(e.kind==='text'&&!e.font_size)||!!image);},[e.id,e.kind,e.hidden,e.font_size,renderKey,image,onLoadState]);
  const stamp=useMemo(()=>{
    if(!image)return null;
    const canvas=document.createElement('canvas');canvas.width=Math.max(1,Math.round(e.w));canvas.height=Math.max(1,Math.round(e.h));const ctx=canvas.getContext('2d');
    const crop=e.kind==='image'?e.crop:{x:0,y:0,w:1,h:1};const sw=crop.w*image.width,sh=crop.h*image.height;
    const factor=Math.min(e.kind==='text'?1:Infinity,e.w/sw,e.h/sh),w=sw*factor,h=sh*factor;
    ctx.drawImage(image,crop.x*image.width,crop.y*image.height,sw,sh,(canvas.width-w)/2,(canvas.height-h)/2,w,h);
    const pixels=ctx.getImageData(0,0,canvas.width,canvas.height),rgb=product.ink.match(/\w\w/g).map(v=>parseInt(v,16));
    for(let i=0;i<pixels.data.length;i+=4){const gray=.299*pixels.data[i]+.587*pixels.data[i+1]+.114*pixels.data[i+2],alpha=pixels.data[i+3]/255;pixels.data[i]=rgb[0];pixels.data[i+1]=rgb[1];pixels.data[i+2]=rgb[2];pixels.data[i+3]=e.kind!=='image'?alpha*255:(255-gray)*.78*alpha;}
    ctx.putImageData(pixels,0,0);return canvas;
  },[image,e.w,e.h,e.crop,e.kind,product.ink]);
  const geometry=node=>{const sx=node.scaleX(),sy=node.scaleY();return{...scaleDetails(e,Math.min(sx,sy)),x:node.x()-node.width()*sx/2,y:node.y()-node.height()*sy/2,w:node.width()*sx,h:node.height()*sy,rotation:((node.rotation()+540)%360)-180};};
  const snapshot=node=>({x:node.x(),y:node.y(),scaleX:node.scaleX(),scaleY:node.scaleY(),rotation:node.rotation()});
  const transformStart=event=>{lastValid.current=snapshot(event.target);};
  const transform=event=>{const node=event.target,next=geometry(node);if(isInside(next,product.area,0))lastValid.current=snapshot(node);else if(lastValid.current){node.setAttrs(lastValid.current);node.getLayer()?.batchDraw();}node.getStage().container().setAttribute('data-live-element',JSON.stringify(geometry(node)));};
  const commit=event=>{const node=event.target,next=geometry(node);if(isInside(next,product.area,0)){node.scale({x:1,y:1});onChange(next);}else if(lastValid.current)node.setAttrs(lastValid.current);};
  if(e.hidden)return null;
  return <Group id={`element-${e.id}`} ref={nodeRef} x={e.x+e.w/2} y={e.y+e.h/2} offsetX={e.w/2} offsetY={e.h/2} width={e.w} height={e.h} rotation={e.rotation||0} draggable={!disabled&&!e.locked} listening={!disabled&&!e.locked} onClick={()=>onSelect?.(e.id)} onTap={()=>onSelect?.(e.id)} onDragStart={event=>{onSelect?.(e.id);transformStart(event);}} onDragEnd={commit} onTransformStart={transformStart} onTransform={transform} onTransformEnd={commit} dragBoundFunc={pos=>{const point=toModel(pos),candidate={...e,x:point.x-e.w/2,y:point.y-e.h/2};let result=candidate;if(!isInside(candidate,product.area,0)){if(!isInside(e,product.area,0))result=e;else{let low=0,high=1;for(let i=0;i<35;i++){const t=(low+high)/2,p={...e,x:e.x+(candidate.x-e.x)*t,y:e.y+(candidate.y-e.y)*t};if(isInside(p,product.area,0))low=t;else high=t;}result={...e,x:e.x+(candidate.x-e.x)*low,y:e.y+(candidate.y-e.y)*low};}}return toScreen({x:result.x+e.w/2,y:result.y+e.h/2});}}><Rect width={e.w} height={e.h} fill={e.placeholder?'#f1f3ec':'rgba(0,0,0,0.001)'} stroke={e.placeholder?'#899f77':undefined} dash={e.placeholder?[5,4]:undefined}/>{e.placeholder?<Text text={e.image_type==='logo'?'Dein Logo':'Dein Foto'} width={e.w} height={e.h} fontSize={Math.max(7,Math.min(18,e.w/8))} fill="#80966f" align="center" verticalAlign="middle" listening={false}/>:e.kind==='text'&&!e.font_size?<Text text={e.text} width={e.w} height={e.h} fontFamily={familyFor(e.font)} fontSize={fontSize(e.text,familyFor(e.font),e)} fill={product.ink} align="center" verticalAlign="middle" wrap="none" listening={false}/>:stamp?<KImage image={stamp} width={e.w} height={e.h} listening={false}/>:<Text text={textError||asset.error?'Vorschau nicht verfügbar':'Vorschau lädt …'} width={e.w} height={e.h} fontSize={10} fill="#87504c" align="center" verticalAlign="middle" listening={false}/>}</Group>;
};