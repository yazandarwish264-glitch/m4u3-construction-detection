# Error Analysis and Iteration Plan

Two evaluations, deliberately kept apart because they say different things.

| | |
|---|---|
| Run date | **2026-09-21**, 22:37 UTC |
| Notebook | `notebooks/02_baseline_inference.ipynb`, Colab T4 |
| Weights | `best.pt`, GitHub Release v1.0, SHA-256 `1c6bed77…d19e13` |
| Validation sample | 10 images drawn with `SEED=0` from the 140-image v1 validation split |
| Held-out sample | all 7 first-party images in `data/new_images/` |
| Inference settings | conf `0.25`, IoU `0.45`, `imgsz=640` — Ultralytics defaults |
| Classes | `brick`, `excavator`, `pvcpipe`, `scaffold`, `steelbar` |

**Read this before the cases below.** The validation split leaks (README §4.1), so validation numbers measure memorisation as much as detection. The seven held-out images do not leak. Where the two disagree, the held-out set is the one to believe — and they disagree completely.

| | Validation (10 images) | Held-out (7 images) |
|---|---|---|
| Images where prediction matched truth | **8 of 10** | **1 of 7** (and that one marginally) |
| Wrong-class detections | 0 | 2, one at confidence 0.78 |
| Images with no detection at all | 0 | 4 |

That gap is the single most important result in this repository. Everything below is an attempt to explain it.

**One caveat stated up front.** The held-out images are **not annotated**. There is no label file to compute IoU against, so "false negative" below means *a human looking at the image can see the object and the model returned nothing*. That is weaker than a measured recall figure and it is why §6 limits what we claim.

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

---

## 1. False positives — the model saw something that is not there

A false positive produces a **phantom record**: a report says blockwork started on level 3 when it has not, or says scaffold is still standing in a zone that was struck last week. The cost is a wasted verification trip and, repeated, a loss of trust in the tool.

### FP-1 — a blockwork wall called `scaffold` at 0.78

| | |
|---|---|
| Image | `results/evidence/new_images/pred_new_04.png` |
| Predicted | `scaffold` at **0.778**, box covering ~90% of the frame |
| Actually in the box | A rendered blockwork wall, plus stacked concrete blocks and cement bags at its base |
| Correct labels | `brick` (the wall and the stacks), `steelbar` (starter bars projecting above the wall head) |

This is the highest-confidence prediction the model made on any unseen image, and it is wrong in three ways at once: wrong class, wrong extent, and it suppressed the two classes that are genuinely present.

**Hypothesis.** `brick` and `scaffold` are both, at low resolution, *a repeating orthogonal grid of light-coloured rectangles*. The features that separate them — a scaffold is an open tube frame you can see through, blockwork is a solid face — live in fine texture, and at `imgsz=640` a 480×640 photograph of a wall is resampled until that texture is gone. What survives the downsampling is the grid, and the grid says scaffold.

**Evidence for the hypothesis — this one is testable, and we tested it.** Running the *same weights* on the *same image* at the *same confidence threshold*, changing only the input resolution:

| `imgsz` | Prediction |
|---|---|
| 640 | `scaffold` 0.78 |
| 1280 | `scaffold` 0.31 |
| 2560 | **`brick` 0.46** ← correct class |

See `results/evidence/new_images/resolution_instability.png`. The class label flips when the only thing that changed was resampling. That is not a borderline case being decided differently; it is the model reading a different object.

### FP-2 — PVC conduit called `scaffold` at 0.28

| | |
|---|---|
| Image | `results/evidence/new_images/pred_new_05.png` |
| Predicted | `scaffold` at **0.279**, box covering the entire frame |
| Actually in the box | A run of white PVC electrical conduit on a concrete soffit, with a blue junction box |
| Correct label | `pvcpipe` — this is the cleanest single-class image in the held-out set |

**Hypothesis.** The same failure as FP-1, with a different geometry: long straight pale tubes running parallel and crossing at angles. A scaffold is *also* long straight pale tubes running parallel and crossing at angles. Nothing in the training data teaches the model that scale and context separate them — that a scaffold is metres across and outdoors, and a conduit run is centimetres across on a ceiling — because bounding boxes carry no scale information and the dataset has no image where both appear.

