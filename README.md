# Construction Element Detection for Site Progress Verification

**MAICEN0526 — M4U3 Assignment · Group 6**
A YOLOv8 object-detection pipeline that identifies construction elements and plant in site photographs, so that progress and site condition can be logged as structured data instead of narrative.

Everything in this repository runs in Google Colab. No local installation is required.

> **Building this for the first time?** Start with [`docs/TEAM_GUIDE.md`](docs/TEAM_GUIDE.md) — a step-by-step replication guide written for someone who has never trained a model or used GitHub, with a checklist, a plain-language glossary, and every trap we hit.

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

**We predicted the `steelbar`/`scaffold` boundary would dominate the confusion matrix. It did not.** A hosted YOLOv11n cross-check produced **zero** steelbar/scaffold confusions in either direction, and one inter-class error in the whole validation set. Two things replaced that prediction:

- **The error mode is missing objects, not mislabelling them.** In the cross-check, 95 of 103 errors were objects never detected; 8 were false positives; 1 was a class confusion. The graded run shows the same signature — precision (0.950) well above recall (0.884).
- **`steelbar` is the weakest class under both architectures.** mAP@50 **0.781** on the graded YOLOv8s run and **0.539** on the YOLOv11n cross-check — worst of the five in each, despite having the *most* training instances. Its recall (0.612) is the lowest by a wide margin.

**Instance count does not explain this.** `brick` has the fewest instances and scores 0.995. The hypothesis that survives is our own labelling rule, *one box per visually separable group*, which is undecidable for a tangled bundle of bar: the training target is inconsistent image to image, so there is no stable boundary to learn.

We first blamed "thin and elongated" objects generally, which would have implicated `pvcpipe` too. It scored 0.964 on the graded run, so that is wrong — the distinguishing feature of `steelbar` is that it comes **bundled**, not that it is thin. Narrowing that hypothesis is documented in [`docs/error_analysis.md`](docs/error_analysis.md) §0.

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

### Our layer — no images were added

We sourced 25 candidate images to extend the dataset and added **none of them**. Twenty were watermarked Shutterstock previews carrying no usable licence; five were CC0 but too few to move a 700-image dataset. The full record, including the three grounds for rejection, is in [`docs/image_provenance.md`](docs/image_provenance.md) §A.

| Field | Value |
|---|---|
| Images added to the training dataset | **0** |
| Candidates sourced, checked and rejected | 20 (no licence) |
| Candidates cleared but unused | 5 (Piqsels, CC0 1.0) |
| Training dataset | The base Roboflow project unchanged — 700 images, wholly CC BY 4.0 |
| Held-out images we do own | 7 first-party photographs in `data/new_images/`, never trained on |
| Provenance and licences | Recorded in [`docs/image_provenance.md`](docs/image_provenance.md) |

The assignment brief does not require dataset expansion, so nothing in the rubric depends on this. What it did cost is measurable and is recorded rather than hidden: two of the five rejected boundary cases targeted the exact confusions that later appeared as FP-1 and FP-2 in [`docs/error_analysis.md`](docs/error_analysis.md).

The dataset is **not** committed to this repository. The training notebook downloads it at runtime from Roboflow using your own API key, which keeps credentials out of version control and the repo small. See §5.

---

## 4. Results summary

### Overall (validation set, 140 images)

| Metric | Value |
|---|---|
| Precision | **0.950** |
| Recall | **0.884** |
| mAP@50 | **0.943** |
| mAP@50–95 | **0.809** |

> **Read §4.1 before quoting these numbers.** They are inflated by near-duplicate leakage between the train and validation splits. They are reported as measured, with the defect documented, rather than quietly presented as a generalisation estimate.

### Per class

| Class | Val images | Train instances | P | R | mAP@50 | mAP@50–95 |
|---|---|---|---|---|---|---|
| `brick` | 140 | 109 | 0.984 | 1.000 | 0.995 | 0.932 |
| `excavator` | 140 | 207 | 0.969 | 1.000 | 0.995 | 0.883 |
| `pvcpipe` | 140 | 129 | 0.986 | 0.930 | 0.964 | 0.835 |
| `scaffold` | 140 | 157 | 0.955 | 0.875 | 0.979 | 0.858 |
| `steelbar` | 140 | 226 | 0.855 | 0.612 | 0.781 | 0.535 |

