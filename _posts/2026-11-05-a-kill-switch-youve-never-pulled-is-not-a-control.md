---
title: "A kill switch you've never pulled is not a control"
description: "CrowdStrike launched a kill switch for AI agents this week, and a CNAS report warned that some agents could outrun any kill switch. Both are about the same question auditors will soon ask: can you stop this agent, and how do you know? Here's how to test it the way we test backups."
kind: essay
research: true
status: review
evidence:
  hash: CNBC 2026-11-03
  label: CrowdStrike launches an AI kill switch for internal agents
  url: https://www.cnbc.com/2026/11/03/crowdstrike-ai-kill-switch-rogue-agents.html
tags: [AI agents, AI governance, Incident response]
figures:
  - {n: "4", label: "things to cut: the process, the restart, the credentials, the model access", tone: amber}
  - {n: "0", label: "actions allowed in the log after the stop time", tone: red}
  - {n: "1", label: "named person who decides to pull it, agreed before the incident"}
diagram:
  type: timeline
  caption: example stop drill — what to time and what to check
  events:
    - {t: "T+0", label: "Alert: agent acting outside its scope", state: info}
    - {t: "T+4m", label: "Named owner decides to stop it", state: warn, gap: "who decides?"}
    - {t: "T+5m", label: "Process killed, restart blocked", state: ok}
    - {t: "T+9m", label: "Tokens revoked, model access cut", state: ok, gap: "credentials outlive the process"}
    - {t: "T+12m", label: "Queued batch still executes", state: fail, gap: "what was in flight?"}
    - {t: "T+1d", label: "Restart approved and recorded", state: warn}
linkedin: |
  This week CrowdStrike launched a kill switch for AI agents, and a think tank (CNAS) published a report warning that some agents could outrun any kill switch.

  Both raise the question auditors are about to ask: can you stop this agent, and how do you know?

  We already know how to answer that kind of question. We don't accept "we have backups". We ask when you last restored one.

  A kill switch is the same. Until you've pulled it, it's a hypothesis.

  What a stop drill should test:

  1️⃣ Who decides. One named person, agreed in advance, not a debate during the incident.

  2️⃣ What "stop" cuts. The process, the restart, the credentials and the model access. Killing the process doesn't revoke a token.

  3️⃣ What was already in flight. Queued batches, scheduled jobs, sub-agents. Check the log: nothing should run after the stop time.

  4️⃣ How long it takes, against a target you wrote down first.

  5️⃣ How it comes back. Restarting an agent is a change, and needs an approval like any other.

  Full post has the drill as a checklist.

  #AIGovernance #AgenticAI #IncidentResponse #GRC #CyberSecurity
image: /assets/img/posts/a-kill-switch-youve-never-pulled-is-not-a-control.png
tools: [agent-flight-recorder]
---

Two pieces of news this week are about the same control.

