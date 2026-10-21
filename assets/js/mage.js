// Mage: a scripted assistant. Answers come only from _data/mage.yml (embedded as JSON);
// questions are matched by keywords in the browser and never sent anywhere.
(function () {
  const kbEl = document.getElementById('mage-kb');
  if (!kbEl) return;
  const kb = JSON.parse(kbEl.textContent);
  const byId = Object.fromEntries(kb.answers.map((a) => [a.id, a]));
  const base = document.documentElement.dataset.baseurl || '';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const canSpeak = 'speechSynthesis' in window;
  let speak = false;

  const SIGIL = '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 2.5 27.7 9.25v13.5L16 29.5 4.3 22.75V9.25Z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M16 8.5 18 14l5.5 2-5.5 2-2 5.5-2-5.5-5.5-2 5.5-2Z" fill="currentColor"/><circle cx="23.5" cy="8.5" r="2.4" fill="var(--red)"/></svg>';

  const poses = kb.poses || {};
  const asset = (u) => (u ? base + u : '');
  const headImg = () => {
    const i = document.createElement('img');
    i.src = asset(poses.head); i.srcset = `${asset(poses.head)} 1x, ${asset(poses.head2x)} 2x`;
    i.alt = ''; i.width = 40; i.height = 40; i.decoding = 'async';
    return i;
  };
  const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
  const safeUrl = (u) => (/^(https:|mailto:)/.test(u) ? u : u.startsWith('/') ? base + u : null);

  // Launcher and panel
  const launcher = el('button', 'mage-launcher');
  launcher.type = 'button';
  launcher.setAttribute('aria-expanded', 'false');
  launcher.setAttribute('aria-controls', 'mage-panel');
  if (poses.head) launcher.append(headImg()); else launcher.innerHTML = SIGIL;
  launcher.append(el('span', null, 'Ask Mage'));

  const panel = el('section', 'mage-panel');
  panel.id = 'mage-panel';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-label', 'Mage, Mihir’s assistant');
  panel.hidden = true;

  const head = el('header', 'mage-head');
  const avatar = el('span', 'mage-avatar');
  if (poses.head) avatar.append(headImg()); else avatar.innerHTML = SIGIL;
  const title = el('div', 'mage-title');
  title.append(el('b', null, 'Mage'), el('span', null, 'Mihir’s assistant · scripted · runs in your browser'));
  const voice = el('button', 'mage-icon');
  voice.type = 'button';
  voice.setAttribute('aria-pressed', 'false');
  voice.title = 'Read answers aloud';
  voice.setAttribute('aria-label', 'Read answers aloud');
  voice.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M11 5 6 9H2v6h4l5 4V5Z"/><path class="wave" d="M15.5 8.5a5 5 0 0 1 0 7M19 5a10 10 0 0 1 0 14"/></svg>';
  if (!canSpeak) voice.hidden = true;
  const close = el('button', 'mage-icon');
  close.type = 'button';
  close.setAttribute('aria-label', 'Close Mage');
  close.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>';
  head.append(avatar, title, voice, close);

  const log = el('div', 'mage-log');
  log.setAttribute('role', 'log');
  log.setAttribute('aria-live', 'polite');
  const form = el('form', 'mage-form');
  const input = el('input');
  input.type = 'text';
  input.placeholder = 'Ask about Mihir…';
  input.setAttribute('aria-label', 'Ask Mage a question');
  input.maxLength = 200;
  const send = el('button', null, 'Ask');
  send.type = 'submit';
  form.append(input, send);
  const foot = el('p', 'mage-foot', 'Every answer is pre-written. Nothing you type leaves this page.');
  panel.append(head, log, form, foot);
  document.body.append(launcher, panel);

  // Conversation
  let busy = false;
  const scroll = () => { log.scrollTop = log.scrollHeight; };

  function userSays(text) {
    log.append(el('div', 'mage-msg user', text));
    scroll();
  }

  function mageSays(text, links = [], next = []) {
    const msg = el('div', 'mage-msg mage');
    const p = el('p');
    msg.append(p);
    log.append(msg);
    if (speak) { speechSynthesis.cancel(); speechSynthesis.speak(new SpeechSynthesisUtterance(text)); }
    const finish = () => {
      p.textContent = text;
      if (links.length) {
        const row = el('div', 'mage-links');
        links.forEach((l) => {
          const href = safeUrl(l.url);
          if (!href) return;
          const a = el('a', null, l.label + ' →');
          a.href = href;
          if (href.startsWith('https:') && !href.startsWith(location.origin)) { a.target = '_blank'; a.rel = 'noopener'; }
          row.append(a);
        });
        msg.append(row);
      }
      if (next.length) {
        const chips = el('div', 'mage-chips');
        next.forEach((id) => {
          const a = byId[id];
          if (!a) return;
          const b = el('button', null, a.label);
          b.type = 'button';
          b.addEventListener('click', () => ask(a.label, a));
          chips.append(b);
        });
        msg.append(chips);
      }
      busy = false;
      scroll();
    };
    if (reduced) return finish();
    busy = true;
    let i = 0;
    const step = () => {
      i = Math.min(text.length, i + 3);
      p.textContent = text.slice(0, i);
      scroll();
      if (i < text.length) setTimeout(step, 12); else finish();
    };
    step();
  }

  function match(q) {
    const t = ' ' + q.toLowerCase().replace(/[^a-z0-9+#@.\- ]/g, ' ').replace(/\s+/g, ' ') + ' ';
    let best = null, bestScore = 0;
    kb.answers.forEach((a) => {
      let score = 0;
      a.keys.forEach((k) => {
        const key = k.toLowerCase();
        if (t.includes(' ' + key + ' ') || (key.includes(' ') && t.includes(key))) score += key.split(' ').length * (key.includes(' ') ? 2 : 1);
      });
      if (score > bestScore) { best = a; bestScore = score; }
    });
    return best;
  }

  const heroImg = document.querySelector('.mage-img');
  function pose(name) {
    if (!heroImg) return;
    const src = asset(poses[name] || poses.wave);
    if (heroImg.getAttribute('src') !== src) heroImg.src = src;
  }

  function ask(text, answer) {
    if (busy) { setTimeout(() => ask(text, answer), 120); return; }
    userSays(text);
    const a = answer || match(text);
    if (a) { pose(a.pose); mageSays(a.text, a.links || [], a.next || []); }
    else mageSays(kb.fallback, [{ label: 'Email Mihir', url: 'mailto:ajmeramihir10@gmail.com' }], kb.start);
  }

  let greeted = false;
  function open(question) {
    panel.hidden = false;
    launcher.setAttribute('aria-expanded', 'true');
    launcher.classList.add('is-open');
    if (!greeted) { greeted = true; mageSays(kb.greeting, [], kb.start); }
    if (question && byId[question]) setTimeout(() => ask(byId[question].label, byId[question]), reduced ? 0 : 400);
    input.focus({ preventScroll: true });
  }
  function shut() {
    panel.hidden = true;
    launcher.setAttribute('aria-expanded', 'false');
    launcher.classList.remove('is-open');
    if (canSpeak) speechSynthesis.cancel();
    launcher.focus();
  }

  launcher.addEventListener('click', () => (panel.hidden ? open() : shut()));
  close.addEventListener('click', shut);
  voice.addEventListener('click', () => {
    speak = !speak;
    voice.setAttribute('aria-pressed', String(speak));
    if (!speak) speechSynthesis.cancel();
  });
  panel.addEventListener('keydown', (e) => { if (e.key === 'Escape') shut(); });
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const q = input.value.trim();
    if (!q) return;
    input.value = '';
    ask(q);
  });
  document.querySelectorAll('[data-mage-open]').forEach((b) => b.addEventListener('click', (e) => {
    e.preventDefault();
    open(b.dataset.mageOpen);
  }));
})();

