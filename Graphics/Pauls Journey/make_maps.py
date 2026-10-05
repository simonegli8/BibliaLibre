"""Generate two SVG maps of the Apostle Paul's journeys from Natural Earth land polygons.

  python make_maps.py land.geojson
    -> viajes-de-pablo-fondo.svg   (land + sea only)
    -> viajes-de-pablo-completo.svg         (cities, names, voyages, legend)
"""
import base64, json, math, sys

LON0, LON1 = 11.4, 38.5
LAT0, LAT1 = 29.5, 44.0
S = 60.0                                  # pixels per degree of latitude
KX = S * math.cos(math.radians(37))       # pixels per degree of longitude
W, H = (LON1 - LON0) * KX, (LAT1 - LAT0) * S


def proj(lon, lat):
    return (lon - LON0) * KX, (LAT1 - lat) * S


def land_path(geojson):
    """SVG path for all land rings; points far outside the view are clamped to its margin."""
    m = 3.0
    clamp = lambda v, lo, hi: max(lo - m, min(hi + m, v))
    parts = []
    for feat in json.load(open(geojson, encoding="utf-8"))["features"]:
        g = feat["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            for ring in poly:
                if not any(LON0 - m <= x <= LON1 + m and LAT0 - m <= y <= LAT1 + m for x, y in ring):
                    continue
                pts, last = [], None
                for x, y in ring:
                    p = proj(clamp(x, LON0, LON1), clamp(y, LAT0, LAT1))
                    p = (round(p[0], 1), round(p[1], 1))
                    if p != last:
                        pts.append(p)
                        last = p
                parts.append("M" + "L".join(f"{x},{y}" for x, y in pts) + "Z")
    return "".join(parts)


# ---- places: name -> (lon, lat) -------------------------------------------------------------
P = dict(
    Jerusalem=(35.22, 31.78), Caesarea=(34.89, 32.50), Ptolemais=(35.07, 32.93), Tyre=(35.20, 33.27),
    Sidon=(35.37, 33.56), Damascus=(36.30, 33.51), Antioch=(36.16, 36.20), Seleucia=(35.93, 36.12),
    Tarsus=(34.89, 36.92), Salamis=(33.90, 35.18), Paphos=(32.42, 34.76), Perga=(30.85, 36.96),
    Attalia=(30.70, 36.88), PisAntioch=(31.19, 38.30), Iconium=(32.49, 37.87), Lystra=(32.35, 37.58),
    Derbe=(33.35, 37.35), Troas=(26.17, 39.76), Assos=(26.34, 39.49), Mitylene=(26.56, 39.11),
    Ephesus=(27.34, 37.94), Miletus=(27.28, 37.53), Cos=(27.29, 36.89), Rhodes=(28.23, 36.44),
    Patara=(29.32, 36.26), Myra=(29.98, 36.26), Cnidus=(27.37, 36.68), FairHavens=(24.80, 34.93),
    Malta=(14.43, 35.95), Syracuse=(15.29, 37.07), Rhegium=(15.65, 38.11), Puteoli=(14.12, 40.82),
    Rome=(12.50, 41.90), Philippi=(24.29, 41.00), Neapolis=(24.41, 40.94), Thessalonica=(22.94, 40.64),
    Berea=(22.20, 40.52), Athens=(23.73, 37.98), Corinth=(22.93, 37.91), Samothrace=(25.52, 40.49),
)

# label: (text, dx, dy, anchor) offsets in px from the marker
LABELS = dict(
    Jerusalem=("Jerusalén", 10, 14, "start"), Caesarea=("Cesarea", -9, 4, "end"),
    Ptolemais=("Tolemaida", -9, 4, "end"), Tyre=("Tiro", -9, 4, "end"), Sidon=("Sidón", -9, 4, "end"),
    Damascus=("Damasco", 10, 5, "start"), Antioch=("Antioquía", 10, -8, "start"),
    Seleucia=("Seleucia", 8, 17, "start"), Tarsus=("Tarso", -8, 16, "end"),
    Salamis=("Salamina", 8, 16, "start"), Paphos=("Pafos", -9, 16, "end"),
    Perga=("Perge", -9, 16, "end"), PisAntioch=("Antioquía de Pisidia", -9, -2, "end"),
    Iconium=("Iconio", 8, -7, "start"), Lystra=("Listra", -8, 14, "end"), Derbe=("Derbe", 8, 15, "start"),
    Troas=("Troas", -9, -3, "end"), Assos=("Asos", -9, 5, "end"), Mitylene=("Mitylene", -9, 6, "end"),
    Ephesus=("Éfeso", -10, -4, "end"), Miletus=("Mileto", -10, 10, "end"), Cos=("Cos", -9, 5, "end"),
    Rhodes=("Rodas", -10, 20, "end"), Patara=("Patara", -8, 25, "end"), Myra=("Mira", 6, 17, "middle"),
    Cnidus=("Cnido", -9, 22, "end"), FairHavens=("Buenos Puertos", 0, 20, "middle"),
    Malta=("Malta", 0, 20, "middle"), Syracuse=("Siracusa", 9, 5, "start"), Rhegium=("Regio", 9, 5, "start"),
    Puteoli=("Puteoli", 9, 12, "start"), Rome=("Roma", 11, 5, "start"), Philippi=("Filipos", 10, -6, "start"),
    Thessalonica=("Tesalónica", -9, -6, "end"), Berea=("Berea", -9, 5, "end"),
    Athens=("Atenas", 8, 17, "start"), Corinth=("Corinto", -9, 16, "end"), Samothrace=None, Neapolis=None,
)
MAJOR = {"Jerusalem", "Antioch", "Ephesus", "Corinth", "Rome"}

# ---- journeys: (id, legend title, colour, legs); leg = ("sea"|"land", [points or place names]) ---
JOURNEYS = [
    ("j1", "Primer viaje  (c. 46–48 d. C.)", "#c1121f", [
        ("land", ["Antioch", "Seleucia"]),
        ("sea", ["Seleucia", (35.4, 35.5), (34.6, 35.15), "Salamis"]),
        ("land", ["Salamis", (33.3, 35.0), "Paphos"]),
        ("sea", ["Paphos", (32.0, 34.9), (31.9, 35.6), (31.0, 36.5), (30.8, 36.85)]),
        ("land", ["Perga", "PisAntioch", "Iconium", "Lystra", "Derbe"]),
        ("sea", ["Attalia", (31.2, 36.1), (32.8, 35.8), (34.2, 35.9), (35.5, 35.95), "Seleucia"]),
    ]),
    ("j2", "Segundo viaje  (c. 49–52 d. C.)", "#173a8a", [
        ("land", ["Antioch", (36.4, 36.6), (36.4, 37.0), (35.5, 37.1), "Tarsus", (34.5, 37.3), "Derbe",
                  "Lystra", "Iconium", "PisAntioch", (29.5, 39.0), (27.6, 39.9), "Troas"]),
        ("sea", ["Troas", "Samothrace", "Neapolis"]),
        ("land", ["Neapolis", "Philippi", "Thessalonica", "Berea"]),
        ("sea", ["Berea", (22.7, 40.3), (23.7, 39.8), (24.9, 38.9), (24.85, 38.2), (24.5, 37.8), (23.9, 37.6),
                 (23.55, 37.8)]),
        ("land", ["Athens", (23.34, 37.99), "Corinth"]),
        ("sea", ["Corinth", (23.2, 37.75), (24.1, 37.45), (26.5, 37.3), "Ephesus"]),
        ("sea", ["Ephesus", (26.6, 37.1), (27.6, 36.1), (28.3, 35.8), (31.0, 35.4), (32.5, 34.4),
                 (34.0, 33.2), "Caesarea"]),
        ("land", ["Caesarea", "Jerusalem", (35.6, 33.6), (36.1, 35.0), "Antioch"]),
    ]),
    ("j3", "Tercer viaje  (c. 53–57 d. C.)", "#14803a", [
        ("land", ["Antioch", (36.4, 36.6), (36.4, 37.0), (35.5, 37.1), "Tarsus", (33.0, 37.7), "Iconium",
                  (29.5, 38.3), "Ephesus", (26.8, 38.9), "Troas"]),
        ("sea", ["Troas", "Samothrace", "Neapolis"]),
        ("land", ["Neapolis", "Thessalonica", (22.4, 39.6), (22.9, 38.9), (23.0, 38.3), "Corinth"]),
        ("land", ["Troas", "Assos", "Mitylene"]),
        ("sea", ["Mitylene", (26.2, 38.7), (26.7, 37.9), "Miletus", "Cos", "Rhodes", "Patara"]),
        ("sea", ["Patara", (31.0, 35.4), (33.5, 34.2), "Tyre"]),
        ("land", ["Tyre", "Ptolemais", "Caesarea", "Jerusalem"]),
    ]),
    ("j4", "Viaje a Roma  (c. 59–60 d. C.)", "#7b2cbf", [
        ("sea", ["Caesarea", (34.8, 33.0), "Sidon", (35.3, 34.6), (35.0, 35.7), (34.0, 36.0), (32.5, 35.8),
                 (31.0, 36.0), (30.2, 36.15), "Myra"]),
        ("sea", ["Myra", "Cnidus", (27.0, 36.0), (26.3, 35.35), (25.5, 34.85), "FairHavens"]),
        ("sea", ["FairHavens", (24.1, 34.6), (21.5, 34.4), (18.5, 34.3), (16.3, 34.9), (15.0, 35.6), "Malta"]),
        ("sea", ["Malta", "Syracuse", "Rhegium", (15.4, 39.2), (14.9, 40.2), (14.1, 40.65), "Puteoli"]),
        ("land", ["Puteoli", (13.4, 41.3), "Rome"]),
    ]),
]
DAMASCUS = ("Camino de Damasco  (c. 34 d. C.)", "#7f8c8d", ["Jerusalem", "Damascus"])

SEA = "#c9deea"
LAND = "#f1e8d0"
COAST = "#9fb5c0"
INK = "#2b2b2b"


def pt(p):
    return proj(*(P[p] if isinstance(p, str) else p))


def fmt(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def smooth(pts, k=0.85):
    """Catmull-Rom spline through pts as cubic Bezier segments [(p0, c1, c2, p1), ...]."""
    if len(pts) < 3:
        return [(pts[0], pts[0], pts[-1], pts[-1])]
    ext = [pts[0]] + list(pts) + [pts[-1]]
    segs = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 6, p1[1] + (p2[1] - p0[1]) * k / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 6, p2[1] - (p3[1] - p1[1]) * k / 6)
        segs.append((p1, c1, c2, p2))
    return segs


def curve_d(segs):
    d = f"M{segs[0][0][0]:.1f},{segs[0][0][1]:.1f}"
    for _, c1, c2, p in segs:
        d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p[0]:.1f},{p[1]:.1f}"
    return d


