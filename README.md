# PS Evaluator Skill v0.4.0

[简体中文](README.zh-CN.md)

A portable, **research-first** Agent Skill for undergraduate personal statements. It supports Hong Kong universities and other institutions with one shared scoring workflow. **No major profiles or university-specific scoring weights are hardcoded.** The five Hong Kong universities have a dated 2027 PS submission-rule baseline, while Major Fit remains researched dynamically. The agent researches the specific programme's current official requirements and curriculum, and then assesses the essay against that evidence.

## Why dynamic research?

Universities and routes vary in whether a statement is required, its length, whether multiple programme choices share one essay, and which additional materials are needed. Public curriculum details do not disclose secret internal PS scoring weights. This Skill explicitly distinguishes official facts from inferred programme fit signals.

## Hong Kong five: 2027 application-rule baseline

The included [`requirements/hk-five-2027.json`](requirements/hk-five-2027.json) and [source-linked notes](references/hk-five-requirements.md) cover HKU, CUHK, HKUST, CityUHK and PolyU, scoped to international/non-HKDSE admissions such as A-Level. Key differences: HKU 1,000 **words** shared; CUHK 6,000 **characters** shared (Medicine exception); HKUST PS required but no general limit verified; CityUHK FAQ mentions **per-programme Applicant Statement** without a verified universal limit; PolyU PS optional for most programmes. Every target, route and major must be rechecked on current official pages.

## Workflow

1. Identify university, exact programme, intake, qualification route and shared-PS programme choices.
2. Research official English admissions instructions and degree curriculum, recording sources and unknowns. Generate a provisional or verified **research snapshot** for this evaluation, outside the public Skill directory.
3. Grade common writing quality using the 70-point universal rubric; evaluate each programme's fit against the verified research on a separate 30-point rubric. These weights are experimental and are **not** universities' admissions weights.
4. Report evidence, risk flags, submission constraints and confidence, without assigning admission probabilities.
5. Compare drafts, assess cross-major fit or run benchmark tests when asked.

If official programme context cannot be verified, report a universal-only evaluation and show unknowns instead of inventing programme criteria. Multiple programmes sharing a statement receive identical universal scores for an unchanged essay, plus separate fit analysis.

## What do scores mean?

The following **experimental editorial levels** describe quality within this Skill's 70+30 framework. They are not universities' marking scales, applicant percentiles or admission probabilities.

| Full score | Level |
|---|---|
| 95–100 | Exceptional within this rubric |
| 90–94 | Excellent |
| 85–89 | Very strong |
| 80–84 | Good |
| 70–79 | Developing |
| 60–69 | Weak |
| 0–59 | Needs fundamental revision |

For evidence anchors and how to interpret **90 versus 80**, see [score interpretation](references/score-interpretation.md). A programme that cannot be researched yields only /70, without a full score or level. Partial research yields a provisional level. Confirmed length or integrity issues remain submission blockers whatever the numerical grade. Language quality contributes 5 points of the universal 70.

## Installation

From this repository, install the independent `ps-evaluator` Skill with a compatible Skills CLI:

```bash
npx skills add who-andy/HK-undergraduate-PS-rate-skill --skill ps-evaluator
```

Or copy the repository root into a compatible agent's skills directory, such as `~/.agents/skills/ps-evaluator/` (Codex) or `~/.claude/skills/ps-evaluator/` (Claude Code). It does not require AIOS or an API key.

## Example

> Use ps-evaluator to assess this PS for [University], [exact Programme], 2027 international A-Level entry. First research the official admissions rules and curriculum, cite sources, then score writing and programme fit. Check whether this single statement must cover two programme choices.

## Deterministic tests

```bash
python3 scripts/validate_profiles.py --root .
python3 -m unittest discover -s tests -v
python3 scripts/aggregate_scores.py --rubrics . --input examples/evaluations.synthetic.json
python3 scripts/benchmark.py --input examples/benchmark.synthetic.json
```

Python scripts only validate/aggregate model-generated records. They **do not** browse the web, conduct an AI evaluation or prove admissions prediction accuracy. Examples are fully synthetic.

See [research protocol](references/research-protocol.md), [rubric methodology](references/methodology.md), and [evaluation schema](references/output-schema.md).

## Privacy

Never publish an applicant's real statements or personal details without explicit consent. Save user-specific research snapshots and evaluation reports outside the public Skill repository. The Skill is model-provider independent.
