---
title: "Supabase's MCP server says pausing your project isn't destructive. It's right, and that's the problem."
description: "MCP tools label themselves read-only or destructive. Supabase's labels are careful and accurate, and they still can't tell you that an agent can pause your production project, create billable projects or write secrets. Those labels answer whether a tool can lose data. An access review asks what privilege it grants."
kind: note
research: true
status: review
tags: [MCP, AI agents, Access review, Least privilege]
figures:
  - {n: "43", label: "of 2,830 public MCP configs run the Supabase npm server"}
  - {n: "5", label: "account or secret tools labelled not destructive", tone: amber}
  - {n: "1", label: "first outside contribution to agent-access-review", tone: green}
diagram:
  type: flow
  caption: "what the tool says about itself vs what an access review needs"
  note: "@supabase/mcp-server-supabase source, 2026-11-15"
  steps:
    - {id: T-01, label: List tables, sub: "read-only: yes", test: "read", state: ok}
    - {id: T-02, label: Pause project, sub: "destructive: no", test: "admin: takes the project offline", state: warn}
    - {id: T-03, label: Create project, sub: "destructive: no", test: "admin: starts a billable project", state: warn}
    - {id: T-04, label: Create secret, sub: "destructive: no", test: "admin: writes a credential", state: warn}
    - {id: T-05, label: Execute SQL, sub: "destructive: yes", test: "execute: any SQL on the project", state: fail}
linkedin: |
  Supabase's MCP server says pausing your production project isn't destructive. It's right. That's the problem.

  Every MCP tool can label itself: read-only or not, destructive or not. Supabase's labels are careful and accurate. "Execute SQL" is destructive. "List tables" is read-only. "Pause project" isn't destructive, because you can restore it.

  But look at what those labels can't say:
  → Pause project: takes your app offline
  → Create project: starts something you pay for
  → Create Edge Function secret: writes a credential

  All three are labelled "not destructive", and all three are admin actions.

  The labels answer "can this tool lose data?" An access review asks a different question: "what privilege does this grant, and should this agent have it?" No annotation covers admin rights, cost or credentials.

  Two more things worth knowing:
  1️⃣ The labels are written by the server's author. The MCP spec calls them hints and tells clients not to trust them from untrusted servers.
  2️⃣ Supabase built a confirmation form before destructive SQL. It's wired into the server's HTTP mode. In the default npm stdio mode, your client's approval prompt is the only check.

  So classify servers by privilege, not by their own labels. Use read-only mode and a single project for agents that only need to read. And record how each server runs, because the safeguards differ.

  This came out of the first outside contribution to agent-access-review: a classification for the Supabase server, checked tool by tool against its source.

  #AISecurity #MCP #AccessReview #AIGovernance
tools: [agent-access-review]
image: /assets/img/posts/not-destructive-is-not-least-privilege.png
---

On Friday, agent-access-review got its first contribution from someone outside the project. [PR #49](https://github.com/Mihirajmera/agent-access-review/pull/49) classifies Supabase's MCP server, so a config that uses it now gets privilege checks instead of a "this server is unknown" finding. It's the 8th most common package in the [2,830 public MCP configs](/case-studies/public-mcp-configs/) I reviewed last week.

The contributor did something I want every reviewer to copy: they checked each tool against Supabase's source code instead of its README. And the source has an interesting detail. Every Supabase tool already describes itself.

{% include figures.html items=page.figures %}

## Tools that label themselves

MCP lets a server attach *annotations* to each tool. Two of them are `readOnlyHint` and `destructiveHint`. Supabase sets both on every tool, and as far as I can tell it sets them accurately:

| Tool | Read-only? | Destructive? | What an access review sees |
|---|---|---|---|
| `list_tables` | yes | no | read |
| `execute_sql`, `apply_migration` | no | **yes** | execute any SQL on the project |
| `delete_branch`, `reset_branch`, `deploy_edge_function` | no | **yes** | delete branches, deploy code |
| `pause_project`, `restore_project` | no | no | **admin**: takes the project offline and back |
| `create_project`, `create_branch` | no | no | **admin**: starts something you pay for |
| `create_edge_function_secret` | no | no | **admin**: writes a credential |

The labels aren't wrong. The MCP spec defines a destructive tool as one that may make destructive updates, as opposed to only additive ones. Pausing a project can be undone, and creating one only adds. By that definition they're not destructive.

But an access review doesn't ask whether a tool can lose data. It asks what privilege the tool grants and whether this agent should have it. Admin rights, spending money and handling credentials have no annotation. So the five tools that change your Supabase account or its secrets all read "not destructive", and a reviewer who sorts by that label misses them.

There's a second reason not to lean on annotations. The server's author writes them. The spec calls them hints and tells clients not to make decisions based on annotations from servers they don't trust. Supabase's are good, but a review process can't assume every server's are.

## A safeguard that depends on how you run it

Supabase went further than labels. Before `execute_sql` or `apply_migration` runs SQL with `DROP`, `DELETE`, `TRUNCATE` or an `UPDATE` without `WHERE`, the server can show a confirmation form ("It may permanently remove data… Run it on project …?"). The form's state is signed and expires after ten minutes. That's a real control.

It's switched on in the server's HTTP mode, when the MCP client can show forms. In the default way most configs run it, `npx @supabase/mcp-server-supabase` over stdio, version 0.17.0 starts the server without it. In that mode, your MCP client's approval prompt is the only check before destructive SQL runs.

That isn't a vulnerability. The client still asks. But it means the same package gives an agent different safeguards depending on one line of config, and a reviewer who only reads the package name can't tell which one they're approving.

## What to check

1. **Classify by privilege, not by the server's own labels.** agent-access-review now treats Supabase as `read, write, delete, execute, admin` on `restricted` data. That reflects what the tools can do, not how they describe themselves.
2. **Use read-only mode where it fits.** `--read-only` (or `read_only=true` on the hosted URL) plus a single `--project-ref` is the right setup for an agent that only needs to read.
3. **Record how each server runs.** Stdio or HTTP, local or hosted. The safeguards differ, so the evidence should say which one you approved.

The classification is merged and ships in the next release. Three more servers are waiting for the same treatment: [Notion](https://github.com/Mihirajmera/agent-access-review/issues/43), [Sentry](https://github.com/Mihirajmera/agent-access-review/issues/44) and [Context7](https://github.com/Mihirajmera/agent-access-review/issues/47). Each one is a short catalog entry and a test, and each issue says exactly how to check it.
