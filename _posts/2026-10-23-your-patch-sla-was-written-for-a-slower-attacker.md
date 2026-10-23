---
title: "Your patch SLA was written for a slower attacker: what PHP2Shell teaches about vulnerability governance in the AI era"
description: AI helped find two critical PHP flaws, and AI helped attackers weaponize them within hours. The 30-day patch window in most compliance programs assumes a world that ended this week.
kind: essay
research: true
status: block
evidence:
  hash: CVE-2026-109618
  label: Amazon Threat Intelligence · exploitation 4 days before disclosure
  url: https://aws.amazon.com/blogs/security/amazon-threat-intelligence-identifies-php2shell-exploitation-prior-to-public-disclosure-in-madpot/
tags: [Vulnerability management, AI-discovered vulnerabilities, Incident analysis]
figures:
  - {n: "4", label: "days between the first exploit attempt and public disclosure", tone: red}
  - {n: "~5h", label: "from leaked details to reported active exploitation, before the patch existed", tone: red}
  - {n: "0", label: "fixed PAN-OS versions a day later: you can't patch PHP inside an appliance", tone: amber}
linkedin: |
  Most compliance programs give you 30 days to patch a critical vulnerability.

  This week, attackers were exploiting PHP2Shell before the patch existed.

  Two critical flaws in PHP, which runs most of the web. AI models helped researchers find and prove them. Then details leaked, and within hours there were "millions" of exploit attempts. Governments took websites offline rather than wait.

  Three lessons for anyone who owns a vulnerability management policy:

  1️⃣ The patch SLA is the wrong control. A 30-day window measures how fast you fix things. It says nothing about what you do in the hours before a fix exists.

  2️⃣ "Patch" isn't always yours to do. PHP is inside firewalls, SIEMs and appliances. A day later, every PAN-OS version was affected with no fix yet. That's third-party risk, not patching.

  3️⃣ You need a pre-approved "take it offline" decision. The FBI and Japan's prime minister both said it out loud this week. Most companies have never decided who's allowed to make that call.

  AI is making exploits cheaper to build. The governance has to assume that.

  Full analysis, timeline and a policy checklist in the first comment 👇

  #VulnerabilityManagement #AISecurity #GRC #CyberSecurity #RiskManagement
image: /assets/img/posts/your-patch-sla-was-written-for-a-slower-attacker.png
---

On October 21, PHP shipped emergency fixes for two critical flaws that, between them, affect every PHP release of the last decade. PHP runs about 70% of the world's websites, according to the AP. By the time the fix was published, attackers were already using the flaws. Within hours there were, in Cloudflare CEO Matthew Prince's words, "millions" of attempts. A day later, government websites in Britain, Finland and Japan had been taken partly offline as a precaution.

The flaws are called PHP2Shell (CVE-2026-109618 and CVE-2026-109619). The story everyone is telling is that **AI found them first**. That's true, and it's good news. But the part that matters for anyone who governs security is the other half: **AI also made them cheap to weaponize**, and almost every vulnerability management policy I've read assumes it's expensive.

{% include figures.html items=page.figures %}

## What happened

The researchers' timeline, from [Wiz](https://www.wiz.io/blog/php2shell-php-rce), [Recorded Future](https://www.recordedfuture.com/blog/php2shell-vulnerability-exploitation) and [Amazon Threat Intelligence](https://aws.amazon.com/blogs/security/amazon-threat-intelligence-identifies-php2shell-exploitation-prior-to-public-disclosure-in-madpot/) (all times UTC):

| When | Event |
|---|---|
| Aug 19 | Wiz Research finds the first vulnerability; unauthenticated code execution against Drupal and WordPress follows within two days |
| Aug 24 | Reported privately to the PHP security team |
| Sep 21 | PHP acknowledges the reports and starts a coordinated fix |
| Oct 17 | Amazon's honeypots record a PHP2Shell exploitation attempt, **four days before disclosure** |
| Oct 20 | PHP announces an out-of-band release for the next day |
| Oct 21, ~02:00 | Details have leaked; the earliest proofs of concept appear |
| Oct 21, 07:34 | Patchstack reports "multiple active exploitation incidents" from hosting partners |
| Oct 21, 13:52 | PHP releases 8.2.35, 8.3.36, 8.4.27 and 8.5.12 |
| Oct 21–22 | "Millions" of exploit attempts; the FBI advises taking sites offline if they can't be updated immediately |
| Oct 22 | Palo Alto says every PAN-OS and Panorama version is affected, with no fixed release yet; Cisco and Fortinet list dozens of products under investigation |

