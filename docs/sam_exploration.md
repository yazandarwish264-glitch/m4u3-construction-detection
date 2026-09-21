# SAM Exploration — What Helped and What Did Not

Required by the assignment brief ("Notes from SAM exploration — what helped / what failed") and by the unit's third key concept: *understanding when automation helps versus when manual QA is essential.*

| | |
|---|---|
| Tool used | Roboflow's SAM-assisted labelling (Smart Polygon / Label Assist) |
| Explored on | `__` images from our own added set |
| Date | `____-__-__` |
| Explored by | `____` |

> **Fill this in from your own session.** The structure below is the argument; the specific observations must be yours. Run SAM over 10–15 of your own images, keep a tally, and fill the tables. Fifteen minutes of actual use produces notes that read as experience; inventing them produces notes that read as invented.

---

## 1. What we asked SAM to do

Our task is **object detection** — axis-aligned bounding boxes — not segmentation. SAM produces masks. So SAM was never going to produce our labels directly. It was used for one specific job:

**Click an object → SAM returns a mask → take the mask's bounding box → accept, adjust or reject.**

The hypothesis was that clicking once is faster than dragging a box, and that a mask-derived box is tighter and more consistent than a hand-dragged one.

---

## 2. Where it helped

| Situation | Observation | Why |
|---|---|---|
| Large, isolated objects against a contrasting background | `__` | An `excavator` against open ground, or a single `pvcpipe` run on a clean slab, is exactly the case SAM was built for: one object, clear edges, high contrast |
| Box tightness and consistency | `__` | A mask-derived box has no human slack in it. Boxes become more uniform across annotators, which is a quality gain, not only a speed gain |
| First-pass speed on easy images | `__ s/object vs __ s/object by hand over __ objects` | Record your own timing. One click beats one drag when the click works first time |
| Finding objects we had missed | `__` | Hovering SAM over a busy image sometimes surfaces an object the annotator's eye had skipped |

---

## 3. Where it failed

This section matters more than the one above. The unit asks specifically when automation stops helping.

| Situation | Observation | Why it fails |
|---|---|---|
| **Group boxes** | `__` | Our class definitions annotate a *bundle of `steelbar`* as one box. SAM segments one bar, or one visually coherent region, and has no concept of "the group a human would call one item". This is the deepest mismatch: SAM segments what is visually separable, our contract labels what is semantically grouped. No amount of prompting fixes it |
| **Open lattice structures** | `__` | `scaffold` is mostly background seen through a grid of tube. SAM either masks one tube or floods the facade behind it. There is no single coherent region to segment |
| **Heavy occlusion** | `__` | SAM masks the visible fragment. Our rule says annotate visible extent only, so this is technically correct — but SAM then returns several small boxes where a human sees one partially hidden object |
| **Texture-similar adjacency** | `__` | A block stack against a rendered wall: SAM's boundary lands somewhere plausible but wrong, and it is wrong *consistently*, which is worse than being noisily wrong |
| **Class assignment** | Always manual | SAM has no idea what a thing *is*. Every mask still needed a human to attach a class. The labelling cost is not the geometry; it is the decision |

---

## 4. The measurement

`Record your actual numbers. Without them this document is opinion.`

| Metric | Manual | SAM-assisted |
|---|---|---|
| Images annotated | `__` | `__` |
| Objects annotated | `__` | `__` |
| Time | `__ min` | `__ min` |
| Seconds per object | `__` | `__` |
| SAM boxes accepted unchanged | — | `__%` |
| SAM boxes adjusted | — | `__%` |
| SAM boxes discarded and drawn by hand | — | `__%` |

**Net effect:** `__`

---

## 5. The conclusion

`State your own, supported by §4. The defensible shape of this conclusion, if your numbers support it:`

> SAM assistance was worth using on roughly the `__%` of our images containing large, separable, high-contrast objects, where it reduced annotation time by `__%` and produced tighter boxes than hand-drawing. It was actively counterproductive on group-boxed `steelbar` and on `scaffold`, where reviewing and correcting its output cost more than drawing the box by hand.
>
> The general finding: **SAM automates the geometry, never the judgement.** Every decision our class-definition contract exists to settle — is this one object or three, is this waste or stock, is this rebar or scaffold — is a decision SAM cannot make and does not attempt. The annotation bottleneck in an AECO dataset is not drawing boxes. It is agreeing what the boxes mean.
>
> Practical rule adopted: **use SAM for the first pass on isolated objects, disable it for group-boxed and amorphous classes, and keep 100% human QA regardless.** Automation moved the effort; it did not remove it.

---

## 6. What we would try next

1. If we moved to **instance segmentation** rather than detection, SAM's value would rise sharply — masks would become the deliverable instead of an intermediate step, and the group-box mismatch would disappear.
2. **SAM bootstrapping a first model, then the model pre-labelling the rest.** After ~200 labelled images, a rough YOLO model becomes a better label-assist than SAM, because it has learned our class boundaries and SAM never will.
3. **Measure inter-annotator agreement with and without SAM.** If SAM-assisted boxes agree more closely between annotators, that is a quality argument for using it even where it saves no time.
