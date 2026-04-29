"""Component ablation: render skill bodies with one of the four sections removed.

Layered on top of skill_loader.Skill, this module enumerates the
ablation conditions that the harness will run when ``--ablation`` is
passed.
"""
from __future__ import annotations

from skill_loader import COMPONENT_KEYS, KEY_TO_NAME, Skill


def ablation_conditions(skill: Skill) -> dict[str, str]:
    """Return a dict of {condition_label: rendered_skill_body}.

    Includes:
      - ``with_skill``: full body
      - ``ablate_<component>`` for each of the four components

    The ``without_skill`` condition is handled by run_eval directly (no
    skill body at all), not here.
    """
    conditions: dict[str, str] = {"with_skill": skill.render_full()}
    for key in COMPONENT_KEYS:
        conditions[f"ablate_{key}"] = skill.render_ablated(key)
    return conditions


def pretty_condition(label: str) -> str:
    """Human-readable label for a condition (used in reports)."""
    if label == "without_skill":
        return "Without skill (baseline)"
    if label == "with_skill":
        return "With full skill"
    if label.startswith("ablate_"):
        key = label[len("ablate_"):]
        return f"Ablated: {KEY_TO_NAME.get(key, key)} removed"
    return label
