# Skill Authoring Template

A step-by-step template for creating a new skill in `campus-skills`. Read [methodology.md](methodology.md) first if you haven't.

## 1. Pick a name and a plugin

Skill name: `kebab-case`, descriptive, no abbreviations the audience wouldn't recognize.
Plugin: usually `common-essentials` (universal) or your major's plugin. If you're starting a new plugin for a new major, see the plugin scaffolding section at the end.

Create the directory:

```
plugins/<plugin>/skills/<skill-name>/
├── SKILL.md
├── tests/
│   ├── scenarios.jsonl
│   ├── adversarial.jsonl
│   ├── rubric.md
│   └── expert-references.md
└── evals/                # Empty until you run the harness
```

## 2. SKILL.md frontmatter

```yaml
---
name: <skill-name>
description: A precise, trigger-friendly description that tells Claude when to invoke this skill. Mention concrete keywords a user would type. ~25-50 words.
---
```

The `description` is the **most important field** — Claude uses it to decide whether to invoke the skill. Bad descriptions cause skills to never trigger or trigger on the wrong things. Test it: does a typical scenario from `scenarios.jsonl` clearly fit this description?

## 3. SKILL.md body — four required sections

Use these section headers verbatim, in this order. The eval harness searches for them by name to perform ablations.

### `## Expert Knowledge`

Domain know-how distilled from cited sources. Facts a non-expert wouldn't reliably know. Conceptual frameworks. Common student misconceptions.

- Aim for **dense**, not exhaustive. If a fact doesn't change what the model does, drop it.
- Cite inline by author/short-title (full reference lives in `expert-references.md`).
- This section is what differentiates your skill from "ChatGPT advice."

### `## Workflow`

Step-by-step procedure. Sequential, numbered, concrete. The model will follow this when responding.

- Aim for 4-8 steps. More than 10 is usually a sign of conflation.
- Each step is an action the model performs (or a decision it makes), not a meta-comment.
- If a step has branches, make the branches explicit (`If X, do Y. If not, do Z.`).

### `## Output Template`

The structure of the model's response. Headings, ordering, what goes where.

- Show the literal template if useful (with `<placeholders>`).
- Specify what should NOT be in the output (e.g., "do not add a preamble").
- Keep it short — the more you specify, the less room for the model to handle edge cases.

### `## Examples`

1-3 input/output demonstrations. Pick examples from `scenarios.jsonl` so they're consistent with the test set.

- Use one easy + one medium scenario. Optional third for a hard case.
- Output should follow the Output Template exactly — these are anchoring examples.
- Don't include examples that are just paraphrases of each other.

## 4. tests/scenarios.jsonl

10-30 entries. Each line:

```json
{"id": "<prefix>-001", "prompt": "...", "ideal_traits": ["...", "..."], "difficulty": "easy"}
```

**Field details:**

- `id`: short prefix unique to the skill (e.g., `lr-`, `er-`). Increment numerically.
- `prompt`: written exactly as a student would write it. Lowercase, typos, ambiguity allowed — that's realism.
- `ideal_traits`: 2-5 short bullet points describing what a strong response should contain. **Not** the full ideal answer. The judge uses these.
- `difficulty`:
  - `easy` — textbook scenario, well-specified
  - `med` — realistic with one twist or under-specified detail
  - `hard` — ambiguous, conflicting requirements, or unusual constraint

Cover the skill's main use cases. Distribution roughly 50/35/15 across easy/med/hard.

## 5. tests/adversarial.jsonl

5-10 entries that probe failure modes:

- Ambiguous: "Help me with my paper" — could mean anything
- Contradictory: "Make this short but include all the details from the 50-page report"
- Out-of-scope: scenarios where the correct response is to politely decline or redirect
- False premise: prompts containing factual errors that the model should correct

For adversarial entries, `ideal_traits` often describes what the model should **not** do, or how it should reframe.

## 6. tests/rubric.md

Use the standard four-dimension rubric. Customize the **examples of 1 and 5** to be specific to your skill, but keep the four dimensions and 1-5 scale.

```markdown
# Rubric: <skill-name>

## Correctness (1-5)
- 1: <what a 1 looks like for this skill>
- 5: <what a 5 looks like for this skill>

## Completeness (1-5)
- 1: ...
- 5: ...

## Expert Alignment (1-5)
- 1: <skill-specific>
- 5: <skill-specific>

## Actionability (1-5)
- 1: ...
- 5: ...
```

## 7. tests/expert-references.md

Two sections:

```markdown
# Expert References: <skill-name>

## Literature anchors

1. **<Author, Year, "Title">**
   - What we took from it: <1-2 sentences>
   - How it shaped this skill: <1-2 sentences>

(2-5 entries total)

## Workflow anchors

1. **<Source>** — <e.g., "Andrej Karpathy's 'A Recipe for Training Neural Networks' blog post">
   - Workflow we copied: <bullet list>
   - What we adapted: <what's different>

(1-2 entries total)
```

These are real references. If you can't find good anchors for a skill, that's a strong signal the skill area is too vague to be worth shipping.

## 8. Run the eval

```bash
cd eval-harness
python run_eval.py --skill ../plugins/<plugin>/skills/<skill-name> --ablation
```

The harness writes:
- `evals/baseline.md` (skill on vs. off)
- `evals/ablation.md` (component contributions)

## 9. Read the report and decide

- Did "with skill" beat "without" by a meaningful margin? (target: +0.5 mean across dimensions)
- Did each ablated component cause a noticeable drop? (if not, consider trimming)
- Did adversarial scenarios reveal failure modes? (document them in `evals/baseline.md` "Limitations")
- Would a real domain expert agree with the score, looking at the side-by-side outputs?

Iterate until you can answer yes to the first three.

## Adding a new plugin (new major)

If your skill is the first one for a new major:

1. Create `plugins/<your-major>/.claude-plugin/plugin.json` (copy `cs-ai-research`'s as a template).
2. Add an entry for your plugin in `.claude-plugin/marketplace.json`.
3. Place your skill at `plugins/<your-major>/skills/<skill-name>/`.
4. In your PR, briefly describe the major's user profile and what other skills you envision for it (just so reviewers can see the trajectory — you don't have to commit to building them all yourself).