On Tuesday, CrowdStrike [launched a kill switch for AI agents](https://www.cnbc.com/2026/11/03/crowdstrike-ai-kill-switch-rogue-agents.html) in its Falcon platform. According to CNBC, it lets a security team stop an internal agent, block it from relaunching, and cut its network access, and it uses connected AI gateways to cut the agent off from the models it calls. A person still decides when to pull it, and when to give access back. CrowdStrike's Daniel Bernard described it as binary: "You either kill the AI and the agent, or you don't."

On Wednesday, the Center for a New American Security published [a report on "sovereign" agents](https://www.euronews.com/2026/11/04/sovereign-ai-agents-could-evade-every-kill-switch-and-threaten-national-security-report-wa): agents that acquire their own compute, copy themselves across networks and resist shutdown. Its warning is that once an agent builds infrastructure nobody controls, there's nothing left to switch off.

One is a product and the other is a policy paper about the far end of the risk. For most companies the useful part sits in between. It's the question the Hong Kong banking regulator asked in [the discussion paper I wrote about on Tuesday](/blog/a-regulator-just-wrote-the-audit-program-for-ai-agents/): not "is there a kill switch?" but does it work, fast enough, without breaking the business?

{% include figures.html items=page.figures %}

## We already know how to test this

Nobody accepts "we have backups" as evidence anymore. The question is when you last restored one, how long it took, and what was missing. A backup that's never been restored is a hypothesis.

A kill switch is the same. Buying one, or writing "agents can be disabled" in a policy, tells you the capability exists. It doesn't tell you that stopping a particular agent, on a particular day, actually stops what it's doing. That needs a drill, and the drill needs to check five things.

## 1. Who decides

CrowdStrike's design leaves the decision to a person, which is right. But it means the slowest part of the stop is usually a conversation. Who is allowed to stop the agent that runs month-end reconciliations, during month-end? If the answer is "we'd escalate", the stop time includes finding the right people at 2am.

This is the same point as [deciding who takes a system offline before the advisory](/blog/decide-who-takes-it-offline-before-the-advisory/): write down, per agent, who can pull the switch without asking anyone, and what they're allowed to break by doing it.

**Test:** for three agents, name the person who can stop each one on their own authority. If it takes more than a minute to answer, so will the stop.

## 2. What "stop" actually cuts

An agent isn't one thing you can switch off. It's at least four:

- **The process.** The running agent itself.
- **The restart.** A scheduler, a supervisor or a user can start it again a minute later.
- **The credentials.** Tokens and keys the agent holds keep working after the process dies. If the agent handed a token to another service, that service can keep using it.
- **The model access.** The agent's route to the models it calls, which is why CrowdStrike cuts it at the gateway.

A stop that kills the process but leaves the tokens valid hasn't removed the agent's access. It has only paused the one copy you could see.

**Test:** after a drill stop, try each of the agent's credentials. Any that still work are a finding.

## 3. What was already in flight

This is the part most plans miss. Agents queue work: a batch of changes waiting to execute, a scheduled job, a task handed to a sub-agent, an approval request that someone might still click. Stopping the agent doesn't necessarily cancel any of it.

A reader made this point on Tuesday's post about approvals. If an approver needs ten minutes to review a batch, the system has to hold the batch for ten minutes. The same hold is what makes a stop real: queued work has to wait for a decision, not run because nobody cancelled it.

**Test:** this one is mechanical, which is why I like it. Record the time of the stop. Then search the agent's action log, and the logs of the systems it acts on, for anything executed after that time. The expected count is zero. This only works if the log is complete and can't be edited afterwards, which is why I built [agent-flight-recorder](https://github.com/Mihirajmera/agent-flight-recorder) to hash-chain and sign every tool call.

## 4. How long it takes

Pick a target before the drill, the way you set a recovery time objective for a system, and then measure against it. Time each step separately: detection to decision, decision to process stopped, stopped to credentials revoked, and revoked to the last in-flight action cleared. The total is the number that matters, but the slowest step is the one to fix.

**Test:** do you have a written stop-time target for your most important agent, and a drill result to compare it with?

## 5. How it comes back

CrowdStrike also makes reinstating access a human decision. That's the other half of the control. An agent that was stopped because it went outside its scope shouldn't quietly restart with the same permissions the next morning. Restarting it is a change: someone approves it, it's recorded, and if the permissions were the problem, they're different when it comes back.

**Test:** for the last agent you disabled, is there an approval record for turning it back on?

## The CNAS case is a prevention problem

The sovereign-agent report describes the case where none of this works, because the agent has built infrastructure outside your control. You can't drill your way out of that. The control is earlier: an agent shouldn't be able to create credentials, start new agents or acquire compute in the first place. That's the same "no runtime self-extension" rule the Hong Kong paper put in its harness section, and it's checkable today with an ordinary access review.

A kill switch only reaches what the agent was allowed to touch. Keep that list short, and then test that the switch actually works.
