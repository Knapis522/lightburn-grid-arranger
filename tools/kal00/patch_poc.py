"""KAL-00 proof of concept: move one top-level group by (dx,dy) via byte-range patch.
Changes: top-level group XForm e,f  +  every Text/BackupPath XForm e,f inside that group."""
import sys, hashlib, xml.parsers.expat
src, dst, gidx, dx, dy = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
data = open(src,'rb').read()
p = xml.parsers.expat.ParserCreate('UTF-8')
stack=[]; group_count=-1; targets=[]  # (byte_start_of_<XForm>, kind)
def start(name, attrs):
    global group_count
    pos=p.CurrentByteIndex
    if name=='Shape' and len(stack)==1:
        if attrs.get('Type')!='Group': pass
        group_count+=1
    in_target = len(stack)>=1 and group_count==gidx and any(n=='Shape' and d==1 for n,d,_ in stack+[(name,len(stack),attrs)]) 
    if name=='XForm' and group_count==gidx and len(stack)>=2:
        parent=stack[-1]
        if parent[0]=='Shape' and parent[1]==1: targets.append((pos,'group'))
        elif parent[0]=='BackupPath' and len(stack)>=2 and stack[-2][0]=='Shape' and stack[-2][2].get('Type')=='Text': targets.append((pos,'backup'))
    stack.append((name,len(stack),attrs))
def end(name): stack.pop()
p.StartElementHandler=start; p.EndElementHandler=end
p.SetParamEntityParsing(xml.parsers.expat.XML_PARAM_ENTITY_PARSING_NEVER)
p.Parse(data, True)
def fmt(v):
    s=format(v,'.8g')
    return s
out=bytearray(); last=0; log=[]
for pos,kind in targets:
    assert data[pos:pos+7]==b'<XForm>', data[pos:pos+20]
    a=pos+7; b=data.index(b'</XForm>',a)
    vals=data[a:b].decode('ascii').split(); assert len(vals)==6
    A,B,C,D,E,F=map(float,vals)
    if kind=='group': assert (A,B,C,D)==(1,0,0,1), vals
    new=' '.join(vals[:4]+[fmt(E+dx),fmt(F+dy)]).encode('ascii')
    log.append((kind,data[a:b].decode(),new.decode()))
    out+=data[last:a]+new; last=b
out+=data[last:]
open(dst,'xb').write(bytes(out))   # 'x' = never overwrite
for l in log: print(l)
print("src sha256", hashlib.sha256(data).hexdigest())
print("dst sha256", hashlib.sha256(out).hexdigest(), "bytes", len(out))
