# What RMOT papers report beyond the headline HOTA table — and what `gmc_v3.tex` can add

Date 2026-08-30. Source: the user's Zotero library (`~/Zotero`, SQLite + Zotero full-text caches), read
offline — no web pass this round (the web survey agent was stopped by the user). 10 RMOT papers had a
PDF: TransRMOT, iKUN, TempRMOT/Refer-KITTI-V2, FlexHook, DKGTrack, CGATracker, COAL, HFF-Tracker,
C²RMOT, LaMOT. **Not covered (no PDF in Zotero):** DeepRMOT, MLS-Track, EchoTrack, ReferGPT, MEX,
TenRMOT, VMRMOT, STORM, ReaMOT, CRTrack, MGLT, CDRMOT — add them when their PDFs are in the library.
Venues come from Zotero metadata / PDF text and the 2026-08-16 landscape note; two are unverified (see §5).

## 1. Conclusion (ranked by how common it is × how cheap it is for us)

1. **HOTA sub-metrics.** 9/10 papers' main tables show DetA and AssA, 7/10 also DetRe/DetPr/AssRe/AssPr/LocA.
   We show HOTA only. Zero cost — TrackEval already computes them for every run dir (one pooled TrackEval
   call per dir to re-read the summary line). Also carries a mechanism sentence: a score-gating plug-in
   moves DetA/DetRe (which boxes are admitted), not the tracker's association.
2. **Hyper-parameter sensitivity of α.** 5/10 show a sweep table for their key threshold (TransRMOT β_ref,
   iKUN (a,b), DKGTrack β, C²RMOT θ_update, CGATracker n). We have the sweeps on disk (iKUN α∈[0,2] n=3;
   FH V2 α∈{0,1,2,3,5,7,10}); a 3-line table or one small figure. Also documents the flat LOSO optimum.
3. **Generalisation across hosts / trackers / datasets.** FlexHook (4 datasets, 4 detector–tracker combos),
   C²RMOT (3 hosts), iKUN (Refer-Dance). We have 2 hosts × 2 datasets. Cheapest honest addition: the
   already-measured TempRMOT negative (Δ −3.8 to −5.4 HOTA, temporal-memory host) as one analysis sentence —
   the paragraph exists in `gmc_v3.tex` §2 but is commented out.
4. **Efficiency relative to the host.** iKUN Tab. 7 (train/inference time vs TransRMOT), FlexHook Tab. 5
   (total time), CGATracker Tab. III (FPS). We give CPU FPS/ms only; add parameters (aligner **0.63 M**
   trainable; MiniLM 22.7 M frozen) and the module's share of host inference time. Cheap.
5. **Qualitative depth.** 8/10 have qualitative figures, 3 with attention/heat-maps, several with a
   before/after comparison across methods. We have one figure. A second panel — a failure case
   (relative-speed expression, which the 12-D residual cannot resolve) — is medium effort.
6. **Ablation breadth.** Others ablate 3–5 components plus design variants (fusion way, text encoder,
   association, freezing). We ablate 2. Cheap rows from existing runs: two-α vs single-α (routing), and a
   STATIC column in Table 3 (numbers already in the prose).
7. **Statistics.** No paper reports seed spread except TransRMOT (ΔHOTA over three runs); COAL and
   HFF-Tracker fix seed 42 (single run); nobody uses a significance test. Our n=3/5 ± std + Welch is a
   differentiator — say so in one sentence in §4.1.
