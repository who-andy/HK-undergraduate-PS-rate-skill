# Interpreting experimental PS scores

The following **seven levels** interpret the Skill's own 70-point universal and 30-point programme-fit rubric. They are editorial descriptors only. No Hong Kong university has endorsed these levels, and they provide **no** admissions percentile, offer probability, or conversion to actual admissions score.

| Total /100 | 中文等级 | English label | Typical meaning |
|---|---|---|---|
| 95–100 | 极强 | Exceptional within this rubric | Nearly all dimensions show exceptional evidence and programme-specific reasoning. |
| 90–94 | 优秀 | Excellent | Strong, integrated intellectual evidence, thoughtful reflection and substantiated programme fit. |
| 85–89 | 很强 | Very strong | Persuasive motivation, contribution and reflection, with minor gaps. |
| 80–84 | 良好 | Good | Coherent and credible with clear room to deepen reasoning or fit. |
| 70–79 | 中等，有明显改进空间 | Developing | Basic case is visible, but substantive weaknesses remain. |
| 60–69 | 偏弱 | Weak | Considerable weakness in evidence, analysis or programme match. |
| 0–59 | 需要重构 | Needs fundamental revision | Major sections or underlying argument need rebuilding. |

**How to use the labels:**

1. The bands apply to a **complete 100-point assessment only**. If the official programme context is unavailable, report the universal subtotal **out of 70** and write **'Full level: not assessable'**. Never scale 56/70 into 80/100 or invent fit points.
2. If research is **partial**, the full score and level may be shown but must say **provisional**, list unknown source gaps and explain what could change. Synthetic fixtures are similarly non-substantive.
3. A 90/100 and 80/100 difference means 10 points **on this experimental rubric**. Show the criterion-by-criterion gap and PS quotations before claiming the difference is meaningful; independent model disagreement may be larger than the gap.
4. These labels reflect the text's apparent quality. **Submission readiness is a separate check**. A 95-point essay can still be **blocked** by a verified exceeded limit, mandatory missing section, or substantiated major factual contradiction. Do not silently discount the score or call the essay ready.
5. A potentially false achievement, word-limit uncertainty or unverified claim requires checking, **not** an automatic accusation or a guessed score cap. Identify confirmed blocking issues separately from unresolved items.
6. For >=90, explicitly substantiate strong critical reasoning, distinctive personal evidence and credible researched fit with quotations; a polished or jargon-heavy essay alone cannot justify the tier. >=95 requires near-uniform exceptional evidence across rubric criteria. **Do not impose a percentile curve**, or force any essay into an upper band.
7. If a score lies near a boundary (e.g. 84 vs 85 or 89 vs 90), say the boundary is an arbitrary reporting convention. If judges disagree or rescores fluctuate across that boundary, report both plausible labels or the uncertainty rather than pretending a one-point change is decisive.
8. Never infer official admissions competitiveness from these labels. Qualifications, references, interviews, availability, context and real review policy are not modelled here.

## Submission-check status

The evaluation JSON may include `submission_checks: {"status": "clear" | "issues_to_verify" | "blocking_issues" | "not_checked", "items": []}`. A `clear` status means the evaluator actually checked applicable published submission constraints and found no known issue, **not** a guarantee of acceptance. `blocking_issues` requires identified, evidence-backed issues and must take priority over the score-band label. `issues_to_verify` means readiness is unresolved. Omitting the field yields `not_checked`, never an implied pass.

The machine-readable band definitions are in [`rubrics/score_bands.json`](../rubrics/score_bands.json). The code performs a deterministic band lookup, but it does not decide whether the underlying LLM score is correct.
