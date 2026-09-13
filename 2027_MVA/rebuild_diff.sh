#!/usr/bin/env bash
# Canonical build: gmc_v3.pdf + diff_gmc_v2_1_vs_gmc_v3.pdf (base = professor's gmc_v2_1.tex).
#
# latexdiff config (A46r/A46t, CHANGES.md):
#   - PICTUREENV includes `table`: changed tables render as clean final form
#     (inline markup mangles structurally-rewritten tables), and latexdiff wraps
#     each changed table in \DIFaddbegin — rule 4 turns that into a blue
#     [changed] tag in the caption.
#   - perl rules 1-3: \DIFadd*FL markers must not precede \hline or \multicolumn
#     (both expand to \omit/\noalign, which must open the cell/row).
set -euo pipefail
cd "$(dirname "$0")"
export PATH=/usr/local/texlive/2026/bin/x86_64-linux:$PATH

latexmk -pdf -interaction=nonstopmode gmc_v3.tex >/dev/null
latexdiff --config="PICTUREENV=(?:picture|DIFnomarkup|table)[\\w\\d*@]*" \
    gmc_v2_1.tex gmc_v3.tex > diff_gmc_v2_1_vs_gmc_v3.tex 2>/dev/null
perl -0pi -e '
s/\\DIFaddendFL \\hline/\\hline \\DIFaddendFL/g;
s/\\DIFaddbeginFL\s+\\hline/\\hline \\DIFaddbeginFL/g;
s/\\DIFaddbeginFL\s+(\\multicolumn\{\d+\}\{c\}\{)/$1\\DIFaddbeginFL /g;
s/(\\DIFaddbegin \\begin\{table\}\[[tb]\]\s*\\centering\s*\\caption\{)/$1\\DIFaddFL{[changed] }/g;
' diff_gmc_v2_1_vs_gmc_v3.tex
latexmk -pdf -interaction=nonstopmode diff_gmc_v2_1_vs_gmc_v3.tex >/dev/null

echo "v3:   $(pdfinfo gmc_v3.pdf | awk '/^Pages/{print $2}') pages, $(grep -c Overfull gmc_v3.log || true) overfull"
echo "diff: $(pdfinfo diff_gmc_v2_1_vs_gmc_v3.pdf | awk '/^Pages/{print $2}') pages, $(grep -c '^!' diff_gmc_v2_1_vs_gmc_v3.log || true) TeX errors, $(grep -c 'DIFaddFL{\[changed\]' diff_gmc_v2_1_vs_gmc_v3.tex || true) tables marked [changed]"
