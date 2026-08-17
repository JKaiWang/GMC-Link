# 實驗 runbook — FlexHook 雙-α LOSO + FPS 乾淨重量(2026-08-18)

在 Linux 主機 `/home/seanachan/GMC-Link` 執行。這份文件從頭到尾照做即可。

## 為什麼要跑

Ship 已定 **Option B(路面鏈 + 雙 α)**,但 Option B 只在 iKUN 驗證過:

- A32:iKUN pooled **44.847 ± 0.107**(+0.191 vs 單-α ship,t=2.50);MOVING **32.606 ± 0.654**(+2.56, t=6.7)
- sim 鏈 × 雙-α 對照 = 平的(+0.016, t=0.34)→ 增益來自 road × 雙-α 的**組合**

FlexHook V1/V2 目前仍是 sim 鏈 + 單 α(54.011 @α=7 / 42.658 @α=5)。
論文方法要三個 host 一致,所以先補跑 FH 的雙-α LOSO。

FPS 也要重量:論文現稿寫 68 FPS(13D 舊管線),現有的 48.0 / 35.3 是**機器有負載時**量的
(A34 自己標註「論文前重量乾淨版」)。

---

## 0. 前置檢查(5 分鐘)

```bash
cd /home/seanachan/GMC-Link && git status && git log --oneline -3

# FH 的路面鏈 cache(A27 跑過,應該在)
ls -d results/ground_road_fh_v1 results/ground_road_fh_v2
ls gmc_link_weights_v1train_sw12d_groad_seed{0,1,2}*.pth 2>/dev/null
ls -d hota_eval_flexhook_phase5_gmc_sw12d_groad_seed0_warm11 2>/dev/null
ls -d hota_eval_flexhook_v2_raw_gmc_sw12d_groad_seed0_warm11 2>/dev/null

# 官方 150 句名單(A31)
wc -l ~/FlexHook/seqmaps/kitti-1.txt   # 應為 150
```

若 FH 的 `_sw12d_groad_seed{N}_warm11` cache 不在,先重建:

```bash
for s in 0 1 2; do
  GMC_GROUND_MODE=road \
  GMC_WEIGHTS=gmc_link_weights_v1train_sw12d_groad_seed${s}.pth \
  GMC_SUFFIX=_sw12d_groad_seed${s}_warm11 \
      python run_build_gmc_cache_flexhook.py
  GMC_GROUND_MODE=road \
  GMC_WEIGHTS=gmc_link_weights_v1train_sw12d_groad_seed${s}.pth \
  GMC_SUFFIX=_sw12d_groad_seed${s}_warm11 \
      python run_build_gmc_cache_flexhook_v2_raw.py
done
```

---

## 1. 程式修改(4 個檔,約 1 小時)

雙-α 目前只有 iKUN 有。參考實作:`run_ikun_linear_additive.py:95-125`(路由融合)
與 `:176-206`(argparse + tag + result.json 欄位)。

### (a) `run_flexhook_phase5_gmc_sweep.py`(FH V1)

1. argparse 加 `--alpha-mot` / `--alpha-app`,與 `--alpha` 互斥(照抄 iKUN 的驗證邏輯:
   兩個都給、或都不給,不可混用)。
2. `gen_predicts()` 的融合式(L128 `if margin + alpha * gmc > 0.0`)改路由:

   ```python
   a_expr = alpha if alpha_app is None else (
       alpha if classify(expr) != "APPEARANCE" else alpha_app)
   ```

   `classify()` 該檔 L48 已有,直接用,不必新寫。
3. 輸出目錄 tag(L199 `tag = f"alpha{args.alpha}"`)改成雙-α 時用 `am{mot}_aa{app}`;
   單-α 維持 `alpha{a}` 不變(不可破壞既有 result.json 路徑)。
4. `result.json` 增 `alpha_mot` / `alpha_app` 兩個欄位。
5. **官方 150 句名單**:加環境變數 `FH_OFFICIAL_SEQMAP=<path>`。
   在寫 seqmap 前(L137-139)先與官方名單取交集。
   A31 原本做法是 TrackEval-only rescore;改成生成時就過濾,結果等價且少一步。
   正確性由第 2 節的 α=0 整合性閘把關(必須精確等於 53.824)。

### (b) `run_flexhook_v2_raw_sweep.py`(FH V2)

同 (a) 的 1–4 點。**不需要** `FH_OFFICIAL_SEQMAP` —— V2 名單本來就與官方一致(862 = 862)。

