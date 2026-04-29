# eval-harness

Python harness that runs the methodology defined in [../docs/methodology.md](../docs/methodology.md): for each skill, it executes the test scenarios with and without the skill, scores each output against the rubric using LLM-as-judge, and writes a domain-expert-readable report.

## Authentication

This harness uses **your Claude Code subscription** — it shells out to the local `claude` binary in `--print` (non-interactive) mode. **No `ANTHROPIC_API_KEY` is required.**

Make sure `claude --version` works in your shell before running anything here.

## Install

```bash
cd eval-harness
pip install -r requirements.txt
```

The only dependency is `PyYAML` (for parsing skill frontmatter). Everything else is the Python stdlib.

## Run

### Smoke test on a tiny subset

```bash
python run_eval.py --skill ../plugins/common-essentials/skills/literature-review --limit 2
```

This runs 2 scenarios × 2 conditions (with/without) = 4 model calls plus 4 judge calls. Use this to confirm the harness works before committing to a full run.

### Full baseline (with vs. without skill)

```bash
python run_eval.py --skill ../plugins/common-essentials/skills/literature-review
```

For 15 scenarios this is 30 model calls + 30 judge calls = ~60 total `claude -p` invocations.

### Full baseline + ablation (the headline run)

```bash
python run_eval.py --skill ../plugins/cs-ai-research/skills/experiment-rigor --ablation
```

Adds 4 ablation conditions (one per removed component) on top of with/without. For 15 scenarios this is 90 model calls + 90 judge calls = ~180 total.

### Include adversarial scenarios

```bash
python run_eval.py --skill <skill-dir> --ablation --include-adversarial
```

Adds the 5-10 adversarial scenarios from `tests/adversarial.jsonl`.

## Outputs

For a skill at `plugins/<plugin>/skills/<name>/`:

```
plugins/<plugin>/skills/<name>/
├── evals/
│   ├── baseline.md           # With vs. without skill (always written)
│   └── ablation.md           # Component contributions (only if --ablation)
└── ...
eval-harness/
└── runs/
    └── <skill-name>-<timestamp>/
        └── results.jsonl     # Raw per-scenario records (kept for traceability)
```

The `runs/` directory is gitignored. `evals/baseline.md` and `evals/ablation.md` should be committed alongside the skill.

## Modules

- [`run_eval.py`](run_eval.py) — CLI entry point, orchestrates the run loop
- [`skill_loader.py`](skill_loader.py) — parses `SKILL.md` into frontmatter + four named sections
- [`ablation.py`](ablation.py) — generates the four ablated body variants
- [`claude_runner.py`](claude_runner.py) — wraps `claude -p` subprocess with retries; defines the judge JSON schema
- [`judge.py`](judge.py) — composes the judge prompt and parses the score
- [`report.py`](report.py) — writes domain-expert-readable markdown reports

## Common flags

| Flag                       | Effect                                                          |
|----------------------------|-----------------------------------------------------------------|
| `--skill <path>`           | Required. Path to a skill directory.                            |
| `--ablation`               | Also run the four component-ablation conditions.                |
| `--include-adversarial`    | Add the adversarial scenario set.                               |
| `--limit N`                | Only run the first N scenarios (smoke testing).                 |
| `--model <name>`           | Override the model for both responses and judge.                |
| `--judge-model <name>`     | Override only the judge model.                                  |
| `--sleep <seconds>`        | Sleep between calls (default 1.0). Increase if you hit rate limits. |

## Rate limits

Claude Code subscription plans have rate limits. The harness sleeps `--sleep` seconds between calls (default 1.0s). If you see rate-limit errors:

1. Increase `--sleep` (try 5.0)
2. Or run with `--limit` to break a large run into batches
3. Or split a run by skipping `--ablation` first, then doing a follow-up `--ablation`-only pass

The harness retries each call up to 2 times with exponential backoff before giving up.

## What the report looks like

The `baseline.md` report contains:

1. **Executive summary** — 3-5 sentences with the headline lift and any caveats
2. **Aggregate scores table** — rubric × condition
3. **Typical scenarios — side-by-side** — 3 scenarios with raw outputs from both conditions, so a domain expert can sanity-check independently of the judge
4. **Limitations & failure modes** — regressions and low-scoring scenarios

The `ablation.md` report adds:

1. **Score drop per removed component** — which of the four sections actually carries the load

These are written for the eyes of a senior practitioner in the relevant field, not a software engineer.
