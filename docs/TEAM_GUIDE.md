# How We Built This — A Guide for the Team

**Written for someone who has never trained a model, never used GitHub, and does not know what any of these words mean yet.** Nothing here assumes prior coding. Where a term appears for the first time, it is explained in plain English.

If you follow this end to end you will have built the same thing we submitted: a public code repository containing a working object-detection model, the evidence that it works (and where it does not), and a short written analysis.

**Everything runs in a web browser.** You do not install Python, you do not need a powerful laptop, and you do not pay for anything.

---

## What you are actually building

A **model** that looks at a photograph of a construction site and draws boxes around five things: reinforcement bar, brick or blockwork, PVC pipe, scaffolding, and excavators.

Why that is useful: on a real project, progress is recorded by someone taking photos and typing a description days later. A model that reads the photo turns it into *data* — this zone, this date, rebar present, 87% confident — which can go into a system instead of sitting in a folder as a JPEG.

The deliverable is **not** the model. The deliverable is a repository that a stranger can open and re-run to get our exact results. That distinction is worth repeating because it is where most of the marks are.

---

## The checklist

Print this. Tick as you go. Each line is a milestone explained in detail further down.

- [ ] **0. Accounts** — Google, GitHub, Roboflow. All free. *(20 min)*
- [ ] **1. Get a dataset** — find one, copy it to your own account, split it. *(45 min)*
- [ ] **2. Write the class rules** — decide what counts as what, in writing, before labelling. *(1 hour)*
- [ ] **3. Set up the repository** — the online folder that holds everything. *(30 min)*
- [ ] **4. Train the model** — the computer learns from the images. *(20 min, mostly waiting)*
- [ ] **5. Publish the trained model** — so the second notebook can download it. *(15 min)*
- [ ] **6. Test it on photos it has never seen** — this is the honest test. *(30 min)*
- [ ] **7. Write the error analysis** — what went wrong and why. *(2 hours)*
- [ ] **8. Write the governance notes** — privacy, limitations, licensing. *(1.5 hours)*
- [ ] **9. Build the slides and report** — the PDF pack. *(1 hour)*
- [ ] **10. Verify from cold** — prove a stranger can re-run it. *(30 min)*
- [ ] **11. Final checks** — broken links, leftover placeholders. *(20 min)*

**Total: roughly 9–10 hours**, spread over a few sittings. Step 7 is where the actual thinking happens; do not rush it.

---

## The words you will keep hearing

Read this once. You do not need to memorise it; come back when a term trips you up.

| Word | What it actually means |
|---|---|
| **Model** | A file full of numbers that has learned a pattern. Ours has learned what rebar looks like. The file is about 22 MB and is called `best.pt`. |
| **Weights** | The numbers inside the model. "Publishing the weights" means uploading that file so others can use it. |
| **Training** | Showing the computer thousands of labelled examples until it learns the pattern. We did 30 rounds ("epochs") in about six minutes. |
| **Epoch** | One complete pass through all the training images. More epochs is not automatically better. |
| **Annotation / label** | A box someone drew around an object plus the name of that object. The model learns from these. |
| **Dataset** | A pile of images plus their annotations. |
| **Split** | Dividing the dataset into a part the model learns from (**train**) and a part it is tested on (**validation**). Usually 80% / 20%. |
| **Validation** | Testing the model on images it did not learn from, to see if it actually learned or just memorised. |
| **Inference** | Using a trained model on a new image. Training is learning; inference is doing. |
| **Confidence** | A number from 0 to 1 the model puts on each box. 0.9 means "fairly sure". It is *not* a probability of being correct. |
| **Threshold** | The cut-off below which you ignore the model's guesses. Default is 0.25. |
| **mAP@50** | The headline score, 0 to 1. Roughly: how often the model finds the right thing in the right place. 0.943 sounds excellent. Section 8 explains why it was not. |
| **Precision** | Of the boxes the model drew, what fraction were correct. Low precision = it invents things. |
| **Recall** | Of the things actually there, what fraction the model found. Low recall = it misses things. |
| **False positive** | The model says something is there and it is not. |
| **False negative** | Something is there and the model misses it. Worse for us — nobody investigates a record that was never created. |
| **YOLO / YOLOv8** | The free, widely used detection software we trained. You do not need to understand how it works internally. |
| **Repository ("repo")** | A folder that lives on GitHub, online, with a full history of every change. Our deliverable. |
| **Commit** | Saving a batch of changes to that history, with a note saying what changed. |
| **Push** | Sending your saved changes up to GitHub so others can see them. |
| **Notebook (`.ipynb`)** | A document that mixes explanation with code you can run, a block at a time. Ours are in `/notebooks/`. |
| **Colab** | Google's free website that runs notebooks on Google's computers, including a free graphics card. |
| **Runtime** | The temporary computer Colab gives you. It switches off when idle and everything on it is lost. |
| **GPU / T4** | The graphics card that makes training fast. Free tier gives you a "T4". |
| **API key** | A long secret password that lets a program use your Roboflow account. **Treat it like a bank PIN.** |

