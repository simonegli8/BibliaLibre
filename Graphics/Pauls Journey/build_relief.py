"""Reproject the shaded-relief image ReliefReisePaulus.png into the grid of the Paul's-voyages map.

The relief is not in this map's projection, so every output pixel is resampled from it. The relief's
georeference was found by optimising a polynomial lon/lat -> pixel model against Natural Earth
coastlines (about 3% of pixels disagree, i.e. a few pixels at the coast). Sea is replaced by a flat
colour and land is masked with the Natural Earth coastline, so the black sea of the relief never shows.

  python build_relief.py land.geojson relief_3600.png relief-map.jpg

relief_3600.png is ReliefReisePaulus.png downscaled to 3600 px wide. Runs headless Edge (canvas).
"""
import base64, json, os, subprocess, sys, tempfile
import make_maps as M

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
Z = 2  # output pixels per map pixel
# fitted model in a 1000-px-wide frame of the relief:
#   u = lat - 37, v = lon - 24
#   x = p0 + p1*lon + p4*u + p7*v*u ;  y = p2 - p3*lat + p5*u^2 + p6*v + p8*u^3
FIT = [-383.805, 34.0328, 1552.085, 32.6203, -0.125, 0.00625, 0.0, -0.0015, -0.02025]
SEA = (0xC9, 0xDE, 0xEA)


