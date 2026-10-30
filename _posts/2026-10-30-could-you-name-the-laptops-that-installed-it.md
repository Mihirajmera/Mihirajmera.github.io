---
title: "Could you name the laptops that installed it? The Claude Code extension backdoor, read as an auditor"
description: For about eleven hours on October 29, Cursor's extension marketplace served a tampered build of the Claude Code extension that planted an SSH key and persistence on developer machines. The payload is ordinary. The control questions it raises about developer endpoints are not, and most teams can't answer the first one.
kind: essay
research: true
status: review
evidence:
  hash: Cursor 2026-10-30
  label: Security notice on the malicious Anthropic.claude-code 2.1.313
  url: https://cursor.com/blog/claude-code-extension-security-notice
tags: [AI supply chain, Developer endpoints, Incident analysis]
figures:
  - {n: "11h", label: "the tampered build was available on Cursor's marketplace", tone: amber}
  - {n: "5,000", label: "users at most received it, according to Cursor", tone: red}
  - {n: "1", label: "SSH key, labeled svc-telemetry, that stays behind after you uninstall", tone: red}
linkedin: |
  Yesterday, for about 11 hours, Cursor's extension marketplace served a tampered build of the Claude Code extension.

  Version 2.1.313. Up to 5,000 users. Cursor says it was not built by Anthropic.

  On install it collected host details, added an attacker's SSH key to the machine, installed persistence and tried to open a reverse tunnel. Removing the extension doesn't remove any of that.

  The malware is ordinary. The control questions aren't:

  1️⃣ Could you name, within an hour, which developer laptops ran version 2.1.313? Most teams have an inventory of servers, not of editor extensions.

  2️⃣ Extensions update themselves. The bad build was live for 11 hours. A rule of "nothing younger than 48 hours" would have skipped it entirely.

  3️⃣ The payload looked for environment variables named KEY, TOKEN and SECRET. Do you know which credentials sit on a developer laptop, so you know what to rotate?

  4️⃣ Uninstalling isn't remediation. Same lesson as Wednesday's post: deleting the secret didn't revoke the key.

  The full post has a test for each one you can run this week.

  #AISecurity #SupplyChainSecurity #DevSecOps #GRC #CyberSecurity
image: /assets/img/posts/could-you-name-the-laptops-that-installed-it.png
---

