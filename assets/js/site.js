// Theme switch: an explicit choice is remembered; otherwise follow the system setting.
(function () {
  const root = document.documentElement;
  const media = window.matchMedia('(prefers-color-scheme: dark)');
  const stored = () => { try { return localStorage.getItem('theme'); } catch (e) { return null; } };
  const apply = (t) => {
    root.dataset.theme = t;
    const sw = document.querySelector('.theme-switch');
    if (sw) {
      sw.setAttribute('aria-checked', String(t === 'dark'));
      sw.setAttribute('aria-label', t === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    }
  };
  apply(stored() || (media.matches ? 'dark' : 'light'));
  media.addEventListener('change', (e) => { if (!stored()) apply(e.matches ? 'dark' : 'light'); });
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.theme-switch')) return;
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('theme', next); } catch (err) {}
    apply(next);
  });
})();

// Ledger: posts and data entries are rendered separately, so sort them newest first.
document.querySelectorAll('ol[data-sort="date"]').forEach((list) => {
  [...list.children]
    .sort((a, b) => (b.dataset.date || '').localeCompare(a.dataset.date || ''))
    .forEach((li) => list.appendChild(li));
});

// Filters: buttons inside a [data-filter-scope] show only items with a matching data-kind.
document.querySelectorAll('[data-filter-scope]').forEach((scope) => {
  const buttons = scope.querySelectorAll('.filters button');
  buttons.forEach((btn) => btn.addEventListener('click', () => {
    const kind = btn.dataset.filter;
    buttons.forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
    scope.querySelectorAll('[data-kind]').forEach((item) => {
      item.hidden = kind !== 'all' && !item.dataset.kind.split(' ').includes(kind);
    });
  }));
});

// Live status card: public GitHub, PyPI and OpenSSF Scorecard APIs, no token.
(async function () {
  const card = document.querySelector('.status');
  if (!card) return;
  const repos = ['agent-access-review', 'llm-redteam-evidence'];
  const getJSON = (url) => fetch(url).then((r) => (r.ok ? r.json() : Promise.reject(r.status)));
  let allGreen = true, anyData = false;

  await Promise.all(repos.map(async (repo) => {
    const row = card.querySelector(`[data-repo="${repo}"]`);
    try {
      const runs = await getJSON(`https://api.github.com/repos/Mihirajmera/${repo}/actions/workflows/tests.yml/runs?branch=main&status=completed&per_page=10`);
      const squares = row.querySelectorAll('.runs span');
      runs.workflow_runs.slice(0, 10).reverse().forEach((run, i) => {
        const c = run.conclusion === 'success' ? 'ok' : run.conclusion === 'failure' ? 'no' : 'other';
        squares[i].className = c;
        squares[i].title = `${run.conclusion} · ${run.created_at.slice(0, 10)} · ${run.head_sha.slice(0, 7)}`;
      });
      if (runs.workflow_runs[0] && runs.workflow_runs[0].conclusion !== 'success') allGreen = false;
      anyData = true;
    } catch (e) { allGreen = false; }
    try {
      const pkg = await getJSON(`https://pypi.org/pypi/${repo}/json`);
      row.querySelector('.ver').textContent = 'v' + pkg.info.version;
    } catch (e) {}
    try {
      const sc = await getJSON(`https://api.scorecard.dev/projects/github.com/Mihirajmera/${repo}`);
      const el = card.querySelector(`[data-score="${repo}"]`);
      if (el) el.textContent = sc.score.toFixed(1);
    } catch (e) {}
  }));

  const head = card.querySelector('.status-head span:last-child');
  const dot = card.querySelector('.status-head .dot');
  if (anyData) {
    head.textContent = allGreen ? 'All checks passing' : 'A check needs attention';
    dot.className = 'dot' + (allGreen ? '' : ' warn');
  } else {
    head.textContent = 'Live status unavailable';
    dot.className = 'dot warn';
  }
  card.querySelector('.status-foot').textContent = 'live from GitHub, PyPI, Scorecard · ' +
    new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
})();
