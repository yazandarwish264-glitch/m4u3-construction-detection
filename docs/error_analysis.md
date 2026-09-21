# Error Analysis and Iteration Plan

Analysis of the validation run produced by `notebooks/01_training_eval.ipynb`.

| | |
|---|---|
| Run date | `____-__-__` |
| Weights | `best.pt`, epoch `__` |
| Validation set | 20% split, `__` images, `__` instances |
| Confidence threshold used for this analysis | `0.25` (Ultralytics default) |
| Classes | `brick`, `excavator`, `pvcpipe`, `scaffold`, `steelbar` |
| IoU threshold | `0.50` |

> **How to fill this in.** Open `results/curves/confusion_matrix.png` first — it tells you *which* class pairs are being confused. Then open the 10 annotated validation images in `results/evidence/validation/` beside their ground truth and find concrete instances. Every row below needs a real filename. A hypothesis without an image behind it reads as guesswork and scores as guesswork.

---

## 0. Prior evidence — the hosted cross-check

Before the graded run, we trained a **YOLOv11n** on the same images (version 2, 546/140/14) on Roboflow's hosted infrastructure, at the same 30 epochs. It is **not** the graded model — the deliverable is YOLOv8s on version 1, run in Colab — but it tells us what this dataset supports, and it tested a prediction we wrote down in advance.

| Overall (validation, 140 images) | |
|---|---|
| mAP@50 | 0.635 |
| mAP@50–95 | 0.328 |
| Precision | 0.547 |
| Recall | 0.653 |

### Per class

| Class | mAP@50 | mAP@75 | Precision | Recall | Train instances |
|---|---|---|---|---|---|
| `scaffold` | **0.866** | 0.656 | 1.000 | 0.708 | 181 |
| `excavator` | 0.856 | 0.249 | 0.977 | 0.824 | 258 |
| `brick` | 0.844 | 0.448 | 0.794 | 0.871 | **140 (fewest)** |
| `pvcpipe` | 0.637 | 0.069 | 0.757 | 0.651 | 172 |
| `steelbar` | **0.539** | 0.057 | 0.732 | 0.517 | **284 (most)** |

### Confusion matrix (validation, conf 0.20) — rows are truth, columns are prediction

| | brick | excavator | pvcpipe | scaffold | steelbar | **missed** |
|---|---|---|---|---|---|---|
| **brick** | 22 | 0 | 0 | 0 | 0 | 9 |
| **excavator** | 0 | 37 | 0 | 0 | 0 | 14 |
| **pvcpipe** | 0 | 0 | 17 | 0 | 0 | 26 |
| **scaffold** | 1 | 0 | 0 | 13 | 0 | 10 |
| **steelbar** | 0 | 0 | 0 | 0 | 22 | **36** |
| **false positives** | 2 | 0 | 2 | 0 | 4 | — |

---

### Finding 1 — our prediction was wrong, and the way it was wrong is informative

The README predicted that `steelbar` and `scaffold` would dominate the confusion matrix, because both are orthogonal steel members and our rules put loose scaffold tube in neither class.

**There is not one steelbar/scaffold confusion in the matrix.** Zero, in either direction. The only inter-class error in the entire validation set is a single `scaffold` called `brick`.

### Finding 2 — the real error mode is missing things, not mislabelling them

Of 103 errors, **95 are missed detections** and 8 are false positives. One is a class confusion. The model is not confused about what these objects are; it fails to see them at all.

This matters for the write-up because it changes which metric we should care about. Class confusion would be a class-definition problem. Wholesale misses are a detection problem — and, per the governance risk note, false negatives are the **silent** error, the one nobody investigates because no record is created.

### Finding 3 — instance count does not predict performance; shape does

We expected `brick` to be weakest because it has the fewest instances (140, 13.5%), and set its success target lower on that basis. The opposite happened:

- `brick`, with the **fewest** instances, scores mAP@50 **0.844**
- `steelbar`, with the **most** instances, scores **0.539** — the worst of the five

So the instance-count hypothesis is falsified on this data. The pattern that does fit is **object morphology**:

| | Compact, solid, clear outline | Thin, elongated, tangled, group-boxed |
|---|---|---|
| Classes | `excavator`, `scaffold`, `brick` stacks | `pvcpipe`, `steelbar` |
| mAP@50 | 0.84 – 0.87 | 0.54 – 0.64 |
| mAP@75 | 0.25 – 0.66 | **0.06 – 0.07** |

### Finding 4 — the thin classes are not just missed, they are badly boxed

Look at the mAP@75 column. `scaffold` holds 0.656 when the overlap requirement tightens; `steelbar` collapses to **0.057** and `pvcpipe` to **0.069**. Even when the model finds them, the box is in roughly the wrong place.

