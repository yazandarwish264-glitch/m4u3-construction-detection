# Class Definitions

**The contract.** These are the written rules governing every label in this dataset. They exist because without them, annotation drifts between people and the model learns the drift rather than the object.

**The swap test:** could a person who has never met this team annotate 25 images consistently using only this document? If not, the document is not finished.

Five classes. Class names and IDs are inherited from the source dataset and **must not be reordered** — the trained weights depend on the ordering.

| ID | Class | Training instances | Share |
|---|---|---|---|
| 0 | `brick` | 140 | 13.5% |
| 1 | `excavator` | 258 | 24.9% |
| 2 | `pvcpipe` | 172 | 16.6% |
| 3 | `scaffold` | 181 | 17.5% |
| 4 | `steelbar` | 284 | 27.4% |

*Instance counts from the full 700-image project at version 1. Note `brick` is the weakest class at 13.5% of instances — expect it to underperform, and expect that to be a data fact rather than a model fact.*

### Why these five, and what each one signals

The model is a progress and site-condition sensor, not an object catalogue. Each class earns its place by mapping to something a planner or engineer would want recorded.

| Class | Signal it carries | Reporting use |
|---|---|---|
| `steelbar` | Reinforcement activity in a zone | Structural progress |
| `brick` | Masonry and blockwork activity | Envelope and partition progress |
| `pvcpipe` | Services installation | MEP first-fix progress |
| `scaffold` | Temporary works in place | Access status; zone not yet complete |
| `excavator` | Plant present and working | Earthworks activity, plant utilisation |

---

## 0 — `brick`

**Definition.** Fired clay brick or concrete masonry block — discrete modular units used to build walls.

**Annotate when the object is:**

- Bricks or blocks on a pallet, banded or loose
- Stacked or piled on the deck or ground
- Laid in a wall, complete or in progress
- Broken or half units in a cutting area, **if still recognisable as units**

**Do not annotate:**

- Cast in-situ concrete surfaces
- Stone cladding, natural stone, dressed masonry
- Paving blocks and kerbs laid horizontally as a ground surface
- Rubble where individual units are no longer distinguishable

**Box rule.** One box per stack, pallet or contiguous wall area. Not one box per brick.

| Hard case | Ruling |
|---|---|
| Blockwork wall with render half applied | Annotate the exposed blockwork only |
| Brick-effect cladding panel | Do not annotate. Not a masonry unit |
| A pile of broken blocks | Annotate if units are still countable; otherwise skip |

---

## 1 — `excavator`

**Definition.** Tracked or wheeled excavating plant — the machine, taken as a whole.

**Annotate when the object is:**

- An excavator, working or parked, tracked or wheeled
- A backhoe or mini-excavator
- The machine partially occluded by spoil, hoarding or another vehicle, where it is still identifiable

**Do not annotate:**

- Dump trucks, loaders, dozers, rollers, cranes, telehandlers
- Excavator attachments lying on the ground separately from a machine
- Machines so distant or so heavily occluded that the type cannot be told

**Box rule.** One box per machine, covering the whole visible machine **including the boom and bucket**. Not one box for the cab and another for the arm. If the arm extends out of frame, box to the frame edge.

| Hard case | Ruling |
|---|---|
| Two excavators overlapping in the frame | Two boxes, each to that machine's visible extent |
| An excavator inside a trench, only the cab and boom showing | Annotate the visible extent |
| A wheeled loader | Do not annotate. Not an excavator |

---

## 2 — `pvcpipe`

**Definition.** Plastic pipe, conduit and duct — generally PVC, in white, grey, orange or blue.

**Annotate when the object is:**

- Pipe stacked, bundled or loose
- Conduit installed in walls, slabs or ceilings
- Drainage pipe in trenches or risers
- Fittings and bends where clearly part of a plastic pipe run

**Do not annotate:**

- Metal pipe, copper, galvanised steel conduit
- HVAC ducting, flexible or rigid
- Cable tray and basket
- Hose. Hose is not pipe, even when plastic

**Box rule.** One box per bundle, or per continuous visible run. A run interrupted by a wall is two boxes, one either side.

| Hard case | Ruling |
|---|---|
| White pipe, material ambiguous under dust | Annotate if form and joint detail read as plastic. Record the image as a boundary case |
| Pipe already buried, only the end visible | Annotate the visible end |
| A neat stack of many pipes | One box for the stack, not one per pipe |

---

## 3 — `scaffold`

**Definition.** Erected scaffolding and access structure — tube-and-fitting, system scaffold, or mobile tower, **as erected**.

**Annotate when the object is:**

- An erected scaffold bay, run or tower
- Scaffold against a facade, in a shaft, or free-standing
- A mobile access tower

**Do not annotate:**

- Loose scaffold tube, boards or fittings stacked on the ground — that is material, not an erected structure, and it is not `steelbar` either
- Permanent handrail, balustrade or guardrail
- Formwork and falsework
- Ladders standing alone
- Mesh fencing and hoarding

**Box rule.** One box per contiguous erected structure. A scaffold run across a whole facade is one box, not one per bay — unless separate structures are visually distinct, in which case one box each.

