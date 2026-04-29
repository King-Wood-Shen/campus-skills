# Baseline Evaluation: `experiment-rigor`

- **Skill:** `experiment-rigor`
- **Description:** Use when a CS/AI researcher is designing experiments or scrutinizing whether results support a claim. Covers experimental design, baselines, ablations, confounders, seeds, statistical significance, test-set contamination, and hyperparameter cheating. Triggers on "is my experiment valid", "what ablation should I run", "is this comparison fair", "do I have enough seeds".
- **Generated:** 2026-04-29T08:07:40+00:00
- **Scenarios:** 15
- **Conditions evaluated:** ablate_examples, ablate_expert_knowledge, ablate_output_template, ablate_workflow, with_skill, without_skill

## Executive Summary

With the `experiment-rigor` skill enabled, the model's mean rubric score improved by +0.83 points (1-5 scale) compared to the same prompts run without any skill context. Average overall: **5.00** with skill vs. **4.17** without. Largest improvement: **actionability** (+1.33). Smallest improvement: **correctness** (+0.47).

## Aggregate Scores

| Condition | Correctness | Completeness | Expert Alignment | Actionability | Overall | Mean tokens out |
| --- | --- | --- | --- | --- | --- | --- |
| Without skill (baseline) | 4.53 | 4.07 | 4.40 | 3.67 | **4.17** | 973 |
| With full skill | 5.00 | 5.00 | 5.00 | 5.00 | **5.00** | 2560 |

## Typical Scenarios — Side-by-Side

Read these and form your own judgment, independent of the LLM judge's score.

### Scenario `er-013` — difficulty: hard

**Prompt:**

> theoretical claim: my new bound is tighter than prior work. should i run experiments at all?

**Without skill** (overall 2.75):

