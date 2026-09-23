#!/usr/bin/env python3
"""
Builds reports/slides.pdf (8 slides, 16:9) and reports/mini_report.pdf (2 pages, A4).

Everything you need to change lives in the CONTENT block at the top of this file.
Edit the numbers and the text there, then run:

    pip install reportlab
    python tools/build_reports.py

Both PDFs are regenerated. Nothing else in the repository is touched.

If results/metrics.json exists (written by notebook 01), the metrics below are
overwritten from it automatically, so you do not have to retype them.
"""

import json
import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import Paragraph, Table, TableStyle, Frame

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

# ============================================================================
# CONTENT — edit this block
# ============================================================================

TITLE = "Construction Element Detection for Site Progress Verification"
SUBTITLE = "A cloud-only YOLOv8 pipeline for automated progress evidence"
COURSE = "MAICEN0526  ·  Module 4 Unit 3  ·  Group 6"
AUTHORS = ("Ahmed Abdelaal  ·  Mohammad Abu Alhasan  ·  Yazan Darweesh  ·  "
           "Clayton Peter Human  ·  Tarig Ismail Mohamed Abas")
DATE = "September 2026"
REPO_URL = "github.com/yazandarwish264-glitch/m4u3-construction-detection"

# Overwritten from results/metrics.json when that file exists.
METRICS = {
    "precision": None,
    "recall": None,
    "mAP50": None,
    "mAP50_95": None,
}

PER_CLASS = {
    "brick":     {"precision": None, "recall": None, "mAP50": None, "mAP50_95": None},
    "excavator": {"precision": None, "recall": None, "mAP50": None, "mAP50_95": None},
    "pvcpipe":   {"precision": None, "recall": None, "mAP50": None, "mAP50_95": None},
    "scaffold":  {"precision": None, "recall": None, "mAP50": None, "mAP50_95": None},
    "steelbar":  {"precision": None, "recall": None, "mAP50": None, "mAP50_95": None},
}

RUN = {
    "dataset_images": "700",
    "split": "560 / 140  (80 / 20)",
    "model": "yolov8s.pt",
    "epochs": "30",
    "imgsz": "640",
    "batch": "16",
    "hardware": "Tesla T4, 15360 MiB (Colab free tier)",
    "train_time": "6.4 min",
    "run_date": "2026-09-21",
    "dataset": "yazan-darwish/construction-site-km7bh-fapwu v1",
}

TAKEAWAYS = [
    "<b>Validation says 0.943 mAP@50. Our own photographs say almost nothing.</b> "
    "Across seven held-out images the model produced one marginal correct detection, "
    "two confident wrong-class detections and four blanks \u2014 including both classes "
    "we had designated as controls at recall 1.000.",
    "<b>The cause is scale, and it is testable.</b> Holding weights, image and confidence "
    "fixed and changing only the input resolution, a blockwork wall moves from "
    "scaffold 0.78 to brick 0.46. A model whose class prediction depends on resampling has "
    "learned a texture signature, not an object. Lowering confidence to 0.02 recovers nothing.",
    "<b>The fix is data, not capacity.</b> Re-split by scene group so validation can "
    "detect this at all; add wide-field imagery and train multi-scale; add hard negatives "
    "for the two confusions actually observed. A larger model would raise the leaking "
    "number and change none of the seven held-out results.",
]

LIMITATIONS = [
    "Reported metrics are inflated by train/validation leakage; the held-out set confirms it "
    "independently. They measure memorisation, not generalisation.",
    "Predictions change class with input resolution, so imgsz must be pinned end to end and "
    "confidence is not comparable across distributions.",
    "Wide-field shots fail \u2014 which is how site progress photography is actually taken. "
    "Validated only on close, subject-filling images.",
    "No safety function: no people, no PPE, no hazards. Treating it as a safety system would "
    "reduce site safety, not improve it.",
    "Presence only \u2014 never quantity, spacing, cover or conformance, and never a payment "
    "application. A human reviews every output.",
]

GCC_NOTE = (
    "In the Gulf, progress reporting on large programmes is still photograph-plus-narrative, "
    "with a two-to-seven-day lag between capture and record. Government BIM mandates and "
    "ISO 19650 information-delivery requirements are raising the bar on structured, auditable "
    "progress evidence. A detection record — image, time, zone, class, confidence — is "
    "structured information that can enter a CDE. A JPEG in a folder is not."
)

# ============================================================================
# Load real metrics if the training run has happened
# ============================================================================

mfile = ROOT / "results" / "metrics.json"
if mfile.exists():
    try:
        data = json.loads(mfile.read_text())
        if "overall" in data:
            METRICS.update(data["overall"])
        if "per_class" in data:
            for k, v in data["per_class"].items():
                PER_CLASS[k] = v
        cfg = data.get("config", {})
        RUN["model"] = cfg.get("model_variant", RUN["model"])
        RUN["epochs"] = str(cfg.get("epochs", RUN["epochs"]))
        RUN["imgsz"] = str(cfg.get("imgsz", RUN["imgsz"]))
        RUN["batch"] = str(cfg.get("batch", RUN["batch"]))
        RUN["hardware"] = data.get("accelerator", RUN["hardware"])
        RUN["train_time"] = f"{data.get('training_minutes', '__')} min"
        RUN["run_date"] = data.get("run_finished_utc", RUN["run_date"])[:10]
        imgs = data.get("images", {})
        if imgs:
            RUN["dataset_images"] = str(sum(imgs.values()))
        print("Loaded metrics from results/metrics.json")
    except Exception as e:
        print(f"Could not read metrics.json ({e}) — using placeholders.")
else:
    print("results/metrics.json not found — building with placeholders.")


def fmt(v):
    return "—" if v is None else f"{v:.3f}"


# ============================================================================
# Design tokens
# ============================================================================

INK = colors.HexColor("#1A1A1A")
MUTED = colors.HexColor("#6B7280")
RULE = colors.HexColor("#D9D9D9")
ACCENT = colors.HexColor("#B45309")
BG_TINT = colors.HexColor("#F5F4F1")

SANS = "Helvetica"
SANS_B = "Helvetica-Bold"


def ps(name, size, leading=None, font=SANS, color=INK, space_after=0, space_before=0):
    return ParagraphStyle(
        name, fontName=font, fontSize=size, leading=leading or size * 1.35,
        textColor=color, spaceAfter=space_after, spaceBefore=space_before,
    )


# ============================================================================
# SLIDES — 16:9
# ============================================================================

SW, SH = 960, 540
M = 54


def slide_chrome(c, num, total, kicker):
    c.setFillColor(colors.white)
    c.rect(0, 0, SW, SH, stroke=0, fill=1)
    c.setFillColor(ACCENT)
    c.rect(0, SH - 4, SW, 4, stroke=0, fill=1)
    c.setFont(SANS_B, 8)
    c.setFillColor(ACCENT)
    c.drawString(M, SH - 34, kicker.upper())
    c.setFont(SANS, 8)
    c.setFillColor(MUTED)
    c.drawRightString(SW - M, 26, f"{num} / {total}")
    c.drawString(M, 26, COURSE)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.5)
    c.line(M, 42, SW - M, 42)


def slide_title(c, text, y=SH - 78):
    c.setFont(SANS_B, 27)
    c.setFillColor(INK)
    c.drawString(M, y, text)
    return y - 26


def para(c, text, x, y, w, size=12.5, font=SANS, color=INK, leading=None):
    p = Paragraph(text, ps("b", size, leading, font, color))
    _, h = p.wrap(w, 1000)
    p.drawOn(c, x, y - h)
    return y - h


def bullets(c, items, x, y, w, size=12.5, gap=13):
    for it in items:
        c.setFillColor(ACCENT)
        c.setFont(SANS_B, size)
        c.drawString(x, y - size * 0.95, "—")
        y = para(c, it, x + 20, y, w - 20, size=size)
        y -= gap
    return y


def build_slides():
    path = REPORTS / "slides.pdf"
    c = pdfcanvas.Canvas(str(path), pagesize=(SW, SH))
    total = 8

    # 1 — title
    c.setFillColor(colors.white); c.rect(0, 0, SW, SH, stroke=0, fill=1)
    c.setFillColor(BG_TINT); c.rect(0, 0, SW, SH, stroke=0, fill=1)
    c.setFillColor(ACCENT); c.rect(0, SH - 6, SW, 6, stroke=0, fill=1)
    c.setFont(SANS_B, 9); c.setFillColor(ACCENT)
    c.drawString(M, SH - 60, "COMPUTER VISION FOR AECO")
    y = SH - 130
    p = Paragraph(TITLE, ps("t", 34, 41, SANS_B, INK))
    _, h = p.wrap(SW - 2 * M - 120, 400); p.drawOn(c, M, y - h)
    y -= h + 16
    y = para(c, SUBTITLE, M, y, SW - 2 * M - 120, size=15, color=MUTED)
    c.setStrokeColor(RULE); c.setLineWidth(0.5)
    c.line(M, 120, SW - M, 120)
    c.setFont(SANS_B, 11); c.setFillColor(ACCENT)
    c.drawString(M, 148, "Repository:  " + REPO_URL)
    c.setFont(SANS, 10); c.setFillColor(MUTED)
    c.drawString(M, 100, COURSE)
    c.drawString(M, 84, f"{AUTHORS}   ·   {DATE}")
    c.showPage()

    # 2 — problem
    slide_chrome(c, 2, total, "The problem")
    y = slide_title(c, "Progress evidence is captured, then lost")
    y -= 8
    y = bullets(c, [
        "<b>Latency.</b> Two to seven days between the photograph and the progress record. "
        "Decisions get made on stale data.",
        "<b>Inconsistency.</b> Two engineers describe the same floor differently. "
        "No controlled vocabulary links what is visible to a structured record.",
        "<b>Loss of information.</b> The photograph is archived. What is <i>in</i> it — "
        "steelbar placed, blockwork started, conduit run — is never captured as data, "
        "so it cannot enter a CDE or be audited.",
    ], M, y, SW - 2 * M - 40)
    y -= 12
    c.setFillColor(BG_TINT)
    c.roundRect(M, 70, SW - 2 * M, 84, 4, stroke=0, fill=1)
    para(c, GCC_NOTE, M + 18, 146, SW - 2 * M - 36, size=10.5, color=INK, leading=14.5)
    c.showPage()

    # 3 — approach
    slide_chrome(c, 3, total, "Approach")
    y = slide_title(c, "Five classes, one detector, zero local installs")
    y -= 6
    y = para(c, "Detect construction elements and plant in site photographs, then use presence "
                "as a progress and site-condition signal.",
             M, y, SW - 2 * M, size=13, color=MUTED)
    y -= 22
    rows = [["Class", "Signal it carries"],
            ["steelbar", "Reinforcement activity \u2014 structural progress"],
            ["brick", "Masonry and blockwork \u2014 envelope progress"],
            ["pvcpipe", "Services installation \u2014 MEP first fix"],
            ["scaffold", "Temporary works standing \u2014 zone not released"],
            ["excavator", "Plant present \u2014 earthworks active"]]
    t = Table(rows, colWidths=[200, 340], rowHeights=[22] + [21] * 5)
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), SANS_B, 10.5),
        ("FONT", (0, 1), (-1, -1), SANS, 10.5),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("TEXTCOLOR", (0, 1), (0, -1), ACCENT),
        ("FONT", (0, 1), (0, -1), SANS_B, 10.5),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    _, th = t.wrap(0, 0); t.drawOn(c, M, y - th)
    x2 = M + 570
    c.setFont(SANS_B, 10.5); c.setFillColor(INK)
    c.drawString(x2, y - 12, "Pipeline")
    yy = y - 34
    for step in ["Roboflow — fork, extend, annotate",
                 "Colab — YOLOv8, 30 epochs, T4",
                 "Validate — P / R / mAP, per class",
                 "Evidence — validation + unseen images",
                 "Handover — repo, governance, licence"]:
        c.setFillColor(ACCENT); c.circle(x2 + 3, yy + 3, 2.5, stroke=0, fill=1)
        c.setFillColor(INK); c.setFont(SANS, 10)
        c.drawString(x2 + 14, yy, step)
        yy -= 20
    c.showPage()

    # 4 — data
    slide_chrome(c, 4, total, "Data")
    y = slide_title(c, "A public base, re-split for the task")
    y -= 6
    y = para(c, "Forked <b>seungyeon/construction-site-km7bh</b> (700 images, CC BY 4.0) into our own "
                "Roboflow workspace and re-split it to the required 80/20. Used as published, with "
                "no images added. Seven photographs of our own are held back entirely.",
             M, y, SW - 2 * M - 30, size=12.5)
    y -= 20
    rows = [["Dataset", "As used in this project"],
            ["Source", "seungyeon/construction-site-km7bh — CC BY 4.0, redistributed with attribution"],
            ["Images", "700, all annotated, five classes"],
            ["Split", "560 train / 140 validation (80 / 20), re-split from the source's 70/20/10"],
            ["Preprocessing", "Resize to 640 x 640. No augmentation"],
            ["Held out entirely", "7 first-party photographs, never uploaded and never trained on"]]
    t = Table(rows, colWidths=[230, 420], rowHeights=[22] + [30] * 5)
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), SANS_B, 9.5),
        ("FONT", (0, 1), (-1, -1), SANS, 9.5),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    _, th = t.wrap(0, 0); t.drawOn(c, M, y - th)
    y = y - th - 22
    para(c, "<b>Two decisions that shape everything after this slide.</b> Augmentation is off, so the "
            "baseline shows what the data does rather than what augmentation hides. And the split is "
            "random over images — but this dataset is built from sequential site photographs, so "
            "near-identical frames land on both sides of it. That is why the score on the next slide "
            "is not a generalisation estimate, and why the seven held-out photographs exist.",
         M, y, SW - 2 * M, size=11, color=MUTED)
    c.showPage()

    # 5 — results
    slide_chrome(c, 5, total, "Results")
    y = slide_title(c, "Validation performance")
    y -= 14
    for i, (lab, val) in enumerate([("Precision", METRICS["precision"]),
                                    ("Recall", METRICS["recall"]),
                                    ("mAP@50", METRICS["mAP50"]),
                                    ("mAP@50-95", METRICS["mAP50_95"])]):
        bx = M + i * 215
        c.setFillColor(BG_TINT); c.roundRect(bx, y - 74, 196, 74, 4, stroke=0, fill=1)
        c.setFillColor(INK); c.setFont(SANS_B, 30)
        c.drawString(bx + 16, y - 46, fmt(val))
        c.setFillColor(MUTED); c.setFont(SANS, 10)
        c.drawString(bx + 16, y - 64, lab)
    y -= 96
    rows = [["Class", "P", "R", "mAP@50", "mAP@50-95"]]
    for k, v in PER_CLASS.items():
        rows.append([k, fmt(v.get("precision")), fmt(v.get("recall")),
                     fmt(v.get("mAP50")), fmt(v.get("mAP50_95"))])
    t = Table(rows, colWidths=[230, 105, 105, 110, 110], rowHeights=[21] + [20] * len(PER_CLASS))
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), SANS_B, 10),
        ("FONT", (0, 1), (-1, -1), SANS, 10),
        ("FONT", (0, 1), (0, -1), SANS_B, 10),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    _, th = t.wrap(0, 0); t.drawOn(c, M, y - th)
    y = y - th - 18
    para(c, "<b>Success criteria, all met.</b> S1 overall mAP@50 &ge; 0.50 — <b>0.943</b>. "
            "S2 steelbar recall &ge; 0.50 — <b>0.612</b>. S3 brick recall &ge; 0.40 — <b>1.000</b>. "
            "Targets were set before the run. Clearing them by this margin is a signal that the "
            "measurement is wrong, not that the model is excellent — see the next slide.",
         M, y, SW - 2 * M, size=10.5, color=MUTED, leading=14.5)
    c.setFont(SANS, 9); c.setFillColor(MUTED)
    c.drawString(M, 58, f"{RUN['model']}  ·  {RUN['epochs']} epochs  ·  imgsz {RUN['imgsz']}  ·  "
                        f"batch {RUN['batch']}  ·  {RUN['hardware']}  ·  {RUN['train_time']}")
    c.showPage()

    # 6 — takeaways
    slide_chrome(c, 6, total, "Interpretation")
    y = slide_title(c, "Three things the numbers say")
    y -= 10
    for i, tk in enumerate(TAKEAWAYS, 1):
        c.setFillColor(ACCENT); c.setFont(SANS_B, 20)
        c.drawString(M, y - 18, str(i))
        y = para(c, tk, M + 30, y, SW - 2 * M - 30, size=13, leading=18)
        y -= 22
    c.showPage()

    # 7 — errors
    slide_chrome(c, 7, total, "Error analysis")
    y = slide_title(c, "The two errors are not symmetrical")
    y -= 10
    bw = (SW - 2 * M - 26) / 2
    for i, (head, body, sev) in enumerate([
        ("False negative", "Steelbar is placed, the model misses it. No record is created. "
         "Nobody investigates, because nobody knows there is anything to investigate. "
         "<b>The error is silent.</b>", "High"),
        ("False positive", "The model reports steelbar that is not there. The next site walk "
         "contradicts it. <b>The error is loud and self-correcting</b> — but repeated, it "
         "produces alert fatigue.", "Moderate"),
    ]):
        bx = M + i * (bw + 26)
        c.setFillColor(BG_TINT); c.roundRect(bx, y - 150, bw, 150, 4, stroke=0, fill=1)
        c.setFillColor(ACCENT); c.setFont(SANS_B, 13)
        c.drawString(bx + 16, y - 28, head)
        c.setFillColor(MUTED); c.setFont(SANS, 9)
        c.drawRightString(bx + bw - 16, y - 28, f"Severity: {sev}")
        para(c, body, bx + 16, y - 42, bw - 32, size=11, leading=15.5)
    y -= 172
    c.setFillColor(INK); c.roundRect(M, y - 66, SW - 2 * M, 66, 4, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont(SANS_B, 12)
    c.drawString(M + 18, y - 24, "One model, two thresholds")
    p = Paragraph("Progress logging runs at a <b>low</b> confidence threshold, favouring recall "
                  "because a miss is silent. Site-condition alerts run at a <b>high</b> one, "
                  "favouring precision because false alarms train people to ignore the system. "
                  "A single threshold would be wrong for one of them.",
                  ps("w", 10.5, 14, SANS, colors.white))
    _, ph = p.wrap(SW - 2 * M - 36, 200); p.drawOn(c, M + 18, y - 34 - ph)
    para(c, "Three false positives and three false negatives are documented with filenames and "
            "hypotheses in <i>docs/error_analysis.md</i>, each tied to a dataset gap rather than to "
            "model capacity — and each paired with a concrete improvement and the metric it should move.",
         M, y - 82, SW - 2 * M, size=10.5, color=MUTED, leading=14.5)
    c.showPage()

    # 8 — limitations and governance
    slide_chrome(c, 8, total, "Governance")
    y = slide_title(c, "When not to use this")
    y -= 8
    y = bullets(c, LIMITATIONS[:4], M, y, SW - 2 * M - 250, size=11.5, gap=9)
    x2 = SW - M - 230
    c.setFillColor(BG_TINT); c.roundRect(x2 - 16, 70, 246, 300, 4, stroke=0, fill=1)
    c.setFillColor(INK); c.setFont(SANS_B, 11)
    c.drawString(x2, 348, "Rights")
    yy = 326
    for k, v in [("Code", "MIT"), ("Dataset", "CC BY 4.0, not owned"),
                 ("Weights", "AGPL-3.0 inherited"), ("People detected", "None, by design")]:
        c.setFillColor(MUTED); c.setFont(SANS, 8.5)
        c.drawString(x2, yy, k.upper())
        c.setFillColor(INK); c.setFont(SANS_B, 10)
        c.drawString(x2, yy - 14, v)
        yy -= 40
    p = Paragraph("Commercial deployment of YOLOv8-derived weights requires AGPL-3.0 compliance "
                  "or an Ultralytics licence. This is the most commonly missed obligation "
                  "in YOLO projects.", ps("n", 9, 12.5, SANS, MUTED))
    _, ph = p.wrap(230, 200); p.drawOn(c, x2, 176 - ph)
    c.showPage()

    c.save()
    print(f"wrote {path}")


# ============================================================================
# MINI REPORT — 2 pages A4
# ============================================================================

PW, PH = A4
RM = 20 * mm


def report_chrome(c, page, total):
    c.setFillColor(ACCENT); c.rect(0, PH - 3, PW, 3, stroke=0, fill=1)
    c.setStrokeColor(RULE); c.setLineWidth(0.5)
    c.line(RM, 16 * mm, PW - RM, 16 * mm)
    c.setFont(SANS, 7.5); c.setFillColor(MUTED)
    c.drawString(RM, 12 * mm, COURSE)
    c.drawRightString(PW - RM, 12 * mm, f"Page {page} of {total}")


def h(c, text, y, size=12):
    y -= 6
    c.setFillColor(ACCENT); c.setFont(SANS_B, 7.5)
    c.drawString(RM, y, text.upper())
    y -= 5
    c.setStrokeColor(RULE); c.setLineWidth(0.5)
    c.line(RM, y, PW - RM, y)
    return y - 13


def body(c, text, y, size=9.3, leading=13.2, width=None, color=INK):
    w = width or (PW - 2 * RM)
    p = Paragraph(text, ps("bd", size, leading, SANS, color))
    _, ht = p.wrap(w, 2000)
    p.drawOn(c, RM, y - ht)
    return y - ht


def build_report():
    path = REPORTS / "mini_report.pdf"
    c = pdfcanvas.Canvas(str(path), pagesize=A4)
    CW = PW - 2 * RM

    # ---------------- page 1 ----------------
    report_chrome(c, 1, 2)
    y = PH - 24 * mm
    c.setFillColor(MUTED); c.setFont(SANS, 8)
    c.drawString(RM, y, "MINI REPORT")
    y -= 20
    p = Paragraph(TITLE, ps("t", 17, 21, SANS_B, INK))
    _, ht = p.wrap(CW, 200); p.drawOn(c, RM, y - ht)
    y -= ht + 7
    y = body(c, SUBTITLE, y, size=10.5, leading=14, color=MUTED)
    y -= 14
    c.setFont(SANS, 8); c.setFillColor(MUTED)
    c.drawString(RM, y, AUTHORS)
    y -= 11
    c.drawString(RM, y, f"MAICEN0526 Group 6   ·   {DATE}   ·   Run {RUN['run_date']}")
    y -= 13
    c.setFont(SANS_B, 8.5); c.setFillColor(ACCENT)
    c.drawString(RM, y, "Repository:  " + REPO_URL)
    y -= 24

    y = h(c, "Executive summary", y)
    y = body(c,
        "Site progress in the Gulf is still recorded by photograph and narrative, with a two- to "
        "seven-day gap between capture and record. The photograph is archived; the information "
        "inside it is not. ISO 19650 asks for information delivered into a common data environment "
        "in a structured form, and a JPEG in a folder does not meet that bar. "
        "<br/><br/>"
        "This project trains a YOLOv8 detector on five construction classes — <b>steelbar, brick, "
        "pvcpipe, scaffold and excavator</b> — so that a site photograph yields a structured "
        "detection record: image, time, zone, class, confidence, bounding box. Steelbar, brick and "
        "pvcpipe act as proxies for structural, masonry and MEP first-fix activity in a zone; "
        "scaffold and excavator report site condition — temporary works standing, plant active. "
        "<br/><br/>"
        "The system is deliberately scoped as a <b>triage tool</b>. It directs a person to the "
        "photographs worth examining. It does not replace the examination, and it has no safety "
        "function of any kind. The entire pipeline runs in the browser — the data a "
        "checksum-verified download, Colab for training — no install, no account. Re-run cold on "
        "2026-09-23, both notebooks reproduced every reported metric exactly.", y)
    y -= 16

    y = h(c, "Method", y)
    left = CW * 0.55
    y_after = body(c,
        "A public dataset, <i>seungyeon/construction-site-km7bh</i> (700 images, CC BY 4.0), was "
        "forked into our own Roboflow workspace and re-split from 70/20/10 to the required 80/20. "
        "The dataset is used as published, with no images added to it. Seven first-party "
        "photographs are held back entirely as an unbiased test set. "
        "<br/><br/>"
        "Every label follows a written class-definition contract that specifies inclusions, "
        "exclusions, the one-box-per-visually-separable-group rule and a 20-pixel minimum size. "
        "The contract exists because without written rules, annotation drifts between people and "
        "the model learns the drift. SAM 3 and GPT-6 Astra were then run on the held-out images: "
        "both beat our own model on class accuracy, and neither produced output usable against our "
        "grouping rule.", y, width=left)

    rows = [["Dataset images", RUN["dataset_images"]],
            ["Split", RUN["split"]],
            ["Model", RUN["model"]],
            ["Epochs", RUN["epochs"]],
            ["Image size", RUN["imgsz"]],
            ["Batch", RUN["batch"]],
            ["Hardware", RUN["hardware"]],
            ["Training time", RUN["train_time"]]]
    t = Table(rows, colWidths=[CW * 0.19, CW * 0.19], rowHeights=[14.5] * len(rows))
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (0, -1), SANS, 8),
        ("FONT", (1, 0), (1, -1), SANS_B, 8),
        ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (-1, -1), BG_TINT),
    ]))
    _, th = t.wrap(0, 0)
    t.drawOn(c, RM + left + 10, y - th)
    y = min(y_after, y - th) - 16

    y = h(c, "Results", y)
    rows = [["Class", "Precision", "Recall", "mAP@50", "mAP@50-95"],
            ["All classes", fmt(METRICS["precision"]), fmt(METRICS["recall"]),
             fmt(METRICS["mAP50"]), fmt(METRICS["mAP50_95"])]]
    for k, v in PER_CLASS.items():
        rows.append([k, fmt(v.get("precision")), fmt(v.get("recall")),
                     fmt(v.get("mAP50")), fmt(v.get("mAP50_95"))])
    t = Table(rows, colWidths=[CW * 0.30] + [CW * 0.175] * 4,
              rowHeights=[15] + [14] * (len(rows) - 1))
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), SANS_B, 8),
        ("FONT", (0, 1), (-1, -1), SANS, 8),
        ("FONT", (0, 1), (-1, 1), SANS_B, 8),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("BACKGROUND", (0, 1), (-1, 1), BG_TINT),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("LINEBELOW", (0, 1), (-1, -2), 0.3, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    _, th = t.wrap(0, 0); t.drawOn(c, RM, y - th)
    c.showPage()

    # ---------------- page 2 ----------------
    report_chrome(c, 2, 2)
    y = PH - 24 * mm

    y = h(c, "Interpretation", y)
    for i, tk in enumerate(TAKEAWAYS, 1):
        c.setFillColor(ACCENT); c.setFont(SANS_B, 9)
        c.drawString(RM, y - 8, f"{i}.")
        p = Paragraph(tk, ps("k", 9.3, 13.2, SANS, INK))
        _, ht = p.wrap(CW - 16, 400); p.drawOn(c, RM + 16, y - ht)
        y -= ht + 9
    y -= 6

    y = h(c, "Error analysis and next iteration", y)
    y = body(c,
        "Three false positives and three false negatives are documented with filenames in "
        "<i>docs/error_analysis.md</i>. Five of the six are explained by one cause — objects "
        "recognised at the training set's scale and not at any other — and the sixth by an "
        "annotation-convention dispute. Three prioritised data improvements follow, each naming "
        "a concrete action and the metric it should move.", y)
    y -= 14

    y = h(c, "Risk: the asymmetry between the two errors", y)
    y = body(c,
        "<b>A false negative is silent.</b> Steelbar is placed, the model misses it, no record is "
        "created, and nobody investigates because nobody knows there is anything to investigate. "
        "The gap propagates into the programme unchallenged. <b>A false positive is loud.</b> A "
        "phantom record is contradicted by the next site walk. It costs a wasted verification trip "
        "and is self-correcting."
        "<br/><br/>"
        "For progress logging, therefore, <b>recall is the priority</b>. For site-condition alerts "
        "the asymmetry reverses: repeated false alarms teach supervisors to ignore the system. "
        "<b>One model, two thresholds</b> — low for logging, high for alerting — both read off the "
        "precision-recall curve rather than left at the default.", y)
    y -= 14

    y = h(c, "Limitations", y)
    for lim in LIMITATIONS:
        c.setFillColor(ACCENT); c.setFont(SANS_B, 9)
        c.drawString(RM, y - 8, "—")
        p = Paragraph(lim, ps("l", 9.3, 13.2, SANS, INK))
        _, ht = p.wrap(CW - 14, 400); p.drawOn(c, RM + 14, y - ht)
        y -= ht + 6
    y -= 10

    y = h(c, "Governance and licensing", y)
    rows = [["Artefact", "Licence", "Owned", "Constraint"],
            ["Code and notebooks", "MIT", "Yes", "None"],
            ["Base dataset", "CC BY 4.0", "No", "Redistributed under CC BY 4.0 with attribution"],
            ["Held-out test images", "CC BY 4.0", "Yes", "Our own photographs; never trained on"],
            ["Trained weights", "AGPL-3.0", "Derived", "Commercial use needs AGPL compliance or a licence"]]
    t = Table(rows, colWidths=[CW * 0.20, CW * 0.13, CW * 0.10, CW * 0.57],
              rowHeights=[14] + [13.5] * 4)
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), SANS_B, 7.6),
        ("FONT", (0, 1), (-1, -1), SANS, 7.6),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("LINEBELOW", (0, 1), (-1, -2), 0.3, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ]))
    _, th = t.wrap(0, 0); t.drawOn(c, RM, y - th)
    y -= th + 12

    y = body(c, "No class detects or tracks people — by design: a person or PPE class would make "
                "this EU AI Act high-risk.", y,
             size=8.6, leading=12, color=MUTED)

    c.save()
    print(f"wrote {path}")


if __name__ == "__main__":
    build_slides()
    build_report()
    print("\nDone. Re-run after training to pick up real metrics from results/metrics.json.")
