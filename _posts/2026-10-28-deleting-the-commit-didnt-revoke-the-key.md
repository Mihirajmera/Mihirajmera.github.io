---
title: "Deleting the commit didn't revoke the key: the LiteLLM root cause, read as an auditor"
description: LiteLLM has published the real root cause of the October 21 release compromise. A master key leaked in May, the commit was rewritten but the key was never revoked, and 136 days later it unlocked an agent platform holding an org owner's GitHub token. Four control failures, and what to test for each.
kind: essay
research: true
status: review
evidence:
  hash: LiteLLM 2026-10-23
  label: The attack chain behind the v1.107.0 LiteLLM release
  url: https://docs.litellm.ai/blog/security-incident-oct-21-2026-attack-chain
tags: [AI supply chain, Secrets management, Incident analysis]
figures:
  - {n: "136", label: "days the leaked master key stayed valid before it was used", tone: red}
  - {n: "11", label: "days between the first break-in and the poisoned release", tone: amber}
  - {n: "1", label: "org owner's personal GitHub token, sitting in an AI agent's config", tone: red}
linkedin: |
  On May 27, a LiteLLM master key was committed to a public repo. Someone noticed and rewrote the history.

  Nobody revoked the key.

  136 days later, an attacker used it. That was the start of the October 21 attack that put a credential stealer into an official LiteLLM release.

  LiteLLM has now published the full attack chain, and it's a list of controls we all claim to have:

  1️⃣ Deleting a secret isn't revoking it. A force-push removes the commit from the branch. It doesn't stop the key working for anyone who already copied it.

  2️⃣ An AI agent was running on an org owner's personal GitHub token, not scoped down and not a service account. One API call returned every agent's config, token included.

  3️⃣ The release approval was relaxed "earlier this week" to ship faster: any two engineers instead of a device-locked account. Two stolen tokens became two approvers.

  4️⃣ The attacker was inside for 11 days. Exfiltration workflows ran and were deleted in under three minutes.

  None of this is exotic. Each one is a control test you can run this week. The full post has the tests.

  Credit to LiteLLM for publishing the detail, including where their first account was wrong.

  #AISecurity #SupplyChainSecurity #SecretsManagement #GRC #CyberSecurity
image: /assets/img/posts/deleting-the-commit-didnt-revoke-the-key.png
---

Last week I wrote about [the LiteLLM release compromise](/blog/the-ai-gateway-is-a-crown-jewel/), when version 1.107.0 shipped a credential stealer through LiteLLM's real release pipeline. At the time, LiteLLM's working theory was that the attacker took GitHub tokens from an internal deployment's logs, and my post repeated that.

