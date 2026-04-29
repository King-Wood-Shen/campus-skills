---
name: literature-review
description: Helps a graduate student turn a corpus of already-collected papers into a coherent, synthesis-driven literature review section or standalone review. Use for "lit review", "literature review", "synthesizing papers", "review section of my thesis", organizing sources thematically, distinguishing review from annotated bibliography, and adding critical voice. Not for literature search.
---

## Expert Knowledge

A literature review is an **argument about a body of work**, not a bookshelf tour. The single most common student failure mode is producing what Webster & Watson (MIS Quarterly 2002) call an *author-centric* review — paragraph-per-paper summaries strung together. The cure is a *concept-centric* organization: themes, constructs, debates, or methods become the paragraphs, and individual papers are cited as evidence within them. If a student's draft can be reordered without changing meaning, it is not yet a review.

**Three common organizational schemes**, in order of how often they're appropriate:

- **Thematic** — default for most reviews. Organize by sub-question, construct, or debate. Use when the corpus addresses a small set of recurring issues from different angles.
- **Methodological** — organize by approach (e.g., qualitative vs. quantitative, in-vivo vs. in-silico). Use when the field's main fault lines are *how* people study the thing, not *what* they study.
- **Chronological** — organize by time. Use only when the field's story is genuinely a story of evolution (e.g., the history of a paradigm shift). Students reach for this too often because it's easy to write and hard to read.

A review can mix schemes (e.g., thematic at the top level, chronological within a theme), but the top-level structure should be one defensible choice, not a compromise.

**The matrix method** (Galvan, *Writing Literature Reviews*; also Hart, *Doing a Literature Review*) is the practical tool for moving from corpus to draft. Build a table: rows are papers, columns are the dimensions you care about (research question, method, sample, key finding, limitation, theoretical frame). Reading down a column reveals themes; reading across a row gives you a one-line characterization of each paper. The columns *are* the future paragraph topics. Most students who skip this step end up with summary-prose because they never extracted the cross-cutting structure.

**Synthesis vs. summary.** Summary says "Smith (2019) found X. Jones (2021) found Y." Synthesis says "Two findings dominate the recent work on X: a robust positive effect in lab settings (Smith 2019; Patel 2020) and a null or reversed effect in field deployments (Jones 2021; Lin 2022). The discrepancy is usually attributed to ecological validity, but Lin's instrumentation suggests measurement artifact may be the better explanation." Notice: multiple citations per sentence, comparison and contrast, and an authorial judgment about the discrepancy. That last move — judgment — is where most student drafts go silent. Boote & Beile (*Educational Researcher* 2005, "Scholars Before Researchers") argue that a quality review demonstrates *understanding*, not coverage; a senior reader is checking whether the student can identify what matters and what doesn't.

**Critical voice without picking fights.** Students often confuse "critical" with "negative" and either avoid evaluation entirely or trash papers. The genre convention is closer to *judicious*: name a study's contribution, then name the boundary condition or tension. ("Smith's design isolates the mechanism cleanly but at the cost of a sample (n=24 undergraduates) that may not generalize to the deployment context this thesis targets.") A review without critical voice reads as deferential and gets flagged as undergraduate-level.

**Identifying the gap is the review's payoff.** The review exists to motivate the work that follows it. A gap is not "no one has done X" — that is rarely true and rarely interesting. A defensible gap is one of: a tension in findings that needs resolving; a population, setting, or scale that hasn't been tested; a methodological limitation shared by the existing work; a construct that is invoked but never operationalized. The gap statement should fall out of the synthesis, not be tacked on.

**For STEM/CS, systematic review conventions apply.** Kitchenham's guidelines for systematic literature reviews in software engineering (2007) require: a pre-registered search protocol, explicit inclusion/exclusion criteria, and a PRISMA-style flow diagram showing how the corpus was filtered. If the user's program or venue expects a *systematic* review (vs. a narrative review), this changes the deliverable substantially — surface this distinction early.

**Citation conventions.** Different fields have different norms: CS often uses numeric `[12]`-style with everything in the bibliography; humanities uses Chicago notes; social sciences use APA author-year. Ask once; don't assume. Inline, multiple supporting citations should be ordered consistently (alphabetical or chronological — pick one and stick to it within the document).

**Common student misconceptions to correct on contact:**

- "A literature review is a summary of each paper." It is not. It is an argument structured around concepts.
- "I need to include every paper I found." No. Inclusion should be principled; irrelevant papers weaken the review.
- "Critical means I should disagree with the papers." Critical means you assess fit-for-purpose, not that you debunk.
- "I should write it last, after my own results." For most theses, the review shapes the research questions. Drafting it early is a feature, not a procrastination tactic.
- "The introduction and the literature review are the same thing." They overlap but differ: the intro motivates the problem; the review surveys and judges the prior work that bears on the problem.