That points straight at our own [`class_definitions.md`](class_definitions.md) rule: *one box per visually separable group*. For a tangled bundle of bar or a stack of pipe, where the group starts and stops is a judgement call, so the training target is inconsistent from image to image. The model cannot learn a boundary that the labels do not agree on. **This is a data problem we created, not a model limitation** — and it is the strongest candidate for improvement D1.

### Finding 5 — 0.25 is the wrong operating threshold

The optimal threshold on this run is **0.09**, not the Ultralytics default of 0.25:

| conf | precision | recall | F1 |
|---|---|---|---|
| 0.10 | 0.845 | 0.689 | 0.754 |
| 0.20 | 0.924 | 0.550 | 0.680 |
| 0.30 | 0.965 | 0.367 | 0.491 |

At the default, **more than a third of real objects are already being dropped**. Per-class optima are lower still — `scaffold` 0.06, `pvcpipe` 0.07, `brick` 0.08, `steelbar` 0.09, `excavator` 0.11 — and at `scaffold` 0.06 precision is 1.000, so a low threshold costs nothing there.

**Refinement to the governance argument:** the data says thresholds should be set **per class**, not per use case. That does not break the two-threshold argument in [`governance_checklist.md`](governance_checklist.md) — the progress classes and the site-condition classes are disjoint sets — but the honest version is that each class has its own operating point, and the use case determines which way to round.

---

### Outcome — the graded run has now happened

The YOLOv8s run on version 1 landed at **mAP@50 0.943**, far above the cross-check's 0.635. Both are inflated by the same cause: near-duplicate frames split across train and validation (evidence in README §4.1). The comparison is still useful for **ranking**, because both runs are equally advantaged.

| Class | YOLOv8s (graded, v1) | YOLOv11n (cross-check, v2) | Agreement |
|---|---|---|---|
| `brick` | 0.995 | 0.844 | strong in both |
| `excavator` | 0.995 | 0.856 | strong in both |
| `scaffold` | 0.979 | 0.866 | strong in both |
| `pvcpipe` | 0.964 | 0.637 | **diverges** |
| `steelbar` | **0.781** | **0.539** | **weakest in both** |

**Confirmed:** `steelbar` is the worst class under two different architectures, despite having the most training instances (226 in train). The instance-count hypothesis stays falsified; the shape-and-group-boxing explanation stands.

**Not confirmed:** `pvcpipe` was predicted to be weak alongside `steelbar` on the same "thin and elongated" reasoning. It scored 0.964 on the graded run. So elongation alone does not explain the deficit — what separates `steelbar` is that it is routinely **bundled and tangled**, which is precisely where our one-box-per-group rule stops being decidable. That narrows the hypothesis rather than confirming it, and it is a better finding for having been narrowed.

---

### What this does and does not license us to say

**Does:** it gives us a prior. If the graded YOLOv8 run shows the same shape — misses dominating, `steelbar` and `pvcpipe` weakest, localisation poor on the thin classes — that is two independent architectures agreeing, which is stronger evidence than either alone.

**Does not:** these are not our reported numbers. Different architecture, different version, different split. Sections 1 and 2 below must be filled from **our own** Colab run on version 1, with our own filenames. If our run contradicts this, the contradiction is the finding and gets written up as such.

---

## 1. False positives — the model saw something that is not there

A false positive produces a **phantom record**: a report says blockwork started on level 3 when it has not, or says scaffold is still standing in a zone that was struck last week. The cost is a wasted verification trip and, repeated, a loss of trust in the tool.

### FP-1

| | |
|---|---|
| Image | `results/evidence/validation/____.jpg` |
| Predicted | `class` at confidence `0.__` |
| Ground truth | `nothing` / `class X` |
| What is actually in the box | `plain description of the real object` |

**Hypothesis.** `Why the model made this mistake. Tie it to a cause: a visual similarity the training data never disambiguated, a class boundary left ambiguous in docs/class_definitions.md §6, or an under-represented negative example.`

**Evidence for the hypothesis.** `What in the confusion matrix, the PR curve, or the instance counts supports this rather than a competing explanation.`

### FP-2

| | |
|---|---|
| Image | `results/evidence/validation/____.jpg` |
| Predicted | `class` at confidence `0.__` |
| Ground truth | `____` |
| What is actually in the box | `____` |

**Hypothesis.** `____`

**Evidence for the hypothesis.** `____`

### FP-3

| | |
|---|---|
| Image | `results/evidence/validation/____.jpg` |
| Predicted | `class` at confidence `0.__` |
| Ground truth | `____` |
| What is actually in the box | `____` |

