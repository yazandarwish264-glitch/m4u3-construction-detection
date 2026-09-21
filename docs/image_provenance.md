# Image Provenance Register

Every image in this project that did not come from the base dataset, with its source and licence. This exists to close governance check 1.3 — *"images added by us were taken with the site's permission, or sourced from openly licensed material"* — with evidence rather than an assertion.

**Summary of what this register records:**

| Group | Count | Status |
|---|---|---|
| Base dataset images | 700 | Public, CC BY 4.0, used by reference — not ours, not redistributed |
| Candidate images sourced to expand the dataset | 25 | **20 rejected on licence grounds, 5 cleared and held in reserve. None added.** |
| Held-out test images | 7 | First-party photographs. In the repo, never trained on |

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
| **Shutterstock preview** | **No licence at all** | — | **No — see §A.1** |

CC0 sources are cleanest. Prefer them where the image quality is adequate.

---

## A — Dataset images: none were added, and here is why

The training dataset is the base Roboflow project **unchanged**: 700 images, `yazan-darwish/construction-site-km7bh-fapwu` v1. We sourced 25 candidate images intending to expand it. **Twenty failed a licence check and were rejected. The remaining five were cleared but not used.** The dataset was therefore left as it was.

This is recorded rather than quietly dropped, because a provenance register that only lists what was accepted is not evidence of anything.

### A.1 — The twenty rejected images

All twenty were **watermarked Shutterstock preview files**, identifiable by the filename pattern `stock-photo-<description>-<10-digit-id>.jpg` and confirmed by inspection: each carries the repeating `shutterstock` tile watermark, the contributor's name, and a footer bearing the image ID and `www.shutterstock.com`.

A Shutterstock preview is **not licensed for any use** — not for publication, not for redistribution, and explicitly not as training data. Three independent reasons to reject them, any one of which is sufficient:

1. **Licensing.** There is no licence. Using them would make the claim in governance check 1.3 false, and §6 of the governance checklist — which states the combined dataset is coherently CC BY 4.0 — would become a misrepresentation in a document graded on accuracy.
2. **Data quality.** The watermark is a large, high-contrast, structured overlay covering the full frame. A detector trained on these learns the watermark as much as the construction element, and because the overlay is identical across all twenty, it becomes a near-perfect shortcut feature. This is the same class of defect as the train/valid leakage documented in README §4.1 — a model scoring well for the wrong reason.
3. **Reproducibility.** Anyone re-running this pipeline could not obtain the same images legally, which breaks the one thing this repository is actually graded on.

The files are retained outside the repository, in a folder marked `_REJECTED_watermarked`, and are not uploaded to Roboflow. They are listed here by description rather than by filename because the filenames themselves are Shutterstock metadata.

| # | Subject | Intended group |
|---|---|---|
| 1 | Stacked red brick pile at a site | dataset |
| 2 | Construction worker on scaffolding, Berlin | dataset |
| 3 | Grey concrete blocks stacked in snow | dataset |
| 4 | Concrete blocks on a villa site | dataset |
| 5 | Excavator digging a trench near a house | dataset |
| 6 | Rainwater drainage pipe in a gravel lot | dataset |
| 7 | Engineer and worker at height | dataset |
| 8 | Excavator and grader levelling ground | dataset |
| 9 | Excavator levelling ground, industrial site | dataset |
| 10 | Heavy excavator during earth moving | dataset |
| 11 | Office building under construction with crane | dataset |
| 12 | Plumbing connection to sewer system | dataset |
| 13 | Reinforced concrete formwork with scaffolding | dataset |
| 14 | PVC water pipes in ground | dataset |
| 15 | Workers installing drainage pipes in a trench | dataset |
| 16 | Wheel loader carrying gravel | boundary — `excavator` vs loader |
| 17 | Metal electrical conduit on a ceiling | boundary — `pvcpipe` vs steel conduit |
| 18 | Natural stone texture, rectangular courses | boundary — `brick` vs stone cladding |
| 19 | Stacked scaffolding tubes on a truck | boundary — `scaffold` vs loose tube |
| 20 | Top view of basement stair concreting | boundary — general |

