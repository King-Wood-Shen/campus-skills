"""Parse a SKILL.md file into frontmatter + four named body sections.

The methodology requires every skill body to contain exactly these four
sections in this order, identified by H2 headings:

    ## Expert Knowledge
    ## Workflow
    ## Output Template
    ## Examples

This module exposes:

- ``load_skill(path)`` returning a ``Skill`` dataclass
- ``Skill.render_full()`` for the "with skill" condition
- ``Skill.render_ablated(component)`` for ablation conditions
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


COMPONENT_NAMES = ["Expert Knowledge", "Workflow", "Output Template", "Examples"]
COMPONENT_KEYS = ["expert_knowledge", "workflow", "output_template", "examples"]
NAME_TO_KEY = dict(zip(COMPONENT_NAMES, COMPONENT_KEYS))
KEY_TO_NAME = dict(zip(COMPONENT_KEYS, COMPONENT_NAMES))


@dataclass
class Skill:
    name: str
    description: str
    components: dict[str, str] = field(default_factory=dict)
    raw_path: Path | None = None

    def render_full(self) -> str:
        """Render the full skill body (all four components) as a single markdown string."""
        parts = []
        for key in COMPONENT_KEYS:
            section_name = KEY_TO_NAME[key]
            body = self.components.get(key, "").strip()
            if body:
                parts.append(f"## {section_name}\n\n{body}")
        return "\n\n".join(parts)

    def render_ablated(self, removed_key: str) -> str:
        """Render the skill body with one component removed."""
        if removed_key not in COMPONENT_KEYS:
            raise ValueError(f"Unknown component key: {removed_key}")
        parts = []
        for key in COMPONENT_KEYS:
            if key == removed_key:
                continue
            section_name = KEY_TO_NAME[key]
            body = self.components.get(key, "").strip()
            if body:
                parts.append(f"## {section_name}\n\n{body}")
        return "\n\n".join(parts)


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def load_skill(skill_md_path: Path) -> Skill:
    """Load and parse a SKILL.md file.

    Raises if frontmatter is missing or any of the four required sections
    are absent.
    """
    text = Path(skill_md_path).read_text(encoding="utf-8")

    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(
            f"{skill_md_path} is missing YAML frontmatter (--- name: ... ---)"
        )

    frontmatter = yaml.safe_load(match.group(1)) or {}
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not name or not description:
        raise ValueError(
            f"{skill_md_path} frontmatter must contain both 'name' and 'description'"
        )

    body = text[match.end():]

    sections = _split_h2_sections(body)
    missing = [n for n in COMPONENT_NAMES if n not in sections]
    if missing:
        raise ValueError(
            f"{skill_md_path} is missing required sections: {missing}. "
            f"Expected exactly: {COMPONENT_NAMES}"
        )

    components = {NAME_TO_KEY[n]: sections[n] for n in COMPONENT_NAMES}

    return Skill(
        name=name,
        description=description,
        components=components,
        raw_path=Path(skill_md_path),
    )


def _split_h2_sections(body: str) -> dict[str, str]:
    """Split a markdown body into a dict of {h2_heading: section_body}.

    Each section runs from its heading to the next H2 (or EOF).
    """
    headings = list(_H2_RE.finditer(body))
    sections: dict[str, str] = {}
    for i, m in enumerate(headings):
        title = m.group(1).strip()
        start = m.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(body)
        sections[title] = body[start:end].strip()
    return sections
