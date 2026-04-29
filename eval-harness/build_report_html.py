"""Generate a single self-contained HTML page that browses every eval result.

Reads the latest ``runs/<skill>-<ts>/results.jsonl`` for each skill in
``plugins/*/skills/*``, embeds the full record set as inline JSON, and
emits ``docs/results.html`` — a static page with no external
dependencies. Open it in any browser.

Usage::

    python eval-harness/build_report_html.py            # auto-discover latest runs
    python eval-harness/build_report_html.py --output custom/path.html
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import html
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

# Allow running from repo root or eval-harness/.
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))


RUBRIC = ["correctness", "completeness", "expert_alignment", "actionability"]
CONDITIONS_ORDER = [
    "without_skill", "with_skill",
    "ablate_expert_knowledge", "ablate_workflow",
    "ablate_output_template", "ablate_examples",
]
CONDITION_LABELS = {
    "without_skill": "Without skill",
    "with_skill": "With full skill",
    "ablate_expert_knowledge": "− Expert Knowledge",
    "ablate_workflow": "− Workflow",
    "ablate_output_template": "− Output Template",
    "ablate_examples": "− Examples",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--output", type=Path,
        default=REPO_ROOT / "docs" / "results.html",
        help="Where to write the HTML file.",
    )
    parser.add_argument(
        "--runs-dir", type=Path,
        default=HERE / "runs",
        help="Directory containing per-skill run subdirectories.",
    )
    args = parser.parse_args()

    skills_data = _collect_latest_runs(args.runs_dir)
    if not skills_data:
        print(f"No runs found under {args.runs_dir}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(_render_html(skills_data), encoding="utf-8")

    total_records = sum(len(s["records"]) for s in skills_data.values())
    print(f"Wrote {args.output} ({len(skills_data)} skills, {total_records} records).")
    return 0


def _collect_latest_runs(runs_dir: Path) -> dict[str, dict]:
    """Return {skill_name: {records, scenarios, run_dir, generated}} for each skill."""
    by_skill: dict[str, list[Path]] = defaultdict(list)
    for path in glob.glob(str(runs_dir / "*")):
        p = Path(path)
        if not p.is_dir():
            continue
        # directory name is "<skill>-<timestamp>"
        name = p.name
        if "-" not in name:
            continue
        # Skill names can contain hyphens. Split off only the trailing
        # timestamp (the last token after the final hyphen).
        head, _, _ts = name.rpartition("-")
        if not head:
            continue
        by_skill[head].append(p)

    out: dict[str, dict] = {}
    for skill, dirs in by_skill.items():
        latest = max(dirs, key=lambda d: d.name)
        results_path = latest / "results.jsonl"
        if not results_path.exists():
            continue
        records = []
        with open(results_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))

        scenarios = _group_scenarios(records)
        skill_md = _find_skill_md(skill)
        description = _read_description(skill_md) if skill_md else ""

        out[skill] = {
            "records": records,
            "scenarios": scenarios,
            "run_dir": str(latest.relative_to(REPO_ROOT)),
            "generated": _file_mtime_iso(results_path),
            "description": description,
            "skill_md_path": str(skill_md.relative_to(REPO_ROOT)) if skill_md else None,
        }
    return out


def _group_scenarios(records: list[dict]) -> list[dict]:
    """Collapse 6 condition records per scenario into one row."""
    by_id: dict[str, dict] = {}
    for r in records:
        sid = r["scenario_id"]
        scn = by_id.setdefault(sid, {
            "id": sid,
            "prompt": r.get("prompt", ""),
            "difficulty": r.get("difficulty"),
            "ideal_traits": r.get("ideal_traits", []),
            "conditions": {},
        })
        scn["conditions"][r["condition"]] = {
            "model_output": r.get("model_output", "") or "",
            "scores": r.get("scores"),
            "tokens_in": r.get("tokens_in"),
            "tokens_out": r.get("tokens_out"),
            "duration_s": r.get("duration_s"),
            "cost_usd": r.get("cost_usd"),
            "error": r.get("error"),
        }
    return [by_id[k] for k in sorted(by_id.keys())]


def _find_skill_md(skill_name: str) -> Path | None:
    matches = list(REPO_ROOT.glob(f"plugins/*/skills/{skill_name}/SKILL.md"))
    return matches[0] if matches else None


def _read_description(skill_md: Path) -> str:
    """Return the description from the skill's YAML frontmatter, if present."""
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError:
        return ""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    if end < 0:
        return ""
    block = text[3:end]
    for raw in block.splitlines():
        if raw.strip().startswith("description:"):
            return raw.split(":", 1)[1].strip().strip('"').strip("'")
    return ""


