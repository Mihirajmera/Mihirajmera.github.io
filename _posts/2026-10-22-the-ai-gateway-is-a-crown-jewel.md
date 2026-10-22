---
title: "The AI gateway is a crown jewel: what the LiteLLM compromise teaches about governing AI infrastructure"
description: For about two hours on October 21, the official LiteLLM release stole credentials from everyone who installed it. It was signed, approved and published by the real pipeline. Every control worked as designed, and that's the lesson.
kind: essay
research: true
status: block
evidence:
  hash: 462d0c9f
  label: BerriAI/litellm#47826 · wheel hashes and IOCs
  url: https://github.com/BerriAI/litellm/issues/47826
tags: [AI supply chain, AI infrastructure, Incident analysis]
figures:
  - {n: "~2h", label: "the poisoned release was live on PyPI and Docker", tone: red}
  - {n: "3", label: "developer accounts whose stolen credentials were used", tone: amber}
  - {n: "0", label: "signatures that failed: the pipeline signed the malware", tone: red}
linkedin: |
  Yesterday, the official LiteLLM release stole credentials from everyone who installed it.

  It was signed. It went through the real release pipeline. It passed the approval gate. Trusted publishing worked exactly as designed.

  And the payload was built for AI infrastructure: it queried LiteLLM's own credential tables, where companies keep the API keys for every model provider they use.

  Three lessons for anyone governing AI:

  1️⃣ Your AI gateway is a crown jewel. It holds the keys to every model, and often the prompts and responses too. Treat it like a domain controller, not a dev tool.

  2️⃣ "Signed" isn't "safe." The provenance was valid, and it named the attacker's lookalike repository. The signal was there; almost nobody checks which repository a signature vouches for.

  3️⃣ Two-person rules fail when one attacker holds both people's tokens. The approval gate was satisfied with a stolen credential, and the branch protection was overridden with another.

  The cheapest control would have worked: the bad release was gone in about two hours, so a one-day cooldown on new versions would have skipped it entirely.

  Full analysis, timeline and a checklist in the first comment 👇

  #AISecurity #SupplyChainSecurity #AIGovernance #GRC #CyberSecurity
image: /assets/img/posts/the-ai-gateway-is-a-crown-jewel.png
---