**Evidence.** Resolution changes the answer here too, and never to the right one:

| `imgsz` | Prediction |
|---|---|
| 640 | `scaffold` 0.28 |
| 1280 | `steelbar` 0.27 |
| 2560 | `steelbar` 0.57, `steelbar` 0.31 |

Three resolutions, three different answers, none of them `pvcpipe`. The model is confident about *tubular thing* and has no stable opinion about which tubular class it is.

**This is the error the rejected boundary images were meant to prevent.** Two of the five boundary cases we sourced and then rejected on licence grounds ([`image_provenance.md`](image_provenance.md) §A.1) were exactly *steel conduit vs PVC* and *loose tube vs erected scaffold*. Their absence is visible here as a measured failure, which is the most honest possible account of what that rejection cost.

### FP-3 — a third `steelbar` box where the truth has two

| | |
|---|---|
| Image | `results/evidence/validation/val_steelBar_5357k_jpg.rf.d8de9b93355f408d0e45e2f58a22b903.png` |
| Predicted | `steelbar` ×3 at 0.87, 0.64, **0.43** |
| Ground truth | `steelbar` ×2 |
| What the extra box contains | More reinforcement bar — genuinely `steelbar` material, but the annotator grouped it into an adjacent box |

**Hypothesis.** This is not a perception error. The model saw bar and called it bar. The disagreement is about **where one group ends and the next begins** — the *one box per visually separable group* rule in [`class_definitions.md`](class_definitions.md). For a tangled bundle that boundary is a judgement call, so the training targets are inconsistent between images, and the model splits where a different annotator would have merged.

**Evidence.** Finding 4 above: `steelbar` holds mAP@50 0.781 but collapses to mAP@75 0.057 on the cross-check. When the model finds bar, the box is in roughly the wrong place. A class whose localisation fails that badly while its classification holds is a labelling-convention problem, not a detection problem. The other validation false positive — a duplicate `scaffold` at 0.27 in `val_scaffold_9767j…` — has the same shape.

**Note the contrast with FP-1 and FP-2.** In-distribution, the model's false positives are *boundary disputes about objects it identified correctly*. Out of distribution, they are *confident assertions of the wrong class*. Those are different failures with different fixes, and treating them as one number is how a mAP figure hides what is actually going on.

---

## 2. False negatives — the model missed something that is there

A false negative produces **silence where there should be a record**: rebar placed but not logged, scaffold left standing but never flagged. For a progress-monitoring tool this is the more damaging error, because nobody goes looking for a record that was never created. See the risk note in [`governance_checklist.md`](governance_checklist.md) §4.

### FN-1 — a frame full of reinforcement, detected as nothing

| | |
|---|---|
| Image | `results/evidence/new_images/pred_new_01.png` |
| Missed objects | `steelbar` — many column cages and starter bars across the full width of the frame; also timber formwork and plant |
| Object condition | Daylight, sharp, unobstructed. Wide establishing shot: the individual bars are thin relative to the frame |
| Detections at conf 0.25 | **none** |
| Highest confidence at conf 0.02 | `excavator` 0.048 — the wrong class, at noise level. No `steelbar` proposal at any threshold |

**Hypothesis.** Scale. In the training data `steelbar` is overwhelmingly a close shot where bar fills the frame. Here the same object is present but each bar is a few pixels wide after the 640 resize. The model has learned `steelbar` at one apparent size and does not recognise it at another.

**Evidence.** Two independent checks, and they point the same way:

1. **Lowering the threshold does not help.** At conf 0.02 — effectively "show me everything you considered" — the model still proposes no `steelbar` anywhere in this image. The detection is not hiding below the threshold. It was never made.
2. **Raising the resolution does.** At `imgsz=1280` the model starts producing detections on this image (`excavator` 0.55, 0.28). Still the wrong class, but the pixels became legible enough to trigger proposals at all.

That distinction matters operationally: a recall problem you can fix by lowering the threshold is cheap, and this is not one.

### FN-2 — the control class, missed entirely

| | |
|---|---|
| Image | `results/evidence/new_images/pred_new_03.png` |
| Missed object | `excavator` ×1 — a tracked excavator, mid-frame, unobstructed, in an open excavation |
| Object condition | Daylight, sharp. Occupies roughly 10% of frame width in a wide urban scene |
| Detections at conf 0.25, `imgsz=640` | **none** |
| At `imgsz=1280` | `excavator` **0.52** and 0.41 — found |

