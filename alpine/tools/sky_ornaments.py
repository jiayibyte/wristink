"""Original tiny bird/airplane sprites, redrawn for native sizes and palettes."""
from PIL import Image,ImageDraw

def generate(folder,scale,mono,amoled):
    ss=4 if amoled else 1
    for name,w,h,paths in [
        ('Bird',9 if mono else 13,5,[[(0,1),(.25,1),(.5,4),(.75,1),(1,1)]]),
        ('Plane',19,11,[[(-0,5),(18,5)],[(9,5),(6,0)],[(9,5),(6,10)],[(2,5),(0,2)],[(2,5),(0,8)],[(6,0),(8,5)],[(6,10),(8,5)]]),
    ]:
        nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
        for state,color in [('Day',(255,255,255) if mono else (0,0,85)),('Night',(255,255,255) if mono else (255,255,170))]:
            im=Image.new('RGBA',(nw*ss,nh*ss));d=ImageDraw.Draw(im)
            for path in paths:
                points=[(round((x*(w-1) if name=='Bird' else x)*nw/w*ss),round(y*nh/h*ss)) for x,y in path]
                d.line(points,fill=(*color,255),width=max(1,round(scale*ss)),joint='curve')
            if ss!=1:im=im.resize((nw,nh),Image.Resampling.LANCZOS)
            im.save(folder/f'{name.lower()}-{state.lower()}.png')
