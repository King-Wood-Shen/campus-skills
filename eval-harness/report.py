"""Generate domain-expert-readable markdown reports from raw eval results.

A run produces ``runs/<timestamp>/results.jsonl`` with one record per
(scenario, condition) pair. This module reads that file and writes:

- ``evals/baseline.md`` — comparison of with-skill vs. without-skill
- ``evals/ablation.md`` — contribution of each of the four components

Reports are written for a domain expert (not a software engineer), so
they include side-by-side raw outputs for typical scenarios.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from statistics import mean

from ablation import pretty_condition
from skill_loader import COMPONENT_KEYS, KEY_TO_NAME


RUBRIC_DIMENSIONS = ["correctness", "completeness", "expert_alignment", "actionability"]


def load_results(results_jsonl: Path) -> list[dict]:
    records = []
    with open(results_jsonl, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_baseline_report(
    results: list[dict],
    *,
    skill_name: str,
    skill_description: str,
    out_path: Path,
    n_typical: int = 3,
) -> None:
    """Write the with-skill vs. without-skill comparison report."""
    with_records = [r for r in results if r["condition"] == "with_skill"]
    without_records = [r for r in results if r["condition"] == "without_skill"]

    if not with_records or not without_records:
        raise ValueError(
            "Baseline report requires both 'with_skill' and 'without_skill' "
            "results. Did you run with --no-baseline?"
        )

    summary = _executive_summary(with_records, without_records, skill_name)
    score_table = _format_score_table(
        [
            ("Without skill (baseline)", without_records),
            ("With full skill", with_records),
        ]
    )
    typical = _select_typical_scenarios(with_records, without_records, n=n_typical)
    typical_block = _format_side_by_side(typical, with_records, without_records)
    limitations = _format_limitations(with_records, without_records)
    metadata = _format_metadata(skill_name, skill_description, results)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        f"# Baseline Evaluation: `{skill_name}`\n\n"
        f"{metadata}\n\n"
        "## Executive Summary\n\n"
        f"{summary}\n\n"
        "## Aggregate Scores\n\n"
        f"{score_table}\n\n"
        "## Typical Scenarios — Side-by-Side\n\n"
        "Read these and form your own judgment, independent of the LLM judge's score.\n\n"
        f"{typical_block}\n\n"
        "## Limitations & Failure Modes\n\n"
        f"{limitations}\n",
        encoding="utf-8",
    )


def write_ablation_report(
    results: list[dict],
    *,
    skill_name: str,
    skill_description: str,
    out_path: Path,
) -> None:
    """Write the component-ablation contribution report."""
    with_records = [r for r in results if r["condition"] == "with_skill"]
    if not with_records:
        raise ValueError(
            "Ablation report requires 'with_skill' (full) results as the reference."
        )

    rows = [("With full skill", with_records)]
    for key in COMPONENT_KEYS:
        condition = f"ablate_{key}"
        records = [r for r in results if r["condition"] == condition]
        if records:
            rows.append((pretty_condition(condition), records))

    if len(rows) == 1:
        raise ValueError(
            "Ablation report requires at least one 'ablate_*' condition. "
            "Did you forget --ablation?"
        )

    summary = _ablation_summary(rows, skill_name)
    score_table = _format_score_table(rows)
    drop_table = _format_ablation_drop_table(with_records, rows)
    metadata = _format_metadata(skill_name, skill_description, results)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        f"# Ablation Study: `{skill_name}`\n\n"
        f"{metadata}\n\n"
        "## Executive Summary\n\n"
        f"{summary}\n\n"
        "## Aggregate Scores\n\n"
        f"{score_table}\n\n"
        "## Score Drop per Removed Component\n\n"
        "Larger drops mean the component contributed more to overall quality. "
        "Components that produce no drop when removed are candidates for "
        "trimming or rewriting.\n\n"
        f"{drop_table}\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _format_metadata(skill_name: str, description: str, results: list[dict]) -> str:
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    n_scenarios = len({r["scenario_id"] for r in results})
    conditions = sorted({r["condition"] for r in results})
    return (
        f"- **Skill:** `{skill_name}`\n"
        f"- **Description:** {description}\n"
        f"- **Generated:** {timestamp}\n"
        f"- **Scenarios:** {n_scenarios}\n"
        f"- **Conditions evaluated:** {', '.join(conditions)}"
    )


def _executive_summary(
    with_records: list[dict],
    without_records: list[dict],
    skill_name: str,
) -> str:
    with_overall = _overall_mean(with_records)
    without_overall = _overall_mean(without_records)
    delta = with_overall - without_overall
    direction = "improved" if delta > 0 else "degraded" if delta < 0 else "did not change"

    lines = [
        f"With the `{skill_name}` skill enabled, the model's mean rubric score "
        f"{direction} by {delta:+.2f} points (1-5 scale) compared to the same "
        f"prompts run without any skill context.",
        f"Average overall: **{with_overall:.2f}** with skill vs. "
        f"**{without_overall:.2f}** without.",
    ]

    per_dim_deltas = []
    for dim in RUBRIC_DIMENSIONS:
        d = _dim_mean(with_records, dim) - _dim_mean(without_records, dim)
        per_dim_deltas.append((dim, d))
    biggest = max(per_dim_deltas, key=lambda t: t[1])
    smallest = min(per_dim_deltas, key=lambda t: t[1])
    lines.append(
        f"Largest improvement: **{biggest[0]}** ({biggest[1]:+.2f}). "
        f"Smallest improvement: **{smallest[0]}** ({smallest[1]:+.2f})."
    )
    if delta < 0.5:
        lines.append(
            "**Caution:** the headline lift is below the +0.5 threshold the "
            "methodology asks for before a skill is considered ready to ship. "
            "Review the typical scenarios below before drawing conclusions."
        )
    return " ".join(lines)


def _ablation_summary(rows: list[tuple[str, list[dict]]], skill_name: str) -> str:
    full_label, full_records = rows[0]
    full_overall = _overall_mean(full_records)
    drops = []
    for label, records in rows[1:]:
        d = full_overall - _overall_mean(records)
        drops.append((label, d))
    if not drops:
        return "No ablation conditions were run."
    drops.sort(key=lambda t: t[1], reverse=True)
    biggest = drops[0]
    smallest = drops[-1]
    return (
        f"Removing the most load-bearing component drops the overall score by "
        f"**{biggest[1]:+.2f}** ({biggest[0]}). The least impactful removal "
        f"changes the score by only **{smallest[1]:+.2f}** ({smallest[0]}). "
        f"If a component's removal causes near-zero drop, consider whether "
        f"its content is doing real work or just adding length."
    )


def _format_score_table(rows: list[tuple[str, list[dict]]]) -> str:
    headers = ["Condition", *[d.replace("_", " ").title() for d in RUBRIC_DIMENSIONS], "Overall", "Mean tokens out"]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for label, records in rows:
        row = [label]
        for dim in RUBRIC_DIMENSIONS:
            row.append(f"{_dim_mean(records, dim):.2f}")
        row.append(f"**{_overall_mean(records):.2f}**")
        row.append(f"{_mean_tokens(records):.0f}")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _format_ablation_drop_table(
    full_records: list[dict],
    rows: list[tuple[str, list[dict]]],
) -> str:
    full_overall = _overall_mean(full_records)
    headers = ["Removed component", "Overall score", "Drop vs. full"]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for label, records in rows[1:]:
        overall = _overall_mean(records)
        drop = full_overall - overall
        lines.append(f"| {label} | {overall:.2f} | {drop:+.2f} |")
    return "\n".join(lines)


def _select_typical_scenarios(
    with_records: list[dict],
    without_records: list[dict],
    n: int,
) -> list[str]:
    """Choose `n` scenario IDs that best illustrate the skill's effect.

    We prefer scenarios where with-skill clearly beats without-skill (so
    the expert sees the skill in action), spread across difficulty levels.
    """
    by_id_with = {r["scenario_id"]: r for r in with_records}
    by_id_without = {r["scenario_id"]: r for r in without_records}
    common = set(by_id_with) & set(by_id_without)

    scored = []
    for sid in common:
        w = _overall_score(by_id_with[sid])
        wo = _overall_score(by_id_without[sid])
        scored.append((sid, w - wo, by_id_with[sid].get("difficulty", "med")))
    scored.sort(key=lambda t: t[1], reverse=True)

    chosen: list[str] = []
    seen_difficulties = set()
    # First pass: pick top-delta scenario per difficulty
    for sid, _delta, diff in scored:
        if diff not in seen_difficulties:
            chosen.append(sid)
            seen_difficulties.add(diff)
        if len(chosen) >= n:
            break
    # Fill from top-delta if still under n
    for sid, _delta, _diff in scored:
        if sid not in chosen:
            chosen.append(sid)
        if len(chosen) >= n:
            break
    return chosen[:n]


def _format_side_by_side(
    scenario_ids: list[str],
    with_records: list[dict],
    without_records: list[dict],
) -> str:
    by_id_with = {r["scenario_id"]: r for r in with_records}
    by_id_without = {r["scenario_id"]: r for r in without_records}
    blocks = []
    for sid in scenario_ids:
        w = by_id_with.get(sid)
        wo = by_id_without.get(sid)
        if not w or not wo:
            continue
        blocks.append(
            f"### Scenario `{sid}` — difficulty: {w.get('difficulty', '?')}\n\n"
            f"**Prompt:**\n\n> {_quote(w.get('prompt', ''))}\n\n"
            f"**Without skill** (overall {_overall_score(wo):.2f}):\n\n"
            f"> {_quote(wo.get('model_output', ''))}\n\n"
            f"**With skill** (overall {_overall_score(w):.2f}):\n\n"
            f"> {_quote(w.get('model_output', ''))}\n"
        )
    return "\n---\n\n".join(blocks) if blocks else "_(No scenarios available for side-by-side comparison.)_"


def _format_limitations(
    with_records: list[dict],
    without_records: list[dict],
) -> str:
    """Surface scenarios where the skill underperformed or scored low."""
    by_id_with = {r["scenario_id"]: r for r in with_records}
    by_id_without = {r["scenario_id"]: r for r in without_records}

    regressions = []
    low_scores = []
    for sid, w in by_id_with.items():
        w_overall = _overall_score(w)
        wo = by_id_without.get(sid)
        if wo and _overall_score(wo) - w_overall > 0.25:
            regressions.append((sid, w_overall, _overall_score(wo)))
        if w_overall < 3.0:
            low_scores.append((sid, w_overall))

    parts = []
    if regressions:
        parts.append("**Regressions** (skill scored worse than baseline):")
        for sid, ws, wos in regressions:
            parts.append(f"- `{sid}`: with-skill {ws:.2f} vs. without-skill {wos:.2f}")
    if low_scores:
        parts.append("\n**Low-scoring scenarios with skill** (overall < 3.0):")
        for sid, sc in low_scores:
            parts.append(f"- `{sid}`: {sc:.2f}")
    if not parts:
        parts.append("No regressions or low-scoring scenarios were detected.")
    return "\n".join(parts)


def _overall_score(record: dict) -> float:
    s = record.get("scores", {})
    return mean(s[d] for d in RUBRIC_DIMENSIONS) if s else float("nan")


def _overall_mean(records: list[dict]) -> float:
    vals = [_overall_score(r) for r in records if r.get("scores")]
    return mean(vals) if vals else float("nan")


def _dim_mean(records: list[dict], dim: str) -> float:
    vals = [r["scores"][dim] for r in records if r.get("scores")]
    return mean(vals) if vals else float("nan")


def _mean_tokens(records: list[dict]) -> float:
    vals = [r.get("tokens_out") for r in records if r.get("tokens_out") is not None]
    return mean(vals) if vals else float("nan")


def _quote(text: str, max_chars: int = 1500) -> str:
    """Format text as a markdown blockquote, truncating if very long."""
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n... [truncated]"
    return text.replace("\n", "\n> ")
