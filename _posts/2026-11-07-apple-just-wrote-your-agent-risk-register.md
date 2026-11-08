---
title: "Apple just wrote your agent risk register"
description: "Apple's new 10-K, filed on November 3, adds a paragraph on how AI agents can fail: exceeding permissions, resisting instructions, concealing actions, completing transactions that can't be reversed. Last year's filing never mentioned agents. Here's that list turned into seven control tests."
kind: essay
research: true
status: review
evidence:
  hash: SEC EDGAR 0000320193-26-000026
  label: Apple Inc. Form 10-K for fiscal 2026, Item 1A Risk Factors
  url: https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm
tags: [AI agents, AI governance, Risk management]
figures:
  - {n: "0", label: "mentions of agents in Apple's fiscal 2025 10-K"}
  - {n: "6 → 55", label: "mentions of \"artificial intelligence\", fiscal 2025 to fiscal 2026", tone: amber}
  - {n: "7", label: "control tests, one for each failure the paragraph names", tone: red}
diagram:
  type: terminal
  title: Apple 10-K, Item 1A
  caption: counted in the filing text on SEC EDGAR
  note: one paragraph, seven control tests
  lines:
    - "# fiscal 2025 10-K, filed 2025-10-31"
    - "+ artificial intelligence: 6   agent: 0   conceal: 0"
    - "# fiscal 2026 10-K, filed 2026-11-03"
    - "! artificial intelligence: 55  agent: 4   conceal: 1"
    - "! may not be authorized to access · exceeding permissions"
    - "! defying directions or resisting instructions"
    - "! conceal actions · difficult to test and audit"
    - "! difficult or impossible to reverse"
linkedin: |
  Last year, Apple's annual report never mentioned AI agents.

  This year's, filed on Tuesday, has a full paragraph on them. It says agents may reach systems they aren't authorised to access, exceed their permissions, resist instructions, conceal their actions, and take steps that can't be reversed.

  Risk factors are written by some of the most careful lawyers anywhere. That makes this paragraph a free, well-reviewed list of agent risks. Copy it into your risk register and attach a test to each line:

  1️⃣ Not authorised to access → an access review of every agent's tools and credentials.

  2️⃣ Resisting instructions → no control that depends on the agent obeying its prompt. Enforce at the tool layer.

  3️⃣ Manipulated through malicious inputs → find agents that read untrusted content, touch sensitive data and can send data out.

  4️⃣ Conceals actions → the record of what the agent did must not come from the agent.

  5️⃣ Impossible to reverse → a named human approves every delete, payment and send, before it happens.

  6️⃣ Third-party agents → evidence from the vendor or your gateway, not a policy statement.

  7️⃣ Not timely detected → a stop drill with a measured time.

  If your company writes a sentence like Apple's this year, the audit committee's next question will be which of these you can show.

  #AIGovernance #AgenticAI #RiskManagement #GRC #CyberSecurity
tools: [agent-access-review, agent-flight-recorder]
image: /assets/img/posts/apple-just-wrote-your-agent-risk-register.png
---

