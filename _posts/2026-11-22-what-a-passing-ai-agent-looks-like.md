---
title: "What a passing AI agent looks like, line by line"
description: "This week was all failing agents. Here's one that passes every access-review check that applies to it, the 25 lines of manifest that make it pass, and the three things a pass still doesn't prove."
kind: note
research: true
status: review
tags: [AI agents, Access reviews, Agent governance]
evidence:
  hash: support-copilot
  label: "agent-access-review: support-copilot's manifest and review packet (no findings)"
  url: https://github.com/Mihirajmera/agent-access-review/blob/main/agent_access_review/examples/agents.yaml
figures:
  - {n: "0", label: "findings for support-copilot, across every check that applies to it", tone: green}
  - {n: "53 days", label: "since its access was approved; the limit is 90", tone: green}
  - {n: "2 of 3", label: "dangerous legs present; the third, sending out, needs a human", tone: amber}
diagram:
  type: flow
  caption: "support-copilot, an example agent bundled with agent-access-review: every question answered by a line in its manifest"
  steps:
    - {id: AAR-01, label: Owned, sub: a named person in the manifest, test: owner on record, state: ok}
    - {id: AAR-02, label: Approved and current, sub: "ai-review-board, 53 days before the review", test: inside 90 days, state: ok}
    - {id: AAR-03, label: A human sends, sub: "the agent drafts ticket replies, a person sends them", test: approval on the way out, state: ok}
    - {id: AAR-04, label: Scoped, sub: "one Confluence space, read-only", test: least privilege, state: ok}
    - {id: AAR-06/07, label: Credentials managed, sub: "token in a vault, rotated 72 days ago", test: inside 90 days, state: ok}
tools: [agent-access-review]
image: /assets/img/posts/what-a-passing-ai-agent-looks-like.png
---

This week I wrote about agents that fail their access review: one with an [exfiltration path](/blog/segregation-of-duties-for-ai-agents/), one with [stale approvals and a tenant-wide scope](/blog/your-ai-agent-is-a-service-account/). That's useful, but it only tells you what to avoid. Here's the other half: an agent that passes, and exactly what makes it pass.

It's `support-copilot`, one of the example agents bundled with [agent-access-review](https://github.com/Mihirajmera/agent-access-review). It's fictional, but its shape is the point.

{% include figures.html items=page.figures %}

## The whole manifest

```yaml
- id: support-copilot
  name: Customer Support Copilot
  framework: langchain
  owner: priya.shah@example.com
  approved_by: ai-review-board
  approved_on: 2026-08-20
  tools:
    - name: zendesk
      type: ticketing
      resource: zendesk:tickets
      actions: [read, write]
      data_classification: confidential
      untrusted_input: true          # customers write ticket text
      requires_approval: true        # agent drafts, a human sends
      last_used: 2026-10-11
    - name: kb-search
      type: knowledge-base
      resource: confluence:space/SUPPORT
      actions: [read]
      data_classification: internal
      last_used: 2026-10-11
  credentials:
    - name: ZENDESK_API_TOKEN
      tool: zendesk
      source: vault
      last_rotated: 2026-08-01
```

The review ran as of 2026-10-12. Result: **no findings.**

## Which line answers which question

| Line | Question it answers | Check |
|---|---|---|
| `owner` | Who is accountable for this agent? | AAR-01 |
| `approved_by`, `approved_on` | Who approved the access, and is it current? 53 days, inside the 90-day limit | AAR-02 |
| `requires_approval: true` on Zendesk | Does a person approve before the agent writes? The agent drafts replies; a human sends them | AAR-03 |
| `resource: confluence:space/SUPPORT`, `actions: [read]` | Is access limited to what the job needs? One space, read-only, not the whole wiki | AAR-04 |
| `source: vault` | Are credentials kept out of config files? | AAR-06 |
| `last_rotated: 2026-08-01` | Are they rotated? 72 days ago, inside 90 | AAR-07 |
| `last_used` on each tool | Is any access unused? Both tools were used the day before | AAR-08 |

Nothing in there is exotic. Every field is something a service-account review would also ask for. The difference is that someone wrote it down, in one place, before the review started.

## It has two of the three dangerous legs, and still passes

This agent reads confidential data (the ticket history) and takes in content outsiders write (customers write the tickets). That's two legs of the [lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/). A prompt injection in a ticket is entirely possible.

What it lacks is the third leg: an unapproved way to send data out. Its only write path is a ticket reply, and a person sends every one. An injected instruction can make the agent *draft* something it shouldn't, but a human sees the draft before anyone else does. That's the [segregation-of-duties](/blog/segregation-of-duties-for-ai-agents/) fix in its simplest form: the approval sits on the way out.

## What a pass still doesn't prove

An auditor would sign this review and then ask three more questions.

1. **The manifest is the owner's statement.** `requires_approval: true` is a claim. The access review checks that the claim is there; it can't check that it's enforced. For that you need the runtime log, showing each reply waited for a human. That's what [agent-flight-recorder](https://github.com/Mihirajmera/agent-flight-recorder) records, and why [the config and the log can disagree](/blog/the-config-failed-the-log-passed/).
2. **A pass has a date on it.** This one is as of 2026-10-12. The token reaches its 90-day rotation limit on October 30, and the approval runs out on November 18. Without anyone acting, the agent that passes in October fails twice before the year ends.
3. **Access isn't behaviour.** The review says what the agent *can* reach. It says nothing about how the model behaves with that access. Whether it can be talked into drafting a harmful reply is a [red-team question](/blog/write-the-tolerance-down-first/), with its own evidence.

## Copy the shape

If you're putting agents into an access review, start by asking each owner to fill in these fields. You'll learn most of what you need from which ones they can't fill in. An agent with no `owner`, no `approved_on` or a credential with no `source` has already produced its first finding, before any tool runs.
