---
title: "Your AI agent is a service account. Review it like one, then ask four more questions."
description: "AI agents hold tokens, shells and databases, and most have never been in an access review. The service-account review you already run covers most of it. Four things it doesn't cover are where agents actually go wrong."
kind: essay
research: true
status: review
tags: [AI agents, Access reviews, Non-human identity]
evidence:
  hash: agent-access-review
  label: "agent-access-review: the review packet for five example agents, and 2,830 public configs"
  url: https://github.com/Mihirajmera/agent-access-review/tree/main/sample-output
figures:
  - {n: "216 days", label: "since the example finance agent's access was approved; the limit is 90", tone: amber}
  - {n: "3.8%", label: "of 2,830 public MCP configs contain a real-looking secret", tone: red}
  - {n: "95%", label: "of their package servers aren't pinned: new code runs under the same identity on every start", tone: red}
diagram:
  type: flow
  caption: "the service-account questions, asked of finance-ops-agent (an example agent bundled with agent-access-review)"
  steps:
    - {id: AAR-01, label: "Who owns it?", sub: a named person in the agent manifest, test: owner named, state: ok}
    - {id: AAR-02, label: "Who approved it, and when?", sub: "cfo-office, 216 days ago", test: over the 90-day limit, state: warn}
    - {id: AAR-04, label: "What can it actually reach?", sub: "SharePoint Sites.Read.All", test: tenant-wide scope, state: fail}
    - {id: AAR-08, label: "What does it still use?", sub: expense-ocr unused for 164 days, test: revoke, state: warn}
    - {id: AAR-07, label: "Where are its credentials?", sub: NetSuite token last rotated 315 days ago, test: rotate, state: warn}
linkedin: |
  Every quarter, most companies review who has access to what. Service accounts included.

  AI agents now hold GitHub tokens, database connections, Slack bots and shells. Most have never been in an access review.

  The good news: the service-account questions mostly work. Who owns it? Who approved it? What can it reach? What does it still use? Where are its credentials?

  But an agent isn't quite a service account. Four differences, and the question each one adds:

  1️⃣ It picks its own actions from what it reads. → Review the combination of tools, and require a human for privileged actions.

  2️⃣ Its code changes under the same identity. 95% of package servers in 2,830 public MCP configs aren't pinned. → Is every tool pinned to a version?

  3️⃣ It lives in a JSON file, not your identity system. An MCP config has no field for an owner or an approval. → Where is your inventory of agents?

  4️⃣ Its config is only half the evidence. → What does the log say it actually did?

  Start with the review you already run. Then add the four questions it was never designed to ask.

  #AIGovernance #IAM #GRC #AIAgents #NonHumanIdentity
tools: [agent-access-review]
image: /assets/img/posts/your-ai-agent-is-a-service-account.png
---

Most companies run a user access review every quarter. A manager looks at each account's access and confirms it's still needed. Service accounts, the non-human identities that run jobs and integrations, are part of that review.

An AI agent is a non-human identity too. It authenticates with tokens, reaches systems through tools and acts on its own. Yet most agents have never appeared in an access review, because they live in a JSON config on a developer's laptop rather than in the identity system.

The good news is that the review already exists, and most of its questions transfer directly.

{% include figures.html items=page.figures %}

## The questions that transfer

Here they are, asked of `finance-ops-agent`, one of the example agents bundled with [agent-access-review](https://github.com/Mihirajmera/agent-access-review). It reads vendor bills in NetSuite, works an accounts-payable mailbox and can send email.

| Question | For a service account | What the review found | Check |
|---|---|---|---|
| Who owns it? | The owner in the identity system or CMDB | A named owner in the agent manifest | AAR-01 |
| Who approved it, and when? | Last quarter's recertification | Approved by cfo-office 216 days ago; the limit is 90 | AAR-02 |
| What can it actually reach? | Its entitlements | SharePoint `Sites.Read.All`: every site in the tenant | AAR-04 |
| What does it still use? | Last login per entitlement | The OCR tool hasn't been used in 164 days | AAR-08 |
| Where are its credentials, and how old are they? | Vault, rotation date | The NetSuite token was last rotated 315 days ago | AAR-06, AAR-07 |

Every one of those findings would be routine in a service-account review, and the decisions are the familiar ones: keep, modify or revoke, signed by a reviewer.

The finance agent at least has an owner. The two raw MCP configs in the same demo, a Claude Desktop config and a VS Code config, come out with **no owner and no approval**. That isn't carelessness in the example: an MCP config file has no field for either.

## Four ways an agent isn't a service account

A service account runs the same code, makes the same calls and never reads a stranger's email. An agent breaks all three assumptions. Each difference adds a question the old review never needed.

### 1. It chooses its own actions from what it reads

A service account's behaviour is fixed by its code. An agent decides which tool to call based on its input, and some of that input is written by outsiders. That's why a prompt injection in one email can turn a reasonable set of permissions into a data leak.

**Add:** review the *combination* of tools, not each one alone, as I covered [yesterday](/blog/segregation-of-duties-for-ai-agents/). And require a human to approve privileged actions (AAR-03). No service account has ever had to ask a person before acting; for an agent that writes, deletes or sends, it's the strongest control you have.

### 2. Its code changes under the same identity

When a service account's job is updated, it goes through change control. Most agent tools don't: in the [2,830 public MCP configs](/case-studies/public-mcp-configs/) I reviewed, 95% of servers installed from npm, PyPI or a container registry aren't pinned to a version. Whatever was published most recently runs on the next start, with the agent's tokens. And 2.8% of configs still run a reference server whose repository is archived and which gets no security fixes.

**Add:** is every tool pinned to a version or digest (AAR-10), and is each one still maintained (AAR-13)?

### 3. It lives outside the identity system

You can export every service account from the identity provider. There's no equivalent export for agents: they're defined in config files in editors, repos and home directories, which is exactly why thousands of them are sitting in public GitHub repos. And 3.8% of those configs contain a real-looking secret in plain text.

**Add:** where is your inventory of agents, and how do you find the ones nobody registered? Until you have one, the review only covers the agents people volunteer.

### 4. Its config is only half the evidence

An access review reads what an identity is *allowed* to do. For a service account that's usually close enough to what it does. For an agent it isn't: the same config can be used carefully or recklessly, and a human approval may exist only in the runtime path. I showed a case where [the config failed least privilege and the log passed it](/blog/the-config-failed-the-log-passed/), and both were right.

**Add:** what does the tool-call log say the agent actually did, and does it agree with what it was approved to do?

## Start with the review you have

You don't need a new framework to begin. Put agents into the access review you already run, with the five questions above, then add the four it was never designed to ask:

1. Is any agent's combination of tools an exfiltration path, and do privileged actions need a human?
2. Is every tool pinned, and still maintained?
3. Where is the agent inventory, and what's missing from it?
4. Does the runtime log match the approved access?

If nobody can say who owns an agent, stop there. That's the first finding, and an agent nobody owns will never lose its access.
