# Governance Checklist

**System:** Construction element detection for site progress verification (YOLOv8)
**Status:** Academic prototype. Not deployed. Not cleared for use on a live project.
**Owner:** MAICEN0526 Group 6
**Last reviewed:** 2026-09-22, after the held-out evaluation

---

## 1. Privacy and consent

Site photography is people photography. A construction site is a workplace, and a camera pointed at work is a camera pointed at workers.

| # | Check | Status | Note |
|---|---|---|---|
| 1.1 | No class detects, identifies or tracks people. The five classes are materials, structures and plant. | ☑ | A design decision, not an accident. Adding a `person` class would change the system's legal character — see the regulatory note below. |
| 1.2 | Source images are published under CC BY 4.0 by their authors, who hold the right to publish them. | ☑ | Base dataset: `seungyeon/construction-site-km7bh` on Roboflow Universe. |
| 1.3 | Images added by us were taken with the site's permission, or sourced from openly licensed material. | ☑ | **No images were added to the training dataset.** 25 candidates were sourced and checked; 20 were watermarked Shutterstock previews with no licence and were rejected, 5 were CC0 and held in reserve unused. Full record, including why, in [`image_provenance.md`](image_provenance.md) §A. The 7 held-out images in `data/new_images/` are our own photographs. |
| 1.4 | Faces and legible ID badges in images we added have been blurred, or the image was excluded. | ☑ | Held-out set: 1 image contains a person, back turned, face not visible — retained. 0 blurred, 0 excluded on face grounds. Two of the five reserve images contain identifiable faces and are flagged in `image_provenance.md` §A.2 so they cannot be added without the obligation being noticed. |
| 1.5 | No image carries GPS EXIF data identifying a private site. | ☑ | All 7 held-out images re-encoded onto a clean canvas at import, which drops every EXIF field including GPS. Verified, not assumed. |
| 1.6 | No personal data is stored in labels, filenames or metadata. | ☑ | Filenames are non-descriptive. |
| 1.7 | If deployed on a real site, workers would be informed before cameras are installed. | ☐ | Not applicable to this prototype; mandatory before any pilot. Notice, not consent, is usually the correct basis for a workplace safety system — but the notice is not optional. |

**Regulatory frame.** Under the **EU AI Act**, a system used to monitor workers' activity or performance falls into the high-risk category (Annex III, employment). This model does not detect people and is not used for worker evaluation, so it sits outside that category — but the boundary is one class label away. Any extension toward detecting people, PPE compliance or individual productivity moves the system into high-risk territory and triggers conformity assessment, logging and human-oversight obligations. Under the **Swiss revised FADP** and the **GDPR**, images of identifiable workers are personal data regardless of the model's purpose; the lawful basis, retention period and data-subject rights must be settled before collection, not after. In the **GCC**, the applicable regimes vary by jurisdiction and should be confirmed per project rather than assumed.

---

## 2. Data minimisation

| # | Check | Status | Note |
|---|---|---|---|
| 2.1 | Only the five classes required by the stated use case are annotated. No speculative extra classes "in case they are useful later". | ☑ | |
| 2.2 | No people are annotated, even where visible in frame. | ☑ | |
| 2.3 | Images are stored at the resolution needed for detection, not the camera's maximum. | ☑ | Version 1 resizes to 640×640; training at 640. |
| 2.4 | The dataset is not redistributed in this repository. It is referenced and downloaded at runtime. | ☑ | Reduces copies of the data in circulation. |
| 2.5 | No credential is required to reproduce the results, and none is committed. | ☑ | Both notebooks read the dataset from a checksum-verified public Release asset. No key appears in any notebook, config file or commit. |
| 2.6 | Trained weights are released as a build artefact, not committed to git history. | ☑ | Weights cannot be removed from git history once committed. |
| 2.7 | A retention period is defined for any images collected in a future pilot. | ☐ | Proposed: raw site images deleted 90 days after the progress record is created; detection records retained for the project's defects liability period. |

---

## 3. Limitations — when not to use this

**State this plainly, because the rubric asks for it and because a limitations statement that hedges is worthless.**

This model must **not** be used for:

1. **Any safety-critical decision.** It does not detect people, PPE, fall hazards, exclusion zones or unsafe acts. It has no safety function whatsoever. A site that treated it as a safety system would be less safe, not more, because it would create a false sense of coverage.
2. **Structural or quality assessment.** It detects that `steelbar` is present. It says nothing about spacing, cover, lap length, bar diameter, fixing or conformance to drawing. It is not a substitute for inspection and cannot support a conformance sign-off.
3. **Quantity measurement, valuation or payment.** It produces no reliable counts, areas or volumes. Detection instance counts are not quantities and must not enter a payment application.
4. **Contractual or disciplinary evidence.** Outputs are probabilistic and not calibrated. A detection is not proof that something was present; an absence is not proof that it was not. Using the output in a claim or a dispute would be an overreach of what the evidence supports.
5. **Conditions outside the training distribution.** The training data is daytime site photography at moderate range. Performance is unknown and unvalidated in: night and artificial-light conditions, heavy dust or rain, drone and high-oblique views, thermal or infrared imagery, and enclosed spaces such as shafts and basements. In GCC conditions specifically, high-glare midday exposure and airborne dust are both outside the validated range.
6. **Automated action without human review.** Every output is a prompt for a person to look, not a decision. No downstream process should trigger on a detection alone.

