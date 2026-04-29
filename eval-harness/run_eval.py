"""End-to-end skill evaluation driver.

For a given skill directory, this script:

1. Loads the skill (SKILL.md + scenarios + adversarial set + rubric).
2. Runs each scenario through `claude -p`, with and without the skill body
   appended to the system prompt. Optionally runs ablated versions.
3. Calls a separate `claude -p` invocation as judge to score each output
   on the 4-dimension rubric (1-5).
4. Writes ``runs/<timestamp>/results.jsonl`` with raw per-scenario results.
5. Generates ``evals/baseline.md`` and (if --ablation) ``evals/ablation.md``.

Usage::

    python run_eval.py --skill ../plugins/common-essentials/skills/literature-review
    python run_eval.py --skill ../plugins/cs-ai-research/skills/experiment-rigor --ablation

Authentication: uses the user's Claude Code subscription via the local
``claude`` CLI binary. No ANTHROPIC_API_KEY needed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

# Allow `python eval-harness/run_eval.py ...` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ablation import ablation_conditions, pretty_condition
from claude_runner import ClaudeError, run_user_query
from judge import score_response
from report import write_ablation_report, write_baseline_report
from skill_loader import Skill, load_skill


@dataclass
class RunRecord:
    scenario_id: str
    condition: str  # "with_skill" | "without_skill" | "ablate_<key>"
    prompt: str
    difficulty: str | None
    ideal_traits: list[str]
    model_output: str
    duration_s: float
    cost_usd: float | None
    tokens_in: int | None
    tokens_out: int | None
    scores: dict | None
    error: str | None = None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--skill", required=True, type=Path,
        help="Path to a skill directory containing SKILL.md and tests/.",
    )
    parser.add_argument(
        "--ablation", action="store_true",
        help="Also run the four component-ablation conditions.",
    )
    parser.add_argument(
        "--include-adversarial", action="store_true",
        help="Include adversarial.jsonl scenarios in the run.",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limit to first N scenarios (useful for smoke tests).",
    )
    parser.add_argument(
        "--model", default=None,
        help="Override the model used for both responses and judge.",
    )
    parser.add_argument(
        "--judge-model", default=None,
        help="Override only the judge model (defaults to --model).",
    )
    parser.add_argument(
        "--sleep", type=float, default=1.0,
        help="Seconds to sleep between calls to be gentle with rate limits.",
    )
    args = parser.parse_args()

    skill_dir: Path = args.skill.resolve()
    skill_md = skill_dir / "SKILL.md"
    tests_dir = skill_dir / "tests"
    evals_dir = skill_dir / "evals"

    if not skill_md.exists():
        print(f"ERROR: {skill_md} not found", file=sys.stderr)
        return 2
    if not tests_dir.exists():
        print(f"ERROR: {tests_dir} not found", file=sys.stderr)
        return 2

    skill = load_skill(skill_md)
    rubric_text = (tests_dir / "rubric.md").read_text(encoding="utf-8")

    scenarios = list(_load_jsonl(tests_dir / "scenarios.jsonl"))
    if args.include_adversarial:
        adv_path = tests_dir / "adversarial.jsonl"
        if adv_path.exists():
            scenarios.extend(_load_jsonl(adv_path))
    if args.limit:
        scenarios = scenarios[: args.limit]

    if not scenarios:
        print("ERROR: no scenarios loaded", file=sys.stderr)
        return 2

    conditions: dict[str, str | None] = {
        "without_skill": None,
        "with_skill": skill.render_full(),
    }
    if args.ablation:
        for cond, body in ablation_conditions(skill).items():
            if cond != "with_skill":
                conditions[cond] = body

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    runs_root = Path(__file__).parent / "runs" / f"{skill.name}-{timestamp}"
    runs_root.mkdir(parents=True, exist_ok=True)
    results_path = runs_root / "results.jsonl"

    total = len(scenarios) * len(conditions)
    print(
        f"Running {len(scenarios)} scenarios × {len(conditions)} conditions = {total} model calls.\n"
        f"Conditions: {', '.join(conditions.keys())}\n"
        f"Raw results → {results_path}\n",
        flush=True,
    )

    records: list[RunRecord] = []
    judge_model = args.judge_model or args.model
    with open(results_path, "w", encoding="utf-8") as f:
        i = 0
        for scenario in scenarios:
            for condition_name, system_append in conditions.items():
                i += 1
                label = pretty_condition(condition_name)
                print(f"  [{i}/{total}] {scenario['id']} — {label} ... ", end="", flush=True)
                rec = _run_one(
                    scenario,
                    condition_name=condition_name,
                    system_append=system_append,
                    rubric_text=rubric_text,
                    response_model=args.model,
                    judge_model=judge_model,
                )
                f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
                f.flush()
                records.append(rec)
                if rec.error:
                    print(f"ERROR: {rec.error}")
                else:
                    overall = _overall_or_nan(rec.scores)
                    print(f"overall {overall:.2f}")
                if args.sleep:
                    time.sleep(args.sleep)

    # Reports
    print("\nWriting reports...")
    plain_records = [asdict(r) for r in records]

    write_baseline_report(
        plain_records,
        skill_name=skill.name,
        skill_description=skill.description,
        out_path=evals_dir / "baseline.md",
    )
    print(f"  → {evals_dir / 'baseline.md'}")

    if args.ablation:
        write_ablation_report(
            plain_records,
            skill_name=skill.name,
            skill_description=skill.description,
            out_path=evals_dir / "ablation.md",
        )
        print(f"  → {evals_dir / 'ablation.md'}")

    print("\nDone.")
    return 0


def _run_one(
    scenario: dict,
    *,
    condition_name: str,
    system_append: str | None,
    rubric_text: str,
    response_model: str | None,
    judge_model: str | None,
) -> RunRecord:
    """Run one (scenario, condition) pair: get response, then judge it."""
    try:
        result = run_user_query(
            scenario["prompt"],
            system_append=system_append,
            model=response_model,
        )
    except ClaudeError as e:
        return RunRecord(
            scenario_id=scenario["id"],
            condition=condition_name,
            prompt=scenario["prompt"],
            difficulty=scenario.get("difficulty"),
            ideal_traits=scenario.get("ideal_traits", []),
            model_output="",
            duration_s=0.0,
            cost_usd=None,
            tokens_in=None,
            tokens_out=None,
            scores=None,
            error=f"response: {e}",
        )

    try:
        scores = score_response(scenario, result.text, rubric_text, model=judge_model)
    except ClaudeError as e:
        return RunRecord(
            scenario_id=scenario["id"],
            condition=condition_name,
            prompt=scenario["prompt"],
            difficulty=scenario.get("difficulty"),
            ideal_traits=scenario.get("ideal_traits", []),
            model_output=result.text,
            duration_s=result.duration_s,
            cost_usd=result.cost_usd,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            scores=None,
            error=f"judge: {e}",
        )

    return RunRecord(
        scenario_id=scenario["id"],
        condition=condition_name,
        prompt=scenario["prompt"],
        difficulty=scenario.get("difficulty"),
        ideal_traits=scenario.get("ideal_traits", []),
        model_output=result.text,
        duration_s=result.duration_s,
        cost_usd=result.cost_usd,
        tokens_in=result.tokens_in,
        tokens_out=result.tokens_out,
        scores=scores,
    )


def _load_jsonl(path: Path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def _overall_or_nan(scores: dict | None) -> float:
    if not scores:
        return float("nan")
    keys = ["correctness", "completeness", "expert_alignment", "actionability"]
    return sum(scores[k] for k in keys) / len(keys)


if __name__ == "__main__":
    sys.exit(main())
