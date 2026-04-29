# campus-skills

A research-methodology-grounded marketplace of [Claude Code](https://claude.com/claude-code) skills for university and graduate students across disciplines.

> Each skill is anchored to expert literature, validated with scenario test sets, scored by LLM-as-judge, and analyzed through component ablations — not just hand-written prose.

## Why this exists

University and graduate students across every major share a long tail of high-leverage, AI-amenable workflows: searching literature, writing reviews, designing experiments, preparing defenses, applying to grad school, drafting emails to professors, and so on. Generic LLM advice on these tasks is uneven — it works sometimes, fails subtly other times, and you can't tell which is which without doing the work yourself.

`campus-skills` is an attempt to close that gap with **discipline-organized, expert-anchored, evaluated** skills. You install only the plugins your major needs, and every skill ships with the evidence that earned it a place in the catalog.

## Status

**v0.1 (Proof of Concept)** — building two reference skills end-to-end to validate the methodology before scaling to all 21 planned skills:

- `common-essentials/literature-review`
- `cs-ai-research/experiment-rigor`

See [the project plan](#roadmap) for the full skill catalog.

## Install

```bash
# Inside Claude Code:
/plugin marketplace add King-Wood-Shen/campus-skills
/plugin install common-essentials
/plugin install cs-ai-research      # only if you do CS/AI research
```

For local development against an unpushed copy:

```bash
/plugin marketplace add /absolute/path/to/campus-skills
```

## Repository structure

```
campus-skills/
├── .claude-plugin/marketplace.json     # Marketplace metadata
├── plugins/
│   ├── common-essentials/              # Universal student skills
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/
│   │       └── <skill-name>/
│   │           ├── SKILL.md            # Skill body (with frontmatter)
│   │           ├── tests/              # Scenarios, adversarial set, rubric, expert refs
│   │           └── evals/              # baseline.md, ablation.md (run output)
│   └── cs-ai-research/                 # CS/AI graduate research skills
├── eval-harness/                       # Python scripts that drive evaluation
├── docs/
│   ├── methodology.md                  # How a skill is designed and validated
│   └── skill-template.md               # Template a new contributor follows
└── CONTRIBUTING.md
```

## Methodology in one paragraph

Every skill ships with four components in its `SKILL.md` body — *expert knowledge*, *workflow*, *output template*, and *examples*. Authors must cite at least 2-5 expert sources (literature or workflow observations) in `tests/expert-references.md`. Quality is measured by feeding ~15 real student scenarios + ~7 adversarial scenarios through Claude both with and without the skill, and having Claude (in a separate context) score outputs against a 4-dimension rubric: correctness, completeness, expert alignment, and actionability. Ablation removes each of the four skill components in turn to identify which content actually drove the gains. Reports are written for the eyes of a domain expert — including side-by-side scenario outputs — so a real professor or senior practitioner can sanity-check the result. Read the long version in [docs/methodology.md](docs/methodology.md).

## Running an evaluation locally

The eval harness uses your **Claude Code subscription** via `claude -p` subprocess calls — no separate Anthropic API key required.

```bash
# From the repo root:
cd eval-harness
pip install -r requirements.txt

# Run baseline (skill on/off comparison) on one skill:
python run_eval.py --skill ../plugins/common-essentials/skills/literature-review

# Run with ablation:
python run_eval.py --skill ../plugins/cs-ai-research/skills/experiment-rigor --ablation
```

Reports land in `<skill-dir>/evals/baseline.md` and `<skill-dir>/evals/ablation.md`.

## Roadmap

| Version | Scope                                                              |
|---------|--------------------------------------------------------------------|
| v0.1    | 2 reference skills with full eval pipeline (POC)                   |
| v0.2    | All 11 `common-essentials` skills, including `create-academic-skill` |
| v0.3    | All 10 `cs-ai-research` skills                                     |
| v0.4    | First non-CS major plugin (medicine / law / econ / etc.)           |
| v1.0    | 5+ major plugins, mature contributor process                       |

## Contributing

Adding a skill — for your own major, or improving an existing one — is welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow. The bar is real: a contribution lands when it ships a SKILL.md that follows the template, a test set, an expert-references file, and an eval report showing it actually helps over baseline.

## License

[MIT](LICENSE)
