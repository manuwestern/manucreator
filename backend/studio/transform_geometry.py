import math

def corners(box):
    theta=math.radians(box.get('rotation',0));c,s=math.cos(theta),math.sin(theta)
    cx,cy=box['x']+box['w']/2,box['y']+box['h']/2
    return [(cx+u*c-v*s,cy+u*s+v*c) for u,v in [(-box['w']/2,-box['h']/2),(box['w']/2,-box['h']/2),(box['w']/2,box['h']/2),(-box['w']/2,box['h']/2)]]

def inside(box,area,tolerance=.12):
    if area.get('shape')=='circle':
        cx,cy=area['x']+area['w']/2,area['y']+area['h']/2
        return all(((x-cx)/(area['w']/2+tolerance))**2+((y-cy)/(area['h']/2+tolerance))**2<=1 for x,y in corners(box))
    return all(area['x']-tolerance<=x<=area['x']+area['w']+tolerance and area['y']-tolerance<=y<=area['y']+area['h']+tolerance for x,y in corners(box))