**The loss is real but small.** Items 16–20 were the five boundary cases described in [`class_definitions.md`](class_definitions.md) §6 — the images that would have demonstrated the class contract handles ambiguity. That demonstration is now made in prose in `class_definitions.md` rather than with images. Nothing in the assignment rubric depends on them.

### A.2 — The five cleared images

These passed the licence check. **They are held in reserve and have not been uploaded to Roboflow or trained on**, because adding five images to a 700-image dataset would require re-annotating, regenerating the version, retraining, and re-deriving every metric in this repository for a change too small to move any of them.

All five are **Piqsels, CC0 1.0** — public domain, no attribution required, no restriction on use as training data.

| # | File | Subject | Classes present | Note |
|---|---|---|---|---|
| 1 | `piqsels.com-id-fbdoc.jpg` | Dense rebar mesh over a slab, top-down | `steelbar` (heavy) | Directly targets the weakest class |
| 2 | `piqsels.com-id-fcbru.jpg` | Brick kiln yard, stacked bricks, handcart | `brick` (heavy) | **Four workers with visible faces — would need blurring under check 1.4 before any use** |
| 3 | `piqsels.com-id-fwmab.jpg` | Formwork panels, scaffold frames, rebar, workers | `scaffold`, `steelbar` | Faces small and mostly turned; review under check 1.4 |
| 4 | `piqsels.com-id-sfmxd.jpg` | Large excavation, rebar mats and **bundles**, formwork | `steelbar` (incl. bundled) | Would test the bundling hypothesis in README §4.1 directly |
| 5 | `piqsels.com-id-zbezp.jpg` | Timber formwork maze with rebar column cages | `steelbar` | No people in frame |

Three of the five are rebar-dominant, which is the right bias — `steelbar` is the weakest class in both architectures tried. If the dataset is ever expanded, these are the starting point, and image 4 is the single most useful of them.

**Note for check 1.4:** two of the five contain identifiable people. They are not in the repository and not in the dataset, so no obligation is currently triggered; the flag is recorded here so that a future contributor cannot add them without noticing.

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

---

## Before adding any image — three checks

The rejection in §A.1 happened because the licence check was run *before* upload rather than after. Keep that order.

1. **Licence first, and open the file to confirm it.** A filename is not a licence. Watermarked previews from paid libraries are freely downloadable and look like ordinary stock images in a folder listing — the watermark is only visible when you open them. Record the source, the exact licence name and the URL in this file at download time.
2. **Strip EXIF.** Governance check 1.5. Stock images usually carry camera and sometimes location metadata.
3. **No identifiable faces or legible ID badges, and no near-duplicates.** Checks 1.4 and README §4.1 respectively. Photographers upload bursts of the same scene; two near-identical images landing on opposite sides of the split is exactly the defect we already have once and should not reproduce.

---

## Limitation, stated plainly

The training dataset is the base Roboflow dataset alone. We added nothing to it. Three consequences we accept and record rather than gloss:

- **It is not GCC site imagery.** The stated use case is Gulf construction; the base dataset is not from the Gulf. Lighting, dust, plant types and construction methods differ. Performance on an actual Omani or Kuwaiti site remains unmeasured by the training and validation data. The seven held-out images in §B are the partial exception — two are from a site in Irbid, Jordan — but seven images measure a direction, not a number.
- **It is 700 images.** That is a small dataset for five classes, and the per-class instance counts are uneven. The floor on performance is set by the data, not the architecture, which is why the improvement plan in [`error_analysis.md`](error_analysis.md) is about data rather than model size.
- **We could not expand it within the constraints.** The intended expansion failed the licence check (§A.1). Expanding it properly would mean either sourcing from CC0 libraries with the discipline described above, or — better — photographing a site in the region directly. The second is what we would do with more time, and it would address the first bullet at the same time.

The honest summary: **this project demonstrates a working, reproducible pipeline. It does not demonstrate a model ready for a Gulf site**, and the difference is the images.
