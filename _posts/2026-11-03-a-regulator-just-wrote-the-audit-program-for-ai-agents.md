---
title: "A regulator just wrote the audit program for AI agents"
description: Hong Kong's banking regulator published a discussion paper on governing AI agents in banks. It creates no new rules, but almost every section ends with a "practical test" an auditor can run tomorrow. Here are the tests, and what they mean outside banking.
kind: essay
research: true
status: review
evidence:
  hash: HKMA 2026-11-02
  label: Discussion Paper on Agentic AI Governance in the Banking Sector
  url: https://www.hkma.gov.hk/media/eng/doc/key-information/press-release/2026/20261102e3a1.pdf
tags: [AI governance, AI agents, Regulation]
figures:
  - {n: "1", label: "named accountable owner per agent deployment, from the business, not IT", tone: amber}
  - {n: "5", label: "agent failures the HKMA asks whether to treat as reportable incidents", tone: red}
  - {n: "Feb 1", label: "2027 deadline for comments on the paper"}
linkedin: |
  Yesterday, Hong Kong's banking regulator published a 57-page discussion paper on governing AI agents in banks.

  It creates no new rules. But almost every section ends with "the practical test is whether…", and those tests are an audit program you can use tomorrow, in any industry.

  The ones that stood out to me:

  1️⃣ One named owner per agent, from the business, not IT. Accountability "should not default to technology functions solely because agentic A.I. is involved."

  2️⃣ An approval step isn't oversight. It only counts if the approver sees the substance, has time, and treats "reject" as a real option. If agents act faster than people can review, the approval doesn't count.

  3️⃣ Prove you can stop it. Not "is there a kill switch" but does it work fast enough, at real speed, without breaking the business.

  4️⃣ No shared accounts. Each agent gets its own identity, because "the log replaces the memory and signature of a human actor."

  5️⃣ Retire agents properly. A casually decommissioned agent leaves credentials and access behind.

  Comments are open until February 1, 2027. The full post turns each section into a test.

  #AIGovernance #AgenticAI #GRC #RiskManagement #CyberSecurity
image: /assets/img/posts/a-regulator-just-wrote-the-audit-program-for-ai-agents.png
---

