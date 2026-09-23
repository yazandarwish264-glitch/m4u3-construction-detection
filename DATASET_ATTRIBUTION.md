# Dataset attribution

This repository **redistributes** a dataset it does not own. CC BY 4.0 permits that,
provided credit is given and changes are indicated. This file is that credit, and it
is reproduced in the notes of the release the file is attached to.

## The redistributed file

| Field | Value |
|---|---|
| File | `construction-site-v1-yolo11.zip` |
| Attached to | Release [`v1.0`](https://github.com/yazandarwish264-glitch/m4u3-construction-detection/releases/tag/v1.0) |
| SHA-256 | `26b21198babe59ebb03c5fc43fee4d956690dfebb1802bb6325f219b234dcb4e` |
| Size | 64,478,143 bytes |

## Credit

**Original work:** *construction site*, 700 annotated images, published on Roboflow
Universe by the user **`seungyeon`** as
[`seungyeon/construction-site-km7bh`](https://universe.roboflow.com/seungyeon/construction-site-km7bh).

**Licence:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

**Copyright:** held by the original author. Nothing in this repository transfers it.

## Changes we made — stated, as the licence requires

CC BY 4.0 requires that modifications be indicated. Ours are:

1. **Forked** into the Roboflow workspace `yazan-darwish`, as project
   `construction-site-km7bh-fapwu`.
2. **Re-split** from the published 70 / 20 / 10 (train / valid / test) to **80 / 20**
   (560 train, 140 valid, no test split). The 70 test images were moved into training;
   the validation split was left untouched. This was done to meet the unit's required
   split, and it inherited a leakage defect that is documented openly in
   [`README.md` §4.1](README.md).
3. **Exported** in YOLO11 format with auto-orientation, EXIF stripping and a stretch
   resize to 640 × 640. No augmentation was applied.

**No images were added.** Candidate images we sourced were rejected on licence grounds
before reaching the dataset; the record is in
[`docs/image_provenance.md`](docs/image_provenance.md) §A. The redistributed zip is
therefore wholly CC BY 4.0 with a single upstream author to credit.

## Why we redistribute it rather than linking to it

A Roboflow download needs an API key. Requiring one meant that nobody outside this
group could reproduce the results — a defect a group member found by trying. Freezing
the exact export as a public, checksum-verified file removes the credential and pins
the bytes, so "this is the data that produced these numbers" becomes a claim anyone can
check. See [`README.md` §3](README.md) and §6.

## If you reuse this work

Credit `seungyeon` for the images. The obligation passes to you; it does not stop here.
Note also that the trained weights carry a **different and stricter** licence — AGPL-3.0,
inherited from Ultralytics — which is covered in [`README.md` §10](README.md).

## Attribution inside the archive

The zip carries Roboflow's own `README.dataset.txt`, which records the CC BY 4.0 licence
but names only our fork, not the upstream author. That is Roboflow's export format, not a
statement of provenance. **This file is the authoritative attribution** and takes
precedence over anything inside the archive.
