"""Built-in illustrations of farm produce (SVG), so FarmConnect shows pictures out of the box.
Real photos in the 'images' folder override these (see images.py)."""
import math

def _svg(bg, body, shadow=True):
    sh = '<ellipse cx="100" cy="128" rx="78" ry="8" fill="#000" fill-opacity=".10"/>' if shadow else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 140" preserveAspectRatio="xMidYMid slice">'
            f'<rect width="200" height="140" fill="{bg}"/>{sh}{body}</svg>')

def _star(cx, cy, r1, r2, fill, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = math.radians(rot + i * 180 / n)
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'

def maize():
    k = ""
    for y in range(26, 116, 8):
        for x in range(80, 124, 8):
            if ((x - 100) / 21) ** 2 + ((y - 70) / 47) ** 2 < 1:
                k += f'<ellipse cx="{x}" cy="{y}" rx="3.3" ry="3.8" fill="#EFA500"/>'
    body = (f'<g transform="rotate(-18 100 70)"><ellipse cx="100" cy="70" rx="24" ry="50" fill="#FBC02D"/>{k}</g>'
            '<path d="M100 128 Q50 112 48 44 Q78 72 102 98Z" fill="#43A047"/>'
            '<path d="M100 128 Q150 112 152 44 Q122 72 98 98Z" fill="#2E7D32"/>'
            '<path d="M100 128 Q84 100 96 62 Q112 100 100 128Z" fill="#66BB6A"/>')
    return _svg("#FFF6D6", body)

def cassava():
    def root(tx, ty, rot, col):
        return (f'<g transform="translate({tx} {ty}) rotate({rot})"><path d="M0 0 Q40 -16 100 -4 Q112 -1 104 7 Q60 22 6 20 Q-8 12 0 0Z" fill="{col}"/>'
                '<path d="M10 8 Q50 -4 96 2" stroke="#6D4326" stroke-width="1.5" fill="none" opacity=".6"/>'
                '<ellipse cx="3" cy="10" rx="6" ry="11" fill="#F6E9C9"/></g>')
    leaf = "".join(f'<ellipse cx="0" cy="-22" rx="5" ry="20" fill="#3E8E41" transform="rotate({a})"/>' for a in (-60, -30, 0, 30, 60))
    body = root(30, 92, -22, "#8A5A3A") + root(40, 108, -8, "#A06B45") + root(48, 74, -34, "#7B4F31") + f'<g transform="translate(160 42)">{leaf}</g>'
    return _svg("#F3ECDC", body)

def yam():
    body = ('<path d="M22 86 Q30 42 96 44 Q170 46 178 86 Q172 118 98 118 Q28 118 22 86Z" fill="#7B5B3A"/>'
            '<path d="M44 74 q10 -6 20 0 M80 62 q12 -6 24 0 M120 74 q10 -6 22 0 M62 96 q12 -6 24 0 M104 100 q10 -6 22 0 M146 92 q8 -5 16 0" '
            'stroke="#5A3E25" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
            '<path d="M150 56 Q170 62 174 84 Q150 80 140 60Z" fill="#E9D3A8"/>'
            '<path d="M62 52 Q70 38 84 36 Q80 48 70 56Z" fill="#43A047"/>')
    return _svg("#F1E8DC", body)

def tomatoes():
    def t(cx, cy, r):
        return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#E53935"/><circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#g)"/>'
                f'<ellipse cx="{cx - r * .4}" cy="{cy - r * .4}" rx="{r * .22}" ry="{r * .13}" fill="#fff" fill-opacity=".55" transform="rotate(-35 {cx - r * .4} {cy - r * .4})"/>'
                + _star(cx, cy - r * .78, r * .38, r * .14, "#2E7D32", 6, -90) + f'<rect x="{cx - 1.5}" y="{cy - r - 6}" width="3" height="8" rx="1.5" fill="#2E7D32"/>')
    body = ('<defs><radialGradient id="g" cx=".35" cy=".3" r=".9"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#7f0000" stop-opacity=".35"/></radialGradient></defs>'
            + t(70, 90, 34) + t(132, 86, 36) + t(100, 58, 30))
    return _svg("#FFEEE9", body)

def pepper():
    def chili(x, y, rot, col, dark):
        return (f'<g transform="translate({x} {y}) rotate({rot})"><path d="M0 0 Q-12 55 38 78 Q52 82 50 74 Q22 60 16 0Z" fill="{col}"/>'
                f'<path d="M4 6 Q2 40 30 66" stroke="#fff" stroke-opacity=".35" stroke-width="3" fill="none" stroke-linecap="round"/>'
                f'<path d="M-4 2 Q8 -10 20 2 Q22 8 12 6 Q4 8 -4 2Z" fill="{dark}"/><path d="M8 -4 Q8 -16 14 -22" stroke="{dark}" stroke-width="4" fill="none" stroke-linecap="round"/></g>')
    body = chili(58, 36, 8, "#D32F2F", "#2E7D32") + chili(112, 34, -6, "#E53935", "#2E7D32") + chili(150, 40, 14, "#43A047", "#1B5E20")
    return _svg("#FFF1E4", body)

