---
title: Segregation of duties for AI agents
description: Finance learned long ago that risk lives in combinations of permissions. AI agents have their own toxic combination.
kind: note
status: note
tags: [AI agents]
linkedin: |
  In finance, the same person shouldn't be able to create a vendor AND approve its payments. Each permission is fine. The combination is fraud risk.

  That's segregation of duties, and it maps almost perfectly onto AI agents.

  An agent becomes dangerous when it combines three things:
  1. It can read sensitive data.
  2. It ingests content outsiders can write (web pages, issues, emails, Slack).
  3. It can send data out.

  Simon Willison calls this the "lethal trifecta". Any one of them is normal. All three in one agent means a prompt injection hidden in a web page can make it leak your data.

  The fix is the same as in finance: review combinations, not permissions. Split the duties across agents, or put a human approval in the path.

  #AIGovernance #AISecurity #GRC #SoD
---

Segregation of duties is one of the oldest controls in finance. The person who creates a vendor shouldn't be the person who approves its payments. Each permission is harmless on its own. Together, they let one person commit fraud without anyone noticing.

AI agents have the same problem, with a different combination. An agent is dangerous when it can:

1. **read sensitive data**: files, databases, mailboxes;
2. **ingest content outsiders can write**: web pages, GitHub issues, emails, Slack messages;
3. **send data out**: HTTP requests, messages, comments, commits.

Simon Willison calls this combination the *lethal trifecta*. With all three, a prompt injection hidden in something the agent reads can instruct it to collect your data and send it somewhere.

The governance answer is the one finance already uses: **review combinations, not permissions.** For each agent, check whether all three are present. If they are, split the duties across separate agents, remove one leg, or require a human approval before anything leaves.

When I [combined nine official MCP README examples](/blog/what-mcp-readmes-teach-you-to-copy/) into one config, the result had all three. No single server did.
