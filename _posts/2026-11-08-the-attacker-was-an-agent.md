---
title: "The attacker was an agent. Your risk register should say so."
description: "Spain's data protection authority received the first GDPR breach notification for an attack carried out by an AI agent. Its advice was that a generic 'unauthorised access' line in a risk analysis is no longer enough. Here's what to change in the risk entry, the response plan and the logs."
kind: essay
research: true
status: review
evidence:
  hash: AEPD blog 2026-09-14
  label: First notification of a personal data breach caused by an attack executed with an AI agent
  url: https://www.aepd.es/prensa-y-comunicacion/blog/primera-notiviacion-brecha-datos-personales-causada-por-ataque-ejecutado-mediante-agente-ia
tags: [Incident response, Data protection, AI-enabled attacks]
figures:
  - {n: "1", label: "first breach notification to Spain's AEPD for an attack run by an AI agent"}
  - {n: "72h", label: "to notify the regulator under GDPR Article 33, however fast the attack was", tone: amber}
  - {n: "4", label: "changes the AEPD says organisations should make", tone: red}
diagram:
  type: flow
  caption: the attack as the AEPD describes it, and the control to test at each step
  steps:
    - {id: S-01, label: Searches generic files, sub: looking for vulnerabilities, test: "what's exposed?", state: info}
    - {id: S-02, label: Logs in successfully, sub: a valid login, not a forced one, test: "would this login look odd?", state: warn}
    - {id: S-03, label: Probes the application, sub: autonomously finds a flaw, test: app-layer detection, state: warn}
    - {id: S-04, label: Modifies personal data, sub: and opens invoices, test: "which records changed?", state: fail}
    - {id: S-05, label: Breach notified, sub: GDPR Article 33, test: 72 hours, state: info}
linkedin: |
  Spain's data protection authority (AEPD) received the first GDPR breach notification for an attack carried out by an AI agent.

  What the agent did, per the AEPD: it searched files for vulnerabilities, logged in successfully, then probed the application on its own until it could modify personal data and open invoices.

  None of those steps is new. What's new is that one tool chained them together without a person driving each step.

  The AEPD's advice is practical, and it maps to four changes:

  1️⃣ The risk analysis. A generic "unauthorised access" entry isn't enough. Name AI-run attacks, and re-rate how likely, how fast and how wide they are.

  2️⃣ Response times. A plan built for a person typing commands is too slow for an attacker that tries many routes at once.

  3️⃣ Credentials. An agent with one over-permissioned account or API key can reach many services before anyone notices.

  4️⃣ Machine-speed containment. People still decide, but the first containment step can't wait for a meeting.

  I'd add a fifth: the agent changed data. To notify the right people within 72 hours, you need to know which records it changed. That means record-level change logs, before the incident.

  #DataProtection #GDPR #IncidentResponse #AIGovernance #CyberSecurity
image: /assets/img/posts/the-attacker-was-an-agent.png
---

On September 14, Spain's data protection authority, the AEPD, [published a short post](https://www.aepd.es/prensa-y-comunicacion/blog/primera-notiviacion-brecha-datos-personales-causada-por-ataque-ejecutado-mediante-agente-ia) about a first. It had received a breach notification where the attack was carried out by an AI agent using a well-known language model.

The AEPD's description is brief. The agent searched generic files for vulnerabilities and logged in successfully. Once inside, it looked for weaknesses in the application on its own, and when it found one, it modified personal data and accessed invoices. The organisation, the sector and the model weren't named. The AEPD was careful to say that using a particular model doesn't mean the model or its provider was compromised, and that its account comes from the organisation's notification, which it still has to analyse.

It's one incident, and the AEPD says it doesn't show a trend. I've come back to it two months later because its advice is the most practical any regulator has given on agent-run attacks, and most risk registers I've seen haven't caught up.

{% include figures.html items=page.figures %}

## Nothing new, except who did it

Every step in that attack is familiar: reconnaissance, a valid login, finding an application flaw, changing data. A competent person could do all of it. The AEPD's point is that AI doesn't create new threats, but it increases the speed, scale and adaptability of known ones. An agent can be given a goal, plan the steps, use tools, read the results and change course without anyone directing each move.

That changes three numbers in a risk assessment without changing the threat's name: how likely the attack is, because it's cheaper to run; how fast it moves from login to damage; and how wide it spreads, because one agent can try many systems at once.

## The four changes the AEPD asks for

The AEPD lists four ways this notification changes risk management. Each one turns into something you can check.

**1. Name it in the risk analysis.** The AEPD says a generic reference to malware, phishing or unauthorised access isn't enough, because automation can substantially change the likelihood, speed and reach of an incident.

In practice that means splitting one line into two. Keep the existing entry for a person attacking you. Add one for an agent-run attack on the same system, with a higher likelihood, a shorter time from first access to impact, and a wider scope. Then check whether the controls listed against it still hold at that speed.

**Test:** for your most important personal-data system, does the risk analysis mention attacks carried out by AI? If the entry predates 2026, it almost certainly doesn't.

**2. Review response times.** Procedures designed for attacks run by hand may be too slow when an agent probes many assets and access routes at the same time. I made the same argument about [patch deadlines written for a slower attacker](/blog/your-patch-sla-was-written-for-a-slower-attacker/). The same applies to detection and containment.

**Test:** take your last real incident. How long was it from the first alert to containment? Compare that with how long an agent would need to get from a valid login to changing data. If the first number is in hours and the second in minutes, the plan needs to change.

**3. Treat credentials as the perimeter.** The attack in Spain started with a *successful* login. The AEPD notes that an agent holding an account, an API key or a token with excessive permissions can reach different services at machine speed before anyone notices.

**Test:** for each system holding personal data, list the accounts and keys that can write to it. Are any shared, unused, or broader than their job needs? This is an ordinary access review, but it's now the main defence, not a box ticked once a year.

**4. Contain at machine speed.** The AEPD is clear that human oversight is still essential, but it has to be backed by detection, containment and response that work fast enough. The practical version is a short list of containment steps that are approved in advance and run automatically: disable the account, revoke its sessions, block the token. A person then decides what happens next.

**Test:** which containment steps can run without waiting for someone to approve them? If the answer is none, the person approving them sets the pace of your response, however fast the attacker is.

## A fifth: know which records changed

The AEPD's list is about preventing and stopping the attack. The notification itself adds a problem the list doesn't cover. This agent didn't only read data, it *changed* it. Under GDPR that's an integrity breach, and you have 72 hours to notify the regulator. If the risk to individuals is high, you also have to tell them.

To do that you need to know which records were changed, and from what to what. Many applications log logins and errors but not field-level changes to the data. Then the honest answer to "which customers were affected?" is "possibly all of them", which makes for a much larger notification and much more work to restore the data.

**Test:** pick one table of personal data. Could you list every record changed in a given hour last week, with the account that changed it and the old value? If not, add that logging now. After an incident it's too late.

## The same basics, faster

The AEPD ends where most good guidance ends: the basics still decide the outcome. Know what personal data you process, keep less of it, limit access, fix vulnerabilities, control your suppliers, and be ready to respond. What's changed is how fast each of those has to work.