> Yes, almost always — even one small experiment that plots your bound vs. the prior bound across a few problem sizes/distributions catches proof bugs and shows whether the tightness is asymptotic-only or shows up at realistic constants. The main tradeoff is venue: pure theory tracks (COLT, STOC-style) accept theorem-only papers, but applied ML venues (NeurIPS/ICML) will ding a "tighter bound" claim that has no empirical comparison, especially if prior work had experiments.
> 
> If you tell me the setting (what kind of bound, what prior work you're comparing to), I can suggest the minimum experiment that would actually move reviewers.

**With skill** (overall 5.00):

> **Restated Claim**
> A new theoretical bound B_new is tighter than prior bound B_old over some setting S. Unspecified: whether "tighter" is uniform/asymptotic/in-constants, the regime of S, whether the bound is on a quantity that is actually measurable, and what the user wants experiments to *establish* beyond the proof.
> 
> **Strong Baselines**
> - The exact prior bound(s) you claim to beat, evaluated *symbolically* on the same problem instances — most "tighter bound" papers are undermined by reviewers plugging numbers in and finding B_old is tighter in the regime that matters.
> - A trivial bound (Markov, union bound, worst-case) plotted alongside, to show B_new is not just beating a strawman.
> - If multiple prior bounds exist with different regimes of tightness, the *minimum* over them — not the easiest one to beat.
> 
> **Minimal Ablation Set**
> Experiments are not validation for a theorem (the proof is), but they earn their keep when they answer one of these questions. Run only the ones whose answer you don't already know:
> - *Non-vacuity check*: evaluate B_new on a concrete instance to confirm it gives a non-trivial number (e.g., < 1 for a probability, < the trivial constant). Cheap, often required by reviewers.
> - *Tightness gap*: B_new vs. B_old vs. the empirical quantity itself, plotted across the regime of S. Shows where the improvement actually lives and whether it is in a regime anyone cares about.
> - *Constant-vs-rate isolation*: if the improvement is in constants, a log-log plot 
> 
> ... [truncated]

---

### Scenario `er-006` — difficulty: easy

**Prompt:**

> i ran my method 3 times and the variance is tiny so i'm confident. do i still need a baseline?

**Without skill** (overall 3.00):

> Yes — low variance tells you your method is *consistent*, not that it's *good*. Without a baseline you have no idea whether your numbers are impressive or terrible; a trivial approach (random, majority-class, last-value) might match or beat you, and you'd never know. Three runs with tight variance on the method alone is half the experiment.

**With skill** (overall 5.00):

> **Restated Claim**
> Method M produces a stable score across 3 seeds (low across-seed variance) on some task. Unspecified: the metric K, distribution D, baseline B, and the actual claim of *improvement* — "I'm confident" in what, exactly? Low variance on M alone is not a claim about M being better than anything.
> 
> **Strong Baselines**
> - Yes, you still need one. Tight variance on M tells you the score is reproducible; it tells you nothing about whether the score is *good*. A reproducible 73% is meaningless until you know whether the obvious baseline gets 70 or 75.
> - Strongest published method on this task, re-run under your exact evaluation harness (same preprocessing, metric implementation, decoding/inference settings). Don't compare against numbers from another paper — protocol drift alone moves results several points.
> - A trivial baseline (random / majority class / zero-shot / nearest-neighbor) under the same protocol. If M doesn't clearly beat trivial, the task is solved by trivial means.
> - If M modifies an existing method, the unmodified version with *matched* compute and hyperparameter-search budget. Otherwise you're measuring tuning effort, not the modification.
> 
> **Minimal Ablation Set**
> - M, full version, current seeds.
> - Strongest baseline B under identical protocol with the same seed count.
> - If M bundles multiple changes, one ablation per change. Bundling and crediting the bundle is the most common false-positive generator.
> 
> **Confounders Worth Worrying About**
> - *Vari
> 
> ... [truncated]

---

### Scenario `er-004` — difficulty: med

**Prompt:**

> we beat sota on imagenet by 0.4% top-1, training from scratch on 8 a100s. reviewers will care about this right

**Without skill** (overall 3.25):

> Honestly, a bare 0.4% top-1 on ImageNet won't carry a paper in 2026 — that's within the noise band of seed/recipe variance, and reviewers have seen too many "+0.X% SOTA" claims that didn't replicate or relied on a tuned recipe vs. an untuned baseline. What will matter is whether the gain is *robust* (multiple seeds with confidence intervals, same training recipe/epochs/augmentation as the baseline, same params/FLOPs) and whether the *method* is interesting on its own — does it transfer to downstream tasks, scale predictably, hold up under distribution shift, give a clean ablation story?
> 
> The 8×A100 angle is actually your better hook if you lean into it: framing this as "competitive at modest compute" with a clear efficiency-frontier plot tends to land better than chasing the SOTA number directly. Want help thinking through what additional experiments would shore this up before submission?

**With skill** (overall 5.00):

> **Restated Claim**
> Method M achieves +0.4% top-1 on ImageNet-1k vs. current SOTA baseline B, when trained from scratch on 8 A100s. Unspecified: which SOTA (architecture, parameter count, training recipe), seed count, training budget (epochs/wall-clock/FLOPs), whether SOTA number is reproduced under your harness or quoted from its paper, augmentation/regularization recipe, and whether 0.4% is a single run or an average.
> 
> **Strong Baselines**
> - The cited SOTA *re-trained under your exact harness* (same epochs, augmentations, optimizer schedule, eval crop, label smoothing, EMA, mixed precision). Quoting the published number while running your method in your own pipeline is the canonical Sculley "winner's curse" setup — protocol drift alone routinely accounts for 0.3–0.8% on ImageNet.
> - The same SOTA at *matched compute* to your method (same total GPU-hours, same epoch count). If you trained longer or with a richer recipe, the delta may be the recipe, not M.
> - A "recipe-only" baseline: the prior SOTA architecture trained with *your* augmentations/optimizer/schedule. ImageNet recipes (e.g., the timm A1/A2/A3 recipes, the ConvNeXt recipe, DeiT-III) move top-1 by 1–2% with no architecture change. This is the most common confound on ImageNet papers.
> 
> **Minimal Ablation Set**
> - M, full recipe, multiple seeds.
> - Baseline B, your recipe, your harness, multiple seeds (the real apples-to-apples number).
> - M with the central novel component removed; everything else identical. If the gap to
> 
> ... [truncated]


## Limitations & Failure Modes

No regressions or low-scoring scenarios were detected.
