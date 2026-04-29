"""LLM-as-judge scoring for skill outputs.

The judge receives a scenario (with its `ideal_traits`), the response
under test, and the skill's rubric, and returns four integer scores
1-5 plus per-dimension justifications. Schema is enforced by the CLI
(see claude_runner.JUDGE_SCHEMA).
"""
from __future__ import annotations

import json
from textwrap import dedent

from claude_runner import run_judge_query


JUDGE_SYSTEM_INSTRUCTIONS = dedent("""\
    You are an evaluation judge for an academic skill being tested in
    isolation. You have NOT seen the skill itself; you only see the user's
    scenario, the model's response, the ideal traits a strong response
    should exhibit, and a four-dimension rubric.

    Score the response 1-5 on each rubric dimension. Be strict but fair.
    A 5 is reserved for responses an expert would adopt without revision.
    A 1 is for responses that are factually wrong, unhelpful, or misleading.

    Provide a one-sentence justification for each dimension. Do not
    include any other prose, headings, or markdown — only the JSON object
    matching the required schema.
""")


def build_judge_prompt(
    scenario: dict,
    response_under_test: str,
    rubric_text: str,
) -> str:
    """Compose the full prompt sent to the judge model."""
    ideal_traits = scenario.get("ideal_traits", [])
    ideal_traits_block = "\n".join(f"- {t}" for t in ideal_traits) if ideal_traits else "(none)"
    return dedent(f"""\
        {JUDGE_SYSTEM_INSTRUCTIONS}

        ============================
        SCENARIO (user-facing prompt):
        ============================
        {scenario.get("prompt", "")}

        ============================
        IDEAL TRAITS a strong response should exhibit:
        ============================
        {ideal_traits_block}

        ============================
        RUBRIC:
        ============================
        {rubric_text}

        ============================
        RESPONSE UNDER TEST:
        ============================
        {response_under_test}

        ============================
        TASK:
        ============================
        Score the response under test against the rubric. Return ONLY a
        JSON object with the four integer scores (1-5) and a one-sentence
        justification for each. Do not echo the scenario or the response.
    """)


def score_response(
    scenario: dict,
    response_under_test: str,
    rubric_text: str,
    *,
    model: str | None = None,
) -> dict:
    """Run the judge and return its parsed score dict.

    Returns: ``{"correctness": int, "completeness": int,
    "expert_alignment": int, "actionability": int,
    "justifications": {...}}``.
    """
    prompt = build_judge_prompt(scenario, response_under_test, rubric_text)
    return run_judge_query(prompt, model=model)


def mean_scores(score_records: list[dict]) -> dict:
    """Compute mean of each rubric dimension across a list of judge outputs."""
    if not score_records:
        return {k: float("nan") for k in (
            "correctness", "completeness", "expert_alignment", "actionability"
        )}
    keys = ["correctness", "completeness", "expert_alignment", "actionability"]
    return {
        k: sum(r["scores"][k] for r in score_records if "scores" in r) / len(score_records)
        for k in keys
    }


def overall_mean(scores: dict) -> float:
    """Average across all four rubric dimensions for a single response."""
    keys = ["correctness", "completeness", "expert_alignment", "actionability"]
    return sum(scores[k] for k in keys) / len(keys)
