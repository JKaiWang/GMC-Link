# 論文變更記錄

每個論文快照(= release tag)一段,新的在上。每一條都掛標籤:

- **[方法]** — 模組本身改了;受影響的數字全部重測
- **[協議]** — 評測方式有錯或不乾淨;修正後重測
- **[筆誤]** — 稿子寫錯,程式一直是對的
- **[編輯]** — 只動呈現方式,數字不變

**文中的 A3、A25 這類編號是什麼**:實驗記錄編號。每個編號「做了什麼、結果是什麼」見**文末附表**;完整記錄(預登記文件、跑法、原始數據位置、統計結論)在 `RESEARCH_NOTES.md` §10 的同編號列,拿編號去搜即可(例如搜「A25」)。

---

## paper-YYYY-MM-DD(待定,修訂中)— `gmc_v2.tex`(對 `gmc_v1.tex`)

2026-08-25 起的修訂輪(reviewer 視角逐段檢查)。程式碼僅動一處(A41 惰性 fallback,快取逐位元等值),所有已報 HOTA 數字不變;FPS 重測。

### [編輯] — §4.3 補 Welch 統計量(#29 item 2 / #31 item 1)

- 「Both drops are significant under Welch's $t$-test」→ 加括號:$n{=}5$;−ego $t{=}11.8$(moving-class)/ $11.7$(pooled);−multiscale $t{=}6.2$ / $6.7$;all $p{<}0.01$。
- 依據:A38(2026-08-25 重建)`diagnostics/welch_ablation_n5.py` → `results/ablation_n5_welch.json`,p = 1.75e-5 / 9.81e-6 / 1.84e-3 / 1.76e-3;平均值與 A34 一致。

### [編輯] — §3.2 補 warm-up 棄權規則(#31 item 2)

- Eq. (3) 說明段後加一段:軌跡需 11 幀連續歷史(最長間隔 10 + 1,三個間隔皆可定義)才產生運動特徵;不足時模組棄權、host 分數原樣通過;門檻由最長間隔決定,無自由參數。
- 依據:`filter_warmup_cache.py`(T_MIN=11),所有 ship 快取皆 `_warm11`;A3 量測(25.0% 軌跡幀受影響,1,239/4,950)。依用戶決定只寫機制、不引新數字。

### [編輯] — §3.2 補 1/g 實作註記(#31 item 3)

- 「All velocities are normalized …」句後加:實作省略 $1/g$;等價於第一層投影對每個 gap 的常數重縮放(Sec. 3.3)。公式與 "velocity" 用詞不動。
- 依據:`gmc_link/utils.py:38-60`、`manager.py:379-388` 僅以影像尺寸正規化、不除 gap;線性層可吸收每維常數(表示等價)。

### [筆誤] — §3.1 框遮罩用詞(#31 item 4)

- 「excluding the region where tracked object boxes overlap」→「excluding the interiors of the previous frame's tracked object boxes」。
- 依據:`gmc_link/core.py:77-83` 將前一幀每個偵測框內部整塊置零(`manager.py:295` 傳入 `prev_detections`)。

### [編輯] — §4.1 fallback 成功率擴到全資料集、FPS 重測(A39/A41)

- 「succeeds on all 2,065 adjacent frame pairs across the four evaluation sequences」→「all 7,690 adjacent frame pairs of the 19 training and evaluation sequences」;「$31.8$ FPS」→「$149$ FPS on CPU ($6.7$\,ms per frame)」。
- 依據(成功率):A39 `diag_road_chain.py`,19 條序列 7,690 對相鄰幀,路面擬合 0 次回傳 None(評估 2,065 對有偵測框遮罩;訓練 5,625 對無遮罩,即訓練程式的條件)。
- 依據(FPS):A41。`gmc_link/manager.py` road 模式改為只在路面擬合失敗時才估全域 ORB(從未發生);0011 seed0 快取重建與既有快取 183,872 筆逐值相同(max |Δ| 0.00),HOTA 數字不受影響。FPS 以同一 session、同機器、`profile_inference.py --seq 0011`、16 reps 取 warm 中位數:road 149.3(IQR 147.5–150.8)/ 舊 ship 全域鏈 63.9。A36 的 31.8/42.8 為當日機器狀態數字,存 `results/fps_profile_a36_2026_08_17.json`;不可跨 session 比較。
- 取代本段上方「[編輯] — ORB fallback 敘述全刪」條目中「程式碼保留 fallback,31.8 FPS 沿用」的說法。