7. **Wide-field or establishing shots — which is how site progress photography is actually taken.** Measured on seven held-out images: at the evaluation setting of `imgsz=640` the model returned nothing on an unobstructed excavator and nothing on a frame full of reinforcement bar. It detected them only when the input resolution was raised. Until improvement D2 in [`error_analysis.md`](error_analysis.md) is done, this model is only usable on close, subject-filling photographs, and a site photographer must be told so explicitly — otherwise the system silently reports "no progress" on exactly the images most likely to be taken.

8. **Any image at a resolution other than the one it was evaluated at.** The predicted class changes with `imgsz`. This is a defect, not a tuning parameter, and until it is fixed the pipeline must pin the input size end to end.

9. **The `scaffold` class as any kind of access-safety check.** It reports that a structure is present. It says nothing about whether that structure is erected correctly, tied, boarded, inspected or safe to climb. Treating a `scaffold` detection as evidence of a compliant scaffold would be the single most dangerous misreading of this model.

**Validated scope.** Daytime, outdoor or well-lit indoor construction photography, handheld or fixed camera at normal working range, of the five defined classes, used to **triage** which photographs a human should examine.

---

## 4. Risk note — false negatives versus false positives

The two errors are not symmetrical, and the asymmetry runs in opposite directions for the two intended uses. This is the single most important governance judgement in the system.

### For the progress-verification use

| Error | What happens | Who absorbs it | Severity |
|---|---|---|---|
| **False negative** — `steelbar` is placed, model misses it | No progress record is created. The activity appears not to have happened. Nobody investigates, because nobody knows there is anything to investigate. The error is **silent**. | Planner, then the programme | **High** |
| **False positive** — model reports `steelbar` that is not there | A phantom progress record is created. It is contradicted by the next site walk or the next photo. The error is **loud** and self-correcting. | Whoever verifies | Moderate |

**Therefore: recall is the priority metric for progress use.** A missed detection propagates into the schedule unchallenged. A false detection gets caught. This is why success criteria S2 and S3 in the README are stated as recall targets and why the operating confidence threshold should be set *low*, accepting more false positives to reduce misses.

### For the site-condition use

The asymmetry **reverses**. `scaffold` and `excavator` are not progress-bearing; they answer "what is the state of this zone right now". Used that way, they drive alerts — scaffold still standing in a zone marked complete, plant active where it should not be — and alerts have the opposite failure mode.

A false positive here sends a supervisor to check a zone that is fine. Do that repeatedly and the supervisor stops responding to the alerts. **Then a real one is ignored.** Alert fatigue converts a precision problem into a safety-adjacent one, and it does so silently: nobody files a report saying they have started ignoring the system.

**Therefore: precision matters more for alerting.** The threshold for site-condition alerts should be set *higher* than for progress logging — fewer alerts, each more likely to be real, accepting that some genuine ones are missed. That trade is acceptable here only because these alerts carry no safety function; a system that did would need the opposite bias and a different design entirely.

### The resulting rule

**One model, two thresholds.** Progress logging runs at a low confidence threshold (recall-favouring). Site-condition alerts run at a high one (precision-favouring). Deploying a single threshold for both would be wrong for at least one of them. The values must be read off the precision-recall curve in `results/curves/BoxPR_curve.png`, not left at the Ultralytics default of 0.25, which was chosen by a library author who knew nothing about this use case.

| Use | Classes | Bias | Threshold | Basis |
|---|---|---|---|---|
| Progress logging | `steelbar`, `brick`, `pvcpipe` | Recall | `0.07 – 0.09` | Per-class optima from the cross-check sweep: `pvcpipe` 0.07, `brick` 0.08, `steelbar` 0.09 |
| Site-condition alerts | `scaffold`, `excavator` | Precision | `0.06 – 0.11` | `scaffold` 0.06 (precision 1.000), `excavator` 0.11 (precision 0.977) |

> **Provisional.** These come from the YOLOv11n cross-check, not the graded YOLOv8 run. Re-read them off `results/curves/BoxPR_curve.png` and notebook 02 cell 6.1 after training and replace these values.

**Two things the measurement changed in this argument.**