8. **Protocol disclosure.** TempRMOT/DKGTrack/HFF-Tracker/C²RMOT mark rows "after frame correction" and
   "‡ reproduced with official code"; C²RMOT discloses a −1.6 reproduction gap. We already disclose the
   44.543 vs 44.56 gap and the official 150-expression list; a footnote naming the frame convention
   (`gt_template_old` = iKUN's) closes the last reviewer question.

Not worth it / not applicable: Refer-Dance (static camera → no ego motion; would need iKUN's Refer-Dance
pipeline), LaMOT/BDD (no host outputs), per-sequence tables (nobody does them), IDF1/MOTA (only in iKUN's
MOT table), per-expression-category tables (none of the 10 papers has one — ours is already unusual).

## 2. Papers × content

| Paper (venue) | Datasets | Metrics in main table | Ablations | Per-category | Efficiency | Qualitative | Limitations / failure | Generalisation | Seeds / std | Ego / camera motion |
|---|---|---|---|---|---|---|---|---|---|---|
| TransRMOT (CVPR 2023) | Refer-KITTI | HOTA (±, 3 runs), DetA, AssA, DetRe, DetPr, AssRe, AssPr, LocA | fusion way, association, text encoder, β_ref sweep; data-ratio study (Tab. 4) | ✗ | ✗ | ✓ | ✗ | BDD100K qualitative only | ✓ variance over 3 runs | ✗ |
| iKUN (CVPR 2024) | Refer-KITTI, Refer-Dance, KITTI (MOT) | HOTA, DetA, AssA, DetRe, DetPr, AssRe, AssPr, MOTA, IDF1; "oracle" row | KUM design, NeuralSORT parts, sim-calib (a,b) sweep | ✗ | ✓ Tab. 7 train/infer time (T4 GPUs) | ✓ Fig. 6 | ✓ §4.5 | Refer-Dance (Fig. 5); tracker swap | ✗ | ✗ |
| TempRMOT / Refer-KITTI-V2 (arXiv 2024–25) | Refer-KITTI, -V2, KITTI | HOTA, DetA, AssA, DetRe, DetPr, AssRe, AssPr, LocA ("† after frame correction") | temporal module (Tab. V) | ✗ (dataset statistics only) | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| FlexHook (arXiv 2503.07516; CVPR 2026) | Refer-KITTI, -V2, Refer-Dance, LaMOT | HOTA, DetA, AssA, LocA | components (Tab. 4), enhancement (Tab. 6), freezing (Tab. 7) | ✗ | ✓ Tab. 5 total train/infer time | supp. | ✗ | ✓ 4 datasets, 4 detector–tracker combos (Tab. 2) | ✗ | grid-displacement "feature optical flow" (no ego compensation) |
| DKGTrack (ICCV 2025) | Refer-KITTI, -V2 | HOTA, DetA, AssA, DetRe, DetPr, AssRe, AssPr, LocA ("∗ frame correction", "‡ reproduced") | modules, query init, temperature β sweep | ✗ (motion/static language split is internal) | ✗ | ✓ heat-maps (Fig. 4), comparison (Fig. 5) | ✗ | ✗ | ✗ | ✗ |
| CGATracker (TCSVT 2025) | Refer-KITTI, -V2 | HOTA, DetA, AssA (+ sub-metrics) | modules, n, cascade depth | ✗ | ✓ Tab. III FPS 5.61 vs 5.07 (5 sentences × 3 videos) | ✓ heat-maps + comparisons (Figs. 4–7) | ✗ | ✗ | ✗ | ✗ |
| COAL (arXiv 2026) | Refer-KITTI, -V2 | HOTA, DetA, AssA, DetRe, DetPr, AssRe, AssPr, LocA | ESI/CFL (Tab. 2), HMSI (Tab. 3) | ✗ | ✗ | t-SNE (Fig. 6) | ✗ | ✗ | seed fixed 42 | ✗ |
| HFF-Tracker (venue unverified) | Refer-KITTI, -V2 | full HOTA family ("♣ frame correction") | incremental path table, look-back variants | ✗ | ✗ | ✓ Fig. 6 | ✗ | ✗ | seeds fixed 42 / 2020 | ✗ |
| C²RMOT (OpenReview, anonymous) | Refer-KITTI, -V2 | full HOTA family ("‡ reproduced"; repro gap disclosed) | components, θ_update sensitivity (Tab. 4), contribution (Tab. 5) | ✗ | ✗ | ✓ Fig. 2 | ✗ | ✓ plug-in on TempRMOT / TransRMOT / DKGTrack (Tab. 6) | ✗ | ✗ |
| LaMOT (dataset) | LaMOT | HOTA, DetA, AssA, MOTA, IDF1 | — | per-scenario difficulty (Fig. 5) | ✗ | ✓ Fig. 4 | ✗ | 5 scenarios | ✗ | ✗ |
| **Ours (gmc_v3)** | Refer-KITTI, -V2 | HOTA only | ego, multiscale (n=5, Welch) | ✓ MOVING / STATIC / APPEARANCE | CPU FPS, ms/frame | 1 figure | ✓ §5 | 2 hosts, 3 settings | ✓ n=3/5 ± std, Welch | ✓ core topic |

## 3. Gap list with feasibility

| # | Addition | Who does it | Form | Cost for us | Data already on disk |
|---|---|---|---|---|---|
| 1 | DetA / AssA (+ LocA) columns for native vs +GMC, 3 settings | 9/10 | Table 1 extra columns (FlexHook style: HOTA/DetA/AssA/LocA) | ~24 pooled TrackEval calls, no inference | all run dirs (`*_mkw/am1.0_aa0.1`, FH `alpha7.0`/`alpha5.0`, natives) |
| 2 | α sensitivity: pooled + MOVING HOTA vs α | 5/10 | 1 small figure or 3-row table | iKUN: sweep dirs exist (single α, routing-invariant) — MOVING needs the A43 regroup (TrackEval only); FH V2: `alpha{0,1,2,3,5,7,10}` full-test dirs exist; FH V1: only α=7 + LOSO folds (folds are not full-test — say so or skip V1) | `results/official150/ikun_official150.json` sweep block; `hota_eval_flexhook_v2_raw_gmc_sw12d_groad_seed*_warm11/alpha*` |
| 3 | TempRMOT negative result (temporal-memory host) | FlexHook / C²RMOT report multi-host | one sentence in §4 or §5 | none — numbers in memory/RESEARCH_NOTES (Δ −3.8 to −5.4, two trials); paragraph exists commented-out in §2 | yes |
| 4 | Parameters + share of host time | 3/10 | one sentence or 2-row table | aligner 0.63 M trainable (this note), MiniLM 22.7 M frozen; host share = ours 6.7 ms vs host per-frame time (measure host once, or quote iKUN Tab. 7) | `results/fps_profile.json` |
| 5 | Two-α vs single-α row | — (our design) | Table 3 row "single α (LOSO 0.35)" | single-α LOSO already done on official-150 (A42: α*=0.35); its full-test dirs exist; MOVING needs A43 regroup | `groad_seed*/alpha0.35` |
| 6 | STATIC column in Table 3 | — | column | none (numbers in §4.3 prose) | yes |
| 7 | Statistics sentence | differentiator | §4.1 one sentence | none | — |
| 8 | Frame-convention footnote | 4/10 mark it | footnote to Table 1 | none | `project_gt_template_two_conventions` |
| 9 | Failure-case panel ("faster than ours" / "turning") | limitations prose common; figures rare | Fig. 2 second row | medium (render frames + scores) | caches + predictions exist |
| 10 | Oracle / upper bound (GT boxes as input) | iKUN "oracle" row | one sentence | moderate: prior measurement (44.549 vs 44.656) is on the old sim chain; re-measure on the road chain for consistency | `results/gtoracle/` (old chain) |
| 11 | Text-encoder ablation | TransRMOT Tab. 3(c) | row | expensive (train 5 seeds × build caches); prior single-seed negatives exist (BGE, CLIP-text) | partial, old chains |
| 12 | Refer-Dance / LaMOT | FlexHook, iKUN | table | expensive and off-topic (static camera) | no |

Recommended set for v3: **1, 2, 3, 4, 6, 7, 8** (all TrackEval/prose; ≤ 1 day), then 5, then 9 if space.
ICASSP page budget (4 + refs) is the binding constraint: 1 and 6 widen existing tables; 2 costs a
figure; 3, 4, 7, 8 cost one sentence each.

## 4. Statistical practice in the field

- Seed spread reported: TransRMOT only ("ΔHOTA presents score variance over three runnings", Tab. 2).
- Fixed single seed stated: COAL (42), HFF-Tracker (42 train / 2020 inference).
- Significance tests: none of the 10.
- Reproduction disclosure: DKGTrack, HFF-Tracker, C²RMOT, TempRMOT mark reproduced rows; C²RMOT states its
  −1.6 HOTA gap vs the published TempRMOT number.
→ Our n=3/5 ± std with Welch t on the ablation is stronger than any of the 10; worth one explicit sentence.

## 5. Sources and verification log

All texts read from `~/Zotero/storage/<attachment>/.zotero-ft-cache` (Zotero's own PDF text index); item
metadata from `~/Zotero/zotero.sqlite`.

| Paper | Zotero item / attachment | Venue basis |
|---|---|---|
| TransRMOT | 18 / F73YYLS8 | Zotero 2023 (CVPR 2023, known) |
| iKUN | (parent of AWDESRA3) | Zotero 2024 (CVPR 2024, known) |
| TempRMOT ("Bootstrapping RMOT") | 16 / MTJYITW9 | Zotero 2025 arXiv (TABLE I–V journal format) |
| FlexHook | 22 / N2NKLUN9 | arXiv 2503.07516; CVPR 2026 per 2026-08-16 landscape note |
| DKGTrack | 24 / UGGUK7SS | ICCV 2025 per 2026-06-11 survey note; PDF has ICCV page numbers |
| CGATracker | 2 / LDRRVK3V | Zotero: IEEE TCSVT 2025 |
| COAL | 1 / 8GXC8KGE | Zotero: arXiv 2026 |
| HFF-Tracker | 23 / BD2V3DBP | **unverified** — Zotero has no date/venue; AAAI-style page numbers in PDF |
| C²RMOT | 306 / ID78E2NP | OpenReview submission (anonymous); Zotero date field "2017" is wrong |
| LaMOT | 260 / V53UXSJV | dataset paper; venue not in Zotero |

Not verified this round (needs web): exact venues for HFF-Tracker, LaMOT, TempRMOT journal; every number
above is quoted from the PDF text, none is invented. Papers without PDFs in Zotero are not characterised.

## 6. Decision 2026-08-30 — observation → proposal → status (record A44)

| # | Observed in other papers | Proposal for `gmc_v3.tex` | Status |
|---|---|---|---|
| A | 9/10 main tables show DetA/AssA (7/10 also DetRe/DetPr/AssRe/AssPr/LocA): TransRMOT Tab. 2, iKUN Tab. 1, TempRMOT Tab. III/IV, FlexHook Tab. 1, DKGTrack Tab. 1/2, CGATracker Tab. I/II, COAL Tab. 1, HFF Tab. 1/2, C²RMOT Tab. 1/2 | Table 1 → HOTA / DetA / AssA, native → +GMC per host; one sentence that the gain sits in DetA (gating) | **DONE** (A44) — `results/moving_kw/submetrics.json`: iKUN ΔDetA +0.87 / ΔAssA +0.46; FH V1 +0.15/+0.15; FH V2 +0.12/+0.04 |
| B | 5/10 sweep their key hyper-parameter in a table: TransRMOT Tab. 3(d) β_ref, iKUN Tab. 5 (a,b), DKGTrack Tab. 5 β, C²RMOT Tab. 4 θ_update, CGATracker Tab. V/VI | small α table (α = 0 / α* / neighbours / grid max) for all three hosts, pooled + MOVING; FH V1 sweep run on the official list (15 fusions) | **DONE as data** (A44) — `results/moving_kw/alpha_sweep_mkw.json`; FH V1 sweep run (15 fusions). **Not in the paper**: the 5-row table pushed the text ~30 lines over the 4-page limit; user decision Z retracted it rather than cut original prose |
| E | ablation tables compare design alternatives, not only removals: TransRMOT Tab. 3(a,b), iKUN Tab. 3, FlexHook Tab. 4, C²RMOT Tab. 5 | Table 3 row "single α = 0.35 (LOSO)", n=5, quantifying the two-α routing | **DONE** (A44; Table 3 row) — 44.95±0.11 / MOV 32.42±0.25 / STA 44.35±0.06 (n=5) |
| F | ablation tables carry all metrics (DKGTrack Tab. 3, COAL Tab. 2) rather than prose | Table 3 STATIC column (numbers already in §4.3) | **DONE** (A44) |
| C | plug-in papers show several hosts: C²RMOT Tab. 6 (TempRMOT/TransRMOT/DKGTrack), FlexHook Tab. 2 (4 detector–tracker pairs), iKUN (tracker swap) | one §5 sentence: on TempRMOT (recurrent memory) an earlier module configuration lost 3.8–5.4 HOTA → claim restricted to two-stage hosts | **RECORD ONLY** (draft in plan; author decides; ~3 lines) |
| D | efficiency tables: iKUN Tab. 7 (train/infer time), FlexHook Tab. 5 (total time), CGATracker Tab. III (FPS) | §4.1 clause: 0.63 M trainable parameters (MiniLM 22.7 M frozen, one encode per expression) | **RECORD ONLY** (~1 line) |
| G | seed spread only in TransRMOT (ΔHOTA over 3 runs); COAL/HFF fix seed 42; no significance tests anywhere | §4.1 sentence stating our n=3/5 ± std + Welch vs single-run prior work | **RECORD ONLY** (~1 line) |
| H | TempRMOT/DKGTrack/HFF/C²RMOT mark "after frame correction" / "‡ reproduced"; C²RMOT discloses −1.6 repro gap | Table 1 footnote naming the iKUN frame convention (`gt_template_old`; TransRMOT convention −6.4) | **RECORD ONLY** (~2 lines) |
| — | qualitative depth (8/10; heat-maps in 3) | second qualitative row: failure case (relative-speed expression) | DEFERRED (page space) |
| — | iKUN Tab. 1 "oracle" row | GT-box oracle sentence, re-measured on the road chain | DEFERRED (new runs) |
| — | TransRMOT Tab. 3(c) text encoders | text-encoder ablation row (prior single-seed negatives: BGE, CLIP-text) | DEFERRED (5-seed retrain) |

Page accounting for the DO set: A 0–1 lines, B ≈ 8, E 1, F 0 (−2 if the §4.3 STATIC sentence is dropped);
page 4 has ≈ 4 free lines, so the author cuts ≈ 5–9 lines elsewhere or the α table reverts to record-only.