### 4.1 The headline number is inflated — here is the evidence

Three independent signals say the train/validation split leaks:

**1. Consecutive frames are split across train and validation.** The source images are sequentially numbered, and neighbouring numbers — the same scene seconds apart — land on opposite sides of the split:

| Image | Split |
|---|---|
| `steelBar_5397k.jpg` | train |
| `steelBar_5398k.jpg` | **valid** |
| `scaffold_9753j.jpeg` | **valid** |
| `scaffold_9754j.jpeg` | train |
| `scaffold_9755j.jpeg` | train |

**2. mAP@50 was 0.677 after a single epoch.** A 5-class detector that has seen the training set once should be near zero on genuinely held-out data. It was already two-thirds of the way to its final score.

| epoch | 1 | 5 | 10 | 20 | 30 |
|---|---|---|---|---|---|
| mAP@50 | **0.677** | 0.590 | 0.875 | 0.941 | 0.941 |

**3. Two classes reach recall 1.000.** `brick` and `excavator` miss nothing at all, on a 560-image training set with no augmentation.

**Cause.** Roboflow's split is random over images. When a dataset is built from video frames or photo bursts, random splitting puts near-identical images on both sides. Our re-split from 70/20/10 to 80/20 inherited this — we moved the test images into training and left validation untouched, which preserved the original split's leakage rather than introducing it.

**What the numbers still support.** Per-class *ranking* is still informative, because every class is equally advantaged: `steelbar` is the weakest class at 0.781 despite having the most training instances, and it was also weakest in an independent YOLOv11n cross-check at 0.539. Two architectures agreeing on that ordering is a real finding.

**What they do not support.** Any claim about performance on unseen sites. The seven images in `data/new_images/` are the only honest generalisation evidence in this project. Section 4.2 reports what they showed.

**The fix**, and the first entry in our iteration plan: re-split by **group** rather than at random — cluster images by filename prefix and sequence number so that consecutive frames stay on the same side — then retrain and report both numbers side by side.

### 4.2 What happened on images the model had never seen

The seven first-party photographs in `data/new_images/` were never in the Roboflow project, never in any split, and never in a shoot that fed one. They are the only measurement here that the leakage in §4.1 cannot flatter. At the same settings used for validation — conf 0.25, `imgsz=640`:

| | Validation (10 images) | Held-out (7 images) |
|---|---|---|
| Prediction matched what is in the image | **8 of 10** | **1 of 7**, and that one marginally (0.254) |
| Wrong-class detections | 0 | 2, one of them at confidence **0.78** |
| Images returning nothing at all | 0 | 4 |

Two of the seven were chosen as **controls** — a `brick` wall and an `excavator`, the classes that scored mAP@50 0.995 with recall **1.000** on validation. Both failed: the blockwork wall was called `scaffold` at 0.78, and the excavator was not detected at all.

**Lowering the confidence threshold does not recover it.** At conf 0.02 — effectively "show everything considered" — the missed objects still produce no proposal of the right class. The detections are not hiding below the threshold; they were never made. This matters because §4 of the governance checklist argues for a low operating threshold to protect recall, and that argument only works in-distribution.

**Changing the input resolution changes the predicted class.** Same weights, same image, same threshold:

| Image | `imgsz=640` | `imgsz=1280` | `imgsz=2560` | Truth |
|---|---|---|---|---|
| `new_04` | `scaffold` 0.78 | `scaffold` 0.31 | **`brick` 0.46** | `brick` |
| `new_05` | `scaffold` 0.28 | `steelbar` 0.27 | `steelbar` 0.57 | `pvcpipe` |
| `new_03` | nothing | **`excavator` 0.52** | nothing | `excavator` |

Evidence: [`results/evidence/new_images/resolution_instability.png`](results/evidence/new_images/resolution_instability.png).

A model that had learned what blockwork *is* would not change its mind when the image is resampled. One that has learned a spatial-frequency signature would. That is the conclusion [`docs/error_analysis.md`](docs/error_analysis.md) reaches, and it explains the validation/held-out gap: validation images match the training set's framing and apparent object size by construction, and our own photographs do not.

**Seven images is a probe, not a statistic.** It establishes that the failure mode exists; it cannot say how often it occurs.

