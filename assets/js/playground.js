// In-browser agent-access-review: Pyodide runs the published PyPI package locally.
// The pasted config is never uploaded; only Pyodide and the package itself are downloaded.
(function () {
  const root = document.getElementById('playground');
  if (!root) return;
  const PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.27.2/full/';
  const PACKAGE = 'agent-access-review==0.2.1';
  const $ = (s) => root.querySelector(s);
  const input = $('#pg-input'), run = $('#pg-run'), status = $('#pg-status'), out = $('#pg-out');
  const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
  let pyodide = null;

  $('#pg-example').addEventListener('click', async () => {
    const r = await fetch(root.dataset.sample);
    input.value = await r.text();
  });
  $('#pg-clear').addEventListener('click', () => { input.value = ''; out.replaceChildren(); status.textContent = ''; });

  const PY = `
import datetime, json, pathlib
from agent_access_review.parsers import load
from agent_access_review.checks import run_all, CONTROLS
from agent_access_review.report import grant_decision
from agent_access_review.model import SEVERITY_ORDER

text = CONFIG.strip()
path = pathlib.Path('/tmp/mcp.json' if text.startswith('{') else '/tmp/agents.yaml')
path.write_text(text, encoding='utf-8')
result = []
for agent in load(path, source='pasted config'):
    findings = sorted(run_all(agent, datetime.date.today()), key=lambda f: (-SEVERITY_ORDER[f.severity], f.check_id))
    result.append({
        'agent': agent.name,
        'grants': [{'tool': g.tool, 'category': g.category or 'unclassified', 'actions': sorted(g.actions),
                    'pinned': g.pinned, 'decision': grant_decision(g, findings)} for g in agent.grants],
        'findings': [{'id': f.check_id, 'title': CONTROLS[f.check_id]['title'], 'severity': f.severity,
                      'tool': f.tool, 'message': f.message, 'rec': f.recommendation} for f in findings],
    })
json.dumps(result)
`;

  async function boot() {
    if (pyodide) return pyodide;
    status.textContent = 'Loading Python in your browser (first run only, about 10 MB)…';
    await new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = PYODIDE + 'pyodide.js';
      s.onload = resolve;
      s.onerror = () => reject(new Error('Could not load Pyodide from the CDN.'));
      document.head.append(s);
    });
    pyodide = await window.loadPyodide({ indexURL: PYODIDE });
    status.textContent = 'Installing agent-access-review from PyPI…';
    await pyodide.loadPackage(['micropip', 'pyyaml']);
    await pyodide.pyimport('micropip').install(PACKAGE);
    return pyodide;
  }

  function render(results) {
    out.replaceChildren();
    if (!results.length) {
      out.append(el('p', 'pg-empty', 'No MCP servers or agents found. Paste a claude_desktop_config.json, a VS Code mcp.json or an agents.yaml manifest.'));
      return;
    }
    results.forEach((r) => {
      const sev = { high: 0, medium: 0, low: 0 };
      r.findings.forEach((f) => { sev[f.severity] += 1; });
      const card = el('article', 'pg-result');
      const top = el('div', 'pg-sev');
      [['high', 'High'], ['medium', 'Medium'], ['low', 'Low']].forEach(([k, label]) => {
        const c = el('div', 'pg-sev-' + k);
        c.append(el('b', null, String(sev[k])), el('span', null, label + ' findings'));
        top.append(c);
      });
      const servers = el('div', 'pg-sev-servers');
      servers.append(el('b', null, String(r.grants.length)), el('span', null, 'servers reviewed'));
      top.append(servers);
      card.append(top);

      const table = el('table', 'pg-table');
      const thead = el('thead'); const hr = el('tr');
      ['Server', 'Capability', 'Can', 'Pinned', 'Decision'].forEach((h) => hr.append(el('th', null, h)));
      thead.append(hr); table.append(thead);
      const tb = el('tbody');
      r.grants.forEach((g) => {
        const tr = el('tr');
        tr.append(el('td', 'mono', g.tool), el('td', null, g.category), el('td', null, g.actions.join(', ')),
          el('td', null, g.pinned === null ? 'n/a' : g.pinned ? 'yes' : 'no'));
        const d = el('td'); d.append(el('span', 'tag ' + ({ Keep: 'fixed', Modify: 'review', Revoke: 'block', Investigate: 'review' })[g.decision], g.decision.toUpperCase()));
        tr.append(d); tb.append(tr);
      });
      table.append(tb);
      const wrap = el('div', 'table-wrap'); wrap.append(table);
      card.append(wrap);

      const list = el('ol', 'pg-findings');
      r.findings.forEach((f) => {
        const li = el('li');
        const h = el('div', 'pg-f-head');
        h.append(el('span', 'tag ' + ({ high: 'block', medium: 'review', low: 'release' })[f.severity], f.severity.toUpperCase()),
          el('span', 'mono', f.id), el('b', null, f.title));
        li.append(h, el('p', null, (f.tool ? f.tool + ': ' : '') + f.message), el('p', 'muted', '→ ' + f.rec));
        list.append(li);
      });
      card.append(list);
      out.append(card);
    });
  }

  run.addEventListener('click', async () => {
    const text = input.value.trim();
    if (!text) { status.textContent = 'Paste a config or load the example first.'; input.focus(); return; }
    run.disabled = true;
    out.replaceChildren();
    try {
      const py = await boot();
      status.textContent = 'Reviewing…';
      py.globals.set('CONFIG', text);
      const results = JSON.parse(await py.runPythonAsync(PY));
      render(results);
      const n = results.reduce((a, r) => a + r.findings.length, 0);
      status.textContent = `Done: ${n} finding${n === 1 ? '' : 's'}. Ran locally with ${PACKAGE}.`;
    } catch (e) {
      const msg = String(e && e.message || e).split('\n').filter(Boolean).pop();
      status.textContent = 'Could not review that input: ' + msg;
    } finally {
      run.disabled = false;
    }
  });
})();
