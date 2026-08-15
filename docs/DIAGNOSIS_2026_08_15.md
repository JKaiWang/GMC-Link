# GMC-Link 系統診斷書（2026-08-15）

依據：2026-08-13 全管線審計（A1-A11）＋ 2026-08-14/15 實驗戰役（A12-A18）。
每條判決附量測證據；無臆測。管線五層逐層審。

```
Detection → Tracking → Motion Representation → Language Alignment → Fusion/Decision
```

---

## 第 1 層：Detection / Tracking（host 端）

**判決：detector-bound，且是全系統最大的單一上限，但路徑關閉。**

- 公開偵測器全滅：ByteTrack/BoT-SORT 替換 < 40 HOTA（vs ship ~44.6）；paper 的
  48.84 需要 DDETR 私有輸出，取得三次被拒。誠實 pooled 天花板 ≈ 44.6（YOLOv8-NS 上）。
- Oracle detection（GT boxes 全管線）從未跑過——審計後補的唯一未做 oracle；
  但替代證據（上行）已足以定性。
- 對 GMC 的意義：我們的模組活在 host 的偵測品質之下，這層不可歸咎於 GMC。

## 第 2 層：Ego-motion 估計

**判決：已解到物理極限，關閉。終點形態 = ORB1500 + similarity 4-DOF + 逐幀連乘 + warmup abstention。**

- 估計品質不是瓶頸：中位 inlier 殘差 0.9px（亞像素）；8 種偵測器/估計器組態
  （AKAZE/BRISK/SIFT/ORB3000/5000/MAGSAC）無一 Pareto 贏過 ship（A12）。
- 真正的牆是**深度視差**：靜止物體級 ego 誤差 3-57px——與估計誤差差兩個數量級；
  任何全域 2D 變換原理上不可修（A14）。解釋 oxts 完美 ego 只值 +0.285、
  單目深度階梯 NEG 的舊墓碑。
- 狂野 H 尾巴（1% 幀、最大 5592px）由 similarity 4-DOF **構造性消滅**（0/916），
  同速度、零門檻（A13）。
- 連乘 > 直接寬基線估計（每個 gap、每個 seq；A14 裁判實驗）——「累積誤差」假說否證。
- 訓練端的髒 ego 是 load-bearing 資料增強：修乾淨反而 −0.20 pooled（A15/D2）。
- Ground-plane 機制（接地點+road-H）：篩選層砍半高視差殘差（0005 −50~60%），
  HOTA 審判進行中——這層唯一未結案項。

## 第 3 層：Motion Representation（12D）

**判決：對「2D 影像運動學所能承載的資訊」而言近乎完備；缺的是資訊源，不是編碼器。**

- 時序視窗資訊存在（moving 0.768→0.873、counter 0.687→0.794，T=1→16），
  但現行 12D 內建多尺度已吃掉 75-85%（ship12-T1 = 0.845/0.770/0.932）；
  殘餘 headroom +0.02-0.03（A16）。
- **時序「順序」資訊 = 零**：shuffle 與 ordered 到小數第四位全等、每個任務——
  GRU/Transformer/Mamba 沒有東西可學，資訊層級關閉（A16）。
  2026-06-11 的 HOTA 收斂擊殺（temporal_transformer 平、window_stats NEG）得到解釋。
- 未來位置預測 T=4-8 飽和（43.8→25.7px）——gap {2,5,10} 設計被追認（A16）。
- **turning 是資訊缺席**：影像平面任何 T、任何 readout ≈ 0.54-0.62；
  oracle GT 3D 世界航向到 **0.718**（假說 B 部分成立：資訊在世界系）；
  但連 GT 3D 都只到 0.72——**expression 標註是 track 級**（轉彎車全軌跡都標
  turning，直行段全是 label noise），標註粒度是不可歸咎於 representation 的
  殘餘上限（A18）。
- counter-direction 是**場景相對**概念：絕對世界航向讀不出（oracle 0.622），
  影像系車道位置＋方向早已編碼（gmc 0.808）——影像表示無罪（A17/A18）。
