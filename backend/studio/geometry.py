import math

def constrain(box, area):
    x, y, w, h = [float(box[k]) for k in ('x', 'y', 'w', 'h')]
    ax, ay, aw, ah = [area[k] for k in ('x', 'y', 'w', 'h')]
    w, h = max(10, min(w, aw)), max(10, min(h, ah))
    if area.get('shape') == 'circle':
        scale = min(1, .999 / math.sqrt((w/aw)**2 + (h/ah)**2))
        w, h = w*scale, h*scale
        if h < 10:
            h = 10; w = min(w, aw*math.sqrt(max(0, .998001-(h/ah)**2)))
        if w < 10:
            w = 10; h = min(h, ah*math.sqrt(max(0, .998001-(w/aw)**2)))
        cx, cy, rx, ry = ax+aw/2, ay+ah/2, aw/2, ah/2
        dy = max(0, ry*math.sqrt(max(0, 1-(w/aw)**2))-h/2)
        by = max(cy-dy, min(y+h/2, cy+dy))
        dx = max(0, rx*math.sqrt(max(0, 1-((abs(by-cy)+h/2)/ry)**2))-w/2)
        bx = max(cx-dx, min(x+w/2, cx+dx))
        return {'x': bx-w/2, 'y': by-h/2, 'w': w, 'h': h}
    return {'x': max(ax, min(x, ax+aw-w)), 'y': max(ay, min(y, ay+ah-h)), 'w': w, 'h': h}

def default_layout(design, product):
    a = product['area']; x,y,w,h = [a[k] for k in ('x','y','w','h')]
    photo = design.template != 'text'
    size = {'small': 32, 'medium': 42, 'large': 52}[design.size]
    shift = {'top': -h*.15, 'center': 0, 'bottom': h*.15}[design.position]
    side = min(w*.6, h*.48)
    text_y = y+h*.68 if photo else y+h*.42
    boxes = {'text': {'x': x+w*.08, 'y': text_y+shift, 'w': w*.84, 'h': min(size,h*.24)}, 'subtitle': {'x': x+w*.08, 'y': text_y+size+shift, 'w': w*.84, 'h': min(25,h*.15)}, 'image': {'x': x+(w-side)/2, 'y': y+h*.08+shift, 'w': side, 'h': side}}
    return {key: constrain(box, a) for key,box in boxes.items()}