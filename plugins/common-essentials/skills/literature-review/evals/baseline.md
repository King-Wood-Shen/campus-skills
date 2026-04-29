# Baseline Evaluation: `literature-review`

- **Skill:** `literature-review`
- **Description:** Helps a graduate student turn a corpus of already-collected papers into a coherent, synthesis-driven literature review section or standalone review. Use for "lit review", "literature review", "synthesizing papers", "review section of my thesis", organizing sources thematically, distinguishing review from annotated bibliography, and adding critical voice. Not for literature search.
- **Generated:** 2026-04-29T07:56:33+00:00
- **Scenarios:** 15
- **Conditions evaluated:** ablate_examples, ablate_expert_knowledge, ablate_output_template, ablate_workflow, with_skill, without_skill

## Executive Summary

With the `literature-review` skill enabled, the model's mean rubric score improved by +1.26 points (1-5 scale) compared to the same prompts run without any skill context. Average overall: **4.70** with skill vs. **3.43** without. Largest improvement: **completeness** (+1.77). Smallest improvement: **correctness** (+0.78).

## Aggregate Scores

| Condition | Correctness | Completeness | Expert Alignment | Actionability | Overall | Mean tokens out |
| --- | --- | --- | --- | --- | --- | --- |
| Without skill (baseline) | 3.93 | 2.80 | 3.53 | 3.47 | **3.43** | 1372 |
| With full skill | 4.71 | 4.57 | 4.71 | 4.79 | **4.70** | 2376 |

## Typical Scenarios — Side-by-Side

Read these and form your own judgment, independent of the LLM judge's score.

### Scenario `lr-015` — difficulty: hard

**Prompt:**

> phd lit review on language model evaluation. theres a methodological civil war in this corpus between benchmark people and red-teaming people. they barely cite each other. how do i handle that

**Without skill** (overall 1.00):

> (File-writing tools aren't available in this session, so I can't persist a memory of your project — flagging so you know.)

**With skill** (overall 5.00):

> The non-citation pattern *is* the most interesting thing in your corpus. Don't paper over it — make it the spine of the review.
> 
> **Recommendation: methodological organization at the top level.** This is exactly the case where it's the right scheme — your field's main fault line really is *how* people evaluate, not *what* they evaluate. Have a section explicitly named for the divide (something like "Two evaluation paradigms and the gap between them"), and treat the absence of cross-citation as evidence to analyze, not a hole to hide.
> 
> **The tradeoff:** this commits you to taking the divide seriously as a structural fact, which means you can't stay neutral. You'll have to characterize what each camp's methodology can and can't see, and your committee will expect you to stake out where *your* work sits — bridging, partisan, or orthogonal. If you're not ready to take that position, a thematic scheme that quietly notes the split is safer but reads as less mature, and it tends to flatten the very tension that makes the lit review worth reading.
> 
> **Three concrete moves:**
> 
> 1. **Diagnose the split early, in your own voice.** Open with a paragraph naming what each camp prizes: benchmarks → reproducibility, scalable measurement, cumulative leaderboards; red-teaming → ecological validity, adversarial coverage, harms that aren't yet operationalizable. Their disagreement isn't really about findings — it's about *what counts as evidence*. Naming that explicitly is what distinguishes a seni
> 
> ... [truncated]

---

### Scenario `lr-012` — difficulty: med

**Prompt:**

> biology phd, lit review on CRISPR off-target effects, 35 papers ranging from 2014 mechanistic work to 2023 clinical trial reports. structure?

**Without skill** (overall 1.50):

> I don't have Write available in this session, so I'll skip the memory save. My structural recommendation above stands — let me know if you want to share the paper list and I'll sketch a section-level outline.

**With skill** (overall 5.00):

