import { Group, Rect, Ellipse } from 'react-konva';

export const MaskRegionNode = ({ zone, selected, drawing, scale, nodeRef, onSelect, onChange }) => {
  const hole = zone.id !== 'area', color = hole ? '#b45b50' : '#567942';
  const commit = event => {
    const node = event.target, { id, ...bounds } = zone;
    const value = { ...bounds, ...(hole ? { id } : {}), x: node.x(), y: node.y(), w: node.width()*node.scaleX(), h: node.height()*node.scaleY() };
    node.scale({ x: 1, y: 1 });
    onChange(value);
  };
  const props = { fill: hole ? '#b45b503d' : '#56794230', stroke: color, strokeWidth: (selected ? 2 : 1)/scale, dash: selected ? undefined : [6, 4] };
  return <Group ref={nodeRef} x={zone.x} y={zone.y} width={zone.w} height={zone.h} draggable={!drawing} listening={!drawing} onClick={onSelect} onTap={onSelect} onDragStart={onSelect} onDragEnd={commit} onTransformEnd={commit} dragBoundFunc={p => ({ x: Math.max(0, Math.min(800-zone.w, p.x/scale))*scale, y: Math.max(0, Math.min(800-zone.h, p.y/scale))*scale })}>
    {zone.shape === 'circle' ? <Ellipse {...props} x={zone.w/2} y={zone.h/2} radiusX={zone.w/2} radiusY={zone.h/2}/> : <Rect {...props} width={zone.w} height={zone.h}/>}
  </Group>;
};