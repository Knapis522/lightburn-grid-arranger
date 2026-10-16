import sys, re, xml.etree.ElementTree as ET
from collections import Counter
r=ET.parse(sys.argv[1]).getroot()
VTOK=re.compile(r'V(-?[\d.eE+-]+) (-?[\d.eE+-]+)((?:c[01][xy]-?[\d.eE+-]+)*)')
CTOK=re.compile(r'c([01])([xy])(-?[\d.eE+-]+)')
def pv(s):
    out=[]
    for m in VTOK.finditer(s):
        cp={c.group(1)+c.group(2):float(c.group(3)) for c in CTOK.finditer(m.group(3))}
        out.append((float(m.group(1)),float(m.group(2)),cp))
    return out
VL={};PL={}
for sh in r.iter('Shape'):
    v=sh.find('VertList'); p=sh.find('PrimList')
    if v is not None and 'VertID' in sh.attrib: VL[sh.attrib['VertID']]=v.text or ''
    if p is not None and 'PrimID' in sh.attrib: PL[sh.attrib['PrimID']]=p.text or ''
def xf(e):
    t=e.find('XForm'); return [float(v) for v in t.text.split()] if t is not None else [1,0,0,1,0,0]
def mul(A,B):
    a,b,c,d,e,f=A; A2,B2,C2,D2,E2,F2=B
    return [a*A2+c*B2,b*A2+d*B2,a*C2+c*D2,b*C2+d*D2,a*E2+c*F2+e,b*E2+d*F2+f]
def ap(M,x,y): a,b,c,d,e,f=M; return (a*x+c*y+e,b*x+d*y+f)
def geom(vtext,ptext,M):
    vs=pv(vtext); pts=[]; straight=True
    for x,y,c in vs:
        pts.append(ap(M,x,y))
        for k in '01':
            if k+'y' in c: pts.append(ap(M,c[k+'x'],c[k+'y'])); straight=False
    pr=ptext or ''
    if pr=='LineClosed': closed=True; kind='LineClosed'
    elif pr=='': closed=None; kind='(none)'
    else:
        prs=re.findall(r'([LB])(\d+) (\d+)',pr); closed= bool(prs) and prs[-1][2]==prs[0][1]; kind=dict(Counter(p[0] for p in prs))
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    return dict(n=len(vs),closed=closed,kind=kind,straight=straight,bb=(min(xs),min(ys),max(xs),max(ys)) if pts else None)
def fmt(bb): return f"({bb[0]:.3f},{bb[1]:.3f})-({bb[2]:.3f},{bb[3]:.3f}) = {bb[2]-bb[0]:.3f} x {bb[3]-bb[1]:.3f}"
noprim=0
for gi,g in enumerate(r.findall('Shape')):
    G=xf(g); items=[]
    for sh in g.find('Children'):
        if sh.tag!='Shape': continue
        t=sh.attrib['Type']; M=mul(G,xf(sh))
        if t=='Path':
            if sh.attrib['PrimID'] not in PL: noprim+=1
            items.append(('Path',sh.attrib['CutIndex'],geom(VL[sh.attrib['VertID']],PL.get(sh.attrib['PrimID']),M)))
        elif t=='Text':
            bp=sh.find('BackupPath')
            A=geom(bp.find('VertList').text,bp.find('PrimList').text if bp.find('PrimList') is not None else '',mul(mul(G,xf(sh)),xf(bp)))
            B=geom(bp.find('VertList').text,'',mul(G,xf(bp)))
            items.append(('Text',sh.attrib['CutIndex'],A,B,sh.attrib['Str']))
    paths=[i for i in items if i[0]=='Path']
    paths.sort(key=lambda i:-(i[2]['bb'][2]-i[2]['bb'][0])*(i[2]['bb'][3]-i[2]['bb'][1]))
    print(f"\n== G{gi}  XForm e,f=({G[4]},{G[5]})  shapes={len(items)}  layers={dict(Counter(i[1] for i in items))}")
    for p in paths[:2]: print(f"   Path L{p[1]} n={p[2]['n']} {p[2]['kind']} closed={p[2]['closed']} straight={p[2]['straight']} {fmt(p[2]['bb'])}")
    for t in items:
        if t[0]=='Text': print(f"   Text '{t[4]}' L{t[1]}  G*T*B: {fmt(t[2]['bb'])} | G*B: {fmt(t[3]['bb'])}")
    allbb=[min(i[2]['bb'][0] for i in paths),min(i[2]['bb'][1] for i in paths),max(i[2]['bb'][2] for i in paths),max(i[2]['bb'][3] for i in paths)]
    print("   all paths bb", fmt(allbb))
print("paths w/o primlist",noprim)
print("\n--- BackupPath XForm vs G∘T ---")
for gi,g in enumerate(r.findall('Shape')):
    G=xf(g)
    for sh in g.find('Children'):
        if sh.attrib.get('Type')=='Text':
            T=xf(sh); bp=sh.find('BackupPath'); B=xf(bp); GT=mul(G,T)
            geomB=geom(bp.find('VertList').text,'',B)
            outline=max((s for s in g.find('Children') if s.attrib.get('Type')=='Path'), key=lambda s: len(VL[s.attrib['VertID']]))
            ob=geom(VL[outline.attrib['VertID']],'',mul(G,xf(outline)))['bb']; bb=geomB['bb']
            inside= bb[0]>=ob[0] and bb[1]>=ob[1] and bb[2]<=ob[2] and bb[3]<=ob[3]
            print(f"G{gi} T={T[4:]} B={B} G∘T={[round(v,5) for v in GT]} equal={all(abs(a-b)<1e-3 for a,b in zip(B,GT))} backup-inside-outline={inside}")
