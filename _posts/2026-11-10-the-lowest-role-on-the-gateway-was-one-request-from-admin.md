---
title: "The lowest role on the AI gateway was one request from admin"
description: "Two LiteLLM advisories published on October 27 gave low-privilege users a route to proxy admin, and from there to commands on the host. On many deployments, the lowest role is what every employee gets by signing in with SSO. Here's what to patch, what to rotate, and what the access review of an AI gateway has to cover."
kind: essay
research: true
status: review
evidence:
  hash: GHSA-7hp6-4w63-5g45
  label: "LiteLLM: Privilege Escalation to Proxy Admin via Cross-Domain Reuse of the Salt Key (CVE-2026-114612)"
  url: https://github.com/advisories/GHSA-7hp6-4w63-5g45
tags: [AI gateways, Access control, Vulnerability management]
figures:
  - {n: "9.9", label: "CVSS score of the salt-key escalation, CVE-2026-114612", tone: red}
  - {n: "2", label: "separate routes from a low-privilege role to proxy admin", tone: amber}
  - {n: "1", label: "key doing two jobs: encrypting secrets and minting session tokens"}
diagram:
  type: flow
  caption: the file-read route, GHSA-g5ff-637f-6q2m (LiteLLM before 1.95.0)
  steps:
    - {id: R-01, label: Employee signs in with SSO, sub: gets internal_user_viewer, test: "who can sign in at all?", state: warn}
    - {id: R-02, label: Crafted vertex_ai_credentials, sub: an alias the blocklist missed, test: "on 1.95.0 or later?", state: fail}
    - {id: R-03, label: Reads /proc/self/environ, sub: master key and provider keys, test: "rotated after patching?", state: fail}
    - {id: R-04, label: Proxy admin, sub: "same end point as the salt-key bug", state: fail}
    - {id: R-05, label: MCP stdio endpoint, sub: commands on the gateway host, test: "what can the host reach?", state: fail}
linkedin: |
  On many AI gateways, every employee is one sign-in away from a role. Two LiteLLM advisories published on October 27 showed how far that lowest role could go.

  Route one (no CVE yet, fixed in 1.95.0): a user with the lowest role sent a credential field under an alias the blocklist didn't cover, and the proxy read any file on the host. That includes the process environment, which holds the master key.

  Route two (CVE-2026-114612, CVSS 9.9): the proxy used one key both to encrypt stored secrets and to mint session tokens. A regular user could get it to encrypt a forged admin identity, then present that as a token.

  Both end at proxy admin, which can run commands on the host through the MCP stdio endpoint.

  What to do this week:

  1️⃣ Check your version, not your tag. "main-stable" doesn't tell you whether you're patched.

  2️⃣ If you ran an affected version with SSO users, rotate the master key and every provider key behind the gateway.

  3️⃣ Review everyone who can sign in to the gateway, not just the admins. On an unpatched gateway, the lowest role was effectively admin.

  4️⃣ One key, one job. Ask what each key on the gateway is used for. More than one answer is a finding.

  5️⃣ Treat the gateway host as a crown jewel. Admin on the gateway means a shell on that host.

  #AISecurity #LiteLLM #AccessControl #GRC #CyberSecurity
tools: [ai-gateway-audit]
image: /assets/img/posts/the-lowest-role-on-the-gateway-was-one-request-from-admin.png
---

Three weeks ago I argued that [the AI gateway is a crown jewel](/blog/the-ai-gateway-is-a-crown-jewel/): it holds every provider key, sees every prompt, and decides who can use which model. On October 27, LiteLLM, the most widely used open-source gateway, published two advisories that show what that means when the access controls inside the gateway fail.

Both start with a user who has very little power, and both end with that user as proxy admin. The usual audit question is who the admins are. These advisories show it also matters who has any role at all.

{% include figures.html items=page.figures %}

## Route one: an alias the blocklist missed

