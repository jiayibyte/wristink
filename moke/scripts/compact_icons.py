"""Encode unchanged legacy drawing commands to reduce resident Monkey C code."""
import json,re
OPS={'drawLine':(0,4),'drawRectangle':(1,4),'fillRectangle':(2,4),'drawCircle':(3,3),'fillCircle':(4,3),'fillEllipse':(5,4),'setPenWidth':(6,1),'fillPolygon':(7,None),'setColor':(8,2)}
def compact(source):
    start=source.index('        switch (kind) {');end=source.rindex('\n        }')
    body=re.sub(r'//[^\n]*','',source[start:end]);parts=re.split(r'((?:\s*case \d+:)+)',body)[1:]
    paths=['']*29;dynamic=[]
    for labels,code in zip(parts[::2],parts[1::2]):
        ids=list(map(int,re.findall(r'case (\d+):',labels)))
        if any(i in (1,7,14,17) for i in ids):dynamic.append(labels+code);continue
        out=[]
        for cmd in code.replace('break;','').split(';'):
            cmd=cmd.strip()
            if not cmd:continue
            if cmd=='sun(dc, x, y)':out += [9];continue
            m=re.fullmatch(r'dc\.(\w+)\((.*)\)',cmd);assert m,cmd
            name,arg=m.groups();op,n=OPS[name];out.append(op)
            if name=='setColor':out.append(0 if arg.replace(' ','')=='ink,paper' else 1);continue
            if name=='fillPolygon':
                points=re.findall(r'\[([^\[\]]+)\]',arg);out.append(len(points));args=[v for point in points for v in point.split(',')]
            else:args=arg.split(',');assert len(args)==n
            for i,value in enumerate(args):
                value=value.strip();value=re.sub(r'\b[xy]\b','0',value)
                assert re.fullmatch(r'[\d +\-]+',value),value
                out.append(eval(value,{'__builtins__':{}},{}))
        packed=''.join(chr(v+32) for v in out)
        for i in ids:paths[i]=packed
    replacement='''        switch(kind){DYNAMIC default: commands(dc,kind,x,y,ink,paper);}
    }
    const PATHS=PATH_DATA;
    function commands(dc,kind,x,y,ink,paper){
        if(kind<0 || kind>=PATHS.size()){return;}
        var c=PATHS[kind].toCharArray();var i=0;
        while(i<c.size()){
            var op=c[i].toNumber()-32;i++;
            if(op==9){sun(dc,x,y);continue;}
            if(op==8){var light=c[i].toNumber()-32;i++;dc.setColor(light==0 ? ink : paper,paper);continue;}
            if(op==6){dc.setPenWidth(c[i].toNumber()-32);i++;continue;}
            if(op==7){var count=c[i].toNumber()-32;i++;var points=[];for(var p=0;p<count;p++){points.add([x+c[i].toNumber()-32,y+c[i+1].toNumber()-32]);i+=2;}dc.fillPolygon(points);continue;}
            var a=x+c[i].toNumber()-32;var b=y+c[i+1].toNumber()-32;var w=c[i+2].toNumber()-32;i+=3;
            if(op==3){dc.drawCircle(a,b,w);continue;}if(op==4){dc.fillCircle(a,b,w);continue;}
            var h=c[i].toNumber()-32;i++;
            switch(op){case 0:dc.drawLine(a,b,x+w,y+h);break;case 1:dc.drawRectangle(a,b,w,h);break;case 2:dc.fillRectangle(a,b,w,h);break;case 5:dc.fillEllipse(a,b,w,h);break;}
        }
'''.replace('DYNAMIC',''.join(dynamic)).replace('PATH_DATA',json.dumps(paths,ensure_ascii=True))
    return source[:start]+replacement+'    }\n}\n'
