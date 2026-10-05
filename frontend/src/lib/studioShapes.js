export const shapeNames={line:'Linie',circle:'Kreis',rectangle:'Rechteck',heart:'Herz',triangle:'Dreieck',star:'Stern'};
export const shapeRatios={circle:1,heart:1.1,triangle:2/Math.sqrt(3),star:1.0514622242382672};
export const circularEnvelope=e=>(e.kind==='shape'&&e.shape_type==='circle')||(e.kind==='decoration'&&['circle-frame','double-circle'].includes(e.ornament));
export const validShape=e=>{
  if(e.kind!=='shape')return true;
  if(!shapeNames[e.shape_type])return false;
  const stroke=e.stroke_width??2;
  if(stroke<.1||stroke>12)return false;
  if(e.shape_type==='line')return e.w>=4&&Math.abs(e.h-stroke)<.02;
  const minimum=stroke*({circle:2,rectangle:2,heart:5,triangle:4,star:6}[e.shape_type]||2)+(e.shape_type==='circle'?10:4);
  if(Math.min(e.w,e.h)<4||e.shape_mode==='outline'&&minimum>=Math.min(e.w,e.h))return false;
  const ratio=shapeRatios[e.shape_type];return !ratio||Math.abs(e.w/e.h/ratio-1)<=.002;
};
export const createShape=(type,product)=>{
  const a=product.area,stroke=2,ratio=shapeRatios[type]||1.35;
  const w=type==='line'?a.w*.55:Math.min(a.w*.38,a.h*.38*ratio),h=type==='line'?stroke:w/ratio;
  return {id:crypto.randomUUID(),kind:'shape',shape_type:type,shape_mode:type==='line'?'outline':'filled',shape_proportional:type!=='rectangle',field_label:shapeNames[type],stroke_width:stroke,x:a.x+(a.w-w)/2,y:a.y+(a.h-h)/2,w,h,rotation:0,text:'',font:'curated:open-sans:400:normal',font_size:0,curvature:0,asset_id:null,original_asset_id:null,locked:false,hidden:false,placeholder:false,crop:{x:0,y:0,w:1,h:1}};
};