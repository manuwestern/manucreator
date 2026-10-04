export const rotatedCorners = e => {
  const t=(e.rotation || 0)*Math.PI/180,c=Math.cos(t),s=Math.sin(t),cx=e.x+e.w/2,cy=e.y+e.h/2;
  return [[-e.w/2,-e.h/2],[e.w/2,-e.h/2],[e.w/2,e.h/2],[-e.w/2,e.h/2]].map(([u,v])=>({x:cx+u*c-v*s,y:cy+u*s+v*c}));
};
export const isInside = (e,a,epsilon=.05) => rotatedCorners(e).every(p => a.shape==='circle' ? ((p.x-a.x-a.w/2)/(a.w/2+epsilon))**2+((p.y-a.y-a.h/2)/(a.h/2+epsilon))**2<=1 : p.x>=a.x-epsilon&&p.y>=a.y-epsilon&&p.x<=a.x+a.w+epsilon&&p.y<=a.y+a.h+epsilon);
export const fitElement = (e,a,allowScale=true) => {
  const out={...e},cx=e.x+e.w/2,cy=e.y+e.h/2,t=(e.rotation||0)*Math.PI/180,c=Math.abs(Math.cos(t)),s=Math.abs(Math.sin(t));
  let scale;
  if(a.shape==='circle') {
    const centered={...e,x:a.x+(a.w-e.w)/2,y:a.y+(a.h-e.h)/2};
    const radius=Math.max(...rotatedCorners(centered).map(p=>Math.sqrt(((p.x-a.x-a.w/2)/(a.w/2))**2+((p.y-a.y-a.h/2)/(a.h/2))**2)));
    scale=Math.min(1,.9999/radius);
  } else scale=Math.min(1,a.w/(c*e.w+s*e.h),a.h/(s*e.w+c*e.h));
  if(scale<.999 && !allowScale) return null;
  out.w=e.w*scale;out.h=e.h*scale;
  if(out.font_size>0 && scale<1)out.font_size*=scale;
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