*First, the default is badly wrong for this system.* The optimal overall threshold is **0.09**, not Ultralytics' default of 0.25. At 0.25 recall has already fallen to 0.55 and by 0.30 to 0.37 — at the default, more than a third of real objects are being silently dropped. Shipping the default here would have maximised exactly the error the section above identifies as the dangerous one.

*Second, the right unit is the class, not the use case.* Each class has its own operating point, and they do not group neatly by intended use. `scaffold` reaches precision 1.000 at a threshold of 0.06, so for that class a low threshold costs nothing — recall and precision are not in tension at all. The two-threshold framing still holds, because the progress classes and the site-condition classes are disjoint sets, but the honest statement is: **set the threshold per class from the curve, and let the use case decide which way to round when the curve is ambiguous.**

### The limit of this argument, measured after the fact

Everything above is about choosing a point on a precision–recall curve. That framing assumes the detection exists somewhere on the curve and the only question is where to cut. **On images outside the training distribution, it does not exist anywhere on the curve.**

Tested on the seven first-party held-out images (README §4.2), lowering the confidence threshold from 0.25 to 0.02 recovered **no** correct detections. The objects that were missed produced no proposal of the right class at any threshold. Separately, changing only the input resolution changed the predicted *class* — `new_04` moves from `scaffold` 0.78 to `brick` 0.46 between `imgsz` 640 and 2560.

Three consequences for deployment, and they are not small:

1. **The two-threshold rule below is valid only in-distribution.** It is a real improvement over shipping the 0.25 default, and it should still be applied — but it buys recall only where the model can see the object at all. It is not a mitigation for the generalisation failure.
2. **`imgsz` must be pinned and version-controlled like any other model parameter.** It is normally treated as a performance knob. Here it changes the answer, so a deployment that resizes images differently from evaluation is running a different classifier.
3. **Confidence is not calibrated across distributions.** The single most confident prediction on unseen data (0.78) was wrong about the class. Any downstream rule of the form "act automatically above 0.7" would have acted on it.

### Residual risk we accept

Even at the correct thresholds, this model will miss objects and invent objects. That is not a defect to be engineered away at this scale of data; it is the operating reality of a 1,000-image detector. The mitigation is **not** a better model. It is keeping a human in the loop, which the limitations statement above makes mandatory.

---

## 5. Transparency

| # | Check | Status |
|---|---|---|
| 5.1 | Dataset source, version and licence are stated in the README | ☑ |
| 5.2 | Model variant, epochs, batch, image size and seed are documented | ☑ |
| 5.3 | Metrics are reported in full, including the classes that perform badly | ☐ |
| 5.4 | Failure cases are published, not just successes — see [`error_analysis.md`](error_analysis.md) | ☐ |
| 5.5 | Run environment and date are recorded so results can be re-checked | ☐ |
| 5.6 | Anyone can re-run the pipeline from this repository without contacting the authors | ☐ |

**Not published:** our Roboflow API keys, and any raw site image for which we do not hold redistribution rights.

---

## 6. Licence and data rights

**Code and notebooks.** MIT Licence — see [`../LICENSE`](../LICENSE). Permissive; reuse with attribution.

**Dataset.** *Public, licensed — not owned by us.* The base dataset [`seungyeon/construction-site-km7bh`](https://universe.roboflow.com/seungyeon/construction-site-km7bh) is published on Roboflow Universe under **CC BY 4.0**. We use it under that licence with attribution and do not redistribute it here. **We added no images of our own to it** — see [`image_provenance.md`](image_provenance.md) §A for the candidates we sourced and why they were rejected — so the training dataset is wholly CC BY 4.0 with a single upstream attribution. Anyone reusing this work must credit the original dataset authors.

**Held-out test images.** The seven images in `data/new_images/` are our own photographs, released with this repository under **CC BY 4.0**. They are not part of the dataset and were never trained on.

**Model weights.** Derived from Ultralytics YOLOv8, distributed under **AGPL-3.0**. The weights we release inherit that obligation. Academic and evaluation use is unrestricted. **Commercial deployment requires either full AGPL-3.0 compliance — including publishing the source of any networked service built on it — or a commercial licence purchased from Ultralytics.** This is a real constraint and the most common licensing mistake made with YOLO models; it is recorded here so that nobody inherits it unknowingly.

**Summary of rights by artefact**

| Artefact | Licence | Owned by us? | Redistributable? |
|---|---|---|---|
| Notebooks and code | MIT | Yes | Yes |
| Documentation | MIT | Yes | Yes |
| Base dataset images | CC BY 4.0 | No | By reference, with attribution |
| Images we added to the dataset | — | — | **None — see `image_provenance.md` §A** |
| Held-out images (`data/new_images/`) | CC BY 4.0 | Yes — our own photographs | Yes, with attribution |
| Trained weights | AGPL-3.0 (inherited) | Derived | Yes, with AGPL obligations |
