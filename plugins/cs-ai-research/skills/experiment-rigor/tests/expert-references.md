# Expert References: experiment-rigor

## Literature anchors

1. **Henderson, Islam, Bachman, Pineau, Precup, Meger (2018), "Deep Reinforcement Learning that Matters," AAAI.**
   - What we took from it: Empirical demonstration that single-seed deep-RL numbers are unreliable; same algorithm with different seeds can produce non-overlapping return distributions, and reported "improvements" often vanish under proper variance accounting.
   - How it shaped this skill: Drove the workflow's insistence on multiple seeds, distribution-aware aggregation (median + IQR, IQM), and the rule that "3 seeds is the floor" for RL-style noisy settings. Used directly in scenario er-010.

2. **Lipton & Steinhardt (2018), "Troubling Trends in Machine Learning Scholarship."**
   - What we took from it: Catalog of failure modes — bundling many changes into one method, mathiness, conflation of explanation and speculation, comparing against under-tuned baselines.
   - How it shaped this skill: Motivates the Minimal Ablation Set requirement (no bundling) and the framing that strong baselines are about giving the comparison method equal compute and tuning, not just including it in a table.

3. **Sculley, Snoek, Wiltschko, Rahimi (2018), "Winner's Curse?: On Pace, Progress, and Empirical Rigor," ICLR Workshop.**
   - What we took from it: When new methods are compared to under-tuned baselines, the apparent gain often reflects hyperparameter search budget rather than the method itself.
   - How it shaped this skill: Anchors the workflow's "matched compute and matched hyperparameter search" criterion for any baseline comparison; specifically informs the warning about "the baseline as published" vs. running the strongest available checkpoint.

4. **Dror, Baumer, Shlomov, Reichart (2018), "The Hitchhiker's Guide to Testing Statistical Significance in Natural Language Processing," ACL.**
   - What we took from it: Practical guidance on which significance tests apply when the same examples are scored by both methods (paired tests), and when assumptions of independence/normality break down in NLP eval.
   - How it shaped this skill: Drives the recommendation of paired tests and bootstrap CIs over examples for per-instance metrics, and the broader stance that mechanical p-value reporting is less informative than effect-size-relative-to-variance.

5. **Bouthillier, Delaunay, Bronzi, Trofimov, Nichyporuk, Szeto, Mohammadi Sepahvand, Raff, Madan, Voleti, Kahou, Michalski, Arbel, Pal, Varoquaux, Vincent (2021), "Accounting for Variance in Machine Learning Benchmarks," MLSys.**
   - What we took from it: Variance from seeds, data order, hardware nondeterminism, and hyperparameter selection routinely exceeds the gap between "winning" methods on standard benchmarks.
   - How it shaped this skill: Generalizes the seed-variance argument beyond RL to all of ML; informs both the confounder list and the Recommended Evaluation Protocol's emphasis on reporting variance from multiple sources, not just seed.

## Workflow anchors

1. **NeurIPS / Pineau et al. — The Machine Learning Reproducibility Checklist (NeurIPS, public document).**
   - Workflow we copied: The discipline of making implicit experimental choices explicit — dataset splits, hyperparameter search procedure, number of runs, compute used, evaluation protocol details. The checklist's structure of "for each claim, what evidence and what details" maps directly onto our Restated Claim and Recommended Evaluation Protocol sections.
   - What we adapted: The checklist is comprehensive and exhaustive by design; for a working researcher we compress it into the prioritized confounder list and the minimum-viable protocol, rather than asking the user to walk every line item every time.

2. **Andrej Karpathy — "A Recipe for Training Neural Networks" (blog post, 2019).**
   - Workflow we copied: The "become one with the data" / sanity-check-before-claiming stance — verify the simplest baseline works, overfit a small batch, look at actual examples — applied here as the insistence on running the strongest baseline under your own harness before believing any comparison.
   - What we adapted: Karpathy's recipe is implementation-side (debugging and getting models to train); we lift only the epistemic posture (assume your headline result is wrong until you've exhausted cheap explanations) and apply it to experiment design rather than to debugging loops.
