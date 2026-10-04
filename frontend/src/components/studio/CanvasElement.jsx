import { useEffect, useMemo, useState } from 'react';
import { Group, Rect, Text, Image as KImage } from 'react-konva';
import { useStudioImage } from '@/hooks/useStudioImage';
import { constrain, fontSize } from '@/lib/studioGeometry';
import { familyFor } from '@/lib/studioLayers';

export const CanvasElement = ({ element: e, product, scale, disabled, nodeRef, onSelect, onChange, onLoadState }) => {
  const asset = useStudioImage(e.kind === 'image' ? e.asset_id : null), [image, setImage] = useState(null);
  useEffect(() => { if (e.kind === 'image') onLoadState(e.id,e.asset_id,!!image && !!asset.url && image.src === asset.url && !asset.error); }, [e.id,e.asset_id,e.kind,image,asset.url,asset.error,onLoadState]);
  useEffect(() => { let alive = true; setImage(null); if (asset.url) { const img = new window.Image(); img.onload = () => { if (alive) setImage(img); }; img.src = asset.url; } return () => { alive = false; }; }, [asset.url]);
  const stamp = useMemo(() => {
    if (!image) return null;
    const canvas = document.createElement('canvas'); canvas.width = Math.max(1, Math.round(e.w)); canvas.height = Math.max(1, Math.round(e.h)); const ctx = canvas.getContext('2d');
    ctx.drawImage(image, e.crop.x * image.width, e.crop.y * image.height, e.crop.w * image.width, e.crop.h * image.height, 0, 0, canvas.width, canvas.height);
    const data = ctx.getImageData(0, 0, canvas.width, canvas.height), rgb = product.ink.match(/\w\w/g).map(v => parseInt(v, 16));
    for (let i = 0; i < data.data.length; i += 4) { const gray = .299 * data.data[i] + .587 * data.data[i + 1] + .114 * data.data[i + 2]; const alpha = data.data[i + 3] / 255; data.data[i] = rgb[0]; data.data[i + 1] = rgb[1]; data.data[i + 2] = rgb[2]; data.data[i + 3] = (255 - gray) * .78 * alpha; }
    ctx.putImageData(data, 0, 0); return canvas;
  }, [image, e.w, e.h, e.crop, product.ink]);
  const commit = event => { const node = event.target, box = constrain({ x: node.x(), y: node.y(), w: node.width() * node.scaleX(), h: node.height() * node.scaleY() }, product.area); node.scale({ x: 1, y: 1 }); node.position(box); onChange(box); };
  if (e.hidden) return null;
  return <Group id={`element-${e.id}`} ref={nodeRef} x={e.x} y={e.y} width={e.w} height={e.h} draggable={!disabled && !e.locked} listening={!disabled && !e.locked} onClick={() => onSelect(e.id)} onTap={() => onSelect(e.id)} onDragStart={() => onSelect(e.id)} onDragEnd={commit} onTransformEnd={commit} dragBoundFunc={pos => { let x = pos.x / scale; const y = pos.y / scale, middle = product.area.x + (product.area.w - e.w) / 2; if (Math.abs(x - middle) < 5) x = middle; const b = constrain({ ...e, x, y }, product.area); return { x: b.x * scale, y: b.y * scale }; }}>
    <Rect width={e.w} height={e.h} fill="rgba(0,0,0,0.001)" />{e.kind === 'text' ? <Text text={e.text || 'Text'} width={e.w} height={e.h} fontFamily={familyFor(e.font)} fontSize={fontSize(e.text || 'Text', familyFor(e.font), e)} fill={product.ink} opacity={e.text ? 1 : .35} align="center" verticalAlign="middle" wrap="none" listening={false} /> : stamp ? <KImage image={stamp} width={e.w} height={e.h} listening={false} /> : <Text text={asset.error ? 'Bild nicht verfügbar' : 'Bild lädt …'} width={e.w} height={e.h} fontSize={12} align="center" verticalAlign="middle" listening={false} />}
  </Group>;
};