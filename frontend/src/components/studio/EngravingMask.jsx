import { Group, Rect, Ellipse } from 'react-konva';

const outline = (ctx, zone) => {
  if (zone.shape === 'circle') {
    ctx.moveTo(zone.x + zone.w, zone.y + zone.h / 2);
    ctx.arc(zone.x + zone.w / 2, zone.y + zone.h / 2, zone.w / 2, 0, Math.PI * 2);
  } else ctx.rect(zone.x, zone.y, zone.w, zone.h);
  ctx.closePath();
};

export const EngravingMask = ({ product, children }) => {
  // Intersect each complement separately: overlapping holes stay fully excluded.
  const masked = (product.exclusions || []).reduceRight((content, zone) => (
    <Group key={zone.id} clipFunc={ctx => {
      ctx.rect(0, 0, 800, 800);
      outline(ctx, zone);
      return ['evenodd'];
    }}>{content}</Group>
  ), children);
  return <Group clipFunc={ctx => outline(ctx, product.area)}>{masked}</Group>;
};

export const MaskGuide = ({ zone, scale, exclusion = false }) => {
  const props = { name: 'editor-decoration', stroke: exclusion ? '#b45b50' : '#718b5b', strokeWidth: 1.2 / scale, dash: [7, 5], listening: false };
  return zone.shape === 'circle'
    ? <Ellipse {...props} x={zone.x+zone.w/2} y={zone.y+zone.h/2} radiusX={zone.w/2} radiusY={zone.h/2}/>
    : <Rect {...props} x={zone.x} y={zone.y} width={zone.w} height={zone.h}/>;
};