"""Wraps `claude -p` invocations with retries and JSON parsing.

The harness uses the user's Claude Code subscription via the local CLI
binary (``claude``) rather than the Anthropic Python SDK. This avoids
requiring a separate ANTHROPIC_API_KEY and exercises the same code path
end users will hit in real usage.

Both flavors of invocation:

- ``run_user_query(...)`` — get a response to a scenario, optionally with
  a skill body appended to the system prompt.
- ``run_judge_query(...)`` — get a structured rubric score, with a JSON
  schema enforced by the CLI.
"""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass


# Common flags applied to every invocation. We disable hooks, plugin sync,
# auto-memory, and slash commands so the eval is reproducible and not
# affected by whatever the user has installed in their Claude Code config.
BASE_FLAGS = [
    "-p",
    "--bare",
    "--disable-slash-commands",
    "--no-session-persistence",
    "--output-format", "json",
]


# JSON schema for the judge's response. The CLI enforces this schema so
# we don't need to defensively parse free-form prose.
JUDGE_SCHEMA = {
    "type": "object",
    "required": [
        "correctness", "completeness", "expert_alignment", "actionability",
        "justifications",
    ],
    "properties": {
        "correctness": {"type": "integer", "minimum": 1, "maximum": 5},
        "completeness": {"type": "integer", "minimum": 1, "maximum": 5},
        "expert_alignment": {"type": "integer", "minimum": 1, "maximum": 5},
        "actionability": {"type": "integer", "minimum": 1, "maximum": 5},
        "justifications": {
            "type": "object",
            "required": [
                "correctness", "completeness", "expert_alignment", "actionability",
            ],
            "properties": {
                "correctness": {"type": "string"},
                "completeness": {"type": "string"},
                "expert_alignment": {"type": "string"},
                "actionability": {"type": "string"},
            },
        },
    },
}


@dataclass
class ClaudeResult:
    """Outcome of a single ``claude -p`` invocation."""
    text: str
    raw_json: dict
    duration_s: float
    cost_usd: float | None
    tokens_in: int | None
    tokens_out: int | None


class ClaudeError(RuntimeError):
    pass


def run_user_query(
    user_prompt: str,
    *,
    system_append: str | None = None,
    model: str | None = None,
    timeout_s: int = 300,
    retries: int = 2,
    backoff_s: float = 5.0,
) -> ClaudeResult:
    """Run a user-side scenario through ``claude -p``.

    If ``system_append`` is provided, it is appended to Claude's default
    system prompt (this is how we inject SKILL.md content for "with skill"
    and ablated conditions).
    """
    cmd = list(BASE_FLAGS)
    if model:
        cmd += ["--model", model]
    if system_append:
        cmd += ["--append-system-prompt", system_append]
    cmd += [user_prompt]
    return _invoke(cmd, timeout_s=timeout_s, retries=retries, backoff_s=backoff_s)


def run_judge_query(
    judge_prompt: str,
    *,
    model: str | None = None,
    timeout_s: int = 180,
    retries: int = 2,
    backoff_s: float = 5.0,
) -> dict:
    """Run a rubric-scoring prompt and return the parsed JSON object.

    The CLI enforces ``JUDGE_SCHEMA`` so the returned object is guaranteed
    to have the four integer scores plus a justifications dict.
    """
    cmd = list(BASE_FLAGS)
    if model:
        cmd += ["--model", model]
    cmd += ["--json-schema", json.dumps(JUDGE_SCHEMA), judge_prompt]
    result = _invoke(cmd, timeout_s=timeout_s, retries=retries, backoff_s=backoff_s)
    try:
        return json.loads(result.text)
    except json.JSONDecodeError as e:
        raise ClaudeError(
            f"Judge returned non-JSON despite schema enforcement: {result.text!r}"
        ) from e


def _invoke(
    cmd: list[str],
    *,
    timeout_s: int,
    retries: int,
    backoff_s: float,
) -> ClaudeResult:
    """Run a claude CLI command with retries on transient failure."""
    full_cmd = ["claude", *cmd]
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        start = time.monotonic()
        try:
            proc = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                encoding="utf-8",
            )
        except subprocess.TimeoutExpired as e:
            last_err = e
            if attempt < retries:
                time.sleep(backoff_s * (2 ** attempt))
                continue
            raise ClaudeError(f"claude CLI timed out after {timeout_s}s") from e
        duration = time.monotonic() - start

        if proc.returncode != 0:
            last_err = ClaudeError(
                f"claude CLI exited {proc.returncode}: {proc.stderr.strip()[:500]}"
            )
            if attempt < retries:
                time.sleep(backoff_s * (2 ** attempt))
                continue
            raise last_err

        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as e:
            raise ClaudeError(
                f"claude CLI returned non-JSON output: {proc.stdout[:500]!r}"
            ) from e

        # The --output-format=json envelope contains a "result" field with
        # the model's textual answer, plus usage info.
        return ClaudeResult(
            text=payload.get("result", ""),
            raw_json=payload,
            duration_s=duration,
            cost_usd=payload.get("total_cost_usd"),
            tokens_in=_get_nested(payload, "usage", "input_tokens"),
            tokens_out=_get_nested(payload, "usage", "output_tokens"),
        )

    assert last_err is not None
    raise last_err


def _get_nested(d: dict, *keys):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur
