# New images — the generalisation test

Put **5 construction photographs** here that were **never** in the training or validation split.

This folder is what makes the "5 new-image predictions" deliverable meaningful. Validation performance tells you the model learned the dataset. Performance here tells you whether it learned the *task*.

## Rules

1. **Never seen.** Not in the Roboflow project, not in any split, not a near-duplicate frame of one. If in doubt, do not use it.
2. **Contains our classes.** At least some of `brick`, `excavator`, `pvcpipe`, `scaffold`, `steelbar` should be present — otherwise a zero-detection result tells you nothing.
3. **Include at least one hard one.** A photograph you expect the model to fail on. Reporting a failure you predicted is stronger evidence of understanding than five easy successes.
4. **Rights.** Your own photographs, or openly licensed. Check the licence before committing.
5. **Privacy.** No identifiable faces or legible ID badges. Blur or exclude. Strip EXIF before committing — GPS coordinates identifying a private site are personal data about that site's workforce. See [`../../docs/governance_checklist.md`](../../docs/governance_checklist.md) §1.

## Naming

`new_01.jpg` … `new_05.jpg`. Keep it boring — the filenames appear in `docs/error_analysis.md` and in `results/inference_record.json`.

## Record what each one is

Fill this in when you add them. It matters at defence, when someone asks why the model missed something.

| File | What is in it | Conditions | What we expect |
|---|---|---|---|
| `new_01.jpg` | | | |
| `new_02.jpg` | | | |
| `new_03.jpg` | | | |
| `new_04.jpg` | | | |
| `new_05.jpg` | | | |