### (c) `run_two_alpha_sweep.py`

目前硬寫 iKUN(`OUT_ROOT`、`FOLDS`、runner 腳本名、對角 α=0.5)。加 `--arch {ikun,fh_v1,fh_v2}`:

| arch | runner | OUT_ROOT | FOLDS | 對角整合性 α |
|---|---|---|---|---|
| ikun | `run_ikun_linear_additive.py` | `hota_eval_ikun_linear_additive` | 0005 / 0011 / 0013(3 折) | 0.5 |
| fh_v1 | `run_flexhook_phase5_gmc_sweep.py` | `hota_eval_flexhook_phase5_gmc` | 0005 / 0011 / 0013(3 折) | 7 |
| fh_v2 | `run_flexhook_v2_raw_sweep.py` | `hota_eval_flexhook_v2_raw_gmc` | 0005 / 0011 / 0013 / 0019(4 折) | 5 |

- 對角整合性檢查(L52-66)現在硬寫 `0.5`,改成用 arch 對應的 α,ref 路徑 `alpha{a}/result.json`。
- 選點邏輯(componentwise median + 軸 censoring,L79-97)**不動**。

### (d) 新增 `docs/PREREG_TWO_ALPHA_FH_2026_08_18.md`

Repo 慣例:**跑之前先 commit**。內容照第 2 節抄。

---

## 2. 預先登記內容(跑之前 commit)

**動機**
iKUN 已採 road × 雙-α(A32)。FlexHook 尚未在同一配置下量測,論文方法需三 host 一致。

**配置**
- 主臂:路面鏈 caches `_sw12d_groad_seed{N}_warm11` × 關鍵字路由雙-α
- 對照臂:sim 鏈 caches `_sw12d_seed{N}_nomema_warm11` × 雙-α(對應 A32 的 sim control)

**格點**
- FH V1:`--am 3,5,7,10,15 --aa 0.5,1,2,3,5`
- FH V2:`--am 2,3,5,7,10 --aa 0.5,1,2,3,5`

**整合性閘(halt condition)**
1. α = 0 必須精確重現 native:FH V1(官方名單)**53.824**;FH V2 **42.526**
2. 對角 α_mot = α_app = α\* 必須與現有單-α 結果 bit-exact:V1 @7 = **54.011**;V2 @5 = **42.658**

任一項不過 → **停,查因,不得讀取任何 α > 0 的結果**。

**選點規則(與 A32 相同)**
LOSO per-fold pooled argmax → componentwise median。
某軸的 argmax 落在該軸格點最大值 = censored。
某軸未 censored 的 fold < 2 → 該軸 unresolved(腳本回傳 `null`)。

**採用門檻(pre-registered)**
full-test pooled 必須超過現行單-α ship + 2σ:

| Host | 現行單-α ship | 門檻 |
|---|---|---|
| FH V1 | 54.011 ± 0.025 (α=7) | **> 54.061** |
| FH V2 | 42.658 ± 0.030 (α=5) | **> 42.718** |

**未達門檻怎麼寫(事先講死,避免事後選擇)**
報告 LOSO 選到對角 / 未達門檻,論文 FlexHook 兩列以單-α 呈現,
方法段寫「per-host LOSO 在 FlexHook 上選到 α_mot = α_app,退化為單一 α」。
這仍是誠實且方法一致的敘事。

---

## 3. 跑 FH V1(主臂)

```bash
cd /home/seanachan/GMC-Link
export FH_OFFICIAL_SEQMAP=$HOME/FlexHook/seqmaps/kitti-1.txt
mkdir -p logs
nohup python run_two_alpha_sweep.py --arch fh_v1 \
    --suffix-template _sw12d_groad_seed{seed}_warm11 \
    --am 3,5,7,10,15 --aa 0.5,1,2,3,5 --seeds 0,1,2 \
    --out-dir results/two_alpha_road_fh_v1 \
    > logs/two_alpha_fh_v1.log 2>&1 &
```

規模:3 folds × 25 cells × 3 seeds = 225 次評測 + 對角檢查 + 3 次 full-test。
以 A32 的 iKUN campaign(270 次)為參考,**估數小時,建議過夜**。
腳本會 skip 已存在的 `result.json`,可中斷續跑。

進度:`tail -f logs/two_alpha_fh_v1.log`(每個 cell 完成印一行 `hold00XX am=A aa=B done`)。

