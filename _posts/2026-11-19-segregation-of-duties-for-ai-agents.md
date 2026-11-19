---
title: "Segregation of duties for AI agents: review the combination, not the permission"
description: "Finance learned long ago that risk lives in combinations of permissions. AI agents have their own toxic combination: sensitive data, content outsiders can write, and a way to send data out. 166 of 2,830 public MCP configs give one agent all three."
kind: note
research: true
status: review
tags: [AI agents, Access reviews, Segregation of duties]
evidence:
  hash: AAR-09
  label: "agent-access-review AAR-09: the exfiltration-path check and its demo agents"
  url: https://github.com/Mihirajmera/agent-access-review#the-ai-specific-risk-exfiltration-paths-aar-09
figures:
  - {n: "166", label: "of 2,830 public MCP configs give one agent all three legs (5.9%)", tone: red}
  - {n: "0/9", label: "official README configs with the path on their own; combined, they form one", tone: amber}
  - {n: "1", label: "human approval on the way in or the way out breaks the chain", tone: green}
diagram:
  type: flow
  caption: "finance-ops-agent from agent-access-review's demo: three ordinary permissions, one toxic combination"
  steps:
    - {id: "1", label: Reads sensitive data, sub: NetSuite vendor bills, test: normal on its own, state: info}
    - {id: "2", label: Reads content outsiders write, sub: an AP inbox anyone can email, test: normal on its own, state: info}
    - {id: "3", label: Sends data out, sub: "sends email, no human approval", test: normal on its own, state: warn}
    - {id: AAR-09, label: All three in one agent, sub: one crafted invoice email could mail out vendor bank details, test: exfiltration path, state: fail}
linkedin: |
  Finance figured this out decades ago: the person who creates a vendor shouldn't approve its payments. Each permission is fine. The combination is fraud waiting to happen.

  AI agents have their own toxic combination. An agent is dangerous when it can:

  1️⃣ Read sensitive data (files, databases, mailboxes)
  2️⃣ Read content outsiders can write (emails, web pages, GitHub issues)
  3️⃣ Send data out (email, HTTP, comments, commits)

  Simon Willison calls it the lethal trifecta. With all three, one prompt injection hidden in an email can get the agent to collect your data and send it somewhere.

  How common is it?
  → 166 of 2,830 public MCP configs I reviewed give one agent all three, with no human approval anywhere.
  → I combined nine official MCP README examples into one config. None had the path alone. Together, they did.

  The control is the one finance already uses: review combinations, not permissions. Then split the agent, remove a leg, or put a human approval on the way in or the way out.

  A permission-by-permission access review will pass every one of these agents.

  #AIGovernance #AgenticAI #GRC #AccessReview #AISecurity
tools: [agent-access-review]
image: /assets/img/posts/segregation-of-duties-for-ai-agents.png
---

Segregation of duties is one of the oldest controls in finance. The person who creates a vendor shouldn't be the person who approves its payments. Each permission is harmless on its own. Together, they let one person commit fraud without anyone noticing.

AI agents have the same problem, with a different combination. An agent is dangerous when it can:

1. **read sensitive data**: files, databases, mailboxes;
2. **read content outsiders can write**: web pages, GitHub issues, emails, Slack messages;
3. **send data out**: HTTP requests, emails, comments, commits.

Simon Willison calls this [the lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/). With all three, a prompt injection hidden in something the agent reads can instruct it to collect your data and send it somewhere.

{% include figures.html items=page.figures %}

## A permission-by-permission review passes it

Take `finance-ops-agent`, one of the example agents bundled with [agent-access-review](https://github.com/Mihirajmera/agent-access-review). It reads vendor bills in NetSuite. It reads the accounts-payable inbox, which any vendor can email. It can send email. Review each grant on its own and every one is reasonable: that's the job.

Put together, one crafted invoice email could tell the agent to forward vendor bank details to an outside address, and nothing would stop it. The tool flags it as AAR-09:

> Exfiltration path: reads sensitive data (expense-ocr, netsuite, outlook, sharepoint), ingests untrusted content (outlook) and can send data out (outlook) with no human approval.

Notice that one tool, Outlook, supplies two of the three legs. A mailbox reads untrusted content and sends data out. Reviewing by tool would miss that too.

## It isn't rare

- In the [2,830 public MCP configs](/case-studies/public-mcp-configs/) I reviewed, **166 (5.9%)** give a single agent all three legs with no human approval on any step.
- When I [combined nine official MCP README examples](/blog/what-mcp-readmes-teach-you-to-copy/) into one config, the result had the full path. None of the nine did on its own. Nobody designed that agent; it was assembled one copy-paste at a time.

## The finance playbook maps straight across

| In finance | For an AI agent |
|---|---|
| Define the toxic pairs (create vendor + approve payment) | Define the toxic combination: sensitive data + untrusted input + egress |
| Review each person's roles together, not one at a time | Review each agent's tools together, not one at a time |
| Split the duties between two people | Split the work between two agents, so the one that reads the inbox can't reach the data |
| Remove one of the conflicting roles | Remove a leg: drop egress, or don't feed it untrusted content |
| Where you can't split, add a compensating control: a second approver | Require human approval before untrusted content is acted on or before anything leaves |
| Review the payment log afterwards | Log every tool call and review what left ([agent-flight-recorder](https://github.com/Mihirajmera/agent-flight-recorder) records them) |

The approval has to sit on the way in or the way out. Approving access to the sensitive data doesn't help: the injection arrives after that decision, through a channel you already allowed.

## What to ask in your next agent access review

- For each agent: does it have all three legs? Count a single tool more than once if it reads untrusted content and sends data out.
- If yes, which one is broken: split, removed, or gated by a person?
- If gated, is the approval actually enforced, or just a setting the agent can skip? Check the log, not the config.

Then run the check yourself on a real config:
