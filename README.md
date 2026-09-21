# Construction Element Detection for Site Progress Verification

**MAICEN0526 — M4U3 Assignment · Group 6**
A YOLOv8 object-detection pipeline that identifies construction elements and plant in site photographs, so that progress and site condition can be logged as structured data instead of narrative.

Everything in this repository runs in Google Colab. No local installation is required.

> **Building this for the first time?** Start with [`DO_THIS_NEXT.md`](DO_THIS_NEXT.md) — what is already done, what is outstanding, and the exact order to do it in.

---

## 1. AECO problem and success criteria

### The problem

On active sites across the GCC, progress reporting is still a manual, photographic process. A site engineer walks the floor, takes 50–200 photos, and later writes a narrative progress note that a planner transcribes into a schedule update. Three things go wrong:

1. **Latency.** The gap between the photo being taken and the progress record being updated is typically 2–7 days. Decisions are made on stale data.
2. **Inconsistency.** Two engineers describe the same floor differently. There is no controlled vocabulary linking what is visible to a structured progress record.
3. **Loss of evidence.** The photograph is archived as an image. The *information* inside it — rebar is placed, blockwork has started, conduit is run — is never captured as data, so it cannot flow into a Common Data Environment or be audited later.

ISO 19650 asks for information to be produced to a defined level of need and delivered into a CDE in a structured form. A JPEG in a folder does not meet that bar. A detection record — *image, timestamp, location, class, confidence, bounding box* — does.

### What this model does

Given a site photograph, it detects five classes of construction items and returns their location and confidence. That output feeds two distinct uses, and the distinction matters because it drives the operating thresholds:

- **Progress signal.** Presence and count of `steelbar`, `brick` and `pvcpipe` in a zone is a proxy for structural, masonry and MEP first-fix activity in that zone.
- **Site-condition signal.** `scaffold` indicates temporary works still standing — a zone not yet released. `excavator` indicates plant present and earthworks active, which feeds plant utilisation and logistics reporting.

### Success criteria

| # | Criterion | Target | Why this threshold |
|---|---|---|---|
| S1 | Overall validation mAP@50 | ≥ 0.50 | Sufficient for a *triage* tool: it directs a human to the right photographs, it does not replace the human. |
| S2 | Recall on `steelbar` | ≥ 0.50 | The primary progress-bearing class, and the largest at 27.4% of instances. Missing it produces a false "no activity" reading, which is the costly error. |
| S3 | Recall on `brick` | ≥ 0.40 | Second progress-bearing class. The bar was set low because `brick` has the fewest instances (13.5%). The cross-check suggests this was the wrong reason — `brick` is among the strongest classes — but the target is left as published rather than quietly raised after seeing results. |
| S4 | Inference speed | < 100 ms/image on a T4 GPU | A 200-photo daily walk must process in under one minute to fit a daily reporting cycle. |
| S5 | Reproducibility | Restart-and-run-all in Colab from this repo | Non-negotiable. A result a third party cannot re-run is not a result. |

**Explicit non-goal:** this model does not measure quantities, percentages complete, or conformance to design. It detects presence. Anything beyond presence requires a different method and is out of scope — see [`docs/governance_checklist.md`](docs/governance_checklist.md).

---

## 2. Classes and label rules

Five classes, inherited from the source dataset's annotation schema:

| ID | Class | What counts | What does not | Instances |
|---|---|---|---|---|
| 0 | `brick` | Clay brick and concrete block — on pallets, stacked, or laid in a wall | Cast concrete, stone cladding, paving | 140 (13.5%) |
| 1 | `excavator` | Tracked or wheeled excavating plant, whole machine including boom | Loaders, dozers, dump trucks, cranes | 258 (24.9%) |
| 2 | `pvcpipe` | Plastic pipe, conduit and duct — stacked or installed | Metal pipe, HVAC duct, cable tray, hose | 172 (16.6%) |
| 3 | `scaffold` | Erected scaffolding and access towers | Loose tube on the ground, handrail, formwork, ladders | 181 (17.5%) |
| 4 | `steelbar` | Reinforcement bar — loose, bundled, tied in cages, or cast-in | Structural steel, **scaffold tube**, mesh fencing | 284 (27.4%) |