def _file_mtime_iso(path: Path) -> str:
    ts = path.stat().st_mtime
    return dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc).isoformat(timespec="seconds")


def _render_html(skills_data: dict[str, dict]) -> str:
    """Build the final HTML string. All data embedded as inline JSON."""
    payload = {
        "skills": skills_data,
        "rubric": RUBRIC,
        "conditions_order": CONDITIONS_ORDER,
        "condition_labels": CONDITION_LABELS,
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    json_blob = json.dumps(payload, ensure_ascii=False)
    # Guard against `</script>` in user content — escape it once.
    json_blob = json_blob.replace("</", "<\\/")

    return (
        _HTML_HEAD
        + f'<script id="eval-data" type="application/json">{json_blob}</script>\n'
        + _HTML_BODY
        + _HTML_SCRIPT
        + _HTML_TAIL
    )


_HTML_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>campus-skills — eval results</title>
<style>
:root {
  --bg: #0e1116;
  --panel: #161b22;
  --panel-2: #1f2630;
  --border: #2a313c;
  --fg: #e6e8eb;
  --muted: #8b95a3;
  --accent: #6ea8ff;
  --good: #4ec9b0;
  --bad: #f48771;
  --warn: #ffb454;
  --code-bg: #0a0d12;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--bg); color: var(--fg);
  font: 14px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
}
header {
  padding: 22px 32px 16px; border-bottom: 1px solid var(--border);
  background: linear-gradient(180deg, #14181f, transparent);
}
header h1 { margin: 0 0 4px; font-size: 20px; letter-spacing: 0.2px; }
header .meta { color: var(--muted); font-size: 12px; }
header a { color: var(--accent); text-decoration: none; }
header a:hover { text-decoration: underline; }

main { padding: 18px 32px 64px; max-width: 1500px; margin: 0 auto; }

.tabs { display: flex; gap: 4px; margin: 8px 0 18px; border-bottom: 1px solid var(--border); }
.tab {
  padding: 10px 18px; cursor: pointer; border-radius: 6px 6px 0 0;
  color: var(--muted); border: 1px solid transparent; border-bottom: none;
  font-weight: 500;
}
.tab:hover { color: var(--fg); }
.tab.active {
  color: var(--fg); background: var(--panel); border-color: var(--border);
  border-bottom: 1px solid var(--panel); margin-bottom: -1px;
}

section.skill { display: none; }
section.skill.active { display: block; }

.summary-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px; margin-bottom: 22px;
}
.card {
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 8px; padding: 14px 16px;
}
.card .label { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.6px; }
.card .value { font-size: 22px; font-weight: 600; margin-top: 2px; }
.card .delta { font-size: 12px; margin-top: 4px; }
.delta.good { color: var(--good); }
.delta.bad { color: var(--bad); }
.delta.flat { color: var(--muted); }

.section-title { font-size: 13px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.7px; margin: 24px 0 8px; }

table { width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
th, td { text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--border); }
th { background: var(--panel-2); font-weight: 600; font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
tr:last-child td { border-bottom: none; }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
td.lift-pos { color: var(--good); }
td.lift-neg { color: var(--bad); }
.row-clickable { cursor: pointer; transition: background 0.1s; }
.row-clickable:hover { background: rgba(110, 168, 255, 0.06); }
.row-clickable.open { background: rgba(110, 168, 255, 0.1); }
.row-clickable .chev { display: inline-block; width: 12px; transition: transform 0.15s; color: var(--muted); }
.row-clickable.open .chev { transform: rotate(90deg); }

.detail {
  background: var(--panel-2); border: 1px solid var(--border); border-top: none;
  padding: 16px 20px 20px;
}
.detail h4 { margin: 14px 0 6px; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.7px; font-weight: 600; }
.detail h4:first-child { margin-top: 0; }
.detail .prompt-box {
  background: var(--code-bg); border: 1px solid var(--border); border-radius: 6px;
  padding: 12px 14px; white-space: pre-wrap; word-wrap: break-word; color: var(--fg);
  font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; font-size: 13px;
}
.ideal-traits { color: var(--muted); }
.ideal-traits li { margin: 2px 0; }

.condition-block {
  border: 1px solid var(--border); border-radius: 6px; margin-bottom: 8px; overflow: hidden;
}
.condition-header {
  padding: 9px 14px; background: var(--panel); cursor: pointer;
  display: flex; align-items: center; justify-content: space-between;
}
.condition-header:hover { background: var(--panel-2); }
.condition-header .name { font-weight: 600; }
.condition-header .pill {
  display: inline-block; padding: 1px 8px; border-radius: 999px;
  font-size: 11px; font-weight: 600; margin-left: 8px;
}
.pill.score-5 { background: rgba(78, 201, 176, 0.18); color: var(--good); }
.pill.score-4 { background: rgba(110, 168, 255, 0.18); color: var(--accent); }
.pill.score-3 { background: rgba(255, 180, 84, 0.18); color: var(--warn); }
.pill.score-low { background: rgba(244, 135, 113, 0.18); color: var(--bad); }
.pill.err { background: rgba(244, 135, 113, 0.25); color: var(--bad); }
.condition-body {
  padding: 14px 16px; background: var(--code-bg); border-top: 1px solid var(--border);
  display: none;
}
.condition-block.open .condition-body { display: block; }
.condition-body pre {
  white-space: pre-wrap; word-wrap: break-word; margin: 0; color: var(--fg);
  font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; font-size: 13px; line-height: 1.55;
}
.scores-mini { color: var(--muted); font-size: 12px; margin-top: 8px; }
.scores-mini .sk { color: var(--fg); margin-right: 8px; }

.toolbar { display: flex; gap: 10px; align-items: center; margin-bottom: 10px; }
.toolbar input[type="text"] {
  background: var(--panel); color: var(--fg); border: 1px solid var(--border);
  border-radius: 6px; padding: 7px 12px; font-size: 13px; flex: 1; max-width: 360px;
}
.toolbar select {
  background: var(--panel); color: var(--fg); border: 1px solid var(--border);
  border-radius: 6px; padding: 7px 10px; font-size: 13px;
}

.diff-easy { color: var(--good); }
.diff-med { color: var(--warn); }
.diff-hard { color: var(--bad); }

.no-data { color: var(--muted); font-style: italic; padding: 32px; text-align: center; }
</style>
</head>
<body>
<header>
  <h1>campus-skills · evaluation results</h1>
  <div class="meta">
    Source: <a href="https://github.com/King-Wood-Shen/campus-skills" target="_blank">King-Wood-Shen/campus-skills</a>
    · methodology: <a href="https://github.com/King-Wood-Shen/campus-skills/blob/main/docs/methodology.md" target="_blank">docs/methodology.md</a>
    · <span id="generated-at"></span>
  </div>
</header>
<main>
  <div class="tabs" id="tabs"></div>
  <div id="sections"></div>
</main>
"""


_HTML_BODY = """"""


_HTML_SCRIPT = """<script>
(function () {
  const data = JSON.parse(document.getElementById("eval-data").textContent);
  const RUBRIC = data.rubric;
  const ORDER = data.conditions_order;
  const LABELS = data.condition_labels;

  document.getElementById("generated-at").textContent =
    "generated " + data.generated;

  const skills = Object.keys(data.skills).sort();
  const tabsEl = document.getElementById("tabs");
  const sectionsEl = document.getElementById("sections");

  if (skills.length === 0) {
    sectionsEl.innerHTML = '<div class="no-data">No eval runs found.</div>';
    return;
  }

  skills.forEach((name, i) => {
    const tab = document.createElement("div");
    tab.className = "tab" + (i === 0 ? " active" : "");
    tab.textContent = name;
    tab.dataset.skill = name;
    tab.onclick = () => activate(name);
    tabsEl.appendChild(tab);

    const section = document.createElement("section");
    section.className = "skill" + (i === 0 ? " active" : "");
    section.id = "sk-" + cssEscape(name);
    section.innerHTML = renderSkill(name, data.skills[name]);
    sectionsEl.appendChild(section);

    bindSection(section, data.skills[name]);
  });

  function activate(name) {
    document.querySelectorAll(".tab").forEach(t =>
      t.classList.toggle("active", t.dataset.skill === name));
    document.querySelectorAll("section.skill").forEach(s =>
      s.classList.toggle("active", s.id === "sk-" + cssEscape(name)));
  }

  function renderSkill(name, sk) {
    const summary = computeSummary(sk);
    return `
      <div class="meta" style="color: var(--muted); margin-bottom: 4px;">
        ${escape(sk.description || "")}
      </div>
      <div class="meta" style="color: var(--muted); font-size: 12px; margin-bottom: 16px;">
        run dir: <code>${escape(sk.run_dir)}</code> · ${sk.scenarios.length} scenarios · generated ${escape(sk.generated || "—")}
      </div>

      <div class="summary-grid">
        ${summaryCard("Without skill", summary.without, summary.without_dim)}
        ${summaryCard("With full skill", summary.with_, summary.with_dim, summary.lift)}
        ${dimCard("Largest lift", summary.biggest_dim_name, summary.biggest_dim_delta)}
        ${dimCard("Smallest lift", summary.smallest_dim_name, summary.smallest_dim_delta)}
      </div>

      <div class="section-title">Aggregate scores by condition</div>
      <table>
        <thead>
          <tr>
            <th>Condition</th>
            ${RUBRIC.map(d => `<th class="num">${prettyDim(d)}</th>`).join("")}
            <th class="num">Overall</th>
            <th class="num">Mean tokens out</th>
          </tr>
        </thead>
        <tbody>
          ${ORDER.map(c => aggregateRow(c, sk)).join("")}
        </tbody>
      </table>

      <div class="section-title">Per-scenario results — click a row to expand</div>
      <div class="toolbar">
        <input type="text" placeholder="filter by id, difficulty, prompt text…" data-search />
        <select data-diff>
          <option value="">all difficulties</option>
          <option value="easy">easy</option>
          <option value="med">med</option>
          <option value="hard">hard</option>
        </select>
      </div>
      <table data-scenario-table>
        <thead>
          <tr>
            <th></th>
            <th>ID</th>
            <th>Difficulty</th>
            <th class="num">w/o</th>
            <th class="num">w/ skill</th>
            <th class="num">Lift</th>
            ${ORDER.filter(c => c.startsWith("ablate_")).map(c =>
              `<th class="num" title="${escape(LABELS[c])}">${shortAblateLabel(c)}</th>`).join("")}
            <th>Prompt (truncated)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    `;
  }

  function aggregateRow(cond, sk) {
    const rs = sk.scenarios
      .map(s => s.conditions[cond])
      .filter(c => c && c.scores);
    if (rs.length === 0) {
      return `<tr><td>${escape(LABELS[cond] || cond)}</td><td colspan="${RUBRIC.length + 2}" class="num">—</td></tr>`;
    }
    const dim = {};
    RUBRIC.forEach(d => dim[d] = mean(rs.map(r => r.scores[d])));
    const overall = mean(Object.values(dim));
    const tok = mean(rs.map(r => r.tokens_out).filter(x => x != null));
    const cls = cond === "with_skill" ? "lift-pos" : (cond === "without_skill" ? "" : "");
    return `
      <tr>
        <td>${escape(LABELS[cond] || cond)}</td>
        ${RUBRIC.map(d => `<td class="num">${dim[d].toFixed(2)}</td>`).join("")}
        <td class="num"><b>${overall.toFixed(2)}</b></td>
        <td class="num">${tok ? Math.round(tok) : "—"}</td>
      </tr>`;
  }

  function bindSection(section, sk) {
    const tbody = section.querySelector("[data-scenario-table] tbody");
    const search = section.querySelector("[data-search]");
    const diffSel = section.querySelector("[data-diff]");

    function render() {
      const q = (search.value || "").toLowerCase().trim();
      const diff = diffSel.value;
      tbody.innerHTML = "";
      sk.scenarios.forEach(scn => {
        if (diff && scn.difficulty !== diff) return;
        if (q) {
          const hay = (scn.id + " " + (scn.difficulty || "") + " " + (scn.prompt || "")).toLowerCase();
          if (!hay.includes(q)) return;
        }
        addScenarioRow(tbody, scn);
      });
    }
    search.oninput = render;
    diffSel.onchange = render;
    render();
  }

  function addScenarioRow(tbody, scn) {
    const wo = overall(scn.conditions["without_skill"]);
    const ws = overall(scn.conditions["with_skill"]);
    const lift = (typeof wo === "number" && typeof ws === "number") ? (ws - wo) : null;
    const tr = document.createElement("tr");
    tr.className = "row-clickable";
    tr.innerHTML = `
      <td><span class="chev">▶</span></td>
      <td><code>${escape(scn.id)}</code></td>
      <td><span class="diff-${escape(scn.difficulty || "")}">${escape(scn.difficulty || "—")}</span></td>
      <td class="num">${fmt(wo)}</td>
      <td class="num"><b>${fmt(ws)}</b></td>
      <td class="num ${liftClass(lift)}">${liftStr(lift)}</td>
      ${ORDER.filter(c => c.startsWith("ablate_")).map(c =>
        `<td class="num">${fmt(overall(scn.conditions[c]))}</td>`).join("")}
      <td style="color: var(--muted); max-width: 420px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
        ${escape((scn.prompt || "").slice(0, 200))}
      </td>
    `;
    const detail = document.createElement("tr");
    detail.style.display = "none";
    detail.innerHTML = `<td colspan="${ORDER.filter(c => c.startsWith("ablate_")).length + 7}" style="padding: 0;">
      <div class="detail">${renderDetail(scn)}</div>
    </td>`;
    tr.onclick = () => {
      const open = tr.classList.toggle("open");
      detail.style.display = open ? "" : "none";
    };
    tbody.appendChild(tr);
    tbody.appendChild(detail);
  }

  function renderDetail(scn) {
    return `
      <h4>Prompt</h4>
      <div class="prompt-box">${escape(scn.prompt || "")}</div>
      <h4>Ideal traits (judge sees these)</h4>
      <ul class="ideal-traits">${(scn.ideal_traits || []).map(t => `<li>${escape(t)}</li>`).join("")}</ul>
      <h4>Outputs by condition (click a header to expand)</h4>
      ${ORDER.map(c => conditionBlock(c, scn.conditions[c])).join("")}
    `;
  }

  function conditionBlock(cond, c) {
    if (!c) {
      return `<div class="condition-block"><div class="condition-header"><span class="name">${escape(LABELS[cond] || cond)}</span><span class="pill err">missing</span></div></div>`;
    }
    const ov = overall(c);
    let pill;
    if (c.error) pill = `<span class="pill err">ERROR</span>`;
    else if (typeof ov !== "number") pill = `<span class="pill err">no score</span>`;
    else if (ov >= 4.5) pill = `<span class="pill score-5">${ov.toFixed(2)}</span>`;
    else if (ov >= 3.5) pill = `<span class="pill score-4">${ov.toFixed(2)}</span>`;
    else if (ov >= 2.5) pill = `<span class="pill score-3">${ov.toFixed(2)}</span>`;
    else pill = `<span class="pill score-low">${ov.toFixed(2)}</span>`;

    const tokens = c.tokens_out != null ? `${c.tokens_out} tokens out` : "";
    let scoreLine = "";
    if (c.scores && !c.error) {
      scoreLine = `<div class="scores-mini">${RUBRIC.map(d => `<span class="sk">${prettyDim(d)}: ${c.scores[d]}</span>`).join("")}${tokens ? ` · ${tokens}` : ""}</div>`;
    }
    const body = c.error
      ? `<pre style="color: var(--bad);">${escape(c.error)}</pre>`
      : `<pre>${escape(c.model_output || "(empty)")}</pre>${scoreLine}`;

    return `
      <div class="condition-block">
        <div class="condition-header">
          <span class="name">${escape(LABELS[cond] || cond)} ${pill}</span>
          <span style="color: var(--muted); font-size: 12px;">${escape(tokens)}</span>
        </div>
        <div class="condition-body">${body}</div>
      </div>`;
  }

  document.addEventListener("click", e => {
    const h = e.target.closest(".condition-header");
    if (!h) return;
    h.parentElement.classList.toggle("open");
  });

  function computeSummary(sk) {
    const wo = sk.scenarios.map(s => s.conditions["without_skill"]).filter(c => c && c.scores);
    const ws = sk.scenarios.map(s => s.conditions["with_skill"]).filter(c => c && c.scores);
    const dim_wo = {}, dim_ws = {};
    RUBRIC.forEach(d => {
      dim_wo[d] = mean(wo.map(r => r.scores[d]));
      dim_ws[d] = mean(ws.map(r => r.scores[d]));
    });
    const overall_wo = mean(Object.values(dim_wo));
    const overall_ws = mean(Object.values(dim_ws));
    const deltas = RUBRIC.map(d => [d, dim_ws[d] - dim_wo[d]]);
    deltas.sort((a, b) => b[1] - a[1]);
    return {
      without: overall_wo, with_: overall_ws, lift: overall_ws - overall_wo,
      without_dim: dim_wo, with_dim: dim_ws,
      biggest_dim_name: deltas[0][0], biggest_dim_delta: deltas[0][1],
      smallest_dim_name: deltas[deltas.length - 1][0], smallest_dim_delta: deltas[deltas.length - 1][1],
    };
  }

  function summaryCard(label, value, dim, lift) {
    let liftEl = "";
    if (typeof lift === "number") {
      const cls = lift > 0.05 ? "good" : lift < -0.05 ? "bad" : "flat";
      liftEl = `<div class="delta ${cls}">${lift >= 0 ? "+" : ""}${lift.toFixed(2)} vs. baseline</div>`;
    }
    return `<div class="card"><div class="label">${escape(label)}</div><div class="value">${value.toFixed(2)}</div>${liftEl}</div>`;
  }
  function dimCard(label, dimName, delta) {
    const cls = delta > 0.05 ? "good" : delta < -0.05 ? "bad" : "flat";
    return `<div class="card"><div class="label">${escape(label)}</div><div class="value" style="font-size: 16px;">${prettyDim(dimName)}</div><div class="delta ${cls}">${delta >= 0 ? "+" : ""}${delta.toFixed(2)}</div></div>`;
  }

  function overall(c) {
    if (!c || !c.scores) return null;
    return mean(RUBRIC.map(d => c.scores[d]));
  }
  function mean(xs) {
    const n = xs.filter(x => x != null && !isNaN(x));
    if (!n.length) return null;
    return n.reduce((a, b) => a + b, 0) / n.length;
  }
  function fmt(x) { return typeof x === "number" ? x.toFixed(2) : "—"; }
  function liftStr(x) {
    if (typeof x !== "number") return "—";
    return (x >= 0 ? "+" : "") + x.toFixed(2);
  }
  function liftClass(x) {
    if (typeof x !== "number") return "";
    if (x > 0.5) return "lift-pos";
    if (x < -0.5) return "lift-neg";
    return "";
  }
  function prettyDim(d) {
    return d.replace(/_/g, " ").replace(/\\b\\w/g, c => c.toUpperCase());
  }
  function shortAblateLabel(c) {
    return ({
      "ablate_expert_knowledge": "−EK",
      "ablate_workflow": "−WF",
      "ablate_output_template": "−OT",
      "ablate_examples": "−EX",
    })[c] || c;
  }
  function escape(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
  function cssEscape(s) { return s.replace(/[^a-zA-Z0-9_-]/g, "_"); }
})();
</script>
"""


_HTML_TAIL = """</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(main())
