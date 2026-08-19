# 論文數字包 — Option B(2026-08-19 更新)

活稿 = `2027_ICASSP/gmc_v1.tex`。**論文文字由用戶主導,這裡只給數字與清單。**
修改項目已開 issue:#23(數字/事實錯誤)、#24(論述修復)。
出處:RESEARCH_NOTES §10 A22–A36;登記書 `docs/PREREG_*.md`;數據 `results/`。

## 配置(2026-08-19 鎖定)

三個 host 共用路面鏈(Shi-Tomasi + 金字塔 LK,下半幅畫面扣偵測框,RANSAC 3px;
失敗回退全域 ORB)+ warm11 遮罩 + 無 EMA + raw cosine + 加性融合(門檻 0.0)。

## Table 1(主結果,pooled HOTA,n=3)

| Host | native(≡ α=0) | 發表值 | Option B |
|---|---|---|---|
| iKUN | 44.224 | 44.564 | **44.847 ± 0.107**(α_mot=0.7, α_app=0.1) |
| FlexHook V1(官方 150 句) | 53.824 | 53.824 | **53.980 ± 0.059**(α=7)+0.156, t=4.6 |
| FlexHook V2 | 42.526 | 42.526 | **42.625 ± 0.032**(α=5)+0.099, t=5.4 |

所有 α 皆由 per-host 留一序列交叉驗證選出(iKUN A32、FlexHook A37);
FlexHook 的折別選擇無 censoring(V1 {7,1,7}、V2 {5,3,5,7})。

註:iKUN 的比較基準是發表值 44.564(我們的 α=0 = 44.224);FlexHook 兩行的發表值
恰等於我們的 α=0。三行基準性質不同,Setup 要揭露一句。

iKUN per-class(native → B):MOVING 25.531 → **32.606 ± 0.654**;
STATIC 43.914 → 44.584 ± 0.122;APPEARANCE 46.346 → 46.468 ± 0.048。

## Table 2(運動類增益,對應 tab:deficit)

| Host | Baseline | 增益 | t | 分母 |
|---|---|---|---|---|
| iKUN | 25.531 | **+7.08 ± 0.65** | 18.7 | 27/158 |
| FlexHook V1(官方名單) | 44.309 | **+0.67 ± 0.13** | 9.2 | 25/150 |
| FlexHook V2(canonical 分類) | 38.154 | **+0.184 ± 0.057** | 5.6 | 136/862 |

V2 的 slug 分類作廢(A30)。路面鏈上 canonical 四類**全部顯著為正**:
MOVING +0.184(t=5.6)/ STATIC +0.256 / APPEARANCE +0.083 / DIRECTION +0.022。
數據 `results/v2_canonical_regroup_road_ship.json`。

**反比律仍然成立且更乾淨**:+7.08(iKUN,無原生運動建模)→ +0.67(FH V1)→ +0.18(FH V2),
但現在三個都顯著為正,不再有「V2 在噪聲內」的弱項。

換到路面鏈的取捨:pooled 各降約 0.03,MOVING 增益 V1 +0.49→+0.67、V2 +0.048→+0.184。

## Table 3(消融,iKUN,n=5,Option B 操作點)

| 配置 | MOVING | pooled |
|---|---|---|
| native | 25.531 | 44.224 |
| full | **32.295 ± 0.632** | **44.803 ± 0.103** |
| −ego | 28.489 ± 0.347(−3.81, t=11.8) | 44.166 ± 0.065(−0.64, t=11.7) |
| −multiscale | 30.449 ± 0.198(−1.85, t=6.2) | 44.485 ± 0.024(−0.32, t=6.7) |

STATIC 欄:full 44.545 ± 0.107、−ego 43.702 ± 0.219、−multiscale 44.428 ± 0.061
(native 43.914)。全欄位:`results/ablation_n5_hedge.json`。

## FPS(A36,乾淨重量,CPU,seq 0011,n=500,8 次取暖機中位數)

**路面鏈 31.8**(process-only)/ 全域鏈 42.8;含 I/O 24.5 / 31.1。
ship 是路面鏈 ⇒ 論文用 **31.8**。舊值 48.0/35.3(有負載)與現稿 68 FPS 皆作廢。

## 路面鏈可用性(方法段佐證)

路面擬合在**四條評測序列的 2065 對相鄰幀上全部成功**,全域 ORB 回退一次都沒觸發
(`results/road_fallback_rate.json`)。柏油路紋理是否足夠是審稿人會問的問題,這個數字直接回答。

## 措辭清單(寫作期執行,行號對 `gmc_v1.tex`)

見 issue #23 與 #24 的逐條清單。另外三項全域性的:

1. Setup 補:三 host 共用路面鏈;α 由 per-host LOSO 選;FlexHook 退化為單 α(A35)。
2. Related work 補 JustHook(= FlexHook 定稿名,CVPR 2026)、STORM、LTTrack;VMRMOT 已引。
3. 不寫「突破天花板」——iKUN vs paper-pure 44.564 寫 +0.28(~2σ)。