def arrow(segs, color):
    """Small triangle at the middle of the longest curve segment, pointing along travel direction."""
    p0, c1, c2, p1 = max(segs, key=lambda s: math.dist(s[0], s[3]))
    if math.dist(p0, p1) < 28:
        return ""
    t = 0.5
    u = 1 - t
    mx = u**3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p1[0]
    my = u**3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p1[1]
    dx = 3 * u * u * (c1[0] - p0[0]) + 6 * u * t * (c2[0] - c1[0]) + 3 * t * t * (p1[0] - c2[0])
    dy = 3 * u * u * (c1[1] - p0[1]) + 6 * u * t * (c2[1] - c1[1]) + 3 * t * t * (p1[1] - c2[1])
    a = math.degrees(math.atan2(dy, dx))
    return (f'<path d="M-6,-5 L7,0 L-6,5 Z" fill="{color}" stroke="#fff" stroke-width="1" '
            f'transform="translate({mx:.1f},{my:.1f}) rotate({a:.1f})"/>')


def svg_open(width_px):
    ratio = H / W
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
            f'width="{width_px}" height="{width_px * ratio:.0f}" font-family="Georgia, \'Times New Roman\', serif">')


def base_layers(land, relief):
    img = ""
    if relief:
        img = (f'<image width="{W:.0f}" height="{H:.0f}" preserveAspectRatio="none" '
               f'href="data:image/jpeg;base64,{relief}"/>')
    return (f'<defs><clipPath id="c"><rect width="{W:.0f}" height="{H:.0f}"/></clipPath></defs>'
            f'<g clip-path="url(#c)"><rect width="{W:.0f}" height="{H:.0f}" fill="{SEA}"/>{img}'
            f'<path d="{land}" fill="{"none" if relief else LAND}" stroke="{COAST}" stroke-width="1" '
            f'fill-rule="evenodd" stroke-linejoin="round" opacity="{0.55 if relief else 0.9}"/></g>')


