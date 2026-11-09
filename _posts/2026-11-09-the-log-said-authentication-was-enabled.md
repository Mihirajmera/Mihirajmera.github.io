---
title: "The log said authentication was enabled"
description: "Four security advisories for AI agent tooling in the last two weeks share one pattern: the control was configured, and it didn't work. An API key that was never checked, a token check that's off by default, an SSRF filter that let localhost through, and a redaction that missed a second path. A screenshot of the setting wouldn't have caught any of them. A negative test would."
kind: essay
research: true
status: review
evidence:
  hash: GHSA-q344-5v34-gm84
  label: "@sylphx/pdf-reader-mcp: HTTP transport accepts unauthenticated requests despite a configured MCP_API_KEY"
  url: https://github.com/advisories/GHSA-q344-5v34-gm84
tags: [AI agents, MCP, Control testing]
figures:
  - {n: "4", label: "advisories in two weeks where a configured control didn't work", tone: red}
  - {n: "0", label: "of them visible in a screenshot of the configuration", tone: amber}
  - {n: "1", label: "request each, sent the wrong way, would have caught them"}
diagram:
  type: terminal
  title: negative tests
  caption: what the affected versions did with a request that should fail
  note: "advisories published 27–29 October 2026"
  lines:
    - "# pdf-reader-mcp < 3.0.1, MCP_API_KEY set, request with no key"
    - "! accepted          expected 401"
    - "# mcp Python SDK < 1.30.0, token issued for another service"
    - "! accepted          expected 401"
    - "# mcp-sanitizer < 1.4.0, fetch http://[::1]:8080/"
    - "! allowed           expected blocked"
    - "# mlflow < 3.17.0 crewai autolog, search spans for the API key"
    - "! 5 attributes      expected 0"
linkedin: |
  "API key authentication enabled."

  That's what an MCP server printed at startup when you set its API key. It then accepted every request without checking the key, on all network interfaces. (CVE-2026-62264, fixed in pdf-reader-mcp 3.0.1.)

  It wasn't the only one. Four advisories for AI agent tooling in the last two weeks share the same pattern: the control was configured, and it didn't work.

  1️⃣ An API key that was read at startup and never checked.

  2️⃣ An MCP SDK token check that existed, but was off unless you turned it on. Upgrading alone changed nothing.

  3️⃣ An SSRF filter that blocked localhost, unless the URL had a port number.

  4️⃣ A redaction that hid the API key in one trace span and leaked it through another.

  A screenshot of the setting wouldn't have caught any of these. Auditors call that evidence of design. What catches them is evidence that the control operates: send the request that should fail, and check that it does.

  No key. A token for a different service. A URL pointing at localhost:8080. A search of your traces for "sk-".

  One request each.

  #AISecurity #MCP #GRC #ControlTesting #CyberSecurity
tools: [agent-access-review]
image: /assets/img/posts/the-log-said-authentication-was-enabled.png
---

When you ran the `@sylphx/pdf-reader-mcp` server over HTTP and set an API key, it printed this at startup: `API key authentication enabled (X-API-Key header)`. According to [the advisory](https://github.com/advisories/GHSA-q344-5v34-gm84) published on October 29, the server read the key into a variable and never checked it on incoming requests. It also listened on all network interfaces by default. Anyone who could reach the port could use every tool and read any PDF the process could open.

The advisory puts the real problem in one line: the misleading startup log made the exposure silent. The operator had done the right thing and had a log line saying so.

That's CVE-2026-62264, fixed in version 3.0.1. Three other advisories for AI agent tooling published the same week have the same shape. In each one, a control was configured, or existed in the code, and didn't work.

{% include figures.html items=page.figures %}

## Four controls that were there and didn't work

**An API key nobody checked.** The case above. The fix in 3.0.1 checks the header, rejects a missing or wrong key with a 401, and changes the default to listen only on the local machine.

**A token check that was off.** The [MCP Python SDK advisory](https://github.com/advisories/GHSA-w4fh-qvv9-3v23) (CVE-2026-116684) covers servers using the SDK's bearer-token authentication. They accepted any valid token from the authorisation server, including tokens issued for a different service. The advisory is unusually blunt about the fix: "Upgrading alone changes nothing." The new audience check is off unless you turn it on, and won't be on by default until version 3.0. A team that upgraded and closed the ticket still has the problem.

**An SSRF filter with a gap.** [mcp-sanitizer](https://github.com/advisories/GHSA-4mfg-r38w-w8fg) exists to check URLs before an agent's fetch tool requests them. Before version 1.4.0 it blocked `http://localhost/` but let `http://localhost:8080/` through, because the check only applied when there was no port. It also missed IPv6 loopback addresses written in the bracketed form that URLs use, like `[::1]`. Internal services nearly always run on a port, so the filter blocked the case that mattered least.

**A redaction that covered one path.** [MLflow's CrewAI autologging](https://github.com/advisories/GHSA-j7qq-vr8c-xvw3) (CVE-2026-116691) already removed the API key from the span describing the LLM. But it also recorded the agent's whole internal state, which contains the LLM object, whose text form includes the key. The researcher found their test key in 5 places across 2 spans, sent wherever the traces go. Fixed in 3.17.0.

## Design and operating effectiveness

Auditors split control testing into two questions. Is the control designed properly: does it exist, is it configured, would it prevent the risk if it worked? And does it operate effectively: does it actually work, every time?

Every one of these four would pass a design review. The API key is set. The SDK supports token authentication. The URL filter is in the middleware. The tracing library redacts keys. Screenshots of the settings, the config file and the startup log would all look fine.

None of them would pass a test of operating effectiveness, and that test is cheap. You send the request that should fail and check that it does.

## The tests

For each control an agent or MCP server relies on, write down the request that should be refused and send it.

- **Authentication:** send a request with no key, then one with a wrong key. Expect a 401 for both. Check what the server is listening on: if it's `0.0.0.0` and it doesn't need to be, that's a finding too.
- **Token audience:** get a valid token from the same authorisation server for a different service and send it. Expect a 401. If you use the MCP Python SDK, check that `validate_token_resource` is set, not just that you've upgraded.
- **URL filters:** try `http://localhost:8080/`, `http://127.0.0.1:8080/`, `http://[::1]:8080/` and `http://169.254.169.254/` (the cloud metadata address). Every one should be blocked.
- **Secrets in telemetry:** put a fake key with a recognisable prefix in a test run, then search everything your tracing sends for it. Expect zero matches.

Each takes a few minutes, and none needs special tools. The result is better evidence than any screenshot: a dated test with the request that was sent and the response that came back.

## Where this fits in an access review

When I review an agent's access, the inventory comes first: which servers it uses, which versions, and what each can reach. [agent-access-review](https://github.com/Mihirajmera/agent-access-review) builds that from the MCP client configs, and it flags servers that aren't pinned to a version, which matters here because all four fixes need a newer version, and one also needs a setting changed. But the inventory is design evidence too. For the controls that matter, the negative test is the step that shows they work.
