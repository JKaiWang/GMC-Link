# DATA.md — dataset paths and GT conventions

Extracted from CLAUDE.md 2026-07-05.

## Paths

- Refer-KITTI dataset: `/home/seanachan/data/Dataset/refer-kitti-v2`
  (also symlinked as `refer-kitti/` and `Refer-KITTI/`)
- Full annotation JSON: `Refer-KITTI_labels.json`
- iKUN precomputed scores: `iKUN/`
- NeuralSORT track detections: `NeuralSORT/`

## GT template — TWO conventions (landmine; corrected 2026-04-30)

Both dirs live under the dataset symlink, NOT at repo root:
`refer-kitti/gt_template_old/` and `refer-kitti/gt_template/`
(→ /home/seanachan/data/Dataset/refer-kitti/). Run scripts hardcode the full
path internally; a bare `ls gt_template_old` at repo root fails — that is
expected, not a missing dir.

- `gt_template_old/` = **paper-iKUN-canonical**. Frame numbering aligns with
  NeuralSORT tracker `predict.txt`. Reproduces paper README 44.56 HOTA at
  44.224 (cascade+simcalib YOLOv8-NS, 3-seq pooled).
  **USE THIS for any iKUN-paper comparison.**
- `gt_template/` = 2026-04-16 TransRMOT-convention regeneration. Frame
  numbering off-by-one vs NeuralSORT. Using it drops HOTA ~6.4 from
  gt-prediction misalignment (NOT a free eval improvement). Only for
  TransRMOT-style tracker outputs.
- The old note "fix closed ~10-point HOTA gap" was misleading — it conflated
  the two label spaces. NeuralSORT lives in gt_template_old's convention.

## Split & label facts (from memory, verified)

- Paper numbers 44.56 / 48.84 are 3-seq POOLED HOTA
  (`project_referkitti_v1_split_conventions`).
- 48.84 requires DDETR detections — refused 3×, path closed
  (`project_ddetr_data_unavailable`). 44.564 is the ceiling on YOLOv8-NS.
- V1 labels are clean (0% noise after legend fix); V2 labels == V1 labels
  plus a paraphrase layer.
- Seq 0013 has only 2 expressions — per-seq numbers there are noise.
  Seq 0011 is systematically the worst per-seq.
