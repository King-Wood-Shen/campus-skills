# campus-skills v0.1.1 — Full benchmark reports

This release adds the complete 15-scenario evaluation reports (baseline + ablation) for both v0.1 reference skills, run against the full methodology defined in [`docs/methodology.md`](docs/methodology.md).

The methodology produced informative — and in one case unexpected — findings.

## Headline numbers

### `literature-review` (common-essentials)

| Condition           | Correctness | Completeness | Expert Alignment | Actionability | Overall |
|---------------------|-------------|--------------|------------------|---------------|---------|
| Without skill       | 3.93        | 2.80         | 3.53             | 3.47          | **3.43** |
| With full skill     | 4.71        | 4.57         | 4.71             | 4.79          | **4.70** |

**Lift: +1.26 overall** (well above the +0.5 threshold the methodology asks for). Largest individual gain: completeness (+1.77).

### `experiment-rigor` (cs-ai-research)

| Condition           | Correctness | Completeness | Expert Alignment | Actionability | Overall |
|---------------------|-------------|--------------|------------------|---------------|---------|
| Without skill       | 4.53        | 4.07         | 4.40             | 3.67          | **4.17** |
| With full skill     | 5.00        | 5.00         | 5.00             | 5.00          | **5.00** |

**Lift: +0.83 overall.** With-skill responses score the maximum on every scenario, hitting a judge ceiling.

Both skills clear the publication bar. Full per-scenario tables and side-by-side raw outputs live in:
- [`plugins/common-essentials/skills/literature-review/evals/baseline.md`](plugins/common-essentials/skills/literature-review/evals/baseline.md)
- [`plugins/common-essentials/skills/literature-review/evals/ablation.md`](plugins/common-essentials/skills/literature-review/evals/ablation.md)
- [`plugins/cs-ai-research/skills/experiment-rigor/evals/baseline.md`](plugins/cs-ai-research/skills/experiment-rigor/evals/baseline.md)
- [`plugins/cs-ai-research/skills/experiment-rigor/evals/ablation.md`](plugins/cs-ai-research/skills/experiment-rigor/evals/ablation.md)

## Unexpected finding: ablations score *higher* than the full skill on `literature-review`

| Condition (literature-review)         | Overall | Δ vs. full |
|---------------------------------------|---------|------------|
| With full skill                       | 4.70    | —          |
| Ablated: Expert Knowledge removed     | 4.90    | **+0.20**  |
| Ablated: Workflow removed             | 4.98    | **+0.29**  |
| Ablated: Output Template removed      | 4.78    | +0.09      |
| Ablated: Examples removed             | 4.95    | +0.25      |

Every ablated variant outperformed the full skill. This is the methodology working as intended: the test set is sensitive enough to surface that some sections of `literature-review/SKILL.md` are net-harmful — they push responses toward verbosity that the rubric implicitly penalizes via "actionability" (tokens out went from 2376 with full skill to ~1600-2300 ablated). Mean tokens per response dropped meaningfully when sections were removed; mean rubric score went up.

This is exactly the kind of negative result the methodology was designed to catch. **A v0.2 of `literature-review` should trim Workflow and Examples sections to the smallest content that still carries the lift, then re-run the ablation to verify the dependency structure.**

`experiment-rigor` ablation results are flat (Δ between -0.00 and -0.03), suggesting the judge has ceilinged out — the skill is good enough that the rubric cannot discriminate between body variants on this test set. A larger or harder test set, or a stricter rubric, would be the natural next step there.

## Methodology proven, methodology gaps surfaced

Three takeaways from the v0.1 evaluation:

1. **Subscription-based execution works.** ~360 calls across both skills ran clean on a Claude Code subscription via the `claude -p` CLI subprocess path, with no separate Anthropic API key.
2. **The reports are domain-expert-readable.** Side-by-side raw outputs are included for the highest-delta scenarios in each skill so a real practitioner can sanity-check the LLM-as-judge verdict.
3. **The ablation framework distinguishes useful and bloat content** — at least on `literature-review`. For `experiment-rigor`, the test set is too easy to draw a finer distinction; that's a real signal about the rubric, not the skill.

## Known gotchas in this run

- **1 judge response (out of 180 for `literature-review`) failed to parse.** Cause: a string field in the judge's JSON contained an escaped apostrophe pattern that broke incremental parsing partway through. Lost 1 record on `lr-011` ablation; remaining 89 records were enough for the aggregate. Will investigate parser hardening for v0.2.
- **The judge runs at the same context as the responses.** A more rigorous setup would use a stronger judge (e.g., `--judge-model claude-opus-4-7`) and a held-out judge that can't accidentally have seen the test set. v0.2 priority.

## What's still NOT in v0.1.1

Same as v0.1.0: the other 19 planned skills are not authored yet, no CI/CD for evals, no major plugins outside CS/AI yet. v0.2 will tackle the `common-essentials` backlog and revise `literature-review` based on the ablation finding above.

## Try it

```bash
# Inside Claude Code:
/plugin marketplace add King-Wood-Shen/campus-skills
/plugin install common-essentials
/plugin install cs-ai-research      # only if you do CS/AI research
```

The skills work as-is. The ablation finding is a note for skill authors — not a problem for end users.
