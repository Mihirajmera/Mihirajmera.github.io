---
title: What the official MCP READMEs teach you to copy
description: I scanned the configuration examples from 9 widely used MCP server READMEs. No single one is dangerous. Pasted together, they build an exfiltration path.
kind: essay
research: true
status: review
evidence:
  hash: 96f44ee
  label: commit 96f44ee · 9 configs, pinned sources
  url: https://github.com/Mihirajmera/agent-access-review/tree/main/case-studies/official-mcp-readmes
tags: [AI agents, MCP, Access reviews]
linkedin: |
  Most AI agent access isn't designed. It's copied from a README.

  So I took the configuration examples from 9 widely used MCP server READMEs (the official reference servers, GitHub's and a popular community one) and ran a user access review on them, the same way we review employee access every quarter.

  🔴 8 of 9 run an unpinned package or image. Whatever was published most recently runs with your agent's access, every time it starts.
  🟠 7 of 9 grant write, send, delete or execute.
  🔴 The Slack example teaches you to paste the bot token into a JSON file.

  None of that is surprising for documentation written to be easy to copy. The interesting part came next.

  I pasted all nine into one config, the way a real setup grows. The scan flagged an exfiltration path: one agent that reads sensitive data, ingests content outsiders can write, and can send data out, with no human approval in between.

  No single README creates that risk. The combination does. It's segregation of duties, applied to AI agents: each permission is reasonable on its own, and the risk lives in the combination.

  Scanning real configs also found two gaps in my own tool (Docker images and volume mounts were invisible), both fixed now.

  Full write-up, sources pinned to exact commits, and the open-source scanner in the first comment 👇

  #AIGovernance #AISecurity #MCP #GRC #AIAgents #CyberSecurity
figures:
  - {n: "8/9", label: "configs run an unpinned package or image", tone: red}
  - {n: "7/9", label: "grant write, send, delete or execute", tone: amber}
  - {n: "1", label: "exfiltration path once they're combined", tone: red}
image: /assets/img/posts/what-mcp-readmes-teach-you-to-copy.png
---

Most companies recertify employee access every quarter. Someone opens a spreadsheet, looks at who can reach what, and signs off. AI agents now hold GitHub tokens, database connections, shells and Slack bots, and almost nobody reviews them at all.

Most of that access isn't designed. It's copied. A developer wants Claude or Cursor to read their files, so they open the server's README, copy the configuration example and paste it in. So I asked a simple question: **if you set up an agent by copying the official examples, what access does it end up with?**

{% include figures.html items=page.figures %}

## Method

I took the first valid configuration example from 9 widely used MCP server READMEs: the official reference servers, GitHub's MCP server and a popular community server. I saved each exactly as published, with a link to the exact commit and line, and scanned them with [agent-access-review](https://github.com/Mihirajmera/agent-access-review), my open-source tool that runs a user access review on AI agents.

These are documentation examples, written to be easy to copy, not production setups. The point isn't that the READMEs are wrong. It's that copying them without a review produces the access below, and nothing in a typical workflow flags it.

## One config at a time

| Server | What the agent can do | Main findings |
|---|---|---|
| Desktop Commander | read, write, delete, **execute** | Unsandboxed shell, unpinned |
| filesystem | read, write, delete | Write access, unpinned |
| git | read, write | Write access, unpinned |
| memory | read, write | Write access, unpinned |
| puppeteer | read, send | Can send data out, unpinned |
| slack | read, send | **Token pasted into the config**, unpinned |
| fetch | read | Unpinned |
| postgres | read | Unpinned |
| github (remote) | read, write | Write access |

**Unpinned packages are the quiet one.** `npx -y <package>`, `@latest`, `uvx <package>` and an untagged `docker run` all fetch whatever was published most recently, every time the client starts. If a release is ever compromised, it runs with your agent's access, and your config never changed. In a normal software supply chain, that would fail a review on day one.

**The Slack example teaches a secrets anti-pattern.** Its `env` block sets the bot token to a placeholder you replace with the real token. Follow it, and your Slack token sits in plain text in a JSON file, in every backup and in any dotfiles repository you sync.

**Write, send and execute are the point of most of these servers.** That's fine. The finding is about governance: who approved giving an agent that power, and is there a human check before it acts?

## Then I pasted them together

Developers rarely run one server. I combined all nine examples into a single config, the way a real setup grows over a few weeks of "let me just add this one". The scanner raised its highest-severity finding:

{% include pull.html text="The agent reads sensitive data, ingests content outsiders can write, and can send data out, with no human approval. That's an exfiltration path." %}

A prompt injection hidden in a web page, a GitHub issue or a Slack message could make the agent read your files or database and send them somewhere. No single README creates this risk. The combination does, and that's exactly what per-server documentation and per-tool reviews miss.

It's the same lesson as segregation of duties in financial controls. Each permission is reasonable on its own. The risk is in the combination, so that's where the review has to look.

## What my own tool got wrong

Running a real scan found two gaps in agent-access-review, both now fixed:

1. **5 of the 9 configs were initially unclassified.** The tool only recognised npm package names, but the official READMEs now mostly recommend Docker images and `uvx`. The capability catalog now supports aliases, and all 9 are assessed.
2. **Docker mounts were invisible.** For containerised servers, what the agent can reach is set by `-v` and `--mount` flags, not by the server's arguments. The scanner now reads host bind mounts as the grant's scope, so mounting your home directory gets flagged, and read-only mounts are treated as read-only.

Testing your own tool against real-world input is the cheapest audit you'll ever run.

## What to do about it

1. **Pin every server.** Use a version for npm and `uvx`, and a digest for Docker images. Treat MCP servers like any other dependency.
2. **Keep secrets out of config files.** Reference an environment variable or a secret manager, never a literal token.
3. **Review the combination, not the server.** Ask the exfiltration question for the whole agent: can it read something sensitive, ingest untrusted content and send data out?
4. **Give agents owners and approval dates.** If nobody owns an agent's access, nobody will ever take it away.

## Caveats

Some MCP clients ask before each tool call. That setting isn't visible in config files, so the scan reports what the configuration allows. The postgres, puppeteer and slack servers have been archived, but their READMEs are still widely linked and copied. The framework mappings are my own judgment.

## Reproduce it

Every config links to the exact commit it came from, and the full results are in the [case study](https://github.com/Mihirajmera/agent-access-review/tree/main/case-studies/official-mcp-readmes).

```bash
pip install agent-access-review
agent-access-review scan path/to/your/mcp-configs
```

Run it on your own setup. I'd be surprised if it comes back clean.