### Key takeaways

1. **The model scores mAP@50 0.943 on validation and detects almost nothing on our own photographs.** One marginal correct detection across seven unseen images, two confident wrong-class calls, four blanks — including both deliberate control classes. Section 4.2 has the numbers. This is the result that matters, and it is only visible because the held-out set exists.

2. **The failure is scale and texture, not capacity.** Changing only `imgsz` flips `new_04` from `scaffold` 0.78 to `brick` 0.46. Predictions that move under a semantically empty transformation indicate the model learned an image signature rather than an object class — so a larger architecture would raise the leaking validation figure and change none of the seven results.

3. **`steelbar` is the weakest class under both architectures tried** — 0.781 here, 0.539 in an independent YOLOv11n cross-check — despite having the *most* training instances (226). Instance count does not explain it; object shape and our own group-boxing rule do.

4. **Every success criterion was met, and that is the least interesting thing in this report.** S1 wanted mAP@50 ≥ 0.50 and got 0.943. Clearing a bar by that margin is itself evidence the measurement is wrong, which §4.1 documents and §4.2 confirms independently.

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
2. It downloads the released weights (no API key needed), runs inference on a 10-image sample of the 140 validation images and on the new images in `data/new_images/`, and writes annotated outputs to `results/evidence/`.
3. The last cell zips the evidence pack for download.

### Expected outputs

| Step | Produces |
|---|---|
| NB1 cell "Train" | `runs/detect/train/` with weights and curves |
| NB1 cell "Evaluate" | Printed P / R / mAP50 / mAP50-95 table, overall and per class |
| NB1 cell "Save curves" | `results/curves/results.png`, `confusion_matrix.png`, `BoxPR_curve.png`, `labels.jpg` |
| NB2 cell "Validation inference" | 10 annotated validation images in `results/evidence/validation/` |
| NB2 cell "New-image inference" | 7 annotated held-out images in `results/evidence/new_images/` |
| NB2 cell "Resolution sensitivity" | `results/evidence/new_images/resolution_instability.png` |

---

## 6. Reproducibility proof

| Field | Value |
|---|---|
| Date and time of last successful full run | **2026-09-21T20:40:39Z** |
| Run mode | **Full 30-epoch run** (not the verification fallback) |
| Accelerator | **Tesla T4, 15360 MiB** |
| Colab tier | Free |
| Wall-clock training time | **6.4 min** |
| Expected runtime range for a third party | 6–15 min on a free-tier T4 |
| ultralytics | **8.4.157** |
| torch | **2.11.0+cu128** |
| Python | 3.13.15 |
| Weights SHA-256 | `1c6bed773b68ac17bd1491d86431dd30178b76f42e128112d7093f5698d19e13` |
| Run by | Yazan Darwish, Colab free tier |

Training took **6.4 minutes**, not the 25–45 originally estimated — 700 images at 640 px on a T4 is a small job. The environment is captured verbatim in [`results/pip_freeze.txt`](results/pip_freeze.txt) and the machine-readable run record in [`results/metrics.json`](results/metrics.json).

### Cold-start verification of notebook 02

Notebook 02 was opened from GitHub into a **fresh Colab runtime** on 2026-09-22 and run end to end with *Run all*, on a different T4 session from the one that produced the committed evidence.

Every output file it produced was compared byte-for-byte against the committed version:

| Artefact | Result |
|---|---|
| `baseline_comparison.png`, `baseline_new_01..03` | **identical** |
| `pred_new_01..07.png` | **identical** |
| `confidence_sweep.png` | **identical** |
| **Total** | **12 of 12 byte-identical, 0 differing** |

That is a stronger result than the brief asks for. It means the pipeline is not merely re-runnable but **deterministic**: same weights from the Release, same seed, same library versions, same bytes out, on a machine that had never seen this project.

**One section did not run in this verification.** Section 5 downloads the validation split from Roboflow and needs a private API key. The key is entered at runtime via `getpass` and is deliberately not stored anywhere in this repository (governance check 2.5), so the cold-start run was taken with that prompt skipped — the notebook offers this explicitly. The ten validation comparisons in `results/evidence/validation/` come from the earlier run on 2026-09-21T22:37Z. Anyone with a Roboflow key reproduces them by entering it at that prompt; everything else runs without one.

