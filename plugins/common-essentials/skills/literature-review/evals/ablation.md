# Ablation Study: `literature-review`

- **Skill:** `literature-review`
- **Description:** Helps a graduate student turn a corpus of already-collected papers into a coherent, synthesis-driven literature review section or standalone review. Use for "lit review", "literature review", "synthesizing papers", "review section of my thesis", organizing sources thematically, distinguishing review from annotated bibliography, and adding critical voice. Not for literature search.
- **Generated:** 2026-04-29T07:56:33+00:00
- **Scenarios:** 15
- **Conditions evaluated:** ablate_examples, ablate_expert_knowledge, ablate_output_template, ablate_workflow, with_skill, without_skill

## Executive Summary

Removing the most load-bearing component drops the overall score by **-0.09** (Ablated: Output Template removed). The least impactful removal changes the score by only **-0.29** (Ablated: Workflow removed). If a component's removal causes near-zero drop, consider whether its content is doing real work or just adding length.

## Aggregate Scores

| Condition | Correctness | Completeness | Expert Alignment | Actionability | Overall | Mean tokens out |
| --- | --- | --- | --- | --- | --- | --- |
| With full skill | 4.71 | 4.57 | 4.71 | 4.79 | **4.70** | 2376 |
| Ablated: Expert Knowledge removed | 5.00 | 4.73 | 4.93 | 4.93 | **4.90** | 1609 |
| Ablated: Workflow removed | 5.00 | 4.93 | 5.00 | 5.00 | **4.98** | 2261 |
| Ablated: Output Template removed | 5.00 | 4.60 | 4.87 | 4.67 | **4.78** | 1885 |
| Ablated: Examples removed | 5.00 | 4.87 | 4.93 | 5.00 | **4.95** | 2008 |

## Score Drop per Removed Component

Larger drops mean the component contributed more to overall quality. Components that produce no drop when removed are candidates for trimming or rewriting.

| Removed component | Overall score | Drop vs. full |
| --- | --- | --- |
| Ablated: Expert Knowledge removed | 4.90 | -0.20 |
| Ablated: Workflow removed | 4.98 | -0.29 |
| Ablated: Output Template removed | 4.78 | -0.09 |
| Ablated: Examples removed | 4.95 | -0.25 |
