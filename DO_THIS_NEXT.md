# Do this next

The dataset is built and live. What remains needs your GitHub and Google accounts, your own photographs, and one GPU run.

**Deadline: Monday 28 September.** Roughly 4 hours of hands-on work left.

---

## Status

| Deliverable | State |
|---|---|
| **Roboflow dataset** | **Done.** `yazan-darwish/construction-site-km7bh-fapwu` v1 — 700 images, 560/140 (80/20), 640×640, no augmentation |
| Repository structure | **Done** |
| README, all 11 sections | **Done** except metrics and two URLs |
| `docs/class_definitions.md` | **Done** — written against the real five classes |
| `docs/governance_checklist.md` | **Done** except 6 checkboxes and 2 thresholds |
| `docs/error_analysis.md` | Structure done, evidence empty — needs your validation images |
| `docs/sam_exploration.md` | Argument done, observations empty — needs 15 min in Roboflow |
| Both Colab notebooks | **Done, tested, and pre-configured** with the real Roboflow slugs |
| `reports/slides.pdf`, `mini_report.pdf` | **Done** — metrics auto-fill from `metrics.json` |
| `LICENSE`, `.gitignore`, `requirements.txt` | **Done** |
| Trained weights | Not started — needs a Colab GPU |
| GitHub repository | Not started — needs your account |
| Held-out test images | **Done** — 7 of our own photographs in `data/new_images/` |
| Dataset expansion (25 images) | **Dropped.** 20 were watermarked Shutterstock previews, 5 were CC0 but too few to matter. Not required by the brief. See `docs/image_provenance.md` §A |

**Nothing in the notebooks needs editing except `WEIGHTS_URL` and `REPO_URL`.** The Roboflow workspace, project and version are already filled in.

---

## Step 1 — GitHub (30 min)

### Easiest on Windows: GitHub Desktop

