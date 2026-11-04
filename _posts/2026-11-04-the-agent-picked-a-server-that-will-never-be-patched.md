---
title: "The agent picked a server that will never be patched"
description: Coding agents are installing MCP servers that were archived in May 2025 and will never get a security fix. Their flaws have no CVEs, so dependency scanners report them clean. I checked npm this morning. Here's what's still being downloaded, and five controls that catch it.
kind: essay
research: true
status: review
evidence:
  hash: npm registry 2026-11-04
  label: Help Net Security on Glow Labs' MCPhantom research
  url: https://www.helpnetsecurity.com/2026/11/03/mcphantom-deprecated-mcp-servers/
tags: [AI agents, Supply chain, MCP]
figures:
  - {n: "11", label: "reference MCP servers deprecated on npm and archived on GitHub", tone: amber}
  - {n: "614,185", label: "npm downloads of those 11 packages in the last week", tone: red}
  - {n: "0", label: "CVEs for the flaws, so a dependency scan reports them clean", tone: red}
diagram:
  type: terminal
  title: npm registry, 2026-11-04
  caption: deprecated reference servers, weekly downloads
  note: "archived May 2025 · no security fixes"
  lines:
    - "$ npm view @modelcontextprotocol/<pkg> deprecated"
    - "! server-github        deprecated   189,189 / week"
    - "! server-slack         deprecated   185,396 / week"
    - "! server-postgres      deprecated   155,598 / week"
    - "! server-brave-search  deprecated    30,371 / week"
    - "! server-puppeteer     deprecated    29,827 / week"
    - "# + 6 more, from gdrive to everart"
    - "+ server-filesystem    maintained  1,294,151 / week"
linkedin: |
  Ask a coding agent to "set up the GitHub MCP server" and there's a good chance it installs one that will never get another security fix.

  Glow Labs reviewed real agent sessions (Claude Code, Cursor, Codex CLI) and found agents choosing the original reference MCP servers, archived in May 2025, straight from training data. One of them, the Puppeteer server, has a remote code execution flaw reachable through prompt injection. Maintainers closed the report: the server is archived, so no fix.

  I checked npm this morning. The 11 deprecated reference servers were downloaded 614,185 times last week.

  The part that matters for security teams: these flaws have no CVEs. Your dependency scanner reports them clean.

  What catches it:

  1️⃣ Add "still maintained" to your approval criteria, next to "no known CVEs".

  2️⃣ Approve one server per service, from the service owner where one exists.

  3️⃣ Search the MCP configs you already have. The package names are a fixed list.

  4️⃣ Block deprecated packages before the agent runs them, with a pre-execution hook.

  5️⃣ Treat the agent's choice of package as an unreviewed change. You approved "set up GitHub", not that package.

  Full post has the list of packages and a config check you can run.

  #AISecurity #SupplyChainSecurity #MCP #GRC #AppSec
image: /assets/img/posts/the-agent-picked-a-server-that-will-never-be-patched.png
tools: [agent-access-review]
---