The [first advisory](https://github.com/advisories/GHSA-g5ff-637f-6q2m) affects LiteLLM before 1.95.0. A user with the lowest role, `internal_user_viewer`, could send a request to a utility endpoint with a Vertex AI credential field. The proxy had a blocklist that rejected the field `vertex_credentials`, but not its alias `vertex_ai_credentials`. The value reached the credential loader, which read a local file and sent its contents to a URL the attacker chose.

The advisory names the obvious target: `/proc/self/environ`, the process's environment, which can contain `LITELLM_MASTER_KEY` and the provider API keys. With the master key, the user is now proxy admin. The advisory also notes that this lowest role is "obtainable through SSO login on many deployments". On those deployments, anyone in the company who could sign in could do this.

There's no workaround. Upgrading to 1.95.0 adds the alias to the blocklist.

## Route two: one key, two jobs

The [second advisory](https://github.com/advisories/GHSA-7hp6-4w63-5g45), CVE-2026-114612, scores 9.9. The proxy used a single key for two different purposes: encrypting secrets it stores, and creating session tokens. A user with the `internal_user` role could ask for a new API key with a metadata field containing a forged admin identity as the "secret". The proxy encrypted it and handed it back. Presented as a bearer token, it decrypted to an admin identity, and the proxy trusted it.

From proxy admin, the advisory says, an attacker can run commands on the host through the MCP stdio endpoint. Versions from 1.91.0 were exploitable in the default configuration. Patched releases exist for each affected line (1.100.4, 1.101.3, 1.102.2, 1.103.1). If you can't upgrade yet, setting `EXPERIMENTAL_UI_LOGIN=false` closes the vulnerable path, though it also breaks CLI SSO and Claude Code gateway login.

The security principle here is old. A key should do one job. If the same key encrypts data and authenticates users, anyone who can get the system to encrypt something of their choosing can produce something that looks like a credential.

## What to do this week

**1. Check the version you're running, not the tag.** If your gateway runs a moving tag like `main-stable`, the tag tells you nothing about whether you have these fixes. Look up the actual version in the running container, and pin the image by its digest from now on. [ai-gateway-audit](https://github.com/Mihirajmera/ai-gateway-audit) flags a gateway image that isn't pinned (GWA-07).

**2. Rotate if you were exposed.** If you ran an affected version and anyone other than your admins could sign in, assume the master key and the provider keys may have been read. Patch first, then rotate the master key and every provider key behind the gateway. Rotating before patching just gives a new key to the same hole.

**3. Look for the requests.** Search the gateway's request logs for calls to `/utils/transform_request` containing `vertex_ai_credentials`, and for key-generation requests from non-admin users with unusual metadata. Either is worth investigating.

**4. Review everyone who can sign in, not only the admins.** Most access reviews of a gateway check the admin list. These two bugs turned the lowest roles into admin. The review should list every person and service with any role, how they got it (SSO auto-provisioning or a deliberate grant), and whether they need it. If the answer for most of the company is "SSO gave it to them and they've never used it", turn auto-provisioning off.

**5. Ask what each key does.** List every key and secret the gateway uses, with its purpose. If any key has more than one purpose, that's a design finding, even after this fix.

**6. Treat the gateway host as part of the crown jewel.** Proxy admin can run commands on the host. Whatever that host can reach, a gateway admin can reach. Check the host's network access and the credentials on it, and keep the master key out of anything a file-read bug could return. ai-gateway-audit's GWA-02 checks the master key isn't written in plain text in the config, but a key loaded into the environment can still leak at runtime, which is why rotation matters.

## The control behind the bug

Both bugs are LiteLLM's to fix, and they're fixed. The lesson for the people who run gateways is about the access review. A gateway's roles only mean what the code enforces. When an advisory shows the lowest role reaching admin, every account with that role was effectively an admin for as long as you ran the affected version. The review should show who those people were, and whether any of them used it.