def main(geojson, relief, out_jpg):
    rings = []
    for f in json.load(open(geojson, encoding="utf-8"))["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            for ring in poly:
                if any(M.LON0 - 3 <= x <= M.LON1 + 3 and M.LAT0 - 3 <= y <= M.LAT1 + 3 for x, y in ring):
                    rings.append([[round(x, 3), round(y, 3)] for x, y in ring])

    W, H = round(M.W * Z), round(M.H * Z)
    html = HTML.replace("__RINGS__", json.dumps(rings, separators=(",", ":"))) \
               .replace("__CFG__", json.dumps(dict(W=W, H=H, Z=Z, lon0=M.LON0, lat1=M.LAT1, kx=M.KX, s=M.S,
                                                  fit=FIT, sea=SEA, src=os.path.basename(relief))))
    work = os.path.dirname(os.path.abspath(relief))
    page = os.path.join(work, "warp.html")
    open(page, "w", encoding="utf-8").write(html)
    r = subprocess.run([EDGE, "--headless", "--disable-gpu", "--allow-file-access-from-files",
                        "--virtual-time-budget=280000", "--dump-dom", "file:///" + page.replace("\\", "/")],
                       capture_output=True, text=True, timeout=290)
    dom = r.stdout
    i = dom.find("data:image/jpeg;base64,")
    if i < 0:
        raise SystemExit("warp failed: " + dom[dom.find('<pre'):][:300])
    j = dom.index("<", i)
    open(out_jpg, "wb").write(base64.b64decode(dom[i + 23:j]))
    print("wrote", out_jpg, os.path.getsize(out_jpg), "bytes", W, "x", H)


HTML = r"""<!doctype html><meta charset=utf-8><body><pre id=out>working</pre><script>
window.onerror=(m,s,l)=>{document.getElementById('out').textContent='ERR '+m+' @'+l};
const RINGS=__RINGS__, C=__CFG__;
const img=new Image();
img.onload=()=>{
 const sw=img.width, sh=img.height, k=sw/1000, p=C.fit.map(v=>v*k);
 const sc=document.createElement('canvas');sc.width=sw;sc.height=sh;
 const sx=sc.getContext('2d',{willReadFrequently:true});sx.drawImage(img,0,0);
 const S=sx.getImageData(0,0,sw,sh).data;
 const valid=(i)=>S[i+3]>=128 && (S[i]+S[i+1]+S[i+2])>=24 && !(S[i+2]>S[i+1]+6 && S[i+2]>S[i]+6);
 function srcXY(lon,lat){const u=lat-37,v=lon-24;
  return [p[0]+p[1]*lon+p[4]*u+p[7]*v*u, p[2]-p[3]*lat+p[5]*u*u+p[6]*v+p[8]*u*u*u];}
 const W=C.W,H=C.H,N=W*H;
 const R=new Float32Array(N),G=new Float32Array(N),B=new Float32Array(N),have=new Uint8Array(N);
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){
  const lon=C.lon0+(x+0.5)/(C.kx*C.Z), lat=C.lat1-(y+0.5)/(C.s*C.Z);
  const [fx,fy]=srcXY(lon,lat);
  const x0=Math.floor(fx-0.5),y0=Math.floor(fy-0.5);
  if(x0<0||y0<0||x0>=sw-1||y0>=sh-1)continue;
  const tx=fx-0.5-x0,ty=fy-0.5-y0;let r=0,g=0,b=0,w=0;
  for(let dy=0;dy<2;dy++)for(let dx=0;dx<2;dx++){
   const i=((y0+dy)*sw+x0+dx)*4;if(!valid(i))continue;
   const wt=(dx?tx:1-tx)*(dy?ty:1-ty);r+=S[i]*wt;g+=S[i+1]*wt;b+=S[i+2]*wt;w+=wt;}
  if(w>0.5){const o=y*W+x;R[o]=r/w;G[o]=g/w;B[o]=b/w;have[o]=1;}
 }
 // land mask from Natural Earth (antialiased)
 const mc=document.createElement('canvas');mc.width=W;mc.height=H;const mx=mc.getContext('2d',{willReadFrequently:true});
 mx.fillStyle='#000';mx.beginPath();
 for(const ring of RINGS){let f=1;for(const [lo,la] of ring){
   const X=(lo-C.lon0)*C.kx*C.Z, Y=(C.lat1-la)*C.s*C.Z; if(f){mx.moveTo(X,Y);f=0}else mx.lineTo(X,Y);}mx.closePath();}
 mx.fill('evenodd');
 const M=mx.getImageData(0,0,W,H).data;
 // erode the sampled area a few pixels away from the shore (drops the dark rim), then fill outward
 for(let it=0;it<5;it++){const nh=have.slice();
  for(let y=1;y<H-1;y++)for(let x=1;x<W-1;x++){const o=y*W+x;
   if(have[o]&&(!have[o-1]||!have[o+1]||!have[o-W]||!have[o+W]))nh[o]=0;}
  have.set(nh);}
 for(let pass=0;pass<120;pass++){let changed=0;
  const nh=have.slice();
  for(let y=1;y<H-1;y++)for(let x=1;x<W-1;x++){const o=y*W+x;
   if(have[o]||M[o*4+3]<10)continue;
   let r=0,g=0,b=0,n=0;
   for(const q of [o-1,o+1,o-W,o+W,o-W-1,o-W+1,o+W-1,o+W+1])if(have[q]){r+=R[q];g+=G[q];b+=B[q];n++;}
   if(n){R[o]=r/n;G[o]=g/n;B[o]=b/n;nh[o]=1;changed++;}}
  have.set(nh);if(!changed)break;}
 const oc=document.createElement('canvas');oc.width=W;oc.height=H;const ox=oc.getContext('2d');
 const od=ox.createImageData(W,H),D=od.data;
 for(let o=0;o<N;o++){const a=M[o*4+3]/255, h=have[o];
  const r=h?R[o]:C.sea[0],g=h?G[o]:C.sea[1],b=h?B[o]:C.sea[2];
  D[o*4]=C.sea[0]*(1-a)+r*a;D[o*4+1]=C.sea[1]*(1-a)+g*a;D[o*4+2]=C.sea[2]*(1-a)+b*a;D[o*4+3]=255;}
 ox.putImageData(od,0,0);
 document.getElementById('out').textContent=oc.toDataURL('image/jpeg',0.9);
};
img.onerror=()=>{document.getElementById('out').textContent='IMGERR'};
img.src=C.src;
</script>"""

if __name__ == "__main__":
    main(*sys.argv[1:4])
