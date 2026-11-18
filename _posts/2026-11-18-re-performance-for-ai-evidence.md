---
title: "I re-performed my own AI assurance results. Every study had something the output missed."
description: "Four case studies, four tools' outputs, and in each one, redoing part of the work by hand found something the output got wrong or couldn't see. A hash proves evidence wasn't swapped. Only re-performance shows it's right."
kind: note
research: true
status: review
tags: [AI assurance, Audit evidence, Re-performance]
evidence:
  hash: ai-assurance-demo
  label: "ai-assurance-demo: a hashed evidence bundle you can verify and rebuild"
  url: https://github.com/Mihirajmera/ai-assurance-demo/tree/main/sample-output
figures:
  - {n: "4/4", label: "case studies where re-performance found something the output missed", tone: amber}
  - {n: "2 of 3", label: "AutoDAN jailbreak attempts the red-team detector scored wrong", tone: red}
  - {n: "15/15", label: "files in the demo bundle that verify against their SHA-256 manifest", tone: green}
diagram:
  type: flow
  caption: what each tool's output said, and what redoing the work found
  steps:
    - {id: RT, label: Red-team detector scores, sub: re-read the 3 AutoDAN responses, test: 2 of 3 scored wrong, state: fail}
    - {id: README, label: 9 official MCP README configs, sub: looked at why 5 were unclassified, test: "Docker, uvx and volume mounts invisible", state: warn}
    - {id: PUB, label: "2,830 public MCP configs", sub: read the flagged credentials, test: most were placeholders, state: warn}
    - {id: IAM, label: Checkov IAM findings, sub: read each policy against its code, test: missing the one permission needed, state: fail}
linkedin: |
  Auditors have a word for checking work by redoing it: re-performance. It's the strongest evidence there is.

  I've published four AI assurance case studies. In every one, redoing part of the work by hand found something the tool's output missed:

  1️⃣ Red-teaming Llama 3.2: garak's detector scored 2 of 3 AutoDAN jailbreak attempts wrong, in both directions.

  2️⃣ Official MCP README configs: my own tool left 5 of 9 unclassified. The examples had moved to Docker and uvx, and volume mounts (what the agent can really reach) were invisible.

  3️⃣ 2,830 public MCP configs: my tool's first pass flagged 25% of Claude Desktop configs for hardcoded credentials. Most were placeholders, burying the real ones.

  4️⃣ My own Terraform: Checkov said two security Lambdas had permissions that were too broad. Reading the code showed each was also missing the one permission its fix needed.

  None of these was visible in the output itself, because the output was the thing that was wrong.

  So when someone hands you AI evidence, ask: can I redo it? That needs the raw output (hashed), attempt-level records, exact versions, and a tolerance set before the run.

  And remember: a hash proves the file wasn't swapped. It doesn't prove the file is right.

  #AIGovernance #Audit #GRC #AIAssurance
tools: [llm-redteam-evidence, agent-access-review]
image: /assets/img/posts/re-performance-for-ai-evidence.png
---

Auditors rank evidence by how much they had to trust someone else to get it. A control owner's statement is weak. A report from a system is better. The strongest is **re-performance**: take the same inputs, redo the test yourself, and check you get the same answer.

I've published four case studies on AI models, AI agents and the infrastructure around them. In every one, redoing part of the work by hand found something the tool's output got wrong or couldn't see.

{% include figures.html items=page.figures %}

## What the output said, and what redoing it found

| Study | What the output said | What re-performance found |
|---|---|---|
| [Red-teaming Llama 3.2 3B](/case-studies/llm-red-team/) | garak's detector scored three AutoDAN jailbreak attempts | Two were wrong: a refusal scored as a jailbreak, and an accepted jailbreak scored as safe |
| [Official MCP README configs](/case-studies/mcp-readme-configs/) | My tool left 5 of 9 configs unclassified | The examples had moved to Docker images and `uvx`, and Docker volume mounts, what the agent can really reach, were invisible |
| [2,830 public MCP configs](/case-studies/public-mcp-configs/) | My tool's first pass flagged 25% of Claude Desktop configs for hardcoded credentials | Most were template placeholders, which buried the real secrets |
| [My own Terraform](/case-studies/policy-as-code-my-own-terraform/) | Checkov: two remediation Lambdas had over-broad IAM permissions | Each was also missing the one permission its fix needed, so the fix would have failed |

Two of the four rows are my own tool, and two are widely used open-source scanners. This isn't about one bad tool; it's how evidence works. Where the tool was mine, the fix went back into it, and the next study found something new.

## Why the output can't check itself

In the red-team study, a dashboard would have shown the jailbreak count, which happened to be right by coincidence, built entirely from the detector's decisions. The only way to test those decisions is to go below the rate, to the individual attempts, and read them.

The same was true in every row above. The error lived inside the output, so no amount of looking at the output could find it.

## What makes AI evidence re-performable

Evidence can be redone when it keeps four things:

1. **The raw tool output, hashed.** The hash proves the file a reviewer checks is the file that was assessed.
2. **Attempt-level records.** Rates hide everything. Individual attempts can be sampled and read.
3. **Exact versions.** Tool, probes, model and configuration, so the run can be repeated.
4. **The tolerance, set before the run.** Otherwise the verdict [can't be re-derived](/blog/write-the-tolerance-down-first/), only re-argued.

A dashboard screenshot, a score in a slide or a vendor's summary has none of the four.

## Try it on a real bundle

[ai-assurance-demo](https://github.com/Mihirajmera/ai-assurance-demo) assesses one AI agent with three tools and writes a SHA-256 manifest of every file it produces. You can check the committed bundle in a few seconds:

```bash
git clone https://github.com/Mihirajmera/ai-assurance-demo && cd ai-assurance-demo/sample-output
sha256sum -c manifest.sha256    # all 15 files: OK
```

Its CI goes further: on every push it rebuilds the whole bundle from pinned versions of the three tools and checks the result matches the committed copy.

That proves the evidence is intact and repeatable. It doesn't prove the evidence is right. **A hash shows a file wasn't swapped; only reading it shows whether it's correct.** That's the part of re-performance no tool can do for you.

## What to ask when someone hands you AI evidence

- Can I have the raw output behind this number, and its hash?
- Which individual attempts can I sample?
- Which versions of the tool, model and prompts produced it?
- When was the pass threshold set, and by whom?

If the answer to all four is "it's in the dashboard", you have a statement, not evidence.
