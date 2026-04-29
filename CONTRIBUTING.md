# Contributing to campus-skills

Thanks for considering a contribution. This project takes skill quality seriously: a skill earns its place by demonstrating measurable improvement over baseline on a real-scenario test set. The bar applies to maintainer-written skills too — it's not arbitrary gating.

## Two kinds of contribution

1. **A new skill in an existing plugin** (e.g., adding `paper-deep-reading` to `cs-ai-research`).
2. **A new plugin for a major we don't cover yet** (e.g., `medicine-major`, `law-major`).

Both go through the same workflow.

## Workflow

### 1. Open an issue first
Before writing, file an issue describing:
- The skill name and one-paragraph purpose
- Who the target user is (which year/major)
- 3-5 concrete scenarios the skill is meant to handle
- Which expert sources you plan to anchor the skill against

This avoids duplicate work and lets maintainers point you at any existing draft.

### 2. Author the skill
Follow [docs/skill-template.md](docs/skill-template.md). Every skill directory must contain:

```
plugins/<plugin>/skills/<skill-name>/
├── SKILL.md                    # Body with frontmatter (English)
├── tests/
│   ├── scenarios.jsonl         # 10-30 real student scenarios
│   ├── adversarial.jsonl       # 5-10 edge cases
│   ├── rubric.md               # 4-dimension scoring criteria
│   └── expert-references.md    # 2-5 papers + 1-2 workflow refs
└── evals/                      # Filled in by step 3
```

`SKILL.md` body must contain four labeled sections (see template):
- **Expert Knowledge** — domain know-how grounded in references
- **Workflow** — step-by-step procedure
- **Output Template** — expected response structure
- **Examples** — 1-3 input/output demonstrations

### 3. Run the evaluation
From the repo root:

```bash
cd eval-harness
pip install -r requirements.txt
python run_eval.py --skill ../plugins/<plugin>/skills/<skill-name> --ablation
```

The harness shells out to `claude -p` (your Claude Code subscription) and writes:
- `evals/baseline.md` — skill on vs. off
- `evals/ablation.md` — contribution of each of the four components

### 4. Open the PR
Your PR description must include:
- Link to the issue
- Summary of skill purpose + 1-2 example scenarios
- The headline numbers from `baseline.md` (mean rubric scores with/without skill)
- A statement of which expert source(s) had the most influence on the final design
- Whether you're including the **typical samples** section in the report (recommended)

### 5. Review
Maintainers will look for:
- Test scenarios are realistic, not just paraphrases of the SKILL.md
- Rubric scores reflect a real lift over baseline
- Expert references are real, citable, and actually shaped the content
- The skill follows YAGNI — no padding for the sake of length

If the eval shows no clear lift, that's important data — we'd rather not ship a skill than ship one that doesn't help. We'll work with you to either revise the skill or document the negative result.

## Style

- **Language**: SKILL.md is English. PR descriptions and issues can be either English or Chinese.
- **Length**: Skill bodies should be tight. If you can't justify a paragraph against ablation, cut it.
- **Tone**: Direct, opinionated, useful. A skill is a senior colleague's advice, not a Wikipedia article.

## Code of Conduct

Be kind. Disagree about ideas, not people. Reviews are about the work, not the worth of the contributor.

## License

By contributing, you agree your contribution is licensed under [MIT](LICENSE).