**We predicted the `steelbar`/`scaffold` boundary would dominate the confusion matrix. It did not.** A hosted YOLOv11n cross-check on the same images produced **zero** steelbar/scaffold confusions in either direction, and only one inter-class error in the whole validation set.

What the evidence shows instead:

- **The error mode is missed detections, not mislabelling.** 95 of 103 errors are objects the model never saw; 8 are false positives; 1 is a class confusion.
- **Instance count does not predict performance.** `brick` has the fewest instances (140) and scores mAP@50 0.844. `steelbar` has the most (284) and scores 0.539, the worst of the five.
- **Shape predicts performance.** Compact objects with a clear outline — `excavator`, `scaffold`, `brick` stacks — land at 0.84–0.87. Thin, elongated, group-boxed objects — `pvcpipe`, `steelbar` — land at 0.54–0.64, and their mAP@75 collapses to 0.06–0.07, meaning even the detections they do make are badly localised.

That last point traces back to our own labelling rule, *one box per visually separable group*, which is ill-defined for a tangled bundle of bar. The training target is inconsistent, so the model cannot learn the boundary. Full evidence: [`docs/error_analysis.md`](docs/error_analysis.md) §0.

Full label rules, edge cases, the occlusion convention and the accepted ambiguities: [`docs/class_definitions.md`](docs/class_definitions.md).

---

## 3. Dataset

A public dataset **forked into our own Roboflow workspace**, re-split, and extended with our own images and boundary cases. The fork is deliberate: the unit requires a cloud-hosted Roboflow project under our own control, and a pure reference to somebody else's dataset would not let us re-split it, add boundary cases, or test our own class definitions against it.

### Our Roboflow project — live

