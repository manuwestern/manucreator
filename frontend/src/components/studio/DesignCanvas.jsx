import { useCallback,useEffect,useRef,useState } from 'react';
import { Stage,Layer,Group,Image as KImage,Line,Transformer } from 'react-konva';
import { EngravingMask,MaskGuide } from './EngravingMask';
import { snapCandidate } from '@/lib/snapGuides';
import { useCanvasAssets } from '@/hooks/useCanvasAssets';
import { useCanvasSize } from '@/hooks/useCanvasSize';
import { useCanvasCamera } from '@/hooks/useCanvasCamera';
import { CanvasElement } from './CanvasElement';
import { CameraControls } from './CameraControls';
import { visualKey } from '@/lib/textPreview';

export const DesignCanvas=({product,design,guides,canvasRef,updateElement,selected,onSelect,disabled,onReady,onNaturalSize,readOnly=false,adminMode=false,snap=false,touchPan=false})=>{
  const [wrap,size]=useCanvasSize(true),stage=useRef(),root=useRef(),transformer=useRef(),nodes=useRef({});
  const {blank,error:blankError,loaded,retry}=useCanvasAssets(product.image),camera=useCanvasCamera(stage,size,readOnly,touchPan),a=product.area;
  const [snapLines,setSnapLines]=useState([]);
  const snapper=useCallback((candidate,element)=>{if(!snap)return null;const scale=size/800*camera.view.zoom;const result=snapCandidate({...element,...candidate},design.elements,a,6/scale);setSnapLines(result.guides);return result;},[snap,size,camera.view.zoom,design.elements,a]);
  const snapEnd=useCallback(()=>setSnapLines([]),[]);
  const [previewAttempt,setPreviewAttempt]=useState(0);
  const [imageStates,setImageStates]=useState({});
  const [boundaryMessage,setBoundaryMessage]=useState('');
  useEffect(()=>setBoundaryMessage(''),[selected,product.id]);
  const imageState=useCallback((id,asset,ready,error='')=>setImageStates(old=>old[id]?.asset===asset&&old[id]?.ready===ready&&old[id]?.error===error?old:{...old,[id]:{asset,ready,error}}),[]);
  const error=blankError||design.elements.some(e=>!e.hidden&&imageStates[e.id]?.asset===visualKey(e)&&imageStates[e.id]?.error)&&'Ein Motiv konnte nicht geladen werden.';
  const allReady=loaded&&design.elements.every(e=>e.hidden||e.placeholder||(imageStates[e.id]?.asset===visualKey(e)&&imageStates[e.id]?.ready));
  const selection=design.elements.find(e=>e.id===selected);
  const lineSelected=selection?.kind==='shape'&&selection.shape_type==='line',freeRectangle=selection?.kind==='shape'&&selection.shape_type==='rectangle'&&!selection.shape_proportional;
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
      <EngravingMask product={product}>{design.elements.map(element=><CanvasElement key={element.id} element={element} product={product} adminMode={adminMode} previewAttempt={previewAttempt} disabled={disabled||readOnly||camera.hand} onLoadState={imageState} onNaturalSize={onNaturalSize} onSelect={onSelect} onChange={changes=>updateElement?.(element.id,changes)} nodeRef={node=>{nodes.current[element.id]=node;}} toModel={camera.toModel} toScreen={camera.toScreen} onBoundary={setBoundaryMessage} snap={snapper} onSnapEnd={snapEnd}/>)}</EngravingMask>
      {snapLines.map(line=><Line key={`${line.axis}-${line.pos}`} name="editor-decoration" points={line.axis==='x'?[line.pos,0,line.pos,800]:[0,line.pos,800,line.pos]} stroke="#c2642f" strokeWidth={1.2/(size/800*camera.view.zoom)} dash={[6,4]} listening={false}/>)}
      {guides&&!readOnly&&<><MaskGuide zone={a} scale={size/800*camera.view.zoom}/>{(product.exclusions||[]).map(zone=><MaskGuide key={zone.id} zone={zone} exclusion scale={size/800*camera.view.zoom}/>)}</>}
      {!readOnly&&<Transformer name="editor-decoration" ref={transformer} rotateEnabled rotationSnaps={[0,45,90,135,180,225,270,315]} rotateAnchorOffset={24} flipEnabled={false} keepRatio={!lineSelected&&!freeRectangle} enabledAnchors={lineSelected?['middle-left','middle-right']:freeRectangle?['top-left','top-center','top-right','middle-left','middle-right','bottom-left','bottom-center','bottom-right']:['top-left','top-right','bottom-left','bottom-right']} anchorSize={11} anchorCornerRadius={3} borderStroke="#496d35" anchorStroke="#496d35" anchorFill="#fff"/>}
    </Group></Layer></Stage><CameraControls camera={camera} prefix={readOnly?'preview':'canvas'} readOnly={readOnly}/>
    {!readOnly&&boundaryMessage&&<p className="canvas-boundary-warning" role="alert" data-testid="canvas-boundary-warning">{boundaryMessage}</p>}
    {(!loaded||error)&&<div className={`studio-canvas-status${error?' is-error':''}`} data-testid={readOnly?'product-preview-status':'canvas-status'} role={error?'alert':'status'}>{error||'Rohling wird geladen …'}{error&&<button type="button" className="canvas-retry" onClick={()=>{retry();setPreviewAttempt(value=>value+1);}} data-testid={readOnly?'preview-retry':'canvas-retry'}>Erneut laden</button>}</div>}
  </div>;
};