---
title: "Nine platforms, one target: the AI keys you handed them"
description: Wiz counts nine breaches of AI developer platforms in October, ending with Northflank telling customers to assume every environment variable was decrypted. There's no single vulnerability behind them. The common thread is what attackers came for, and the controls that decide how much it costs you are on your side, not the vendor's.
kind: essay
research: true
status: review
evidence:
  hash: Wiz 2026-10
  label: Black October for AI Developer Platforms
  url: https://www.wiz.io/blog/black-october-for-ai-developer-platforms
tags: [Third-party risk, Secrets management, AI supply chain]
figures:
  - {n: "9", label: "AI developer platforms breached in October, by Wiz's count", tone: red}
  - {n: "30 min", label: "from reported credential access to the first model call on a stolen key", tone: red}
  - {n: "$100k+", label: "of model usage Wiz estimates from just two stolen enterprise keys", tone: amber}
linkedin: |
  On Friday, Northflank told its customers: "Assume all environment variables have been decrypted."

  It was the ninth AI developer platform breached in October, by Wiz's count. Railway, OpenCode, Warp, Lightning AI, Fireworks AI and others all had incidents.

  Wiz found no single vulnerability linking them. What links them is the target: the AI API keys and cloud credentials customers had stored on the platform.

  Three things stood out to me, reading it as an auditor:

  1️⃣ Abuse starts fast. In both cases Wiz traced, the first model call on a stolen key came within 30 minutes of the reported credential access. That's well before most customers read a status page.

  2️⃣ The key's own policy shaped the bill. One stolen Bedrock key allowed global cross-region inference, and Wiz says only about 6% of the attacker's calls were throttled. Two keys, $100k+ in usage.

  3️⃣ Most of these platforms were never in a vendor inventory. A developer signs up with a card and pastes in the production keys.

  You can't fix the vendor's breach. You can decide how much it costs you. The full post has a test for each.

  #AISecurity #ThirdPartyRisk #SecretsManagement #GRC #CyberSecurity
image: /assets/img/posts/nine-platforms-one-target-your-ai-keys.png
---

On Friday, Northflank's status page told customers to "assume all environment variables have been decrypted" and to rotate every key, after Wiz alerted it to an attack that morning. Within hours, customers were reporting that their AI API keys were being used by someone else.

Northflank was the ninth. Wiz's write-up, [Black October for AI Developer Platforms](https://www.wiz.io/blog/black-october-for-ai-developer-platforms), counts nine breaches of platforms that developers use to build and run AI applications, all in one month. Wiz is clear that "no single vulnerability or dependency" links them. The pattern is in what the attackers wanted: stored environment variables, especially the ones that grant access to AI models.

{% include figures.html items=page.figures %}

## The month, in one table

From Wiz's summary, with each company's own description of the cause where it gave one:

| Date | Platform | Cause, as described |
|---|---|---|
| Oct 6 | Fireworks AI | Credential access |
| Oct 9 | Andromeda | Part of an "industry-wide attack" |
| Oct 14 | Zeabur | Credential access; the company is shutting down |
| Oct 15 | Lightning AI | Credential access |
| Oct 16–17 | OpenCode | A "legacy system" |
| Oct 20 | Railway | "Privilege escalation in our build infrastructure" |
| Oct 23 | Warp | A third-party vendor |
| Oct 28 | CommandCode | Not described |
| Oct 30 | Northflank | Not yet disclosed |

This isn't one bug to patch. It's a category of vendor, the platform that holds your secrets so your code can run, being worked through one at a time.

## What happens to a stolen AI key

Wiz traced two enterprise keys that were stolen in these breaches and then abused on Amazon Bedrock:

- In both cases, the first model call came **within 30 minutes** of the reported credential access.
- **Case A:** about 800,000 calls over roughly 30 hours; three quarters of the successful calls went to Opus models. The key's policy allowed global cross-region inference, and Wiz says only about 6% of calls were throttled.
- **Case B:** about 1.7 million calls over 13 hours from a single address. This key was limited to US inference profiles, so calls outside that were throttled.
- Together, Wiz estimates they "likely ran up over $100k in usage" at list price.

Wiz also linked the key testing to services that resell access to AI models. A stolen AI key is easy to turn into money, which is why these keys were the target.

## Four controls on your side of the breach

You can't stop your hosting provider being breached. You can decide what it was holding, how long it stays useful, and how quickly you notice.

### 1. Know which vendors hold your keys

Most of these platforms are adopted the same way: a developer signs up with a company card, connects the repo, and pastes production keys into the environment settings. The vendor never goes through procurement, so it never appears in the vendor inventory, and nobody receives the breach notice.

**Test it:** pick your three most-used AI provider keys (Anthropic, OpenAI, Bedrock or whichever you use). For each one, list every place it is stored. Then check how many of those places are in your vendor inventory. If you can't answer the first question, the second one doesn't matter yet.

### 2. Limit what a stolen key can do

The two Bedrock cases are the clearest lesson in the report. The same kind of key, stolen the same way, but the one with the broader policy let the attacker spread across regions with little throttling.

Least privilege applies to AI keys like any other credential: restrict the models, the regions and the spend, and give each platform its own key rather than one shared key everywhere. Better still, use short-lived credentials through workload identity federation where the platform supports it, so there is no long-lived secret for a breach to take.

**Test it:** for each AI key stored on a third-party platform, write down which models and regions it can use, and what its spending limit is. A key with no limits is a blank check held by your vendor.

### 3. Detect use, not just disclosure

Thirty minutes from theft to first use means the vendor's status page is not your alert. Northflank's first instruction to rotate came about two hours after Wiz's alert, and that was a fast response.

The signal you control is usage: model calls from new addresses, a jump in volume, calls to models your application never uses. For most teams the first place that shows up is the bill.

**Test it:** if one of your AI keys made 800,000 calls overnight, who would be told, and when? If the answer is "finance, at month end," make spend and usage alerts a security control with an owner, not a billing setting.

### 4. Rotation is the control you'll need, so practice it

Every platform in the table gave the same advice: rotate everything. Northflank had to ship rotation for its own database add-ons, one type at a time, over two days.

This is the same lesson as [the LiteLLM key](/blog/deleting-the-commit-didnt-revoke-the-key/) and [last week's extension backdoor](/blog/could-you-name-the-laptops-that-installed-it/). The incident is a rotation exercise, run under pressure, with whatever process you already have.

**Test it:** time a full rotation of the secrets on one platform: revoke at the provider, issue new ones, update the workloads, confirm the old ones fail. If it takes days, that's how long a stolen key keeps working.

## What to ask these vendors

For any platform that stores secrets for you:

1. Who and what can decrypt our environment variables, and where are the keys held?
2. Can we reference secrets from our own secret manager, or use short-lived federated credentials, instead of storing them with you?
3. Do you offer audit logs of secret access? (Northflank turned them on for all customers *after* the breach.)
4. How fast will you tell us, and will you tell us which of our secrets were exposed?

## What I haven't verified

Wiz's list relies on each company's public statements, and several causes are still preliminary. Northflank hasn't published a root cause yet; its latest update, on November 2, says it believes the attack was contained within an hour, that running workloads weren't accessed, and that a root cause analysis will follow. I haven't seen any of the investigations directly.

*Sources: [Wiz, Black October for AI Developer Platforms](https://www.wiz.io/blog/black-october-for-ai-developer-platforms) · [Northflank status page](https://status.northflank.com/cmvv0rn5a092f14rutwccodpp) · [BleepingComputer](https://www.bleepingcomputer.com/news/security/northflank-security-breach-leads-to-abuse-of-customers-ai-api-keys/).*
