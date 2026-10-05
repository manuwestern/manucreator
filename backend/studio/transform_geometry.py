import math

def corners(box):
    theta=math.radians(box.get('rotation',0));c,s=math.cos(theta),math.sin(theta)
    cx,cy=box['x']+box['w']/2,box['y']+box['h']/2
    return [(cx+u*c-v*s,cy+u*s+v*c) for u,v in [(-box['w']/2,-box['h']/2),(box['w']/2,-box['h']/2),(box['w']/2,box['h']/2),(-box['w']/2,box['h']/2)]]

def inside(box,area,tolerance=.12):
    if (box.get('kind')=='shape' and box.get('shape_type')=='circle') or (box.get('kind')=='decoration' and box.get('ornament') in {'circle-frame','double-circle'}):
        # Outer circular contour already includes stroke; bounding-square corners are not ink.
        if abs(box['w']-box['h'])>.1:return False
        cx,cy=box['x']+box['w']/2,box['y']+box['h']/2;r=box['w']/2
        if area.get('shape')=='circle':
            return math.hypot(cx-area['x']-area['w']/2,cy-area['y']-area['h']/2)+r<=area['w']/2+tolerance
        return area['x']-tolerance<=cx-r and cx+r<=area['x']+area['w']+tolerance and area['y']-tolerance<=cy-r and cy+r<=area['y']+area['h']+tolerance
    if area.get('shape')=='circle':
        cx,cy=area['x']+area['w']/2,area['y']+area['h']/2
        return all(((x-cx)/(area['w']/2+tolerance))**2+((y-cy)/(area['h']/2+tolerance))**2<=1 for x,y in corners(box))
    return all(area['x']-tolerance<=x<=area['x']+area['w']+tolerance and area['y']-tolerance<=y<=area['y']+area['h']+tolerance for x,y in corners(box))