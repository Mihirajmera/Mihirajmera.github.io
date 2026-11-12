---
title: "The config failed least privilege. The log passed it. Both were right."
description: "I assessed one AI agent at three layers: what its config allows, what its signed runtime log shows it did, and whether the gateway its model calls go through is controlled. Read one layer at a time and you get three partial answers. Merged into one OSCAL bundle, the layers disagree in the places an auditor most needs to see."
kind: essay
research: true
status: review
evidence:
  hash: ai-assurance-demo
  label: "ai-assurance-demo: the scenario, the three tools and the merged OSCAL bundle"
  url: https://github.com/Mihirajmera/ai-assurance-demo
tags: [AI agents, AI assurance, OSCAL, Access review, Audit evidence]
figures:
  - {n: "31", label: "NIST SP 800-53 controls with evidence from at least one layer"}
  - {n: "8", label: "controls with evidence from more than one layer", tone: amber}
  - {n: "13", label: "controls not satisfied, 2 of them only visible at runtime", tone: red}
diagram:
  type: flow
  caption: one agent, three layers of evidence, one OSCAL bundle
  note: synthetic scenario; every file is in the demo repo
  steps:
    - {id: L-01, label: Configuration, sub: merge and delete with no approval, test: "AC-6: what is it allowed to do?", state: fail}
    - {id: L-02, label: Runtime log, sub: every merge waited for a human, test: "AC-6: what did it actually do?", state: ok}
    - {id: L-03, label: Runtime log, sub: the owner approved their own agent, test: "AC-5: who approved it?", state: fail}
    - {id: L-04, label: Gateway, sub: "image pinned by tag, not digest", test: "SI-7: can it be swapped?", state: fail}
    - {id: L-05, label: Merged OSCAL, sub: "31 controls, 8 from two layers", test: "does every link resolve?", state: ok}
linkedin: |
  I audited one AI agent three times. The config failed least privilege. The runtime log passed it. Both were right.

  An auditor reviewing an AI agent is really asking three questions, and each has different evidence:
  → What is it allowed to do? (its manifest and MCP config)
  → What did it actually do? (a signed log of its tool calls)
  → Is the path its model calls take controlled? (the AI gateway)

  I built a small demo that answers all three for one agent, with three open-source tools, and merges the results into one OSCAL bundle. Read one layer at a time and you get three partial answers. Merged, the layers disagree in useful places:

  1️⃣ Least privilege (AC-6): the config lets the agent merge and delete with no approval. The log shows every merge waited for a human. The control still fails: the approval only happened because the recorder sat in the path, not because the config requires it.

  2️⃣ Separation of duties (AC-5): the config can't show this one at all. Only the runtime log shows the agent's owner approving their own agent's branch deletion.

  3️⃣ Integrity (SI-7) fails at two layers for two reasons: the MCP server changed a tool description mid-session, and the gateway image can be swapped under its tag.

  31 controls have evidence, 8 from more than one layer, 13 not satisfied. Every evidence link resolves to a hashed file, and the bundle is byte-identical on every run.

  The tools roll up mechanically: any failing layer fails the control. Deciding whether one layer's evidence makes up for another's is still the auditor's call, so the report shows every layer side by side.

  #AISecurity #GRC #AIGovernance #AgenticAI #OSCAL
tools: [agent-access-review, agent-flight-recorder, ai-gateway-audit]
image: /assets/img/posts/the-config-failed-the-log-passed.png
---

An auditor reviewing an AI agent is really asking three questions. What is the agent allowed to do? What did it actually do? And is the path its model calls take controlled? Each question has its own evidence: the agent's manifest and MCP config, a log of its tool calls, and the configuration of the AI gateway between the agent and its model provider.

I've written a tool for each of those: [agent-access-review](https://github.com/Mihirajmera/agent-access-review) for the config, [multiagent-flight-recorder](https://github.com/Mihirajmera/agent-flight-recorder) for the runtime log, and [ai-gateway-audit](https://github.com/Mihirajmera/ai-gateway-audit) for the gateway. Each one exports OSCAL assessment results. So I built a [demo](https://github.com/Mihirajmera/ai-assurance-demo) that runs all three on the same agent and merges their results into one bundle, to see what the combined view shows that no single layer does.

{% include figures.html items=page.figures %}

<video controls preload="none" playsinline width="1280" height="720" poster="{{ '/assets/video/ai-assurance-demo.jpg' | relative_url }}" style="width:100%;height:auto;border:1px solid var(--rule);border-radius:6px"><source src="{{ '/assets/video/ai-assurance-demo.mp4' | relative_url }}" type="video/mp4"></video>

## The agent