**Hypothesis.** The same scale effect as FN-1, and this case is the more damning of the two because `excavator` is the class we nominated as a **control**: mAP@50 0.995 and recall **1.000** on the graded validation run. A class that misses nothing in validation and misses an unobstructed excavator on the first unseen photograph is not a class that was learned. It is a class that was memorised at one framing.

**Evidence.** The recovery at 1280 is the evidence — the object is present and detectable, it is the 640 resize that destroys it. Note also that at 1280 one of the two boxes lands on a parked van rather than the excavator, so the recovered recall arrives with a false positive attached.

### FN-3 — scaffold at distance, absent at every setting

| | |
|---|---|
| Image | `results/evidence/new_images/pred_new_06.png` |
| Missed object | `scaffold` — shoring towers on a large deck project, seen from across the site |
| Object condition | Daylight. Small in frame, partially occluded, competing structure behind |
| Detections | **none** at conf 0.25, 0.09, 0.05 **or** 0.02, at `imgsz` 640, 1280 or 1920 |
| Only result anywhere | `excavator` 0.69 at `imgsz=2560` — wrong class |

**Hypothesis.** This was designated the deliberate hard case, and it behaved as predicted — but for the predicted reason plus one more. Distance and occlusion explain part of it. The rest is that `scaffold` in training is a **close, face-on, regular tube grid**; shoring towers viewed obliquely across a site present as an irregular silhouette, which is a different object as far as the learned features are concerned.

**Evidence.** It is the only held-out image that produces nothing across the entire threshold *and* resolution sweep. Every other failure recovered something at some setting. This one has no recoverable signal at all, which separates it from FN-1 and FN-2: those are resize artefacts, this is a genuine appearance gap in the training distribution.

---

## 3. Error pattern summary

**The model has not learned five object classes. It has learned five image textures at the scale and framing of the training set.**

The evidence is that predictions are unstable under a change that carries no semantic content. Holding the weights, the image and the confidence threshold fixed and varying only `imgsz`, `new_04` moves `scaffold` 0.78 → `scaffold` 0.31 → `brick` 0.46, and `new_05` moves `scaffold` → `steelbar` → `steelbar`. A model that had learned what blockwork *is* would not change its mind about it when the image is resampled. One that has learned a spatial-frequency signature would, and does.

That single explanation covers all six cases:

- **FP-1, FP-2** — at low resolution, distinct objects collapse onto the same texture signature: repeating rectangles → `scaffold`, parallel pale tubes → `scaffold`.
- **FN-1, FN-2** — at low resolution, real objects fall below the signature's scale and produce no proposal at all, not even at conf 0.02.
- **FN-3** — an appearance genuinely outside the training distribution, which no resampling recovers.
- **FP-3** — the one error that is *not* about scale: an annotation-convention dispute, which is why it is also the only one that appears inside the validation split.

**A fourth miss, found while cataloguing.** `new_07` was first logged as containing few or none of our classes. Looking at it properly, it is dominated by stacked reinforcement mesh — unambiguous `steelbar` under our contract, at mid range, in daylight. The model returns **nothing** on it at thresholds from 0.25 down to 0.02 and at every resolution from 640 to 2560. It belongs with FN-1 and FN-2, not with the probes, and the register has been corrected ([`image_provenance.md`](image_provenance.md) §B). It is worth stating plainly: a human skim made the same mistake the model did, which is a reminder that "obviously present" is a judgement, and that the honest way to hold an unannotated test set is to look at every image rather than trusting the note you wrote about it.

And it explains the 8-of-10 versus 1-of-7 gap in the header. Validation images come from the same shoots as training images, at the same framing and the same apparent object size, with near-duplicates on both sides of the split. They match the learned signature by construction. Our own photographs do not, and performance collapses.

**The uncomfortable corollary.** The reported mAP@50 of 0.943 does not describe how this model behaves on a construction site. It describes how it behaves on the remainder of one scraped dataset. We have no measurement that would have revealed this, because the only unbiased data in the project is the seven images in §1–2 — which is why they exist.

---

## 4. Three prioritised data improvements