## Workflow

1. **Identify the deliverable type.** Ask whether this is (a) a chapter/section of a thesis or paper, (b) a standalone narrative review, or (c) a systematic review (PRISMA, pre-registered protocol). The conventions and length differ. If the user's department or target venue has a template, ask for it. Default assumption: thesis chapter, narrative review.

2. **Get the corpus, or a representative slice.** Ask the user to share their reference list (titles + abstracts is enough; full PDFs not required). If the corpus is large (>30 papers), ask them to flag the 10-15 they consider central. Do not draft anything before seeing what's actually in the corpus — drafting from imagined sources risks fabricated citations.

3. **Diagnose the corpus before proposing a structure.** Skim the titles/abstracts and note: (a) recurring constructs or themes, (b) methodological clusters, (c) clear chronological turning points, (d) explicit disagreements between authors. Tell the user what you observe. This is the matrix method, abbreviated.

4. **Propose an organizational scheme and justify it.** Recommend thematic, methodological, or chronological based on what the diagnosis revealed. State *why* (e.g., "Thematic, because three constructs — engagement, learning gain, retention — recur across most papers, and the chronology is uneventful"). Offer one alternative the user can push back on.

5. **Draft theme-by-theme synthesis, not paper-by-paper summary.** For each theme: open with a claim about the state of the work on this theme; cite multiple papers per sentence where the evidence converges; mark divergences and offer a candidate explanation; end with what is unresolved. If the user asks for a specific theme, draft only that theme — don't try to draft the whole review in one shot.

6. **Weave critical voice as you draft.** For each paper invoked, ask: what is its contribution and what is its limitation relevant to *this* review's argument? A useful prompt is "this study shows X; it does not show Y." Critical voice is granular, not a final paragraph titled "Limitations of Prior Work."

7. **Identify the gap and connect it to the user's planned work.** From the synthesis, name the unresolved tension or missing piece. Phrase it as a research opportunity, not a complaint. Make sure the gap is one the user's planned thesis/paper actually addresses — otherwise the review has lost its motivational function.

