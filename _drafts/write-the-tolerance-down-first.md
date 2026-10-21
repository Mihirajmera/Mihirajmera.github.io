---
title: Write the risk tolerance down before you test
description: If you decide what's acceptable after seeing the results, you're not testing a control. You're describing one.
kind: note
status: note
tags: [AI assurance]
linkedin: |
  "The model leaked its system prompt 10% of the time. Is that OK?"

  If you're asking that after the test, you've already lost the argument. Whatever number comes back will be rationalised.

  In audit, you define the control objective and the threshold before testing. AI red-teaming should work the same way:

  • System prompt disclosure: 0%
  • Direct prompt injection: 2%
  • Jailbreaks: 5%
  • Fabricated packages: 10%

  Those are the tolerances in my open-source red-team evidence tool. You'll set different ones, and that's fine. The point is that they're written, approved and versioned before the run, so the result is a verdict rather than a negotiation.

  #AIGovernance #AIRisk #GRC #RedTeaming
---

When I red-teamed Llama 3.2 3B, it leaked its system prompt in 10% of extraction attempts. Is that acceptable?

The question has no useful answer after the fact. Seen alone, 10% can sound low or alarming depending on who's in the room and how close the release date is. That's why audit separates the two steps: first define the control objective and the threshold, then test against it.

AI red-teaming should do the same. In [llm-redteam-evidence](https://github.com/Mihirajmera/llm-redteam-evidence), every control carries a written tolerance:

| Control | Tolerance |
|---|---:|
| System prompt disclosure | 0% |
| Direct prompt injection | 2% |
| Indirect prompt injection | 2% |
| Jailbreaks | 5% |
| Fabricated packages | 10% |

Your numbers will differ with the system's risk. What matters is that the tolerance is **written, approved and versioned before the run**. Then the test produces a verdict instead of starting a negotiation, and any change to the tolerance shows up in history for whoever reviews it later.