Each names a **specific gap**, a **specific action**, and the **metric it should move**. Ordered by expected gain per hour.

### D1 — Split the dataset by scene group, not at random

| | |
|---|---|
| **Gap it addresses** | Every finding above. The validation split shares shoots with training (`steelBar_5397k` in train, `5398k` in valid), so validation cannot detect the failure the held-out images expose. Until this is fixed, no other improvement can be *measured*. |
| **Action** | Cluster the 700 images by perceptual hash and filename stem, treat each cluster as one unit, and assign whole clusters to train or valid 80/20. Regenerate as version 3 and retrain identically. |
| **Effort** | 2–3 hours, no new images required |
| **Metric it should move** | mAP@50 will **fall**, probably a long way — 0.943 is the number being corrected. The target is a validation figure that tracks held-out behaviour, not a higher one. |
| **How we will know it worked** | Re-run the seven held-out images. If validation mAP and held-out behaviour finally move together, the split is honest. |

**This is first on the list even though it makes the headline number worse.** Every other improvement is unverifiable without it.

### D2 — Train and infer multi-scale, and add wide-field imagery

| | |
|---|---|
| **Gap it addresses** | FP-1, FP-2, FN-1, FN-2 — the scale instability demonstrated in `resolution_instability.png`. The dataset is close, subject-filling crops; real progress photography is wide establishing shots. |
| **Action** | Two parts. (a) Collect ~100 wide-field site photographs where the target classes occupy under 15% of frame width, and annotate them. (b) Retrain with `imgsz=1024` and Ultralytics multi-scale augmentation, and evaluate tiled inference (SAHI) at 640 tiles as the deployment path. |
| **Effort** | 8–10 hours, most of it annotation |
| **Metric it should move** | Recall on `steelbar` (currently 0.612 on a leaking split) and — the real target — the held-out detection rate, currently 1 of 7 |
| **How we will know it worked** | Re-run the `imgsz` sweep. Success is predictions that **stop changing class** between 640 and 2560. Stability is the metric, not confidence. |

### D3 — Add hard negatives for the two confusions actually observed

| | |
|---|---|
| **Gap it addresses** | FP-1 and FP-2 specifically: blockwork→`scaffold` and PVC conduit→`scaffold`. Note these are *not* the confusions we predicted — we predicted `steelbar`/`scaffold`, which never once occurred (Finding 1). |
| **Action** | Source ~40 CC0 images under the licence-check-first procedure in [`image_provenance.md`](image_provenance.md): rendered and unrendered blockwork walls at range, PVC and steel conduit runs on soffits, and erected scaffold beside both. Annotate to the correct class; leave genuinely empty frames as explicit negatives. Re-instate the five boundary cases lost to the licence rejection. |
| **Effort** | 4–5 hours |
| **Metric it should move** | Precision on `scaffold`, and specifically the count of `scaffold` predictions on images containing no scaffold — currently 2 of 7 held-out images |
| **How we will know it worked** | `new_04` returns `brick` and `new_05` returns `pvcpipe` at the default `imgsz=640`, not only at 2560 |

**What is deliberately not on this list:** a bigger model. Nothing above is a capacity problem. Moving from `yolov8s` to `yolov8m` would raise the leaking validation number and change none of the seven held-out results, because the failures are in the data — its framing, its split and its missing negatives.

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

## 6. What we are not claiming

- **The held-out images are not annotated.** There is no label file, so every "false negative" above is a human judgement that an object is visibly present, not a measured IoU miss. This is a qualitative probe, not a recall figure.
- **Seven images is not a sample.** It can show that a failure mode exists. It cannot tell you how often it occurs. No claim of the form "the model detects X% on new sites" is supported here, and none is made.
- **Two effects are confounded.** The held-out images differ from the training data in framing *and* in geography, construction method and light. The resolution sweep isolates scale as one real cause; it does not prove scale is the only cause.
- **Confidence values are not probabilities.** A detection at 0.78 is not "78% likely to be correct". FP-1 is the demonstration.
- **The improvements in §4 are untested hypotheses.** D1 is the one we are most confident about, because it fixes a defect we have direct evidence of rather than predicting a gain.
- **This analysis covers 6 cases** selected to be informative across 10 validation and 7 held-out images. It is a directed sample, not a random one.
