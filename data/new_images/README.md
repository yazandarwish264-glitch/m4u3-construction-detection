# New images — the only unbiased test in this project

Seven construction photographs, all taken by us, that were **never** in the Roboflow project, in any split, or in any shoot that fed one. The brief asks for five; three extra cost nothing and unbiased test images are the scarcest thing here.

## Why these carry more weight than they normally would

The validation split leaks. Consecutively numbered frames sit on both sides of it — `steelBar_5397k` in train, `5398k` in validation — so the reported mAP@50 of 0.943 measures memorisation as much as detection. Full evidence in [README §4.1](../../README.md).

These seven sit outside that problem entirely. They are the only measurement in the repository that a leak cannot flatter.

They are also the only images here that we hold outright: the training dataset is someone else's, used by reference under CC BY 4.0, and the images we tried to add to it were rejected on licence grounds ([`../../docs/image_provenance.md`](../../docs/image_provenance.md) §A).

## What is in the set

| File | Contains | Role |
|---|---|---|
| `new_01.jpg` | `steelbar` — rebar starters and timber formwork, close and clear | The weakest class under *easy* conditions — separates "hard class" from "hard photograph" |
| `new_02.jpg` | `steelbar` plus concrete pump boom and stacked timber | Same class under heavy clutter |
| `new_03.jpg` | `excavator` in an excavation, buildings behind | **Control** |
| `new_04.jpg` | `brick` + `steelbar` — blockwork wall with starters | **Control**, and the only image with both |
| `new_05.jpg` | `pvcpipe` — conduit run on a soffit with junction box | Only close-range MEP image in the set |
| `new_06.jpg` | `scaffold` — shoring and tower crane, distant | **Hard case**: small objects at range |
| `new_07.jpg` | Few or none — formwork panels and timber stacks | **Hard case**: mostly objects outside our schema, so a good false-positive probe |

Locations span Amman, Irbid, Nashville and New York. Two are from the authors' own house build in Irbid.

### Why `brick` and `excavator` are the controls

Both scored mAP@50 **0.995** with recall **1.000** on the graded run — they missed nothing. On genuinely unseen images, one of two things happens, and both are useful:

- **They hold up** → the leakage was mild; the model really did learn those classes
- **They collapse** → the 0.995 was largely memorisation, and the gap quantifies how severe the leak was

This is a free diagnostic. It is why the set is not seven `steelbar` shots.

### Why `steelbar` gets two

It is the weakest class under **both** architectures tried — 0.781 on YOLOv8s, 0.539 on YOLOv11n — despite having the most training instances. Its recall (0.612) is the lowest of any class by a wide margin. Whether that survives on unseen data is the single most interesting question these images can answer.

## The rules these images were selected under

Kept here because anyone extending the set must follow them, and because two of them were nearly broken.

1. **Never seen.** Not in the Roboflow project, not in any split, not a near-duplicate of one, and not from a source the base dataset could have been scraped from. The base dataset's filenames (`scaffold_9180j.jpg`) show it was scraped and systematically renamed, so a stock-library image carries a real risk of being a training image you then measure yourself against. Taking the photographs ourselves removes that risk entirely.
2. **No near-duplicates inside the set either.** Three views of the `new_06` site were available; two were dropped after visual inspection and perceptual hashing (distances 28–35). Using all three would inflate the evidence exactly the way the validation leak does.
3. **Include cases you expect to fail.** `new_06` and `new_07` are deliberate. A predicted failure is stronger evidence of understanding than seven clean successes, and it gives the error analysis something real to work with.
4. **Vary them.** Different countries, lighting, distance and density. Seven near-identical easy shots measure one thing seven times.
5. **Rights.** Our own photographs, released under CC BY 4.0 with the repository. Recorded in [`../../docs/image_provenance.md`](../../docs/image_provenance.md) §B.
6. **Privacy.** No legible ID badges. One image contains a person with their back turned, face not visible — retained under governance check 1.4. EXIF stripped from all seven by re-encoding onto a clean canvas, because GPS coordinates identifying a private site are personal data about that site's workforce. Check 1.5.

## Naming

`new_01.jpg` … `new_07.jpg`. Deliberately boring — these filenames appear in [`../../docs/error_analysis.md`](../../docs/error_analysis.md) and in `results/inference_record.json`.
