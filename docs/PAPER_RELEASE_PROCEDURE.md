# 論文 Release 流程(paper-YYYY-MM-DD)

每個論文里程碑(投稿版、大改版)開一個 GitHub release,tag 釘住 commit,
三個 assets:論文 PDF、latexdiff PDF、可編譯來源包。舊版本的檔案一律不進包。

## 步驟

1. **前置檢查**(在 `2027_ICASSP/`):
   ```bash
   latexmk -pdf -interaction=nonstopmode gmc_v1.tex && latexmk -c gmc_v1.tex
   pdfinfo gmc_v1.pdf | grep Pages          # 必須 5 頁
   pdftotext -f 5 -l 5 gmc_v1.pdf - | head  # 第 5 頁必須只有參考文獻
   ```
   工作區乾淨、要進 release 的內容已在 main 上。

2. **重生 latexdiff**(基準 = `gmc.tex`;latexdiff 會把標記放在表格 `\hline`
   前面導致 `Misplaced \noalign`,用 python 後處理搬到 `\hline` 後):
   ```bash
   latexdiff --type=UNDERLINE gmc.tex gmc_v1.tex > diff_gmc_vs_gmc_v1.tex
   python3 -c "
   import re
   p='diff_gmc_vs_gmc_v1.tex'; s=open(p).read()
   s=re.sub(r'((?:\\\\DIF(?:addbegin|addend|delbegin|delend)FL\s*)+)(\\\\hline)', r'\2 \1', s)
   open(p,'w').write(s)"
   latexmk -pdf -interaction=nonstopmode diff_gmc_vs_gmc_v1.tex && latexmk -c diff_gmc_vs_gmc_v1.tex
   ```
   diff 的 tex+pdf commit 進 repo。

3. **組來源包**(cherry-pick 現行版本需要的檔案,不含舊版):
   - 進包:`gmc_v1.tex`、`refs.bib`、`spconf.sty`、`IEEEbib.bst`、`gmc_v1.bbl`
     (先編譯一次留下,讓收件人免跑 BibTeX)、`figures/Architecture.png`、
     `figures/qualitative.pdf`、`figures/Architecture.excalidraw`(圖的可編輯源)、
     一份 `README.md`(建置指令 + 檔案清單)
   - 不進包:`gmc.tex`/`gmc.pdf`(舊活稿,只當 diff 基準)、`submission_mainv3/`、
     `ICASSP2024_Paper_Templates/`、所有編譯中間檔
   - **在乾淨資料夾實測 `latexmk -pdf gmc_v1.tex` 編得過、頁數對,才打 zip**:
     `zip -r gmc_v1-latex-source.zip gmc_v1-latex-source/`

4. **更新 `2027_ICASSP/CHANGES.md`**:開新段 `paper-YYYY-MM-DD`,每條掛
   [方法]/[協議]/[筆誤]/[編輯] 標籤;引用的實驗編號補進文末附表。

5. **開 release**:
   ```bash
   gh release create paper-YYYY-MM-DD --target "$(git rev-parse HEAD)" \
     --title "Paper YYYY-MM-DD" --notes "<見下方格式>" \
     2027_ICASSP/gmc_v1.pdf 2027_ICASSP/diff_gmc_vs_gmc_v1.pdf gmc_v1-latex-source.zip
   ```

## Release notes 格式(照 GitHub 預設 What's Changed)

```markdown
<一句話:這版是什麼>

## What's Changed
* <PR 標題> by @<作者> in <PR 連結>
* ...(沒走 PR 的大改動:一行 + commit hash)

## Assets
* `gmc_v1.pdf` — 論文,5 頁(4 內文 + 1 純參考文獻)
* `diff_gmc_vs_gmc_v1.pdf` — 對 <上一個 tag> 基準的 latexdiff
* `gmc_v1-latex-source.zip` — 可編譯來源包,`latexmk -pdf gmc_v1.tex` 即建

**Full Changelog**: https://github.com/Seanachan/GMC-Link/compare/<上一個 tag>...paper-YYYY-MM-DD
```

## 規則

- Tag 用日期(`paper-2026-08-22`),不用內部代號(S0–S6、Option B 之類讀者看不懂的)
- Asset 檔名平實(`gmc_v1.pdf`,不加 `-s0-s6` 這類後綴)
- 標題/內文不出現 AI 署名
- 更新既有 release 的 assets:`gh release delete-asset <tag> <name> -y` 再 `gh release upload`

*首例:`paper-2026-08-19`(基準)與 `paper-2026-08-22`,照此格式。*