Yesterday the Hong Kong Monetary Authority launched Project SAGE, a program for banks to trial AI agents in payments and treasury, and alongside it published a [discussion paper on agentic AI governance in banking](https://www.hkma.gov.hk/media/eng/doc/key-information/press-release/2026/20261102e3a1.pdf).

The paper is careful about its status. It "creates no new obligations" and asks for comments by February 1, 2027. But it's the most concrete regulatory document on AI agents I've read, for one reason: almost every section ends with a sentence starting "the practical test is whether." Those sentences are audit tests. Read together, they're an audit program for AI agents, and almost none of it is specific to banks.

One note on reading it: the paper uses "AI" to mean *authorized institution*, the HKMA's term for a bank, and writes artificial intelligence as "A.I."

{% include figures.html items=page.figures %}

## Five practical tests

### 1. Can you name who answers for each agent?

Before an agent goes into production, the paper wants the bank to write down its "business intent": what it's for, what it can do, which data and tools it can touch, what data can leave the firm, its limits, and when its authority should be withdrawn.

Then one person owns it, and that person should normally come from the business, not technology. The paper is blunt that accountability "should not default to technology functions solely because agentic A.I. is involved." Technology owns the build, the logs and the stop mechanism. A separate control owner, independent of the build, owns testing and challenge.

It also says an agent shouldn't keep running if its owner or boundaries are unclear. That's a stronger line than most companies hold today.

**Test it:** pick five agents in production and ask who owns each one. If the answer is the engineer who built it, or "the platform team," the business has handed its decision to the people who wrote the code.

### 2. Do its actual capabilities still match what was approved?

The paper's answer to prompt injection and scope creep is that prompts are not controls. Critical controls "should not depend solely on a model's ability to interpret and follow instructions." Instead it describes a *harness*: tools, permissions, data access and limits defined in advance, enforced technically, version-controlled and changed only through change management.

The key line for auditors: an agent should not be able to extend its own authority, acquire new tools, create credentials or modify its own controls at runtime. High-impact actions get deterministic checks, ordinary code that verifies the action is within limits and going to an authorized recipient. If a check fails, the action stops or goes to a person. It isn't left to the agent to sort out.

**Test it:** for one agent, compare the tools and permissions it was approved for with what its credentials can actually do today. That's an access review, and the gap between the two lists is the finding. I built [agent-access-review](https://github.com/Mihirajmera/agent-access-review) to do this for MCP servers, and the gap is rarely zero.

### 3. Is the human approval real?

This is my favorite section. "A formal approval step is not, by itself, meaningful human oversight." Approval only counts if the approver sees the substance of the action, has the authority and time to reject it, and treats rejection as a legitimate outcome. If agents act faster or in greater volume than a person can meaningfully review, the bank shouldn't count the approval step as a control at all.

That describes most approval prompts I've seen in agent tooling: a button clicked hundreds of times a day.

**Test it:** pull the approval log for one agent. Count approvals per reviewer per day, the median time to approve, and how many were rejected. A rejection rate of zero with a median of four seconds isn't oversight.

### 4. Can you actually stop it?

Every governance framework mentions a kill switch. This paper asks whether it works. Testing should cover whether the stop takes effect fast enough, what happens to actions already in flight, and whether the business can keep running on the fallback. It should also work "regardless of the status of a vendor."

The practical test is the strongest sentence in the paper: if a bank cannot stop or constrain an agent "without unacceptable disruption, the principle is not met in substance."

**Test it:** ask when the stop mechanism was last exercised in production, how long it took, and who decided. If it has never been run, it is a design document, not a control.

### 5. Can you explain any action it took?

"When software acts, the log replaces the memory and signature of a human actor." So the paper wants every deployment recorded before production: owners, capabilities, data leaving the firm, dependencies, stop mechanism, log locations, change and suspension history.

Two details I hadn't seen in a regulator's text before. Each agent should have **its own identity and credentials**, because shared or borrowed accounts break the link between an action and the authority behind it. That's the failure in the [bank agents story](/blog/the-banks-just-ran-an-access-review-on-ai-agents/) last week, where agents logged in with customers' passwords. And when an agent is **retired**, its record should be closed properly, because "casually decommissioned deployments may leave active credentials" and access behind.

**Test it:** pick one action an agent took last month and trace it: which agent, which credential, which instruction, which person's authority, which approval. Then pick one agent that was switched off and check whether its credentials still work.

## Five incidents worth reporting

The paper also asks whether these should ordinarily count as incidents under existing reporting rules:

1. The agent acts beyond its authority.
2. The stop mechanism or the fallback fails when it's needed.
3. The agent's identity or credentials are compromised.
4. A monitoring agent is found to have failed silently.
5. An approval gate lets an action through that it shouldn't have.

Most incident policies I've read wouldn't classify any of these, because nothing was breached and no data was lost. Number 3 isn't hypothetical either: last month's [run of AI platform breaches](/blog/nine-platforms-one-target-your-ai-keys/) was largely about stolen credentials that agents and applications use.

**Test it:** take that list to your incident classification policy. For each item, would it be logged, triaged and reported, or would it be closed as a bug?

## Why this matters outside Hong Kong

Hong Kong is not the only regulator thinking about this. The UK ICO's call for evidence on agentic AI closes November 20, and NIST has an AI agent standards initiative under way. But this paper goes further than anything I've seen in turning principles into checks, and the checks work in any company that lets software act on its behalf.

If you run AI agents in production, you don't need to wait for a rule. Run the five tests above against your most important agent this month.

## What I haven't covered

This is a summary of a 57-page paper that is explicitly preliminary. I've left out its sections on customer-facing agents, the proposed notification and registry arrangements for material deployments, and "Know Your Agent" checks for agents arriving from outside the bank, each of which deserves its own post. Read the paper itself before relying on anything here.

*Sources: [HKMA discussion paper (PDF)](https://www.hkma.gov.hk/media/eng/doc/key-information/press-release/2026/20261102e3a1.pdf) · [HKMA press release](https://www.hkma.gov.hk/eng/news-and-media/press-releases/2026/11/20261102-4/) · [Caixin Global](https://www.caixinglobal.com/2026-11-02/hong-kong-launches-ai-agent-governance-project-102500128.html).*
