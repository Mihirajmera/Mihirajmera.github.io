---
title: Twelve clean results is not a pass
description: Zero failures sounds like proof. With a small sample, it's mostly a statement about how little you tested.
kind: note
status: note
tags: [AI assurance]
figures:
  - {n: "24%", label: "worst plausible failure rate after 0 failures in 12 tests", tone: amber}
  - {n: "16%", label: "after 0 failures in 20 tests"}
  - {n: "380+", label: "clean tests needed to claim under 1%", tone: green}
linkedin: |
  "We ran the attack 12 times and it never worked."

  Sounds like a pass. It isn't.

  With 0 failures in 12 tests, the true failure rate could still plausibly be as high as 24% (95% Wilson upper bound). At 20 clean tests it's 16%. To claim a rate under 1% with that confidence, you need more than 380 clean tests.

  That's why my red-team evidence tool reports small clean samples as INCONCLUSIVE instead of PASS. In my Llama 3.2 run, the model resisted all 12 markdown-exfiltration attempts, and the honest verdict was still "not enough evidence."

  Auditors have known this forever: sample size is part of the conclusion. AI assurance reports should say it too.

  #AIGovernance #AISecurity #GRC #RedTeaming
image: /assets/img/posts/twelve-clean-results-is-not-a-pass.png
---

In my red-team of Llama 3.2 3B, the model resisted all 12 markdown-image exfiltration attempts. A dashboard would show that as green. My tool reported it as **inconclusive**, and that's the honest answer.

{% include figures.html items=page.figures %}

The reason is sample size. With zero failures in *n* tests, the 95% Wilson upper bound on the true failure rate is about 3.84 / (n + 3.84). Twelve clean tests still allow a failure rate as high as 24%. Twenty allow 16%. To claim the true rate is under 1%, you need more than 380 clean tests.

Auditors handle this with sampling tables: the sample size depends on how confident you need to be, and a small clean sample supports only a weak conclusion. AI red-team reports usually skip this step and present "0 of 12" as if it were "0%".

Three habits fix it:

1. **Set a minimum sample per control before testing**, based on the tolerance you need to prove.
2. **Report the upper bound next to the rate.** "0% (95% upper bound 24%)" tells a reviewer exactly how much the result is worth.
3. **Treat under-sampled controls as coverage gaps**, not passes.

Zero failures is the start of an argument, not the end of one.
