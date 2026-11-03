"""Publish a draft: move it into _posts, render its share images and write the LinkedIn post.

    python tools/publish.py _drafts/my-note.md            # publish today
    python tools/publish.py _drafts/my-note.md 2026-10-24 # publish on a given date
    python tools/publish.py --cards _posts/2026-10-21-x.md # only (re)render images

Outputs:
    _posts/YYYY-MM-DD-slug.md               the post (front matter gets `image:`)
    assets/img/posts/slug.png               1200x630 link-preview image (committed)
    linkedin-out/slug.png                   1080x1350 feed image to upload (not committed)
    linkedin-out/slug.txt                   LinkedIn post text with the link for the first comment
Images are technical schematics drawn from the post's `diagram:` front matter (see tools/schematic.py).
Needs PyYAML and Google Chrome (or Edge).
"""
import datetime as dt
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

import schematic

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://mihirajmera.github.io'
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


def render(meta, out, w, h, date):
    page = schematic.page(meta, w, h, date)
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
        dest, slug, date = src, src.stem[11:], src.stem[:10]
    else:
        date = args[1] if len(args) > 1 else dt.date.today().isoformat()
        slug = src.stem
        dest = ROOT / '_posts' / f'{date}-{slug}.md'

    render(meta, ROOT / 'assets' / 'img' / 'posts' / f'{slug}.png', 1200, 630, date)
    render(meta, ROOT / 'linkedin-out' / f'{slug}.png', 1080, 1350, date)
    if 'image:' not in fm:
        fm = fm.rstrip('\n') + f'\nimage: /assets/img/posts/{slug}.png\n'
    dest.write_text('---' + fm + '---' + body, encoding='utf-8', newline='\n')
    if not cards_only and src != dest:
        src.unlink()

    url = f'{SITE}/blog/{slug}/'
    post = (meta.get('linkedin') or meta.get('description', '')).strip()
    (ROOT / 'linkedin-out' / f'{slug}.txt').write_text(f'{post}\n\n---\nFirst comment:\n{url}?utm_source=linkedin\n', encoding='utf-8')
    print(f'post:     {dest.relative_to(ROOT)}\nimage:    linkedin-out/{slug}.png\nlinkedin: linkedin-out/{slug}.txt\nurl:      {url}')


if __name__ == '__main__':
    main(sys.argv[1:])