Acme's Release Agent works in GitHub on behalf of its owner, dana. Everything about it is fictional, and every file is in the [scenario folder](https://github.com/Mihirajmera/ai-assurance-demo/tree/main/scenario):

- **The manifest** says merges and deletions need a human approval. It was last approved 104 days ago.
- **The MCP config actually deployed** runs the archived GitHub reference server from npm, with no pinned version.
- **The runtime log** is a signed, hash-chained record of one session. The agent reads a pull request, is blocked from pushing to `main`, waits for approval before merging, and has a branch deletion approved by dana. Partway through, the MCP server changes one of its tool descriptions.
- **The gateway** is a LiteLLM deployment. It's mostly hardened, but it has no spend cap and its image is pinned by tag rather than by digest.

One command runs the three tools and produces a single report: 31 NIST SP 800-53 controls have evidence, 8 of them from more than one layer, and 13 aren't satisfied. The [combined report](https://github.com/Mihirajmera/ai-assurance-demo/blob/main/sample-output/assurance-report.md) shows each layer's result side by side. Three of its rows are the reason to assess at more than one layer.

## Least privilege: the config failed, the log passed

The deployed config lets the agent merge and delete without approval, so the access review fails AC-6 (AAR-03). The runtime log shows every merge in the session waited for a human, so the flight recorder passes the same control (AFR-03).

Both results are true, and an auditor who saw only one of them would reach the wrong conclusion. The log passes because the recorder sat in the path and enforced the approval. Nothing in the agent's own configuration requires it. Remove the recorder, or run the agent from a laptop where it isn't installed, and the same config merges freely. It's the lesson from [The approval prompt had nobody to ask](/blog/the-approval-prompt-had-nobody-to-ask/): an approval control has to be checked in every way the agent runs, not only the one you observed. The control stays failed until the config itself requires approval. The passing log is evidence that the compensating control works, not that the design is right.

## Separation of duties: only the log can see it

The manifest names dana as the agent's owner. The runtime log shows dana approving the agent's branch deletion. That's the owner approving their own agent's privileged action, which fails AC-5 (AFR-04).

No config review can find this. The config says an approval is needed. It can't say who gave it. An approval step is only a control if the approver is independent of the agent's owner, and that only shows up in what actually happened.

## Integrity: two layers, two different failures

SI-7 fails at two layers for unrelated reasons. At runtime, the MCP server changed a tool's description in the middle of the session (AFR-06), which is how a server can change what the agent believes a tool does after it was reviewed. At the gateway, the container image is pinned by tag (GWA-07), so whoever controls the registry can swap the image without anything in the config changing.

Either finding alone would be a ticket. Together they say the same thing about two different supply chains: what was reviewed isn't guaranteed to be what's running.

## What the merge has to get right

Merging three tools' OSCAL output is mostly bookkeeping, but two parts of it are what make the bundle usable as evidence.

**Every link has to resolve.** Each tool writes evidence files and points at them from its OSCAL results. When the outputs are combined into one bundle, those links have to be rewritten to the new paths. The demo's tests open every link in the merged file and check that the file exists, and a manifest hashes every file in the bundle. An auditor can start from any finding and reach the exact evidence it rests on.

**The output has to be reproducible.** With a fixed timestamp, the bundle is byte-identical on every run, on Windows and on Linux CI. CI rebuilds it on every push and fails if it differs from the committed sample. Anyone can rerun the assessment and get the same bytes. That's what makes re-performance cheap, the same reason I hashed every attempt when I [audited my own red-team results](/blog/auditing-the-red-team/).

## What the roll-up can't decide

The roll-up is deliberately mechanical: a control fails overall if any layer fails it. That's the right default for a tool, because the alternative is software deciding that one layer's evidence makes up for another's.

That decision belongs to the auditor. In the AC-6 case, a reasonable auditor might accept the recorder as a compensating control, if it's deployed everywhere the agent runs and can't be bypassed. Another might not. The report shows every layer's result and the checks behind it, so the person signing off can see exactly what each layer proved and make that call on the record.

## Try it on your own agent

```bash
git clone https://github.com/Mihirajmera/ai-assurance-demo
cd ai-assurance-demo
pip install -r requirements.txt
python assure.py --out assurance
```

To assess your own agent, replace the files in `scenario/` with its manifest, MCP config, flight log and gateway config. If you only want the first layer in CI, agent-access-review is now also a [GitHub Action](https://github.com/marketplace/actions/agent-access-review) that reviews MCP configs on every pull request.

The limits are in the [README](https://github.com/Mihirajmera/ai-assurance-demo#limits): the scenario is synthetic, and the merged OSCAL follows the tools' own structure but hasn't been validated against NIST's schema yet.
