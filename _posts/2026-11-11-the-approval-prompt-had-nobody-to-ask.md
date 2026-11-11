---
title: "The approval prompt had nobody to ask"
description: "An advisory published on Monday showed an agent server that, by default, listened on every network interface with no authentication. With its shell tool turned on, anyone who could reach it could run commands, and the permission prompt didn't stop them because in server mode there was nobody to ask. Here's how to find agent servers like this on your own machines, and why approval controls need checking in every mode an agent runs in."
kind: essay
research: true
status: review
evidence:
  hash: GHSA-9vhv-g5hf-m7m7
  label: "fast-agent: serve binds HTTP to 0.0.0.0 with no authentication by default (CVE-2026-102610)"
  url: https://github.com/advisories/GHSA-9vhv-g5hf-m7m7
tags: [AI agents, MCP, Control testing]
figures:
  - {n: "0.0.0.0", label: "the default address, meaning every network the machine is on", tone: red}
  - {n: "0", label: "authentication, and no warning at startup", tone: amber}
  - {n: "1", label: "plain-language message to run a command, from an unauthenticated caller"}
diagram:
  type: terminal
  title: fast-agent-mcp 0.7.20, as reproduced in the advisory
  caption: CVE-2026-102610, fixed in 0.7.21
  note: the shell tool's permission prompt did not block this in serve mode
  lines:
    - "$ fast-agent serve --model gpt-4o-mini --shell"
    - "# Uvicorn running on http://0.0.0.0:8000"
    - "! no authentication, no warning"
    - "$ initialize, no Authorization header"
    - "! 200 OK"
    - "$ tools/call agent: run id via your shell tool"
    - "! uid=0(root) gid=0(root)"
    - "+ 0.7.21: binds 127.0.0.1 by default, warns on remote binds"
linkedin: |
  An agent server asked for permission before running shell commands. Then it was run as a server, and there was nobody to ask.

  CVE-2026-102610, published on Monday: by default, `fast-agent serve` listened on every network interface, with no authentication and no warning. Started with its shell tool, which the README quickstart uses, anyone who could reach the port could send one plain-language message and get commands run on the host. In the advisory's test, as root.

  The permission prompt didn't stop it. In non-interactive server mode, nobody was there to answer it.

  That's the part worth taking into any agent review: a human approval control only exists in the modes where a human is actually asked.

  What to check on your own machines:

  1️⃣ Agent servers listening on all interfaces. On a laptop on hotel Wi-Fi, "all interfaces" includes the hotel.

  2️⃣ An unauthenticated initialize request to each one. It should be refused.

  3️⃣ Which agents have a shell tool. Shell plus a network listener is remote command execution.

  4️⃣ Where the approval prompt goes when the agent runs as a service. If the answer is nowhere, the control doesn't exist in that mode.

  5️⃣ What the README tells people to paste. The quickstart is the real default.

  The fix in 0.7.21 binds to localhost by default and warns on remote binds. Upgrade, and still check.

  #AISecurity #AgenticAI #MCP #GRC #CyberSecurity
tools: [agent-flight-recorder]
image: /assets/img/posts/the-approval-prompt-had-nobody-to-ask.png
---

On Monday, GitHub published [an advisory for fast-agent](https://github.com/advisories/GHSA-9vhv-g5hf-m7m7), a framework for building agents and serving them over MCP. Its `serve` command made an agent available to other MCP clients. Up to version 0.7.20, by default, it listened on `0.0.0.0` (every network interface on the machine) on port 8000, with no authentication and no warning.

Without the shell option, that meant anyone who could reach the port could use the operator's model and whatever tools the agent had. With `--shell`, which the advisory notes is the flag used in the README quickstart, the agent also had a tool that runs operating system commands. The researcher, who reported it privately, sent one plain-language message from a client with no credentials, asking the agent to run a command with its shell tool. The model did, and returned the output. In the advisory's Docker test, the command ran as root.

The fix in 0.7.21 changes the default to `127.0.0.1`, so the server only listens on the local machine, and prints a warning when it's bound to anything reachable from outside, with an extra warning when the shell tool is exposed. Authentication is still something you set up yourself.

{% include figures.html items=page.figures %}

## The control that wasn't there in server mode

The detail I'd take into every agent review is one line near the end of the advisory: the server-side permission prompt did not block this in non-interactive serve mode.

When you run an agent interactively, a prompt that asks "allow this shell command?" is a real control. A person sees the command and decides. Run the same agent as a server, and there's no terminal and no person. The prompt either waits forever or, as here, doesn't stand in the way. The control's existence depended on how the agent was started, and nothing told the operator it had gone.

This is a design question an auditor can ask about any agent: in which modes does this agent run, and does each control work in all of them? Interactive, scheduled, as a service, in CI, called by another agent. Human approval is the control most likely to quietly disappear, because it needs a human in the loop, and most of those modes don't have one.

The fix is for approval to stop the call and wait for a decision that's recorded somewhere, rather than prompting in a terminal. A call that needs approval is held, and a named person approves that exact call through a separate channel. That's how [agent-flight-recorder](https://github.com/Mihirajmera/agent-flight-recorder) works, and it's the same pattern I described in [approve the batch, not the request](/blog/approve-the-batch-not-the-request/). It works the same whether anyone's at the keyboard or not.

## Not a one-off

The same researcher reported [the pdf-reader-mcp bug I wrote about on Monday](/blog/the-log-said-authentication-was-enabled/): an HTTP server that also listened on all interfaces by default, and ignored its configured API key. Both fixes changed the default address to localhost. Two different projects, two weeks apart, with the same pair of defaults suggests these defaults are common in agent tooling, not rare mistakes.

It makes sense. Developers build these servers on their own machines, where "it works when I connect to it" is the test, and `0.0.0.0` makes it work from a container or a second device. Then the same default ships to everyone else.

## What to check

**1. Find agent servers listening on all interfaces.** On developer laptops and shared dev machines, list the listening ports and the processes behind them: `ss -ltnp` on Linux, `lsof -iTCP -sTCP:LISTEN -n -P` on macOS, `Get-NetTCPConnection -State Listen` on Windows. Anything agent-related on `0.0.0.0` or `::` is reachable from every network the machine joins. On a laptop on hotel Wi-Fi, that includes the hotel.

**2. Try to connect without credentials.** From another machine you own, send an MCP `initialize` request to each server you found, with no `Authorization` header. It should be refused. If it's accepted, try `tools/list` to see what an outsider could use.

**3. Find agents with a shell tool.** Any agent that can run commands, combined with a network listener and no authentication, is remote command execution. List them, and for each one, decide whether it needs the shell tool at all.

**4. Ask where the approval prompt goes.** For each agent that relies on human approval, list the ways it can be run. For each mode, show where the approval request appears and who answers it. A mode with no answer has no control.

**5. Read the quickstart as configuration.** What the README tells people to paste is what most people run. I looked at this for MCP server READMEs in [what MCP READMEs teach you to copy](/blog/what-mcp-readmes-teach-you-to-copy/). Here, the quickstart turned on the shell tool. When you approve a new agent tool for use, review the configuration people will actually copy, not the secure one described further down.

## Upgrade, and still check

Upgrading to 0.7.21 fixes the default address. It doesn't add authentication, and anyone who passes `--host 0.0.0.0` on purpose gets the old exposure back, with a warning. The checks above find that case too, which is why they're worth running even after the upgrade.