For roughly two hours on October 21, installing the official release of [LiteLLM](https://github.com/BerriAI/litellm), one of the most widely used AI gateways, gave an attacker your cloud credentials, your SSH keys and, if you ran the proxy, the API keys for every model provider your company uses.

It wasn't a typosquat or a fake package. Version `1.107.0` was built, signed and published by LiteLLM's real release pipeline, and passed its approval gate. Every control did what it was designed to do.

That's what makes it worth studying. Here's what happened, why it matters more than another supply-chain incident, and what governing AI infrastructure should look like after it.

{% include figures.html items=page.figures %}

## What happened

LiteLLM is a proxy that sits between applications and model providers: one API in front of OpenAI, Anthropic, Bedrock, Vertex and dozens more. Datadog's write-up cites about 23 million weekly downloads. Companies run it as the central gateway for their AI traffic.

According to [LiteLLM's incident report](https://docs.litellm.ai/blog/security-incident-oct-21-2026) and independent reconstructions by [StepSecurity](https://www.stepsecurity.io/blog/litellm-1-107-0-compromised-pypi-backdoored-wheels-credential-stealer), [Datadog](https://securitylabs.datadoghq.com/articles/litellm-compromised-pypi-docker/) and [Chainguard](https://www.chainguard.dev/unchained/litellm-attacked-again-malicious-1-107-0-wheels-on-pypi-and-docker-hub-october-2026) (all times UTC):

| Time | Event |
|---|---|
| 10:08 | An unauthorized change to the private release workflow is blocked by branch protection, then applied using a privileged developer's credential |
| 11:11 | A second developer's credential satisfies the production approval gate |
| 11:39 | Seven `litellm==1.107.0` wheels are uploaded to PyPI |
| 11:46 | Infected Docker images are published, and `latest`, `main-latest` and `main-stable` are repointed to them |
| 12:06 | A user reports the compromise publicly ([#47826](https://github.com/BerriAI/litellm/issues/47826)) |
| ~13:20 | PyPI quarantines 1.107.0 |
| 14:20 | The Docker Hub tags are removed or repointed |

The source code was never modified; the `v1.107.0` git tag is clean. The attacker repointed the release workflow at a lookalike repository, `Berri-AI/litellm` instead of `BerriAI/litellm`, and added one line to the build configuration so that three extra files landed in every wheel.

**The payload ran without anyone importing LiteLLM.** A `cook.pth` file in site-packages executes on every Python start, pip included. It ran a credential stealer covering 16 categories, including cloud credentials, SSH and GPG keys, browser passwords, CI secrets, the environment of every readable process, and AI coding tool configs. It also planted an hourly loader designed to fetch and run new code.

**How the attacker got the credentials** is still under investigation. LiteLLM's report describes an unexpected user account on an internet-exposed internal LiteLLM deployment, and says that GitHub CLI tokens could appear in that deployment's logs because response bodies were logged. It hasn't confirmed how the attacker got into the deployment.

This was LiteLLM's second compromise in seven months; in March, according to Chainguard, a stolen PyPI token was used to publish two malicious versions.

## Why this one is different

### The payload was built for AI infrastructure

Most credential stealers grab whatever's on disk. This one had a module, `db_litellm`, that connected to the proxy's database when `DATABASE_URL` was set and queried `LiteLLM_CredentialsTable` and `LiteLLM_ProxyModelTable`: the tables where the gateway stores **every model provider's API key**.

An AI gateway is the most valuable place in a company to steal AI credentials from, because it's designed to hold all of them. It often also logs prompts and responses, which can contain customer data, internal documents and, as LiteLLM found, other people's tokens.

**We've been treating AI gateways as developer tooling. They're tier-0 infrastructure**, closer to an identity provider than a library.

### "Signed" didn't mean "safe"

LiteLLM had done the hardening the industry recommends after March: a private release workflow, PyPI trusted publishing, immutable Docker tags and image signing. None of it helped, because the attacker didn't bypass the pipeline. They changed what the pipeline built, and the pipeline signed it.

But the evidence was there. The build provenance named the lookalike repository. A signature answers *"did this pipeline build this artifact?"* It doesn't answer *"did it build it from the source I think it did?"* unless someone checks the source in the provenance. Tools like `slsa-verifier` take a `--source-uri` for exactly this reason. Almost nobody consuming PyPI packages runs that check.

### Two-person rules fail when one person holds two keys

The release had two strong controls on paper: branch protection on the workflow, and a production approval gate. Each was defeated with a different developer's stolen credential.

Auditors call this segregation of duties, and it's the oldest lesson in controls: a two-person rule only works if no single party can act as both people. When credentials are long-lived and collectable from one place, such as logs, one attacker can impersonate everyone in the chain. The control was designed for insiders acting alone, not for an outsider holding three tokens.

## What would have helped, ranked by cost

**For everyone who installs open-source packages:**

1. **A cooldown on new versions.** The malicious release was removed from PyPI in under two hours. A policy of not installing versions younger than one day, available through Dependabot's cooldown setting or uv's `--exclude-newer`, would have skipped it entirely. I use a two-week window on my own projects; this is the incident that justifies it.
2. **Pin versions and images, never `latest`.** The attacker repointed `latest`, `main-latest` and `main-stable`. Anyone pulling a mutable tag got the malware without changing a line of config. Pin Docker images by digest.
3. **Hash-locked dependencies, with a caveat.** Hash pinning protects you from a *changed* artifact you've already vetted. It would not have stopped you from regenerating a lockfile onto the malicious version. Pinning and cooldown work together.
4. **Egress control on AI infrastructure.** The stealer sent data over plain HTTP to an attacker domain. A gateway that can only reach model providers can't exfiltrate to anywhere else.

**For anyone running an AI gateway:**

5. **Keep provider keys in a secret manager**, not in the gateway's database, so a compromised process can't dump them all with one query.
6. **Don't log full request and response bodies by default.** AI traffic carries credentials and sensitive data in places nobody expects. If you must log, redact.
7. **Give the gateway its own identity, least privilege and monitoring**, as you would an identity provider. Alert on new outbound destinations.

**For anyone publishing software:**

8. **Verify the source, not just the signature.** Check that provenance names the repository you expect, in CI, before publishing and before installing.
9. **Make approval gates require something an attacker can't replay**, such as a hardware key or a fresh MFA prompt, not a long-lived token.
10. **Treat the release workflow definition as a crown jewel too.** Changes to it should be rarer and more heavily reviewed than changes to the code.

## If you were affected

Follow the [official remediation](https://docs.litellm.ai/blog/security-incident-oct-21-2026) and the [tracking issue](https://github.com/BerriAI/litellm/issues/47826), which has the wheel hashes and indicators of compromise. The short version from the incident responders:

- **Don't run Python in an affected environment first.** Every interpreter start re-runs the stealer; find and kill the loader process, then delete `cook.pth`, `cook.py` and the foreign `sitecustomize.py`.
- **Rebuild rather than clean**, pinned to `litellm==1.106.2` or the `v1.106.2` image by digest.
- **Assume exfiltration succeeded** and rotate everything the host could reach, including every provider key in the gateway's database, its master and salt keys, and the database password.

## What this means for AI governance

AI governance conversations tend to focus on models: bias, hallucination, misuse. This incident had nothing to do with model behavior. It was about the plumbing around the models, and that plumbing now concentrates some of the most valuable credentials and data a company has.

Three questions every AI governance program should be able to answer after this week:

1. **Do we have an inventory of our AI infrastructure**, not just our models: gateways, proxies, agent frameworks and MCP servers, with owners?
2. **Is that infrastructure held to tier-0 controls?** Pinned and verified dependencies, secrets out of databases and logs, egress allowlists, monitored identities.
3. **Would we know within two hours?** LiteLLM's community spotted this in under 30 minutes. Most companies wouldn't have noticed at all until the credentials were used.

The release was signed, approved and published by the real pipeline. Every control worked as designed. That's not a reason to trust controls less. It's a reason to design them for an attacker who holds more than one key.

*Sources: [LiteLLM incident report](https://docs.litellm.ai/blog/security-incident-oct-21-2026) · [BerriAI/litellm#47826](https://github.com/BerriAI/litellm/issues/47826) · [StepSecurity](https://www.stepsecurity.io/blog/litellm-1-107-0-compromised-pypi-backdoored-wheels-credential-stealer) · [Datadog Security Labs](https://securitylabs.datadoghq.com/articles/litellm-compromised-pypi-docker/) · [Chainguard](https://www.chainguard.dev/unchained/litellm-attacked-again-malicious-1-107-0-wheels-on-pypi-and-docker-hub-october-2026) · [TechCrunch](https://techcrunch.com/2026/10/21/the-internet-is-having-a-very-bad-cybersecurity-day/). Details may change as the investigation continues; times are UTC.*
