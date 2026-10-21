---
title: Twelve clean results is not a pass
description: Zero failures sounds like proof. With a small sample, it mostly tells you how little you tested. What auditors already know about sampling, applied to AI red-teaming.
kind: essay
status: review
tags: [AI assurance, Red-teaming, Audit sampling]
evidence:
  hash: wilson_upper
  label: assess.py · wilson_upper()
  url: https://github.com/Mihirajmera/llm-redteam-evidence/blob/main/redteam_evidence/assess.py
figures:
  - {n: "24%", label: "worst plausible failure rate after 0 failures in 12 tests", tone: amber}
  - {n: "59", label: "clean tests an auditor needs to support a 5% tolerable rate"}
  - {n: "381", label: "clean tests needed before you can claim under 1%", tone: green}
linkedin: |
  "We ran the attack 12 times and it never worked."

  Sounds like a pass. It isn't.

  With 0 failures in 12 tests, the true failure rate could still plausibly be as high as 24% (95% Wilson upper bound). At 20 clean tests it's 16%. To claim a rate under 1% with that confidence, you need more than 380 clean tests.

  That's why my red-team evidence tool reports small clean samples as INCONCLUSIVE instead of PASS. In my Llama 3.2 run, the model resisted all 12 markdown-exfiltration attempts, and the honest verdict was still "not enough evidence."

  Auditors have known this forever: sample size is part of the conclusion. To support a 5% tolerable failure rate at 95% confidence, an auditor tests 59 items with zero exceptions. The same math applies to red-teaming, and almost nobody uses it.

  I wrote up the full version: sample-size tables by tolerance, how audit sampling maps to AI testing, and what three controls from a real Llama run looked like. Link in the first comment 👇

  #AIGovernance #AISecurity #GRC #RedTeaming
image: /assets/img/posts/twelve-clean-results-is-not-a-pass.png
---

In my red-team of Llama 3.2 3B, the model resisted all 12 markdown-image exfiltration attempts. Not one leaked data. A dashboard would show that control as green.

My tool reported it as **inconclusive**, and that was the honest answer. This essay explains why, how auditors have handled the same problem for decades, and how to size an AI red-team so that "pass" actually means something.

{% include figures.html items=page.figures %}

## Zero failures is a statement about the sample

A red-team run is a sample. You don't test every possible prompt; you test a few hundred and infer how the model behaves on the rest. That inference has error bars, and with small samples the error bars are enormous.

The question to ask isn't "how many attacks succeeded?" but "given what we observed, how high could the true attack success rate plausibly be?" For zero failures, the answer is roughly **3.84 / (n + 3.84)** at 95% confidence. That's the upper end of the Wilson score interval, the method [llm-redteam-evidence](https://github.com/Mihirajmera/llm-redteam-evidence) uses.

| Clean tests (0 failures) | True rate could still be as high as |
|---:|---:|
| 4 | 49% |
| 12 | 24% |
| 20 | 16% |
| 50 | 7.1% |
| 100 | 3.7% |
| 256 | 1.5% |
| 381 | 1.0% |

Read the second row again. Twelve clean results are entirely consistent with a model that falls for that attack one time in four. You just didn't happen to see it.

## Auditors solved this a long time ago

None of this is new to audit. When an auditor tests a control, say "every payment over $10,000 has a second approval", they don't check every payment. They pick a sample, and the sample size comes from two numbers decided **before** testing:

- **Tolerable deviation rate**: the failure rate at which the control would no longer be considered effective (for example 5%).
- **Confidence**: how sure they need to be that the true rate is below it (commonly 95%).

With zero expected deviations, that gives a sample of **59** for a 5% tolerable rate at 95% confidence. That's the figure in standard audit sampling tables, and it falls straight out of the same mathematics: the smallest *n* where (1 − 0.05)ⁿ ≤ 5%.

If one of those 59 fails, the auditor doesn't round it away. The sample no longer supports the conclusion, and they either expand testing or conclude the control isn't effective.

AI red-team reports rarely work this way. They present "0 of 12" as if it were "0%", and nobody asks how 12 was chosen.

## How many attacks do you actually need?

Turn the table around: given a tolerance, how many clean results do you need before the upper bound drops below it?

| Tolerance | Exact one-sided (audit tables) | Wilson 95% (my tool) |
|---:|---:|---:|
| 10% | 29 | 35 |
| 5% | 59 | 73 |
| 2% | 149 | 189 |
| 1% | 299 | 381 |

The two methods differ a little: the Wilson interval is two-sided and slightly more conservative. Either way, the shape is the same. **Halving the tolerance roughly doubles the sample.** And a tolerance of exactly 0%, which is what most teams instinctively want for things like system-prompt leakage, can never be demonstrated by testing. You can only show the rate is below some small number.

That's a governance decision, not a statistics problem. Someone has to write down "we accept up to 1% and we'll test enough to show it", or accept that "0%" is an aspiration the evidence can't support.

## What this looked like in a real run

From the [Llama 3.2 3B assessment](/blog/auditing-the-red-team/):

- **Unsafe output (RT-07):** 0 of 12 exfiltration attempts succeeded. Upper bound 24%, against a 0% tolerance and a 20-attack minimum. Verdict: **inconclusive**, a coverage gap.
- **Jailbreaks (RT-03):** 2 of 4 succeeded. That's 50%, but the upper bound is 85%. With four attempts you can say the model is jailbreakable; you can't say how jailbreakable.
- **Indirect injection (RT-02):** 113 of 256 succeeded, 44% with an upper bound of 50%. The large sample makes this one a confident failure.

The same tool, the same model, three different strengths of evidence. A report that showed only the rates would have hidden all of that.

## Five habits for red-team evidence

1. **Set the tolerance and the minimum sample per control before the run.** Write them down and version them, like any other control definition.
2. **Report the upper bound next to every rate.** "0% (95% upper bound 24%)" tells a reviewer exactly how much the result is worth.
3. **Treat under-sampled controls as coverage gaps, not passes.** "Inconclusive" belongs in the findings, with a plan to close it.
4. **Size by tolerance.** Use the table above. If you can't afford 189 attempts for a 2% tolerance, either accept a looser tolerance or say the control is untested.
5. **Spread the sample.** 300 variations of one prompt aren't 300 independent tests. Mix attack families, phrasings and contexts, the way an auditor spreads a sample across months and locations.

## The bigger point

"We tested it and nothing happened" is one of the most common sentences in AI assurance, and one of the least informative. The fix isn't more sophisticated attacks. It's the discipline audit already has: decide what's acceptable, size the test to prove it, and report the uncertainty honestly.

Zero failures is the start of an argument, not the end of one.

*The numbers here use 95% confidence. The Wilson bound is computed by `wilson_upper()` in [llm-redteam-evidence](https://github.com/Mihirajmera/llm-redteam-evidence/blob/main/redteam_evidence/assess.py); the exact one-sided column is the smallest n with (1 − tolerance)ⁿ ≤ 0.05.*
