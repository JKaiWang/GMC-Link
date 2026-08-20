# gmc_v1.tex 剩餘修改草案(S3–S6)— 待 review,尚未套用

2026-08-20。已完成:S0 版面、S1 數字、S2 方法段(commit `70e231b`)。
以下每項:位置錨點 → 建議的 LaTeX → 一句理由。**看完在對話裡說「S3 可以」「S4 的 2 改成…」即可。**

## 空間現況(先看這個)

現在 5 頁、餘裕 ≈ 0。下面全部加進去約 +300 字(≈1.7 欄),**塞不下**。
同時列了三個壓縮項(D1–D3,共約 −200 字)。**優先序**:P1 必加,P2 想加,P3 版面不夠就放棄。
若 P1+P2 仍超頁,依 P2c → P2b 順序放棄。

---

## S3 — Setup

### S3-1(P1)LOSO 協議段:重寫,不是還原

被註解的原文(`:174`)描述的是**舊協議**(在測試序列上調參 + 事後 LOSO 檢查)。
現在 LOSO 就是選擇程序本身,§3.4 已講機制,Setup 只需補「為什麼」:

```latex
Refer-KITTI does not provide a dedicated validation split. All fusion
weights are therefore selected by the leave-one-sequence-out procedure of
Sec.~\ref{sec:fusion}, so no weight is chosen on the sequence it is
evaluated on.
```

位置:取代 `:174` 的註解行。約 +40 字。

### S3-2(P1)表1 基準揭露(一句)

表1 三行的 Gain 都是對發表值;iKUN 的發表值(44.564)高於我們的 α=0(44.224),
FlexHook 的發表值恰等於 α=0。誠實揭露,而且對我們有利(模組自身貢獻其實是 +0.623):

```latex
Our reproduced FlexHook baselines match their published scores exactly at
$\alpha_c{=}0$, while our reproduced iKUN is $44.224$ against its published
$44.564$; Table~\ref{tab:main} reports the stricter comparison against the
published scores, so the iKUN gain over its reproduced native is larger
($+0.623$).
```

位置:接在 S3-1 之後(現 `:172` 那段的尾巴)。約 +45 字。

### S3-3(P1)FPS(一句)

全文現在沒有任何速度數字(舊稿 68 FPS 已作廢)。A36 乾淨值:

```latex
Excluding host inference, the module runs at $31.8$ FPS on CPU.
```

位置:Setup 末尾。+12 字。出處 `results/fps_profile.json`(road, process-only)。

---

## S4 — 結果論述

### S4-1(P1)主結果段強化:三個設定全部超過發表值

現況(`:216` 附近)只說「improves pooled HOTA in all three settings」。
現在事實更強:**44.847 > 44.564、53.980 > 53.824、42.625 > 42.526 —— 三行全超過發表值**。
建議替換該句:

```latex
With the module attached, all three settings exceed not only our reproduced
natives but also the hosts' published pooled HOTA
($+0.283$, $+0.156$, and $+0.099$, respectively).
```

理由:這是 Option B 才成立的新事實,現稿還在用弱版本敘述。不寫「surpass SOTA」之類的話。約 +15 字。

### S4-2(P1)還原趨勢解釋段(`:236` 註解,原文不含數字,原封還原)

```latex
In our evaluated settings, this trend suggests that GMC-Link is most
beneficial for host models with weaker motion understanding. When the host
model already distinguishes camera motion from object motion reasonably
well, the proposed module provides only a small improvement. Conversely,
when the host struggles with motion grounding, GMC-Link can effectively
compensate for this limitation and achieve a larger performance gain.
```

+61 字。這是全篇主要發現的唯一解釋段。措辭紅線:不寫 law / ∝ / scaling(已遵守)。

### S4-3(P2a)還原 n=3 誠實但書(`:238` 註解,原封還原)

```latex
Although this trend is consistent across all evaluated settings, it is
observed on two host architectures. Evaluating additional host models would
help verify whether this trend generalizes to other architectures.
```

+30 字。先擋「n=3 就下結論」的攻擊。

---

## S5 — Related work 與參考文獻

### S5-1(P2b)還原 TempRMOT 範圍段(`:100` 附近註解,原封還原)

```latex
TempRMOT~\cite{temprmot} is different because it already stores trajectory
history in recurrent memory. In our experiments, adding our external motion
module to TempRMOT reduced pooled Higher Order Tracking Accuracy (HOTA) in
two separate trials. This result suggests that the additional module may
introduce redundant motion information or unnecessary constraints because
TempRMOT already models motion over time. We therefore focus on two-stage
RMOT models that do not already encode trajectory history in recurrent
memory.
```

