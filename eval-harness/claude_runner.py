"""Wraps `claude -p` invocations with retries and JSON parsing.

The harness uses the user's Claude Code subscription via the local CLI
binary (``claude``) rather than the Anthropic Python SDK. This avoids
requiring a separate ``ANTHROPIC_API_KEY`` and exercises the same code
path end users will hit in real usage.

Two flavors of invocation are exposed:

- ``run_user_query(...)`` — get a model response to a scenario, optionally
  with a skill body appended to the system prompt.
- ``run_judge_query(...)`` — get a structured rubric score, with prompt-level
  JSON instructions and a tolerant parser.

Several Windows- and CLI-specific gotchas are handled here:

1. ``shutil.which`` resolves ``claude.cmd`` so subprocess.run doesn't fail
   with WinError 2 when only a ``.cmd`` shim is on PATH.
2. ``CLAUDE_CODE_GIT_BASH_PATH`` is auto-set on Windows when the parent
   shell hasn't exported it (Claude Code on Windows requires git-bash).
3. The prompt is piped via stdin rather than passed as a positional
   argument. Otherwise the variadic ``--disallowedTools`` parser greedily
   consumes the prompt as a tool name.
4. Tool use is disallowed so the model cannot ``Read``/``Bash``/``Glob``
   the working directory and turn evaluation responses into file-fishing
   meta-commentary.
5. The subprocess runs in a fresh temp directory so any nearby ``CLAUDE.md``
   or project context cannot leak into the eval.
6. ``--bare`` is NOT used: it disables subscription OAuth and demands
   ``ANTHROPIC_API_KEY``, which would defeat the point of running on a
   Claude Code subscription.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from functools import lru_cache


_CODE_FENCE_RE = re.compile(r"```(?:json)?\s*\n(.*?)\n```", re.DOTALL)
_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


# Tools we block. The model should answer with text only — no file access,
# shell, web, or task spawning. Listed comma-separated because that's how
# the CLI's variadic flag accepts them in a single argv slot.
DISALLOWED_TOOLS = ",".join([
    "Bash", "Read", "Write", "Edit", "Glob", "Grep", "Task",
    "WebFetch", "WebSearch", "NotebookEdit", "TodoWrite",
])


BASE_FLAGS = [
    "-p",
    "--no-session-persistence",
    "--output-format", "json",
    "--disallowedTools", DISALLOWED_TOOLS,
]


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
    system prompt (this is how SKILL.md content is injected for the
    "with skill" and ablated conditions). To avoid Windows argv length
    limits (~32K UTF-16 chars), we write the body to a temp file and
    use ``--append-system-prompt-file``.
    """
    cmd = list(BASE_FLAGS)
    if model:
        cmd += ["--model", model]

    sys_prompt_file: str | None = None
    if system_append:
        sys_prompt_file = _write_temp(system_append, suffix=".sysprompt.md")
        cmd += ["--append-system-prompt-file", sys_prompt_file]

    try:
        return _invoke(
            cmd, prompt=user_prompt,
            timeout_s=timeout_s, retries=retries, backoff_s=backoff_s,
        )
    finally:
        if sys_prompt_file:
            try:
                os.unlink(sys_prompt_file)
            except OSError:
                pass


