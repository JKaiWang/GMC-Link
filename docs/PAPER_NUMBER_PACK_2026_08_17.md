# 論文數字包(2026-08-17)— gmc.tex 不在此修改;寫作由用戶發起

兩個 ship 選項的完整替換值。老師勾選後,取對應欄位。
出處:RESEARCH_NOTES §10 A22–A34;pre-reg `docs/PREREG_*.md`;數據 `results/`。

## Table 1(主結果,pooled HOTA,n=3)

| Host | native | 選項 A | 選項 B | 發表值對照 |
|---|---|---|---|---|
| iKUN | 44.224 | 44.656 ± 0.078 (α=0.5) | **44.847 ± 0.107** (α_mot=0.7, α_app=0.1) | paper-pure 44.564 |
| FlexHook V1(官方 150 句協議) | **53.824(≡發表值)** | 54.011 ± 0.025 (α=7) | 同 A | 發表值 53.824 |
| FlexHook V2 | 42.526(≡發表值) | 42.658 ± 0.030 (α=5) | 同 A | 發表值 42.526 |

iKUN per-class(native → A → B):MOVING 25.531 → 30.045 → **32.606**;
STATIC 43.914 → 44.448 → 44.584;APPEAR 46.346 → 46.572 → 46.468。

V2 per-class(canonical 分類,A30):MOVING +0.048 / STATIC +0.294 /
APPEAR +0.125 / DIRECTION +0.021(全非負)。

## Table 2(消融,iKUN,n=5,固定各選項 LOSO 選點)

| 配置 | 選項 A pooled | A MOVING | 選項 B pooled | B MOVING |
|---|---|---|---|---|
| full | 44.649 ± 0.087 | 30.102 ± 0.132 | 44.803 ± 0.103 | 32.295 ± 0.632 |
| −ego | 44.251 ± 0.128 **(−0.398, t=5.8)** | 28.213 **(−1.89, t=15.9)** | 44.166 ± 0.065 **(−0.637, t=11.7)** | 28.489 **(−3.81, t=11.8)** |
| −multiscale | 44.442 ± 0.097 (−0.207, t=3.6) | 29.330 (−0.77, t=2.9) | 44.485 ± 0.024 (−0.318, t=6.7) | 30.449 (−1.85, t=6.2) |

## FPS(CPU;負載中量測,論文前重量乾淨版)

sim 鏈 48.0 FPS / road 鏈 35.3 FPS(process-only,seq 0011,200 幀)。

## 措辭修改清單(寫作期執行)

1. **刪除** FH V1 reproduction-gap 段落 → 改「evaluated on the host's official
   150-expression protocol」(A31);FH V1 α\* 2→7
2. V2 表格改用 canonical 分類行(A30);slug 分類作廢
3. A25 機制措辭:歸因已證(road chain),「繞過深度視差」降為假說
   + 引 A29 訊號證據(0011 判別力 6×,seq-scoped)
4. Oracle 結論 scope:「decision-level plug-in 體制內」的實用上限(A22/A26)
5. 若選 B:方法節加 road 鏈定義 + 句型路由公式一行;robustness note
   (fold 異質性 {0.2,1.5,0.5} 同型存在於兩鏈,median 規則吸收)
6. Related work 增補:JustHook(= FlexHook 定稿名,CVPR 2026)、STORM(CVPR 2026,
   MLLM 端到端)、LTTrack(PatCog 2026);VMRMOT 已引
7. 不寫「突破天花板」——iKUN vs paper-pure 44.564 寫 parity(A)或 +0.28(B,~2σ)
8. 部署段:per-class 全正 + FPS 數字 + MOVING = 安全攸關子集論述
