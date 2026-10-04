import { useCallback,useRef,useState } from 'react';

export const useCanvasCamera=(stage,size,initialHand=false)=>{
  const [view,setView]=useState({zoom:1,x:0,y:0}),[hand,setHand]=useState(initialHand),current=useRef(view),gesture=useRef(null);
  current.current=view;
  const apply=useCallback(value=>{const zoom=Math.max(.5,Math.min(4,value.zoom)),limit=Math.max(0,(size*zoom-size)/2);const next={zoom,x:Math.max(-limit,Math.min(limit,value.x)),y:Math.max(-limit,Math.min(limit,value.y))};current.current=next;setView(next);},[size]);
  const toModel=useCallback(p=>{const v=current.current,s=size/800*v.zoom;return{x:(p.x-size/2-v.x)/s+400,y:(p.y-size/2-v.y)/s+400};},[size]);
  const toScreen=useCallback(p=>{const v=current.current,s=size/800*v.zoom;return{x:(p.x-400)*s+size/2+v.x,y:(p.y-400)*s+size/2+v.y};},[size]);
  const zoomAt=useCallback((zoom,point={x:size/2,y:size/2})=>{const p=toModel(point),next=Math.max(.5,Math.min(4,zoom)),s=size/800*next;apply({zoom:next,x:point.x-size/2-(p.x-400)*s,y:point.y-size/2-(p.y-400)*s});},[size,toModel,apply]);
  const touches=event=>{const box=stage.current.container().getBoundingClientRect();return Array.from(event.evt.touches||[]).map(t=>({x:t.clientX-box.left,y:t.clientY-box.top}));};
  const down=event=>{
    const points=touches(event);
    if(points.length>=2){event.evt.preventDefault();const center={x:(points[0].x+points[1].x)/2,y:(points[0].y+points[1].y)/2};stage.current.find('Group').forEach(n=>{if(n.isDragging())n.stopDrag();});gesture.current={kind:'pinch',distance:Math.hypot(points[0].x-points[1].x,points[0].y-points[1].y),model:toModel(center),zoom:current.current.zoom};return;}
    if(hand){const p=stage.current.getPointerPosition();if(p)gesture.current={kind:'pan',point:p,view:{...current.current}};}
  };
  const move=event=>{
    const g=gesture.current;if(!g)return;event.evt.preventDefault();
    if(g.kind==='pinch'){const points=touches(event);if(points.length<2)return;const point={x:(points[0].x+points[1].x)/2,y:(points[0].y+points[1].y)/2},distance=Math.hypot(points[0].x-points[1].x,points[0].y-points[1].y),zoom=Math.max(.5,Math.min(4,g.zoom*distance/Math.max(1,g.distance))),s=size/800*zoom;apply({zoom,x:point.x-size/2-(g.model.x-400)*s,y:point.y-size/2-(g.model.y-400)*s});}
    else {const p=stage.current.getPointerPosition();if(p)apply({...g.view,x:g.view.x+p.x-g.point.x,y:g.view.y+p.y-g.point.y});}
  };
  const stop=()=>{gesture.current=null;};
  const wheel=event=>{if(event.evt.ctrlKey||event.evt.metaKey){event.evt.preventDefault();zoomAt(current.current.zoom*(event.evt.deltaY>0?1/1.15:1.15),stage.current.getPointerPosition());}};
  return {view,hand,setHand,toModel,toScreen,zoomAt,fit:()=>apply({zoom:1,x:0,y:0}),handlers:{onMouseDown:down,onTouchStart:down,onMouseMove:move,onTouchMove:move,onMouseUp:stop,onTouchEnd:stop,onMouseLeave:stop,onWheel:wheel}};
};