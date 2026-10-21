---
title: Re-performance is the test AI evidence keeps failing
description: Auditors don't trust a result they can't redo. Most AI assurance evidence is a screenshot of a dashboard.
kind: note
status: note
tags: [AI assurance]
linkedin: |
  Auditors have a word for checking someone's work by redoing it: re-performance.

  It's the strongest kind of evidence. You don't trust the control owner's result; you take the same inputs, run the same test and see if you get the same answer.

  Most AI assurance evidence can't be re-performed. It's a screenshot of a dashboard, a score in a slide, a vendor's summary.

  What makes AI evidence re-performable:
  • the raw tool output, hashed so it can't be quietly swapped
  • attempt-level records, not just rates
  • the exact tool and model versions
  • the tolerance that was set before the run

  When I re-performed my own red-team results by hand, I found the detector had mis-scored 2 of 3 AutoDAN jailbreak attempts. A screenshot would never have shown that.

  #AIGovernance #Audit #GRC #AIAssurance
---

Auditors rank evidence by how much they had to trust someone else to get it. A control owner's statement is weak. A screenshot is a bit better. The strongest is **re-performance**: take the same inputs, run the test yourself and check you get the same result.

Most AI assurance evidence today can't be re-performed. It's a dashboard screenshot, a score in a slide or a summary from a vendor. There's nothing to redo.

Evidence becomes re-performable when it keeps four things:

1. **The raw tool output, hashed.** The hash proves the file a reviewer checks is the file that was assessed.
2. **Attempt-level records.** Rates hide everything. Individual attempts can be sampled and checked.
3. **Exact versions.** Tool, probes, model and configuration, so the run can be repeated.
4. **The tolerance set before the run.** Otherwise the verdict can't be re-derived.

When I [re-performed my own red-team results](/blog/auditing-the-red-team/) by hand, the detector turned out to have mis-scored 2 of 3 AutoDAN attempts. No dashboard would have surfaced that, because the dashboard *was* the detector's output.