On Wednesday I wrote that in the LiteLLM attack, [deleting the commit didn't revoke the key](/blog/deleting-the-commit-didnt-revoke-the-key/). A day later the same lesson came back from a different direction: uninstalling the extension doesn't remove the backdoor.

On October 29, from about 2:27am to 1:35pm Pacific time, Cursor's VS Code extension marketplace served a maliciously modified build of the Claude Code extension, version 2.1.313. Cursor's [security notice](https://cursor.com/blog/claude-code-extension-security-notice) says the build "was not developed by Anthropic" and that at most 5,000 users were affected. Version 2.1.314 is clean.

{% include figures.html items=page.figures %}

## What the build did

From Cursor's notice and [StepSecurity's analysis](https://www.stepsecurity.io/blog/claude-code-extension-trojanized):

| Step | What it did |
|---|---|
| Recon | Collected hostname, username, OS, home directory, working directories, Git email, public IP, and the *names* of environment variables. StepSecurity says it looked for names containing KEY, TOKEN, SECRET, PASS, AWS or GCP. |
| Access | Added an attacker-controlled key to `authorized_keys`, labeled `svc-telemetry`, and tried to turn on the SSH service and open a reverse tunnel. |
| Persistence | A LaunchAgent named `com.apple.sysmond` on macOS; a scheduled task named `SysMon`, running as SYSTEM, on Windows. Scripts retried the tunnel about every 60 seconds. |
| Report | Sent host details and backdoor status to the attacker's server over plain HTTP. |

The impact was probably smaller than that list suggests. Turning on the SSH service needs admin rights, which the extension usually didn't have, so the tunnel usually failed. The attacker's server is now offline. But the key was still added and the persistence still installed, and Cursor says plainly that "uninstalling the extension may not be sufficient."

Nothing here is new technique. What makes it worth an auditor's time is *where* it landed: the machine where your engineers hold their cloud credentials, Git tokens and production access.

## Four control questions, and the test for each

### 1. Could you name the laptops that installed it?

Cursor's first instruction is to find everyone who installed or updated to 2.1.313 during the window. That should be a five-minute query. In most companies I've looked at, it's a Slack message asking people to check.

Asset inventories usually stop at the device. They know the laptop exists and which OS it runs. They rarely know which editor extensions are installed, at which version, which is exactly what an incident like this needs.

**Test it:** pick one extension your developers use, and ask how long it takes to produce a list of every machine running a specific version of it. If the answer involves asking people, extensions aren't in your software inventory, and an AI coding extension runs with the same rights as the developer.

### 2. Updates arrive faster than anyone can review them

Editors built on VS Code update extensions automatically in most setups. The bad build was live for about eleven hours. Anyone whose editor checked for updates in that window got it without doing anything.

You can't review every extension update, and you shouldn't try. The cheaper control is time. Package managers already support a minimum release age (pnpm and Renovate both have one): don't install a version until it has been public for a set period. Most malicious releases are caught and pulled within a day or two. A 48-hour rule would have skipped this build entirely, and the [LiteLLM wheels](/blog/the-ai-gateway-is-a-crown-jewel/) too, which were live for about two hours.

VS Code also has an allowlist setting, `extensions.allowed`, that can restrict which extensions and versions are installed. Check whether your editors honor it before relying on it.

**Test it:** for your developer tooling (extensions, package managers, CLI plugins), write down who decides when an update is installed. If the answer is "the publisher, automatically," you have outsourced change management to whoever controls the publisher's account.

### 3. Do you know what to rotate?

Cursor's notice says to rotate "credentials and sessions accessible from affected hosts," and warns that the limited collection "does not rule out later credential access over the backdoor."

That instruction assumes you know which credentials are on a developer's laptop. Usually nobody does: long-lived cloud keys in `~/.aws/credentials`, a GitHub token in the CLI config, `.env` files in a dozen old project folders, a database password in shell history.

The recon step only collected variable *names*. That's a target list for a second visit.

**Test it:** pick one developer laptop and list every credential on it that grants access to something real. Then check how many are long-lived. Every long-lived credential on that list is something you'd have to rotate by hand after an incident like this one, and something that keeps working if you miss it.

### 4. Uninstalling isn't remediation

Removing the extension leaves the SSH key, the scheduled task and the LaunchAgent in place. A ticket that closes when the bad version is gone has closed the wrong thing. This is the same gap as a leaked secret that is deleted from the repo but never revoked.

The persistence was also built to blend in. `SysMon` and `com.apple.sysmond` look like system components at a glance, and `svc-telemetry` looks like a service account.

**Test it:** does your endpoint tooling alert on a new entry in `authorized_keys` on a laptop, a new scheduled task running as SYSTEM, or a new LaunchAgent? Developer machines are often given looser rules because developers install things all day. Check whether that exception covers exactly these events.

## What to ask your vendors

If your developers use an AI-enabled editor, add these to the vendor review:

1. How does the marketplace verify that a package matches what the named publisher actually built?
2. If a publisher's account is compromised, what stops a new version reaching every user within the hour?
3. Can we control which versions are installed, and delay updates by a set period?
4. How quickly will you tell us which of our users installed a bad version?

## What I haven't verified

The details above come from Cursor's notice and StepSecurity's analysis. Neither says how the modified package got into the marketplace, and they describe the channel differently: Cursor's notice is about its own marketplace, while StepSecurity says the build was also published to Open VSX, under the legitimate Anthropic namespace. I haven't seen the package or the logs, and the account may change as the investigation goes on.

If you or your team installed Claude Code from Cursor's marketplace on October 29, follow [Cursor's notice](https://cursor.com/blog/claude-code-extension-security-notice) first. It has the indicators and the cleanup scripts.

*Sources: [Cursor security notice](https://cursor.com/blog/claude-code-extension-security-notice) · [StepSecurity](https://www.stepsecurity.io/blog/claude-code-extension-trojanized) · [Help Net Security](https://www.helpnetsecurity.com/2026/10/30/claude-code-extension-ssh-backdoor/) · [Cursor on X](https://x.com/cursor_ai/status/2116074289053175808).*
