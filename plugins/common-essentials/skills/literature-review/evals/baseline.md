# Baseline Evaluation: `literature-review`

- **Skill:** `literature-review`
- **Description:** Helps a graduate student turn a corpus of already-collected papers into a coherent, synthesis-driven literature review section or standalone review. Use for "lit review", "literature review", "synthesizing papers", "review section of my thesis", organizing sources thematically, distinguishing review from annotated bibliography, and adding critical voice. Not for literature search.
- **Generated:** 2026-04-29T06:31:59+00:00
- **Scenarios:** 1
- **Conditions evaluated:** with_skill, without_skill

## Executive Summary

With the `literature-review` skill enabled, the model's mean rubric score improved by +1.25 points (1-5 scale) compared to the same prompts run without any skill context. Average overall: **5.00** with skill vs. **3.75** without. Largest improvement: **completeness** (+2.00). Smallest improvement: **correctness** (+0.00).

## Aggregate Scores

| Condition | Correctness | Completeness | Expert Alignment | Actionability | Overall | Mean tokens out |
| --- | --- | --- | --- | --- | --- | --- |
| Without skill (baseline) | 5.00 | 3.00 | 4.00 | 3.00 | **3.75** | 761 |
| With full skill | 5.00 | 5.00 | 5.00 | 5.00 | **5.00** | 1293 |

## Typical Scenarios — Side-by-Side

Read these and form your own judgment, independent of the LLM judge's score.

### Scenario `lr-001` — difficulty: easy

**Prompt:**

> i have ~30 papers on transformer-based language models for code generation and need to write the related work section of my MS thesis. how should i structure it?

**Without skill** (overall 3.75):

> For ~30 papers, I'd go thematic rather than chronological — group by sub-problem (e.g., pre-trained code models, training data/benchmarks, evaluation, fine-tuning/alignment, downstream tasks like completion or repair) and end each subsection by pointing at the gap your thesis addresses. The main tradeoff: thematic reads naturally and shows you understand the landscape, but it can bury your contribution — so consider opening with a short paragraph that frames the section around your specific research questions, then let the themes flow from those.
> 
> If you want, share your thesis's actual research question and I can suggest a more tailored grouping (or a problem-driven structure if your contribution is narrower than the thematic buckets above).

**With skill** (overall 5.00):

> Before I propose a structure, I need to see what's actually in your corpus — drafting from imagined sources risks fabricating citations or anchoring on themes that don't match your papers.
> 
> **What I need from you:**
> 
> 1. **The reference list** — titles + abstracts is enough; full PDFs not required. If 30 feels like a lot to paste, flag the 10–15 you consider central and list the rest by title.
> 2. **Your thesis's research question or contribution** — the review's job is to motivate *your* work, so the gap statement has to point at what you're actually doing. Are you proposing a new model? A new benchmark? An empirical study of existing models? A tool built on top of one?
> 3. **Scope boundaries** — does "code generation" mean line completion (Copilot-style), full-function synthesis (HumanEval-style), repo-level agents, or all of the above? Does your corpus include pre-transformer work (e.g., seq2seq, tree-based models) for historical framing, or is it transformer-era only?
> 4. **Citation style** — numeric `[12]` (typical for ACL/NeurIPS/ICSE) or author-year (some software-engineering venues)?
> 5. **Deliverable type** — narrative review chapter (most likely for an MS thesis) or systematic review with PRISMA protocol (less common, but worth confirming if your program requires it)?
> 
> **Quick prediction so you know where I'm headed:** a transformer-for-code corpus typically clusters thematically around (a) pretraining objectives and data (Codex, CodeT5, InCoder, StarCoder lineage), (b) 
> 
> ... [truncated]


## Limitations & Failure Modes

No regressions or low-scoring scenarios were detected.