def halo(text, x, y, size, anchor="start", style="", fill=INK, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" '
            f'stroke="#fffdf5" stroke-width="3.5" stroke-linejoin="round" paint-order="stroke" '
            f'{style} {extra}>{text}</text>')


def build_full(land, relief):
    o = [svg_open(1800), base_layers(land, relief)]

    # region and sea names
    for t, lon, lat, sz, sty in [
        ("Mar Mediterráneo", 25.0, 33.3, 26, 'font-style="italic" letter-spacing="3"'),
        ("Mar Egeo", 25.2, 36.3, 15, 'font-style="italic" letter-spacing="2"'),
        ("Mar Jónico", 18.6, 38.0, 17, 'font-style="italic" letter-spacing="2"'),
        ("Mar Adriático", 15.3, 42.9, 13, 'font-style="italic"'),
        ("Mar Tirreno", 13.4, 39.9, 14, 'font-style="italic" letter-spacing="1"'),
        ("Mar Negro", 33.0, 42.0, 20, 'font-style="italic" letter-spacing="3"'),
        ("ITALIA", 13.4, 43.3, 17, 'letter-spacing="5"'), ("GRECIA", 21.6, 39.2, 14, 'letter-spacing="4"'),
        ("ASIA MINOR", 31.2, 39.6, 22, 'letter-spacing="7"'), ("SIRIA", 37.0, 35.1, 15, 'letter-spacing="4"'),
        ("CHIPRE", 32.9, 35.35, 10, 'letter-spacing="3"'), ("CRETA", 24.9, 35.45, 11, 'letter-spacing="2"'),
        ("EGIPTO", 30.0, 30.4, 22, 'letter-spacing="8"'), ("LIBIA", 22.6, 31.0, 20, 'letter-spacing="8"'),
        ("JUDEA", 34.9, 31.15, 11, 'letter-spacing="3"'), ("SICILIA", 14.1, 37.6, 11, 'letter-spacing="2"'),
    ]:
        x, y = proj(lon, lat)
        if t.startswith("Mar "):
            o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{sz}" text-anchor="middle" fill="#fff" '
                     f'stroke="#1d5a8a" stroke-width="3.2" stroke-linejoin="round" paint-order="stroke" '
                     f'{sty}>{t}</text>')
        else:
            o.append(halo(t, x, y, sz, "middle", sty, fill="#3a3322"))

    # Damascus road
    a, b = pt(DAMASCUS[2][0]), pt(DAMASCUS[2][1])
    o.append(f'<polyline points="{fmt([a, b])}" fill="none" stroke="{DAMASCUS[1]}" stroke-width="3" '
             f'stroke-dasharray="2 6" stroke-linecap="round"/>')

    # journeys
    for _, _, col, legs in JOURNEYS:
        for kind, names in legs:
            pts = [pt(n) for n in names]
            dash = ' stroke-dasharray="9 6"' if kind == "land" else ""
            segs = smooth(pts)
            d = curve_d(segs)
            o.append(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="8.5" '
                     f'stroke-linejoin="round" stroke-linecap="round" opacity="0.92"/>')
            o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="3.4" '
                     f'stroke-linejoin="round" stroke-linecap="round" opacity="0.95"{dash}/>')
            o.append(arrow(segs, col))

    # cities
    for name, lbl in LABELS.items():
        x, y = pt(name)
        if name in MAJOR:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7.5" fill="#fff" stroke="{INK}" stroke-width="2"/>'
                     f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{INK}"/>')
        elif lbl:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="#fff" stroke="{INK}" stroke-width="1.8"/>')
        if lbl:
            t, dx, dy, anc = lbl
            sty = 'font-weight="bold"' if name in MAJOR else ""
            o.append(halo(t, x + dx, y + dy, 15 if name in MAJOR else 13, anc, sty))

    # title
    tx, ty = proj(27.2, 43.35)
    o.append(f'<g><rect x="{tx - 10:.0f}" y="{ty - 34:.0f}" width="560" height="78" rx="6" fill="#fffdf5" '
             f'opacity="0.88" stroke="{COAST}"/>'
             f'<text x="{tx + 6:.0f}" y="{ty:.0f}" font-size="30" font-weight="bold" fill="{INK}">'
             f'Los viajes del apóstol Pablo</text>'
             f'<text x="{tx + 6:.0f}" y="{ty + 26:.0f}" font-size="15" font-style="italic" fill="#555">'
             f'Hechos de los Apóstoles, c. 34 – 60 d. C.</text></g>')

    # legend
    lx, ly = 22, H - 262
    o.append(f'<rect x="{lx}" y="{ly}" width="368" height="240" rx="6" fill="#fffdf5" opacity="0.93" '
             f'stroke="{COAST}"/>')
    o.append(f'<text x="{lx + 16}" y="{ly + 28}" font-size="17" font-weight="bold" fill="{INK}">Leyenda</text>')
    yy = ly + 54
    for _, title, col, _ in JOURNEYS:
        o.append(f'<line x1="{lx + 16}" y1="{yy - 5}" x2="{lx + 66}" y2="{yy - 5}" stroke="{col}" '
                 f'stroke-width="4" stroke-linecap="round"/>'
                 f'<text x="{lx + 78}" y="{yy}" font-size="14" fill="{INK}">{title}</text>')
        yy += 24
    o.append(f'<line x1="{lx + 16}" y1="{yy - 5}" x2="{lx + 66}" y2="{yy - 5}" stroke="{DAMASCUS[1]}" '
             f'stroke-width="3.4" stroke-dasharray="2 6" stroke-linecap="round"/>'
             f'<text x="{lx + 78}" y="{yy}" font-size="14" fill="{INK}">{DAMASCUS[0]}</text>')
    yy += 34
    o.append(f'<line x1="{lx + 16}" y1="{yy - 5}" x2="{lx + 66}" y2="{yy - 5}" stroke="#555" stroke-width="3.4"/>'
             f'<text x="{lx + 78}" y="{yy}" font-size="14" fill="{INK}">Por mar</text>')
    yy += 24
    o.append(f'<line x1="{lx + 16}" y1="{yy - 5}" x2="{lx + 66}" y2="{yy - 5}" stroke="#555" stroke-width="3.4" '
             f'stroke-dasharray="9 6"/><text x="{lx + 78}" y="{yy}" font-size="14" fill="{INK}">Por tierra</text>')
    yy += 26
    o.append(f'<circle cx="{lx + 28}" cy="{yy - 5}" r="4.2" fill="#fff" stroke="{INK}" stroke-width="1.8"/>'
             f'<text x="{lx + 78}" y="{yy}" font-size="14" fill="{INK}">Ciudad visitada</text>'
             f'<circle cx="{lx + 215}" cy="{yy - 5}" r="7.5" fill="#fff" stroke="{INK}" stroke-width="2"/>'
             f'<circle cx="{lx + 215}" cy="{yy - 5}" r="3.2" fill="{INK}"/>'
             f'<text x="{lx + 232}" y="{yy}" font-size="14" fill="{INK}">Centro principal</text>')
    o.append("</svg>")
    return "".join(o)


def build_background(land, relief):
    return svg_open(1800) + base_layers(land, relief) + "</svg>"


if __name__ == "__main__":
    # usage: make_maps.py land.geojson [relief-map.jpg]
    land = land_path(sys.argv[1])
    relief = ""
    if len(sys.argv) > 2:
        relief = base64.b64encode(open(sys.argv[2], "rb").read()).decode()
    open("viajes-de-pablo-fondo.svg", "w", encoding="utf-8").write(build_background(land, relief))
    open("viajes-de-pablo-completo.svg", "w", encoding="utf-8").write(build_full(land, relief))
    print("ok", round(W), round(H))
