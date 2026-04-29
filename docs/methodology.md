# Methodology

This document explains the design principles and evaluation methodology that every skill in `campus-skills` must satisfy. The goal is for every skill to ship with the same evidentiary backing a small empirical paper would have: a test set, rubric-based scores, ablation analysis, and explicit expert anchoring.

## Why a methodology at all?

Skills authored by hand drift toward "what feels good to write," not "what actually helps." Without a measurement loop, prose accretes, and the document gets longer without getting better. We want the opposite: every section earns its place by surviving an ablation.

## The four-component skill body

Every `SKILL.md` body — after the YAML frontmatter — contains exactly four labeled sections in this order:

1. **Expert Knowledge** — Domain know-how distilled from cited sources. Facts, conceptual frameworks, common misconceptions.
2. **Workflow** — Step-by-step procedure: what to do first, what to do next, where to stop. Sequential and concrete.
3. **Output Template** — The structure the skill's response should take. Headings, ordering, what goes where.
4. **Examples** — 1-3 input/output demonstrations showing the workflow + template applied to realistic scenarios.

This decomposition is not arbitrary — these four are the **independently-removable components** the ablation experiment targets. If you can't decide which section your prose belongs in, that's usually a signal the prose is doing two things at once and should be split.

## Test set design

Each skill has two test sets, both stored as JSONL:

### `tests/scenarios.jsonl` (10-30 entries)
Realistic prompts a student would type. Cover the **core use cases** of the skill — not edge cases. Each entry:

```json
{"id": "lr-001", "prompt": "...", "ideal_traits": ["...", "..."], "difficulty": "easy"}
```

- `id`: short prefix tied to skill (`lr-` for literature-review, `er-` for experiment-rigor)
- `prompt`: the user-facing message exactly as a student would write it (warts, ambiguity, and all)
- `ideal_traits`: 2-5 short bullets describing what a good response should contain. **Not** the full ideal answer — just the high-leverage signals. The judge uses these.
- `difficulty`: `easy` / `med` / `hard`. Roughly: easy = textbook scenario, med = realistic with one twist, hard = ambiguous or under-specified prompt.

### `tests/adversarial.jsonl` (5-10 entries)
Edge cases designed to break naive responses:
- Ambiguous requests (could mean two different things)
- Contradictory constraints
- Out-of-scope asks (politely declining is correct)
- False premises (correcting the user is correct)

Same schema as `scenarios.jsonl`. The `ideal_traits` for adversarial entries often emphasize **what the skill should refuse to do**.

## The rubric (LLM-as-judge)

Stored as `tests/rubric.md`. Every skill uses the same four dimensions, scored 1-5:

| Dimension          | What 1 looks like                              | What 5 looks like                                          |
|--------------------|------------------------------------------------|------------------------------------------------------------|
| **Correctness**    | Factually wrong or misleading                  | Every claim is correct and verifiable                      |
| **Completeness**   | Misses the core thing the user needs           | Covers all `ideal_traits` plus appropriate context         |
| **Expert alignment** | A practitioner would push back on the approach | A practitioner would adopt this advice as written          |
| **Actionability**  | Vague — student couldn't act on it             | Student can execute the next step immediately              |

Plus a side metric (not scored, just tracked): **output token count**. We want to detect skills that get high scores by being long-winded — adding bloat that the model can't justify against ablation.

The judge call is a separate `claude -p` invocation. It receives the prompt, the response under test, and the rubric, and returns JSON with the four scores plus a one-sentence justification per dimension.

## Two layers of ablation

### Layer 1: Skill on vs. off
Run the same scenarios through `claude -p` twice:
1. **Without skill**: send the scenario prompt as-is.
2. **With skill**: prepend the skill's `SKILL.md` body to the prompt as system context (via `--append-system-prompt` or inline).

Compare mean rubric scores. If "with skill" doesn't beat "without" by a meaningful margin (e.g., +0.5 average across dimensions), the skill needs work or shouldn't ship.

### Layer 2: Internal component ablation
Run "with skill" four more times, each time with one of the four body components removed:
- Without **Expert Knowledge**
- Without **Workflow**
- Without **Output Template**
- Without **Examples**

The score drop relative to the full skill tells you which component is doing the work. If removing a section doesn't drop the score, you can probably cut it.

## Expert anchoring

Stored as `tests/expert-references.md`. Two kinds of references, both required:

1. **Literature anchors (2-5)** — Papers, books, or canonical guides the skill draws from. For each, write 1-2 sentences: *what we took from it*.
2. **Workflow anchors (1-2)** — Observations of real expert practice: a senior researcher's lab notebook, a published "how I do X" essay, a documented review process. For each, write what we copied vs. what we adapted.

This file is not just decorative. The "Expert alignment" rubric dimension explicitly checks whether the response is consistent with these references.

## The eval report — written for a domain expert

Reports go to `evals/baseline.md` and `evals/ablation.md`. They are designed to be read by a senior practitioner in the relevant field (e.g., a writing professor for `literature-review`, an ML researcher for `experiment-rigor`) — not by a software engineer. That means:

- **Executive summary** at the top in 3-5 sentences (no jargon)
- **Aggregate scores table** (rubric × condition)
- **Ablation table** (component contribution)
- **Typical samples**: 3 scenarios where the report includes the **actual model output side-by-side** (with vs. without skill). The expert reads these and forms their own judgment, independent of the LLM judge's score.
- **Limitations**: known failure modes, scenarios where the skill underperforms, anything to be cautious about.

The "typical samples" section exists because LLM-as-judge can be biased or wrong — including raw outputs lets a real expert calibrate.

## Why subscription-based execution

The harness uses `claude -p` (the Claude Code CLI's non-interactive mode) rather than the Anthropic API directly. Reasons:

- Most contributors already have a Claude Code subscription; not all have separate API credits.
- It exercises the same code path students will actually use.
- It removes a per-contribution cost barrier.

The trade-off: rate limits on subscription plans are stricter than on the API. The harness includes light backoff and per-scenario logging so a partial failure can be resumed.

## When a skill should NOT ship

Be honest about negative results. A skill should not ship if any of these are true:

- "With skill" scores are flat or worse than "without skill"
- Ablation shows zero components contributed (the skill is decorative)
- Adversarial set scores are catastrophic (skill encourages confabulation)
- Expert references are vapor — cited but didn't actually shape the content

A clean retraction is more useful than a noisy contribution.
