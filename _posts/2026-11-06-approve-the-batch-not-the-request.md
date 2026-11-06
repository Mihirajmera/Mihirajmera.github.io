---
title: "Approve the batch, not the request"
description: "When an agent queues work for a human to approve, the approval usually points at a ticket or a request ID. The agent can change what's inside the request after someone approves it. Here's how to bind an approval to the exact batch, so a changed batch needs a new approval, and how an auditor tests it."
kind: essay
status: review
tags: [AI agents, AI governance, Access control]
figures:
  - {n: "1", label: "fingerprint of the exact batch, stored with the approval", tone: amber}
  - {n: "1", label: "release per approval, then it's used up"}
  - {n: "0", label: "released batches whose fingerprint matches no approval", tone: red}
diagram:
  type: flow
  caption: an approval bound to the batch it approves
  steps:
    - {id: Q-01, label: Agent queues a batch, sub: 40 credit-limit changes, state: info}
    - {id: A-01, label: Approver reviews it, sub: "fingerprint, approver, expiry stored", test: approver is not the requester, state: ok}
    - {id: Q-02, label: Agent rebuilds the batch, sub: 41 changes after new data arrives, state: warn}
    - {id: R-01, label: Release check, sub: fingerprint no longer matches, test: recompute at release, state: fail}
    - {id: Q-03, label: Back in the queue, sub: a new request for a new decision, state: ok}
linkedin: |
  An approval should name exactly what it approves.

  When an agent queues work for a human, the approval usually points at a ticket or a request ID. But an agent can rebuild the batch after the approval: new data arrives, it recalculates, it adds one more record. The request ID stays the same. The approval still "covers" it.

  Louisa Johnson Bullock put the rule well in a comment this week: the approval should identify the batch and its release conditions, and if the batch changes, the earlier approval shouldn't be assumed to cover it.

  Here's how to make that enforceable:

  1️⃣ Fingerprint the batch when it's approved: the exact records, values and target system.

  2️⃣ Store the fingerprint with the approver's name, an expiry time and the release conditions.

  3️⃣ Recompute the fingerprint at release. No match means a new request, not a judgement call.

  4️⃣ One approval, one release. A retry needs a new decision.

  5️⃣ Show the approver the same content you fingerprint. Otherwise they're approving a hash of something they never read.

  The audit test becomes mechanical: for every released batch, find the approval with the same fingerprint, a different person, and an expiry that hadn't passed.

  #AIGovernance #AgenticAI #AccessControl #GRC #CyberSecurity
tools: [agent-flight-recorder]
image: /assets/img/posts/approve-the-batch-not-the-request.png
---

On Tuesday's post about [the Hong Kong regulator's paper on AI agents](/blog/a-regulator-just-wrote-the-audit-program-for-ai-agents/), Louisa Johnson Bullock, founder of Regulayer, raised a timing problem. If an agent queues a batch of credit-limit changes and the approver needs ten minutes to review them, the system has to hold that batch for ten minutes. Otherwise the option to reject it only exists on paper.

When the discussion continued, she added the rule that makes the hold mean something: the approval should identify the batch and its release conditions, and if the batch changes, the earlier approval shouldn't be assumed to cover it.

That's easy to agree with and easy to get wrong in practice, so this post is about building it.

{% include figures.html items=page.figures %}

## How approvals drift

Most approval steps point at a container: a ticket, a change request, a workflow ID. The approver opens it, reads what's inside, and clicks approve. The system records "request 4471 approved by priya".

The problem is that an agent doesn't treat the contents as fixed. Between the request and the release, it can:

- **Rebuild the batch.** New data arrives during the ten-minute review, and the agent recalculates. Forty changes become forty-one.
- **Retry with different values.** The first attempt failed, so the agent adjusts an amount and tries again under the same request.
- **Reuse the approval.** The release succeeds, a later step fails, and the agent runs the whole thing again.

In each case the request ID hasn't changed, so the record still says "approved". Nobody approved the forty-first change, the new amount or the second run.

None of this needs a misbehaving agent. It's what a helpful agent does when the data moves under it.

## Bind the approval to the content

The fix is to approve the content itself, not the container. When the approver decides, the system computes a fingerprint (a SHA-256 hash) of exactly what will be released, and stores it with the decision. A useful approval record holds:

- **The fingerprint** of the batch: the records, the values and the target system.
- **The approver**, who must not be the person the agent is acting for.
- **An expiry time.** An approval from yesterday shouldn't release anything today.
- **The release conditions**, if there are any, such as "only during the batch window".
- **Whether it's been used.** One approval releases one batch.

At release, the system computes the fingerprint again from what it's about to send. If it doesn't match, the batch goes back in the queue as a new request. The same happens if the approval has expired or has already been used. Then "has the batch changed?" isn't something two people argue about later. The hashes either match or they don't.

## Two details that decide whether it works

**What goes into the fingerprint.** Hash the content in a fixed order, so the same batch always gives the same fingerprint. Then choose the fields carefully. Include a field that changes on every run, such as a generated timestamp, and no approval will ever match. Leave out a field that matters, such as the amount, and the fingerprint will match batches the approver never saw. Decide per action which fields count, and write the list down, because an auditor will ask.

**What the approver sees.** The approver has to review the same content you fingerprint. If the screen shows a summary ("40 limit increases, total 2.1m") but the hash covers the full records, the approver has signed off on a hash of something they never read. Show the records, or fingerprint the summary and release only what the summary describes.

## How an auditor tests it

The useful thing about this control is that the test is mechanical. Take a sample of released batches. For each one:

1. Recompute the fingerprint from what was actually released.
2. Find an approval record with the same fingerprint.
3. Check that the approver isn't the person the agent acted for.
4. Check that the release happened before the approval expired.
5. Check that no other release used the same approval.

Each of these has a clear failure: a release with no matching fingerprint, a self-approval, a release after expiry, or two releases on one approval. You don't need anyone's account of what happened.

The test only works if the release log is complete and nobody can edit it afterwards. Otherwise someone could fix a mismatch by changing the record.

## Where I've built this, and where I haven't

[agent-flight-recorder](https://github.com/Mihirajmera/agent-flight-recorder) does this for individual MCP tool calls. When policy says a call needs a human, the proxy holds it and records a pending request. The approval is bound to a SHA-256 of the server, the tool and the arguments, so approving "merge PR 41" doesn't approve "merge PR 42". It expires after a set time and works once. The log is hash-chained and signed, and the report re-performs the checks above: AFR-03 fails a call that ran on a missing, expired, reused or mismatched approval, and AFR-04 fails a self-approval.

Two limits are worth stating. First, it binds one tool call. If an agent submits a batch in one call, the approval covers the batch. If it spreads the batch across forty separate calls, you either approve each call or put a step in front that submits the batch as one. Second, `afr approve` trusts the approver name it's given, so in production you'd run approvals through a system that authenticates the person first.

## It's also what makes a stop work

There's a link to [yesterday's post about kill switches](/blog/a-kill-switch-youve-never-pulled-is-not-a-control/). Its hardest test was proving that nothing the agent had queued ran after the stop. A batch that's held until its exact fingerprint is approved is also a batch that can be cancelled: if the agent is stopped while the batch waits, the batch has nothing to release it.

So the same hold does two jobs. It makes the approver's decision mean something, and it gives the stop something to catch.
