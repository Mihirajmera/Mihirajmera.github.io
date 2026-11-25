---
title: "Three laptops went into my access review. One came out with evidence."
description: "An older version of agent-access-review took three MCP configs, showed two in its summary, wrote evidence for one, copied a plain-text token into evidence meant for auditors, and exited 0. An outside contributor found all three bugs. The lesson is the oldest one in audit: reconcile the population before you test anything."
kind: note
research: true
status: review
tags: [AI agents, Access review, Audit evidence, MCP]
evidence:
  hash: agent-access-review
  label: "agent-access-review: the fix (PR #21) and the parser tests that cover it"
  url: https://github.com/Mihirajmera/agent-access-review/pull/21
figures:
  - {n: "3 → 1", label: "laptop configs in, evidence files out, on the version before the fix", tone: red}
  - {n: "0", label: "the exit code, every time: nothing told the reviewer", tone: amber}
  - {n: "1", label: "plain-text token copied into evidence meant to be shared with auditors", tone: red}
diagram:
  type: flow
  caption: "three MCP configs through agent-access-review before the fix"
  steps:
    - {id: IN, label: Three laptops, sub: "laptop-a, laptop-b, laptop-c: one claude_desktop_config.json each", test: 3 configs, state: info}
    - {id: PARSE, label: laptop-c skipped, sub: "saved with a UTF-8 byte-order mark; a warning on stderr", test: 2 parsed, state: fail}
    - {id: ID, label: laptop-a overwritten, sub: "both got the id claude-desktop-config, from the file name", test: 1 evidence file, state: fail}
    - {id: REDACT, label: Token kept in evidence, sub: "--token value, with a space, wasn't matched", test: "not reported, not masked", state: fail}
tools: [agent-access-review]
image: /assets/img/posts/three-laptops-went-in-one-came-out.png
---

Every access review I've worked on started with the same question from the auditor, before a single control was tested: **how do you know this list is complete?** Auditors call it the completeness and accuracy of the population. If the tool that produced the list quietly dropped some of it, every test after that is clean on a sample you didn't choose.

I build [agent-access-review](https://github.com/Mihirajmera/agent-access-review), which reviews the MCP configs that give AI agents their tools. In October an outside contributor, [CJstate](https://github.com/CJstate), sent [a fix](https://github.com/Mihirajmera/agent-access-review/pull/21) titled "stop losing findings silently in three places". I reran the version before the fix to see what it would have looked like from the reviewer's chair.

{% include figures.html items=page.figures %}

## The test

Three fake laptops, one Claude Desktop config each. Nothing exotic:

- **laptop-a:** the filesystem server, pointed at a projects folder.
- **laptop-b:** GitHub and Postgres. The Postgres server takes its token as `--token <value>`, the way most command-line tools document it. The value is fake.
- **laptop-c:** the Slack server. The file was saved with a UTF-8 byte-order mark, which is what Notepad and PowerShell's `Out-File` write by default on Windows.

## What the old version produced

```
$ agent-access-review scan hosts --out out-old
warning: skipped hosts/laptop-c/claude_desktop_config.json: JSONDecodeError: Unexpected UTF-8 BOM ...
AGENT                        TOOLS  HIGH   MED   LOW
claude-desktop-config            1     3     1     1
claude-desktop-config            2     4     2     1
$ echo $?
0
```

Three things went wrong, and none of them stopped the run.

**laptop-c disappeared.** The byte-order mark made the JSON parser fail, so the file was treated as unrelated and skipped. The only trace is one warning line on stderr, which is the first thing a CI log or a scheduled job throws away.

**laptop-a lost its evidence.** Both remaining agents got the same id, `claude-desktop-config`, because the id came from the file name. The summary shows two rows with the same name. In the evidence folder there is one file, and its source is laptop-b: the second write replaced the first.

**The token ended up in the evidence.** The secret check only matched `--token=value`. With a space, the token wasn't reported as a hardcoded credential and wasn't masked, so it sat in plain text in the evidence file. The README says secrets are masked during parsing so that evidence can be shared with auditors.

## What the current version produces

```
AGENT                        TOOLS  HIGH   MED   LOW
hosts-laptop-a-claude-deskto     1     3     1     1
hosts-laptop-b-claude-deskto     2     7     2     1
hosts-laptop-c-claude-deskto     1     5     1     1
```

Three agents, three evidence files, and the token reported as AAR-06 (a plain-text credential) and masked in the evidence. Some of the extra findings come from checks added since, so don't read the high counts as one-for-one.

## The gap that's still there

While writing this I tried one more thing on the current version: a fourth config with broken JSON. It was skipped with a warning, the run exited 0, and the review packet doesn't mention it. The byte-order mark case is fixed, but the general one isn't: **the report doesn't say what it didn't review.**

That's the next fix. The packet should open with a population line: files found, agents reviewed, files skipped and why. And a run that skipped something should be able to fail in CI, the same way findings can.

## What to ask of any tool that produces your population

This isn't about my tool. It applies to any scanner, export or script whose output becomes the list you test against:

1. **Count in, count out.** How many sources did it read, and how many items did it produce? If those don't reconcile, stop before testing anything.
2. **Where do skips go?** A warning on stderr isn't evidence. Skips should be in the report, with the reason.
3. **Can two items collide?** If the key comes from a file name, a hostname or a display name, two different things can share it, and one write replaces the other.
4. **Test the redaction with the real format.** Feed the tool a secret written the way your tools actually write it, and grep the output for it.

The bugs that hurt an access review aren't the ones that crash. They're the ones that finish cleanly on less than you gave them. Thanks to CJstate for finding three of them.
