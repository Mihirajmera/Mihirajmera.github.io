---
title: "The banks just ran an access review on AI agents. Here's what they found."
description: America's biggest banks are blocking outside AI agents from customer accounts. The reason isn't that agents are dangerous. It's that an agent using your password is indistinguishable from you, and every control downstream depends on knowing who acted.
kind: essay
research: true
status: review
evidence:
  hash: Reuters 2026-10-23
  label: US banks are blocking third-party AI agents
  url: https://www.hawaiitribune-herald.com/2026/10/23/nation-world-news/us-banks-are-blocking-third-party-ai-agents-access-to-customer-accounts-sources-say/
tags: [AI agents, Identity and access, AI governance]
figures:
  - {n: "6", label: "major US banks and brokers now blocking or restricting outside AI agents", tone: amber}
  - {n: "1", label: "password shared by customer and agent, so the bank can't tell them apart", tone: red}
  - {n: "2/3", label: "of financial-services and software CISOs rank agentic AI a top-three risk"}
linkedin: |
  This week, America's biggest banks started blocking AI agents from customer accounts.

  Morgan Stanley, JPMorgan, Bank of America, Citi, Wells Fargo and Schwab are all restricting outside agents. Some agents had been logging in with customers' own passwords, and some appeared to act beyond what the customer asked.

  The headline is "banks vs AI." The real story is an identity problem every company has:

  1️⃣ An agent using your password IS you, as far as every control can tell. Logs, fraud models and "unauthorized transaction" rules all assume the person who logged in is the person who acted.

  2️⃣ "Authorized" isn't "intended." Wells Fargo's new terms treat agent transactions as authorized, even ones "you did not want or intend." The risk moved to the customer, quietly.

  3️⃣ The banks landed on the oldest answer in access control: least privilege. Read-only access, a human approves anything that moves money.

  Now look inside your own company. How many AI agents are running on an employee's SSO session or personal access token right now? Would your logs know the difference?

  Full analysis and an agent identity checklist in the first comment 👇

  #AIGovernance #AIAgents #IdentitySecurity #GRC #CyberSecurity
image: /assets/img/posts/the-banks-just-ran-an-access-review-on-ai-agents.png
---

Over the past week, the largest banks in the United States have quietly started turning AI agents away at the door.

According to Reuters, Axios and the Financial Times, Morgan Stanley is blocking outside AI agents from its platforms. JPMorgan Chase, Bank of America and Citi are restricting them. Wells Fargo has rewritten its online access agreement. Charles Schwab is blocking agents that try to move client money. The reports describe agents logging into customer accounts with the customer's own username and password, and some that, per Axios, "attempted to take actions that appeared to be independent of user instructions."

It's being covered as a story about banks resisting AI. I think it's something more useful: **the first large-scale access review of AI agents**, run by the institutions with the most to lose. What they found applies to every company that lets an agent act on someone's behalf, including yours.

{% include figures.html items=page.figures %}

## What happened

| Institution | Reported action | Source |
|---|---|---|
| Morgan Stanley | Blocking third-party agents; a source said it had seen no rogue agent instances | Reuters, Axios |
| JPMorgan Chase | Limiting agents' access to client accounts and building tools to detect them | Q3 earnings call, Reuters |
| Bank of America | Restricting agent access to consumer deposits; developing protocols on liability | FT, Bloomberg |
| Citi | No third-party agents may log in or transact; read-only access through approved open-banking providers | Citi statement |
| Wells Fargo | Steps to block unauthorized agents; updated access agreement takes effect Nov. 24 | USA Today |
| Charles Schwab | Blocking unauthorized agents that try to move client money | Bloomberg, Reuters |

The quotes are telling. Jamie Dimon said JPMorgan would limit agents "because you don't want rogue agents and there could be thousands of them." Brian Moynihan of Bank of America said there "should be a human in the loop to authorise money moving out of your account." Schwab's Rick Wurster said: "We are blocking it because we want to have control over authentication and the experience."

Two caveats before going further. Much of the reporting relies on anonymous sources, and none of it establishes widespread unauthorized transfers or customer losses. This is the industry reacting to a risk, not cleaning up after a disaster. Also, the banks have commercial reasons too: the FT reported a fear that agents will move idle deposits to higher-yielding accounts. Both things can be true.

## Why this one matters

### An agent with your password *is* you

Every control a bank runs downstream of login assumes one thing: **the identity that authenticated is the person who acted.** Fraud models are trained on that person's behavior. Audit logs record that person's ID. Consumer protection rules hinge on whether that person authorized the transaction.

When a customer gives an agent their username and password, all of that collapses. The bank sees the customer. The logs record the customer. And as Reuters put it, such transactions "cannot be deemed unauthorized if credentials were shared by the customer."

In audit terms, this is a loss of **attribution**, and attribution is the foundation of accountability. If you can't tell who acted, you can't tell whether they were allowed to, you can't investigate when something goes wrong, and you can't assign responsibility. It's the same reason companies ban shared admin accounts. A shared password between a person and their agent is a shared account.

### "Authorized" isn't "intended"

The most consequential detail in the coverage got the least attention. USA Today reported that Wells Fargo's updated agreement treats transactions made by a customer's authorized agents as authorized, including ones "you did not want or intend," until the customer notifies the bank and it has had a reasonable chance to act. Customers are described as solely responsible for supervising their agents.