**The controlling distinction.** *Erected, not stacked.* This is the rule most likely to be applied inconsistently, so it is the first thing to check when explaining `scaffold` errors.

| Hard case | Ruling |
|---|---|
| Scaffold partially dismantled | Annotate if it still reads as a standing structure |
| Scaffold seen through another scaffold | One box per structure you can separate; if you cannot, one box |
| A tower crane mast | Do not annotate. Not access scaffold |

---

## 4 — `steelbar`

**Definition.** Steel reinforcement bar intended to be embedded in concrete — ribbed or plain round bar, any diameter, at any stage from delivery to cast-in.

**Annotate when the object is:**

- Loose bars on the deck or ground
- Bundled bars, strapped, as delivered
- Bent or cut bars in a fabrication area
- Tied cages, mats and mesh reinforcement in position
- Starter bars and dowels protruding from cast concrete

**Do not annotate:**

- Structural steel sections — I-beams, channels, angle, hollow section
- **Scaffold tube** — the single most likely confusion. Scaffold tube is larger diameter, smooth, and usually coupled or erected. If it is part of an erected structure it is `scaffold`; if it is loose tube on the ground it is neither class
- Mesh fencing and hoarding frame
- Reinforcement fully buried in cast concrete and not visible

**Box rule.** One box per **visually separable group**, not per bar. A strapped bundle is one box. A tied mat is one box. Two bundles lying apart are two boxes. Where bars overlap so a human cannot say where one group ends and the next begins, treat it as one box.

| Hard case | Ruling |
|---|---|
| Bundle half-covered by a tarpaulin | Annotate the visible portion only |
| Rebar behind a mesh fence | Annotate if identifiable; the fence itself is not annotated |
| Rebar at distance, under ~20 px | Skip. Too small to label reliably |
| Rusted bar | Annotate. Rust is not a disqualifier |

---

## 5 — Conventions that apply to every class

1. **Occlusion.** Annotate the visible extent only. Never extrapolate a box over the part you cannot see. If less than roughly 25% of the object is visible, skip it.
2. **Truncation at the frame edge.** Annotate up to the edge. Do not skip a truncated object.
3. **Tight boxes.** The box touches the outermost visible pixels and contains no more background than necessary.
4. **Blur and motion.** Annotate if a human can still name the class confidently. If you hesitate, skip.
5. **Near-identical frames.** Both are annotated. Do not assume the model sees them as one image.
6. **Minimum size.** Skip objects under about 20 × 20 pixels at the annotated resolution. Below that the label is noise and harms training more than it helps.
7. **When in doubt, do not label.** A missing label costs recall. A wrong label costs recall *and* precision, and corrupts the class boundary for every future image.

---

## 6 — Known ambiguities we have accepted

Recorded rather than resolved, because resolving them needs a decision the images alone cannot supply. **This is the first place to look when explaining model errors.**

| Ambiguity | Why it is unresolved | Error we expect |
|---|---|---|
| `steelbar` vs `scaffold` tube | Both are orthogonal steel members; diameter and coupling are the only cues, and both are lost at distance | Confusion between classes 4 and 3 in the confusion matrix |
| Loose scaffold tube belongs to neither class | Our rules exclude it from both, so the model sees near-identical objects labelled and unlabelled across images | Inconsistent recall on `scaffold`, and false positives on `steelbar` |
| `brick` stack vs rubble pile | The boundary is a judgement about whether units remain countable | Missed `brick` instances on degraded stacks |
| `pvcpipe` vs metal conduit under dust | Colour, the main cue, is unreliable when dusty | False positives on class 2 |
| Group boxes vs individual boxes | The "visually separable group" rule is inherently subjective | Inconsistent instance counts, depressing recall |
| `excavator` vs other tracked plant | Dozers and loaders share silhouette features at distance | False positives on class 1 |

---

## 7 — Review record

| Version | Date | Change | Reviewed by |
|---|---|---|---|
| 1.0 | 2026-09-21 | Rules drafted against the forked dataset's five classes | `____` |
| 1.1 | `____-__-__` | §6 extended after the first annotation round | `____` |

**Swap test result:** `____` — *record it: two annotators labelled the same 10 held-out images using only this document; agreement was __%. Disagreements were on __.*

---

## 8 — Inherited annotations

**Be honest about this in the defence.** 700 of the images in this dataset were annotated by the original authors of [`seungyeon/construction-site-km7bh`](https://universe.roboflow.com/seungyeon/construction-site-km7bh), **before this document existed**. We did not re-annotate them.

That means:

- The rules above describe the schema we *adopted* and the rules we apply to images **we** add. They are not guaranteed to describe how the inherited 700 were labelled.
- Any systematic disagreement between this document and the inherited labels will surface as model error — most likely on the `steelbar` / `scaffold` boundary, where our rules are strict and the source's intent is unknown.
- Checking a sample of inherited labels against this contract is a cheap, high-value exercise, and any disagreement found belongs in [`error_analysis.md`](error_analysis.md) as a **data** finding rather than a model one.

This is the annotation-drift problem the contract exists to prevent, appearing in its most common real-world form: inheriting someone else's labels.