// Hero: Mage tilts toward the cursor, and the speech bubble cycles through short lines.
(function () {
  const stage = document.querySelector('.mage-stage');
  if (!stage) return;
  const hero = stage.querySelector('.mage-hero');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const kb = JSON.parse(document.getElementById('mage-kb').textContent);
  if (!reduced && window.matchMedia('(pointer: fine)').matches) {
    let raf = null;
    window.addEventListener('pointermove', (e) => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = null;
        const r = hero.getBoundingClientRect();
        const dx = (e.clientX - (r.left + r.width / 2)) / window.innerWidth;
        const dy = (e.clientY - (r.top + r.height / 2)) / window.innerHeight;
        hero.style.setProperty('--ry', (dx * 22).toFixed(2) + 'deg');
        hero.style.setProperty('--rx', (-dy * 14).toFixed(2) + 'deg');
      });
    }, { passive: true });
  }
  const lines = kb.bubble || [];
  const text = stage.querySelector('.mage-bubble-text');
  if (!text || lines.length < 2 || reduced) return;
  let i = 0;
  setInterval(() => {
    if (document.hidden) return;
    i = (i + 1) % lines.length;
    text.classList.add('swap');
    setTimeout(() => { text.textContent = lines[i]; text.classList.remove('swap'); }, 220);
  }, 3200);
})();