### [編輯] — §3.1 補「為何取畫面下半部」的幾何理由

- RANSAC 句後加兩句:前視相機的地平線約在畫面垂直中央;其上是建物與天空(不在路面平面),其下是車前到地平線的路面,故只對下半部擬合。
- 依據:幾何(單應性只對平面精確);A39 光度殘差佐證 —— 起點高於地平線的區域(0.3/0.4)一律較差,0.5–0.7 在近路面打平、但只有 0.5 取樣到中距離物體所在區域(`results/road_diag/road_chain_diag_evalnear.json`)。數字不入文。

### [編輯] — §4.1 補訓練資料句(#29 item 1)

- optimizer 句後加:aligner 以 Refer-KITTI V1 訓練分割(15 條序列,與測試序列不交)訓練;正樣本 = expression × 其標註指涉的 ground-truth 物體之運動特徵(由 GT 框計算);tracker 輸出僅在測試時使用。
- 依據:`gmc_link/train.py:410-414, 717-719`(`--split v1` → 15 seqs)、`gmc_link/dataset.py:884, 926`(`labels_with_ids` GT 軌跡)、`refer-kitti/expression/` 818 條 = V1 發布數(#29 留言 2026-08-25)。

### [編輯] — ORB fallback 敘述全刪

- 刪方法段末句(路面擬合失敗 → ORB 全域單應性 fallback)與 Setup 的 fallback 參數句(1,500 keypoints / 5px 門檻)。
- 依據:路面擬合在四條評測序列 2065/2065 全數成功(A37 的支持測量,`results/road_fallback_rate.json`),fallback 從未觸發、不影響任何已報數字;程式碼保留 fallback,31.8 FPS 沿用。
- 保留「succeeds on all 2,065 adjacent frame pairs」作穩健性敘述;`\cite{orb}` 隨之移除(refs.bib 條目保留,BibTeX 不輸出未引用條目)。

### [筆誤] — Limitations 誤述 fallback 觸發機制

- 原句稱「非平面時退回 global estimate」;實際 fallback 只在特徵不足時觸發(<12 角點 / LK 追蹤失敗 / findHomography 回 None,`gmc_link/core.py:86-94`),與平面性無關 —— 路面不平時擬合多半「成功但有偏」,fallback 不會接手。
- 改為直述模型適用範圍(不作未量測的退化宣稱、不用情態詞):「assumes a flat ground plane; scenes with strong slopes or uneven terrain fall outside the model」。程式一直是對的。方法段 L120「A homography is exact for a plane」保留 —— 那句講的是理想模型類(射影幾何定理),是設計動機;Limitations 講的是估計的適用範圍,分工清楚。

### [編輯] — §2.2 三種速度定義補強(定義句用戶重寫)

- raw / ego 補上公式($v^{raw}_g=(o_t-o_{t-g})/g$、$v^{ego}_g=(\hat o_t-o_{t-g})/g$),單應性應用明寫齊次座標,ego 句補「evaluated at the object's location」。
- raw 的動機句改為字面精確的陳述:「it is the sum of the object's own motion and the motion induced by the camera」(原「is mixed with」語法含混;由 Eq. (2) 移項 $v^{raw}=v^{res}+v^{ego}$,此句字面為真)。
- residual 定義句(camera-motion-compensated,raw 減 ego)作 Eq. (2) 引導;Eq. (2) 補恒等式 $v^{res}_g=(o_t-\hat o_t)/g$(殘差 = 觀測質心對「靜止預測」的偏差),句尾逗號改句號(後接新句子)。
- 定義句草稿兩處事實更正:「consecutive frames」→ gap-$g$ 幀對($I_{t-g}$、$I_t$,gaps 2/5/10);「inter-frame homography」→ 累積單應性 $H_{t-g\to t}$。

## paper-2026-08-22 — `gmc_v1.tex`(對 `gmc.tex`)

配置:**Option B,2026-08-19 拍板**(`docs/SHIP_DECISION_2026_08_16.md`)— 三個 host 設定統一路面 ego 鏈、warm11 遮罩、無 motion EMA、raw cosine、類別權重加法融合。

### [方法] — 配置改了,實驗重跑

每一步的增益都單獨量過(iKUN,累積疊加;出處 `docs/SHIP_DECISION_2026_08_16.md`):

| 累積配置 | pooled | Δ pooled | MOVING | Δ MOVING |
|---|---|---|---|---|
| native(無模組) | 44.224 | — | 25.531 | — |
| + GMC 模組(12D、單 α)= gmc.tex 版 | 44.512 | +0.288 | 30.222 | +4.69 |
| + warmup 遮罩(下述第 1 條) | 44.634 | +0.122 | 30.043 | −0.18(噪聲內) |
| + 刪 EMA、similarity ego(第 2 條) | 44.656 | +0.022 | 30.045 | +0.00 |
| + 路面估法 + 雙權重(第 3、4 條) | **44.847** | +0.191 | **32.606** | +2.56 |

warm11 與刪 EMA 兩步是為 pooled 增益和正確性(訓練/推論一致、不融合垃圾)而採,
MOVING 本來就不預期動;−0.18 在 n=3 種子變異範圍內。

**1. Warmup 遮罩(warm11)—— 沒把握就閉嘴**

- 問題:每條軌跡自己的前 10 幀(連續歷史 ≤ 10 = 最長速度時距)算不出長時距速度,程式補零。零速度看起來就是「靜止」,所以剛進畫面的移動車會被一個錯的分數大力扣分。這種幀佔測試資料 25.1%(實驗記錄 A3,編號說明見檔頭)。
- 作法:這些幀的 GMC 分數從 cache 刪除,融合端查不到就加 0 —— host 的分數原樣通過,等同模組對該幀棄權;第 11 幀起才生效(故名 warm11)。零新超參數。
- 效果:iKUN pooled +0.122。

**2. 刪掉推論期的速度平滑(EMA)—— 考試和練習要用同一套**

- 問題:推論時速度特徵有做平滑,訓練時沒有。模型從沒看過平滑後的資料(A2)。
- 作法:刪掉平滑,推論吃和訓練一樣的原始特徵。
- 效果:+0.022(與同批清理合計)。

**3. 相機運動改用路面估(核心改動)—— 在平的東西上量,量得才準**

- 問題:單應性這種變換只有對「一個平面」才準。舊作法把它擬合在整張畫面的背景點上 —— 建築、桿子、停放車輛,深度都不同,估出來的相機運動被視差帶偏。
- 作法:只用畫面下半部的路面點來估(Shi-Tomasi 角點 + LK 光流,RANSAC 3px)。路面接近一個平面,假設成立。舊的全域估計留作備援。
- 為什麼確定是這個原因:
  - 拆開驗證(A25):只換路面估法,運動類 +1.46(t=3.9);只換另一個候選因素(地面接觸點),+0.18,等於沒動。功勞在路面估法。
  - 在哪裡起作用(A29):三條測試序列裡,舊估法在 seq 0011 幾乎分不出「符合運動描述的車」和「不符合的車」(分離度 0.022);換路面估法後變 0.135,6 倍。0011 也正是運動類進步最多的序列(+2.23)。
  - 「路面點夠不夠」的疑慮:2,065 對評測幀全部擬合成功,備援一次都沒用到。
- 效果:見第 5 條的合併數字。

**4. 融合權重一個變兩個(α_c)—— 運動句大聲、外觀句小聲**

- 問題:模組只懂運動。遇到「black cars」這種外觀句,它的分數是噪聲。只有一個權重時,調大傷外觀句、調小浪費運動句。
- 作法:句子先分類(關鍵字),運動/靜止句用 α_mot,外觀句用 α_app。iKUN 交叉驗證選出 (0.7, 0.1) —— 外觀句幾乎關掉。
- 為什麼 FlexHook 不需要:它底層本來就看運動,模組的分數對它的外觀句不是噪聲,沒東西可分流 —— 交叉驗證自己選出兩個權重相等(7 / 5),等於退回單一權重(A35)。
- 對照組:把雙權重放在「舊」估法上只 +0.016 —— 效果來自「路面估法 × 分流」的組合,不是分流自己(A32)。

**5. 三個 host 統一用路面估法(A37)**

- 代價與收穫:FlexHook 兩設定 pooled 各降 0.03,換到運動類 V1 增益近乎翻倍(+0.49 → +0.67)、V2 翻四倍(+0.048 → +0.184,從噪聲內變成顯著)。
- 和第 3 條一致:路面估法改善的是「運動/靜止分得開」,運動類直接受惠,pooled 因為運動句只佔六分之一所以幾乎無感。
- 定案數字:iKUN 44.847 ± 0.107、FH V1 53.980 ± 0.059、FH V2 42.625 ± 0.032 —— 三行全部超過發表值。

### [協議] — 評測修正後重測

- **FH V1 句子名單**:158(含 8 條格式異常句)→ 官方 150。重現 native 從 53.110 變 **53.824 = 發表值**;舊 Table 1 的「重現落差」註腳消失,因為落差是名單錯誤的產物(A31)。
- **V2 逐類分組**:改寫 slug 分類(108/862 句分錯)→ canonical `raw_sentence`。MOVING baseline 48.02 → 38.15,增益從 −0.07 翻正為 +0.18(A30、A4)。
- **FPS**:舊值 68 是髒量測;乾淨重測(process-only、CPU)路面鏈 31.8 / 全域鏈 42.8(A36)。論文報 31.8。
- **LOSO**:從事後穩健性檢查變成選點程序本身,搜索格加密且無截斷(A24、A37)。任何權重都不在自己被評測的序列上選。
- **消融重定基**在 Option B 工作點,n=5(A34):−ego 為 MOVING −3.81 / pooled −0.64(t≈11.8),−multiscale −1.85 / −0.32。

### [筆誤] — 稿子錯,程式一直對

- **§3.2 ego 速度定義**:舊稿寫成 warp 後質心與「當前」質心的距離 —— 那個量是殘差本身,使公式變成「殘差 = 原始 − 殘差」的自我矛盾。改為 ego 位移 $\hat{o}_t - o_{t-g}$(`gmc_link/manager.py:385`)。

### [編輯]

- 版面:開 `\ninept`;刪 tikz 流程圖(與架構圖重複)。6 頁 → 5 頁,第 5 頁純參考文獻。
- 方法名全篇 GMC-Link → **GMC Module**。
- 架構圖改用 Excalidraw 重繪(`figures/Architecture.excalidraw`),取代 PowerPoint 源;修正語言分支兩處誤標成 Motion 的向量、回饋箭頭補上融合權重、host 分數從向量條改為純量(箭頭標籤)。
- 文獻:刪 `mlstrack`/`cdrmot`/`tellmewhat`,加 STORM(對 CVPR 2026 Findings 核對過);LTTrack **不引用** —— 查無可信來源。
- Setup:基準揭露(重現 iKUN 44.224 vs 發表 44.564)、兩條估計鏈的參數、seeds 與協議句。
- 限制段改寫成三條可查證項目:路面平面假設 + 回退、關鍵字誤路由(V1 方向句 14/126)、FlexHook 雙權重退化。
- 摘要補上代表數字;67 個紅字標記全部拆除(PDF 文字逐字元驗證未變)。
- 作者拍板維持刪除:趨勢解釋段、n=3 但書、TempRMOT 範圍段、消融支撐的貢獻條目。

---

## paper-2026-08-19 — `gmc.tex`(對 `paper/latex/mainv3.tex`,2026-08-05 MMAsia 投稿版)

論文移植到 2026-08-10 簡化配置(「Option A 前身」:12D、單一 α、全域 ORB similarity 鏈)的 ICASSP 版。

### [方法]

- **運動特徵 13D → 12D**:ρ(殘差對背景 SNR)槽位移除,消融顯示無 HOTA 代價(教授指示的簡化,2026-08-10)。
- **融合:逐類配方 $s_{host} + \alpha(sc\cdot\cos + thr)$**(每 host 運動/外觀兩軸,約 18 個手調超參數)→ **單一加法權重** $s_{host} + \alpha\,s_{gmc}$,LOSO 選點(0.5 / 2 / 5)。分數側 sigmoid + EMA 移除;raw cosine。
- 當時數字:iKUN 44.512 ± 0.104、FH V1 53.157 ± 0.022(對重現值 53.110)、FH V2 42.684 ± 0.058。

### [編輯]

- 新開 ICASSP 工作區(`2027_ICASSP/`),spconf 模板;MMAsia 稿凍結為 `paper/latex/mainv3.tex`。
- 移植時多段分析被註解(LOSO、TempRMOT 範圍、趨勢解釋、GPS/IMU);去留在 2026-08-22 那輪定案(issue #23/#24)。

---

## 附:本文引用的實驗記錄一覽

| 編號 | 做了什麼 | 結果 |
|---|---|---|
| A2 | 盤查全管線,發現速度特徵在推論期有 EMA 平滑、訓練期沒有 | 訓練/推論分布不一致確認;移除後 +0.022(與同批清理合計) |
| A3 | 統計測試軌跡的歷史長度,量化「補零速度」幀的比例 | 25.1% 的 track-frame 缺長時距歷史 → 催生 warm11 遮罩 |
| A4 | 檢查 V2 逐類評測的標籤空間 | 分類器跑在改寫過的 slug 上,108/862 句分錯 → 改用 canonical 句 |
| A24 | iKUN 的 LOSO 重跑:搜索格加密、去掉邊界截斷 | 選出的 α*=0.5 不變 → 選點程序本身可信 |
| A25 | 歸因 2×2:「路面估法」與「地面接觸點」兩個候選因素分開開關,每臂獨立訓練 + 全評測,n=3 | 只換路面估法 MOVING +1.46(t=3.9);只換接觸點 +0.18(t≈0.55)→ 功勞在路面估法 |
| A29 | 逐幀分數分離度探針:GT 物件以 IoU≥0.5 對應 tracker 軌跡,量「符合運動句的軌跡平均分數 − 不符合的平均分數」 | seq 0011 分離度 0.022 → 0.135(6 倍),0005 本來就高、不變 → 定位路面估法在哪裡起作用 |
| A30 | V2 逐類評測改用 canonical 句重跑 | MOVING 負值異常消失,四類增益全非負 |
| A31 | FH V1 換官方 150 句名單重評 | 重現 native 53.110 → 53.824 = 發表值 → 「重現落差」是名單錯誤,不是管線問題 |
| A32 | 雙權重 × 路面估法,LOSO 二維格點選 (α_mot, α_app),n=3;另設「雙權重 × 舊估法」對照組 | iKUN pooled 44.847(+0.19)、MOVING +2.56;對照組僅 +0.016 → 增益來自組合 |
| A34 | 兩個 ship 候選配置各做 n=5 消融(固定 LOSO 工作點) | Option B 臂:−ego 為 −3.81/−0.64、−multiscale 為 −1.85/−0.32,全部顯著 |
| A35 | FlexHook 也照跑雙權重 LOSO(V1 三折、V2 四折)+ 格外探針確認最佳點在格內 | 各折增益 ≤ +0.10、出格點全下跌 → FlexHook 維持單權重 |
| A36 | FPS 乾淨重測(seq 0011、n=500 幀、process-only、CPU) | 路面估法 31.8 / 全域估法 42.8 FPS;取代舊的髒量測 68 |
| A37 | FlexHook 在路面估法上重跑單 α LOSO(預登記先 commit 再跑) | V1 α*=7 → 53.980、V2 α*=5 → 42.625;運動類 V1 +0.67、V2 +0.184(轉顯著) |
