import shapefile, json, collections as C, shapely, sys
from shapely.geometry import shape, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
D='kmap/'
def R(n): return shapefile.Reader(D+n,encoding='cp949')
Q=10.0; X0=595000; Y0=1333000
def enc_line(coords):
    out=[]; px=py=0
    for x,y in coords:
        ix=round((x-X0)/Q); iy=round((y-Y0)/Q)
        if out and ix==px and iy==py: continue
        out+= [ix-px, iy-py] if out else [ix,iy]; px,py=ix,iy
    return out
def polys(g):
    return list(g.geoms) if g.geom_type=='MultiPolygon' else ([g] if g.geom_type=='Polygon' else [p for p in getattr(g,'geoms',[]) if p.geom_type=='Polygon'])
def enc_poly(g, minarea):
    rings=[]
    for p in polys(g):
        if p.area<minarea: continue
        rings.append(enc_line(p.exterior.coords))
        for h in p.interiors:
            if shapely.Polygon(h).area>=minarea: rings.append(enc_line(h.coords))
    return [r for r in rings if len(r)>=6]
admin=C.defaultdict(lambda:C.defaultdict(list))
for sr in R('KOR_ADMIN_AS_KO').iterShapeRecords():
    g=shape(sr.shape.__geo_interface__)
    if not g.is_valid: g=g.buffer(0)
    admin[sr.record['FTR_CDE']][sr.record['MNG_NAM']].append(g)
def simp(geoms,tol):
    try: return shapely.coverage_simplify(geoms,tol)
    except Exception as e: print('cov fail',e,file=sys.stderr); return [g.simplify(tol) for g in geoms]
def grouped(code,parents):
    # parents: (names, geoms, tree) -> group raw polygons by (name, parent)
    pn,pg,pt=parents; groups=C.defaultdict(list)
    for n,gs in admin[code].items():
        for g in gs:
            p=g.representative_point(); par=''
            for i in pt.query(p):
                if pg[i].contains(p) and pn[i]: par=pn[i]; break
            groups[(n,par)].append(g)
    keys=list(groups); geoms=[unary_union(groups[k]) for k in keys]
    return keys,geoms
FOREIGN=set('랴오닝성 프리모르스키크라이 내이멍구자치구 지린성 히로시마현 야마구치현 시마네현 가고시마현 미야자키현 오이타현 후쿠오카현 사가현 나가사키현 구마모토현 에히메현'.split())
NORTH=set('황해남도 황해북도 평안북도 평안남도 자강도 양강도 함경남도 함경북도 강원도 평양직할시 남포특별시 라선특별시 개성특별시'.split())
sn=list(admin['KG021']); sg=[unary_union(admin['KG021'][n]) for n in sn]; ss=simp(sg,300)
gk,gg=grouped('KG022',(sn,sg,STRtree(sg))); gs=simp(gg,150)
gfull=[(k[1]+' '+k[0]).strip() for k in gk]
ek,eg=grouped('KG023',(gfull,gg,STRtree(gg))); es=simp(eg,150)
out={'q':Q,'x0':X0,'y0':Y0}
def kind(n): return 'f' if n in FOREIGN else ('n' if n in NORTH else ('?' if n=='' else 'k'))
def lab(g):
    p=max(polys(g),key=lambda q:q.area).representative_point() if polys(g) else g.representative_point()
    return [round((p.x-X0)/Q),round((p.y-Y0)/Q)]
out['sido']=[{'n':n,'k':kind(n),'l':lab(g),'r':enc_poly(s,150000)} for n,g,s in zip(sn,sg,ss)]
out['sgg']=[{'n':k[0],'p':k[1],'r':enc_poly(s,80000)} for k,s in zip(gk,gs) if k[0]]
out['emd']=[{'n':k[0],'p':k[1],'r':enc_poly(s,50000)} for k,s in zip(ek,es) if k[0]]
for k in ('sido','sgg','emd'): out[k]=[f for f in out[k] if f['r']]
def lines(name,fld,tol):
    res=[]
    for sr in R(name).iterShapeRecords():
        g=shape(sr.shape.__geo_interface__).simplify(tol)
        parts=list(g.geoms) if g.geom_type.startswith('Multi') else [g]
        nm=sr.record[fld] if fld else ''
        for p in parts:
            e=enc_line(p.coords)
            if len(e)>=4: res.append([nm,e])
    return res
out['river']=lines('KOR_RIVER_LS_KO','RIV_NAM',80)
out['road']=lines('KOR_ROAD_LS_KO','ROD_NAM',80)
out['rail']=lines('KOR_RAILW_LS_KO','RAL_NAM',80)
out['dmz']=lines('KOR_DZONE_LS_KO',None,40)
def pts(name,fld,extra=None):
    res=[]
    for sr in R(name).iterShapeRecords():
        x,y=sr.shape.points[0]; v=[sr.record[fld].strip(),round((x-X0)/Q),round((y-Y0)/Q)]
        if extra: v.append(sr.record[extra])
        if v[0]: res.append(v)
    return res
out['place']=pts('KOR_PREMI_PS_KO','MNG_NAM'); out['name']=pts('KOR_NAME_PS_KO','KOR_NAM')
out['mount']=pts('KOR_MOUNT_PS_KO','MOT_NAM','MOT_HIG'); out['cultu']=pts('KOR_CULTU_PS_KO','CUL_NAM'); out['ocean']=pts('KOR_OCEAN_PS_KO','OCN_NAM')
s=json.dumps(out,ensure_ascii=False,separators=(',',':'))
open('kmap.json','w').write(s)
for k,v in out.items():
    if isinstance(v,list): print(k,len(v),len(json.dumps(v,ensure_ascii=False,separators=(',',':'))))
print('total',len(s.encode()))
