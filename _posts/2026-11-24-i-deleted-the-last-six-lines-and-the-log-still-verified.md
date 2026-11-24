---
title: "I deleted the last six lines of a signed agent log and it still verified"
description: "A hash-chained, signed log catches any edit in the middle. It can't catch entries cut off the end. Cutting six lines from my own recorder's sample log removed a branch deletion and both of the session's medium findings, and verify still said the chain was intact."
kind: note
research: true
status: review
tags: [AI agents, Audit evidence, Logging, MCP]
evidence:
  hash: agent-flight-recorder
  label: "agent-flight-recorder: the sample flight log, its public key and the verify and report commands"
  url: https://github.com/Mihirajmera/agent-flight-recorder/tree/main/sample-output
figures:
  - {n: "6", label: "lines cut from the end of a 16-entry signed log", tone: amber}
  - {n: "2 → 0", label: "medium findings after the cut (self-approval, changed tool), chain still intact", tone: red}
  - {n: "1", label: "value stored somewhere else that catches it: the head hash", tone: green}
diagram:
  type: timeline
  caption: "the sample flight log, cut after entry 9 and checked three ways"
  events:
    - {t: "Entries 0–9", label: "Reads, a denied push, an approved merge", state: ok}
    - {t: "Entries 10–15", label: "Self-approved branch deletion, a changed tool description", state: fail, gap: "cut"}
    - {t: "verify", label: "10 entries; chain intact; 10 signed", state: warn}
    - {t: "report", label: "AFR-04 and AFR-06 pass: their entries are gone", state: fail}
    - {t: "--anchor", label: "anchor 15:fb82… is not in the log", state: ok}
tools: [agent-flight-recorder]
image: /assets/img/posts/i-deleted-the-last-six-lines-and-the-log-still-verified.png
---

When I review an AI agent's activity log, the first control I test is whether the log itself can be trusted. [agent-flight-recorder](https://github.com/Mihirajmera/agent-flight-recorder) answers that with a hash chain: every entry stores the hash of the one before it, and every hash is signed with Ed25519. Change one character in the middle and every link after it breaks.

That's a strong guarantee, and it has a gap at exactly one end. This post shows the gap on my own tool's sample log, with commands you can rerun.

{% include figures.html items=page.figures %}

## The log

The repo ships a 16-entry log of a fictional release bot working in GitHub, plus the public key that signed it:

```
$ afr verify --log sample-output/flight.jsonl --pubkey sample-output/demo-signing.pub
16 entries; chain intact; 16 signed
Head: 15:fb82444db4f0...  (store it elsewhere; pass it later as --anchor)
```

The report on the full log has two real findings:

- **AFR-04 (separation of duties), entry 11:** dana@example.com approved a `delete_branch` call that the agent made on their own behalf.
- **AFR-06 (change control), entry 14:** the `merge_pull_request` tool changed its description partway through the session, which is what a tool-poisoning "rug pull" looks like.

Both are in the last six entries.

## The cut

I didn't edit anything. I kept the first ten lines and dropped the rest:

```
$ head -10 flight.jsonl > cut.jsonl
$ afr verify --log cut.jsonl --pubkey demo-signing.pub
10 entries; chain intact; 10 signed
```

That's correct. Every remaining entry still links to the one before it, and every signature is still valid. Nothing was forged, so there's nothing for the chain to catch.

Now the report:

| Check | Full log | Cut log |
|---|---|---|
| AFR-04 self-approval | FAIL, entry 11 | PASS |
| AFR-06 tool definition changed | FAIL, entry 14 | PASS |
| AFR-01 log complete and unaltered | low: no anchor given | low: no anchor given |

The self-approval is gone, the changed tool description is gone, and the branch deletion itself (entry 12) is gone too. The one note about the log's integrity reads the same on both versions, because the tool has no way to tell them apart.

## Why the chain can't see it

A hash chain proves that each entry is consistent with what came **before** it. Nothing after the last entry vouches for it. Whoever can write the file can cut it at any entry boundary and get a shorter log that is perfectly valid.

Signatures don't help either. The attacker isn't creating entries, so they don't need the key. They're only removing them.

This isn't specific to my tool. Any append-only log verified only against itself has the same property: [Certificate Transparency](https://certificate.transparency.dev/howctworks/) logs deal with it by publishing signed tree heads that outside monitors keep, and [git](https://git-scm.com/book/en/v2/Git-Internals-Git-References) only catches a rewound branch when someone else still holds the old commit.

## The fix is one value stored somewhere else

`afr verify` prints the head: the index and hash of the last entry. If that value lives somewhere the agent's operator can't change, the cut shows up:

```
$ afr verify --log cut.jsonl --pubkey demo-signing.pub --anchor 15:fb82444db4f0...
10 entries; chain intact; 10 signed
  - anchor 15:fb82444db4f0... is not in the log (entries removed or replaced)
$ echo $?
1
```

In the report, AFR-01 goes from a low note to a high finding: the log is not complete.

Where to put the head matters more than how. It needs to be somewhere the person who controls the agent's host can't edit:

- a change ticket or the approval record for the session
- an object-lock (WORM) bucket in another account
- the SIEM, if the agent's operators can't delete from it
- a message to a channel the audit team owns

How often matters too. An anchor taken at session end protects that session. An agent that runs for days needs one taken on a schedule, and anything written after the latest anchor is still exposed.

## What this means for a review

When someone hands you an agent's log as evidence, "the chain verifies" answers one question: was anything in the middle changed? Ask a second one: **how would we know if the end was missing?** If the answer is "we'd check the head against X," ask to see X. If there is no X, the log proves what the agent did up to some point, and that point was chosen by whoever held the file.

One more thing I noticed while writing this: the cut log ends without a `session-end` entry, and my report doesn't flag that. It's a weak signal (a crashed agent leaves no `session-end` either), but it's worth a note in the report, so it's on my list.

## Try it

```bash
pip install multiagent-flight-recorder
git clone https://github.com/Mihirajmera/agent-flight-recorder && cd agent-flight-recorder/sample-output
head -10 flight.jsonl > cut.jsonl
afr verify --log cut.jsonl --pubkey demo-signing.pub
afr verify --log cut.jsonl --pubkey demo-signing.pub --anchor 15:fb82444db4f0a284cd14130d10d5da54ae11d99f76a3224dac23033873624779
```
