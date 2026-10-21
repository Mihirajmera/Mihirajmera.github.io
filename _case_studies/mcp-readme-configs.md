---
title: What the official MCP READMEs teach you to copy
description: A user access review of the configuration examples in 9 widely used MCP server READMEs. No single one is dangerous; pasted together, they build an exfiltration path.
date: 2026-10-19
question: If a developer sets up an AI agent by copying official README examples, what access does it end up with?
method: Took the first valid config example from 9 MCP server READMEs, pinned to exact commits, and ran agent-access-review on each one and on all nine combined.
tools: [agent-access-review]
frameworks: [NIST 800-53, SOC 2, NIST AI RMF, OWASP LLM Top 10]
evidence:
  - {label: configs pinned to source commits, url: "https://github.com/Mihirajmera/agent-access-review/tree/main/case-studies/official-mcp-readmes"}
  - {label: combined review packet, url: "https://github.com/Mihirajmera/agent-access-review/blob/main/case-studies/official-mcp-readmes/results/combined/access-review.md"}
numbers:
  - {n: "8/9", label: configs run an unpinned package or image, tone: red}
  - {n: "7/9", label: grant write, send, delete or execute, tone: amber}
  - {n: "1", label: exfiltration path once combined, tone: red}
---

## Why this matters

Companies recertify employee access every quarter. AI agents now hold GitHub tokens, database connections, shells and Slack bots, and almost nobody reviews them. Most of that access isn't designed; it's copied from a README.

## What I found

**8 of 9 run an unpinned package or image.** Whatever was published most recently runs with the agent's access on every start, so a compromised release would inherit it without any config change.

**7 of 9 grant write, send, delete or execute.** That's the purpose of most of these servers; the finding is about governance: who approved it, and is there a human check before the agent acts?

**The Slack example teaches pasting a bot token into a JSON file**, and Desktop Commander gives the agent an unsandboxed shell.

**Combined, they form an exfiltration path.** One agent that reads sensitive data, ingests content outsiders can write, and can send data out, with no human approval. No single README creates that risk; the combination does. It's segregation of duties, applied to AI agents.

## What my own tool got wrong

Scanning real configs found two gaps in agent-access-review: 5 of 9 configs were unclassified because the official examples now use Docker images and `uvx`, and Docker volume mounts (what the agent can really reach) were invisible. Both are fixed, and a community contributor has since added support for commented VS Code configs.

## Try it

Paste your own MCP config into the [in-browser playground](/work/#try). It runs the same review locally, and nothing is uploaded.
