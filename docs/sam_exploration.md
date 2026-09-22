# Foundation-Model Exploration — What Helped and What Did Not

Required by the assignment brief ("Notes from SAM exploration — what helped / what failed") and by the unit's third key concept: *understanding when automation helps versus when manual QA is essential.*

| | |
|---|---|
| Models tested | **SAM 3** (`sam3-rle`) and **GPT-6 Astra** (`gpt-6-astra-boxes`), both via Roboflow hosted auto-label |
| Run on | The 7 first-party held-out images, plus dataset images from the validation split |
| Date | 2026-09-22 |
| Prompt ontology | `rebar → steelbar`, `brick wall → brick`, `pvc pipe → pvcpipe`, `scaffolding → scaffold`, `excavator → excavator` |
| Confidence threshold | 0.30 for SAM 3. Astra reports fixed confidence and has no threshold |
| Evidence | [`../results/evidence/new_images/foundation_model_comparison.png`](../results/evidence/new_images/foundation_model_comparison.png) |

**What we set out to test, and what we actually found.** The plan was the usual one: does click-to-segment beat drag-a-box for annotation speed? We ended up measuring something more useful, because the held-out evaluation had just shown our trained model failing on our own photographs. The obvious question became: **do the foundation models fail on the same images?**

They do not. That is the finding, and it is uncomfortable.

---

## 1. Why a segmentation model at all

Our task is **object detection** — axis-aligned boxes — not segmentation. SAM produces masks. So SAM was never going to produce our labels directly. It was used for one job:

**Prompt with a class noun → model returns a region → take its bounding box → accept, adjust or reject.**

The hypothesis was that prompting once is faster than dragging, and that a mask-derived box is tighter and more consistent than a hand-drawn one.

---

## 2. The comparison that matters

The same seven held-out images, three models, no training on any of them for the two foundation models.

| Image | What is actually in it | Our YOLOv8s (conf 0.25) | SAM 3 (conf 0.30) |
|---|---|---|---|
| `new_01` | `steelbar`, many column cages | **nothing** | 3 × `excavator` — plant found, rebar missed |
| `new_02` | `steelbar`, plant, clutter | `steelbar` 0.25 (one box) | 3 × `excavator` — rebar missed |
| `new_03` | `excavator` | **nothing** | **`excavator` 0.90** + 2 weak `brick` |
| `new_04` | `brick` wall and stacks, `steelbar` starters | **`scaffold` 0.78** (wrong) | **3 × `brick`** up to 0.91 — right class |
| `new_05` | `pvcpipe` conduit run | **`scaffold` 0.28** (wrong) | **23 × `pvcpipe`** — right class |
| `new_06` | `scaffold` shoring, distant | **nothing** | 21 detections incl. 2 × `scaffold`, 1 × `excavator` |
| `new_07` | `steelbar`, dense stacks | **nothing** | **4 × `steelbar`** + 1 × `scaffold` |

**Score on the target class: our fine-tuned model 1 of 7. SAM 3, 5 of 7. Neither found `steelbar` in `new_01` or `new_02`.**

GPT-6 Astra was then run on the two images our model got most wrong:

| Image | Our model | GPT-6 Astra |
|---|---|---|
| `new_04` | `scaffold` 0.78, one box over 90% of the frame | 7 × `steelbar` on the starter bars, 19 × `brick` on the block stacks, **zero `scaffold`** |
| `new_01` | nothing | 11 × `steelbar` across the column cages, 2 × `excavator`, 2 × `scaffold`, 9 × `brick` |

See the rendered boxes in [`foundation_model_comparison.png`](../results/evidence/new_images/foundation_model_comparison.png). Astra placed boxes on the individual starter bars and on individual blocks — geometry a person would accept.

**The honest reading.** A model that has never seen this dataset outperforms our fine-tuned detector on data from outside the training distribution. That is not a failure of fine-tuning in principle; it is what happens when you fine-tune on 700 leaky, narrowly-framed images. The foundation models have seen millions of construction photographs at every scale, which is exactly the weakness [`error_analysis.md`](error_analysis.md) §3 identifies in ours.

---

## 3. Where automation helped

| Situation | What we observed | Why |
|---|---|---|
| Isolated, high-contrast objects | `new_03`: SAM 3 returned `excavator` at **0.90** — the single highest-confidence correct call anywhere in this evaluation, on an image our model returned nothing for | One object, clear silhouette, contrasting background. This is the case SAM was built for |
| Class assignment on look-alikes | `new_04` and `new_05`: both foundation models got the class right where ours produced confident nonsense | Language grounding. "Brick wall" and "scaffolding" are distinct concepts to a model trained on text-image pairs; to ours they are two similar textures |
| Finding what the eye skipped | `new_07`: SAM 3 flagged rebar stacks we had ourselves catalogued as "few or none of our classes" | Exhaustive prompting does not get bored. See the correction in [`image_provenance.md`](image_provenance.md) §B |
| Box tightness | Astra's boxes on `new_04` sit on individual bars and blocks with no human slack | A derived box has no drag error in it |

---

## 4. Where automation failed

This section matters more. The unit asks specifically when automation stops helping.