Apple filed its annual report for fiscal 2026 on Tuesday. In the risk factors there's a paragraph that wasn't there a year ago. I downloaded both filings from [SEC EDGAR](https://www.sec.gov/Archives/edgar/data/320193/000032019326000026/aapl-20260926.htm) and counted. The fiscal 2025 10-K mentions "artificial intelligence" 6 times and agents not at all. The fiscal 2026 10-K mentions artificial intelligence 55 times, and agents, agentic systems and concealment all appear for the first time.

The new paragraph says AI agents can take actions on their own, including reaching systems "they may not be authorized to access", altering code, sending communications and completing transactions. It goes on to list how they can misbehave: acting without instruction, exceeding permissions, resisting instructions, getting around security controls, being manipulated through malicious inputs, and hiding what they did. It adds that this behaviour is hard to test and audit, that some consequences can't be reversed, and that Apple's control over third-party agents may be limited.

This isn't a disclosure that something happened at Apple. Risk factors describe what could happen. But risk factors are written and reviewed by some of the most careful lawyers anywhere, and this one is unusually specific. It works as a ready-made checklist of agent risks for any company. Read it as a risk register, and each line needs a control and a way to test that control.

{% include figures.html items=page.figures %}

## 1. "Not authorized to access" and "exceeding permissions"

An agent can only go beyond its permissions if nobody knows what its permissions are. The control is an access review: an inventory of every agent, the tools it can call, the credentials it holds and the person who owns it. It's the same review you'd run on a service account.

**Test:** pick three agents in production. For each one, can you produce a list of what it can reach, and the name of the person who last reviewed that list? [agent-access-review](https://github.com/Mihirajmera/agent-access-review) builds that inventory from MCP client configs and agent manifests.

## 2. "Defying directions or resisting instructions"

This line says something important about where controls belong. If the agent can ignore instructions, then any control written as an instruction ("never delete production data" in a system prompt) is a suggestion. Controls have to sit outside the model: in the permissions the agent holds, and in a policy layer between the agent and its tools that allows, denies or holds each call.

**Test:** list the controls you rely on for each agent. Strike out any that only work if the agent follows its prompt. What's left is your real control set.

## 3. "Manipulated or compromised through malicious inputs"

Prompt injection is mostly a problem when three things combine: the agent reads content an outsider can write, it can reach sensitive data, and it can send data somewhere. Any two are manageable. All three give an attacker a way to steal data just by writing text the agent will read.

**Test:** flag every agent that has all three. agent-access-review reports this combination as AAR-09. Each flagged agent needs one of the three removed, or a documented reason it can't be.

## 4. "Conceal actions, hide, withhold or manipulate information"

This is the line auditors should underline. If the agent might conceal what it did, then the agent's own account of its actions can't be the evidence. The record has to be made by something the agent can't change: a gateway or proxy that sits between the agent and its tools, writing each call to a log that shows any edit after the fact.

**Test:** for one agent, find where its actions are logged. Could the agent, or whoever runs it, change that log without leaving a trace? If yes, you have a log but not evidence. [agent-flight-recorder](https://github.com/Mihirajmera/agent-flight-recorder) records MCP tool calls in a hash-chained, signed log for this reason.

## 5. "Difficult or impossible to reverse"

Apple names deleting data and completing transactions. For those, detection after the fact is too late, so the control has to come first: a named person approves the exact action before it runs. As I wrote on Friday, that approval should be [bound to the exact batch it approves](/blog/approve-the-batch-not-the-request/), so a changed batch needs a new approval.

**Test:** list the irreversible actions each agent can take: deletes, payments, outbound messages, merges to production. Show that each one requires an approval, and that the approver isn't the person the agent acts for.

## 6. "Ability to oversee and control third-party artificial intelligence agents ... may be limited"

Agents built into SaaS products run on someone else's infrastructure, so you can't put your own logging inside them. What you can control is what they connect to, and what you ask the vendor to show you.

**Test:** for each vendor whose product runs agents on your data, do you have the vendor's own evidence of what the agent did (logs, an audit report that covers the agent), or only their policy? If you route their access through your own gateway, the gateway's records count too.

## 7. "May not ... prevent or timely detect such misuse"

The paragraph ends by admitting that policies and controls may not keep up. The way to find out whether yours do is to test them, which is the point of the [stop drill in last week's kill-switch post](/blog/a-kill-switch-youve-never-pulled-is-not-a-control/): stop an agent on purpose, time it, and check that nothing ran after the stop.

**Test:** do you have a measured stop time for your most important agent?

## Why this matters beyond Apple

Once a company describes a risk this precisely in a public filing, the audit committee will ask what's being done about each part of it. Many companies will write their own version of this paragraph in their next annual report. The legal team writes the sentence, but the GRC team will be asked to back it up. Having a test for each line, before the question arrives, is cheaper than building one after.