def rice():
    g = "".join(f'<ellipse cx="{x}" cy="{y}" rx="4" ry="1.7" fill="#E7E2D6" transform="rotate({r} {x} {y})"/>'
                for x, y, r in [(70, 62, 20), (88, 52, -15), (108, 56, 30), (126, 48, -25), (140, 62, 10), (98, 70, -5), (118, 72, 25), (80, 74, 40), (64, 82, -20), (132, 80, -35)])
    stalk = ('<path d="M24 120 Q22 70 40 30" stroke="#C9A227" stroke-width="2" fill="none"/>'
             + "".join(f'<ellipse cx="{40 - i * 1.5}" cy="{34 + i * 7}" rx="3" ry="6" fill="#E3C24A" transform="rotate({-20 + i * 3} {40 - i * 1.5} {34 + i * 7})"/>' for i in range(4)))
    body = (stalk + '<ellipse cx="102" cy="68" rx="58" ry="32" fill="#FFFFFF"/>' + g +
            '<path d="M42 72 H162 Q160 122 102 126 Q44 122 42 72Z" fill="#C2622D"/><ellipse cx="102" cy="72" rx="60" ry="9" fill="#D97B45"/>'
            '<path d="M60 90 Q102 104 144 90" stroke="#F3C9A6" stroke-width="3" fill="none" stroke-linecap="round" opacity=".7"/>')
    return _svg("#EAF4E4", body)

def beans():
    def bean(x, y, rot, col):
        return (f'<g transform="translate({x} {y}) rotate({rot})"><path d="M-14 0 Q-14 -11 0 -11 Q14 -11 14 -2 Q14 4 6 4 Q0 2 -6 6 Q-14 8 -14 0Z" fill="{col}"/>'
                '<ellipse cx="-3" cy="-5" rx="6" ry="2" fill="#fff" fill-opacity=".3"/></g>')
    pts = [(60, 100, 10), (84, 104, -15), (110, 102, 20), (136, 100, -8), (72, 84, -30), (98, 86, 12), (124, 84, -20), (148, 86, 25),
           (84, 68, 18), (112, 68, -12), (136, 70, 30), (98, 52, -5)]
    cols = ["#8B2E2E", "#A23B3B", "#7A2525", "#B04A4A"]
    body = ('<path d="M20 34 Q60 14 120 26 Q112 40 60 44 Q32 46 20 34Z" fill="#7CB342"/><path d="M26 34 Q62 22 112 30" stroke="#558B2F" stroke-width="2" fill="none"/>'
            + "".join(bean(x, y, r, cols[i % 4]) for i, (x, y, r) in enumerate(pts)))
    return _svg("#F8EEE5", body)

def onions():
    def onion(x, y, s, col, hi):
        return (f'<g transform="translate({x} {y}) scale({s})"><path d="M-6 -24 Q-2 -44 4 -52 Q8 -42 8 -24Z" fill="{hi}"/>'
                f'<ellipse cx="0" cy="0" rx="31" ry="27" fill="{col}"/><path d="M-12 -22 Q-26 0 -10 26 M12 -22 Q26 0 10 26 M0 -26 Q-6 0 0 27" stroke="{hi}" stroke-width="2" fill="none" opacity=".55"/>'
                '<path d="M-6 27 l-3 6 M0 28 v7 M6 27 l3 6" stroke="#D7C9A8" stroke-width="2" stroke-linecap="round"/></g>')
    body = onion(58, 84, .95, "#9C4F96", "#C27DBB") + onion(138, 82, 1.0, "#B35FA8", "#D49BCB") + onion(98, 96, .85, "#E0A93B", "#F2CD7A")
    return _svg("#F5EDF6", body)

def other():
    leaves = "".join(f'<ellipse cx="0" cy="-20" rx="9" ry="26" fill="{c}" transform="rotate({a})"/>' for a, c in [(-50, "#43A047"), (-20, "#66BB6A"), (10, "#2E7D32"), (40, "#43A047")])
    weave = "".join(f'<path d="M{50 + i * 8} 70 L{58 + i * 6} 120" stroke="#8A5F2B" stroke-width="1.6"/>' for i in range(12)) + \
            "".join(f'<path d="M{46 + j * 2} {82 + j * 14} H{154 - j * 2}" stroke="#8A5F2B" stroke-width="1.6"/>' for j in range(3))
    body = (f'<g transform="translate(100 74)">{leaves}</g><circle cx="70" cy="64" r="14" fill="#E53935"/><ellipse cx="136" cy="62" rx="9" ry="16" fill="#FB8C00" transform="rotate(25 136 62)"/>'
            '<path d="M44 68 H156 L146 122 Q100 128 54 122Z" fill="#B98542"/>' + weave + '<rect x="42" y="64" width="116" height="10" rx="5" fill="#9A6C2F"/>')
    return _svg("#EAF5EA", body)

ART = {"maize": maize, "cassava": cassava, "yam": yam, "tomatoes": tomatoes, "tomato": tomatoes, "pepper": pepper,
       "rice": rice, "beans": beans, "onions": onions, "onion": onions}

def svg_for(key):
    return ART.get(key, other)()

def hero_svg():
    hills = ('<path d="M0 150 Q150 90 320 130 T640 120 T800 130 V200 H0Z" fill="#43A047"/>'
             '<path d="M0 175 Q200 125 400 160 T800 150 V200 H0Z" fill="#2E7D32"/>')
    rows = "".join(f'<path d="M{-40 + i * 70} 200 Q{80 + i * 70} 150 {200 + i * 90} 120" stroke="#66BB6A" stroke-width="3" fill="none" opacity=".55"/>' for i in range(9))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 200" preserveAspectRatio="xMidYMid slice">'
            '<defs><linearGradient id="s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A5D6A7"/><stop offset="1" stop-color="#E8F5E9"/></linearGradient></defs>'
            '<rect width="800" height="200" fill="url(#s)"/><circle cx="690" cy="52" r="26" fill="#FDD835"/>' + hills + rows + '</svg>')