The bugs themselves are memory-safety flaws in how PHP cleans up after a request fails partway through, for example when it runs out of memory. Corrupted state can survive into the next request on the same worker, and a remote attacker with no account can turn that into code execution. Wiz says the flaws had been present for years; what was missing was a practical way to exploit them.

**That's where AI changed the economics.** Wiz says frontier models helped find the bug, build the exploit, and adapt it to different PHP versions and memory layouts, which "shortened exploit development from months to hours." OpenAI, which coordinated the disclosure through its Patch the Planet initiative, said AI appeared to find the flaws before any attacker did. Amazon's post makes the uncomfortable corollary explicit: AI-assisted analysis makes it cheaper to turn a patch diff or an advisory into a working exploit, so more actors can act within hours or minutes of disclosure.

The defenders had a two-month head start. It shrank to hours when the details leaked, and it would have shrunk to hours anyway the moment the patch was public.

## Why this one is different

### The race was lost before the patch existed

Every vulnerability management policy is built around one event: **the vendor releases a fix**. The clock starts there. "Critical: remediate within 30 days" or, for the most aggressive programs, 14 or 7 days.

In this case, exploitation started four days before that event, according to Amazon, and was widespread on the day of it. A policy that starts the clock at patch release had nothing to say about the period when the risk was highest. No SLA was breached. Every organization was "compliant" while it was being attacked.

### "Patch" assumes the code is yours

The PHP Foundation fixed PHP in about two months. That fixes PHP on servers where you install PHP. It doesn't fix the PHP inside your firewall's management interface, your SIEM, your load balancer or your vendor's SaaS platform.

