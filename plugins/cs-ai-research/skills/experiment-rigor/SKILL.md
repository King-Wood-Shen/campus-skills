---
name: experiment-rigor
description: Use when a CS/AI researcher is designing experiments or scrutinizing whether results support a claim. Covers experimental design, baselines, ablations, confounders, seeds, statistical significance, test-set contamination, and hyperparameter cheating. Triggers on "is my experiment valid", "what ablation should I run", "is this comparison fair", "do I have enough seeds".
---

## Expert Knowledge

Most empirical CS/AI papers fail not because their idea is wrong but because the experiment cannot, in principle, distinguish their idea from cheaper explanations. The job of experimental rigor is to make that distinction inevitable.

**The role of baselines.** A result is only as strong as the alternatives it beats. Sculley et al. ("Winner's Curse?", 2018) document the field's pattern of comparing complex new methods against under-tuned baselines and concluding the new method works; in many cases the old baseline, given equal hyperparameter search budget, matches or beats it. A strong baseline is one that has received the same compute, the same hyperparameter sweep, and the same evaluation protocol as the proposed method. Anything less measures budget, not insight. Two specific failure modes: (1) "the baseline as published" — using numbers from another paper run on a slightly different setup; (2) "our re-implementation of the baseline" — where the re-implementation is subtly worse than the original. Prefer running the strongest publicly available checkpoint of the baseline under your own evaluation harness.

**Ablations isolate contribution.** An ablation removes one component at a time to show that component is what's doing the work. Lipton & Steinhardt ("Troubling Trends in Machine Learning Scholarship") call out the common failure of bundling many changes into one method and claiming credit for the bundle. The minimal ablation set is determined by the claim: if you claim "component X improves performance because of mechanism Y," you need an ablation that removes X (showing performance drops) and ideally one that breaks mechanism Y while keeping X (showing the mechanism, not the parameters, is what matters). Ablations are not optional decoration; they are the load-bearing evidence for any architectural or algorithmic claim.

**Confounders specific to ML/AI.** The high-leverage ones:

- *Test-set contamination.* The test set was seen during pretraining, validation, or hyperparameter search. With internet-scale pretraining, public benchmarks (GSM8K, MMLU, HumanEval, ImageNet test images) are often in the training corpus. Symptoms: implausibly high scores, scores that improve with model scale faster than on held-out variants. Mitigation: held-out splits constructed after the model's training cutoff, paraphrased or perturbed test items, or contamination-detection probes.
- *Hyperparameter cheating.* Selecting hyperparameters on the test set, or selecting them on a "validation" set that is statistically indistinguishable from test. The Bayesian-optimization-on-test-set version of this is now common. Mitigation: declare the hyperparameter search space and budget before evaluation, and use a true held-out test split touched only once.
- *Seed sensitivity and single-seed reporting.* Henderson et al. ("Deep Reinforcement Learning that Matters", AAAI 2018) showed that in deep RL, the same algorithm with different random seeds can produce non-overlapping performance distributions; reporting one seed is essentially reporting noise. Bouthillier et al. ("Accounting for Variance in Machine Learning Benchmarks") generalize this beyond RL and show that variance from seeds, data order, and hardware nondeterminism routinely exceeds the gap between "winning" methods. Mitigation: report multiple seeds (5-10 minimum for noisy settings), give confidence intervals or interquartile ranges, never report only the max.
- *Evaluation protocol variance.* Decoding temperature, batch size, prompt formatting, tokenizer version, evaluation script version. These are not nuisance details; in LLM evaluation a prompt change can shift accuracy by 10+ points. Pin every evaluation knob and report it.
- *Hardware and numerical nondeterminism.* GPU type, CUDA version, mixed-precision settings, kernel selection. These affect both speed claims and (subtly) accuracy claims for long-running training.
- *Training-time vs. inference-time confounds.* "Method X is better" can mean better-per-FLOP, better-per-parameter, better-per-wall-clock, or better-at-fixed-quality. Always specify the comparison axis. Efficiency claims in particular are easy to dress up by switching axes between table and prose.

**Statistical significance vs. practical significance.** A small but real difference can be statistically significant with enough seeds; a large difference can fail significance with too few. ML rarely has the n to make traditional NHST informative; what matters is the *effect size relative to seed variance* and whether the confidence intervals of the two methods overlap. Dror et al. ("The Hitchhiker's Guide to Testing Statistical Significance in NLP", ACL 2018) recommend paired tests when the same examples are scored by both methods, with attention to whether assumptions (independence, normality) hold. For per-example metrics, bootstrap CIs over examples are usually more informative than parametric tests. Cohen's effect-size language (small/medium/large) is useful for keeping the question of practical significance in view: a 0.2-point gain on a 100-point benchmark with seed variance of 0.5 is noise, regardless of any p-value.

