# New images — the only unbiased test in this project

Five construction photographs that were **never** in the Roboflow project, in any split, or in any shoot that fed one.

## Why these five carry more weight than they normally would

The validation split leaks. Consecutively numbered frames sit on both sides of it — `steelBar_5397k` in train, `5398k` in validation — so the reported mAP@50 of 0.943 measures memorisation as much as detection. Full evidence in [README §4.1](../../README.md).

These five images sit outside that problem entirely. They are the only measurement in the repository that a leak cannot flatter.

## What each one should contain

All five classes should appear across the set, but the assignment is not "one class per image". Two of these answer a specific question and two act as controls.

| File | Should contain | What it is testing |
|---|---|---|
| `new_01.jpg` | `steelbar`, close and clearly visible | The weakest class under *easy* conditions — separates "hard class" from "hard photograph" |
| `new_02.jpg` | `steelbar`, bundled or tangled | Tests the bundling hypothesis directly: is group-boxing the cause of the deficit? |
| `new_03.jpg` | `brick` + `pvcpipe` | **Control** plus remaining class coverage |
| `new_04.jpg` | `scaffold`, ideally with `steelbar` in frame | Tests the steelbar/scaffold confusion we predicted and never observed |
| `new_05.jpg` | `excavator`, wider cluttered scene | **Control**, under realistic clutter rather than an isolated subject |

### Why `brick` and `excavator` are the controls

Both scored mAP@50 **0.995** with recall **1.000** on the graded run — they missed nothing. On genuinely unseen images, one of two things happens, and both are useful:

- **They hold up** → the leakage was mild; the model really did learn those classes
- **They collapse** → the 0.995 was largely memorisation, and the gap quantifies how severe the leak was

This is a free diagnostic. Do not skip them in favour of five `steelbar` shots.

### Why `steelbar` gets two

It is the weakest class under **both** architectures tried — 0.781 on YOLOv8s, 0.539 on YOLOv11n — despite having the most training instances. Its recall (0.612) is the lowest of any class by a wide margin. Whether that survives on unseen data is the single most interesting question these images can answer.

## Rules

1. **Never seen.** Not in the Roboflow project, not in any split, not a near-duplicate of one, **and not from the same source the base dataset was scraped from.** The base dataset's filenames (`scaffold_9180j.jpg`) show it was scraped and systematically renamed — so if you source these from a stock library, use a *different* one from the rest of the added images, or you risk re-downloading a training image and measuring the leak twice.
2. **Include at least one you expect to fail.** Distant, dusty, cluttered, awkward angle. A predicted failure is stronger evidence of understanding than five clean successes, and it gives the error analysis something real to work with.
3. **Vary them.** Different lighting, distance and density. Five near-identical easy shots measure one thing five times.
4. **Rights.** Your own photographs, or openly licensed with the licence recorded in [`../../docs/image_provenance.md`](../../docs/image_provenance.md).
5. **Privacy.** No identifiable faces or legible ID badges — blur or exclude. Strip EXIF before committing: GPS coordinates identifying a private site are personal data about that site's workforce. Governance checks 1.4 and 1.5.

## The best option, if it is at all practical

**Photograph these five yourself.** Not the other 25 — just these.

One walk past any building site with a phone. It removes the overlap risk completely, and it produces **GCC imagery** rather than European stock, which directly addresses the limitation recorded in [`../../docs/image_provenance.md`](../../docs/image_provenance.md): that this project demonstrates a working pipeline but has never been validated on a Gulf site.

Five phone photos move that from *unmeasured* to *measured, and here is what happened*. That is a materially better position at the oral defence for about ten minutes of effort.

## Naming

`new_01.jpg` … `new_05.jpg`. Keep it boring — these filenames appear in [`../../docs/error_analysis.md`](../../docs/error_analysis.md) and in `results/inference_record.json`.
