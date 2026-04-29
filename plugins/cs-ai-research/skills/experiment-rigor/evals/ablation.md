# Ablation Study: `experiment-rigor`

- **Skill:** `experiment-rigor`
- **Description:** Use when a CS/AI researcher is designing experiments or scrutinizing whether results support a claim. Covers experimental design, baselines, ablations, confounders, seeds, statistical significance, test-set contamination, and hyperparameter cheating. Triggers on "is my experiment valid", "what ablation should I run", "is this comparison fair", "do I have enough seeds".
- **Generated:** 2026-04-29T08:07:40+00:00
- **Scenarios:** 15
- **Conditions evaluated:** ablate_examples, ablate_expert_knowledge, ablate_output_template, ablate_workflow, with_skill, without_skill

## Executive Summary

Removing the most load-bearing component drops the overall score by **+0.03** (Ablated: Output Template removed). The least impactful removal changes the score by only **+0.00** (Ablated: Examples removed). If a component's removal causes near-zero drop, consider whether its content is doing real work or just adding length.

## Aggregate Scores

| Condition | Correctness | Completeness | Expert Alignment | Actionability | Overall | Mean tokens out |
| --- | --- | --- | --- | --- | --- | --- |
| With full skill | 5.00 | 5.00 | 5.00 | 5.00 | **5.00** | 2560 |
| Ablated: Expert Knowledge removed | 5.00 | 5.00 | 5.00 | 5.00 | **5.00** | 2321 |
| Ablated: Workflow removed | 5.00 | 5.00 | 5.00 | 4.93 | **4.98** | 2536 |
| Ablated: Output Template removed | 5.00 | 5.00 | 5.00 | 4.87 | **4.97** | 2384 |
| Ablated: Examples removed | 5.00 | 5.00 | 5.00 | 5.00 | **5.00** | 2975 |

## Score Drop per Removed Component

Larger drops mean the component contributed more to overall quality. Components that produce no drop when removed are candidates for trimming or rewriting.

| Removed component | Overall score | Drop vs. full |
| --- | --- | --- |
| Ablated: Expert Knowledge removed | 5.00 | +0.00 |
| Ablated: Workflow removed | 4.98 | +0.02 |
| Ablated: Output Template removed | 4.97 | +0.03 |
| Ablated: Examples removed | 5.00 | +0.00 |
