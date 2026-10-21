---
title: Your AI agent is a service account. Review it like one.
description: AI agents hold tokens, shells and databases. The access review we already run for service accounts covers most of what they need.
kind: note
status: note
tags: [AI agents]
linkedin: |
  Every quarter, most companies review who has access to what. Service accounts included.

  AI agents now hold GitHub tokens, database connections, Slack bots and shells. Most of them have never been in an access review.

  You don't need a new framework to start. The questions we already ask about a service account work:

  1. Who owns it?
  2. What is it for?
  3. What can it actually reach (not what we think it reaches)?
  4. Who approved that, and when?
  5. When did it last use each permission?
  6. Where are its credentials stored?

  If nobody can answer #1, that's your first finding.

  I built an open-source tool that runs this review on MCP configs and agent manifests. Link in the first comment.

  #AIGovernance #IAM #GRC #AIAgents
---

Most companies run a user access review every quarter. A manager looks at each account's access and confirms it's still needed. Service accounts, the non-human identities that run jobs and integrations, are part of that review.

An AI agent is a non-human identity too. It authenticates with tokens, reaches systems through tools and acts on its own. Yet most agents have never appeared in an access review, because they live in a JSON config on a developer's laptop rather than in the identity system.

The good news is that the review already exists. Ask the service-account questions:

1. **Owner:** who is accountable for this agent?
2. **Purpose:** what is it for, in one sentence?
3. **Actual access:** what can its tools read, write, send or execute?
4. **Approval:** who approved that access, and when?
5. **Usage:** when did it last use each permission? Unused access should go.
6. **Credentials:** are its tokens in a secret store, or pasted into a file?

An agent nobody owns will never lose access, so an unowned agent is the first finding to fix.

[agent-access-review](https://github.com/Mihirajmera/agent-access-review) automates this for MCP configs and agent manifests and produces the sign-off packet an auditor expects.