- 部署 turning 增益需單目逐物體 3D 航向估計：重模組、破 plug-in 敘事、
  HOTA EV ~+0.1-0.3（小表達子集×fusion 瓶頸×iKUN-only）→ 本篇不做，下篇方向。

## 第 4 層：Language Alignment

**判決：representation-bound（沿用舊結論），且兩個「理論修正」實測有毒。**

- 0.779 pool-AUC 上限：18 種架構、7 種特徵、編碼器替換全滅（歷史結論，仍然成立；
  且 pool-AUC 與 HOTA 脫鉤——per-frame 條件訊號才是有效成分）。
- FNM（補上遮罩）全 arch 全 α NEG（iKUN 峰值 −0.23）：同組 in-batch 負樣本是
  STATIC/APPEAR 判別的必要壓力（A1 結案）。
- 訓練端 ego 修乾淨 NEG（A15）：髒訓練 = 視差不變性的免費教材。
- V2 paraphrase 文本域：862 條改寫句 vs 只看過 V1 句式的 aligner——
  V2 反常謎題的候選主因（未完全定案，canonical 分組已修掉報表層的混淆）。

## 第 5 層：Fusion / Decision

**判決：形式窮盡；single-α 是量化過的 Pareto 妥協；host veto 是 load-bearing 的。**

- 學習式融合 5 連敗（F1-MLP −3.79、殘差 MLP −1.305、HOTA-direct=手調、
  FiLM −1.60、learned gate pooled 輸）；std-matching 自動導出災難性 NEG ×3。
- oracle_motion +6.13 / oracle_appear +13.3 的缺口存在，但出路是**更好的分數**
  （上游），不是更好的融合形式（這層）。
- 每類最適 α 分歧（iKUN APPEAR 峰值 α=0.2、MOVING α=1.0）——two-α 中間點
  未測（PARTIAL，需教授同意，LOSO 先例不利 pooled 回收）。
- Appearance 災難（46/119 表達、73% GT）是 host-CLIP 層問題，GMC 無罪；
  已驗證的解（CLIP-L/14 rerank +0.7）off-story。

---

## 總表：病灶 → 歸屬 → 狀態

| 病灶 | 歸屬層 | 狀態 |
|---|---|---|
| 偵測品質上限（~44.6 pooled 天花板） | 1 Detection | 路徑關閉（DDETR 不可得） |
| 深度視差（ego 誤差 3-57px） | 2 Ego | 物理極限；ground-plane 部分繞過（HOTA 審判中） |
| warmup 垃圾 25% 幀 | 2→3 交界 | **已修**（warm11，+0.12 iKUN） |
| 狂野 H 尾巴 1% | 2 Ego | **已修**（similarity 4-DOF，構造性） |
| turning 資訊缺席 | 3 Representation | 資訊在世界系（oracle 0.72）＋標註粒度上限；下篇方向 |
| 時序編碼器空間 | 3 Representation | **不存在**（順序資訊=0）；關閉 |
| aligner 0.779 上限 | 4 Alignment | representation-bound；與 HOTA 脫鉤，不追 |
| V2 paraphrase 域偏移 | 4 Alignment | 候選主因，報表層已修（canonical 分組） |
| 融合形式 | 5 Fusion | 窮盡；single-α 保留；two-α 待教授 |
| appearance 災難 | 1+5（host CLIP） | GMC 無罪；rerank +0.7 备用（off-story） |
| host-native veto | 5 Decision | load-bearing，不可拆（un-veto 全 NEG） |

## 一句話診斷

**系統不是「GMC 不夠好」：ego 估計已到物理極限、12D 表示已近資訊完備、融合形式已窮盡。
剩餘的真實缺口按大小排序 = 偵測品質（路關閉）＞ appearance host 判分（rerank 可解但
off-story）＞ turning 世界航向（下篇）＞ two-α 中間點（待拍板）。本篇論文的正確姿態是
把已收割的（warm11＋similarity＋刪 EMA，iKUN +0.144）鎖進 ship、用診斷數據防禦審稿，
把 turning/世界系/標註粒度寫成 future work 的具體路標。**
