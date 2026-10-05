export const rotatedCorners = e => {
  const t=(e.rotation || 0)*Math.PI/180,c=Math.cos(t),s=Math.sin(t),cx=e.x+e.w/2,cy=e.y+e.h/2;
  return [[-e.w/2,-e.h/2],[e.w/2,-e.h/2],[e.w/2,e.h/2],[-e.w/2,e.h/2]].map(([u,v])=>({x:cx+u*c-v*s,y:cy+u*s+v*c}));
};
export const scaleDetails=(e,scale)=>({...e,...(e.font_size>0?{font_size:e.font_size*scale,...(e.text_mode==='outline'?{outline_width:(e.outline_width??1)*scale}:{}),...(e.shadow_enabled?{shadow_distance:(e.shadow_distance??3)*scale}:{})}:{}),...(e.kind==='decoration'?{stroke_width:(e.stroke_width??1.5)*scale}:{})});
export const isInside = (e,a,epsilon=.05) => {
  if(!Number.isFinite(e.w)||!Number.isFinite(e.h)||e.w<.1||e.h<.1||e.font_size>200||e.font_size>0&&e.font_size<4)return false;
  if(e.kind==='text'&&((e.outline_width??1)>12||(e.outline_width??1)<.1||(e.shadow_distance??3)>40))return false;
  if(e.kind==='decoration'&&(Math.min(e.w,e.h)<4||(e.stroke_width??1.5)>12||(e.stroke_width??1.5)<.1||(e.stroke_width??1.5)+2>=Math.min(e.w,e.h)))return false;
  if(e.kind==='decoration'&&['circle-frame','double-circle'].includes(e.ornament)){
    if(Math.abs(e.w-e.h)>.1)return false;
    const cx=e.x+e.w/2,cy=e.y+e.h/2,r=e.w/2;
    return a.shape==='circle'?Math.hypot(cx-a.x-a.w/2,cy-a.y-a.h/2)+r<=a.w/2+epsilon:cx-r>=a.x-epsilon&&cx+r<=a.x+a.w+epsilon&&cy-r>=a.y-epsilon&&cy+r<=a.y+a.h+epsilon;
  }
  return rotatedCorners(e).every(p => a.shape==='circle' ? ((p.x-a.x-a.w/2)/(a.w/2+epsilon))**2+((p.y-a.y-a.h/2)/(a.h/2+epsilon))**2<=1 : p.x>=a.x-epsilon&&p.y>=a.y-epsilon&&p.x<=a.x+a.w+epsilon&&p.y<=a.y+a.h+epsilon);
};
export const fitElement = (e,a,allowScale=true) => {
  const out={...e},cx=e.x+e.w/2,cy=e.y+e.h/2,t=(e.rotation||0)*Math.PI/180,c=Math.abs(Math.cos(t)),s=Math.abs(Math.sin(t));
  let scale;
  if(a.shape==='circle') {
    const centered={...e,x:a.x+(a.w-e.w)/2,y:a.y+(a.h-e.h)/2};
    const radius=e.kind==='decoration'&&['circle-frame','double-circle'].includes(e.ornament)?e.w/a.w:Math.max(...rotatedCorners(centered).map(p=>Math.sqrt(((p.x-a.x-a.w/2)/(a.w/2))**2+((p.y-a.y-a.h/2)/(a.h/2))**2)));
    scale=Math.min(1,.9999/radius);
  } else scale=Math.min(1,a.w/(c*e.w+s*e.h),a.h/(s*e.w+c*e.h));
  if(scale<.999 && !allowScale) return null;
  out.w=e.w*scale;out.h=e.h*scale;
  Object.assign(out,scaleDetails(out,scale));
  out.x=cx-out.w/2;out.y=cy-out.h/2;
  if(a.shape!=='circle') {
    const ex=(c*out.w+s*out.h)/2,ey=(s*out.w+c*out.h)/2;
    const bx=Math.max(a.x+ex,Math.min(cx,a.x+a.w-ex)),by=Math.max(a.y+ey,Math.min(cy,a.y+a.h-ey));
    out.x=bx-out.w/2;out.y=by-out.h/2;
  } else if(!isInside(out,a,0)) {
    const acx=a.x+a.w/2,acy=a.y+a.h/2;let low=0,high=1;
    for(let i=0;i<35;i++){const v=(low+high)/2,b={...out,x:acx+(cx-acx)*v-out.w/2,y:acy+(cy-acy)*v-out.h/2};if(isInside(b,a,0))low=v;else high=v;}
    out.x=acx+(cx-acx)*low-out.w/2;out.y=acy+(cy-acy)*low-out.h/2;
  }
  return out;
};
export const imageFrame = (e,ratio,a) => {
  const cx=e.x+e.w/2,cy=e.y+e.h/2,w=Math.min(e.w,e.h*ratio),h=w/ratio;
  return fitElement({...e,w,h,x:cx-w/2,y:cy-h/2},a);
};