### Cold-start verification of notebook 01 — a full re-train

On **2026-09-22** notebook 01 was opened from GitHub into a fresh Colab runtime and run end to end with *Run all*. This was a complete 30-epoch re-train from the COCO-pretrained checkpoint, not a reload of the released weights: the dataset was re-downloaded from Roboflow, re-split, and trained from scratch on a T4 that had never seen this project.

**Every reported metric came back identical to three decimal places.**

| | Original run (2026-09-21) | Re-train (2026-09-22) |
|---|---|---|
| Precision | 0.950 | **0.950** |
| Recall | 0.884 | **0.884** |
| mAP@50 | 0.943 | **0.943** |
| mAP@50–95 | 0.809 | **0.809** |
| `brick` (P/R/mAP50/mAP50-95) | 0.984 / 1.000 / 0.995 / 0.932 | **identical** |
| `excavator` | 0.969 / 1.000 / 0.995 / 0.883 | **identical** |
| `pvcpipe` | 0.986 / 0.930 / 0.964 / 0.835 | **identical** |
| `scaffold` | 0.955 / 0.875 / 0.979 / 0.858 | **identical** |
| `steelbar` recall | 0.612 | **0.612** |

All three success criteria passed with the same values: S1 mAP@50 0.943, S2 `steelbar` recall 0.612, S3 `brick` recall 1.000.

**Why it is exact rather than approximate.** `seed=0` is set in the config cell, Ultralytics runs with `deterministic=True` by default, and the dataset version is pinned. Neural-network training is often assumed to be irreproducible; with the seed fixed, the data version pinned and the same accelerator architecture, it is not.

**The bound on that claim.** This is reproducibility on the *same GPU architecture*. Different accelerator hardware (A100, L4, CPU) changes floating-point reduction order and would likely move the last digit or two. The claim here is "same notebook, same pinned inputs, same class of machine, same numbers" — which is what the assignment asks a third party to be able to check.

### Reproducibility checklist