**Multiple comparisons.** If you tried 12 architectural variants and reported the best one, the probability that a random variant looks "significant" is high. Either correct (Bonferroni, Holm, BH-FDR) or pre-register the comparisons. The same logic applies to ablation tables: if the ablation set was chosen after seeing results, it is not really an ablation, it is a selection.

**Negative results and asymmetric evidence.** A failed experiment that was well-controlled is informative; a successful experiment that was poorly controlled is not. When something doesn't work, the question is whether it failed because the hypothesis is wrong or because the experiment was incapable of detecting the effect (low power, wrong metric, wrong baseline). Pre-specifying what success would look like — before running — is the cleanest way to make negative results meaningful.

**The Pineau ML Reproducibility Checklist** (used by NeurIPS) operationalizes much of the above and is worth working through line-by-line for any paper-grade experiment. The checklist's value is not in any single item but in forcing the author to externalize implicit choices.

## Workflow

Apply these steps in order. Skipping ahead is the most common failure mode.

1. **Extract the precise empirical claim.** Force the user to state the claim as a single sentence of the form "Method M improves metric K on distribution D, compared to baseline B, by amount A." If any of M, K, D, B, A is unspecified, surface that gap before doing anything else. Vague claims ("X works better") cannot be experimentally tested, only rhetorically defended.

2. **Identify what a strong baseline would be.** Ask: what is the strongest method in the literature for this task? Has it been tuned to convergence on this exact setup? If the user is comparing only against a weak or stale baseline, name the stronger one and explain why the comparison currently means little. If only published numbers are available, flag the protocol-mismatch risk.

3. **Enumerate plausible confounders.** Walk the list — test-set contamination, hyperparameter selection on test, single-seed reporting, evaluation-protocol variance, hardware effects, training-vs-inference axis switching, and any domain-specific confounders (e.g., for RL: environment version, frame stacking; for NLP: tokenizer; for systems: warm-up runs). For each, decide: real risk here, or not applicable. Don't dump the whole list — name only the confounders that actually threaten this claim.

4. **Design the minimal ablation set.** Given the claim, ask: what is the smallest set of comparisons that would force a reader to attribute the result to the proposed mechanism rather than a cheaper alternative? Typically: (a) full method, (b) method without component X, (c) baseline with budget matched to the full method. If the claim invokes a specific mechanism, add (d) a variant that keeps the component but breaks the mechanism.

5. **Specify the evaluation protocol.** Number of seeds, what each seed varies (model init, data order, both), how aggregation is reported (mean ± std, median + IQR, bootstrap CIs over examples), decoding/inference settings, evaluation set version, and how ties are broken. If the user proposes a single-seed run, push back unless the metric's seed variance is known to be negligible.

6. **Pre-register success criteria.** Before any results come in, define what would count as a positive result, a null result, and an inconclusive result. This is the single most effective defense against post-hoc reasoning. If the user resists this step, that is itself diagnostic.

7. **Sanity-check for significance and multiple comparisons.** Given the planned seed count and expected effect size, would any plausible result be distinguishable from noise? If multiple variants will be compared, plan the correction (or pre-register the primary comparison) up front.

8. **Stop and surface unknowns.** End the analysis by listing what you cannot answer with the information given (e.g., "I don't know your dataset's seed variance, so the seed-count recommendation is provisional"). Better an honest gap than a confident wrong number.

## Output Template

Respond with these six headed sections, in this order, and nothing else (no preamble, no closing pep talk):

```
**Restated Claim**
<One sentence in the form "Method M improves metric K on distribution D vs. baseline B by amount A." Note any element the user left unspecified.>

**Strong Baselines**
<2-4 bullets. The strongest comparison(s) the user should run, and why each is the right reference point. Flag any baseline currently in the plan that is too weak.>

**Minimal Ablation Set**
<2-5 bullets. Each bullet is one experimental condition. State what it removes/changes and what conclusion it would license.>

**Confounders Worth Worrying About**
<2-5 bullets. Only confounders that actually threaten this specific claim. For each: the mechanism, and the cheapest mitigation.>

**Recommended Evaluation Protocol**
<Concrete numbers: seeds, what each seed varies, aggregation (mean+/-std, bootstrap CI, etc.), decoding/inference settings, and what counts as "the same setup" across conditions.>

**Open Questions**
<Up to 4 bullets. Things the user must answer before the plan is final, or unknowns the assistant cannot resolve from the information given.>
```

Do NOT include: framework-specific code, generic statistics tutorials, motivational closers, or restatements of the user's prompt beyond the Restated Claim.

## Examples

### Example 1 (easy)

**User:** i finetuned llama-3-8b on my domain data and it gets 4 points higher on my eval than the base model. is that a real result?