> **Diagnosis of the corpus (tentative — without seeing the actual list)**
> A 2014→2023 CRISPR off-target corpus typically clusters along three fault lines: *detection methodology* (in silico prediction → biochemical assays like CIRCLE-seq/SITE-seq → cellular GUIDE-seq → in vivo DISCOVER-seq/VIVO), *engineering responses* (high-fidelity Cas9 variants, base editors with their own DNA/RNA off-target profiles, prime editing), and *translational assessment* (preclinical specificity panels → clinical trial reports for sickle cell, β-thalassemia, etc.). This field has a real chronological arc — early mechanistic work genuinely *enabled* later clinical assessment — but a pure chronology will read as a timeline rather than an argument. Recommended scheme: **thematic at the top level, with chronological evolution surfaced inside each theme**.
> 
> **Proposed structure**
> - *Defining and detecting off-targets* — claim: detection methodology has been the rate-limiting step; what counts as an "off-target" has shifted with each new assay generation.
> - *Mechanistic determinants* — claim: mismatch tolerance, DNA/RNA bulges, chromatin context, and gRNA concentration jointly govern off-target activity, but their relative weights remain contested.
> - *Engineering solutions and their new problems* — claim: high-fidelity variants reduced canonical off-targets but base/prime editors introduced *new* classes (deaminase-driven RNA edits, guide-independent DNA edits) the early frameworks didn't anticipate.
> -
> 
> ... [truncated]

---

### Scenario `lr-001` — difficulty: easy

**Prompt:**

> i have ~30 papers on transformer-based language models for code generation and need to write the related work section of my MS thesis. how should i structure it?

**Without skill** (overall 3.00):

> For a thesis-length related work, I'd recommend a **thematic structure organized to motivate your contribution** — typical buckets are (1) model architectures/scaling, (2) pretraining objectives and data curation for code, (3) evaluation benchmarks (HumanEval, MBPP, etc.), and (4) the specific subarea your thesis sits in (e.g. repo-level context, RLHF for code, retrieval-augmented generation). Within each bucket, go roughly chronological so the reader sees the trajectory.
> 
> The main tradeoff: thematic reads better and frames your gap clearly, but it requires you to already know your thesis's contribution sharply enough to pick buckets that converge on it — a purely chronological structure is easier to draft but tends to read like an annotated bibliography.
> 
> If you want, tell me your thesis's specific contribution and I can suggest concrete section headings tuned to it.

**With skill** (overall 5.00):

> **Diagnosis of the corpus**
> I can't see your specific 30 papers, but a corpus on transformer-based LMs for code generation almost certainly clusters around: (a) model architectures and pre-training (Codex, CodeT5, CodeBERT, StarCoder, Code Llama, etc.), (b) code-specific pre-training objectives (fill-in-the-middle, identifier prediction, span corruption), (c) evaluation benchmarks and their limitations (HumanEval, MBPP, APPS, SWE-bench, LiveCodeBench), (d) post-training/alignment (instruction tuning, RLHF, execution-feedback RL), and (e) inference-time strategies (sampling, self-repair, agentic loops). The field has moved fast (2021→2026) but the *story* isn't really chronological — the same debates recur. Recommended scheme: **thematic**, with chronology surfaced only where a clear paradigm shift happened (e.g., decoder-only displacing encoder-decoder for generation, or the 2024+ shift toward agentic evaluation).
> 
> **Proposed structure**
> - *Architectures and pre-training paradigms* — claim: the field has consolidated on decoder-only transformers, with the substantive variation now in data and objectives, not architecture.
> - *Code-specific pre-training objectives and data* — claim: FIM and identifier-aware objectives produce measurable gains over naive language modeling, but their relative contribution remains entangled with data scale.
> - *Evaluation: from function-completion to repository-scale* — claim: HumanEval-style benchmarks are saturated and increasingly misleading; SW
> 
> ... [truncated]


## Limitations & Failure Modes

**Regressions** (skill scored worse than baseline):
- `lr-003`: with-skill 1.50 vs. without-skill 4.75

**Low-scoring scenarios with skill** (overall < 3.0):
- `lr-003`: 1.50