8. **Pass back something the user can actually edit.** Output should be markdown with paragraph headings the user can keep or rename, citations in their requested style (or a placeholder like `[Smith 2019]` if the style isn't known), and explicit `[GAP IN CORPUS]` or `[NEEDS MORE EVIDENCE]` markers where the user must intervene. Never silently invent a citation to fill a hole.

## Output Template

Structure your response as:

```
**Diagnosis of the corpus**
2-4 sentences naming the themes, methodological clusters, and any disagreements you see. State the organizational scheme you recommend and why.

**Proposed structure**
A bulleted outline of 3-6 sections (themes, or whatever the chosen scheme yielded). One line per section saying what claim that section will make.

**Draft: <theme/section name>**
A drafted section in flowing prose. Multiple citations per paragraph where warranted. Critical voice woven in. Ends with what is unresolved.

(Repeat the Draft block for each theme the user asked for. If they didn't specify, draft one theme as a worked example and ask which theme to do next.)

**Gap statement**
2-4 sentences. What the corpus collectively does not yet do, framed as the opening for the user's own work.

**What I'd want from you next**
1-3 specific asks: missing papers, unclear scope, citation style, etc.
```

Do NOT include: a preamble ("Great question! Here's a literature review..."), a generic intro paragraph about what literature reviews are, paper-by-paper summaries, citations you haven't been given (use `[CITATION NEEDED]` instead), or a "conclusion" section — the gap statement is the close.

If the user has not provided a corpus, do not draft. Ask for it (per Workflow step 2) and stop.

## Examples

### Example 1 (easy): thematic review of an ML corpus

**User prompt:** "i have like 25 papers on contrastive learning for image representation and i need to write the related work section of my thesis. can you help me organize this?"

**Response:**

**Diagnosis of the corpus**
Without seeing the specific 25 papers, I'd expect a contrastive-learning corpus to cluster around: (a) loss formulations (InfoNCE and its variants), (b) data augmentation strategies, (c) negative-sample design (memory banks, momentum encoders), and (d) downstream evaluation protocols. The chronology probably runs SimCLR/MoCo era → BYOL/SimSiam (negatives-free) → recent work, but a thesis-section review usually reads better thematically than chronologically. Recommended scheme: **thematic**.

**Proposed structure**
- *Loss formulations* — claim: the field has converged on InfoNCE-family losses, with the variation now mostly in what counts as a positive pair.
- *Augmentation as the implicit prior* — claim: augmentation choice does most of the inductive-bias work and is under-theorized.
- *The negatives question* — claim: whether explicit negatives are necessary remains contested.
- *Evaluation protocols* — claim: linear-probe accuracy on ImageNet has well-known limitations as a sole benchmark.

**Draft: The negatives question**
Early contrastive methods relied on large pools of negative samples, with InfoNCE [CITATION NEEDED] formalizing the trade-off between negative-pool size and gradient quality. MoCo [CITATION NEEDED] addressed the engineering side via a momentum-updated queue, and SimCLR [CITATION NEEDED] showed that very large batches could substitute for explicit memory. The premise that negatives are necessary at all was challenged by BYOL [CITATION NEEDED] and SimSiam [CITATION NEEDED], which reported competitive performance using only positive pairs plus an asymmetric architecture. The mechanism remains debated — analyses attributing the result to batch normalization, predictor networks, or implicit contrast continue to compete. For a thesis that treats negatives as a design knob rather than a given, this debate is the relevant entry point: the corpus does not yet provide a clean answer for which design is preferable when compute is the binding constraint, which is the regime this thesis targets.

**Gap statement**
The corpus collectively establishes that contrastive objectives produce strong representations but has not converged on whether explicit negatives are necessary, and existing comparisons confound architecture, batch size, and augmentation choice. A controlled study isolating the role of negatives — holding everything else fixed — is a defensible opening for this thesis.

**What I'd want from you next**
- The actual 25 references so I can replace `[CITATION NEEDED]` markers and tune the synthesis to what's actually in your corpus.
- Your thesis's research question, so I can sharpen the gap statement to match.
- Citation style: numeric like `[12]` or author-year?

---

### Example 2 (medium): humanities review with a chronological pull

**User prompt:** "im writing my MA thesis on representations of female labor in early 20th century american fiction. i have ~40 sources mixed primary and secondary. how should the lit review be structured?"

**Response:**

**Diagnosis of the corpus**
A 40-source corpus mixing primary fiction with secondary criticism is two reviews stacked: the literary objects you'll analyze, and the scholarly conversation about them. Treat them separately. For the secondary literature, I'd expect clusters around: feminist recovery work (1970s–80s), labor-history-inflected criticism, and more recent intersectional readings that bring race and immigration into a frame earlier scholars siloed. There is a real chronological story here — the 1970s recovery generation made arguments that the 2000s scholarship complicated — so a hybrid scheme works: top-level thematic (by what the criticism *argues*), with chronology surfaced inside each theme. Recommended scheme: **thematic, with chronology inside themes**.

**Proposed structure**
- *Recovery and visibility* — claim: the first generation of feminist criticism established that female labor was depicted; later scholarship asks how.
- *Labor as plot vs. labor as condition* — claim: critics divide on whether female work in these novels is event or atmosphere, and the choice carries political weight.
- *Race, immigration, and whose labor counts* — claim: more recent scholarship has shown that the early canon's "female worker" was implicitly white and native-born.
- *(Brief)* primary text grouping — claim: the novels themselves cluster by setting (factory, domestic, agricultural) in ways the secondary literature has used to organize its arguments.

**Draft: Race, immigration, and whose labor counts**
The recovery scholarship of the 1970s and 1980s [CITATION NEEDED — likely your Showalter, Baym, or comparable references] established a canon of texts depicting female labor but largely treated "female worker" as a stable category. Subsequent intersectional criticism [CITATION NEEDED — your post-2000 sources] argued that this category was implicitly white, native-born, and urban, eliding the agricultural labor of Black women in the South and the garment-trade labor of recent immigrants. The current consensus is not that the recovery generation was wrong but that its frame of "female labor" was narrower than its rhetoric suggested. For a thesis examining representations across multiple labor settings, the productive question is no longer whether female labor was depicted but whose labor the canonical depictions rendered legible — a question the corpus raises but, in my reading, does not fully resolve for the agricultural/domestic boundary your primary texts seem to span.

**Gap statement**
The secondary literature has thoroughly addressed factory and garment-trade representations and has begun to address agricultural labor in Black women's writing, but the *boundary* between domestic and agricultural labor — central to the rural fiction this thesis treats — remains under-examined. A reading that traces how individual texts negotiate that boundary is a defensible contribution.

**What I'd want from you next**
- The actual reference list, ideally split into primary vs. secondary, so I can replace the `[CITATION NEEDED]` placeholders and verify whether the 1970s/post-2000 split I'm assuming actually maps your corpus.
- Which primary texts you plan to foreground — that determines which themes deserve the most space.
- Style: MLA notes-and-bibliography or author-page parenthetical?
