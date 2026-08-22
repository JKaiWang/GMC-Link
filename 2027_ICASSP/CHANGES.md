# Paper change log

One section per paper snapshot (= release tag). Newest first. Every line is tagged:

- **[method]** — the module itself changed; all affected numbers were re-measured
- **[protocol]** — the evaluation was wrong or dirty; fixed, then re-measured
- **[writing]** — the text mis-described what the code always did
- **[editorial]** — presentation only; no number changed

Evidence pointers: `A<n>` = RESEARCH_NOTES.md §10 ledger row; files under `results/` and `docs/PREREG_*.md`.

---

## paper-2026-08-22 — `gmc_v1.tex` (vs `gmc.tex`)

Configuration: **Option B, locked 2026-08-19** (`docs/SHIP_DECISION_2026_08_16.md`) — road-plane ego chain on all three host settings, warm11 mask, no motion EMA, raw cosine, category-weighted additive fusion.

### [method] — configuration changed, experiments re-run

- Warmup validity mask (warm11): frames without full long-gap history abstain instead of fusing garbage (A3). iKUN pooled +0.122.
- Inference-only MotionBuffer EMA removed (A2). +0.022 together with the similarity-ego cleanup.
- Ego estimator replaced: global-ORB homography → **road-plane chain** (Shi-Tomasi corners + pyramidal Lucas-Kanade on the lower half-frame, RANSAC 3 px; global ORB kept only as fallback). Attribution A25; road fit succeeds on 2,065/2,065 eval frame pairs, fallback never fires (`results/road_fallback_rate.json`).
- Fusion: single α → **category weight α_c** (keyword classes MOVING/STATIC → α_mot, APPEARANCE → α_app). LOSO selects (0.7, 0.1) on iKUN (A32); on both FlexHook settings LOSO selects α_mot = α_app (7 / 5), so FlexHook stays single-weight (A35).
- All three hosts unified on the road chain (A37): pooled −0.03 on each FlexHook setting, in exchange the moving-class gain nearly doubles on V1 (+0.49 → +0.67) and quadruples on V2 (+0.048 → +0.184, now t = 5.6).
- Resulting headline numbers: iKUN 44.847 ± 0.107, FH V1 53.980 ± 0.059, FH V2 42.625 ± 0.032 — all three above the hosts' published pooled HOTA.

### [protocol] — evaluation fixed, then re-measured

- FH V1 expression list: 158 (8 malformed entries included) → official 150. Reproduced native moves 53.110 → **53.824 = published**; the "reproduction gap" footnote in the old Table 1 is gone because the gap was an eval-list artifact (A31).
- V2 per-class grouping: paraphrase-slug classification (108/862 misassigned) → canonical `raw_sentence`. MOVING baseline 48.02 → 38.15 and the gain flips from −0.07 to +0.18 (A30, A4).
- FPS: old 68 was a dirty measurement; clean process-only CPU re-measure gives road 31.8 / global 42.8 (A36). Paper reports 31.8.
- LOSO: from a post-hoc robustness check to the selection procedure itself, on a dense un-censored grid (A24, A37). No weight is chosen on the sequence it is evaluated on.
- Ablation re-based at the Option-B operating point, n = 5 (A34): −ego −3.81 MOVING / −0.64 pooled (both t ≈ 11.8), −multiscale −1.85 / −0.32.

### [writing] — text was wrong, code was always right

- §3.2 ego velocity: the old text defined it as the distance between the warped and the *current* centroid — that quantity is the residual, making eq. (residual = raw − residual) self-contradictory. Corrected to the ego displacement $\hat{o}_t - o_{t-g}$ (`gmc_link/manager.py:385`).

### [editorial]

- Layout: `\ninept` enabled; the tikz pipeline figure deleted (duplicated the architecture figure). 6 pages → 5, page 5 references-only.
- Method renamed GMC-Link → **GMC Module** throughout.
- Architecture figure redrawn in Excalidraw (`figures/Architecture.excalidraw`), replacing the PowerPoint source; fixes two mislabeled language-branch vectors, adds the fusion weight to the feedback arrow, draws the host score as a scalar (arrow label) instead of a vector slab.
- Related work: `mlstrack`/`cdrmot`/`tellmewhat` out, STORM in (verified against CVPR 2026 Findings); LTTrack not cited — no verifiable source found.
- Setup: baseline disclosure (reproduced iKUN 44.224 vs published 44.564), both estimators' parameters, seeds/protocol sentence.
- Limitations rewritten to three documented items: road-plane assumption + fallback, keyword misrouting (14/126 V1 direction expressions), FlexHook single-weight degeneration.
- Abstract now carries the headline numbers; 67 red change-markers stripped (PDF text verified identical).
- Kept cut by author decision: trend-explanation paragraph, n=3 hedge, TempRMOT scope paragraph, ablation contribution bullet.

---

## paper-2026-08-19 — `gmc.tex` (vs `paper/latex/mainv3.tex`, the 2026-08-05 MMAsia submission)

ICASSP port of the paper onto the 2026-08-10 simplified configuration ("Option A precursor": 12D, single α, global-ORB similarity chain).

### [method]

- Motion feature 13D → **12D**: the ρ (residual-to-background SNR) slot removed after ablation showed no HOTA cost (professor-directed simplification, 2026-08-10).
- Fusion: per-class recipe $s_{host} + \alpha(sc\cdot\cos + thr)$ with per-host motion/appearance axes (~18 hand-tuned hyperparameters) → **single additive weight** $s_{host} + \alpha\,s_{gmc}$, LOSO-selected (0.5 / 2 / 5). Score-side sigmoid + EMA removed; raw cosine.
- Resulting numbers: iKUN 44.512 ± 0.104, FH V1 53.157 ± 0.022 (against reproduced 53.110), FH V2 42.684 ± 0.058.

### [editorial]

- New ICASSP workspace (`2027_ICASSP/`), spconf template; MMAsia draft frozen as `paper/latex/mainv3.tex`.
- Several analysis paragraphs commented out during the port (LOSO, TempRMOT scope, trend explanation, GPS/IMU); their disposition was settled in the 2026-08-22 pass (issues #23/#24).
