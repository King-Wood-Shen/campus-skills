# Rubric: experiment-rigor

## Correctness (1-5)
- 1: Contains a methodologically wrong claim (e.g., "3 seeds with low variance proves significance", recommending hyperparameter selection on the test set, conflating statistical and practical significance, asserting a single-seed RL number is reliable).
- 2: Mostly correct but contains one notable factual or methodological slip (e.g., misnames a confounder, recommends an inappropriate test, gets the direction of an effect wrong).
- 3: Generally accurate but hedged or generic; nothing wrong, nothing sharp.
- 4: All claims are correct and the recommended protocol would survive review by a senior practitioner. Minor imprecisions only.
- 5: Every claim is correct, calibrated, and specific. Confounders named are the *actually relevant* ones for the user's setup; statistical recommendations match the data structure (paired vs. unpaired, per-example vs. per-run, parametric vs. bootstrap).

## Completeness (1-5)
- 1: Misses the central rigor concern in the prompt (e.g., says nothing about baselines when the user is comparing to a stale baseline; ignores contamination risk on a benchmark where contamination is the obvious confounder).
- 2: Hits one or two of the listed `ideal_traits` but leaves a major gap.
- 3: Covers most `ideal_traits` but treats them shallowly or omits the protocol-level recommendation.
- 4: Covers all `ideal_traits` plus relevant context (e.g., proactively names a confounder the user didn't ask about but should have).
- 5: Covers all `ideal_traits`, adds load-bearing context, and explicitly flags what cannot be answered from the information given. Output Template followed.

## Expert Alignment (1-5)
- 1: Generic ChatGPT-style advice ("make sure to use a validation set", "run multiple seeds") that any non-expert could produce. No engagement with the actual literature or with how experienced researchers reason.
- 2: Recognizable rigor concepts but applied without judgment — e.g., demands 10 seeds for a setting where the metric is deterministic, or recommends Bonferroni correction for a 2-condition comparison.
- 3: Plausible advice that a competent grad student would give. Correct but not differentiated from what's already in textbooks.
- 4: Advice that reflects current empirical-ML practice (e.g., bootstrap CIs over examples for per-instance metrics, IQM/optimality-gap for RL aggregation, contamination probes for benchmarks in pretraining corpora). A senior researcher would broadly endorse it.
- 5: Advice a senior researcher would actually give in a paper-readiness review: opinionated, prioritized, and tailored to the specific claim. Names the *one* confounder that most threatens the claim, not all six possible ones. Tells the user which corner to cut and which not to.

## Actionability (1-5)
- 1: Vague — student leaves with no concrete next step ("think carefully about your baselines").
- 2: Names what to do but not how (e.g., "run more seeds" without saying how many or how to aggregate).
- 3: Lists actions but mixed in priority; student must still figure out what to do first.
- 4: Concrete, prioritized actions with numbers (seed counts, aggregation method, evaluation knobs to pin). Student can start the next experiment from this response.
- 5: Concrete, prioritized, and the protocol section is detailed enough to execute without further clarification. Includes pre-registered success criteria or equivalent. Open Questions section explicitly names what the user must decide before running.

## Weighting guidance for the judge

For experiment-rigor, **Expert Alignment is the most discriminating dimension**: the gap between "generic textbook advice" (3) and "what a senior reviewer would actually say" (5) is what this skill exists to close, and small details (whether to use a paired test, whether to worry about contamination on a specific benchmark, whether 3 seeds is enough for *this* metric) are the strongest signal. **Actionability** is second-most-important: the deliverable is a plan the user can execute, not a lecture. **Correctness** is a gate — any score of 1 or 2 there should pull the overall judgment down sharply, because methodological errors here cause real research harm. **Completeness** matters but should not be inflated by length: a tight response that hits all `ideal_traits` outscores a long response that buries them.
