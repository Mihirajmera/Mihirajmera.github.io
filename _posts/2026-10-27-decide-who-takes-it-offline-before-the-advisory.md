---
title: "Decide who takes it offline before the advisory lands"
description: PHP2Shell was exploited four days before disclosure, and some vendors still had no fix a day after it. The decisions that mattered that week can't be made well in the moment. Here are three to write down per system now, with a one-row template.
kind: essay
research: true
status: review
evidence:
  hash: Amazon MadPot 2026-10
  label: PHP2Shell exploited before public disclosure
  url: https://aws.amazon.com/blogs/security/amazon-threat-intelligence-identifies-php2shell-exploitation-prior-to-public-disclosure-in-madpot/
tags: [Vulnerability management, Incident response, Third-party risk]
figures:
  - {n: "4", label: "days of exploitation Amazon saw before PHP2Shell was disclosed", tone: red}
  - {n: "0", label: "fixed PAN-OS versions the day after disclosure", tone: amber}
  - {n: "3", label: "decisions to write down per system before the next advisory"}
linkedin: |
  The hardest call during PHP2Shell wasn't technical. It was "who is allowed to take this site offline?"

  Last week the FBI advised taking unpatchable PHP sites offline. Government sites in the UK, Finland and Japan went partly dark. And somewhere, a lot of teams spent hours finding out who could actually say yes.

  After my post on patch SLAs, the comments pushed me to write down what should be decided before the next advisory, not during it:

  1️⃣ Per system: who can take it offline, who must be told, and what customers hear. Outage runbooks cover things breaking. They don't cover choosing to switch something off.

  2️⃣ A list of which vendor products embed PHP (and OpenSSL, and log4j). Palo Alto said every PAN-OS version was affected with no fix. If you already know which appliances embed the runtime, the vendor questions go out the same day.

  3️⃣ The clock starts at disclosure, not at "patch available." The first deadline is a compensating control within hours, with an owner and an expiry, tested to prove it blocks. Then look back: Amazon saw exploitation four days before disclosure.

  The full post has a one-row template you can copy per system.

  Which of the three does your team already have written down?

  #VulnerabilityManagement #IncidentResponse #ThirdPartyRisk #GRC #CyberSecurity
image: /assets/img/posts/decide-who-takes-it-offline-before-the-advisory.png
---

Last week I wrote that [your patch SLA was written for a slower attacker](/blog/your-patch-sla-was-written-for-a-slower-attacker/). The replies were better than the post. One reader argued for moving from checkbox compliance to continuous, risk-based exposure management. Answering them made me realise the real gap wasn't the SLA. It was the three decisions nobody had made in advance.

## What the week looked like

A quick recap, all from the sources in the earlier post:

- **Oct 17:** Amazon's honeypots saw PHP2Shell exploitation, [four days before public disclosure](https://aws.amazon.com/blogs/security/amazon-threat-intelligence-identifies-php2shell-exploitation-prior-to-public-disclosure-in-madpot/).
- **Oct 21:** details leaked and PHP shipped fixed releases the same day ([Wiz](https://www.wiz.io/blog/php2shell-php-rce)).
- **Oct 21–22:** the FBI advised taking sites that couldn't be patched offline, and some government sites in the UK, Finland and Japan went partly offline ([Recorded Future](https://www.recordedfuture.com/blog/php2shell-vulnerability-exploitation)).
- **Oct 22:** Palo Alto said every PAN-OS version was affected with no fix yet, and Fortinet and Cisco had dozens of products under investigation ([Help Net Security](https://www.helpnetsecurity.com/2026/10/22/php2shell-vulnerability-fortinet-cisco-palo-alto-networks/)).

Two things in that list can't be fixed by patching faster. Exploitation started before anyone could patch, and for some appliances there was nothing to patch with.

## Decision 1: who can take it offline

When the FBI says "take it offline," someone has to decide that for each system. In most companies that person isn't written down anywhere.

An outage runbook usually covers the service breaking. It rarely covers choosing to break it yourself. So the call gets made in a meeting, under pressure, by whoever is senior enough and awake. Then comes a second round of delay: legal, comms and the business owner each find out separately.

Write it down per system before you need it:

- **Who can approve taking it offline.** One name, plus a deputy, both reachable out of hours.
- **Who must be told.** The business owner, the customer-facing teams, and legal if contracts have uptime terms.
- **What customers hear.** A pre-approved holding message, so comms isn't drafting from scratch at 2 a.m.
- **The longest acceptable outage.** If it's two hours, you already know an all-day shutdown needs a different answer.

This is a risk-acceptance decision made in advance, which is exactly what GRC teams are meant to own.

## Decision 2: which vendors embed the runtime

"Patch PHP" assumes you own the PHP. On a firewall, VPN or appliance, the vendor owns it and you wait.

What you can control is how fast you ask. Keep a list of which vendor products embed common runtimes and libraries: PHP, OpenSSL, log4j, glibc. Your SBOM requests and vendor questionnaires should already hold most of this. When the advisory lands, the email to each affected vendor goes out the same day, asking whether they're affected, when a fix is coming, and what mitigation to use until then.

A vendor that can't answer within a day is telling you something too. Record it in your third-party risk file, because next renewal is the time to raise it.

## Decision 3: the clock starts at disclosure

Most patch SLAs start counting when a patch is available. PHP2Shell shows why that's the wrong starting point. For PAN-OS there was no patch, so the clock never started, while attackers were already working.

Start the clock at disclosure. The first deadline isn't "patched." It's "a compensating control in place within hours." That could be a WAF rule, restricting access to the management interface, or taking the service offline (see decision 1). Each compensating control needs three things:

- **An owner**, so someone is accountable for removing it.
- **An expiry**, so a temporary rule doesn't quietly become permanent.
- **Proof it works.** Send a safe test request and confirm it's blocked. An untested WAF rule is a guess.

Then look back. Amazon saw exploitation four days before disclosure. Patching on day one doesn't tell you whether someone got in on day minus four. Search your logs from before the disclosure date, not just after.

## A one-row template

Copy this per internet-facing system. It takes about ten minutes each and makes the next bad week shorter.

| Field | Example |
|---|---|
| System | Customer portal (`portal.example.com`) |
| Can approve taking it offline | Head of Platform; deputy: on-call engineering manager |
| Must be told | Product owner, support lead, legal (SLA terms) |
| Customer message | Pre-approved status-page text, stored in the comms runbook |
| Longest acceptable outage | 4 hours |
| Embedded runtimes | PHP 8.3 (app); OpenSSL via load balancer appliance |
| Vendor contact for advisories | Appliance vendor PSIRT address and account manager |
| Default compensating controls | WAF virtual patch; restrict admin paths to VPN |
| Log retention for look-back | 90 days in SIEM |

## What I haven't tested

This is a proposal, not a measured result. I haven't run this template through a real incident, and the right maximum outage and approvers will differ by company. The FBI advice and government shutdowns are as reported by Recorded Future; I haven't independently confirmed which sites went offline or for how long.

Thanks to the readers whose comments on the last post shaped this one.
