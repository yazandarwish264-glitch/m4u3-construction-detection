# Image Provenance Register

Every image we added to the dataset, with its source and licence. This exists to close governance check 1.3 — *"images added by us were taken with the site's permission, or sourced from openly licensed material"* — with evidence rather than an assertion.

**Fill a row as you download each image.** Reconstructing provenance afterwards is slow and error-prone, and an unrecorded licence is the same as no licence.

---

## Licence names — get these right

These are not interchangeable, and calling a Pexels image "public domain" is a factual error in a document that is marked on accuracy.

| Source | Correct licence name | Attribution required? | Public domain? |
|---|---|---|---|
| [StockSnap](https://stocksnap.io) | CC0 1.0 | No | **Yes** |
| [Piqsels](https://www.piqsels.com) | CC0 1.0 | No | **Yes** |
| [Pexels](https://www.pexels.com) | Pexels License | No | No — custom licence |
| [Unsplash](https://unsplash.com) | Unsplash License | No | No — custom licence |
| [Pixabay](https://pixabay.com) | Pixabay Content License | No | No — custom licence |

CC0 sources are cleanest. Prefer them where the image quality is adequate.

---

## A — Dataset images (target: 25)

These are uploaded to Roboflow, annotated, and trained on.

| # | Filename | Class(es) present | Source site | Licence | URL | Date |
|---|---|---|---|---|---|---|
| 1 | `add_01.jpg` | | | | | |
| 2 | `add_02.jpg` | | | | | |
| 3 | `add_03.jpg` | | | | | |
| 4 | `add_04.jpg` | | | | | |
| 5 | `add_05.jpg` | | | | | |
| 6 | `add_06.jpg` | | | | | |
| 7 | `add_07.jpg` | | | | | |
| 8 | `add_08.jpg` | | | | | |
| 9 | `add_09.jpg` | | | | | |
| 10 | `add_10.jpg` | | | | | |
| 11 | `add_11.jpg` | | | | | |
| 12 | `add_12.jpg` | | | | | |
| 13 | `add_13.jpg` | | | | | |
| 14 | `add_14.jpg` | | | | | |
| 15 | `add_15.jpg` | | | | | |
| 16 | `add_16.jpg` | | | | | |
| 17 | `add_17.jpg` | | | | | |
| 18 | `add_18.jpg` | | | | | |
| 19 | `add_19.jpg` | | | | | |
| 20 | `add_20.jpg` | | | | | |

### Boundary cases — the five that matter

Each one tests a specific rule in [`class_definitions.md`](class_definitions.md). These are the images that demonstrate we understand our own class contract, so record precisely *why* each was chosen.

| # | Filename | Looks like | Actually is | Rule it tests | Source | Licence | URL |
|---|---|---|---|---|---|---|---|
| 21 | `bound_01.jpg` | `steelbar` | Loose scaffold tube on the ground | Belongs to **neither** class — the hardest rule we wrote | | | |
| 22 | `bound_02.jpg` | `scaffold` | Ladder / guardrail / hoarding frame | "Erected access structure", not any vertical frame | | | |
| 23 | `bound_03.jpg` | `brick` | Stone cladding or paving block | Material versus form | | | |
| 24 | `bound_04.jpg` | `pvcpipe` | Galvanised steel conduit | Material identification when colour is unreliable | | | |
| 25 | `bound_05.jpg` | `excavator` | Wheel loader or dozer | Machine type, not "yellow plant" | | | |

---

## B — Held-out images

**Seven images, all photographed by us.** These live in `data/new_images/`, are never uploaded to Roboflow, and are never trained on. Because the validation split leaks (README §4.1), these are the only unbiased evidence in the project.

The brief asks for five. We use seven because unbiased test images are the scarcest thing here and three extra cost nothing.

| File | Location | What is in it | Classes | Role |
|---|---|---|---|---|
| `new_01.jpg` | `____` | Core wall under construction, rebar starters, timber formwork | `steelbar` | The weakest class, clear conditions |
| `new_02.jpg` | `____` | Retaining wall, rebar starters, concrete pump boom, stacked timber | `steelbar`, plant | Weak class under clutter |
| `new_03.jpg` | `____` | Excavation with tracked excavator, surrounding buildings | `excavator` | **Control** |
| `new_04.jpg` | **Irbid, Jordan** | Blockwork wall with rebar starters, stacked concrete blocks | `brick`, `steelbar` | **Control** — taken while building our own home |
| `new_05.jpg` | **Irbid, Jordan** | PVC conduit run on a concrete soffit with junction box | `pvcpipe` | Only close-range MEP image — taken while building our own home |
| `new_06.jpg` | `____` | Large deck project, shoring and tower crane, distant | `scaffold` | **Hard case** — small objects at range |
| `new_07.jpg` | `____` | Formwork panels and timber stacks beside a building | few / none | **Hard case** — mostly objects outside our schema |

> **TODO:** fill the remaining `____` location cells. The set spans Amman, Irbid, Nashville and New York — record which is which.

**Held back, not committed:**

| Image | Why |
|---|---|
| Manhattan street scene | Contains none of the five classes. Retained as an optional false-positive probe: does a stone facade trigger `brick`? |
| Two further views of the `new_06` site | Near-duplicates of `new_06` by visual inspection and perceptual hash (distances 28–35). Using all three would inflate the evidence the same way the validation leak does |

### Provenance and handling

- **All seven photographed by us.** No stock imagery in the held-out set.
- **EXIF stripped from all seven** at import (re-encoded onto a clean canvas). Governance check 1.5.
- **Renamed** to `new_01`–`new_07` so no filename carries incidental metadata.
- One image contains a person, back turned, face not visible. Retained under check 1.4; flag for review if the group disagrees.

### What this set does and does not establish

**Does:** it spans **four cities on two continents** — Amman, Irbid, Nashville and New York. That is a harder generalisation test than a single site, because it varies construction method, materials, plant and light all at once. Two of the seven are from the authors' own house build in Irbid, which is about as unambiguous as provenance gets.

**Does not:** seven images is a qualitative probe, not a statistical estimate. It can show that a class fails on unseen data; it cannot tell you how often. Any claim of the form "the model achieves X on new sites" is unsupported by a set this size.

## Before uploading — three checks

1. **Strip EXIF.** Right-click → Properties → Details → *Remove Properties and Personal Information*. Governance check 1.5. Stock images usually carry camera and sometimes location metadata.
2. **No identifiable faces or legible ID badges.** Governance check 1.4. Blur or discard.
3. **No near-duplicates.** Photographers upload bursts of the same scene. Two near-identical images landing on opposite sides of the split is exactly the defect documented in README §4.1 — do not reproduce it. If two images look like the same shoot, keep one.

---

## Limitation, stated plainly

The **25 dataset images** were sourced from stock photography libraries, not photographed on site by us. (The seven held-out images in section B are our own photographs and are not affected by this.) Two consequences we accept and record rather than gloss:

- **They are not GCC site imagery.** The stated use case is Gulf construction; stock libraries are dominated by European and North American sites. Lighting, dust, plant types and construction methods differ. Performance on an actual Omani or Kuwaiti site remains unmeasured.
- **Stock photography is systematically unrepresentative.** It is well-lit, well-composed, and shot by photographers choosing attractive subjects. Real site photography is none of those things. A model validated on stock images will look better than it is.

This is a resource constraint, not a methodological choice, and it bounds every claim in this repository. The honest summary: **this project demonstrates a working, reproducible pipeline. It does not demonstrate a model ready for a Gulf site**, and the difference is the images.