A day after disclosure, according to [Help Net Security](https://www.helpnetsecurity.com/2026/10/22/php2shell-vulnerability-fortinet-cisco-palo-alto-networks/), Palo Alto listed every PAN-OS and Panorama version as affected with no fixed release yet. Fortinet had 12 products under investigation. Cisco had 18 products and 13 cloud services under investigation, and said there were no workarounds. Your 30-day SLA can't start until those vendors ship, and you don't control when that is.

This is where vulnerability management quietly becomes third-party risk management. The question isn't "how fast do we patch?" It's "which of our vendors have PHP inside, and what have they told us?" Most companies can't answer that today, because they don't have software bills of materials (SBOMs) from their appliance vendors, or don't read the ones they have.

### Most of the exposure can't be patched at all

Scans quoted by Recorded Future found about 5.1 million IP addresses running PHP. Of the roughly 1.1 million that disclose a version, about 758,000 run branches that are end-of-life: PHP 8.1 and older, which get no official fix. For those, the remediation isn't a patch. It's a migration project, and it was overdue before this week.

End-of-life software usually sits in a risk register as an accepted risk with a note like "no known exploitable vulnerabilities." That sentence expired on October 21.

## What would have helped, ranked by cost

**Policy changes (cost: a meeting and a signature):**

1. **Add a "pre-patch" tier to the vulnerability policy.** For critical, internet-facing, actively exploited flaws, the policy should require *mitigation* within hours, whether or not a patch exists: WAF rules, restricting access, disabling the affected feature or taking the service offline. Amazon's advice was to measure these timelines "in hours, not days or weeks."
2. **Pre-approve the decision to go offline.** The FBI recommended it. Japan's prime minister said suspending websites was an option. Britain's prime minister's office took some services offline. Inside a company, that decision usually needs a business owner, and at 3 a.m. nobody knows who it is. Name the role, the criteria and the maximum outage in advance, so the incident team doesn't have to find a vice president.
3. **Start investigations from first exploitation, not from disclosure.** Amazon's advice was to look back to October 17. If your incident procedure says "review logs since the advisory," you'll miss the four days that matter.

**Inventory (cost: weeks, then continuous):**

4. **Know where the runtime is, not just the application.** "Do we run WordPress?" is the wrong question. "Where does PHP execute, including inside products we bought?" is the right one. Container images, managed hosting and appliances all count.
5. **Ask vendors for SBOMs and read them.** Then, when the next runtime-level flaw lands, the third-party risk team can send targeted questions within the hour instead of a generic questionnaire within the month.
6. **Put end-of-life software on a funded plan, not an exception.** An exception without an expiry date is a decision not to decide.

**Architecture (cost: real, but already justified):**

7. **Never expose management interfaces to the internet.** Palo Alto's main mitigation was to restrict management access to trusted internal addresses. If that was already true, the firewall issue was a low-priority patch, not an emergency.
8. **Make origins unreachable except through the WAF.** A virtual patch at the edge does nothing if the server behind it has a public address. Recorded Future called this out explicitly.
9. **Detect behavior, not CVEs.** Repeated out-of-memory errors, PHP worker churn and web servers spawning shells look the same whatever the next CVE number is.

## If you run PHP

Update to **8.5.12, 8.4.27, 8.3.36 or 8.2.35**. PHP says configuration changes don't fully close both flaws, so treat any mitigation as temporary. If you're on 8.1 or older, use your OS vendor's backported package or move to a supported branch. Check appliances and SaaS vendors separately, and review logs from **October 17** onward, not from the advisory. [watchTowr's FAQ](https://watchtowr.com/intelligence/php-cve-2026-109618-faq/) and [Amazon's post](https://aws.amazon.com/blogs/security/amazon-threat-intelligence-identifies-php2shell-exploitation-prior-to-public-disclosure-in-madpot/) have the detection guidance.

## What this means for AI governance

AI governance usually means governing the AI you build or buy. PHP2Shell is a reminder that it also means governing **for** an environment where everyone, including attackers, has AI.

That has two consequences for a control framework.

**First, the good news is real.** AI models found flaws that had sat in critical infrastructure for years, and the industry got a two-month head start to coordinate a fix. OpenAI is now proposing a framework for handling AI-discovered vulnerabilities and has asked the security community to critique it. That's the right instinct: when finding bugs gets cheap, disclosure processes designed for a few dozen critical bugs a year will be overwhelmed.

**Second, the assumptions behind our timelines are out of date.** Patch SLAs, exception approvals and risk acceptances all carry an unstated assumption about how long it takes an attacker to go from "a flaw exists" to "a flaw is exploited." For PHP2Shell, the gap was measured in hours, and in at least one case it was negative.

Three questions every security and risk program should be able to answer after this week:

1. **What does our policy require before a patch exists?** If the answer is "nothing," the policy covers the safe part of the timeline and skips the dangerous one.
2. **Which of our vendors would we have to call, and how fast would we know?** If the answer depends on a questionnaire, it's too slow.
3. **Who is allowed to take a service offline, and on what criteria?** If nobody knows, the decision will be made late, or not at all.

The patch arrived two months after the bug was reported, and AI deserves credit for that head start. The exploits arrived before the patch, and AI deserves some credit for that too. Policies that start the clock at patch release are measuring the wrong race.

*Sources: [Wiz Research](https://www.wiz.io/blog/php2shell-php-rce) · [Amazon Threat Intelligence](https://aws.amazon.com/blogs/security/amazon-threat-intelligence-identifies-php2shell-exploitation-prior-to-public-disclosure-in-madpot/) · [Recorded Future](https://www.recordedfuture.com/blog/php2shell-vulnerability-exploitation) · [watchTowr](https://watchtowr.com/intelligence/php-remote-code-execution-php2shell/) · [AP via PBS NewsHour](https://www.pbs.org/newshour/nation/ai-discovered-a-software-vulnerability-that-could-impact-70-of-websites-worldwide-the-rush-is-on-to-patch-it) · [Help Net Security](https://www.helpnetsecurity.com/2026/10/22/php2shell-vulnerability-fortinet-cisco-palo-alto-networks/) · [Fortune](https://fortune.com/2026/10/21/ai-tools-discovered-the-php-vulnerability-that-could-take-down-70-of-the-internet-now-the-race-is-on-to-patch-it-before-ai-powered-hackers-attack/). Vendor fix status is changing daily; check each vendor's advisory. Exposure counts are scan results, not confirmed vulnerable hosts. Times are UTC.*