Yesterday Help Net Security [reported on research from Glow Labs](https://www.helpnetsecurity.com/2026/11/03/mcphantom-deprecated-mcp-servers/) that it calls MCPhantom. Glow reviewed real AI coding sessions in Claude Code, Cursor, Codex CLI and other tools, with models from Anthropic, OpenAI and xAI. When a developer asked the agent to set up an MCP server for a service like GitHub, the agent often installed the original reference server from the `@modelcontextprotocol` npm scope.

Those reference servers were archived in May 2025. The repository they moved to, [`modelcontextprotocol/servers-archived`](https://github.com/modelcontextprotocol/servers-archived), describes itself as servers "that are no longer maintained." In the sessions Glow reviewed where a deprecated server came up, 98% of the time the user hadn't asked for it by name. The agent filled in the package from what it remembered.

Glow found four high-severity flaws in these servers. The worst is in the Puppeteer server, which lets an agent drive a browser: a prompt injection can make it start any process. Glow's report was closed as out of scope, because the server is archived and won't be fixed. Glow's VP of R&D put it well: "The model's memory is now a package manager with no deprecation feed."

None of the four flaws has a CVE. No exploitation has been reported yet.

{% include figures.html items=page.figures %}

## What I found on npm this morning

I didn't want to rely on one write-up, so I checked the npm registry for each of the original reference servers. Eleven are marked deprecated with the message "Package no longer supported." Between them, they were downloaded 614,185 times in the last week:

| Package (`@modelcontextprotocol/…`) | npm status | Downloads, last week |
|---|---|---:|
| `server-github` | deprecated | 189,189 |
| `server-slack` | deprecated | 185,396 |
| `server-postgres` | deprecated | 155,598 |
| `server-brave-search` | deprecated | 30,371 |
| `server-puppeteer` | deprecated | 29,827 |
| `server-google-maps` | deprecated | 7,846 |
| `server-gdrive` | deprecated | 6,271 |
| `server-gitlab` | deprecated | 5,453 |
| `server-redis` | deprecated | 3,892 |
| `server-aws-kb-retrieval` | deprecated | 197 |
| `server-everart` | deprecated | 145 |

Not all of those downloads are agents choosing badly. Some are CI jobs, mirrors, and people who installed it a year ago and never changed their config. But that's the point: each one is a server that has had no security fixes for about 18 months, and a deprecation warning doesn't stop `npx` from installing and running it.

For comparison, the reference servers that are still maintained, like `server-filesystem` (1,294,151 downloads last week) and `server-memory`, are fine to keep. This isn't a reason to distrust the whole scope. It's a reason to check status per package.

## Why the usual controls miss it

Most third-party software controls ask two questions: is it on the approved list, and does it have known vulnerabilities? An archived MCP server can pass both.

- **It looks official.** The package comes from the `@modelcontextprotocol` scope, which is the protocol's own organisation. If your allowlist is scoped by publisher, it's on it.
- **It has no CVEs.** Software composition analysis matches packages against vulnerability databases. A flaw that's never assigned a CVE never matches, so the scan report is clean. "No known vulnerabilities" and "still gets fixed" are different claims, and most approval criteria only check the first.
- **Nobody chose it.** The human approved "set up GitHub". The agent picked the package. In a normal change process, the specific dependency is part of what gets reviewed. Here it never reached a reviewer.

## Five controls that catch it

### 1. Make "still maintained" an approval criterion

Next to "no known critical CVEs", add: not deprecated in its registry, repository not archived, and a release in the last 12 months (or a stated reason why not). These are all checkable from public metadata.

**Test:** take your approved MCP server list and check each one's registry status today. For npm, `npm view <package> deprecated` prints the deprecation message, or nothing if the package is supported.

### 2. Approve one server per service

Decide in advance which integration is allowed for each service, rather than letting each developer, or each agent, pick. Where the service owner ships its own MCP server (GitHub does, for example), prefer that over a third-party or archived one, and write down the decision.

**Test:** for each service your agents connect to, is there exactly one approved server, with a named owner and a recorded reason?

### 3. Search the configs you already have

This is the quickest win, because the list of deprecated package names is fixed. MCP servers are configured in files like `claude_desktop_config.json`, `.cursor/mcp.json` and `.vscode/mcp.json`. A search for the eleven names across developer machines and repositories finds them:

```bash
grep -rlE '@modelcontextprotocol/server-(github|slack|postgres|brave-search|puppeteer|google-maps|gdrive|gitlab|redis|aws-kb-retrieval|everart)\b' \
  --include='*mcp*.json' --include='claude_desktop_config.json' ~ 2>/dev/null
```

**Test:** run it (or your endpoint tool's equivalent) and count the hits. If the answer is "we can't search developer machines for config files", that's the finding.

### 4. Block it before it runs

Glow's recommendation for security teams is to use the pre-execution hooks that many agent harnesses already support. Claude Code, for example, can run a hook before each tool call and block it. A hook that refuses any command or config edit naming a server on your deprecated list turns a policy into something enforced at the moment it matters, instead of at the next quarterly review.

**Test:** try to install a deprecated server through the agent on a managed machine. Does anything stop it, or record it?

### 5. Treat the agent's dependency choice as a change

When a person adds a dependency, it goes through code review. When an agent adds an MCP server to a config file, the same change often lands without anyone looking at which package it chose. The fix is the same as for any other unreviewed change: the config file is in version control, and a change to it needs a second pair of eyes.

**Test:** pick a recent change that added an MCP server. Who reviewed the package choice?

## What my own tool doesn't catch yet

I build [agent-access-review](https://github.com/Mihirajmera/agent-access-review), which reads MCP configs and runs an access review on each agent. It already flags unpinned packages, and most of these configs would fail that. But it doesn't yet say "this server is deprecated and will never be fixed", which is a more useful finding. I've opened [an issue](https://github.com/Mihirajmera/agent-access-review/issues/29) to add deprecation and replacement data to its catalog. If you'd like to help, that's a good place to start.

The broader lesson is the one behind most of these posts: an agent making a choice doesn't remove the need for a control. It removes the person who would have noticed.