- [x] **Dataset version:** `yazan-darwish/construction-site-km7bh-fapwu`, version `1`, YOLOv8 export. Forked from [`seungyeon/construction-site-km7bh`](https://universe.roboflow.com/seungyeon/construction-site-km7bh) and re-split.
- [x] **Split:** 560 train / 140 validation (80/20), rebalanced from the source's 70/20/10 in Roboflow
- [x] **Model variant:** `yolov8s.pt` (COCO-pretrained), Ultralytics default architecture
- [x] **Epochs:** 30
- [x] **Batch size:** 16
- [x] **Image size:** 640
- [x] **Optimiser / LR:** Ultralytics defaults (`optimizer='auto'`, `lr0=0.01`), not overridden
- [x] **Random seed:** `0` (Ultralytics default, set explicitly in the config cell)
- [x] **Ultralytics version:** `8.4.157` — pinned in `requirements.txt` and printed by the notebook at runtime
- [x] **Full environment:** `pip freeze` output written to `results/pip_freeze.txt` by the notebook
- [ ] **Weights:** published as a GitHub Release asset — see §7
- [x] **Hardware:** recorded in the table above
- [ ] **Notebook runs end to end from a clean runtime:** verified on the date above

**Code-path verification.** Before the first training run, every Ultralytics API call in `01_training_eval.ipynb` and `02_baseline_inference.ipynb` was executed against **ultralytics 8.4.157 / torch 2.14.0** on a synthetic five-class dataset, to confirm no cell raises. Two issues were found and fixed: `model.val()` wrote its plots outside the results tree until `project`/`name` were passed, and the precision-recall plot is named `BoxPR_curve.png` in the 8.4 series, not `PR_curve.png`. This is a check that the pipeline *executes*; it is not a substitute for the full cold-start run recorded above.

---

## 7. Trained weights

Distributed as a **GitHub Release asset**, not committed to the repository — a 22.5 MB binary cannot be removed from git history once pushed.

| Asset | Value |
|---|---|
| File | [`best.pt`](https://github.com/yazandarwish264-glitch/m4u3-construction-detection/releases/download/v1.0/best.pt) |
| Release | [`v1.0` — Trained weights v1.0](https://github.com/yazandarwish264-glitch/m4u3-construction-detection/releases/tag/v1.0) |
| Size | 22.5 MB (22,520,170 bytes) |
| SHA-256 | `1c6bed773b68ac17bd1491d86431dd30178b76f42e128112d7093f5698d19e13` |
| Architecture | `yolov8s`, 5 classes |
| Licence | AGPL-3.0, inherited from Ultralytics — see §10 |

Both notebooks read this URL from `WEIGHTS_URL` in their config cell; it is already set. Notebook 02 prints the SHA-256 of what it downloads — if it does not match the value above, the released file is not the model that produced the reported metrics.

---

## 8. Repository structure

```
.
├── README.md                     ← you are here
├── LICENSE                       ← MIT, code only
├── requirements.txt              ← pinned versions
├── notebooks/
│   ├── 01_training_eval.ipynb    ← train, evaluate, export curves
│   └── 02_baseline_inference.ipynb ← load weights, run inference, build evidence pack
├── docs/
│   ├── TEAM_GUIDE.md             ← how to replicate this from scratch, start here
│   ├── class_definitions.md      ← the five classes and their label rules
│   ├── error_analysis.md         ← 3 FP + 3 FN + 3 prioritised data improvements
│   ├── governance_checklist.md   ← privacy, minimisation, limitations, risk
│   ├── image_provenance.md       ← source and licence for every image we added
│   └── sam_exploration.md        ← SAM 3 and GPT-6 Astra vs our trained model
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
| [**Team guide — how we built this**](docs/TEAM_GUIDE.md) | Step-by-step replication guide written for someone who has never trained a model or used GitHub. Checklist, plain-language glossary, every trap we hit |
| [Class definitions](docs/class_definitions.md) | The five classes, inclusion and exclusion rules, occlusion convention |
| [Error analysis](docs/error_analysis.md) | Three false positives and three false negatives with hypotheses, plus three prioritised dataset improvements |
| [Governance checklist](docs/governance_checklist.md) | Privacy and consent, data minimisation, limitations statement, false-negative vs false-positive risk |
| [Image provenance](docs/image_provenance.md) | Source and licence for every image outside the base dataset — including the 20 candidates rejected on licence grounds, and why |
| [Foundation-model exploration](docs/sam_exploration.md) | SAM 3 and GPT-6 Astra run on the same held-out images. Both beat our trained model on class accuracy; neither produced output usable against our grouping contract |
| [Slides (PDF)](reports/slides.pdf) | 8-slide summary |
| [Mini report (PDF)](reports/mini_report.pdf) | 2-page executive summary, results and limitations |

---

## 10. Licence and data rights

**Code and notebooks in this repository:** MIT Licence — see [`LICENSE`](LICENSE). Free to use, modify and redistribute with attribution.

**Dataset:** *not owned by this project.* The base dataset is published on Roboflow Universe as [`seungyeon/construction-site-km7bh`](https://universe.roboflow.com/seungyeon/construction-site-km7bh) under **CC BY 4.0**. It is used here under that licence, with attribution. Our fork re-splits it and adds nothing to it (see §3 and [`docs/image_provenance.md`](docs/image_provenance.md) §A); it is not redistributed in this repository, and the notebook downloads it from our Roboflow project at runtime. Anyone reusing this work must credit the original dataset authors.

**Trained weights:** derived from a CC BY 4.0 dataset and from Ultralytics YOLOv8, which is distributed under **AGPL-3.0**. The weights are released for academic and evaluation purposes. Any commercial deployment of a YOLOv8-derived model requires either compliance with AGPL-3.0 or an Ultralytics commercial licence. This is a real constraint, not a formality.

**Images in the evidence pack:** drawn from the CC BY 4.0 dataset and from `data/new_images/`. No images of identifiable individuals on a private site are included — see the governance checklist for how this was checked.

---

## 11. Authors

MAICEN0526 — Master in AI for Architecture & Construction, ZIGURAT Institute of Technology / University of Barcelona (IL3).
Module 4, Unit 3 — Group 6.

- Ahmed Abdelaal
- Mohammad Abu Alhasan
- Yazan Abdel Rauof Ahmad Darweesh
- Clayton Peter Human
- Tarig Ismail Mohamed Abas

Supervisor: Pablo Aumente Gallego.
