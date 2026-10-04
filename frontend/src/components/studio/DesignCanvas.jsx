import { useCallback, useEffect, useRef, useState } from 'react';
import { Stage, Layer, Image as KImage, Rect, Ellipse, Transformer } from 'react-konva';
import { useCanvasAssets } from '@/hooks/useCanvasAssets';
import { useCanvasSize } from '@/hooks/useCanvasSize';
import { CanvasElement } from './CanvasElement';

export const DesignCanvas = ({ product, design, guides, canvasRef, updateElement, selected, onSelect, disabled, onReady }) => {
  const [wrap, size] = useCanvasSize(), stage = useRef(), transformer = useRef(), nodes = useRef({});
  const { blank, error, loaded } = useCanvasAssets(product.image);
  const a = product.area, scale = size / 800;
  const [imageStates,setImageStates] = useState({});
  const imageState = useCallback((id,asset,ready) => setImageStates(old => old[id]?.asset === asset && old[id]?.ready === ready ? old : {...old,[id]:{asset,ready}}), []);
  const allReady = loaded && design.elements.every(e => e.kind !== 'image' || e.hidden || (imageStates[e.id]?.asset === e.asset_id && imageStates[e.id]?.ready));
  const selection = design.elements.find(e => e.id === selected);
  useEffect(() => { const node = nodes.current[selected]; transformer.current?.nodes(node && selection && !selection.locked && !selection.hidden && !disabled ? [node] : []); transformer.current?.getLayer()?.batchDraw(); }, [selected, selection, design, size, disabled, loaded]);
  useEffect(() => { onReady?.(allReady && !error); }, [allReady, error, onReady]);
  useEffect(() => {
    canvasRef.current = { toDataURL: () => { if (!loaded) throw new Error('Bild lädt noch'); const decorations = stage.current.find('.editor-decoration'); decorations.forEach(n => n.hide()); try { return stage.current.toDataURL({ pixelRatio: 800 / size }); } finally { decorations.forEach(n => n.show()); stage.current.batchDraw(); } } };
    return () => { canvasRef.current = null; };
  }, [canvasRef, size, loaded]);
  return <div className="studio-canvas-wrap konva-wrap" ref={wrap} data-testid="design-canvas" data-loaded={loaded} data-elements={JSON.stringify(design.elements)} data-selected={selected || ''} aria-label={`Gestaltungsfläche: ${product.name}`}>
    <Stage width={size} height={size} scaleX={scale} scaleY={scale} ref={stage} onMouseDown={e => { if (e.target === e.target.getStage()) onSelect(null); }} onTouchStart={e => { if (e.target === e.target.getStage()) onSelect(null); }}><Layer><KImage image={blank} width={800} height={800} listening={false} />
      {design.elements.map(element => <CanvasElement key={element.id} element={element} product={product} scale={scale} disabled={disabled} onLoadState={imageState} onSelect={onSelect} onChange={changes => updateElement(element.id, changes)} nodeRef={node => { nodes.current[element.id] = node; }} />)}
      {guides && (a.shape === 'circle' ? <Ellipse name="editor-decoration" x={a.x + a.w / 2} y={a.y + a.h / 2} radiusX={a.w / 2} radiusY={a.h / 2} stroke="#718b5b" strokeWidth={1.5 / scale} dash={[7, 5]} listening={false} /> : <Rect name="editor-decoration" x={a.x} y={a.y} width={a.w} height={a.h} stroke="#718b5b" strokeWidth={1.5 / scale} dash={[7, 5]} listening={false} />)}
      <Transformer name="editor-decoration" ref={transformer} rotateEnabled={false} flipEnabled={false} keepRatio={selection?.kind === 'image'} enabledAnchors={['top-left','top-right','bottom-left','bottom-right']} anchorSize={12} anchorCornerRadius={3} borderStroke="#496d35" anchorStroke="#496d35" anchorFill="#fff" boundBoxFunc={(old, next) => next.width < 10 * scale || next.height < 10 * scale ? old : next} />
    </Layer></Stage>{(!loaded || error) && <div className="studio-canvas-error" data-testid="canvas-status" role={error ? 'alert' : 'status'}>{error || 'Rohling wird geladen …'}</div>}
  </div>;
};