+72 字。回答「為什麼只測兩個 host」;把範圍變成量測出的邊界。

### S5-2(P1,同時是壓縮項)近期文獻換血:4 筆換 2 筆

現況 `:98`:`More recent RMOT methods~\cite{mlstrack,deeprmot,cdrmot,tellmewhat} further improve...`
建議:

```latex
Recent work continues to broaden the task: LTTrack~\cite{lttrack} couples
language guidance with temporal representation learning, and
STORM~\cite{storm} unifies grounding and tracking in a multimodal large
language model.
```

刪 `mlstrack, cdrmot, tellmewhat`;**開放決定**:`deeprmot` 是 ICASSP 2024 論文,
投 ICASSP 引它有社群意義 —— 要留就寫
`~\cite{deeprmot,lttrack,storm}`,參考文獻少省一筆。
淨效果:正文字數持平,參考文獻 −2 或 −1 筆(約 −60~−90pt,直接給第 5 頁餘裕)。

### S5-3(P1)bib 條目更新(不佔正文空間)

- `flexhook`:改成 CVPR 2026 camera-ready(標題含 "Just … Hook";**套用前需上網核對
  精確標題與作者序**,arXiv 2503.07516)。key 不變,內文名稱維持 FlexHook。
  可選:首次出現處寫 `FlexHook (published as JustHook)~\cite{flexhook}`。
- 新增 `lttrack`:Xu & Huang, Pattern Recognition vol.~179, 2026,
  DOI 10.1016/j.patcog.2026.113823(**標題需核對**)。
- 新增 `storm`:CVPR 2026, arXiv 2604.10527(**作者名單需核對,不可杜撰**)。

### S5-4(決定已定)GPS/IMU 段(`:69` 註解)放棄

版面不允許(142 字)。`kitti` bib 條目未被引用不會印出,無需處理。

---

## S6 — 摘要 / 貢獻 / 用語

### S6-1(P1)摘要補一句數字(現在整段摘要零數字)

```latex
On iKUN, the module raises moving-class HOTA by $7.08$ points, and all
three evaluated settings exceed their hosts' published pooled HOTA.
```

位置:摘要倒數第二句(「In the evaluation, we verify…」之後或取代它)。+22 字。

### S6-2(P2c)還原消融支撐的貢獻條目(`:80` 註解,數字更新為 n=5 路面鏈值)

```latex
\item We show that ego-motion compensation is the key component: removing
it costs $3.81$ moving-class and $0.64$ pooled HOTA on iKUN ($n{=}5$, both
significant under Welch's $t$-test).
```

+30 字。出處 `results/ablation_n5_hedge.json`(B-noego:MOV −3.81 t=11.8、pooled −0.64 t=11.7)。

### S6-3(P1,零成本)用語統一

- 全篇「three evaluated host settings」保留,但首次出現處(貢獻條目)已寫
  「Across iKUN and FlexHook … three evaluated host settings」→ 語意清楚,不動。
- 檢查點:不得出現「three hosts」(實際 2 個 host 架構、3 個評測設定)。
  現稿掃描:摘要「across different RMOT hosts」(2 個,OK)。無違規。

---

## 壓縮項(換空間用,依需要啟用)

| # | 位置 | 動作 | 省 |
|---|---|---|---|
| D1 | `:250` qualitative 圖 caption | 150 字 → ~50 字(細節正文已有) | ~100 字 |
| D2 | §3.2 殘差速度散文 | 公式已自明,刪重複敘述 | ~50 字 |
| D3 | §2.2 「We do not propose a new camera-motion estimation technique…」前的方法羅列 | 四筆技術引用壓成一句 | ~40 字 |

D1 草案:

```latex
\caption{``Moving cars'' (Refer-KITTI seq 0005). The parked car (red) sweeps
across the image as the camera passes, while the moving car (green) barely
shifts. Raw image motion misclassifies both; the ego-compensated residual
recovers both from the same host score.}
```

## 帳目

P1 合計 ≈ +134 字;P2 合計 ≈ +132 字;壓縮 D1–D3 ≈ −190 字。
P1+P2+D1–D3 淨 ≈ +76 字 ≈ 0.2 欄 —— **臨界**。實際套用時逐項編譯量頁,
超頁就依 P2c → P2b 順序砍(S6-2 貢獻條目、S5-1 TempRMOT 段)。

## 套用後的收尾(不在本草案內)

1. 重跑 latexdiff 給你比對;2. issue #23/#24 逐條勾稽;3. **投稿前最後一步**才拆 58 個紅字標記;
4. STORM/JustHook/LTTrack 書目上網核對後才進 bib(絕不杜撰作者)。