1. Install **GitHub Desktop** from [desktop.github.com](https://desktop.github.com) and sign in.
2. **File → Add local repository** → browse to
   `C:\Master In Ai\35 Builds and Experiments\M4U3 Computer Vision Repo`
3. It offers **"create a repository"** — click that. Name it `m4u3-construction-detection`.
4. **Publish repository**, and **untick "Keep this code private."** It must be public or the markers cannot open it.

### Or, browser only

github.com → **+** → **New repository** → `m4u3-construction-detection` → **Public** → **Create**. Then **Add file → Upload files** and drag everything in, folders included.

### Then fix the two Colab badges

1. GitHub → `notebooks/01_training_eval.ipynb` → **pencil** icon.
2. In the first cell, replace `GITHUB_USER/REPO_NAME` with `yourusername/m4u3-construction-detection`. Commit.
3. Same for `02_baseline_inference.ipynb`.
4. Click a badge — if Colab opens, it worked.

---

## Step 2 — Train (20 min of attention, ~40 min of waiting)

**You can do this before adding your own images.** Train on v1 now, get a working baseline and real numbers in the README, then retrain on v2 after you add your photographs if time allows. A complete repo with v1 results beats an incomplete one waiting on v2.

1. roboflow.com → **Settings → API Keys** → copy your **Private API Key**. Never paste it into a cell or a commit — the notebook asks at runtime and hides it.
2. GitHub → `notebooks/01_training_eval.ipynb` → **Open in Colab**.
3. **Runtime → Change runtime type → T4 GPU → Save.** Skip this and nothing works.
4. **Runtime → Restart session and run all.** Paste the key when prompted.
5. Wait 25–45 min with the tab open — Colab drops idle sessions.

### Collect the outputs

The last cell downloads `m4u3_results.zip` and `best.pt`.

1. Unzip. Upload the contents of `results/` to GitHub — **not** `results/weights/`.
2. **Releases → Create a new release** → tag `v1.0` → attach `best.pt` → **Publish**.
3. Right-click the attached file → **Copy link address** → that is `WEIGHTS_URL`. Paste it into both notebooks' CONFIG cells and into README §7. Commit.
4. **Cell 11.1 prints paste-ready markdown tables.** Copy them into README §4 and §6. Don't retype.
5. Copy the ultralytics version it prints into `ULTRALYTICS_PIN`, `requirements.txt`, and the README checklist.

---

## Step 3 — Your own images (2–3 hours)

The unit requires 25 of your own images, at least 5 of them boundary cases.

### Photograph

Any site with visible reinforcement, blockwork, plastic pipe, scaffolding or an excavator. Your phone is fine.

**Five deliberate near-misses** — this is what the unit is testing:

| Photograph | Looks like | Is not |
|---|---|---|
| Loose scaffold tube lying on the ground | `steelbar` | Belongs to **neither** class — the hardest rule in the contract |
| A ladder, handrail or hoarding frame | `scaffold` | Erected access structure, not any vertical frame |
| Stone cladding or paving blocks | `brick` | Material versus form |
| Metal conduit under dust | `pvcpipe` | Not plastic |
| A wheeled loader or dozer | `excavator` | Machine type, not just yellow plant |

**Before uploading:** no identifiable faces, no legible ID badges, and strip EXIF so no GPS goes up. Right-click → Properties → Details → *Remove Properties and Personal Information*. That is governance checks 1.4 and 1.5, and they carry marks.

### Upload and annotate

1. [Your project](https://app.roboflow.com/yazan-darwish/construction-site-km7bh-fapwu) → **Upload** → drag the 25 in.
2. **Annotate** with `docs/class_definitions.md` open beside you. Follow it even where it feels wrong — if a rule is genuinely wrong, change the document first, then annotate.
3. The rules people break: **one box per group** not per object; **visible extent only**; **skip anything under ~20 px**; **when in doubt, don't label**.
4. Try **Smart Polygon / SAM** on 10–15 images and keep score — time with and without, and how many of its boxes you accepted, adjusted, discarded. Those numbers fill `docs/sam_exploration.md` §4, which is already written around them.
5. **Generate** a new version at **80/20**, Auto-Orient + Resize 640×640, augmentation off. Note the new version number.
6. If you retrain on it, change `RF_VERSION` in both notebooks and update README §3.

---

## Step 4 — Evidence and error analysis (1 hour)

1. Put 5 photographs in `data/new_images/` that were **never** in the dataset. Rules are in that folder's README. Commit.
2. Open `notebooks/02_baseline_inference.ipynb` in Colab. Set `WEIGHTS_URL` and `REPO_URL`. **Restart session and run all.**
3. Unzip `m4u3_evidence.zip` into `results/evidence/` and commit.

### Write the error analysis

Open `results/curves/confusion_matrix.png` **first** — it tells you which class pairs are confused. Based on the class definitions, expect `steelbar` ↔ `scaffold` to dominate.

Then open the 10 validation comparisons. Ground truth left, prediction right.

- A box on the **right** only → **false positive**
- A box on the **left** only → **false negative**

Find three of each, note the **filenames**, fill in `docs/error_analysis.md`.

This is 1.5 marks and it's where most submissions go vague. A hypothesis with an image behind it reads as analysis; one without reads as guesswork and is marked that way.

### Set the two thresholds

Cell 6.1 sweeps confidence 0.10 → 0.75. Pick a **low** value for progress logging (`steelbar`/`brick`/`pvcpipe`) and a **high** one for site-condition alerts (`scaffold`/`excavator`). Record both in `docs/governance_checklist.md` §4 — the reasoning is written, you supply the numbers.

---

## Step 5 — Reports and the final proof (1 hour)

### Rebuild the PDFs

New Colab notebook, one cell:

```python
!git clone https://github.com/YOUR_USER/m4u3-construction-detection.git
%cd m4u3-construction-detection
!pip install -q reportlab
!python tools/build_reports.py
from google.colab import files
files.download("reports/slides.pdf"); files.download("reports/mini_report.pdf")
```

It reads `results/metrics.json` and fills every metric automatically. Edit the `CONTENT` block at the top of `tools/build_reports.py` first — author names, the three takeaways, the run details. Upload both PDFs back to `reports/`.

### Kill every placeholder

| Search for | Where |
|---|---|
| `GITHUB_USER`, `REPO_NAME` | both notebooks |
| `PASTE_GITHUB_RELEASE_ASSET_URL_HERE` | both notebooks, README §7 |
| `____` | README §3, §4, §6; all four docs; `build_reports.py` |
| `TODO` | README §3, §7, §11 |
| Author names | README §11, `build_reports.py` |

### The cold-start run — 3 of the 10 marks

1. Open `01_training_eval.ipynb` from GitHub in a **fresh** Colab session.
2. **Runtime → Restart session and run all.**
3. Watch it finish without touching anything.
4. Record the date, time, GPU and runtime in README §6.

If it fails, fix it and run again. A notebook needing a human nudge is not reproducible, and that is precisely what is marked.

### Final pass

- [ ] Every README link opens
- [ ] Both Colab badges work from GitHub
- [ ] The Release link downloads `best.pt`
- [ ] `results/evidence/` has annotations, 10 validation, 5 new images
- [ ] Both PDFs current and linked
- [ ] Search the repo for `api_key` — nothing found
- [ ] No `____`, no `TODO`
- [ ] A groupmate who didn't build it can follow the README alone

### Submit

The **repository URL**, on Canvas.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `NO GPU DETECTED` | Runtime → Change runtime type → T4 GPU → Save → run all again |
| Roboflow download fails | Check the key. The workspace/project/version are already correct |
| Training looks frozen | It isn't. Only worry after ~60 min with no epoch line |
| Colab disconnects | Keep the tab visible; free tier drops idle sessions |
| `WEIGHTS_URL is not set` | Create the Release first |
| Notebook 02 clone fails | Repository is private — Settings → make it Public |
| Out of GPU quota | Wait, or set `VERIFICATION_RUN = True` and document it in README §6. The brief explicitly permits this |
| Roboflow "hard limit of 1000 images" | Workspace is at 700 of 1000. Adding more than 300 images needs the trash emptied again |

---

## Where the marks are

| Criterion | Marks | Won by |
|---|---|---|
| Reproducibility and cloud-only execution | **3.0** | The cold-start run, README §5 and §6 |
| Repository professionalism | **2.0** | Clean structure, working links, a README a stranger can follow |
| Evidence and results communication | **2.0** | Full evidence pack, interpretation not bare numbers |
| Error analysis and iteration plan | **1.5** | Step 4, with real filenames |
| Governance and licensing | **1.5** | Already written — 6 checkboxes and 2 thresholds from you |

**Model accuracy is worth nothing.** A modest mAP in a repository that runs cleanly from a cold start beats a strong model nobody can re-run.