def run_judge_query(
    judge_prompt: str,
    *,
    model: str | None = None,
    timeout_s: int = 180,
    retries: int = 2,
    backoff_s: float = 5.0,
) -> dict:
    """Run a rubric-scoring prompt and return the parsed JSON object.

    The prompt itself instructs the model to emit JSON; the parser
    tolerates markdown fencing or extra prose around the JSON body in
    case the model adds it despite instructions.

    We deliberately do NOT pass ``--json-schema``: in practice that flag
    pushes Claude into a meta/explanatory mode where it describes what
    it would output rather than emitting the JSON. Plain prompt-level
    instructions plus a tolerant parser work better.
    """
    cmd = list(BASE_FLAGS)
    if model:
        cmd += ["--model", model]
    result = _invoke(cmd, prompt=judge_prompt, timeout_s=timeout_s, retries=retries, backoff_s=backoff_s)
    return _extract_judge_json(result.text)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _resolve_claude_binary() -> str:
    """Locate the Claude Code CLI binary, with Windows-aware fallbacks."""
    for candidate in ("claude", "claude.cmd", "claude.exe", "claude.bat"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise ClaudeError(
        "Could not find the 'claude' CLI on PATH. "
        "Install Claude Code (https://claude.com/claude-code) and ensure "
        "'claude --version' works in your shell before running the harness."
    )


@lru_cache(maxsize=1)
def _build_subprocess_env() -> dict[str, str]:
    """Return an environment dict for subprocess invocations."""
    env = dict(os.environ)
    if sys.platform.startswith("win") and not env.get("CLAUDE_CODE_GIT_BASH_PATH"):
        bash_path = shutil.which("bash")
        if bash_path:
            env["CLAUDE_CODE_GIT_BASH_PATH"] = bash_path
    return env


@lru_cache(maxsize=1)
def _clean_cwd() -> str:
    """A scratch directory with no CLAUDE.md, settings, or project context.

    Created once per process and reused. Inside this directory Claude
    sees nothing relevant about the campus-skills repo, so prompts are
    interpreted on their own terms.
    """
    return tempfile.mkdtemp(prefix="campus-skills-eval-")


def _write_temp(content: str, suffix: str = ".txt") -> str:
    """Write `content` to a temp file (UTF-8) and return its absolute path."""
    fd, path = tempfile.mkstemp(suffix=suffix, prefix="campus-skills-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception:
        os.unlink(path)
        raise
    return path


def _invoke(
    cmd: list[str],
    *,
    prompt: str,
    timeout_s: int,
    retries: int,
    backoff_s: float,
) -> ClaudeResult:
    """Run a claude CLI command with retries on transient failure.

    The prompt is piped via stdin rather than passed as a positional
    argument so that variadic flags like ``--disallowedTools`` cannot
    accidentally consume it.
    """
    full_cmd = [_resolve_claude_binary(), *cmd]
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        start = time.monotonic()
        try:
            # Use bytes mode and decode at the end. Python's text-mode
            # reader thread on Windows can split a multi-byte UTF-8
            # character across reads, raising UnicodeDecodeError; doing
            # the decode once on the full buffer avoids that.
            proc = subprocess.run(
                full_cmd,
                input=prompt.encode("utf-8"),
                capture_output=True,
                timeout=timeout_s,
                env=_build_subprocess_env(),
                cwd=_clean_cwd(),
            )
        except subprocess.TimeoutExpired as e:
            last_err = e
            if attempt < retries:
                time.sleep(backoff_s * (2 ** attempt))
                continue
            raise ClaudeError(f"claude CLI timed out after {timeout_s}s") from e
        duration = time.monotonic() - start

        stdout = (proc.stdout or b"").decode("utf-8", errors="replace")
        stderr = (proc.stderr or b"").decode("utf-8", errors="replace")

        if proc.returncode != 0:
            err_blob = stderr.strip()[:500] or stdout.strip()[:500] or "(no output)"
            last_err = ClaudeError(
                f"claude CLI exited {proc.returncode}: {err_blob}"
            )
            if attempt < retries:
                time.sleep(backoff_s * (2 ** attempt))
                continue
            raise last_err

        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as e:
            raise ClaudeError(
                f"claude CLI returned non-JSON output: {stdout[:500]!r}"
            ) from e

        # When `is_error` is true on the envelope it usually means an
        # auth/quota issue surfaced as a successful exit code.
        if payload.get("is_error"):
            err_text = payload.get("result", "<unknown>")
            raise ClaudeError(f"Claude CLI reported error: {err_text[:300]}")

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


def _extract_judge_json(text: str) -> dict:
    """Extract a JSON object from the judge's text response.

    Handles three cases: (1) raw JSON, (2) JSON wrapped in markdown code
    fences, (3) JSON embedded in surrounding prose (fallback to first
    balanced ``{...}``).
    """
    candidates: list[str] = [text.strip()]

    fence_match = _CODE_FENCE_RE.search(text)
    if fence_match:
        candidates.append(fence_match.group(1).strip())

    obj_match = _JSON_OBJECT_RE.search(text)
    if obj_match:
        candidates.append(obj_match.group(0))

    last_err: Exception | None = None
    for candidate in candidates:
        try:
            obj = json.loads(candidate)
            _validate_judge_payload(obj)
            return obj
        except (json.JSONDecodeError, ValueError) as e:
            last_err = e
            continue

    raise ClaudeError(
        f"Could not extract a valid judge JSON payload. "
        f"Raw response: {text[:600]!r}. Last parse error: {last_err}"
    )


def _validate_judge_payload(obj) -> None:
    """Ensure a parsed object has the four integer scores in 1-5 range."""
    if not isinstance(obj, dict):
        raise ValueError(f"Expected object, got {type(obj).__name__}")
    for k in ("correctness", "completeness", "expert_alignment", "actionability"):
        if k not in obj:
            raise ValueError(f"Missing key {k!r}")
        v = obj[k]
        if not isinstance(v, int) or not 1 <= v <= 5:
            raise ValueError(f"{k} = {v!r} is not int in 1-5")


def _get_nested(d: dict, *keys):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur
