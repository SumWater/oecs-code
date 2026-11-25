"""Generate the three core manuscript figures from frozen paper artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import subprocess
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
FIGURE_DIR = ROOT / "manuscript" / "figures"
DATA_DIR = FIGURE_DIR / "data"
E2E3 = ROOT / "outputs" / "paper_2026" / "e2_e3_formal_analysis" / "tables.json"
E4 = ROOT / "outputs" / "paper_2026" / "e4_diagnostics" / "diagnostics.json"
PROVENANCE = ROOT / "paper" / "generated" / "provenance_manifest.json"
RENDERER = ROOT / "manuscript" / "scripts" / "render_svg.js"
NODE = None

WIDTH = 2100
FONT = "Arial, Helvetica, sans-serif"
QWEN = "#0072B2"
MISTRAL = "#D55E00"
POSITIVE = "#009E73"
NEGATIVE = "#CC6677"
INK = "#1B1F23"
MUTED = "#59636E"
GRID = "#D9DEE3"
PALE_BLUE = "#EAF3F8"
PALE_TEAL = "#E8F5F0"
PALE_RED = "#F9EDEF"
WHITE = "#FFFFFF"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def verify_sources() -> dict[str, str]:
    manifest = load_json(PROVENANCE)
    expected = {entry["name"]: entry for entry in manifest["sources"]}
    checks = {"e2e3_tables": E2E3, "e4_diagnostics": E4}
    identities: dict[str, str] = {}
    for name, path in checks.items():
        actual = sha256(path)
        if name not in expected:
            raise ValueError(f"provenance manifest lacks {name}")
        if actual != expected[name]["sha256"]:
            raise ValueError(f"hash mismatch for {path}: {actual}")
        identities[str(path.relative_to(ROOT)).replace("\\", "/")] = actual
    return identities


def unique(rows: list[dict[str, Any]], predicate, label: str) -> dict[str, Any]:
    found = [row for row in rows if predicate(row)]
    if len(found) != 1:
        raise ValueError(f"expected one {label} row, found {len(found)}")
    return found[0]


def fmt_pp(value: float) -> str:
    return f"{value * 100:.2f}"


def text(x: float, y: float, value: str, size: int = 30, anchor: str = "start", weight: int = 400,
         fill: str = INK, extra: str = "") -> str:
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill}" {extra}>{escape(value)}</text>')


def line(x1: float, y1: float, x2: float, y2: float, stroke: str = GRID, width: float = 2,
         dash: str | None = None) -> str:
    dashed = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}"{dashed}/>'


def rect(x: float, y: float, w: float, h: float, fill: str = WHITE, stroke: str = GRID,
         width: float = 2, radius: float = 18, dash: str | None = None) -> str:
    dashed = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{width}"{dashed}/>')


def circle(x: float, y: float, r: float, fill: str, stroke: str = WHITE, width: float = 3) -> str:
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def diamond(x: float, y: float, r: float, fill: str, stroke: str = WHITE, width: float = 3) -> str:
    points = f"{x:.1f},{y-r:.1f} {x+r:.1f},{y:.1f} {x:.1f},{y+r:.1f} {x-r:.1f},{y:.1f}"
    return f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def arrow(x1: float, y1: float, x2: float, y2: float, color: str = MUTED) -> str:
    angle = math.atan2(y2 - y1, x2 - x1)
    head = 15
    p1 = (x2 - head * math.cos(angle - 0.5), y2 - head * math.sin(angle - 0.5))
    p2 = (x2 - head * math.cos(angle + 0.5), y2 - head * math.sin(angle + 0.5))
    return (line(x1, y1, x2, y2, color, 4) +
            f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')


def svg_document(height: int, body: Iterable[str], title_value: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
            f'viewBox="0 0 {WIDTH} {height}" role="img" aria-label="{escape(title_value)}">'
            f'<title>{escape(title_value)}</title><rect width="100%" height="100%" fill="white"/>'
            + "".join(body) + "</svg>\n")


def write_svg(stem: str, height: int, body: Iterable[str], title_value: str) -> Path:
    path = FIGURE_DIR / f"{stem}.svg"
    path.write_text(svg_document(height, body, title_value), encoding="utf-8")
    return path


def render(svg_path: Path) -> tuple[Path, Path]:
    png = svg_path.with_suffix(".png")
    pdf = svg_path.with_suffix(".pdf")
    if not NODE.exists():
        raise FileNotFoundError(f"bundled Node.js not found: {NODE}")
    subprocess.run([str(NODE), str(RENDERER), str(svg_path), str(png), str(pdf)], check=True)
    return png, pdf


def write_csv(name: str, rows: list[dict[str, Any]], fields: list[str]) -> Path:
    path = DATA_DIR / name
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


def pipeline_figure() -> Path:
    h = 1180
    parts = [text(1050, 72, "Conservative selection from observable execution evidence", 42, "middle", 500)]
    stages = [
        (70, 155, 380, 330, PALE_BLUE, "1  Observable state", ["Task instruction", "Latest tool error", "Public tool interfaces", "Execution trace", "Remaining budget"]),
        (510, 155, 380, 330, WHITE, "2  Candidate memories", ["TF-IDF Top-10", "Policy-card extraction", "Trigger and preconditions", "Repair target", "Proposed tool/action"]),
        (950, 155, 500, 330, WHITE, "3  Applicability checks", ["Operation-specific support", "Precondition status", "Repair-target agreement", "Tool compatibility", "Contradiction evidence"]),
        (1510, 135, 520, 370, PALE_TEAL, "4  Conservative gate", ["Replace Rank-1 only when", "an eligible alternative is", "supported and decisively", "superior on a declared", "compatibility dimension"]),
    ]
    for x, y, w, hh, fill, heading, items in stages:
        parts.append(rect(x, y, w, hh, fill, "#9AA5AF", 2.5, 20))
        parts.append(text(x + 28, y + 53, heading, 32, weight=500))
        for i, item in enumerate(items):
            yy = y + 105 + i * 46
            parts.append(circle(x + 34, yy - 9, 5, MUTED, MUTED, 0))
            parts.append(text(x + 52, yy, item, 27, fill=MUTED))
    parts += [arrow(450, 320, 505, 320), arrow(890, 320, 945, 320), arrow(1450, 320, 1505, 320)]

    outcomes = [(1325, 585, 220, PALE_BLUE, "Keep Rank-1"),
                (1575, 585, 270, PALE_TEAL, "Select alternative"),
                (1875, 585, 155, "#F2F3F5", "Abstain")]
    parts.append(arrow(1770, 505, 1770, 545))
    parts.append(line(1435, 545, 1952, 545, MUTED, 3))
    for x, y, w, fill, label in outcomes:
        parts.append(arrow(x + w / 2, 545, x + w / 2, 575))
        parts.append(rect(x, y, w, 95, fill, "#9AA5AF", 2, 14))
        parts.append(text(x + w / 2, y + 58, label, 24, "middle", 500))
    parts.append(text(1952, 724, "Declines to replace; does not", 22, "middle", fill=MUTED))
    parts.append(text(1952, 753, "certify Rank-1 applicability", 22, "middle", fill=MUTED))

    parts.append(rect(70, 825, 1960, 285, PALE_RED, NEGATIVE, 2.5, 18, "14 10"))
    parts.append(text(105, 890, "Forbidden selector inputs", 31, weight=500, fill="#8B3A4A"))
    forbidden = ["Benchmark or scenario identity", "Hidden fault plan", "Gold action",
                 "Evaluator outcome", "Prior model outcomes"]
    positions = [(105, 960), (740, 960), (1280, 960), (105, 1022), (740, 1022)]
    for (x, y), label in zip(positions, forbidden):
        parts.append(text(x, y + 5, "×", 36, weight=500, fill=NEGATIVE))
        parts.append(text(x + 38, y, label, 24, fill="#6E4048"))
    parts.append(text(105, 1075, "Rejected at the input boundary; no path connects these fields to the selector.", 23, fill="#6E4048"))
    return write_svg("proper_pipeline", h, parts, "Observable-evidence conservative selection pipeline")


@dataclass
class ForestRow:
    model: str
    baseline: str
    n: int
    positive: int
    negative: int
    effect: float
    low: float
    high: float
    family: str
    population: str
    status: str
    source_path: str
    source_sha256: str


def forest_rows(e2: dict[str, Any], identities: dict[str, str]) -> list[ForestRow]:
    rows = e2["inference_rows"]
    source_path = str(E2E3.relative_to(ROOT)).replace("\\", "/")
    source_hash = identities[source_path]
    output: list[ForestRow] = []
    for population, family, status in [
        ("changed_target_union", "primary_proper_vs_tfidf", "formal primary"),
        ("changed_target_union", "key_secondary_selector_baselines", "formal key secondary"),
        ("all_valid_targets", "all_valid_sensitivity", "sensitivity"),
    ]:
        baselines = ["tfidf"] if family != "key_secondary_selector_baselines" else ["dense", "llm_judge"]
        for baseline in baselines:
            for model in ["qwen3_8b", "mistral_7b_instruct_v0_3"]:
                row = unique(rows, lambda r, p=population, f=family, b=baseline, m=model:
                             r["population"] == p and r["family"] == f and r["baseline"] == b
                             and r["model_name"] == m and r["stratum"] == "all_strata",
                             f"{family}/{baseline}/{model}")
                expected_n = 403 if population == "changed_target_union" else 541
                if row["pair_count"] != expected_n:
                    raise ValueError(f"unexpected n for {row['analysis_id']}")
                ci = row["paired_bootstrap_ci"]
                output.append(ForestRow(model, baseline, row["pair_count"], row["positive_discordant"],
                                        row["negative_discordant"], row["paired_risk_difference"], ci["lower"],
                                        ci["upper"], family, population, status, source_path, source_hash))
    if len(output) != 8:
        raise ValueError(f"overall figure requires 8 unique rows, found {len(output)}")
    return output


def forest_x(value: float, left: float, right: float, xmin: float, xmax: float) -> float:
    return left + (value - xmin) / (xmax - xmin) * (right - left)


def overall_figure(rows: list[ForestRow]) -> Path:
    h = 1320
    parts = [text(1050, 70, "Paired effects on Recovery Validity", 42, "middle", 500)]
    left, right = 760, 1670
    xmin, xmax = -2.0, 15.0
    zero = forest_x(0, left, right, xmin, xmax)

    parts.append(text(70, 135, "A  Changed-target union (n = 403)", 32, weight=500))
    parts.append(text(1750, 135, "+ / −", 27, "middle", 500, MUTED))
    for tick in [-2, 0, 5, 10, 15]:
        x = forest_x(tick, left, right, xmin, xmax)
        parts.append(line(x, 180, x, 820, GRID if tick else "#7B858E", 2 if tick else 3))
        parts.append(text(x, 858, str(tick), 25, "middle", fill=MUTED))
    parts.append(text((left + right) / 2, 902, "Paired risk difference (percentage points)", 28, "middle", 500))

    baseline_order = ["tfidf", "dense", "llm_judge"]
    labels = {"tfidf": "Proposed vs TF-IDF  [primary]", "dense": "Proposed vs Dense",
              "llm_judge": "Proposed vs fixed LLM Judge"}
    y = 235
    for baseline in baseline_order:
        parts.append(text(70, y, labels[baseline], 29, weight=500))
        group = [r for r in rows if r.population == "changed_target_union" and r.baseline == baseline]
        for model in ["qwen3_8b", "mistral_7b_instruct_v0_3"]:
            row = next(r for r in group if r.model == model)
            y += 72
            color = QWEN if model == "qwen3_8b" else MISTRAL
            model_label = "Qwen3-8B" if model == "qwen3_8b" else "Mistral-7B-Instruct-v0.3"
            parts.append(text(110, y + 10, model_label, 27, fill=MUTED))
            lo = forest_x(row.low * 100, left, right, xmin, xmax)
            hi = forest_x(row.high * 100, left, right, xmin, xmax)
            point = forest_x(row.effect * 100, left, right, xmin, xmax)
            parts += [line(lo, y, hi, y, color, 5), line(lo, y - 11, lo, y + 11, color, 4),
                      line(hi, y - 11, hi, y + 11, color, 4)]
            parts.append(circle(point, y, 13, color) if model == "qwen3_8b" else diamond(point, y, 15, color))
            parts.append(text(hi + 20, y + 10, f"{row.effect*100:.2f}", 25, fill=color))
            parts.append(text(1750, y + 10, f"{row.positive} / {row.negative}", 26, "middle"))
        y += 64

    parts.append(text(70, 985, "B  All-valid sensitivity (n = 541)", 32, weight=500))
    for tick in [-2, 0, 5, 10, 15]:
        x = forest_x(tick, left, right, xmin, xmax)
        parts.append(line(x, 1030, x, 1195, GRID if tick else "#7B858E", 2 if tick else 3))
        parts.append(text(x, 1235, str(tick), 25, "middle", fill=MUTED))
    parts.append(text(70, 1065, "Proposed vs TF-IDF", 29, weight=500))
    y = 1105
    sensitivity = [r for r in rows if r.population == "all_valid_targets"]
    for model in ["qwen3_8b", "mistral_7b_instruct_v0_3"]:
        row = next(r for r in sensitivity if r.model == model)
        color = QWEN if model == "qwen3_8b" else MISTRAL
        label = "Qwen3-8B" if model == "qwen3_8b" else "Mistral-7B-Instruct-v0.3"
        parts.append(text(110, y + 10, label, 27, fill=MUTED))
        lo, hi = forest_x(row.low * 100, left, right, xmin, xmax), forest_x(row.high * 100, left, right, xmin, xmax)
        point = forest_x(row.effect * 100, left, right, xmin, xmax)
        parts += [line(lo, y, hi, y, color, 5), line(lo, y - 11, lo, y + 11, color, 4),
                  line(hi, y - 11, hi, y + 11, color, 4)]
        parts.append(circle(point, y, 13, color) if model == "qwen3_8b" else diamond(point, y, 15, color))
        parts.append(text(hi + 20, y + 10, f"{row.effect*100:.2f}", 25, fill=color))
        y += 70
    parts.append(text(1840, 1280, "● Qwen   ◆ Mistral", 24, "middle", fill=MUTED))
    return write_svg("overall_paired_effects", h, parts, "Overall paired Recovery Validity effects")


def heterogeneity_rows(e2: dict[str, Any], identities: dict[str, str]) -> list[dict[str, Any]]:
    source_path = str(E2E3.relative_to(ROOT)).replace("\\", "/")
    source_hash = identities[source_path]
    result = []
    for stratum, expected_n in [("argument_omission", 152), ("transient_authorization", 146), ("timeout", 105)]:
        for model in ["qwen3_8b", "mistral_7b_instruct_v0_3"]:
            row = unique(e2["inference_rows"], lambda r, s=stratum, m=model:
                         r["family"] == "stratified_primary_exploratory" and r["stratum"] == s
                         and r["model_name"] == m and r["baseline"] == "tfidf",
                         f"stratified/{stratum}/{model}")
            if row["pair_count"] != expected_n:
                raise ValueError(f"unexpected stratified n for {row['analysis_id']}")
            ci = row["paired_bootstrap_ci"]
            result.append({"source_path": source_path, "source_sha256": source_hash,
                           "population": row["population"], "analysis_status": "exploratory stratified",
                           "model": model, "comparison": "proper_vs_tfidf", "stratum": stratum,
                           "n": row["pair_count"], "positive_discordant": row["positive_discordant"],
                           "negative_discordant": row["negative_discordant"],
                           "effect_pp": row["paired_risk_difference"] * 100,
                           "ci_lower_pp": ci["lower"] * 100, "ci_upper_pp": ci["upper"] * 100})
    if len(result) != 6:
        raise ValueError("heterogeneity panel requires six rows")
    return result


def transfer_rows(e4: dict[str, Any], identities: dict[str, str]) -> list[dict[str, Any]]:
    source_path = str(E4.relative_to(ROOT)).replace("\\", "/")
    source_hash = identities[source_path]
    result = []
    for model in ["qwen3_8b", "mistral_7b_instruct_v0_3"]:
        row = unique(e4["risk_rows"], lambda r, m=model: r["model_name"] == m and r["baseline"] == "no_memory"
                     and r["treatment"] == "proper" and r["population"] == "changed_target_union"
                     and r["stratum"] == "all_strata", f"risk/proper/no_memory/{model}")
        if row["n"] != 403:
            raise ValueError("transfer panel requires n=403")
        result.append({"source_path": source_path, "source_sha256": source_hash,
                       "population": row["population"], "analysis_status": "descriptive",
                       "model": model, "comparison": "proper_vs_no_memory", "n": row["n"],
                       "positive_transfer": row["positive_transfer"], "negative_transfer": row["negative_transfer"],
                       "positive_share_pp": row["positive_transfer"] / row["n"] * 100,
                       "negative_share_pp": row["negative_transfer"] / row["n"] * 100,
                       "net_effect_pp": row["paired_risk_difference"] * 100})
    return result


def heterogeneity_figure(strata: list[dict[str, Any]], transfers: list[dict[str, Any]]) -> Path:
    h = 1540
    parts = [text(1050, 70, "Heterogeneity and absolute memory utility", 42, "middle", 500),
             text(70, 135, "A  Proposed vs TF-IDF by failure stratum — exploratory", 32, weight=500)]
    left, right = 790, 1760
    xmin, xmax = -5.0, 22.0
    for tick in [-5, 0, 5, 10, 15, 20]:
        x = forest_x(tick, left, right, xmin, xmax)
        parts.append(line(x, 185, x, 840, GRID if tick else "#7B858E", 2 if tick else 3))
        parts.append(text(x, 878, str(tick), 25, "middle", fill=MUTED))
    parts.append(text((left + right) / 2, 922, "Paired risk difference (percentage points)", 28, "middle", 500))
    names = {"argument_omission": "Argument omission", "transient_authorization": "Transient authorization",
             "timeout": "Timeout"}
    y = 235
    for stratum in ["argument_omission", "transient_authorization", "timeout"]:
        parts.append(text(70, y, names[stratum], 29, weight=500))
        for model in ["qwen3_8b", "mistral_7b_instruct_v0_3"]:
            row = next(r for r in strata if r["stratum"] == stratum and r["model"] == model)
            y += 76
            color = QWEN if model == "qwen3_8b" else MISTRAL
            label = "Qwen3-8B" if model == "qwen3_8b" else "Mistral-7B-Instruct-v0.3"
            parts.append(text(110, y + 10, f"{label}  (n={row['n']}, +/− {row['positive_discordant']}/{row['negative_discordant']})", 25, fill=MUTED))
            lo, hi = forest_x(row["ci_lower_pp"], left, right, xmin, xmax), forest_x(row["ci_upper_pp"], left, right, xmin, xmax)
            point = forest_x(row["effect_pp"], left, right, xmin, xmax)
            parts += [line(lo, y, hi, y, color, 5), line(lo, y - 11, lo, y + 11, color, 4),
                      line(hi, y - 11, hi, y + 11, color, 4)]
            parts.append(circle(point, y, 13, color) if model == "qwen3_8b" else diamond(point, y, 15, color))
            label_x = max(point, hi) + 22
            parts.append(text(label_x, y + 10, f"{row['effect_pp']:.2f}", 25, fill=color))
        y += 65

    parts.append(text(70, 1025, "B  Positive and negative transfer vs No Memory — descriptive", 32, weight=500))
    center, scale = 1050, 24
    for tick in [-20, -10, 0, 10, 20, 30]:
        x = center + tick * scale
        parts.append(line(x, 1080, x, 1390, GRID if tick else "#7B858E", 2 if tick else 3))
        parts.append(text(x, 1430, str(abs(tick)), 25, "middle", fill=MUTED))
    parts.append(text(center - 300, 1480, "Negative-transfer share (%)", 27, "middle", 500))
    parts.append(text(center + 390, 1480, "Positive-transfer share (%)", 27, "middle", 500))
    y = 1170
    for model in ["qwen3_8b", "mistral_7b_instruct_v0_3"]:
        row = next(r for r in transfers if r["model"] == model)
        label = "Qwen3-8B" if model == "qwen3_8b" else "Mistral-7B-Instruct-v0.3"
        parts.append(text(70, y + 15, label, 29, weight=500))
        neg_w, pos_w = row["negative_share_pp"] * scale, row["positive_share_pp"] * scale
        parts.append(f'<rect x="{center-neg_w:.1f}" y="{y-28}" width="{neg_w:.1f}" height="56" fill="{NEGATIVE}"/>')
        parts.append(f'<rect x="{center:.1f}" y="{y-28}" width="{pos_w:.1f}" height="56" fill="{POSITIVE}"/>')
        parts.append(text(center - neg_w - 18, y + 10, f"−{row['negative_transfer']}", 25, "end", fill=NEGATIVE))
        parts.append(text(center + pos_w + 18, y + 10, f"+{row['positive_transfer']}", 25, fill=POSITIVE))
        parts.append(text(2070, y + 10, f"Net {row['net_effect_pp']:+.2f} pp", 27, "end", 500,
                          POSITIVE if row["net_effect_pp"] >= 0 else NEGATIVE))
        y += 145
    return write_svg("heterogeneity_and_transfer", h, parts, "Heterogeneity and positive or negative transfer")


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    identities = verify_sources()
    e2, e4 = load_json(E2E3), load_json(E4)

    overall = forest_rows(e2, identities)
    overall_csv_rows = [{"source_path": r.source_path, "source_sha256": r.source_sha256,
                         "population": r.population, "analysis_status": r.status, "model": r.model,
                         "comparison": f"proper_vs_{r.baseline}", "n": r.n,
                         "positive_discordant": r.positive, "negative_discordant": r.negative,
                         "effect_pp": r.effect * 100, "ci_lower_pp": r.low * 100,
                         "ci_upper_pp": r.high * 100} for r in overall]
    common_fields = ["source_path", "source_sha256", "population", "analysis_status", "model", "comparison",
                     "n", "positive_discordant", "negative_discordant", "effect_pp", "ci_lower_pp", "ci_upper_pp"]
    csv_paths = [write_csv("overall_paired_effects.csv", overall_csv_rows, common_fields)]

    strata = heterogeneity_rows(e2, identities)
    transfers = transfer_rows(e4, identities)
    csv_paths.append(write_csv("heterogeneity_stratified.csv", strata,
                               common_fields[:6] + ["stratum"] + common_fields[6:]))
    csv_paths.append(write_csv("transfer_vs_no_memory.csv", transfers,
                               ["source_path", "source_sha256", "population", "analysis_status", "model",
                                "comparison", "n", "positive_transfer", "negative_transfer",
                                "positive_share_pp", "negative_share_pp", "net_effect_pp"]))

    svgs = [pipeline_figure(), overall_figure(overall), heterogeneity_figure(strata, transfers)]
    outputs: list[Path] = []
    for svg in svgs:
        png, pdf = render(svg)
        outputs.extend([svg, png, pdf])

    captions = ROOT / "manuscript" / "figures" / "core_figure_captions.tex"
    captions.write_text(
        "\\textbf{Figure 1.} Observable-evidence conservative selection pipeline. The selector reads only the public post-failure state and TF-IDF Top-10 policy cards. Abstention declines to replace Rank-1 and does not certify its applicability.\\n\\n"
        "\\textbf{Figure 2.} Paired Recovery Validity effects. Panel A reports the formal primary and key-secondary comparisons on the pre-frozen 403-target changed-target union; Panel B reports the all-valid sensitivity analysis (n=541). Points are paired risk differences and whiskers are 95\\% paired-instance bootstrap intervals from 10,000 replicates. +/− denotes positive/negative discordances.\\n\\n"
        "\\textbf{Figure 3.} Heterogeneity and absolute memory utility. Panel A is an exploratory stratified analysis of the proposed method versus TF-IDF on the changed-target union; points are paired risk differences with 95\\% paired-instance bootstrap intervals. Panel B descriptively reports positive and negative transfer relative to No Memory on the 403-target union; no confidence intervals or hypothesis tests are attached to this panel.\\n",
        encoding="utf-8",
    )
    outputs.append(captions)

    manifest_path = FIGURE_DIR / "core_figure_manifest.json"
    manifest = {
        "schema_version": 1,
        "generator": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
        "generator_sha256": sha256(Path(__file__)),
        "renderer": str(RENDERER.relative_to(ROOT)).replace("\\", "/"),
        "renderer_sha256": sha256(RENDERER),
        "sources": [{"path": path, "sha256": digest} for path, digest in identities.items()],
        "outputs": [{"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path),
                     "bytes": path.stat().st_size} for path in outputs + csv_paths],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "manifest": str(manifest_path), "outputs": len(manifest["outputs"])}, indent=2))


if __name__ == "__main__":
    main()
