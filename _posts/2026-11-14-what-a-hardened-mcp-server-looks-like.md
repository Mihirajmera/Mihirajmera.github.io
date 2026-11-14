---
title: "I went bug hunting in four popular MCP packages. I found their defences instead."
description: "I reviewed four widely installed MCP packages for the bugs that usually turn up in local servers: missing origin checks, DNS rebinding, path traversal and weak tokens. All four were already defended. Here's what those defences look like, as a checklist for anyone building an MCP server or approving one for their agents."
kind: note
research: true
status: review
tags: [MCP, AI agents, Secure development, Access review]
figures:
  - {n: "4", label: "popular MCP packages reviewed for local-server bug classes"}
  - {n: "0", label: "exploitable bugs found", tone: green}
  - {n: "1", label: "risky default, documented and warned about at startup", tone: amber}
diagram:
  type: terminal
  title: what the four packages already did
  caption: source review, 2026-11-12
  note: no vulnerabilities found; nothing to disclose
  lines:
    - "# manual review: origin, rebinding, paths, auth"
    - "+ postMessage: sender + origin checked"
    - "+ local HTTP: Host + Origin checked"
    - "+ API token: random, constant-time compare"
    - "+ file paths: resolved, then confined"
    - "+ HTTP mode: no auth only on loopback"
    - "! relay: any website by default (warns)"
linkedin: |
  On Thursday I went looking for security bugs in four popular MCP packages. I didn't find any. I found their defences instead, and they make a better checklist than most guidance I've read.

  The bugs I was hunting are the ones that keep turning up in local MCP servers: a website talking to a server on your laptop, a request walking out of its folder, a token that's easy to guess. Each package had already closed them:

  1️⃣ Browser messages: every postMessage listener checks both who sent the message and its origin, and the allowed origins are required, not optional.

  2️⃣ Local HTTP servers: the Host and Origin headers are checked, so a malicious page can't reach the server through DNS rebinding.

  3️⃣ Tokens: random per run, at least 16 characters, compared in constant time.

  4️⃣ Files: paths are normalised and then checked to stay inside their folder, and IDs that end up in file names are restricted to a strict pattern.

  5️⃣ HTTP mode: the server refuses to start without authentication unless it's bound to localhost.

  One package does accept connections from any website by default. It's documented in the README and it prints a warning at startup, which is the right way to handle a convenient-but-risky default. It's also exactly the setting an access review should check before an agent runs it.

  If you build MCP servers, steal this list. If you approve them for your agents, ask for it.

  #AISecurity #MCP #AppSec #AgenticAI
tools: [agent-access-review]
image: /assets/img/posts/what-a-hardened-mcp-server-looks-like.png
---

On Thursday I set out to find my next MCP vulnerability. The plan was simple: take some of the most-installed MCP packages on npm, read the parts of each one that face the outside world, and look for the bug classes that keep turning up in local servers.

This time I found nothing to report. What I found instead was four codebases that had already closed every door I tried, in ways worth copying.

{% include figures.html items=page.figures %}

The four packages were [`@mcp-b/transports`](https://github.com/WebMCP-org/npm-packages) and its local relay, [`@next-ai-drawio/mcp-server`](https://github.com/DayuanJiang/next-ai-draw-io) and [`@serdnaley/metabase-mcp`](https://github.com/Serdnaley/metabase-mcp). I reviewed their source as of November 12, 2026, looking only at the outward-facing parts: message handlers, local HTTP and WebSocket servers, authentication, and anything that turns input into a file path.

## 1. Browser messages: check the sender and the origin, every time

`@mcp-b/transports` moves MCP messages between browser tabs, iframes and extensions using `postMessage`. Any page can send a `postMessage` to any window it can reference, so a listener that doesn't check where a message came from will act on messages from any site.

Every listener in the package checks two things before reading a message: that it came from the expected window (`event.source`), and that the sending page's origin is on an allow list (`event.origin`). The allow list is a required argument. Leave it empty and the constructor throws. Allowing every origin is possible, but you have to write `['*']` on purpose. And when the iframe transport replies, it sends to the origin it actually heard from, never to `*`.

**What to check:** every `message` listener tests both `event.source` and `event.origin`, and the allowed origins have no permissive default.

## 2. Local HTTP servers: check Host and Origin, not just the bind address

Binding a server to `127.0.0.1` stops other machines from reaching it. It doesn't stop a web page in your own browser. Through DNS rebinding, a malicious site can make your browser send requests to `localhost` that look like ordinary same-site requests to the page.

The draw.io MCP server binds to `127.0.0.1` and also checks every request's `Host` header against `localhost` or `127.0.0.1`, with an `Origin` that must match the server's own address or be absent. A rebound request carries the attacker's hostname in `Host`, so it's refused before any route runs. Its API also requires a token generated fresh on each start (`randomBytes(16)`), which a page on another origin never sees.

**What to check:** a local server validates `Host` and `Origin` on every request, and its API needs a secret that only its own page receives.

## 3. Tokens: random, long enough, compared in constant time

`metabase-mcp` can run over HTTP. In that mode it refuses to start without a bearer token, rejects tokens shorter than 16 characters, and compares the presented token by hashing both sides and using `timingSafeEqual`, so response time doesn't leak how much of a guess was right. Running without a token is allowed only when you set an explicit opt-out and bind to a loopback address, and then it turns on the MCP SDK's DNS rebinding protection.

**What to check:** HTTP mode fails closed without authentication, and "no auth" is only possible on loopback, behind an explicit flag.

## 4. File paths: normalise, then prove the result is still inside

Path traversal is the oldest bug on this list and still one of the most common in MCP servers, because so many of them serve or save files. The draw.io server does it in the right order. It decodes the path, normalises it, resolves it against its folder, and only then checks that the result still starts with that folder. It also rejects backslashes and null bytes outright. Session IDs that become part of saved file names must match `^mcp-[a-z0-9-]{1,64}$` before they're used anywhere.

The common mistake in this area is a check done on the path text alone, which a symlink inside the folder can get around. Here the checks guard the server's own fixed folders, not a folder the user chooses, which is why the simple version is enough. A server that scopes itself to a user's folder needs to resolve symlinks before it checks.

**What to check:** paths are resolved first and checked second, and any identifier that becomes part of a path is restricted to a strict pattern.

## 5. Risky defaults: if you keep one, say so loudly

The one thing I'd flag is in the WebMCP local relay. By default it accepts browser connections from any website, which means any page you visit could offer tools to your local agent. For a developer tool that's a deliberate convenience trade-off, and the project handles it well. The README says so in its security section, the relay prints a `WARNING` on startup, and `--widget-origin` restricts it to the sites you trust. It also stops browser pages from using its internal relay-to-relay protocol at all.

That's the right way to ship a risky default. It's also exactly the kind of setting an access review should catch, because a config line that runs the relay without `--widget-origin` looks identical to one that's locked down.

**What to check:** look for risky defaults in the README's security section and the startup output, and make sure the config that runs the server sets the safe option.

## Why a null result is worth writing up

Most security writing is about what went wrong. But the people who approve MCP servers for their organisation's agents need the other half too: what "done properly" looks like, so they can ask for it. This list is short enough to put in an intake checklist:

1. Messages from browsers are checked for sender and origin.
2. Local servers check `Host` and `Origin`, not just the bind address.
3. Any HTTP mode requires a strong token, compared in constant time.
4. File paths are resolved, then checked against their folder.
5. Risky defaults are documented, warned about, and turned off in your config.

And credit to the maintainers. These defences don't happen by accident, and several of them have comments in the code naming exactly the attack they block.
