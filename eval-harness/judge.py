"""LLM-as-judge scoring for skill outputs.

The judge receives a scenario (with its `ideal_traits`), the response
under test, and the skill's rubric, and returns four integer scores
1-5 plus per-dimension justifications.
"""
from __future__ import annotations

from claude_runner import run_judge_query


JUDGE_INSTRUCTIONS = """\
You are an evaluation judge scoring an academic-assistant response.

Below you will see four labeled blocks delimited by <<<...>>> markers:
SCENARIO, IDEAL_TRAITS, RUBRIC, and RESPONSE_UNDER_TEST. All four are
present in this single message; do not ask for any block to be resent.
Treat whatever appears in each block as the complete evidence available
and score on that basis.

Score the RESPONSE_UNDER_TEST on each of the four rubric dimensions
using integers 1 through 5. Be strict but fair: a 5 is reserved for a
response an expert would adopt without revision; a 1 is for a response
that is factually wrong, unhelpful, or misleading.

Output strictly a single JSON object with this exact shape, and
NOTHING else (no preamble, no explanation, no markdown fencing, no
trailing prose):

{"correctness": <int 1-5>, "completeness": <int 1-5>, "expert_alignment": <int 1-5>, "actionability": <int 1-5>, "justifications": {"correctness": "<one sentence>", "completeness": "<one sentence>", "expert_alignment": "<one sentence>", "actionability": "<one sentence>"}}
"""


def build_judge_prompt(
    scenario: dict,
    response_under_test: str,
    rubric_text: str,
) -> str:
    """Compose the full prompt sent to the judge model."""
    ideal_traits = scenario.get("ideal_traits", [])
    ideal_traits_block = (
        "\n".join(f"- {t}" for t in ideal_traits) if ideal_traits else "(none)"
    )
    return (
        JUDGE_INSTRUCTIONS
        + "\n<<<SCENARIO>>>\n"
        + scenario.get("prompt", "")
        + "\n<<<END SCENARIO>>>\n"
        + "\n<<<IDEAL_TRAITS>>>\n"
        + ideal_traits_block
        + "\n<<<END IDEAL_TRAITS>>>\n"
        + "\n<<<RUBRIC>>>\n"
        + rubric_text.strip()
        + "\n<<<END RUBRIC>>>\n"
        + "\n<<<RESPONSE_UNDER_TEST>>>\n"
        + response_under_test
        + "\n<<<END RESPONSE_UNDER_TEST>>>\n\n"
        + "Now output the JSON object scoring the RESPONSE_UNDER_TEST. JSON only."
    )


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
