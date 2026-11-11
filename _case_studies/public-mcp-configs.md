---
title: What 2,830 public MCP configs run with
description: An access review of the MCP client configs developers commit to GitHub, across Claude Desktop, Claude Code, VS Code and Cursor. Almost nothing is pinned, and the archived reference servers are still everywhere.
date: 2026-11-11
question: When developers commit their AI agents' MCP configs to public repos, what are those agents running, and would the access survive a review?
method: Collected up to 1,000 configs per client through GitHub code search, removed duplicates by content, and ran agent-access-review on each of the 2,830 that define at least one server. Only aggregate numbers are published.
tools: [agent-access-review]
frameworks: [NIST 800-53, SOC 2, OWASP LLM Top 10]
evidence:
  - {label: method, scripts and aggregate results, url: "https://github.com/Mihirajmera/agent-access-review/tree/main/case-studies/public-mcp-configs"}
numbers:
  - {n: "95%", label: of 1,920 package and image servers have no pinned version, tone: red}
  - {n: "2.8%", label: of configs run an archived reference server, tone: amber}
  - {n: "3.8%", label: of configs contain a real-looking secret, tone: red}
---

## Why this matters

An MCP config is an access grant. It says which servers an AI agent starts, what they can reach and which credentials they hold. In most companies nobody reviews it, because it lives in a developer's editor rather than in an identity system. Public repos are the one place where thousands of these grants can be read side by side.

## What I found

**95% of servers installed from npm, PyPI or a container registry aren't pinned to a version.** That's 1,822 of 1,920. Each one runs whatever was published most recently, every time the agent starts, with the agent's tokens. The rate barely moves by client: 96% for Claude Desktop and VS Code, 95% for Cursor, 91% for Claude Code. This is the same supply-chain gap that dependency pinning closed for application code years ago, reopened by agents.

**The archived reference servers are still running.** 79 configs (2.8%) use a server whose repository was archived and whose npm package is deprecated, so it gets no security fixes. The old GitHub server alone appears in 55 configs, more than twice as often as the container image of GitHub's maintained server (21). Postgres (23), Puppeteer (12), Brave Search (11) and Slack (7) follow.

**3.8% of configs appear to hold a real secret in plain text.** Of the configs with a credential-named value, most hold placeholders such as `YOUR_API_KEY`. The rest look real, and 12 values match a known provider format, mostly OpenAI or Anthropic keys. I didn't test any of them. Those providers take part in GitHub's secret scanning, which is the right channel for revoking them. Cursor configs were the most likely to hardcode a credential: 14%, against 5–9% for the other clients.

**5.9% give one agent a complete exfiltration path.** That means a single agent that reads sensitive data, takes in content outsiders can write, and can send data out, with no human approval on any step.

**Known CVEs were rare, but only because almost nothing is pinned.** One config pinned a release with a critical command injection (`mcp-remote` 0.1.15). The unpinned majority picks up fixes automatically, and it would pick up a malicious release just as automatically. Pinning without a process to update is not a control either; the answer is to pin, then review updates on a schedule.

**No one ran the malicious npm look-alikes.** `mcp-server-fetch` and `mcp-server-git` are real servers on PyPI, run with `uvx`. The npm packages with the same names are flagged as malware. None of the 2,830 configs used them.

## What my own tool got wrong

The first pass reported 25% of Claude Desktop configs as having hardcoded credentials. Most were template placeholders, which buried the real ones. agent-access-review now recognises obvious placeholders and still reports anything that isn't clearly fake. The scan also led to two new checks: AAR-13 for deprecated servers and AAR-14 for known-vulnerable versions and malicious packages.

## Limits

GitHub code search ranks by relevance and stops at 1,000 results per query, so this is a large sample rather than a census. Public repos lean toward templates and demos, and private production configs may be better or worse. No repository names or file contents are published: only totals.

## Try it

```bash
pip install agent-access-review
agent-access-review scan ~/.cursor/mcp.json
```

Or paste a config into the [in-browser playground](/work/#try). It runs locally, and nothing is uploaded.
