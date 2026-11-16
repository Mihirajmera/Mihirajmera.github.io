"""LinkedIn feed images (1080x1350) in three print-inspired editions that rotate every 21 days.

    workpaper  an audit working paper: header block, tickmarked table, summary
    memo       a typed memorandum: TO / FROM / DATE / RE, numbered findings
    poster     a Swiss poster: one accent colour, the headline number set large

The edition follows the day the image is rendered, not the post's date, so everything posted to the feed in the
same 21-day window shares a design. Cycle: workpaper from 2026-11-16, memo from 12-07, poster from 12-28, repeat.
"""
import datetime as dt
import html

e = html.escape
ANCHOR, CYCLE = dt.date(2026, 11, 16), 21
FONTS = ('<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700'
         '&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Sans+Condensed:wght@600;700'
         '&family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400&family=Source+Serif+4:ital,opsz,wght@0,8..60,600;1,8..60,400'
         '&display=swap" rel="stylesheet">')
TERM_STATE = {'!': 'fail', '+': 'ok', '$': 'info', '#': 'info'}


def edition_for(day):
    return ('workpaper', 'memo', 'poster')[(day - ANCHOR).days // CYCLE % 3]


def rows(spec):
    """Every diagram type as rows of ref, label, detail, result, state."""
    kind = spec.get('type', 'flow')
    if kind == 'timeline':
        return [dict(ref=str(v['t']), label=str(v['label']), detail='', result=str(v.get('gap', '')),
                     state=v.get('state', 'info'), mono=False) for v in spec.get('events', [])[:7]]
    if kind == 'terminal':
        out = []
        for i, ln in enumerate(spec.get('lines', [])[:9], 1):
            ln = str(ln)
            out.append(dict(ref=f'{i:02d}', label=ln[1:].strip() if ln[:1] in TERM_STATE else ln, detail='', result='',
                            state=TERM_STATE.get(ln[:1], 'info'), mono=True))
        return out
    return [dict(ref=str(s.get('id', f'{i:02d}')), label=str(s['label']), detail=str(s.get('sub', '')),
                 result=str(s.get('test', '')), state=s.get('state', 'info'), mono=False)
            for i, s in enumerate(spec.get('steps', [])[:5], 1)]


def _title_size(title, sizes):
    n = len(title)
    return sizes[0] if n <= 50 else sizes[1] if n <= 80 else sizes[2]


def _shell(w, h, css, body):
    return (f'<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>'
            f'*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:{w}px;height:{h}px;overflow:hidden}}'
            f'body{{display:flex;flex-direction:column;-webkit-font-smoothing:antialiased}}{css}</style></head><body>{body}</body></html>')


# ---------------------------------------------------------------- workpaper
WP_CSS = """
body{background:#F2EEE5;color:#1B1B1B;padding:60px 64px 52px;font-family:"IBM Plex Sans",sans-serif}
.hb{display:grid;grid-template-columns:1fr 1fr;border:1.5px solid #1B1B1B}
.hb div{padding:12px 16px;font:400 19px "IBM Plex Mono",monospace;border-right:1px solid #1B1B1B;border-bottom:1px solid #1B1B1B}
.hb div:nth-child(2n){border-right:0}.hb div:nth-last-child(-n+2){border-bottom:0}
.hb span{display:block;font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#6B655A;margin-bottom:3px}
.hb .blank{color:#9C9584}
h1{font:600 %(ts)spx/1.08 "Source Serif 4",serif;letter-spacing:-.01em;margin:42px 0 14px}
.obj{font:italic 400 24px/1.35 "Source Serif 4",serif;color:#4A453C;margin-bottom:26px}
.tb{flex:1;display:flex;flex-direction:column;min-height:0}
.tr:last-child{border-bottom:0}
.tr{flex:1;display:grid;grid-template-columns:120px 1fr 290px;align-items:center;border-bottom:1px solid #C9C1AE;padding:10px 0}
.tr.th{flex:0 0 auto;font:600 14px "IBM Plex Mono",monospace;letter-spacing:.12em;text-transform:uppercase;color:#6B655A;border-bottom:1.5px solid #1B1B1B;padding:0 0 8px}
.r{font:600 19px "IBM Plex Mono",monospace;color:#6B655A}
.l b{display:block;font:600 %(ls)spx/1.18 "Source Serif 4",serif}
.l b.mono{font:400 %(ms)spx/1.35 "IBM Plex Mono",monospace}
.l span{display:block;font:400 19px/1.35 "IBM Plex Sans",sans-serif;color:#5E584D;margin-top:5px}
.k{display:flex;gap:12px;align-items:flex-start;font:400 19px/1.35 "IBM Plex Sans",sans-serif;color:#3A362F;padding-left:18px}
.k i{flex:0 0 30px;font:600 32px/1 "IBM Plex Sans",sans-serif;color:#B42318;font-style:normal;margin-top:-4px}
.sum{margin-top:30px;display:flex;border-top:1.5px solid #1B1B1B;padding-top:18px}
.sum div{flex:1;padding-right:20px}.sum div+div{border-left:1px solid #C9C1AE;padding-left:20px}
.sum b{display:block;font:600 54px/1 "Source Serif 4",serif}.sum b.red{color:#B42318}
.sum span{display:block;font:400 16px/1.35 "IBM Plex Sans",sans-serif;color:#5E584D;margin-top:8px}
.ft{display:flex;justify-content:space-between;margin-top:24px;font:400 15px "IBM Plex Mono",monospace;color:#6B655A}
.ft b{font-weight:600;color:#1B1B1B}
"""
TICK = {'ok': '✓', 'fail': '✗', 'warn': '△', 'info': '·'}


def workpaper(meta, w, h, date, spec):
    rs = rows(spec)
    tight = len(rs) > 5
    d = dt.date.fromisoformat(date)
    tag = (meta.get('tags') or ['AI assurance'])[0]
    ref = ''.join(p[0] for p in tag.split()[:2]).upper() + d.strftime('-%m%d')
    body_rows = ''.join(
        f'<div class="tr"><span class="r">{e(r["ref"])}</span><div class="l"><b class="{"mono" if r["mono"] else ""}">{e(r["label"])}</b>'
        + (f'<span>{e(r["detail"])}</span>' if r['detail'] else '') + '</div>'
        f'<div class="k"><i>{TICK.get(r["state"], "·")}</i><span>{e(r["result"])}</span></div></div>' for r in rs)
    figs = (meta.get('figures') or [])[:3]
    summary = ''.join(f'<div><b class="{"red" if f.get("tone") == "red" else ""}">{e(str(f["n"]))}</b><span>{e(f["label"])}</span></div>'
                      for f in figs)
    cap = spec.get('caption')
    css = WP_CSS % dict(ts=_title_size(meta['title'], (72, 62, 52)), ls=26 if tight else 30, ms=20 if tight else 23)
    body = f"""
<div class="hb"><div><span>Subject</span>{e(tag)}</div><div><span>W/P ref</span>{e(ref)}</div>
<div><span>Prepared by</span>M. Ajmera · {d.strftime('%d %b %Y').lstrip('0')}</div><div><span>Reviewed by</span><em class="blank">________________</em></div></div>
<h1>{e(meta['title'])}</h1>
{f'<div class="obj">Objective: {e(cap)}</div>' if cap else ''}
<div class="tb"><div class="tr th"><span>Ref</span><span>Item tested</span><span style="padding-left:18px">Result</span></div>{body_rows}</div>
{f'<div class="sum">{summary}</div>' if summary else ''}
<div class="ft"><span><b>Mihir Ajmera</b> · ✓ agreed ✗ exception △ open · note</span><span>mihirajmera.github.io</span></div>"""
    return _shell(w, h, css, body)


# ---------------------------------------------------------------- memo
MEMO_CSS = """
body{background:#FBFBF8;color:#161616;padding:72px 72px 56px;font-family:"IBM Plex Serif",serif}
.mh{font:700 24px "IBM Plex Mono",monospace;letter-spacing:.32em}
.rule{border-top:3px solid #161616;border-bottom:1px solid #161616;height:7px;margin:14px 0 22px}
.fl{display:grid;grid-template-columns:110px 1fr;row-gap:6px;font:400 20px "IBM Plex Mono",monospace}
.fl span{color:#6E6E6E}
.re{font:400 20px "IBM Plex Mono",monospace;color:#6E6E6E;margin-top:26px}
h1{font:600 %(ts)spx/1.1 "IBM Plex Serif",serif;letter-spacing:-.01em;margin-top:6px}
.lead{font:italic 400 23px/1.4 "IBM Plex Serif",serif;color:#444;margin-top:16px;padding-bottom:22px;border-bottom:1px solid #D4D4D0}
ol{list-style:none;flex:1;display:flex;flex-direction:column;min-height:0}
li{flex:1;display:grid;grid-template-columns:58px 1fr auto;column-gap:10px;align-items:center;padding:10px 0;border-bottom:1px solid #E6E6E2}
li .n{font:600 22px "IBM Plex Mono",monospace;color:#6E6E6E}
li b{font:600 %(ls)spx/1.25 "IBM Plex Serif",serif;display:block}
li b.mono{font:400 %(ms)spx/1.35 "IBM Plex Mono",monospace}
li p{font:400 19px/1.4 "IBM Plex Sans",sans-serif;color:#555;margin-top:4px}
li .s{font:600 15px "IBM Plex Mono",monospace;letter-spacing:.08em;white-space:nowrap}
.fail{color:#B91C1C}.warn{color:#8A5A00}.ok{color:#161616}.info{color:#8C8C8C}
.kf{margin-top:28px;display:flex;border:1.5px solid #161616}
.kf div{flex:1;padding:16px 18px}.kf div+div{border-left:1px solid #161616}
.kf b{display:block;font:700 40px/1 "IBM Plex Mono",monospace}.kf b.red{color:#B91C1C}
.kf span{display:block;font:400 16px/1.35 "IBM Plex Sans",sans-serif;color:#555;margin-top:8px}
.ft{display:flex;justify-content:space-between;margin-top:22px;font:400 16px "IBM Plex Mono",monospace;color:#6E6E6E}
"""
STATUS = {'ok': 'SATISFIED', 'fail': 'EXCEPTION', 'warn': 'OPEN', 'info': 'NOTE'}


def memo(meta, w, h, date, spec):
    rs = rows(spec)
    tight = len(rs) > 5
    d = dt.date.fromisoformat(date)
    items = ''.join(
        f'<li><span class="n">{i}.</span><div><b class="{"mono" if r["mono"] else ""}">{e(r["label"])}</b>'
        + (f'<p>{e(" · ".join(x for x in (r["detail"], r["result"]) if x))}</p>' if r['detail'] or r['result'] else '')
        + f'</div><span class="s {r["state"]}">[{STATUS.get(r["state"], "NOTE")}]</span></li>' for i, r in enumerate(rs, 1))
    figs = (meta.get('figures') or [])[:3]
    kf = ''.join(f'<div><b class="{"red" if f.get("tone") == "red" else ""}">{e(str(f["n"]))}</b><span>{e(f["label"])}</span></div>'
                 for f in figs)
    cap = spec.get('caption')
    css = MEMO_CSS % dict(ts=_title_size(meta['title'], (64, 54, 46)), ls=25 if tight else 29, ms=19 if tight else 22)
    body = f"""
<div class="mh">MEMORANDUM</div><div class="rule"></div>
<div class="fl"><span>TO:</span><div>Reviewers approving AI systems</div><span>FROM:</span><div>Mihir Ajmera, GRC engineering</div>
<span>DATE:</span><div>{d.strftime('%d %B %Y').lstrip('0')}</div></div>
<div class="re">RE:</div><h1>{e(meta['title'])}</h1>
{f'<div class="lead">{e(cap[:1].upper() + cap[1:])}.</div>' if cap else ''}
<ol>{items}</ol>
{f'<div class="kf">{kf}</div>' if kf else ''}
<div class="ft"><span>{e((meta.get('tags') or ['AI assurance'])[0])}</span><span>mihirajmera.github.io</span></div>"""
    return _shell(w, h, css, body)


# ---------------------------------------------------------------- poster
POSTER_CSS = """
body{background:#F4F3EF;color:#111;padding:60px 64px 52px;font-family:"IBM Plex Sans",sans-serif}
.top{display:flex;justify-content:space-between;font:600 19px "IBM Plex Sans Condensed",sans-serif;letter-spacing:.1em;text-transform:uppercase;padding-bottom:14px;border-bottom:6px solid #111}
.hero{display:flex;align-items:flex-end;gap:28px;margin-top:30px}
.hero b{font:700 %(hs)spx/.82 "IBM Plex Sans Condensed",sans-serif;color:#D62D20;letter-spacing:-.03em}
.hero span{font:400 22px/1.3 "IBM Plex Sans",sans-serif;max-width:380px;padding-bottom:6px}
h1{font:700 %(ts)spx/1.02 "IBM Plex Sans Condensed",sans-serif;letter-spacing:-.01em;margin-top:34px}
.rows{margin-top:30px;border-top:1.5px solid #111;flex:1;display:flex;flex-direction:column;min-height:0}
.row{flex:1;display:grid;grid-template-columns:84px 1fr auto;column-gap:14px;align-items:center;padding:10px 0;border-bottom:1px solid #C8C6BE}
.row .n{font:700 34px/1 "IBM Plex Sans Condensed",sans-serif}
.row b{display:block;font:600 %(ls)spx/1.2 "IBM Plex Sans",sans-serif}
.row b.mono{font:400 %(ms)spx/1.35 "IBM Plex Mono",monospace}
.row p{font:400 19px/1.35 "IBM Plex Sans",sans-serif;color:#5B5952;margin-top:4px}
.row .s{font:600 17px "IBM Plex Sans Condensed",sans-serif;letter-spacing:.1em;text-transform:uppercase;color:#77756D}
.row .s.fail,.row .s.warn{color:#D62D20}
.more{display:flex;gap:40px;padding-top:24px}
.more div{flex:1}.more b{display:block;font:700 44px/1 "IBM Plex Sans Condensed",sans-serif}
.more span{display:block;font:400 16px/1.35 "IBM Plex Sans",sans-serif;color:#5B5952;margin-top:6px}
.ft{display:flex;justify-content:space-between;align-items:baseline;margin-top:26px;padding-top:14px;border-top:1.5px solid #111;font:400 16px "IBM Plex Sans",sans-serif}
.ft b{font:700 22px "IBM Plex Sans Condensed",sans-serif;letter-spacing:.02em}
"""
WORD = {'ok': 'Pass', 'fail': 'Fail', 'warn': 'Open', 'info': ''}


def poster(meta, w, h, date, spec):
    rs = rows(spec)
    tight = len(rs) > 5
    figs = (meta.get('figures') or [])[:3]
    hero, rest = (figs[0], figs[1:]) if figs else (None, [])
    hs = 0
    if hero:
        hs = {1: 260, 2: 260, 3: 230, 4: 190, 5: 160}.get(len(str(hero['n'])), 130)
    items = ''.join(
        f'<div class="row"><span class="n">{i:02d}</span><div><b class="{"mono" if r["mono"] else ""}">{e(r["label"])}</b>'
        + (f'<p>{e(" · ".join(x for x in (r["detail"], r["result"]) if x))}</p>' if r['detail'] or r['result'] else '')
        + f'</div><span class="s {r["state"]}">{WORD.get(r["state"], "")}</span></div>' for i, r in enumerate(rs, 1))
    more = ''.join(f'<div><b>{e(str(f["n"]))}</b><span>{e(f["label"])}</span></div>' for f in rest)
    d = dt.date.fromisoformat(date)
    css = POSTER_CSS % dict(hs=hs, ts=_title_size(meta['title'], (76, 64, 54)) - (6 if hero else 0),
                            ls=24 if tight else 28, ms=19 if tight else 22)
    body = f"""
<div class="top"><span>{e((meta.get('tags') or ['AI assurance'])[0])}</span><span>{d.strftime('%d.%m.%Y')}</span></div>
{f'<div class="hero"><b>{e(str(hero["n"]))}</b><span>{e(hero["label"])}</span></div>' if hero else ''}
<h1>{e(meta['title'])}</h1>
<div class="rows">{items}</div>
{f'<div class="more">{more}</div>' if more else ''}
<div class="ft"><b>Mihir Ajmera</b><span>mihirajmera.github.io</span></div>"""
    return _shell(w, h, css, body)


def page(meta, w, h, date, spec, edition=None):
    return {'workpaper': workpaper, 'memo': memo, 'poster': poster}[edition or edition_for(dt.date.today())](meta, w, h, date, spec)


assert [edition_for(dt.date.fromisoformat(x)) for x in ('2026-11-16', '2026-12-06', '2026-12-07', '2026-12-28', '2027-01-18')] == \
       ['workpaper', 'workpaper', 'memo', 'poster', 'workpaper']
