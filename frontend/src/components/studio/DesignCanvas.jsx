import { useCallback,useEffect,useRef,useState } from 'react';
import { Stage,Layer,Group,Image as KImage,Rect,Ellipse,Transformer } from 'react-konva';
import { useCanvasAssets } from '@/hooks/useCanvasAssets';
import { useCanvasSize } from '@/hooks/useCanvasSize';
import { useCanvasCamera } from '@/hooks/useCanvasCamera';
import { CanvasElement } from './CanvasElement';
import { CameraControls } from './CameraControls';

export const DesignCanvas=({product,design,guides,canvasRef,updateElement,selected,onSelect,disabled,onReady,onNaturalSize,readOnly=false})=>{
  const [wrap,size]=useCanvasSize(true),stage=useRef(),root=useRef(),transformer=useRef(),nodes=useRef({});
  const {blank,error,loaded}=useCanvasAssets(product.image),camera=useCanvasCamera(stage,size,readOnly),a=product.area;
  const [imageStates,setImageStates]=useState({});
  const imageState=useCallback((id,asset,ready)=>setImageStates(old=>old[id]?.asset===asset&&old[id]?.ready===ready?old:{...old,[id]:{asset,ready}}),[]);
  const allReady=loaded&&design.elements.every(e=>{const key=e.kind==='image'?e.asset_id:JSON.stringify([e.text,e.font,e.font_size,e.curvature]);return e.hidden||e.placeholder||(imageStates[e.id]?.asset===key&&imageStates[e.id]?.ready);});
  const selection=design.elements.find(e=>e.id===selected);
  useEffect(()=>{const node=nodes.current[selected];transformer.current?.nodes(node&&selection&&!selection.locked&&!selection.hidden&&!disabled&&!readOnly&&!camera.hand?[node]:[]);transformer.current?.getLayer()?.batchDraw();},[selected,selection,design,size,disabled,loaded,readOnly,camera.hand,camera.view]);
  useEffect(()=>{onReady?.(allReady&&!error);},[allReady,error,onReady]);
  useEffect(()=>{
    if(!canvasRef)return;
    canvasRef.current={toDataURL:()=>{
      if(!allReady)throw new Error('Vorschau lädt noch');
      const original={stage:stage.current.size(),root:{x:root.current.x(),y:root.current.y(),offsetX:root.current.offsetX(),offsetY:root.current.offsetY(),scaleX:root.current.scaleX(),scaleY:root.current.scaleY()}};
      const decorations=stage.current.find('.editor-decoration'),visibility=decorations.map(n=>n.visible());
      try {decorations.forEach(n=>n.hide());stage.current.size({width:800,height:800});root.current.setAttrs({x:0,y:0,offsetX:0,offsetY:0,scaleX:1,scaleY:1});stage.current.draw();return stage.current.toDataURL({width:800,height:800,pixelRatio:1});}
      finally {root.current.setAttrs(original.root);stage.current.size(original.stage);decorations.forEach((n,i)=>n.visible(visibility[i]));stage.current.draw();}
    }};
    return()=>{canvasRef.current=null;};
  },[canvasRef,allReady]);
  const start=e=>{camera.handlers.onMouseDown(e);if(!camera.hand&&!readOnly&&e.target===e.target.getStage())onSelect?.(null);};
  return <div className={`studio-canvas-wrap konva-wrap ${camera.hand?'camera-hand':''}`} ref={wrap} data-testid={readOnly?'product-preview-canvas':'design-canvas'} data-loaded={loaded} data-elements={JSON.stringify(design.elements)} data-selected={selected||''} data-camera={JSON.stringify(camera.view)} aria-label={`Gestaltungsfläche: ${product.name}`}>
    <Stage style={{position:'absolute',left:'50%',top:'50%',transform:'translate(-50%,-50%)'}} width={size} height={size} ref={stage} {...camera.handlers} onMouseDown={start}><Layer><Group ref={root} x={size/2+camera.view.x} y={size/2+camera.view.y} offsetX={400} offsetY={400} scaleX={size/800*camera.view.zoom} scaleY={size/800*camera.view.zoom}><KImage image={blank} width={800} height={800} listening={false}/>
      {design.elements.map(element=><CanvasElement key={element.id} element={element} product={product} disabled={disabled||readOnly||camera.hand} onLoadState={imageState} onNaturalSize={onNaturalSize} onSelect={onSelect} onChange={changes=>updateElement?.(element.id,changes)} nodeRef={node=>{nodes.current[element.id]=node;}} toModel={camera.toModel} toScreen={camera.toScreen}/>)}
      {guides&&!readOnly&&(a.shape==='circle'?<Ellipse name="editor-decoration" x={a.x+a.w/2} y={a.y+a.h/2} radiusX={a.w/2} radiusY={a.h/2} stroke="#718b5b" strokeWidth={1.2/(size/800*camera.view.zoom)} dash={[7,5]} listening={false}/>:<Rect name="editor-decoration" x={a.x} y={a.y} width={a.w} height={a.h} stroke="#718b5b" strokeWidth={1.2/(size/800*camera.view.zoom)} dash={[7,5]} listening={false}/>)}
      {!readOnly&&<Transformer name="editor-decoration" ref={transformer} rotateEnabled rotationSnaps={[0,45,90,135,180,225,270,315]} rotateAnchorOffset={24} flipEnabled={false} keepRatio enabledAnchors={['top-left','top-right','bottom-left','bottom-right']} anchorSize={11} anchorCornerRadius={3} borderStroke="#496d35" anchorStroke="#496d35" anchorFill="#fff"/>}
    </Group></Layer></Stage><CameraControls camera={camera} prefix={readOnly?'preview':'canvas'} readOnly={readOnly}/>
    {(!loaded||error)&&<div className={`studio-canvas-status${error?' is-error':''}`} data-testid={readOnly?'product-preview-status':'canvas-status'} role={error?'alert':'status'}>{error||'Rohling wird geladen …'}</div>}
  </div>;
};