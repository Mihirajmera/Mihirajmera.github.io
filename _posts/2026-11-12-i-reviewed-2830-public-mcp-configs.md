---
title: "I reviewed 2,830 public MCP configs. 95% of their servers aren't pinned."
description: "I collected the MCP client configs developers commit to public GitHub repos, from Claude Desktop, Claude Code, VS Code and Cursor, and ran an access review on each one. Almost nothing is pinned, the archived reference servers are still everywhere, and about one config in 26 holds a real-looking secret. Here's what to check in your own."
kind: essay
research: true
status: review
evidence:
  hash: public-mcp-configs
  label: "Case study: method, scripts and aggregate results"
  url: https://mihirajmera.github.io/case-studies/public-mcp-configs/
tags: [AI agents, MCP, Supply chain, Access review]
figures:
  - {n: "95%", label: "of 1,920 package and image servers have no pinned version", tone: red}
  - {n: "55", label: "configs still run the archived GitHub server", tone: amber}
  - {n: "3.8%", label: "of configs hold a real-looking secret in plain text", tone: red}
diagram:
  type: terminal
  title: agent-access-review over 2,830 public MCP configs
  caption: four MCP clients, collected 2026-11-11
  note: totals only; no repository names or values published
  lines:
    - "$ agent-access-review scan public-configs/"
    - "# 2,830 configs · 4,896 servers"
    - "! AAR-10  1,822 of 1,920 package servers unpinned (95%)"
    - "! AAR-13  79 configs run an archived reference server"
    - "! AAR-06  109 configs hold a real-looking secret"
    - "! AAR-09  166 configs have a full exfiltration path"
    - "! AAR-14  1 pinned to a critical CVE (mcp-remote 0.1.15)"
    - "+ 0 configs run the malicious npm look-alikes"
linkedin: |
  I reviewed 2,830 MCP configs that developers committed to public GitHub repos. 95% of the servers they install aren't pinned to a version.

  An MCP config is an access grant: which servers an AI agent starts, what they reach, which tokens they hold. It lives in an editor, so almost nobody reviews it. Public repos are the one place you can read thousands side by side, so I ran an access review on every one I could collect from Claude Desktop, Claude Code, VS Code and Cursor.

  What came back:

  1️⃣ 1,822 of 1,920 servers installed from npm, PyPI or a container registry have no pinned version. Every start runs whatever was published last, with the agent's tokens. The rate is 91–96% across all four clients.

  2️⃣ The archived reference servers are still running. 55 configs use the old GitHub server, which gets no more security fixes. That's more than twice as many as use the image of GitHub's maintained server.

  3️⃣ About 1 config in 26 holds a real-looking secret in plain text. Most "credentials" were placeholders like YOUR_API_KEY; my own tool flagged those too, until I fixed it.

  4️⃣ 166 configs give one agent a full exfiltration path: sensitive data, content outsiders can write, and a way to send data out, with no human approval.

  5️⃣ Known CVEs were rare, but only because almost nothing is pinned. Unpinned servers pick up fixes automatically, and would pick up a malicious release just as fast.

  The control isn't "pin" or "don't pin". It's pin, then review updates on a schedule, the way we already treat application dependencies.

  Method, scripts and totals are public. No repository names or secrets are published.

  #AISecurity #MCP #SupplyChainSecurity #GRC #AgenticAI
tools: [agent-access-review]
image: /assets/img/posts/i-reviewed-2830-public-mcp-configs.png
---

An MCP config is an access grant. It says which servers an AI agent starts, what each one can reach, and which credentials it holds. In most companies nobody reviews it, because it lives in a developer's editor rather than in an identity system. That makes it hard to know what normal looks like.

