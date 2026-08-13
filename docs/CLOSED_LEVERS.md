# CLOSED_LEVERS.md — falsified experiment directions (veto list)

Compiled 2026-07-05 from memory index. RULE: before proposing any experiment,
scan this file. If the lever family is listed NEG, do not rerun it unless the
user explicitly overrides. Each entry names its memory file — for details:
`grep -ril "<keyword>" /home/seanachan/.claude/projects/-home-seanachan-GMC-Link/memory/`
One-liners here are summaries; when a decision hinges on one, open the memory
file itself.

## Fusion forms (exhausted — hand-tuned linear additive won)

| Lever | Verdict | Memory file |
|---|---|---|
| F1-optimized MLP fusion head | HOTA −3.79 | project_flexhook_learned_fusion_negative |
| Residual additive MLP on iKUN | −1.305 | project_ikun_learned_residual_negative |
| HOTA-direct black-box fusion | = hand exactly; form exhausted | project_hota_direct_fusion_gate_c_negative_2026_06_04 |
| Auto-derive sc via std-matching (variant B) | catastrophic NEG ×3 archs | project_variant_b_std_matching_negative_2026_05_21 |
| Decision-FiLM K-fold | best −1.60 | project_decision_film_kfold_negative_2026_06_02 |
| Learned gate | wins macro, loses pooled | project_learned_gate_v1_holdout |
| Per-class specialist aligners | NEG all 3 archs | project_tier_b1_specialist_negative |
| V1/V2 STATIC recipe split | falsified / inside noise | project_v1_static_recipe_split_negative, project_v2_static_recipe_split_neutral |

## CLIP integration sites (4 closed, 1 POS exception)

| Lever | Verdict | Memory file |
|---|---|---|
| CLIP-visual 64D/128D concat | NEG (feature drowning; HOTA NEG) | project_exp39_* |
| CLIP-text swap | iKUN +0.032 / FH NEG, scale mismatch | project_exp40_cliptext_revisit_mixed |
| Late-concat (exp41) | needed EMA; NEG at sw+no-EMA ship | project_phase1_exp41_gate_negative_2026_05_21 |
| CLIP-logit fusion | NEG all 8 arms | project_exp43_clip_logit_fusion_negative |
| CLIP early-concat at n=3 | NEG all hosts (single-seed had misled) | project_sw_clip_earlyconcat_flat_2026_05_25 |
| **CLIP-L/14 spatial rerank** | **POS +0.690; stack 45.612, iKUN-only** | project_appearance_rerank_clipL14_2026_06_01 |

## Motion representation / features (data-bound at 0.779 ceiling)

| Lever | Verdict | Memory file |
|---|---|---|
| 25D MLP, feature+arch variants (exp36) | all < 0.779; data-bound | project_exp36_series_negative |
| Ego source, EMAP concat, OMF 28D, ORB-grid 61D (exp37 A/B/C) | NEG; Farneback corrupts 13D | project_exp37_* |
| Depth-augmented 17D | iKUN +0.215 sig / FH noise | project_depth_augmented_17d_negative |
| World-XY projection | flat; aligner absorbs unit scale | project_world_xy_projection_neutral |
| Monocular-depth / info-cap ladder | NEG; can't break cap | project_ego_motion_metric_ladder_negative_2026_05_27 |
| Strict motion filter | −0.142; mixed samples teach invariance | project_strict_filter_negative |
| Text encoder swap (BGE-base 768D) | worst of 7; encoder lever falsified | project_exp36d_bge_negative |
| Curriculum, V1+V2 joint train | flat | project_exp36e_*, project_exp36c_* |
| Group-level FNM in stage-1 InfoNCE (GMC_FNM=1, 2026-08-14) | pooled NEG all 3 archs every α>0 (iKUN −0.23 at own peak); same-group negatives load-bearing for STATIC/APPEAR | project_full_audit_2026_08_13 (A1), results/fnm{,_warm11}/ |
| sw-arch search (18 runs), temporal transformer | exhausted / dead | project_autoresearch_aligner_arch_exhausted_2026_06_13, project_seq_encoder_hota_rescreen_flat_2026_06_11 |

## Hosts / trackers / detectors

| Lever | Verdict | Memory file |
|---|---|---|
| Cascade onto TempRMOT (temporal-memory trackers) | −3.8 to −5.4 STRUCTURAL, never | project_exp37_stage_d_tracker_class_dichotomy |
| DDETR detections | data refused 3×; path to 48.84 closed | project_ddetr_data_unavailable |
| ByteTrack / BoT-SORT substitutes | < 40; detector-bound | project_path2_ddetr_public_trackers_negative |
| FH tracker substitute | −5.02 | project_flexhook_tracker_substitute_negative |
| DETR-NS for cascade KUM | NEG | project_phase5g_cascade_detr_negative |
| KUM mode swap (cascade B / xcorr / text-first) | exhausted; cascade B best | project_kum_modes_all_evaluated |

## Other closed families

| Lever | Verdict | Memory file |
|---|---|---|
| Feature-level injection (motion into CLIP) | −21.7% F1 catastrophic | (design decision, CLAUDE.md history) |
| Case 2 variants 1a/1b/1c/1d | all HOTA-NEG; family closed | project_case2_1d_ship_stack_negative |
| CDRMOT consensus aux loss | NEG | project_lever_a_struct_consensus_negative |
| What/where dual cosine | −3.67 | project_lever_b_what_where_negative |
| Grounding-DINO recall gate | fail | project_path_a_grounding_dino_g1_negative |
| Qwen2-VL-2B LVLM calibration | degenerate; 7B blocked on 8GB VRAM | project_path_c_lvlm_calibration_negative |
| Range/depth rerank (front/behind) | cx geometry not depth; LiDAR unlocks nothing at decision layer | project_range_rerank_falsified_2026_06_02 |
| FH + ego integration | Δ=−0.09; ego = iKUN-only lever | project_fh_ego_lean_v2_negative_2026_06_04 |
| Seed-ensemble cache | reproducibility recipe, not gain | project_path_b_ensemble_cache_neutral |
| Turning-verbs recovery (3 levers) | dead | project_turning_verbs_three_lever_exhaustion |

## Still-open positives (the short list)

- CLIP-L/14 spatial rerank stack (iKUN-only): 45.612 = +1.03 vs ship.
- Ego-motion SOTA: iKUN +0.285 (iKUN-only lever; FH NEG).
- Motion classifier: oracle_motion shows +6.13 reachable via classifier alone
  (project_signal_decomp_native_vetoes_gmc_2026_05_26).
- Survey 2026-06-11: V2 SOTA unbeaten; Mamba-trajectory-language unclaimed
  (reference_rmot_2026_survey_levers).
- HOTA-direct learned fusion named by user as future direction
  (feedback_fusion_too_simple_2026_05_30) — note tension with the falsified
  fusion attempts above; requires a genuinely new form, not a rerun.