On October 23 LiteLLM published [the full attack chain](https://docs.litellm.ai/blog/security-incident-oct-21-2026-attack-chain), and the log theory was wrong. The real story is simpler, and more useful for anyone who runs or audits controls. Every step is an ordinary control that existed on paper.

{% include figures.html items=page.figures %}

## What actually happened

All from LiteLLM's post; times are UTC.

| When | What |
|---|---|
| May 27 | A config file containing the master key for LiteLLM's internal Agent Platform is committed to a public repo. The commit is force-pushed over. The key is not revoked. |
| Oct 10, 21:27 | The attacker uses that key to call the Agent Platform API. One request returns the configuration of every managed agent, including a GitHub CLI token belonging to one of the two GitHub organization owners. |
| Oct 10, 22:11 | Using the owner's access, the attacker runs a workflow on a throwaway branch that posts six secrets, including a second maintainer's token, to an outside endpoint. A second workflow takes a third maintainer's token. Both runs are deleted in under three minutes. |
| Oct 12 | A second round of exfiltration across private repos. |
| Oct 21, 10:08 | A push to the release workflow is rejected by branch protection, then forced through five seconds later with the owner's token. |
| Oct 21, 11:11 | A second stolen maintainer token approves the production release gate. |
| Oct 21, 11:39 | The poisoned wheels go to PyPI. They are live for about two hours. |

## Four control failures, and the test for each

### 1. A leaked secret was deleted, not revoked

Rewriting git history removes a commit from the branch. It does nothing about copies that were already made, and it doesn't make the key stop working. The key stayed valid for 136 days.

This is the most common gap I see in secrets handling: the ticket closes when the secret disappears from the repo, because that's what the scanner checks.

**Test it:** pull your last ten secret-scanning alerts marked resolved. For each one, is there evidence the credential was *revoked*, such as a rotation record or the old key returning 401? "Removed from code" is not remediation.

### 2. An AI agent ran on an org owner's personal token

The token in the agent's config was, in LiteLLM's words, "not associated with a service account and was not scoped down." It belonged to one of the two people with the most power in the GitHub organization. And the platform's API returned it in full to anyone holding the master key.

I wrote on Monday that [an agent using your password *is* you](/blog/the-banks-just-ran-an-access-review-on-ai-agents/) as far as every control can tell. This is the same failure inside a software company. LiteLLM also notes that these CLI tokens skip GitHub's re-authentication prompt for sensitive actions, so the strongest account was protected by the weakest credential type.

**Test it:** list every token your AI agents, MCP servers and automation hold. Which ones belong to a named person, and which of those people are admins or owners? Any agent config API that returns secrets in plain text is a finding on its own.

### 3. A control was relaxed to ship faster, and nobody owned the risk

Releases used to need approval from "a special account locked to a physical device in our office." That was relaxed "earlier this week" to allow faster releases: any two engineers could trigger and approve.

Two-person approval only works if the two credentials can't be stolen together. A device-locked approver can't be replayed from a stolen token; two engineers' CLI tokens can. Weakening the control turned a two-person rule into a two-token rule, and the attacker already had three tokens.

The decision to relax it was reasonable. The gap is that it wasn't treated as what it was: a risk acceptance. That is the same pattern as [yesterday's post](/blog/decide-who-takes-it-offline-before-the-advisory/) on compensating controls. A temporary change to a control needs an owner, an expiry date and something that compensates while it's in place.

**Test it:** ask when your release approval, branch protection or MFA settings last changed, who approved the change, and when it is due to be reversed. If the answer comes from the audit log instead of a change record, that's the finding.

### 4. Eleven days inside, with the evidence deleted

The attacker was in on October 10 and released on October 21. The exfiltration workflows ran from throwaway branches and were deleted in under three minutes. On release day, branch protection was overridden and the run records were deleted.

Every one of those actions shows up in GitHub's audit log: a workflow run deleted, branch protection bypassed by an owner, a new branch pushed and removed. They're rare events, and each one was a chance to notice.

**Test it:** do you alert on branch-protection bypasses, deleted workflow runs, and organization-owner tokens used from a new IP? If those events only exist in a log nobody reads, the control is evidence after the fact, not detection.

## What to ask your vendors

LiteLLM reports holding [SOC 2 Type 2](https://docs.litellm.ai/blog/soc2-type-2-report) and [ISO 27001](https://docs.litellm.ai/blog/vanta-compliance-recertification). I'm not suggesting the audits were wrong; I haven't seen the reports, and an audit covers a period and a scope. The point is that none of the four failures above would show up unless someone asked about them directly. For any vendor in your AI supply chain, add these to the questionnaire:

1. When a secret is exposed, what evidence shows it was revoked, not just removed?
2. Do automated agents or pipelines ever run on a named person's credentials?
3. Is release approval bound to something that can't be replayed, like a hardware key?
4. How are temporary relaxations of security controls approved and tracked?

## What I haven't verified

Everything above comes from LiteLLM's own account, and it says the process changes will be published separately. I haven't seen the audit logs or the agent platform. LiteLLM corrected its own first account, and details may change again.

Credit to LiteLLM for publishing the attack chain in this much detail, including the parts where its first theory was wrong. Most companies never publish that.

*Sources: [LiteLLM, The attack chain behind the v1.107.0 release](https://docs.litellm.ai/blog/security-incident-oct-21-2026-attack-chain) · [The Hacker News](https://thehackernews.com/2026/10/leaked-litellm-master-key-let-attackers.html) · [Wiz](https://www.wiz.io/blog/litellm-compromised-steals-credentials).*