---

## 4. 跑 FH V2(主臂)

```bash
nohup python run_two_alpha_sweep.py --arch fh_v2 \
    --suffix-template _sw12d_groad_seed{seed}_warm11 \
    --am 2,3,5,7,10 --aa 0.5,1,2,3,5 --seeds 0,1,2 \
    --out-dir results/two_alpha_road_fh_v2 \
    > logs/two_alpha_fh_v2.log 2>&1 &
```

規模:4 folds × 25 cells × 3 seeds = 300 次 + 對角 + 3 次 full-test。比 V1 更久。

---

## 5. sim 鏈對照臂(只在主臂過門檻時才需要)

用來複製 A32 的論證:「不是雙-α 單獨有效,是 road × 雙-α 的組合」。

```bash
python run_two_alpha_sweep.py --arch fh_v1 \
    --suffix-template _sw12d_seed{seed}_nomema_warm11 \
    --am 3,5,7,10,15 --aa 0.5,1,2,3,5 --out-dir results/two_alpha_sim_fh_v1

python run_two_alpha_sweep.py --arch fh_v2 \
    --suffix-template _sw12d_seed{seed}_nomema_warm11 \
    --am 2,3,5,7,10 --aa 0.5,1,2,3,5 --out-dir results/two_alpha_sim_fh_v2
```

---

## 6. FPS 乾淨重量(30 分鐘,機器必須閒置)

```bash
uptime && nvidia-smi 2>/dev/null | head -15    # 先確認閒置,load average 應接近 0
cd /home/seanachan/GMC-Link
for rep in 1 2 3; do
  GMC_MODEL=similarity python profile_inference.py --seq 0011 --n 500 \
    >> logs/fps_clean_rep${rep}.log 2>&1
done
```

`profile_inference.py:31-37` 用 `GMC_GROUND_MODE=road` 切模式,兩模式(sim / road)一次跑完。
取 3 次的**中位數**,同時保留 `fps_process_only` 與 `fps_incl_io` 兩組數字,
覆寫 `results/fps_profile.json`。

參考(有負載時量的舊值,要被取代):sim 48.0 FPS / road 35.3 FPS(process-only, 200 幀)。

---

## 7. 驗證(讀結果前先檢查)

1. 整合性閘全過(第 2 節的 1、2)。
2. `two_alpha_campaign.json` 的 `am_star` / `aa_star` **不可為 `null`** —— null 代表該軸 unresolved。
3. full-test pooled 對門檻:**V1 > 54.061**、**V2 > 42.718** 才算採用。
4. FPS 三次重複的離散度 < 5%,否則機器仍有負載,重量。

```bash
python3 -c "
import json
for a in ['fh_v1','fh_v2']:
    d=json.load(open(f'results/two_alpha_road_{a}/two_alpha_campaign.json'))
    print(a, 'folds', d['fold_argmaxes'], 'star', d['am_star'], d['aa_star'])
    print('  full', d.get('full_test_at_star',{}).get('aggregate'))
"
```

---

## 8. 帶回來的東西(commit + push,論文才能寫)

1. `results/two_alpha_road_fh_v1/two_alpha_campaign.json`
2. `results/two_alpha_road_fh_v2/two_alpha_campaign.json`
3.(選)`results/two_alpha_sim_fh_v{1,2}/two_alpha_campaign.json`
4. 更新後的 `results/fps_profile.json`
5. `RESEARCH_NOTES.md` §10 新增 A35(FH 雙-α)、A36(FPS 乾淨重量)兩列
6. `docs/PREREG_TWO_ALPHA_FH_2026_08_18.md`

---

## 附:數字回來後論文要改什麼(下一輪,不在這份 runbook 內)

- Method 加路面鏈定義(`gmc_link/core.py:54-94`)+ 雙-α 路由式
- Setup 刪 FH V1 reproduction-gap,改「官方 150 句協議」(A31)
- Table 1 / 2 / 3 全換 Option B 數字;V2 用 **canonical** 分類(baseline 38.154, +0.048)
- **消融結論翻轉**:−multiscale 由「不顯著 p=0.22」變顯著(Option B:MOVING t=6.2, pooled t=6.7)
- Abstract / Intro 的 `+4.42` → `+7.08`
- FPS 填第 6 節的乾淨值(現稿 68 FPS 作廢)
- Related work 補 JustHook / STORM / LTTrack 三筆引用(host 名字全文維持 FlexHook)
