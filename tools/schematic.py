"""Share images drawn as technical schematics: a control flow, an incident timeline or a terminal readout.

Each post describes its own figure in front matter, so no two images share a layout and content:

    diagram:
      type: flow                       # flow | timeline | terminal
      caption: Agent control path, as proposed by the HKMA
      steps:                           # flow: one box per control, top to bottom
        - {id: C-01, label: Business intent, sub: written down before production, test: who owns it?, state: warn}
      events:                          # timeline: one row per event
        - {t: May 27, label: Master key committed, state: fail}
      lines:                           # terminal: $ command, ! finding, # comment
        - "$ grep svc-telemetry ~/.ssh/authorized_keys"

state is ok, warn, fail or info. Without `diagram:`, the post's 1️⃣ 2️⃣ 3️⃣ LinkedIn points become a flow.
"""
import html
import re

STATE = {'ok': '#3DDC97', 'warn': '#FFB020', 'fail': '#FF5A4E', 'info': '#5CC8FF'}
BADGE = {'ok': 'PASS', 'warn': 'TEST', 'fail': 'FAIL', 'info': 'INFO'}
KEYCAP = re.compile(r'^\s*([0-9])️?⃣\s*(.+)$')
e = html.escape

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(w)spx;height:%(h)spx;overflow:hidden}
body{background:#0B0F14;color:#E6EBF0;font-family:"IBM Plex Sans",sans-serif;padding:%(pad)spx;display:flex;flex-direction:column;position:relative;
 background-image:linear-gradient(#18202B 1px,transparent 1px),linear-gradient(90deg,#18202B 1px,transparent 1px),
 linear-gradient(#11171F 1px,transparent 1px),linear-gradient(90deg,#11171F 1px,transparent 1px);
 background-size:120px 120px,120px 120px,24px 24px,24px 24px;background-position:-1px -1px}
.mk{position:absolute;width:28px;height:28px;border-color:#5CC8FF;border-style:solid;opacity:.7}
.mk.a{top:22px;left:22px;border-width:2px 0 0 2px}.mk.b{top:22px;right:22px;border-width:2px 2px 0 0}
.mk.c{bottom:22px;left:22px;border-width:0 0 2px 2px}.mk.d{bottom:22px;right:22px;border-width:0 2px 2px 0}
.mono{font-family:"IBM Plex Mono",monospace}
.hd{display:flex;justify-content:space-between;font:500 %(ks)spx "IBM Plex Mono",monospace;color:#7D8A99;letter-spacing:.06em;
 border-bottom:1px solid #2A3644;padding-bottom:12px}
.hd b{color:#5CC8FF;font-weight:500}
h1{font-weight:700;font-size:%(ts)spx;line-height:1.08;letter-spacing:-.02em;margin:%(g2)spx 0 %(g)spx;max-width:96%%}
.cap{font:500 %(ks)spx "IBM Plex Mono",monospace;color:#7D8A99;letter-spacing:.04em;margin-bottom:%(g)spx}
.cap b{color:#E6EBF0;font-weight:500}
.fig{flex:1;display:flex;min-height:0}
/* flow */
.flow{flex:1;display:flex;flex-direction:%(dir)s;justify-content:center}
.node{position:relative;border:1.5px solid var(--c);background:rgba(11,15,20,.92);display:flex;flex-direction:%(ndir)s;gap:%(g)spx;padding:%(np)spx}
.flow.row{align-items:center}.flow.row .node{flex:1;align-self:stretch;max-height:100%%;justify-content:space-between}
.node .id{font:500 %(ids)spx "IBM Plex Mono",monospace;color:var(--c);letter-spacing:.05em}
.node .lb{font-weight:700;font-size:%(lbs)spx;line-height:1.15;margin-top:4px}
.node .sb{font:500 %(sbs)spx "IBM Plex Mono",monospace;color:#8D9AA9;margin-top:6px;line-height:1.35}
.node .main{flex:1}
.node .ts{font:500 %(sbs)spx "IBM Plex Mono",monospace;color:var(--c);%(tsw)s;line-height:1.35;display:flex;flex-direction:column;gap:4px}
.node .ts i{font-style:normal;align-self:flex-start;border:1px solid var(--c);padding:1px 6px;font-size:%(bgs)spx;letter-spacing:.08em}
.node:before,.node:after{content:"";position:absolute;width:7px;height:7px;background:var(--c)}
.node:before{top:-4px;left:-4px}.node:after{bottom:-4px;right:-4px}
.wire{flex:0 0 %(wl)spx;display:flex;align-items:center;justify-content:center;position:relative}
.wire:before{content:"";position:absolute;background:repeating-linear-gradient(%(wdeg)s,#5CC8FF 0 6px,transparent 6px 11px);%(wline)s}
.wire:after{content:"";position:absolute;%(warrow)s}
/* timeline */
.tl{flex:1;display:flex;flex-direction:%(dir)s;justify-content:space-between;position:relative;%(tlpad)s}
.tl:before{content:"";position:absolute;background:#5CC8FF;opacity:.6;%(axis)s}
.ev{position:relative;display:flex;flex-direction:%(edir)s;gap:%(g)spx;%(evw)s}
.ev .dot{flex:0 0 auto;width:%(dot)spx;height:%(dot)spx;border:2px solid var(--c);background:#0B0F14;transform:rotate(45deg);position:relative;z-index:1;%(dotpos)s}
.ev .dot:after{content:"";position:absolute;inset:4px;background:var(--c)}
.ev .t{font:500 %(ids)spx "IBM Plex Mono",monospace;color:var(--c);letter-spacing:.04em}
.ev .lb{font-size:%(evs)spx;line-height:1.3;margin-top:4px}
.gap{font:700 %(bgs)spx "IBM Plex Mono",monospace;letter-spacing:.08em;color:#FFB020;border:1px dashed #FFB020;padding:3px 8px;align-self:flex-start;%(gappos)s}
/* terminal */
.term{flex:1;border:1.5px solid #2A3644;background:rgba(6,9,12,.95);display:flex;flex-direction:column}
.term .bar{display:flex;gap:8px;align-items:center;padding:12px 16px;border-bottom:1px solid #2A3644;font:500 %(bgs)spx "IBM Plex Mono",monospace;color:#7D8A99}
.term .bar i{width:12px;height:12px;border-radius:50%%;background:#2A3644}
.term pre{padding:%(np)spx;counter-reset:ln;font:500 %(trs)spx/1.55 "IBM Plex Mono",monospace;white-space:pre-wrap;overflow-wrap:anywhere;color:#C9D2DC}
.term pre>span{display:block;counter-increment:ln}.term pre>span:before{content:counter(ln,decimal-leading-zero);display:inline-block;width:2.4em;color:#3A4757}
.term .st{margin-top:auto;display:flex;justify-content:space-between;padding:10px 16px;border-top:1px solid #2A3644;font:500 %(bgs)spx "IBM Plex Mono",monospace;color:#7D8A99}.term .st b{color:#FF5A4E;font-weight:500}
.term .p{color:#5CC8FF}.term .f{color:#FF5A4E}.term .c{color:#5F6C7B}.term .o{color:#3DDC97}
/* readout */
.ro{display:flex;margin-top:%(g)spx;border:1px solid #2A3644;background:rgba(11,15,20,.92)}
.ro div{flex:1;padding:%(rp)spx;border-left:1px solid #2A3644}.ro div:first-child{border-left:0}
.ro b{display:block;font:700 %(rns)spx/1 "IBM Plex Mono",monospace;color:var(--c);letter-spacing:-.02em}
.ro span{display:block;font:500 %(rls)spx "IBM Plex Mono",monospace;color:#8D9AA9;margin-top:8px;line-height:1.35}
.ft{display:flex;justify-content:space-between;align-items:baseline;margin-top:%(g)spx;font:500 %(ks)spx "IBM Plex Mono",monospace;color:#7D8A99}
.ft b{font:700 %(ns)spx "IBM Plex Sans",sans-serif;color:#E6EBF0}
"""


def _points(meta):
    found = []
    for line in (meta.get('linkedin') or '').splitlines():
        m = KEYCAP.match(line)
        if m:
            found.append(re.split(r'(?<=[.?!])\s', m.group(2).strip(), maxsplit=1)[0].rstrip('.'))
    return found


def _spec(meta):
    d = meta.get('diagram')
    if d:
        return d
    steps = [{'id': f'P-{i:02d}', 'label': p, 'state': 'warn'} for i, p in enumerate(_points(meta)[:5], 1)]
    return {'type': 'flow', 'caption': 'Key points', 'steps': steps} if steps else {'type': 'flow', 'steps': []}


def _flow(spec, big):
    steps = spec.get('steps', [])[:5 if big else 4]
    out = []
    for i, s in enumerate(steps):
        c = STATE.get(s.get('state', 'info'), STATE['info'])
        test = s.get('test')
        ts = (f'<div class="ts"><i>{BADGE.get(s.get("state", "info"), "INFO")}</i>{e(test)}</div>' if test else '')
        out.append(f'<div class="node" style="--c:{c}"><div class="main"><div class="id">{e(str(s.get("id", f"C-{i + 1:02d}")))}</div>'
                   f'<div class="lb">{e(str(s["label"]))}</div>'
                   + (f'<div class="sb">{e(str(s["sub"]))}</div>' if s.get('sub') else '') + f'</div>{ts}</div>')
        if i < len(steps) - 1:
            out.append('<div class="wire"></div>')
    return f'<div class="flow{"" if big else " row"}">{"".join(out)}</div>'


def _timeline(spec, big):
    evs = spec.get('events', [])[:7 if big else 5]
    rows = ''.join((f'<div class="gap">{e(str(v["gap"]))}</div>' if v.get('gap') and big else '')
                   + f'<div class="ev" style="--c:{STATE.get(v.get("state", "info"), STATE["info"])}"><div class="dot"></div>'
                   f'<div>' + (f'<div class="gap" style="margin:0 0 6px">{e(str(v["gap"]))}</div>' if v.get('gap') and not big else '')
                   + f'<div class="t">{e(str(v["t"]))}</div><div class="lb">{e(str(v["label"]))}</div></div></div>' for v in evs)
    return f'<div class="tl">{rows}</div>'


def _terminal(spec, big):
    cls = {'$': 'p', '!': 'f', '#': 'c', '+': 'o'}
    lines = []
    for ln in spec.get('lines', [])[:16 if big else 8]:
        ln = str(ln)
        k = cls.get(ln[:1], '')
        lines.append(f'<span class="{k}">{e(ln)}</span>')
    title = e(str(spec.get('title', 'bash')))
    return (f'<div class="term"><div class="bar"><i></i><i></i><i></i><span style="margin-left:8px">{title}</span></div>'
            f'<pre>{"".join(lines)}</pre>'
            f'<div class="st"><span>{e(str(spec.get("note", "")))}</span><b>{sum(1 for l in spec.get("lines", []) if str(l)[:1] == "!")} findings</b></div></div>')


def _readout(meta, big):
    figs = (meta.get('figures') or [])[:3]
    if not figs:
        return ''
    cells = ''.join(f'<div style="--c:{STATE.get({"red": "fail", "amber": "warn", "green": "ok"}.get(f.get("tone"), "info"))}">'
                    f'<b>{e(str(f["n"]))}</b><span>{e(f["label"])}</span></div>' for f in figs)
    return f'<div class="ro">{cells}</div>'


def page(meta, w, h, date):
    big = w < h
    spec = _spec(meta)
    kind = spec.get('type', 'flow')
    n = len(meta['title'])
    v = dict(w=w, h=h, pad=64 if big else 44, ks=17 if big else 14, g=16 if big else 12, g2=28 if big else 16,
             ts=(60 if n <= 50 else 52 if n <= 75 else 46) if big else (40 if n <= 50 else 34),
             ns=22 if big else 18, ids=16 if big else 13, lbs=27 if big else 19, sbs=17 if big else 13, bgs=13 if big else 11,
             np=18 if big else 12, wl=26 if big else 30, rp=16 if big else 10, rns=44 if big else 26, rls=15 if big else 12, evs=23 if big else 16, dot=22 if big else 18,
             trs=25 if big else 15,
             gappos='margin:6px 0 6px 40px' if big else '',
             dir='column' if big else 'row', ndir='row' if big else 'column',
             tsw='width:300px;flex:0 0 300px;border-left:1px dashed #2A3644;padding-left:16px' if big else '',
             wdeg='180deg' if big else '90deg',
             wline='left:50%;top:0;bottom:7px;width:2px;margin-left:-1px' if big else 'top:50%;left:0;right:7px;height:2px;margin-top:-1px',
             warrow=('bottom:0;left:50%;margin-left:-6px;border:6px solid transparent;border-top:8px solid #5CC8FF;border-bottom:0' if big
                     else 'right:0;top:50%;margin-top:-6px;border:6px solid transparent;border-left:8px solid #5CC8FF;border-right:0'),
             tlpad='padding:8px 0 8px 0' if big else 'padding:0 8px;align-items:flex-start',
             axis='left:10px;top:0;bottom:0;width:2px' if big else 'top:9px;left:0;right:0;height:2px',
             edir='row' if big else 'column', evw='' if big else 'flex:1;padding-right:12px',
             dotpos='margin-top:2px' if big else '')
    body = {'timeline': _timeline, 'terminal': _terminal}.get(kind, _flow)(spec, big)
    tag = (meta.get('tags') or ['AI assurance'])[0].upper()
    status = (meta.get('status') or meta.get('kind', 'note')).upper()
    cap = spec.get('caption')
    figno = {'flow': 'FIG.1 // CONTROL FLOW', 'timeline': 'FIG.1 // TIMELINE', 'terminal': 'FIG.1 // EVIDENCE'}.get(kind, 'FIG.1')
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;700&family=IBM+Plex+Sans:wght@500;700&display=swap" rel="stylesheet">
<style>{CSS % v}</style></head><body>
<i class="mk a"></i><i class="mk b"></i><i class="mk c"></i><i class="mk d"></i>
<div class="hd"><span><b>MA/</b> {e(tag)}</span><span>{e(date)} · REV {e(status)}</span></div>
<h1>{e(meta['title'])}</h1>
<div class="cap"><b>{figno}</b>{(' — ' + e(cap)) if cap else ''}</div>
<div class="fig">{body}</div>
{_readout(meta, big)}
<div class="ft"><b>Mihir Ajmera</b><span>mihirajmera.github.io</span></div>
</body></html>"""
