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

## B — Held-out images (target: 5)

These go in `data/new_images/`. They are **never** uploaded to Roboflow and never trained on. Since the validation split is known to leak (README §4.1), these are the only unbiased evidence in the project.

| # | Filename | What is in it | Conditions | What we expect | Source | Licence | URL |
|---|---|---|---|---|---|---|---|
| 1 | `new_01.jpg` | | | | | | |
| 2 | `new_02.jpg` | | | | | | |
| 3 | `new_03.jpg` | | | | | | |
| 4 | `new_04.jpg` | | | | | | |
| 5 | `new_05.jpg` | | | | | | |

---

## Before uploading — three checks

1. **Strip EXIF.** Right-click → Properties → Details → *Remove Properties and Personal Information*. Governance check 1.5. Stock images usually carry camera and sometimes location metadata.
2. **No identifiable faces or legible ID badges.** Governance check 1.4. Blur or discard.
3. **No near-duplicates.** Photographers upload bursts of the same scene. Two near-identical images landing on opposite sides of the split is exactly the defect documented in README §4.1 — do not reproduce it. If two images look like the same shoot, keep one.

---

## Limitation, stated plainly

All added images were **sourced from stock photography libraries**, not photographed on site by us. Two consequences we accept and record rather than gloss:

- **They are not GCC site imagery.** The stated use case is Gulf construction; stock libraries are dominated by European and North American sites. Lighting, dust, plant types and construction methods differ. Performance on an actual Omani or Kuwaiti site remains unmeasured.
- **Stock photography is systematically unrepresentative.** It is well-lit, well-composed, and shot by photographers choosing attractive subjects. Real site photography is none of those things. A model validated on stock images will look better than it is.

This is a resource constraint, not a methodological choice, and it bounds every claim in this repository. The honest summary: **this project demonstrates a working, reproducible pipeline. It does not demonstrate a model ready for a Gulf site**, and the difference is the images.
