---
title: "The 30-line diff between a failing and a passing AI gateway"
description: "A LiteLLM gateway set up the quick way fails 11 of 11 checks with 15 findings, 7 of them high. The hardened version passes all 11. The difference is about 30 lines of config, and every one of them maps to a control."
kind: note
research: true
status: review
tags: [AI gateways, LiteLLM, Configuration review]
evidence:
  hash: ai-gateway-audit
  label: "ai-gateway-audit: the insecure and hardened example deployments and the report"
  url: https://github.com/Mihirajmera/ai-gateway-audit/tree/main/ai_gateway_audit/examples
figures:
  - {n: "15 → 0", label: "findings, from the quick setup to the hardened one", tone: green}
  - {n: "7", label: "of the 15 are high severity: plain-text keys, prompt logging, TLS off, a vulnerable release", tone: red}
  - {n: "~30", label: "changed lines across config.yaml and docker-compose.yml", tone: amber}
diagram:
  type: flow
  caption: "ai-gateway-audit's insecure example, fixed in four groups of changes"
  steps:
    - {id: GWA-01/02, label: Secrets out of files, sub: "provider key, master key, database URL, UI password", test: 4 high findings, state: fail}
    - {id: GWA-03/04, label: Prompts and keys out of storage, sub: "spend logs, logging callbacks, keys in the database", test: 1 high · 2 medium, state: fail}
    - {id: GWA-05/06, label: Named admins and a spend cap, sub: "no shared UI login, a global budget, a per-key ceiling", test: 2 medium · 1 low, state: warn}
    - {id: GWA-07–11, label: Know what you're running, sub: "patched release pinned by digest, TLS on, docs off, request limits", test: 2 high · 1 medium · 2 low, state: fail}
tools: [ai-gateway-audit]
image: /assets/img/posts/the-30-line-diff-that-hardens-an-ai-gateway.png
---

An AI gateway such as LiteLLM sits between your applications and every model provider. It holds the provider keys, sees every prompt and decides who can spend what. I've written about [why that makes it a crown jewel](/blog/the-ai-gateway-is-a-crown-jewel/) and [how its lowest role was one request from admin](/blog/the-lowest-role-on-the-gateway-was-one-request-from-admin/). This post is the fix, as a diff.

[ai-gateway-audit](https://github.com/Mihirajmera/ai-gateway-audit) ships two example deployments of the same proxy. One is set up the quick way, the way most tutorials leave it. The other is hardened. Every credential in both is fake.

{% include figures.html items=page.figures %}

## The result

The quick setup fails all 11 checks, with 15 findings: 7 high, 5 medium and 3 low. The hardened one passes all 11. Here's what changed, grouped by what each change protects.

## 1. Get secrets out of files

```diff
-      api_key: example-openai-key-not-real
+      api_key: os.environ/OPENAI_API_KEY
-  master_key: sk-1234
+  master_key: os.environ/LITELLM_MASTER_KEY
```

In `docker-compose.yml`, the database password in `DATABASE_URL` and the admin `UI_PASSWORD` move out the same way. That accounts for four high findings. The master key matters most: it grants admin over every model, key and budget on the proxy. The tool's advice for each is the same two steps: reference it from the environment, filled by a secret manager, and **rotate it**, because anyone who could read the file has already had it.

## 2. Keep prompts and keys out of storage

```diff
-  store_prompts_in_spend_logs: true
+  store_prompts_in_spend_logs: false
+  turn_off_message_logging: true
-  store_model_in_db: true
+  store_model_in_db: false
```

With spend logging of prompts on, every prompt and response is written to the gateway database next to the billing records. Without `turn_off_message_logging`, they also go to every logging callback, here Langfuse. And with `store_model_in_db` on and no key management system, provider keys added through the UI sit in the database, where one query reads them all. That's what the payload did in the [October LiteLLM compromise](/blog/deleting-the-commit-didnt-revoke-the-key/).

## 3. Name the admins, cap the money

```diff
+  disable_env_credential_login: true
+  max_budget: 2000
+  budget_duration: 30d
+  upperbound_key_generate_params:
+    max_budget: 100
+    duration: 30d
```

The shared `UI_USERNAME` / `UI_PASSWORD` login means admin actions can't be tied to a person, so the fix is named admin accounts or SSO, then turning the shared login off. The budgets close a different gap. Without a global cap, a leaked key or a runaway agent can spend without limit, and stolen gateway access is used to run attackers' own workloads. The per-key ceiling stops anyone creating a key with no limit at all.

## 4. Know what you're running

```diff
-    image: ghcr.io/berriai/litellm:main-v1.94.0-stable
+    image: ghcr.io/berriai/litellm:v1.106.2@sha256:<digest of the reviewed image>
-  ssl_verify: false
+      NO_DOCS: "True"
+      NO_REDOC: "True"
+      NO_OPENAPI: "True"
+  max_request_size_mb: 25
+  allowed_file_extensions: [".jsonl", ".pdf", ".txt"]
```

This group has the two findings I'd fix first. Version 1.94.0 is affected by two high-severity advisories, including one that lets the lowest built-in role read local files. The fix is 1.100.4 or later. And `ssl_verify: false` means provider certificates aren't checked, so anyone on the network path can read prompts and provider keys.

The rest are smaller but cheap. Pin the image by digest, not just by tag, because a tag can be moved to different content. Turn off the interactive API docs, which describe every admin route. Limit request sizes and upload types.

## What the diff doesn't show

The checks confirm a setting exists. A reviewer still has to judge three things:

- **Whether the numbers are right.** A $2,000 monthly cap passes the check whether or not anyone approved $2,000. The control is the approval, so ask who signed off on the number.
- **Whether the digest is real.** The hardened example uses a placeholder digest on purpose. In a real deployment, it should be the digest of the image someone actually reviewed.
- **Whether the config is what's deployed.** The hardened example also binds the port to localhost and mounts the config read-only. Those are good practice, but the point is broader: the file in the repo is evidence about the deployment, not the deployment itself.

If you run a LiteLLM gateway, run the same checks on your own config and compose file. They make no network calls and change nothing.