**Response:**

**Restated Claim**
Llama-3-8B fine-tuned on domain data D improves accuracy on eval E by ~4 points vs. base Llama-3-8B. Unspecified: seed count, decoding settings, eval variance, whether E is held out from D.

**Strong Baselines**
- Base Llama-3-8B with the *same* prompt formatting and decoding settings used for the fine-tuned model. Prompt-format mismatch alone can move scores several points and may be the entire effect.
- Llama-3-8B with a small in-context-learning prompt drawn from D. If 4 points can be recovered with a few exemplars, fine-tuning isn't earning its keep.
- A LoRA / lightweight tune at matched compute, to separate "fine-tuning helps" from "this much fine-tuning helps."

**Minimal Ablation Set**
- Full fine-tune on D, evaluated on E.
- Base model on E with identical prompt + decoding (true baseline).
- Fine-tune on a *shuffled-label* or domain-irrelevant subset of D, same size and compute. If this also gains 4 points, the gain is from continued pretraining, not domain content.

**Confounders Worth Worrying About**
- *Eval contamination*: if E or near-duplicates appear in D, the gain is memorization. Check overlap by n-gram or embedding similarity.
- *Prompt-format drift*: fine-tuning often standardizes formatting; the base model may be losing points to formatting alone.
- *Single-seed noise*: with one fine-tune run, 4 points may be within seed variance for an 8B model on a small eval.

**Recommended Evaluation Protocol**
- Fine-tune with 3 seeds (data order + init), evaluate each on the full E.
- Report mean +/- std and the 95% bootstrap CI over examples in E.
- Pin decoding (greedy or fixed temperature/top-p) and use the *same* prompt template for base and fine-tuned.
- Fix tokenizer and eval script versions; record them.

**Open Questions**
- How large is E, and what is its per-example variance?
- Was any portion of E used during fine-tune model selection?
- Is the 4-point gain on overall accuracy or on a slice? Slice-level gains need slice-level CIs.

### Example 2 (medium)

**User:** new RL algorithm beats PPO on 4/6 atari games we tried. paper deadline in 2 weeks. what ablations do i need?

**Response:**

**Restated Claim**
Proposed RL algorithm A achieves higher final return than PPO on 4 of 6 Atari games at matched training budget. Unspecified: seed count, training budget definition (frames vs. wall-clock), which 6 games and why those, what "beats" means (final return, AUC, sample efficiency).

**Strong Baselines**
- PPO with the same hyperparameter search budget you gave A. Henderson et al. show that under-tuned PPO is the most common false-positive generator in deep-RL papers.
- A second strong baseline (e.g., IMPALA or DQN-Rainbow) on the same 6 games. Beating only PPO is weak evidence of a general advance.
- "PPO with the trick from A bolted on" if A is a modification rather than a new algorithm — this isolates the contribution.

**Minimal Ablation Set**
- A, full version (all 6 games, multiple seeds).
- A with the central novel component removed; everything else identical.
- If A introduces multiple changes (e.g., new objective + new exploration), one ablation per change. Bundling them and reporting one number is the Lipton-Steinhardt failure.
- PPO at A's exact compute and hyperparameter-search budget.

**Confounders Worth Worrying About**
- *Game cherry-picking*: 4/6 on 6 chosen games is a selection. If the 6 were chosen after seeing preliminary results, this is not evidence of generality. Pre-commit to the suite or run the standard 26/57.
- *Seed variance*: Atari results with fewer than 5 seeds are widely known to be unreliable; non-overlapping seed runs of the same algorithm are common. 3 seeds is the floor for a credible claim.
- *Evaluation protocol*: sticky actions on/off, no-op starts vs. random starts, frame skipping, evaluation episodes per checkpoint. Pin all of these across A and baselines.
- *Final-return vs. sample-efficiency confound*: "beats PPO" can mean either; choose one as primary.

**Recommended Evaluation Protocol**
- 5 seeds per (algorithm, game) cell, minimum.
- Report median + IQR across seeds (RL distributions are heavy-tailed; means are misleading). Per Agarwal et al.'s "Deep RL at the Edge of the Statistical Precipice" framing, also report aggregate metrics (IQM, optimality gap) across the game suite, not per-game win counts.
- Define training budget in environment frames, fixed across A and PPO.
- Fix evaluation: 30 episodes per checkpoint, no-op starts, sticky actions matching the standard ALE protocol.

**Open Questions**
- Were the 6 games chosen before or after seeing A's results?
- How many seeds did the current 4/6 number use?
- Is the claim about final policy quality or sample efficiency? The required ablations differ.
- With 2 weeks left, can you run 5 seeds on the standard 26-game subset, or do you need to scope the claim to a deliberately chosen subset and say so explicitly?
