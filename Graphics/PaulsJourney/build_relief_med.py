"""Reproject Graphics/Mediterranean.png (coloured relief with sea-depth shading) into the map grid.

Mediterranean.png is a stylised, slightly tilted rendering, so it has no clean projection. Its georeference
(fit_params.json) is a cubic polynomial lon/lat -> pixel warp plus a 13x10 displacement grid, optimised
against the Natural Earth coastline (about 3% of pixels disagree). Land and sea are resampled as two
separate layers (sea = blue pixels), each inpainted across the coastline, then composited with the
Natural Earth land mask so the shore follows the true coastline without a cyan or green fringe.

  python build_relief_med.py land.geojson Mediterranean.png fit_params.json relief-map.jpg
"""
import base64, json, os, shutil, subprocess, sys
import make_maps as M

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
Z = 1.5  # output pixels per map pixel (the source is only ~47 px/degree)


def main(geojson, image, params, out_jpg):
    rings = []
    for f in json.load(open(geojson, encoding="utf-8"))["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            for ring in poly:
                if any(M.LON0 - 3 <= x <= M.LON1 + 3 and M.LAT0 - 3 <= y <= M.LAT1 + 3 for x, y in ring):
                    rings.append([[round(x, 3), round(y, 3)] for x, y in ring])
    W, H = round(M.W * Z), round(M.H * Z)
    cfg = dict(W=W, H=H, Z=Z, lon0=M.LON0, lat1=M.LAT1, kx=M.KX, s=M.S, fit=json.load(open(params)),
               sea=[0xC9, 0xDE, 0xEA], src="med_src.png")
    work = os.path.join(os.path.dirname(os.path.abspath(out_jpg)), "_warp")
    os.makedirs(work, exist_ok=True)
    shutil.copy(image, os.path.join(work, "med_src.png"))
    page = os.path.join(work, "warp.html")
    open(page, "w", encoding="utf-8").write(
        HTML.replace("__RINGS__", json.dumps(rings, separators=(",", ":"))).replace("__CFG__", json.dumps(cfg)))
    r = subprocess.run([EDGE, "--headless", "--disable-gpu", "--allow-file-access-from-files",
                        "--virtual-time-budget=280000", "--dump-dom", "file:///" + page.replace("\\", "/")],
                       capture_output=True, text=True, timeout=290)
    dom = r.stdout
    i = dom.find("data:image/jpeg;base64,")
    if i < 0:
        raise SystemExit("warp failed: " + dom[dom.find("<pre"):][:300])
    open(out_jpg, "wb").write(base64.b64decode(dom[i + 23:dom.index("<", i)]))
    shutil.rmtree(work, ignore_errors=True)
    print("wrote", out_jpg, os.path.getsize(out_jpg), "bytes", W, "x", H)


HTML = r"""<!doctype html><meta charset=utf-8><body><pre id=out>working</pre><script>
window.onerror=(m,s,l)=>{document.getElementById('out').textContent='ERR '+m+' @'+l};
const RINGS=__RINGS__, C=__CFG__, FIT=C.fit;
const LO0=8,LO1=42,LA0=26,LA1=47;
const img=new Image();
img.onload=()=>{
 const sw=img.width, sh=img.height;
 const sc=document.createElement('canvas');sc.width=sw;sc.height=sh;
 const sx=sc.getContext('2d',{willReadFrequently:true});sx.drawImage(img,0,0);
 const S=sx.getImageData(0,0,sw,sh).data;
 const isSea=(i)=>S[i+2]>S[i]+40 && S[i+2]>110;
 function disp(lon,lat){
  let gx=(lon-LO0)/(LO1-LO0)*(FIT.Nx-1), gy=(lat-LA0)/(LA1-LA0)*(FIT.Ny-1);
  gx=Math.max(0,Math.min(FIT.Nx-1.0001,gx));gy=Math.max(0,Math.min(FIT.Ny-1.0001,gy));
  const i=Math.floor(gx),j=Math.floor(gy),tx=gx-i,ty=gy-j,o=j*FIT.Nx+i,a=(1-tx)*(1-ty),b=tx*(1-ty),c=(1-tx)*ty,d=tx*ty,N=FIT.Nx;
  return [FIT.dx[o]*a+FIT.dx[o+1]*b+FIT.dx[o+N]*c+FIT.dx[o+N+1]*d, FIT.dy[o]*a+FIT.dy[o+1]*b+FIT.dy[o+N]*c+FIT.dy[o+N+1]*d];}
 function srcXY(lon,lat){const u=(lon-24)/10,v=(lat-37)/10,t=[1,u,v,u*u,u*v,v*v,u*u*u,u*u*v,u*v*v,v*v*v];
  let X=0,Y=0;for(let k=0;k<10;k++){X+=FIT.cx[k]*t[k];Y+=FIT.cy[k]*t[k];}const d=disp(lon,lat);return [X+d[0],Y+d[1]];}
 const W=C.W,H=C.H,N=W*H;
 // two layers: 0 = land colours, 1 = sea colours
 const L=[0,1].map(()=>({R:new Float32Array(N),G:new Float32Array(N),B:new Float32Array(N),have:new Uint8Array(N)}));
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){
  const lon=C.lon0+(x+0.5)/(C.kx*C.Z), lat=C.lat1-(y+0.5)/(C.s*C.Z);
  const [fx,fy]=srcXY(lon,lat);
  const x0=Math.floor(fx-0.5),y0=Math.floor(fy-0.5);
  if(x0<0||y0<0||x0>=sw-1||y0>=sh-1)continue;
  const tx=fx-0.5-x0,ty=fy-0.5-y0;
  const acc=[[0,0,0,0],[0,0,0,0]];
  for(let dy=0;dy<2;dy++)for(let dx=0;dx<2;dx++){
   const i=((y0+dy)*sw+x0+dx)*4, k=isSea(i)?1:0, wt=(dx?tx:1-tx)*(dy?ty:1-ty), a=acc[k];
   a[0]+=S[i]*wt;a[1]+=S[i+1]*wt;a[2]+=S[i+2]*wt;a[3]+=wt;}
  for(let k=0;k<2;k++){const a=acc[k];if(a[3]>0.6){const o=y*W+x,l=L[k];l.R[o]=a[0]/a[3];l.G[o]=a[1]/a[3];l.B[o]=a[2]/a[3];l.have[o]=1;}}
 }
 // Natural Earth land mask (antialiased)
 const mc=document.createElement('canvas');mc.width=W;mc.height=H;const mx=mc.getContext('2d',{willReadFrequently:true});
 mx.fillStyle='#000';mx.beginPath();
 for(const ring of RINGS){let f=1;for(const [lo,la] of ring){
   const X=(lo-C.lon0)*C.kx*C.Z, Y=(C.lat1-la)*C.s*C.Z; if(f){mx.moveTo(X,Y);f=0}else mx.lineTo(X,Y);}mx.closePath();}
 mx.fill('evenodd');
 const M=mx.getImageData(0,0,W,H).data;
 const inLand=(o)=>M[o*4+3]>=128;
 // restrict each layer to its own side (plus a margin), erode away from the shore, then inpaint
 for(let k=0;k<2;k++){const l=L[k];
  for(let it=0;it<3;it++){const nh=l.have.slice();
   for(let y=1;y<H-1;y++)for(let x=1;x<W-1;x++){const o=y*W+x;
    if(l.have[o]&&(!l.have[o-1]||!l.have[o+1]||!l.have[o-W]||!l.have[o+W]))nh[o]=0;}
   l.have.set(nh);}
  // wanted region: land layer on land, sea layer on sea
  for(let pass=0;pass<(k==0?40:160);pass++){let changed=0;const nh=l.have.slice();
   for(let y=1;y<H-1;y++)for(let x=1;x<W-1;x++){const o=y*W+x;
    if(l.have[o])continue; const wanted=(k==0)?true:M[o*4+3]<245; if(!wanted)continue;
    let r=0,g=0,b=0,n=0;
    for(const q of [o-1,o+1,o-W,o+W,o-W-1,o-W+1,o+W-1,o+W+1])if(l.have[q]){r+=l.R[q];g+=l.G[q];b+=l.B[q];n++;}
    if(n){l.R[o]=r/n;l.G[o]=g/n;l.B[o]=b/n;nh[o]=1;changed++;}}
   l.have.set(nh);if(!changed)break;}
 }
 const oc=document.createElement('canvas');oc.width=W;oc.height=H;const ox=oc.getContext('2d');
 const od=ox.createImageData(W,H),D=od.data;
 for(let o=0;o<N;o++){const a=M[o*4+3]/255;
  const g0=L[0],g1=L[1];
  const lr=g0.have[o]?g0.R[o]:150, lg=g0.have[o]?g0.G[o]:165, lb=g0.have[o]?g0.B[o]:80;
  const sr=g1.have[o]?g1.R[o]:C.sea[0], sg=g1.have[o]?g1.G[o]:C.sea[1], sb=g1.have[o]?g1.B[o]:C.sea[2];
  D[o*4]=sr*(1-a)+lr*a;D[o*4+1]=sg*(1-a)+lg*a;D[o*4+2]=sb*(1-a)+lb*a;D[o*4+3]=255;}
 ox.putImageData(od,0,0);
 document.getElementById('out').textContent=oc.toDataURL('image/jpeg',0.92);
};
img.onerror=()=>{document.getElementById('out').textContent='IMGERR'};
img.src=C.src;
</script>"""

if __name__ == "__main__":
    main(*sys.argv[1:5])
