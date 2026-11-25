"""Generate submission-style vector figures from the frozen paper evidence.

The visual language is intentionally close to conventional ACL/EMNLP/IEEE
figures: white background, restrained color, thin rules, direct labels, and no
decorative cards or editorial callouts. Source identity checks are delegated to
``generate_core_figures.py``.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
from html import escape
from pathlib import Path

import generate_core_figures as core


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "manuscript" / "figures" / "formal"
RENDERER = ROOT / "manuscript" / "scripts" / "render_svg.js"
NODE = None

W = 2100
FONT = "Arial, Helvetica, sans-serif"
METHOD_FONT = "Times New Roman, Times, serif"
INK = "#202124"
MUTED = "#62676D"
RULE = "#B8BDC3"
GRID = "#E1E4E8"
BLUE = "#1F5A94"
ORANGE = "#B45A16"
DATA_BLUE = "#0072B2"
DATA_ORANGE = "#D55E00"
TRANSFER_POS = "#009E73"
TRANSFER_NEG = "#CC6677"
NEG = "#555B61"
POS = "#A9ADB2"
WHITE = "#FFFFFF"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(x, y, value, size=28, anchor="start", weight=400, fill=INK,
         style=None, rotate=None):
    st = f' font-style="{style}"' if style else ""
    tr = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate is not None else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill}"{st}{tr}>'
            f'{escape(str(value))}</text>')


def line(x1, y1, x2, y2, color=RULE, width=2, dash=None):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{width}"{ds}/>')


def rect(x, y, w, h, fill="none", stroke=RULE, width=2, radius=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')


def circle(x, y, radius, fill, stroke=WHITE, width=3):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{width}"/>')


def diamond(x, y, radius, fill, stroke=WHITE, width=3):
    pts = f"{x:.1f},{y-radius:.1f} {x+radius:.1f},{y:.1f} {x:.1f},{y+radius:.1f} {x-radius:.1f},{y:.1f}"
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def arrow(x1, y1, x2, y2, color=INK, width=2):
    angle = math.atan2(y2 - y1, x2 - x1)
    head = 12
    p1 = (x2 - head * math.cos(angle - .48), y2 - head * math.sin(angle - .48))
    p2 = (x2 - head * math.cos(angle + .48), y2 - head * math.sin(angle + .48))
    return line(x1, y1, x2, y2, color, width) + (
        f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} '
        f'{p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>'
    )


def document(height: int, parts: list[str], title: str, defs: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
            f'viewBox="0 0 {W} {height}" role="img" aria-label="{escape(title)}">'
            f'<title>{escape(title)}</title>{defs}<rect width="100%" height="100%" fill="white"/>'
            + "".join(parts) + "</svg>\n")


def save(stem: str, height: int, parts: list[str], title: str, defs: str = ""):
    OUT.mkdir(parents=True, exist_ok=True)
    svg = OUT / f"{stem}.svg"
    png = OUT / f"{stem}.png"
    pdf = OUT / f"{stem}.pdf"
    svg.write_text(document(height, parts, title, defs), encoding="utf-8")
    return (svg,)


def system_overview_figure():
    global FONT
    previous_font = FONT
    FONT = METHOD_FONT
    h = 620
    p: list[str] = []
    pale_blue = "#F2F6FA"
    pale_gray = "#F7F8F9"

    # Public execution path.
    nodes = [
        (45, 90, 300, 110, "Task + history", "instruction · public trace"),
        (405, 90, 260, 110, "LLM agent", "current execution"),
        (725, 90, 330, 110, "Tool environment", "call · public return"),
    ]
    for x, y, w, hh, title, subtitle in nodes:
        p.append(rect(x, y, w, hh, pale_gray, RULE, 2))
        p.append(text(x + w / 2, y + 47, title, 34, "middle", 500))
        p.append(text(x + w / 2, y + 84, subtitle, 28, "middle", fill=MUTED))
    p.append(arrow(345, 145, 390, 145, MUTED, 3))
    p.append(arrow(665, 145, 710, 145, MUTED, 3))

    # A public failure and the current context form the observable state.
    p.append(rect(725, 280, 330, 105, WHITE, RULE, 2))
    p.append(text(890, 324, "Public failure", 33, "middle", 500))
    p.append(text(890, 361, "error · call · retry budget", 27, "middle", fill=MUTED))
    p.append(arrow(890, 200, 890, 268, MUTED, 3))
    p.append(rect(405, 280, 260, 105, pale_blue, BLUE, 3))
    p.append(text(535, 325, "Observable state", 31, "middle", 500, BLUE))
    p.append(text(535, 361, "sₜ", 34, "middle", 500, BLUE))
    p.append(arrow(713, 332, 677, 332, BLUE, 3))

    # Failure memories and observable state meet only inside the proposed selector.
    p.append(rect(45, 280, 300, 105, WHITE, RULE, 2))
    p.append(text(195, 325, "Failure-memory bank", 31, "middle", 500))
    p.append(text(195, 361, "fixed before selection", 27, "middle", fill=MUTED))

    p.append(rect(1135, 105, 470, 280, "#FCFDFE", BLUE, 3))
    p.append(text(1370, 153, "Failure-memory selector", 35, "middle", 500, BLUE))
    p.append(text(1370, 190, "observable evidence only", 28, "middle", fill=MUTED))
    p.append(line(1175, 214, 1565, 214, GRID, 2))
    p.append(text(1370, 260, "retrieve  →  evaluate  →  gate", 32, "middle", 500))
    p.append(rect(1210, 302, 320, 54, pale_blue, GRID, 1))
    p.append(text(1370, 338, "c*   ·   c₁   ·   abstain", 30, "middle", 500, BLUE))

    p.append(line(345, 332, 370, 332, MUTED, 3))
    p.append(line(370, 332, 370, 465, MUTED, 3))
    p.append(line(370, 465, 1075, 465, MUTED, 3))
    p.append(line(1075, 465, 1075, 335, MUTED, 3))
    p.append(arrow(1075, 335, 1122, 335, MUTED, 3))
    p.append(text(720, 452, "retrieved candidates", 27, "middle", fill=MUTED))
    p.append(line(665, 332, 690, 332, BLUE, 3))
    p.append(line(690, 332, 690, 415, BLUE, 3))
    p.append(line(690, 415, 1095, 415, BLUE, 3))
    p.append(line(1095, 415, 1095, 255, BLUE, 3))
    p.append(arrow(1095, 255, 1122, 255, BLUE, 3))
    p.append(text(885, 402, "public evidence", 27, "middle", fill=BLUE))

    # Exactly one recovery decision; no rollout is represented.
    p.append(arrow(1605, 245, 1685, 245, BLUE, 3))
    p.append(rect(1698, 105, 355, 280, pale_blue, BLUE, 3))
    p.append(text(1876, 163, "One-step recovery", 35, "middle", 500, BLUE))
    p.append(line(1735, 188, 2016, 188, GRID, 2))
    p.append(text(1876, 241, "memory-conditioned", 30, "middle"))
    p.append(text(1876, 282, "tool / action", 30, "middle", 500))
    p.append(text(1876, 342, "no rollout · no multi-step claim", 26, "middle", fill=MUTED))

    p.append(rect(45, 500, 2008, 80, pale_gray, RULE, 2))
    p.append(rect(45, 500, 10, 80, MUTED, MUTED, 0))
    p.append(text(80, 549,
                  "Unavailable: scenario ID · hidden fault plan · gold action · evaluator outcome · prior model outcomes",
                  29, fill=MUTED))
    result = save("system_overview_formal", h, p,
                  "System overview for observable-evidence one-step recovery")
    FONT = previous_font
    return result


def selector_detail_figure():
    global FONT
    previous_font = FONT
    FONT = METHOD_FONT
    h = 720
    p: list[str] = []
    pale_blue = "#F2F6FA"
    pale_gray = "#F7F8F9"

    p.append(text(45, 58, "FIXED INPUTS", 30, weight=500, fill=MUTED))
    p.append(text(490, 58, "DETERMINISTIC SELECTOR", 30, weight=500, fill=BLUE))
    p.append(text(1775, 58, "OUTPUT", 30, weight=500, fill=MUTED))

    # Fixed candidate pool and observable state are the only two selector inputs.
    p.append(rect(45, 105, 340, 180, WHITE, RULE, 2))
    p.append(text(215, 151, "Failure-memory bank", 32, "middle", 500))
    p.append(arrow(215, 171, 215, 210, MUTED, 3))
    p.append(text(240, 199, "TF-IDF", 25, fill=MUTED))
    p.append(rect(90, 218, 250, 48, pale_blue, BLUE, 2))
    p.append(text(215, 251, "C = Top-10", 29, "middle", 500, BLUE))

    p.append(rect(45, 390, 340, 125, pale_blue, BLUE, 3))
    p.append(text(215, 438, "Observable state  sₜ", 32, "middle", 500, BLUE))
    p.append(text(215, 474, "task · call · error", 25, "middle", fill=MUTED))
    p.append(text(215, 502, "history · budget", 25, "middle", fill=MUTED))

    # Enlarged internal stages avoid dense explanatory prose.
    stages = [
        (490, 330, "1  POLICY CARD"),
        (855, 420, "2  EVIDENCE  eᵢ"),
        (1310, 350, "3  CONSERVATIVE GATE"),
    ]
    for x, w, label in stages:
        p.append(rect(x, 105, w, 410, WHITE, BLUE if x == 490 else RULE, 2))
        p.append(text(x + 24, 151, label, 30, weight=500, fill=BLUE))
        p.append(line(x + 24, 171, x + w - 24, 171, GRID, 2))

    p.append(text(655, 223, "P(cᵢ)", 42, "middle", 500, BLUE))
    policy_rows = ["trigger + conditions", "operation + target", "continue / stop", "source + qᵢ"]
    for j, value in enumerate(policy_rows):
        yy = 255 + j * 58
        p.append(rect(535, yy, 240, 44, pale_gray, GRID, 1))
        p.append(text(655, yy + 30, value, 28, "middle", fill=INK if j < 3 else MUTED))

    p.append(text(1065, 223, "Lexicographic checks", 31, "middle", 500))
    evidence_rows = [
        ("nᵢ", "contradictions"), ("sᵢ, pᵢ", "support"),
        ("rᵢ, tᵢ", "alignment"), ("kᵢ, qᵢ", "tool fit"),
    ]
    for j, (symbol, label) in enumerate(evidence_rows):
        yy = 255 + j * 58
        p.append(rect(900, yy, 330, 44, pale_gray, GRID, 1))
        p.append(text(922, yy + 30, symbol, 29, weight=500, fill=BLUE))
        p.append(text(1045, yy + 30, label, 28))

    gate_rows = [("n* = 0", "no conflict"), ("s* = 2", "compatible"), ("e* ≻ e₁", "decisive")]
    for j, (formula, label) in enumerate(gate_rows):
        yy = 220 + j * 82
        p.append(rect(1360, yy, 250, 64, pale_blue, GRID, 1))
        p.append(text(1485, yy + 28, formula, 29, "middle", 500, BLUE))
        p.append(text(1485, yy + 54, label, 23, "middle", fill=MUTED))
    p.append(text(1485, 480, "all 3  →  replace", 30, "middle", 500, BLUE))

    # Candidate and evidence streams join at their corresponding stages.
    p.append(arrow(385, 195, 477, 195, MUTED, 3))
    p.append(arrow(820, 310, 842, 310, MUTED, 3))
    p.append(arrow(1275, 310, 1297, 310, MUTED, 3))
    p.append(line(385, 452, 420, 452, BLUE, 3))
    p.append(line(420, 452, 420, 550, BLUE, 3))
    p.append(line(420, 550, 1065, 550, BLUE, 3))
    p.append(arrow(1065, 550, 1065, 515, BLUE, 3))
    p.append(text(735, 538, "observable evidence", 26, "middle", fill=BLUE))

    p.append(arrow(1660, 310, 1755, 310, BLUE, 3))
    p.append(rect(1775, 145, 280, 330, pale_gray, RULE, 2))
    p.append(text(1915, 195, "Selector output", 32, "middle", 500))
    outputs = [(260, "c*", "alternative"), (330, "c₁", "retain Rank-1"), (400, "∅", "fallback to c₁")]
    for yy, symbol, label in outputs:
        p.append(text(1815, yy, symbol, 32, weight=500, fill=BLUE))
        p.append(text(1870, yy, label, 28))

    p.append(rect(45, 585, 2010, 90, pale_gray, RULE, 2))
    p.append(rect(45, 585, 10, 90, MUTED, MUTED, 0))
    p.append(text(80, 622, "EXCLUDED FROM EVERY CHECK", 27, weight=500, fill=MUTED))
    p.append(text(80, 657,
                  "scenario ID · hidden fault plan · gold action · evaluator outcome · prior model outcomes",
                  28, fill=INK))
    result = save("selector_detail_formal", h, p,
                  "Detailed observable-evidence conservative selector")
    FONT = previous_font
    return result


def scale(value, left, right, xmin, xmax):
    return left + (value - xmin) / (xmax - xmin) * (right - left)


def whisker(parts, y, effect, low, high, model, left, right, xmin, xmax,
            value_label=True):
    color = DATA_BLUE if model == "qwen3_8b" else DATA_ORANGE
    x1, x2, xp = [scale(v, left, right, xmin, xmax) for v in (low, high, effect)]
    parts.extend([
        line(x1, y, x2, y, color, 4),
        line(x1, y - 10, x1, y + 10, color, 3),
        line(x2, y - 10, x2, y + 10, color, 3),
    ])
    parts.append(circle(xp, y, 11, color) if model == "qwen3_8b" else diamond(xp, y, 13, color))
    if value_label:
        parts.append(text(x2 + 17, y + 8, f"{effect:.2f}", 21, fill=color, weight=500))


def axes(parts, top, bottom, left, right, xmin, xmax, ticks):
    for tick in ticks:
        x = scale(tick, left, right, xmin, xmax)
        parts.append(line(x, top, x, bottom, RULE if tick == 0 else GRID, 3 if tick == 0 else 2))
        parts.append(text(x, bottom + 39, str(tick), 28, "middle", fill=MUTED))


def model_legend(parts, x, y):
    parts.append(circle(x, y, 10, DATA_BLUE))
    parts.append(text(x + 22, y + 8, "Qwen3-8B", 22))
    parts.append(diamond(x + 190, y, 12, DATA_ORANGE))
    parts.append(text(x + 212, y + 8, "Mistral-7B", 22))


def main_effects_figure(rows: list[core.ForestRow]):
    h = 1040
    p: list[str] = []
    left, right = 650, 1465
    xmin, xmax = -2.0, 15.0

    # Panel A: primary population. A light band keeps the primary comparison visible
    # without relying on significance stars or decorative callouts.
    p.append(rect(45, 145, 2010, 122, "#F7FAFD", "none", 0))
    p.append(text(55, 55, "(a)", 30, weight=500))
    p.append(text(115, 55, "Changed-target union (n = 403)", 32, weight=500))
    p.append(text(55, 112, "Baseline", 31, weight=500, fill=MUTED))
    p.append(text(315, 112, "Model", 31, weight=500, fill=MUTED))
    p.append(text((left + right) / 2, 112, "Paired risk difference (pp)", 31,
                  "middle", 500, fill=MUTED))
    p.append(text(1725, 112, "Estimate [95% CI]", 31, "middle", 500, fill=MUTED))
    p.append(text(1990, 112, "+ / -", 31, "middle", 500, fill=MUTED))
    p.append(line(45, 128, 2055, 128, RULE, 2))
    axes(p, 140, 620, left, right, xmin, xmax, [-2, 0, 5, 10, 15])

    groups = [
        ("tfidf", "TF-IDF", "primary"),
        ("dense", "Dense retrieval", "key secondary"),
        ("llm_judge", "Fixed LLM judge", "key secondary"),
    ]
    for gi, (baseline, label, status) in enumerate(groups):
        base_y = 175 + gi * 150
        p.append(text(55, base_y + 16, label, 32, weight=500))
        p.append(text(55, base_y + 53, status, 28, fill=MUTED, style="italic"))
        for offset, model, model_name in [
            (0, "qwen3_8b", "Qwen3-8B"),
            (60, "mistral_7b_instruct_v0_3", "Mistral-7B"),
        ]:
            row = next(r for r in rows if r.population == "changed_target_union"
                       and r.baseline == baseline and r.model == model)
            y = base_y + offset
            whisker(p, y, row.effect * 100, row.low * 100, row.high * 100,
                    model, left, right, xmin, xmax, value_label=False)
            model_color = DATA_BLUE if model == "qwen3_8b" else DATA_ORANGE
            p.append(text(315, y + 10, model_name, 31, fill=model_color, weight=500))
            p.append(text(1725, y + 9,
                          f"{row.effect * 100:.2f} [{row.low * 100:.2f}, {row.high * 100:.2f}]",
                          30, "middle"))
            p.append(text(1990, y + 10, f"{row.positive} / {row.negative}", 30, "middle"))
        if gi < 2:
            p.append(line(45, base_y + 105, 2055, base_y + 105, GRID, 2))

    # Panel B: all-valid sensitivity, kept on the identical effect scale.
    p.append(line(45, 700, 2055, 700, RULE, 2))
    p.append(text(55, 755, "(b)", 30, weight=500))
    p.append(text(115, 755, "All-valid sensitivity (n = 541; vs TF-IDF)", 32, weight=500))
    p.append(text(315, 805, "Model", 31, weight=500, fill=MUTED))
    p.append(text(1725, 805, "Estimate [95% CI]", 31, "middle", 500, fill=MUTED))
    p.append(text(1990, 805, "+ / -", 31, "middle", 500, fill=MUTED))
    axes(p, 820, 940, left, right, xmin, xmax, [-2, 0, 5, 10, 15])
    for offset, model, model_name in [
        (0, "qwen3_8b", "Qwen3-8B"),
        (65, "mistral_7b_instruct_v0_3", "Mistral-7B"),
    ]:
        row = next(r for r in rows if r.population == "all_valid_targets" and r.model == model)
        y = 850 + offset
        whisker(p, y, row.effect * 100, row.low * 100, row.high * 100,
                model, left, right, xmin, xmax, value_label=False)
        model_color = DATA_BLUE if model == "qwen3_8b" else DATA_ORANGE
        p.append(text(315, y + 10, model_name, 31, fill=model_color, weight=500))
        p.append(text(1725, y + 9,
                      f"{row.effect * 100:.2f} [{row.low * 100:.2f}, {row.high * 100:.2f}]",
                      30, "middle"))
        p.append(text(1990, y + 10, f"{row.positive} / {row.negative}", 30, "middle"))

    p.append(text((left + right) / 2, 1015,
                  "Paired risk difference (percentage points); right favors the proposed selector",
                  31, "middle", 500))

    return save("main_effects_formal", h, p, "Paired Recovery Validity effects with 95 percent intervals")


def heterogeneity_figure(strata: list[dict]):
    h = 790
    p: list[str] = []

    p.append(text(55, 58, "Failure-stratum effects vs TF-IDF", 36, weight=500))
    p.append(text(55, 102, "Exploratory; changed-target union", 29, fill=MUTED, style="italic"))
    p.append(text(55, 158, "Failure stratum", 31, weight=500, fill=MUTED))
    p.append(text(385, 158, "Model", 31, weight=500, fill=MUTED))
    p.append(text(1075, 158, "Paired risk difference (pp)", 31, "middle", 500, fill=MUTED))
    p.append(text(1750, 158, "Estimate [95% CI]", 30, "middle", 500, fill=MUTED))
    p.append(text(2010, 158, "+ / -", 30, "middle", 500, fill=MUTED))
    p.append(line(45, 176, 2055, 176, RULE, 2))

    left, right = 690, 1460
    xmin, xmax = -5.0, 22.0
    axes(p, 188, 650, left, right, xmin, xmax, [-5, 0, 5, 10, 15, 20])
    labels = [
        ("argument_omission", "Argument omission", 152),
        ("transient_authorization", "Transient authorization", 146),
        ("timeout", "Timeout", 105),
    ]
    for gi, (key, label, n) in enumerate(labels):
        base_y = 225 + gi * 145
        p.append(text(55, base_y + 12, label, 31, weight=500))
        p.append(text(55, base_y + 50, f"n = {n}", 28, fill=MUTED))
        for offset, model, model_name in [
            (0, "qwen3_8b", "Qwen3-8B"),
            (60, "mistral_7b_instruct_v0_3", "Mistral-7B"),
        ]:
            row = next(r for r in strata if r["stratum"] == key and r["model"] == model)
            y = base_y + offset
            whisker(p, y, row["effect_pp"], row["ci_lower_pp"], row["ci_upper_pp"],
                    model, left, right, xmin, xmax, value_label=False)
            model_color = DATA_BLUE if model == "qwen3_8b" else DATA_ORANGE
            p.append(text(385, y + 10, model_name, 31, fill=model_color, weight=500))
            p.append(text(1750, y + 10,
                          f'{row["effect_pp"]:.2f} [{row["ci_lower_pp"]:.2f}, {row["ci_upper_pp"]:.2f}]',
                          30, "middle"))
            p.append(text(2010, y + 10,
                          f'{row["positive_discordant"]} / {row["negative_discordant"]}',
                          30, "middle"))
        if gi < 2:
            p.append(line(45, base_y + 105, 2055, base_y + 105, GRID, 2))
    p.append(text((left + right) / 2, 735,
                  "Paired risk difference (percentage points); right favors the proposed selector",
                  31, "middle", 500))
    return save("heterogeneity_formal", h, p,
                "Exploratory failure-stratum effects relative to TF-IDF")


def transfer_figure(transfers: list[dict]):
    h = 700
    p: list[str] = []

    p.append(text(55, 58, "Positive and negative transfer relative to No Memory", 36, weight=500))
    p.append(text(55, 102, "Descriptive; n = 403 paired targets per model", 29, fill=MUTED, style="italic"))

    bx0 = 1060
    max_share = 30.0
    extent = 600
    plot_top, plot_bottom = 155, 520
    p.append(line(bx0, plot_top, bx0, plot_bottom, INK, 3))
    for tick in [-30, -20, -10, 0, 10, 20, 30]:
        x = bx0 + tick / max_share * extent
        if tick != 0:
            p.append(line(x, plot_top, x, plot_bottom, GRID, 2))
        p.append(line(x, plot_bottom, x, plot_bottom + 12, INK, 2))
        p.append(text(x, plot_bottom + 48, str(abs(tick)), 29, "middle", fill=MUTED))
    p.append(text(bx0 - 330, 615, "Negative transfer (%)", 31, "middle", 500, fill=TRANSFER_NEG))
    p.append(text(bx0 + 330, 615, "Positive transfer (%)", 31, "middle", 500, fill=TRANSFER_POS))

    defs = (f'<defs><pattern id="neg-hatch" width="10" height="10" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate(45)"><rect width="10" height="10" fill="#FFFFFF"/>'
            f'<line x1="0" y1="0" x2="0" y2="10" stroke="{TRANSFER_NEG}" stroke-width="4"/>'
            f'</pattern></defs>')
    model_names = {"qwen3_8b": "Qwen3-8B", "mistral_7b_instruct_v0_3": "Mistral-7B"}
    for i, model in enumerate(["qwen3_8b", "mistral_7b_instruct_v0_3"]):
        row = next(r for r in transfers if r["model"] == model)
        y = 235 + i * 205
        p.append(text(55, y + 10, model_names[model], 34, weight=500))
        nw = row["negative_share_pp"] / max_share * extent
        pw = row["positive_share_pp"] / max_share * extent
        p.append(rect(bx0 - nw, y - 31, nw, 62, "url(#neg-hatch)", TRANSFER_NEG, 2))
        p.append(rect(bx0, y - 31, pw, 62, TRANSFER_POS, TRANSFER_POS, 1))
        p.append(text(bx0 - nw - 18, y + 11, str(row["negative_transfer"]), 31, "end", weight=500))
        p.append(text(bx0 + pw + 18, y + 11, str(row["positive_transfer"]), 31, weight=500))
        sign = "+" if row["net_effect_pp"] >= 0 else "-"
        net_color = TRANSFER_POS if row["net_effect_pp"] >= 0 else TRANSFER_NEG
        p.append(text(1800, y + 11, f'Net RD: {sign}{abs(row["net_effect_pp"]):.2f} pp',
                      32, weight=500, fill=net_color))

    p.append(text(1060, 675,
                  "Bar length = share of paired targets; labels = discordant counts",
                  29, "middle", fill=MUTED))
    return save("transfer_formal", h, p,
                "Descriptive positive and negative transfer relative to no memory", defs)


def main():
    identities = core.verify_sources()
    e2 = core.load_json(core.E2E3)
    e4 = core.load_json(core.E4)
    overall = core.forest_rows(e2, identities)
    strata = core.heterogeneity_rows(e2, identities)
    transfers = core.transfer_rows(e4, identities)
    outputs = [
        system_overview_figure(), selector_detail_figure(), main_effects_figure(overall),
        heterogeneity_figure(strata), transfer_figure(transfers),
    ]
    manifest = {
        "generator": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
        "design": "submission-style ACL/EMNLP/IEEE vector figures",
        "sources": identities,
        "outputs": [
            {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(path)}
            for group in outputs for path in group
        ],
    }
    manifest_path = OUT / "formal_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
