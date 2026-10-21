# Writing playbook

The goal is to be the person people think of for **AI assurance: governing AI with audit-grade evidence.** Every piece should teach one thing, show proof, and connect GRC thinking to AI.

## Cadence

| Day | What | Length | Where |
|---|---|---|---|
| Mon–Thu | **Note**: one finding, one control, one idea | 150–300 words | Blog + LinkedIn |
| Friday (or every other week) | **Essay**: original research with evidence | 800–1,500 words | Blog + LinkedIn + Medium/Substack |
| Any day | Comment thoughtfully on 3–5 posts from people in AI security and GRC | 2–3 sentences each | LinkedIn |

Consistency beats volume. Four good notes a week for three months will do more than daily posts for two weeks.

## Workflow

1. **Draft** in `_drafts/<slug>.md`. Front matter: `title`, `description`, `kind: note|essay`, `status`, `tags`, optional `figures` (the first one becomes the big number on the card), `evidence`, and the `linkedin:` post text.
2. **Publish**: `python tools/publish.py _drafts/<slug>.md` moves it into `_posts/` with today's date and renders:
   - `assets/img/posts/<slug>.png`: the link-preview image (committed);
   - `linkedin-out/<slug>.png`: the 1080×1350 image to upload to LinkedIn;
   - `linkedin-out/<slug>.txt`: the LinkedIn text plus the link for the first comment.
3. **Commit and push.** GitHub Pages builds in about a minute.
4. **Post on LinkedIn**: upload the image, paste the text, and put the link in the first comment.
5. **Log it**: research and releases that aren't blog posts go in `_data/ledger.yml`; new headline numbers go in `_data/proof.yml`.

## LinkedIn checklist

- Hook in the first line: a number, a contradiction or a question. Nothing before it.
- One idea per post. Short paragraphs. End with a takeaway, not "thoughts?".
- Image: the generated card. Link: first comment.
- Post Tue–Thu, 8–10am in your time zone. Reply to every comment in the first hour.
- 3–5 hashtags, specific ones first (#AIGovernance #AISecurity #GRC).
- Never paste anything from work. Use public tools, public models and your own repos.

## Rules for credibility

- Every number links to its source: a hash, a commit, an evidence file or a citation.
- Say what you didn't test. Caveats make findings more believable, not less.
- Credit other people's ideas and names for things (for example, Simon Willison's "lethal trifecta").
- No harmful model output in public, ever. Hashes, not text.

## Backlog (30 topics)

**AI agents and access**
1. Your AI agent is a service account *(drafted)*
2. Segregation of duties for AI agents *(drafted)*
3. Pin your MCP servers like dependencies: a 5-minute fix
4. The three questions to ask before approving a new MCP server
5. Why "the client asks before each tool call" isn't a control
6. Mapping MCP risks to SOC 2 CC6 and NIST 800-53 AC-6
7. Dormant agent access: how to find tokens no one uses

**Red-teaming and evidence**
8. Twelve clean results is not a pass *(drafted)*
9. Write the risk tolerance down first *(drafted)*
10. Re-performance for AI evidence *(drafted)*
11. Hardened system prompt vs none: a before/after run (essay, uses `compare`)
12. Five open models, one test suite: which passes the OWASP LLM Top 10 controls? (essay)
13. Slopsquatting: when a model invents the package you install
14. How to sample-review a red-team detector in 30 minutes
15. A release gate for models: change management for AI

**Frameworks, translated**
16. NIST AI RMF MEASURE 2.7 in plain English
17. OWASP LLM01 vs LLM05: injection in, unsafe output out
18. What MITRE ATLAS adds that OWASP doesn't
19. EU AI Act Annex IV: the documentation checklist engineers will actually read
20. ISO 42001 for people who already know ISO 27001
21. OSCAL in 300 words: why machine-readable evidence matters

**Supply chain and engineering**
22. SLSA provenance, explained for auditors
23. What fuzzing found in my own GRC tools
24. Dependabot without the noise: a config that works
25. Reproducible evidence: why the same input should give the same hash

**Career and craft**
26. From audit testing to GRC engineering: what transferred
27. The GRC engineer's toolkit in 2026
28. How to write a control that can be tested by code
29. What auditors wish AI teams documented
30. Six months of AI assurance: what I'd tell myself on day one
