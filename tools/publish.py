"""Publish a draft: move it into _posts, render its share images and write the LinkedIn post.

    python tools/publish.py _drafts/my-note.md            # publish today
    python tools/publish.py _drafts/my-note.md 2026-10-24 # publish on a given date
    python tools/publish.py --cards _posts/2026-10-21-x.md # only (re)render images

Outputs:
    _posts/YYYY-MM-DD-slug.md               the post (front matter gets `image:`)
    assets/img/posts/slug.png               1200x630 link-preview image (committed)
    linkedin-out/slug.png                   1080x1350 feed image to upload (not committed)
    linkedin-out/slug.txt                   LinkedIn post text with the link for the first comment
Needs PyYAML and Google Chrome (or Edge).
"""
import datetime as dt
import html
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://mihirajmera.github.io'
TONES = {'red': '#B3261E', 'amber': '#8F6100', 'green': '#1E6B3A'}
TAGS = {'block': ('#F6E1DE', '#8E1F17'), 'review': ('#F4E9D2', '#6B4600'), 'fixed': ('#E3EFE6', '#1E6B3A'),
        'release': ('#E4E7EC', '#2B3440'), 'note': ('#ECEAE4', '#3D3B37'), 'essay': ('#141414', '#F4F3EF')}
BROWSERS = [r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 'google-chrome', 'chromium']


def split(path):
    text = path.read_text(encoding='utf-8')
    _, fm, body = text.split('---', 2)
    return yaml.safe_load(fm), fm, body


def browser():
    for b in BROWSERS:
        if Path(b).exists() or shutil.which(b):
            return b
    sys.exit('Chrome or Edge not found; install one or add it to BROWSERS.')


def more(meta):
    figs = (meta.get('figures') or [])[1:3]
    if not figs:
        return ''
    cells = ''.join(f'<div><b style="color:{TONES.get(f.get("tone"), "#141414")}">{html.escape(str(f["n"]))}</b>'
                    f'<span>{html.escape(f["label"])}</span></div>' for f in figs)
    return f'<div class="more">{cells}</div>'


def render(meta, out, w, h):
    fig = (meta.get('figures') or [{}])[0]
    status = meta.get('status') or meta.get('kind', 'note')
    tagbg, tagtx = TAGS.get(status, TAGS['note'])
    big = w < h
    values = {
        'w': w, 'h': h, 'pad': 80 if big else 64, 'gap': 20 if big else 16, 'gap2': 56 if big else 36,
        'ks': 22 if big else 18, 'ts': 84 if big else 54, 'ss': 300 if big else 150, 'ls': 30 if big else 24,
        'lw': 520 if big else 440, 'ns': 28 if big else 22, 'tagbg': tagbg, 'tagtx': tagtx,
        'statc': TONES.get(fig.get('tone'), '#141414'),
        'kicker': html.escape(('ESSAY' if meta.get('kind') == 'essay' else 'NOTE') + ' · ' + (meta.get('tags') or ['AI assurance'])[0].upper()),
        'status': html.escape(status.upper()), 'title': html.escape(meta['title']),
        'more': more(meta) if big else '',
        'stat': html.escape(str(fig.get('n', ''))), 'statlabel': html.escape(fig.get('label', meta.get('description', ''))),
    }
    if not fig.get('n'):  # no headline number: let the description carry the card
        values.update(stat='', ts=104 if big else 60, ls=44 if big else 30, lw=920 if big else 1072)
    page = (ROOT / 'tools' / 'card.html').read_text(encoding='utf-8')
    for k, v in values.items():
        page = page.replace('{' + k + '}', str(v))
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / 'card.html'
        src.write_text(page, encoding='utf-8')
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([browser(), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                        f'--window-size={w},{h}', '--virtual-time-budget=4000', f'--screenshot={out}', src.as_uri()],
                       check=True, capture_output=True)


def main(args):
    cards_only = args and args[0] == '--cards'
    if cards_only:
        args = args[1:]
    if not args:
        sys.exit(__doc__)
    src = Path(args[0]).resolve()
    meta, fm, body = split(src)
    if cards_only:
        dest, slug = src, src.stem[11:]
    else:
        date = args[1] if len(args) > 1 else dt.date.today().isoformat()
        slug = src.stem
        dest = ROOT / '_posts' / f'{date}-{slug}.md'

    render(meta, ROOT / 'assets' / 'img' / 'posts' / f'{slug}.png', 1200, 630)
    render(meta, ROOT / 'linkedin-out' / f'{slug}.png', 1080, 1350)
    if 'image:' not in fm:
        fm = fm.rstrip('\n') + f'\nimage: /assets/img/posts/{slug}.png\n'
    dest.write_text('---' + fm + '---' + body, encoding='utf-8', newline='\n')
    if not cards_only and src != dest:
        src.unlink()

    url = f'{SITE}/blog/{slug}/'
    post = (meta.get('linkedin') or meta.get('description', '')).strip()
    (ROOT / 'linkedin-out' / f'{slug}.txt').write_text(f'{post}\n\n---\nFirst comment:\n{url}\n', encoding='utf-8')
    print(f'post:     {dest.relative_to(ROOT)}\nimage:    linkedin-out/{slug}.png\nlinkedin: linkedin-out/{slug}.txt\nurl:      {url}')


if __name__ == '__main__':
    main(sys.argv[1:])