Public repos are the exception. Developers commit these files, sometimes on purpose as templates and sometimes by accident, and GitHub's code search can find them. So I collected as many as I could for four clients (Claude Desktop, Claude Code, VS Code and Cursor), removed duplicates, and ran [agent-access-review](https://github.com/Mihirajmera/agent-access-review) on each of the 2,830 that define at least one server. The full method, scripts and totals are in the [case study](/case-studies/public-mcp-configs/).

{% include figures.html items=page.figures %}

## Almost nothing is pinned

Of the 1,920 servers installed from npm, PyPI or a container registry, 1,822 (95%) have no pinned version. A config line like `npx -y @playwright/mcp` installs whatever was published most recently, every time the agent starts. If a maintainer's account is taken over and a bad release goes out, every one of those agents runs it with its own tokens the next time it starts, and no config changes.

The rate is the same everywhere: 96% for Claude Desktop and VS Code, 95% for Cursor, 91% for Claude Code. This is not one tool's bad default. It's what the ecosystem's READMEs teach, as I found when I [reviewed the official README examples](/blog/what-mcp-readmes-teach-you-to-copy/).

Known vulnerabilities were rare: one config pinned `mcp-remote` 0.1.15, a release with a critical command-injection CVE. That isn't good news. It's the same fact seen from the other side. Unpinned servers pick up fixes automatically, and they'd pick up a malicious release just as automatically. Pinning without anyone updating isn't a control either. The control is the one we already use for application dependencies: pin, then review and apply updates on a schedule.

## The archived servers are still running

Most of the original MCP reference servers were archived in 2025, and their npm packages are now marked deprecated. They no longer get security fixes. 79 configs still run one. The old GitHub server appears in 55 configs, more than twice as often as the container image of GitHub's maintained server (21). Postgres, Puppeteer, Brave Search and Slack follow.

That's what happens when access is copied rather than designed: the README a developer copied from in early 2025 is still the configuration in late 2026.

## About one config in 26 holds a real secret

At first, agent-access-review reported that a quarter of Claude Desktop configs had a hardcoded credential. Most of those were template placeholders such as `YOUR_API_KEY` or `<token>`, which aren't leaks. I changed the tool to recognise obvious placeholders while still reporting anything that isn't clearly fake. Across all 2,830 configs, 109 (3.8%) hold a value that looks like a real secret, and 12 match a known provider format, mostly OpenAI or Anthropic keys.

I didn't test any of them. Those providers take part in GitHub's secret scanning, which is the right route for getting them revoked. Cursor configs were the most likely to hardcode a credential: 14%, against 5–9% for the other clients.

## One agent, a full exfiltration path

166 configs (5.9%) give one agent all three parts of an exfiltration path: it reads sensitive data, it takes in content outsiders can write (web pages, issues, email), and it can send data out, with no human approval on any of those steps. One prompt injection in the untrusted content can tell the agent to send the data out. No single server creates that risk. The combination does, which is why it only shows up when you review the whole config rather than one server at a time.

## What to check in your own

**1. List every MCP config on your developers' machines and in your repos.** `claude_desktop_config.json`, `.mcp.json`, `.vscode/mcp.json` and `.cursor/mcp.json`. The repo copies are the easy part: search your organisation's code for those file names.

**2. Pin, and own the updates.** Give every `npx`, `uvx` and `docker` server an exact version or image digest, and put those versions under the same update process as your other dependencies, with someone reviewing each bump.

**3. Replace archived servers.** If a config runs `@modelcontextprotocol/server-github`, `-postgres`, `-slack`, `-puppeteer` or `-brave-search`, move to the maintained server or remove it.

**4. Move secrets out of the files.** Use environment references or a secret manager, and treat any key that was ever committed as exposed: rotate it.

**5. Review the combination, not the server.** For each agent, ask whether it can read sensitive data, read outsider content and send data out. If it can do all three, put a human approval on at least one of them.

agent-access-review does all five checks in one run. `pip install agent-access-review`, then point `agent-access-review scan` at a config file or a folder. It runs locally and produces a review packet a reviewer can sign off.