| Situation | What we observed | Why it fails |
|---|---|---|
| **Group boxes — the deepest mismatch** | `new_05`: SAM 3 returned **23 separate `pvcpipe`** instances. Our contract says *one box per visually separable group*, which would make this 1–3 boxes. Astra did the same on `new_04`: **19 `brick`** where our rule wants 3 or 4 stacks | The models segment what is *visually* separable. Our contract labels what is *semantically* grouped. No prompt fixes this — it is a difference of definition, not of accuracy |
| **Thin objects at wide field** | `new_01` and `new_02`: SAM 3 found **zero `steelbar`** in frames full of it, the same miss our model made | Not purely a training-data artefact, then. Slender repeated objects at distance are hard for everything, which sharpens improvement D2: the fix is capture distance and inference tiling, not just more data |
| **Confidence is not comparable** | Astra reports fixed confidence 1.0 on every detection. SAM 3's correct `scaffold` calls on `new_06` were its *lowest*-confidence outputs (0.30, 0.32), below several of its wrong ones | You cannot triage a foundation model's output by confidence. Every box needs a human, which removes most of the hoped-for saving |
| **Noise on complex scenes** | `new_06`: 21 detections including 3 `pvcpipe` that are not there, on a site photograph with no visible pipe | Open-vocabulary prompting will find something for every class you ask about. Asking about five classes guarantees five classes of false positive |
| **Class coverage still differs** | On `new_04` Astra boxed the loose blocks as `brick` but not the built wall. Our contract covers both | Getting the class *name* right is not the same as applying the class *definition*. The contract still has to be enforced by a person |

---

## 5. The measurement

Ten images, judged by eye against what is in them. Small, and stated as such.

| | Our YOLOv8s | SAM 3 | GPT-6 Astra |
|---|---|---|---|
| Held-out images tested | 7 | 7 | 2 |
| Target class detected | **1** | **5** | **2** |
| Confident wrong-class calls | 2 (incl. one at 0.78) | 0 | 0 |
| Images returning nothing | 4 | 0 | 0 |
| Output usable as-is against our contract | — | **0 of 7** | **0 of 2** |

The last row is the one that decides the workflow. Every foundation-model output had the right idea and the wrong granularity: correct classes, far too many instances, no grouping. Accepting them unchanged would have produced a dataset that disagrees with our own class definitions.

**Net effect: the models moved the work, they did not remove it.** Prompting is faster than drawing. Merging 23 pipe segments into the two groups our contract wants, and checking that a `pvcpipe` on a site with no pipe is discarded, is not faster than drawing — and it is the part that requires knowing the contract.

---

## 6. The conclusion

**Automation handles the geometry and the vocabulary. It does not handle the contract.**

Every decision [`class_definitions.md`](class_definitions.md) exists to settle — is this one bundle or nine bars, is that stack stock or waste, does the built wall count as `brick` as well as the loose blocks — is a decision neither model makes or attempts. The annotation bottleneck in an AECO dataset is not drawing boxes. It is agreeing what the boxes mean, and then applying that agreement consistently across a thousand images.

**Practical rule adopted:** use a foundation model for the first pass and for class assignment, merge to our grouping rule by hand, and keep 100% human QA. Disable it entirely for `steelbar` at wide field, where it fails the same way our own model does.

**The larger conclusion, which we did not expect to reach.** A foundation model with zero training on this dataset beat our fine-tuned detector on every out-of-distribution image we tried. That reframes the project's own improvement plan: before collecting more data and retraining (D2, D3 in [`error_analysis.md`](error_analysis.md)), the honest question is whether a 700-image fine-tune was the right architecture for this problem at all, or whether a prompted foundation model with a thin post-processing layer to enforce our grouping rule would deliver more, sooner, for a Gulf contractor.

We are not claiming it would. We are recording that the evidence we gathered points that way and that we did not test it, which is a better position than not having asked.

---

## 7. What we would try next

1. **Foundation model as pre-labeller, our model as the specialist.** Run Astra over 200 unlabelled site photographs, merge its instances to our grouping rule, correct, and retrain. This is the standard modern loop and it is cheaper than annotating from scratch.
2. **Test the prompted foundation model as the product.** Measure Astra and SAM 3 against the seven held-out images *with annotations*, so the comparison in §2 becomes mAP rather than a count. If a prompted model wins, the deliverable changes shape entirely.
3. **Move to instance segmentation.** SAM's value rises sharply when masks are the deliverable rather than an intermediate step, and the group-box mismatch in §4 disappears because grouping becomes a post-processing choice rather than a labelling one.
4. **Measure inter-annotator agreement with and without assistance.** If assisted boxes agree more closely between two people, that is a quality argument for using them even where they save no time. This is the swap test [`class_definitions.md`](class_definitions.md) §7 records as not yet performed.

---

## 8. Limits of this exploration

- **Ten images, judged by eye.** No annotations exist for the held-out set, so "correct" here means a person looking at the box and agreeing. This identifies behaviour; it does not measure accuracy.
- **One prompt set, one threshold.** Prompt wording materially changes SAM 3's output, and we did not sweep it. `rebar` was used for `steelbar`; a different noun phrase might have recovered the `new_01` miss.
- **No timing study.** The original plan was to time manual against assisted annotation. We did not run it, so no speed claim is made anywhere above — only claims about what the output contains.
- **Foundation models are not free.** Both cost credits per image at scale, and Astra runs on metered tokens. A cost comparison against annotation labour was not done and would decide the recommendation in §7.1 in practice.