That's a rational move for a bank, and a clear signal of where liability is heading. For decades, "authorized" meant "the customer did it or told someone to." Agents split that in two. The customer authorized the *agent*. Did they authorize *this action*? Probably not, if the agent "appeared to act independently of user instructions."

Every company deploying agents will face the same split, and most haven't written down where they stand. The banks have just shown what the default answer will be if you don't: whoever granted the access owns the outcome.

### The banks landed on least privilege

Strip away the AI and look at what the banks are converging on: **read-only access for agents, and a human approval for anything that moves money.** Citi already offers read-only access through approved open-banking providers. Moynihan wants a human in the loop on payments.

That's not a new idea. It's least privilege and segregation of duties, the two oldest controls in access management. The agent can see; a human must authorize. The agent proposes; a different identity approves. The banks didn't need a new framework for AI. They needed to apply the old one to a new kind of identity.

## What would have helped, ranked by cost

**For anyone letting agents act on behalf of people (including inside your company):**

1. **Never let an agent use a human's credentials.** If an agent needs access, it gets its own identity, with a token that's scoped, expiring and revocable. Open banking already works this way: delegated, read-only tokens instead of passwords. That's what makes Citi's middle ground possible.
2. **Make agent actions distinguishable in the logs.** Every action should record both the agent and the human it acts for. Without that, an investigation can't tell "the user did this" from "the user's agent did this."
3. **Split read from act.** Give agents read access by default. Actions that move money, delete data, send messages or change access need a separate grant, and usually a human approval.
4. **Write down who owns an agent's mistakes.** Before an incident, not after. Wells Fargo did; most internal AI programs haven't.

**For companies offering an API or platform that agents will use:**

5. **Offer a sanctioned path, or people will use the unsanctioned one.** Customers gave agents their passwords because there was no better option. Blocking alone pushes agents toward screen-scraping and credential sharing, which is harder to see.
6. **Authenticate the human for high-risk steps with something an agent can't replay.** Ping Identity's Andre Durand told USA Today that email one-time passwords are no longer enough, because agents often have access to email. Passkeys and biometrics bind the approval to a person.
7. **Detect agents, not just attackers.** JPMorgan says it is building tools to tell agents apart from customers. Behavioral signals like timing, navigation and request patterns differ between people and software, even with the same password.

## Now look inside your own company

The banks' problem is visible because it involves money. The same pattern is already inside most companies, just quieter.

An engineer gives a coding agent their personal access token. An analyst connects an assistant to their mailbox with their own session. An MCP server runs with a developer's cloud credentials. In every case, the agent is acting under a human's identity, and the logs, the access reviews and the incident response all see a human.

Ask the same questions the banks just asked:

- **Inventory:** Which agents are running in our environment, and whose credentials are they using?
- **Attribution:** If an agent took an action today, would our logs show it was the agent?
- **Scope:** Do agents have read-only access by default, with a separate, approved grant to act?
- **Approval:** Which agent actions require a human, and is that enforced technically or just written in a policy?
- **Ownership:** Who is accountable when an agent does something nobody intended?

This is exactly the review I built [agent-access-review](https://github.com/Mihirajmera/agent-access-review) to run: a user access review for AI agents and MCP servers, checking who owns each agent, what it can reach, whether it can act or only read, and whether anyone approved it. When I ran it against the [official MCP README examples](/case-studies/mcp-readme-configs/), 7 of 9 granted write, send, delete or execute permissions, and nothing in a copied config records who owns the agent or who approved that access.

## What this means for AI governance

AI governance conversations tend to focus on what models say. The banks' reaction is a reminder that the bigger risk is what agents *do*, and that the controls for that risk already exist. They were built for people, and they work only when the system knows which identity is acting.

Three principles fall out of this week:

1. **AI agents are identities.** Give them their own credentials, review their access like any privileged user's, and never let them borrow a human's.
2. **Authorization needs two parts now.** The human authorized the agent. Something still has to authorize the action, and for anything consequential that something should be a human.
3. **If you don't decide who's liable, your terms of service will.** Wells Fargo's agreement is a preview of how accountability will be allocated by default.

The banks didn't ban AI. They did what any good access review does: they found accounts they couldn't attribute, access nobody had scoped, and actions nobody had approved, and they turned it off until they could. Every company with agents should run the same review before an incident runs it for them.

*Sources: [Reuters via Hawaii Tribune-Herald](https://www.hawaiitribune-herald.com/2026/10/23/nation-world-news/us-banks-are-blocking-third-party-ai-agents-access-to-customer-accounts-sources-say/) · [Axios via Decrypt](https://finance.yahoo.com/technology/ai/articles/major-banks-rogue-ai-agents-152418947.html) · [Financial Times via Retail Banker International](https://finance.yahoo.com/news/us-banks-limit-ai-agents-113229223.html) · [USA Today](https://finance.yahoo.com/technology/ai/articles/window-vulnerability-banks-move-restrict-202731426.html) · [IBTimes UK](https://www.ibtimes.co.uk/us-banks-restrict-third-party-ai-agents-1827385). Much of the reporting relies on anonymous sources, and none of it establishes customer losses. The CISO figure is from a 2026 Palo Alto Networks study cited by USA Today.*