| Field | Value |
|---|---|
| Workspace | `yazan-darwish` |
| Project | [`construction-site-km7bh-fapwu`](https://app.roboflow.com/yazan-darwish/construction-site-km7bh-fapwu) |
| **Version used for the reported run** | **`1`** (generated 2026-09-21) |
| Images | 700 |
| Split | **Train 560 (80%) / Valid 140 (20%) / Test 0** |
| Preprocessing | Auto-orient; resize stretch to 640×640 |
| Augmentation | **None** |
| Export format | YOLOv8 |

These three values are already set in the CONFIG cell of both notebooks:

```python
RF_WORKSPACE = "yazan-darwish"
RF_PROJECT   = "construction-site-km7bh-fapwu"
RF_VERSION   = 1
```

### Forked source

| Field | Value |
|---|---|
| Source | Roboflow Universe — [`seungyeon/construction-site-km7bh`](https://universe.roboflow.com/seungyeon/construction-site-km7bh) |
| Images | 700 |
| Published split | Train 490 (70%) / Valid 140 (20%) / Test 70 (10%) |
| Licence | CC BY 4.0 |
| Attribution | SeungYeon workspace, Roboflow Universe |

**On the re-split.** The source ships 70/20/10. The assignment requires 80/20, so we rebalanced to 560/140/0 — moving 70 images out of the test split and into training, and leaving validation untouched at 140. Validation membership is therefore identical to the source's, which means the split change did not leak any previously-held-out image into the set we report on.

**The cost of that, stated plainly:** there is now no untouched test set. Every number in §4 comes from the validation set, which is also the set we will inspect while writing the error analysis. That makes the reported metrics a *development* estimate, not an unbiased generalisation estimate. This is exactly why the five unseen images in `data/new_images/` matter — they are the only genuinely held-out evidence in this project, and they should be weighted accordingly.

### Augmentation: deliberately off

Version 1 applies no augmentation. Adding augmentation before a baseline exists hides what the data is doing — you cannot tell whether a gain came from the augmentation or from the model, and you cannot tell which class was weak to begin with. The baseline comes first; augmentation, if it is warranted, becomes version 2 and is justified by the error analysis.

### Our layer — added images

> **TODO:** complete after adding your own images. The unit requires 25, of which at least 5 are boundary cases.

| Field | Value |
|---|---|
| Images added by us | `__` (target: 25 minimum) |
| Of which boundary cases | `__` (target: 5 minimum) |
| Version regenerated after adding | `__` |
| Annotation tool | Roboflow annotate, SAM-assisted — see [`docs/sam_exploration.md`](docs/sam_exploration.md) |
| QA | Every added image reviewed by a second group member against [`docs/class_definitions.md`](docs/class_definitions.md) |

**Boundary cases to add** — the objects that look like a class and are not. The first row is the important one: it targets the `steelbar`/`scaffold` boundary that we expect to dominate the confusion matrix.

| File | Looks like | Actually is | Rule it tests |
|---|---|---|---|
| `__` | `steelbar` | Loose scaffold tube on the ground | Belongs to *neither* class — the hardest rule in the contract |
| `__` | `scaffold` | Ladder, handrail or hoarding frame | "Erected access structure", not any vertical frame |
| `__` | `brick` | Stone cladding or paving block | Material versus form |
| `__` | `pvcpipe` | Metal conduit under dust | Material identification when colour is unreliable |
| `__` | `excavator` | Wheeled loader or dozer | Machine type, not just "yellow plant" |

The dataset is **not** committed to this repository. The training notebook downloads it at runtime from Roboflow using your own API key, which keeps credentials out of version control and the repo small. See §5.

---

## 4. Results summary

> **STATUS: awaiting first full training run.** The table below is the reporting template. Numbers are filled from the run summary printed by `notebooks/01_training_eval.ipynb`. Do not submit with placeholders in place.

### Overall (validation set, 190 images)

| Metric | Value |
|---|---|
| Precision | `__` |
| Recall | `__` |
| mAP@50 | `__` |
| mAP@50–95 | `__` |

### Per class

| Class | Images | Instances | P | R | mAP@50 | mAP@50–95 |
|---|---|---|---|---|---|---|
| brick | `__` | `__` | `__` | `__` | `__` | `__` |
| excavator | `__` | `__` | `__` | `__` | `__` | `__` |
| pvcpipe | `__` | `__` | `__` | `__` | `__` | `__` |
| scaffold | `__` | `__` | `__` | `__` | `__` | `__` |
| steelbar | `__` | `__` | `__` | `__` | `__` | `__` |

### Key takeaways

> Replace with three observations once the run completes. Each one should name a class, a number, and a consequence. Template:

1. **Against success criteria:** S1 was `met / not met` at mAP@50 = `__` against a target of 0.50. `One sentence on what that means for the triage use case.`
2. **Strongest and weakest class:** `Class X` performs best (mAP@50 `__`), `Class Y` worst (`__`). The gap is explained by `instance count / object scale / annotation consistency`.
3. **Dominant error mode:** `Most errors are false negatives on small, occluded instances / most errors are false positives confusing class A with class B`. This matters because `consequence for the progress-reporting use case`.

Curves and confusion matrix: [`results/curves/`](results/curves/) · Prediction examples: [`results/evidence/`](results/evidence/) · Full error analysis: [`docs/error_analysis.md`](docs/error_analysis.md)

---

## 5. How to reproduce

Two notebooks, run in order. Both open directly in Colab from this repository.

### Before you start: get a Roboflow API key (one minute, free)

1. Create a free account at [roboflow.com](https://roboflow.com).
2. Go to **Settings → API Keys** and copy your **Private API Key**.
3. Keep it to hand. The notebook will prompt you for it and hide it as you type. **Never paste it into a code cell and never commit it.**

### Notebook 1 — Training and evaluation

**Open:** `notebooks/01_training_eval.ipynb` → in GitHub, click the *Open in Colab* badge at the top of the notebook.

1. **Runtime → Change runtime type → T4 GPU → Save.** Confirm the GPU is live: cell 2 prints the device name. If it prints `CPU`, stop and change the runtime — training on CPU will not finish.
2. **Runtime → Restart session and run all.**
3. When prompted, paste your Roboflow API key and press Enter.
4. Wait. Expected runtime is given in §6.
5. The notebook prints a metrics table, writes curves to `results/curves/`, and zips the trained weights for download.
6. **Download `best.pt`** when the last cell offers it, and attach it to a GitHub Release (see §7).

**Configuration is in one cell, near the top, marked `# ---- CONFIG ----`.** Nothing else needs editing.

```python
MODEL_VARIANT = "yolov8s.pt"   # yolov8n.pt is faster, yolov8s.pt is more accurate
EPOCHS        = 30             # assignment minimum
IMGSZ         = 640
BATCH         = 16
VERIFICATION_RUN = False       # set True for the 5-epoch no-GPU fallback — see below
```

**If no GPU is available:** set `VERIFICATION_RUN = True`. The notebook then trains for 5 epochs purely to prove the pipeline executes, and loads the real released weights for all inference and metrics. The notebook prints a clear banner saying which mode it is in, and that mode is recorded in the output.

### Notebook 2 — Baseline inference and evidence pack

**Open:** `notebooks/02_baseline_inference.ipynb`

1. **Runtime → Restart session and run all.**
2. It downloads the released weights (no API key needed), runs inference on the 190 validation images and on the new images in `data/new_images/`, and writes annotated outputs to `results/evidence/`.
3. The last cell zips the evidence pack for download.

### Expected outputs

| Step | Produces |
|---|---|
| NB1 cell "Train" | `runs/detect/train/` with weights and curves |
| NB1 cell "Evaluate" | Printed P / R / mAP50 / mAP50-95 table, overall and per class |
| NB1 cell "Save curves" | `results/curves/results.png`, `confusion_matrix.png`, `BoxPR_curve.png`, `labels.jpg` |
| NB2 cell "Validation inference" | 10 annotated validation images in `results/evidence/validation/` |
| NB2 cell "New-image inference" | 5 annotated new images in `results/evidence/new_images/` |

---

## 6. Reproducibility proof

> **STATUS: to be completed after the first successful end-to-end run.** Fill every field. This section is worth marks on its own.

| Field | Value |
|---|---|
| Date and time of last successful full run | `____-__-__ __:__ (UTC+3)` |
| Run mode | `Full 30-epoch run` / `5-epoch verification run + released weights` |
| Accelerator reported by the notebook | `Tesla T4` / `____` |
| Colab tier | `Free` / `Pro` |
| Wall-clock training time | `__ min` |
| Wall-clock total, restart-to-finish | `__ min` |
| Expected runtime range for a third party | `25–45 min on a free-tier T4` |
| Run by | `____` |

### Reproducibility checklist

- [ ] **Dataset version:** `yazan-darwish/construction-site-km7bh-fapwu`, version `1`, YOLOv8 export. Forked from [`seungyeon/construction-site-km7bh`](https://universe.roboflow.com/seungyeon/construction-site-km7bh) and re-split.
- [ ] **Split:** 560 train / 140 validation (80/20), rebalanced from the source's 70/20/10 in Roboflow
- [ ] **Model variant:** `yolov8s.pt` (COCO-pretrained), Ultralytics default architecture
- [ ] **Epochs:** 30
- [ ] **Batch size:** 16
- [ ] **Image size:** 640
- [ ] **Optimiser / LR:** Ultralytics defaults (`optimizer='auto'`, `lr0=0.01`), not overridden
- [ ] **Random seed:** `0` (Ultralytics default, set explicitly in the config cell)
- [ ] **Ultralytics version:** pinned in `requirements.txt` and printed by the notebook at runtime
- [ ] **Full environment:** `pip freeze` output written to `results/pip_freeze.txt` by the notebook
- [ ] **Weights:** published as a GitHub Release asset — see §7
- [ ] **Hardware:** recorded in the table above
- [ ] **Notebook runs end to end from a clean runtime:** verified on the date above

**Code-path verification.** Before the first training run, every Ultralytics API call in `01_training_eval.ipynb` and `02_baseline_inference.ipynb` was executed against **ultralytics 8.4.157 / torch 2.14.0** on a synthetic five-class dataset, to confirm no cell raises. Two issues were found and fixed: `model.val()` wrote its plots outside the results tree until `project`/`name` were passed, and the precision-recall plot is named `BoxPR_curve.png` in the 8.4 series, not `PR_curve.png`. This is a check that the pipeline *executes*; it is not a substitute for the full cold-start run recorded above.

---

## 7. Trained weights

Weights are distributed as a **GitHub Release asset**, not committed to the repository (a `.pt` file is ~22 MB and does not belong in git history).

> **TODO before submission:** create a release and paste the link here.
> `Releases → Draft a new release → Tag v1.0 → attach best.pt → Publish`

| Asset | Link | Size | SHA-256 |
|---|---|---|---|
| `best.pt` | `PASTE RELEASE ASSET URL HERE` | `__ MB` | `__` |

Both notebooks read the weights from the constant `WEIGHTS_URL` in their config cell. Update it in both places once the release exists.

---

## 8. Repository structure

```
.
├── README.md                     ← you are here
├── DO_THIS_NEXT.md               ← remaining steps, in order
├── LICENSE                       ← MIT, code only
├── requirements.txt              ← pinned versions
├── notebooks/
│   ├── 01_training_eval.ipynb    ← train, evaluate, export curves
│   └── 02_baseline_inference.ipynb ← load weights, run inference, build evidence pack
├── docs/
│   ├── class_definitions.md      ← the five classes and their label rules
│   ├── error_analysis.md         ← 3 FP + 3 FN + 3 prioritised data improvements
│   ├── governance_checklist.md   ← privacy, minimisation, limitations, risk
│   └── sam_exploration.md        ← what SAM helped with and what it did not
├── results/
│   ├── curves/                   ← training curves, PR curve, confusion matrix
│   ├── evidence/
│   │   ├── annotations/          ← 3–5 ground-truth annotation examples
│   │   ├── validation/           ← 10 validation predictions
│   │   └── new_images/           ← 5 new-image predictions
│   ├── metrics.json              ← machine-readable metrics, written by NB1
│   └── pip_freeze.txt            ← full environment capture
├── reports/
│   ├── slides.pdf                ← 8 slides
│   └── mini_report.pdf           ← 2 pages
├── data/
│   └── new_images/               ← unseen images for the generalisation test
└── tools/
    └── build_reports.py          ← regenerates the two PDFs from markdown source
```

---

## 9. Documents

| Document | Contents |
|---|---|
| [Class definitions](docs/class_definitions.md) | The five classes, inclusion and exclusion rules, occlusion convention |
| [Error analysis](docs/error_analysis.md) | Three false positives and three false negatives with hypotheses, plus three prioritised dataset improvements |
| [Governance checklist](docs/governance_checklist.md) | Privacy and consent, data minimisation, limitations statement, false-negative vs false-positive risk |
| [SAM exploration](docs/sam_exploration.md) | Where the Segment Anything Model assisted annotation and where it did not |
| [Slides (PDF)](reports/slides.pdf) | 8-slide summary |
| [Mini report (PDF)](reports/mini_report.pdf) | 2-page executive summary, results and limitations |

---

## 10. Licence and data rights

**Code and notebooks in this repository:** MIT Licence — see [`LICENSE`](LICENSE). Free to use, modify and redistribute with attribution.

**Dataset:** *not owned by this project.* The base dataset is published on Roboflow Universe as [`seungyeon/construction-site-km7bh`](https://universe.roboflow.com/seungyeon/construction-site-km7bh) under **CC BY 4.0**. It is used here under that licence, with attribution. Our fork re-splits it and adds our own images; it is not redistributed in this repository, and the notebook downloads it from our Roboflow project at runtime. Anyone reusing this work must credit the original dataset authors.

**Trained weights:** derived from a CC BY 4.0 dataset and from Ultralytics YOLOv8, which is distributed under **AGPL-3.0**. The weights are released for academic and evaluation purposes. Any commercial deployment of a YOLOv8-derived model requires either compliance with AGPL-3.0 or an Ultralytics commercial licence. This is a real constraint, not a formality.

**Images in the evidence pack:** drawn from the CC BY 4.0 dataset and from `data/new_images/`. No images of identifiable individuals on a private site are included — see the governance checklist for how this was checked.

---

## 11. Authors

MAICEN0526 — Master in AI for Architecture & Construction, ZIGURAT Institute of Technology / University of Barcelona (IL3).
Module 4, Unit 3 — Group 6.

> **TODO:** list group member names here.