**Hypothesis.** `____`

**Evidence for the hypothesis.** `____`

---

## 2. False negatives — the model missed something that is there

A false negative produces **silence where there should be a record**: rebar placed but not logged, debris accumulating but never flagged. For a progress-monitoring tool this is the more damaging error, because nobody goes looking for a record that was never created. See the risk note in [`governance_checklist.md`](governance_checklist.md).

### FN-1

| | |
|---|---|
| Image | `results/evidence/validation/____.jpg` |
| Missed object | `class`, `__` instances |
| Object condition | `occluded __% / small (~__ px) / motion blur / unusual lighting / atypical viewpoint` |
| Highest confidence the model gave it | `0.__` (below threshold) / `no detection at all` |

**Hypothesis.** `____`

**Evidence for the hypothesis.** `____`

### FN-2

| | |
|---|---|
| Image | `results/evidence/validation/____.jpg` |
| Missed object | `____` |
| Object condition | `____` |
| Highest confidence the model gave it | `____` |

**Hypothesis.** `____`

**Evidence for the hypothesis.** `____`

### FN-3

| | |
|---|---|
| Image | `results/evidence/validation/____.jpg` |
| Missed object | `____` |
| Object condition | `____` |
| Highest confidence the model gave it | `____` |

**Hypothesis.** `____`

**Evidence for the hypothesis.** `____`

---

## 3. Error pattern summary

Once the six cases above are filled in, state the pattern in two or three sentences. The rubric asks for *plausible hypotheses*, and a hypothesis is stronger when it explains several errors at once rather than one.

> `Example of the shape this should take: "Five of the six errors involve objects under roughly 40 px in the long dimension. The dataset was published at 416×416 and we train at 640, so small objects are upsampled from an already-degraded source. This is a data resolution problem, not a model capacity problem — which is why improvement D1 below is about image sourcing rather than about switching to yolov8m."`

`____`

---

## 4. Three prioritised data improvements

Each one names a **specific dataset gap**, a **specific action**, and the **metric it should move**. Ordered by expected gain per hour of effort.

### D1 — `Name the improvement`

| | |
|---|---|
| **Gap it addresses** | `Which of the six errors above this fixes, and why that gap exists` |
| **Action** | `Concrete and countable: "add N images of X under condition Y", not "improve the dataset"` |
| **Effort** | `__ hours` |
| **Metric it should move** | `recall on class __, currently 0.__` |
| **How we will know it worked** | `Re-run validation on the same held-out set; expect recall on class __ to rise above 0.__` |

### D2 — `Name the improvement`

| | |
|---|---|
| **Gap it addresses** | `____` |
| **Action** | `____` |
| **Effort** | `__ hours` |
| **Metric it should move** | `____` |
| **How we will know it worked** | `____` |

### D3 — `Name the improvement`

| | |
|---|---|
| **Gap it addresses** | `____` |
| **Action** | `____` |
| **Effort** | `__ hours` |
| **Metric it should move** | `____` |
| **How we will know it worked** | `____` |

---

## 5. Candidate improvements, for reference

Draw D1–D3 from this list once the real errors are known. Do not use these verbatim — they are prompts, and an improvement that does not match your actual errors will read as generic.

**If errors cluster on small or distant objects**
Add images captured closer to the subject; source at native resolution rather than the 416×416 published base; train at `imgsz=960`; apply a tiling strategy at inference so small objects occupy more pixels per tile.

**If errors cluster on one class with few instances**
Count instances per class from the training labels. A class under roughly 5% of total instances will underperform regardless of architecture. Targeted collection of that class is worth more than any hyperparameter change.

**If errors cluster on a class *pair* in the confusion matrix**
The boundary between those two classes is under-specified in [`class_definitions.md`](class_definitions.md) §6. Resolve the rule first, re-annotate the affected images second, retrain third. Retraining without fixing the rule reproduces the confusion.

**If errors cluster on a lighting or environmental condition**
Indoor low-light, direct sun, dust and wet surfaces each shift the appearance distribution. Add images in the failing condition; augmentation alone cannot invent a condition absent from the data.

**If errors cluster on boundary cases**
This is the good outcome — it means the boundary cases are doing their job. Add more negatives of the specific confuser, and consider whether the class definition needs a new explicit exclusion.

---

## 6. What we are not claiming

- This analysis covers six cases out of `__` validation instances. It is a **directed sample**, chosen to be informative, not a random one. It identifies failure *modes*; it does not quantify their frequency.
- Confidence values are model outputs, not calibrated probabilities. A detection at 0.9 is not "90% likely to be correct".
- The improvements in §4 are hypotheses about what will help. None has been tested yet. Testing them is the next iteration, not this one.
