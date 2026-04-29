# campus-skills v0.1.0 — Proof of Concept

The first release of `campus-skills`: a research-methodology-grounded marketplace of [Claude Code](https://claude.com/claude-code) skills for university and graduate students across disciplines.

This release exists to **validate the methodology** before scaling to all 21 planned skills. It ships two reference skills end-to-end, plus the evaluation harness that future skills will go through.

## What's in v0.1.0

### Two reference skills

| Plugin              | Skill              | Purpose                                                      |
|---------------------|--------------------|--------------------------------------------------------------|
| `common-essentials` | `literature-review`| Help a student turn ~30 collected papers into a synthesis-driven review |
| `cs-ai-research`    | `experiment-rigor` | Help a CS/AI researcher pressure-test experiment design before publishing |

Each skill ships with:
- `SKILL.md` (~2400 words) anchored to 5 real, citable expert references
- 15 realistic scenarios + 7 adversarial probes (`tests/scenarios.jsonl`, `tests/adversarial.jsonl`)
- A 4-dimension rubric (`tests/rubric.md`) — correctness, completeness, expert alignment, actionability
- Real expert anchors in `tests/expert-references.md`

### Evaluation harness

`eval-harness/` is a Python harness that runs each skill's test set through the Claude Code CLI **using the user's subscription** (no separate Anthropic API key needed). It produces:

- `evals/baseline.md` — with-skill vs. without-skill comparison
- `evals/ablation.md` — contribution of each of the four `SKILL.md` body sections (Expert Knowledge / Workflow / Output Template / Examples)

Reports are written for the eyes of a domain expert, not a software engineer — they include side-by-side raw scenario outputs so a real practitioner can sanity-check the LLM-as-judge verdict.

### Methodology docs

- [`docs/methodology.md`](docs/methodology.md) — the full methodology every skill must follow
- [`docs/skill-template.md`](docs/skill-template.md) — step-by-step authoring guide
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — what a contribution PR has to demonstrate

## Smoke test result

A single-scenario run on `literature-review/lr-001` showed the methodology delivers:

| Condition           | Correctness | Completeness | Expert Alignment | Actionability | Overall |
|---------------------|-------------|--------------|------------------|---------------|---------|
| Without skill       | 5.00        | 3.00         | 4.00             | 3.00          | **3.75** |
| With full skill     | 5.00        | 5.00         | 5.00             | 5.00          | **5.00** |

The "with skill" response correctly asks for the corpus first and poses five concrete clarifying questions; the baseline gives generic structural advice without seeing the actual papers. This is what the skill is designed to do, and the methodology surfaces it cleanly.

The full 15-scenario × ablation reports for both skills will land in v0.1.1 once the maintainer has time to run them on subscription quota.

## How to try it

```bash
# Inside Claude Code:
/plugin marketplace add King-Wood-Shen/campus-skills
/plugin install common-essentials
/plugin install cs-ai-research      # only if you do CS/AI research
```

## What's NOT in v0.1.0

This is a deliberate scope. See the [roadmap](README.md#roadmap):

- The other 19 planned skills are spec'd but not authored
- No CI/CD for evals (manual, but reproducible)
- No major plugins outside CS/AI yet
- Full ablation reports for the two shipping skills are pending a longer eval pass

## Known gotchas

If you intend to author a new skill or run the harness yourself, the eval-harness has been hardened against several Windows + Claude CLI quirks (PATHEXT resolution, `CLAUDE_CODE_GIT_BASH_PATH`, argv length limits, UTF-8 stdout decoding, tool-disallow list to keep responses focused on the prompt). See `eval-harness/claude_runner.py` for the full set of fixes.

## Acknowledgements

The methodology owes a lot to the cited experts in each skill's `tests/expert-references.md` — Webster & Watson, Boote & Beile, Henderson et al., Lipton & Steinhardt, Karpathy, the NeurIPS Reproducibility Checklist, and others.