---

## Step 0 — Accounts and software *(20 min)*

**You need three free accounts and a web browser. That is all.**

| What | Where | Why | Cost |
|---|---|---|---|
| **Google account** | you almost certainly have one | Runs Google Colab, which does the training | Free |
| **GitHub account** | [github.com/signup](https://github.com/signup) | Holds the repository — the thing you submit | Free |
| **Roboflow account** | [app.roboflow.com](https://app.roboflow.com) | Holds and prepares the images | Free tier: **1,000 images maximum** |
| **Chrome or Edge** | already installed | Colab behaves best in these | Free |

**Optional but strongly recommended on Windows:**

- **GitHub Desktop** — [desktop.github.com](https://desktop.github.com). A normal-looking app for uploading files to GitHub without typing commands. If the words "command line" make you uneasy, install this.

**You do NOT need:** Python on your laptop, a graphics card, Visual Studio Code, Docker, or a paid subscription to anything.

> ### About the 1,000-image limit
> Roboflow's free tier counts **every image in your account**, including ones in the trash. If you hit the limit you must empty the trash in the web interface before you can upload more. We ran into this and lost half an hour to it.

---

## Step 1 — Get a dataset *(45 min)*

You need a few hundred labelled construction images. Labelling them yourself would take weeks, so start from someone else's public dataset and check its licence.

**1.1 — Find one.** Go to [universe.roboflow.com](https://universe.roboflow.com) and search for your subject — we searched "construction site". Roboflow Universe is a library of public datasets other people have already labelled.

**1.2 — Check three things before you commit to it.** This is the step people skip.

- **How many images?** Under 1,000 or you cannot fit it in the free tier. Ours had 700.
- **What licence?** Look for **CC BY 4.0** or **CC0**. These allow use with credit. If it does not say, do not use it.
- **What classes?** The list of object types it labels. Ours gave us `brick`, `excavator`, `pvcpipe`, `scaffold`, `steelbar` — five, which is a sensible number.

We used [`seungyeon/construction-site-km7bh`](https://universe.roboflow.com/seungyeon/construction-site-km7bh), 700 images, CC BY 4.0.

**1.3 — Fork it.** "Fork" means make your own copy you can change. On the dataset page there is a **Fork** or **Download this Dataset** button. Fork it into your own Roboflow workspace. The original stays untouched.

**1.4 — Fix the split.** Datasets usually arrive split 70% train / 20% validation / 10% test. The assignment wants **80/20**. In Roboflow, open your project, find the split controls, and rebalance so there is no test portion — move those images into training.

**1.5 — Generate a version.** In Roboflow, "generating a version" freezes a snapshot of your dataset that never changes. Set the image size to **640 × 640** and turn **augmentation off**.

> **Why augmentation off?** Augmentation makes extra copies of images — rotated, brighter, flipped — to give the model more to learn from. It also hides what your data is actually doing. Get a plain baseline first; add augmentation later only if the error analysis says you need it.

Write down your **workspace name**, **project name** and **version number**. You will type them into the notebooks. Ours: `yazan-darwish` / `construction-site-km7bh-fapwu` / version `1`.

---

## Step 2 — Write the class rules *before* touching images *(1 hour)*

This feels like paperwork. It is the single highest-value hour in the project.

A **class contract** is a written document saying exactly what counts as each class. Not "steelbar means reinforcement bar" — that is useless. It needs to answer the arguments:

- If ten bars are tied in a bundle, is that **one** box or **ten**?
- A loose scaffold tube lying on the ground — is it `scaffold`? Is it `steelbar`? Neither?
- A pile of broken bricks — still `brick`, or is it rubble?
- How small is too small to bother boxing? (We said 20 pixels.)
- If a wall hides half an excavator, do you box the visible part or guess the whole shape?

**Why it matters.** If two people label the same image differently, the model learns the disagreement rather than the object. It cannot learn a boundary that the labels do not agree on.

Ours is [`class_definitions.md`](class_definitions.md). Copy its structure: one section per class with what's included, what's excluded, and a worked example; then a section listing the ambiguities you are *accepting* rather than solving.

> **The test to apply:** could someone who has never met your team label 25 images consistently using only this document? If not, it is not finished.

**One honest note.** We inherited 700 images that were labelled by someone else *before* our contract existed. So our rules describe what we adopted, not necessarily how those 700 were actually labelled. We wrote that down rather than hiding it, and you should too.

---

## Step 3 — Set up the repository *(30 min)*

The repository is the deliverable. Everything else lives inside it.

**3.1 — Create it.** On GitHub, click **New repository**. Name it something descriptive. **Set it to Public** — a marker has to be able to open it without logging in. Tick "Add a README file".

**3.2 — Make the folders.** Your structure should be:

```
/notebooks/    the two Colab notebooks
/docs/         the written analysis
/results/      metrics, curves, and the evidence images
/data/         only the few photographs you took yourself
/reports/      the slides and mini report PDFs
README.md      the front page — this is what gets read first
LICENSE        which licence your code is under (we used MIT)
.gitignore     a list of things to never upload
requirements.txt  which software versions you used
```

**3.3 — Set up `.gitignore` properly.** This is a plain text file listing things Git must never upload. Put these in it:

```
*.pt          model weights — too big, and they can never be deleted from history
dataset/      the images — downloaded at runtime instead
*.zip
.env          anything holding a password
*.key
```

> **Why weights must not be committed:** once a file enters Git history it is there permanently, even if you delete it later. A 22 MB file bloats the repo forever. Publish it as a "Release" instead — Step 5.

**3.4 — Getting files up there.** Easiest route on Windows: install **GitHub Desktop**, click **Clone** to pull the repo onto your laptop as a normal folder, drag your files into it, then in GitHub Desktop type a short summary and click **Commit** then **Push**. That is the whole workflow.

---

## Step 4 — Train the model *(20 min, mostly waiting)*

This is the part that sounds hardest and is actually the easiest, because the notebook does it.

**4.1 — Open the notebook from GitHub in Colab.** Take this address and replace the middle with your own username and repo name:

```
https://colab.research.google.com/github/USERNAME/REPO/blob/main/notebooks/01_training_eval.ipynb
```

Opening it *this way* matters. It proves the notebook runs straight from the repository, which is what the assignment asks for.

**4.2 — Switch the graphics card on.** Menu: **Runtime → Change runtime type → T4 GPU → Save**. Without this, training takes hours instead of minutes.

**4.3 — Fill in your details.** The first code block has your Roboflow workspace, project and version. Change them to yours.

**4.4 — Run it.** **Runtime → Run all.** A warning appears saying the notebook was not written by Google — click **Run anyway**. That warning is normal for any notebook opened from GitHub.

**4.5 — Paste your API key when asked.** Partway through, a small white box appears asking for your Roboflow Private API Key. Get it from Roboflow: **Settings → API Keys**. Paste it in and press Enter.

> ### Handle the key properly
> The notebook asks for the key with something called `getpass`, which hides it as you type and never writes it into the file. **Never type your key directly into a code block** — anyone who reads the repo would then have it. If you ever paste a key somewhere public, go to Roboflow and revoke it immediately.

**4.6 — Wait.** Roughly 6–8 minutes for 700 images and 30 epochs. Numbers scroll past. Ignore them.

**4.7 — Read the results.** At the end you get a table: Precision, Recall, mAP@50, mAP@50-95, overall and per class. Write these down — they go in the README.

**4.8 — Download the outputs.** The last block bundles everything into a zip and downloads it: the trained `best.pt`, the training curves, the confusion matrix. Unzip it into your repo's `/results/` folder (but **not** `best.pt` — see Step 5).

### Things that go wrong here

| What you see | What it means | Fix |
|---|---|---|
| "Too many sessions" | You have another Colab notebook still running | **Manage sessions** → terminate the old one |
| Training is extremely slow | GPU not switched on | Runtime → Change runtime type → T4 GPU |
| "no space left" | Colab's temporary disk filled up | Runtime → Restart session, run again |
| Nothing happens for ages | Normal. Installing takes ~60s, downloading the dataset another ~60s | Wait |

---

## Step 5 — Publish the trained model *(15 min)*

The `best.pt` file is 22 MB. It must not go into the repository itself (Step 3.3), but the second notebook needs to download it. GitHub **Releases** solve exactly this.

A Release is a labelled snapshot of your project with files attached — like publishing version 1.0 with a download button.

1. On your repo page, look at the right-hand column for **Releases** → **Create a new release**.
2. **Tag:** type `v1.0` and choose "Create new tag".
3. **Title:** something like "Trained weights v1.0".
4. **Attach binaries:** drag `best.pt` from your Downloads folder into the box.
5. Click **Publish release**.
6. Afterwards, **right-click the `best.pt` link on the release page and copy the address.** It looks like:
   `https://github.com/USER/REPO/releases/download/v1.0/best.pt`
7. Paste that address into the `WEIGHTS_URL` line at the top of notebook 02.

**Check it works anonymously.** Open that address in a private/incognito window. If it downloads without asking you to log in, a marker can get it too.

---

## Step 6 — Test on photos the model has never seen *(30 min)*

**This is the most important step in the project and the one most likely to be skipped.**

Validation images come from the same dataset as training images — often the same photo shoot, minutes apart. A model can score brilliantly on them by memorising rather than learning. The only way to find out is to show it photographs from somewhere else entirely.

**6.1 — Get 5–7 photographs.** Take them yourself. A walk past any building site with a phone is enough. Your own photos are better than stock images because there is zero chance they overlap with the training data, and you know exactly where they came from.

Aim for variety, and deliberately include:
- One image of your **strongest** class (a control — if this fails, something is badly wrong)
- One of your **weakest** class under easy conditions
- One you **expect to fail** — distant, cluttered, dusty

**6.2 — Strip the hidden data.** Phone photos carry invisible information including **GPS coordinates**. Publishing the exact location of a private site is a real privacy problem. Re-saving each image through any basic editor removes it. Also check: no readable faces, no legible ID badges.

**6.3 — Put them in `/data/new_images/`** named boringly: `new_01.jpg`, `new_02.jpg`... Those filenames end up quoted in your error analysis.

**6.4 — Run notebook 02.** Same as before: open from GitHub in Colab, Run all. It downloads your published weights, runs them on the validation images *and* your new photos, and saves annotated pictures into `/results/evidence/`.

**6.5 — Actually look at the pictures.** Do not just read the numbers. Open every output image and compare it to what is really in the photo.

> ### What happened to us here
> Validation: the model matched the truth on **8 of 10** images. Our own photographs: **1 of 7**. It called a blockwork wall "scaffold" with 78% confidence, missed an unobstructed excavator completely, and returned nothing at all on four images.
>
> Both classes we had picked as "controls" — the ones scoring 99.5% on validation — failed. Without those seven photos we would have submitted a 0.943 score and believed it.

---

## Step 7 — Write the error analysis *(2 hours — the real work)*

The assignment asks for **3 false positives, 3 false negatives, and 3 improvements**. The marks are not for finding mistakes; they are for explaining *why* they happened in a way the data can address.

**7.1 — Collect the cases.** Go through your output images. For each error write down: the filename, what the model said, the confidence, and what is actually in the box. **A hypothesis without a filename behind it reads as guesswork.**

**7.2 — Test your explanations instead of asserting them.** This is what separates a good analysis from a plausible one. Two free experiments:

- **Lower the confidence threshold to 0.02.** If the missed objects still produce nothing, the model never considered them — it is not a threshold problem, and nothing about tuning will fix it.
- **Change the image size** (`imgsz` 640 → 1280 → 2560) and re-run. Resizing carries no meaning; a blockwork wall is a blockwork wall at any resolution. **If the predicted class changes, the model has learned a texture, not an object.**

Ours changed. `new_04` went `scaffold` 0.78 → `scaffold` 0.31 → `brick` 0.46 purely from resizing. That one test explained five of our six errors and became the centre of the whole report.

**7.3 — Look for one cause behind several errors.** A hypothesis that explains five errors is far stronger than five separate hypotheses.

**7.4 — Write improvements that are countable.** Not "improve the dataset". Instead: *"Collect ~100 wide-field photographs where targets occupy under 15% of frame width, annotate them, retrain at imgsz 1024. Success = predictions stop changing class between 640 and 2560."* Name the gap, the action, the metric, and how you will know it worked.

**7.5 — Say what you are NOT claiming.** Seven images show that a failure mode exists. They cannot tell you how often it happens. Write that down. Markers notice the difference between confidence and overclaiming.

---

## Step 8 — Governance and licensing *(1.5 hours)*

Four things the brief asks for. None require technical skill; all require thinking honestly.

**8.1 — Privacy and consent.** A construction site is a workplace; a camera pointed at work is pointed at workers. Record: does any class detect people (ours deliberately does not)? Were faces blurred or excluded? Was GPS stripped? Under the **EU AI Act**, a system that monitors workers becomes "high-risk" and triggers heavy obligations — note that you are one class label away from that line.

**8.2 — Data minimisation.** Only label the classes you need. Store images at the size you use, not the camera's maximum. Keep keys out of the repository. Do not commit weights.

**8.3 — Limitations — when NOT to use this.** Be blunt. Ours says: no safety use of any kind, no quantity measurement, nothing that could enter a payment application, no contractual evidence, and — after Step 7 — no wide-field photographs, which is how site photos are actually taken.

**8.4 — False negatives versus false positives.** The two errors are not equal and the asymmetry flips depending on use:

- **Progress logging:** a miss is *silent*. No record is created, so nobody investigates. Favour recall, lower the threshold.
- **Alerting:** false alarms train people to ignore the system, and then a real one gets ignored. Favour precision, raise the threshold.

**8.5 — Licensing.** Three separate things, each with its own licence. Your code (we used MIT). The dataset (someone else's — ours CC BY 4.0, requiring credit). **And the weights.** YOLOv8 is AGPL-3.0, and anything trained with it inherits that. Commercial use requires either full AGPL compliance or a paid Ultralytics licence. This is the most commonly missed obligation in YOLO projects.

> ### A trap we walked into
> We sourced 25 extra images to enlarge the dataset. Twenty turned out to be **watermarked Shutterstock previews** — free to download, licensed for nothing at all. A filename is not a licence; the watermark is only visible when you open the file.
>
> We rejected all twenty and wrote down why. Check licences **before** upload, not after. And if you do reject something, record it — a marker reading "we checked, found a problem, and dropped them" sees judgement, not failure.

---

## Step 9 — Build the slides and mini report *(1 hour)*

The brief wants **6–8 slides** and a **2-page** report, as PDFs, linked from the README.

You can make these in PowerPoint and export to PDF — that is perfectly acceptable. We generated ours with a script (`tools/build_reports.py`) so that the numbers come straight from `results/metrics.json` and cannot drift out of date when we re-run training. If you want to do the same, you need Python installed locally plus one library:

```
pip install reportlab
python tools/build_reports.py
```

Whichever route you take:

- **Put the repository address on page one of both documents.** PDFs get downloaded and forwarded and lose whatever message carried the link.
- **Check the page count.** Ours: 8 slides, 2 pages. Over the limit loses marks for no reason.
- **Open both PDFs and read every page.** Text that overruns the footer is invisible in the source and obvious to a marker.
- Lead with the finding, not the score.

---

## Step 10 — Verify from cold *(30 min)*

Three of the ten marks are for reproducibility. Not accuracy — *reproducibility*. A modest model in a repo that runs cleanly beats a strong model nobody can re-run.

So test it the way a stranger would:

1. Open a **private/incognito** browser window, logged out of everything.
2. Go to your repository address. Does it load? (If not, it is still private — fix that first.)
3. Open notebook 01 from GitHub in Colab. **Runtime → Restart session → Run all.**
4. Let it finish and compare the numbers to what your README claims.
5. Do the same for notebook 02.

**What to expect.** Ours reproduced *exactly* — every metric identical to three decimal places, and notebook 02 produced twelve output files byte-for-byte identical to the committed ones. That is because the random seed is fixed, the dataset version is pinned, and the GPU type was the same. If yours lands slightly off, that is also fine — report both runs side by side rather than pretending.

**Write the proof note in the README:** date and time of the run, which GPU, how long it took, and the software versions. That note is what the marker is looking for.

---

## Step 11 — Final checks *(20 min)*

Quick, boring, and worth real marks under "repository professionalism".

- [ ] **Search the whole repo for `TODO` and `____`.** Template placeholders left in a submitted document look worse than an honest gap.
- [ ] **Click every link in the README.** Broken links are explicitly marked.
- [ ] **Confirm the repo is public** — incognito window, not logged in.
- [ ] **Confirm the weights download** without a login.
- [ ] **Confirm both PDFs are linked** from the README and open correctly.
- [ ] **Search the repo for your API key.** It should appear nowhere. If it does, revoke it in Roboflow immediately and generate a new one.
- [ ] **Check the evidence counts** against the brief: 3–5 annotation examples, 10 validation predictions, 5 new-image predictions.
- [ ] **Read the README top to bottom as if you had never seen the project.** It is the first and sometimes only thing read in full.
- [ ] **Delete working files** that are not deliverables — scratch notes, half-finished checklists. We removed a `DO_THIS_NEXT.md` whose stale status lines misrepresented the state of the repo.

---

## Everything that went wrong, so it does not go wrong for you

Honest list. Most of our time went here, not on the model.

**Dataset and images**

1. **Roboflow's 1,000-image cap counts the trash.** Deleting images does not free the quota until you empty the trash in the web interface.
2. **Twenty "free" stock images were watermarked previews.** Check licences by *opening the file*, before uploading.
3. **The dataset split leaked.** The source images were sequential photos — `steelBar_5397k` and `5398k` are the same scene seconds apart — and a random split put them on opposite sides. The model saw near-identical images in training and validation, which is why it scored 0.943 and then failed on real photos. **Watch for:** a high score after just one epoch, or any class hitting 100% recall. Both are warning signs, not good news.
4. **We mis-catalogued one of our own photos** as containing almost nothing; it was full of rebar. Look properly at every image in your test set.

**Colab**

5. **"Too many sessions"** — old notebooks keep holding the GPU. Manage sessions, terminate, retry.
6. **Runtimes vanish.** Anything not downloaded is lost when the session ends. Download at the end of every run.
7. **Repeated automatic downloads get blocked** by the browser after a few. If a file does not arrive, fetch it from Colab's file panel on the left.

**Git and files**

8. **Never commit the weights.** Once a big file is in Git history it is there permanently. Releases exist for this.
9. **PDFs and images can be corrupted by careless copying.** If a file changes size when you move it, it is broken. Check before committing.
10. **Do not commit helper scripts** you wrote to automate yourself. Keep the repo to deliverables.

**Security**

11. **Never paste an API key into a chat, an email, or a code block.** Use the `getpass` prompt, which hides it and stores nothing. If a key is ever exposed, revoke it the same minute.

---

## What we would do differently

Worth reading before you start, because these are design decisions, not fixes.

1. **Split by scene group, not at random.** Cluster images that come from the same shoot and keep each cluster entirely in train or entirely in validation. Your score will drop. That drop *is* the correction.
2. **Take your own test photographs on day one, not at the end.** They are the only honest signal you get, and knowing early would have changed what we did next.
3. **Check licences before uploading**, not after.
4. **Try a foundation model before fine-tuning your own.** We ran SAM 3 and GPT-6 Astra on the same seven photos out of curiosity. They found the right class on 5 of 7 and 2 of 2 respectively, against our trained model's 1 of 7 — with no training on our data at all. Neither was usable *as-is*, because they box every individual object where our rules want one box per group. But it raises a fair question we never tested: whether fine-tuning on 700 images was the right approach at all.

---

## If you get stuck

| Problem | Where to look |
|---|---|
| Notebook throws an error | Read the **last line** of the red text — that is the actual error. The rest is trace. |
| Numbers do not match the README | Check dataset version, `imgsz`, and epochs are the same |
| Cannot get files onto GitHub | Use GitHub Desktop — clone, drag files in, Commit, Push |
| Roboflow will not accept uploads | You are at the 1,000-image cap. Empty the trash. |
| Colab will not connect | Terminate other sessions, or wait — free-tier GPUs are sometimes all in use |

**Reference implementation:** every file mentioned here exists in this repository. When the guide says "ours looks like this", go and open ours.

---

*Written for MAICEN0526 Module 4 Unit 3, Group 6. Everything described here was done in a browser on a free account.*
