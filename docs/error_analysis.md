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
