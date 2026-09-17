#!/usr/bin/env python3
"""由 R/*.R 重新產生 README.md 與 downloads/food-analysis-statistics-R.md。

R/ 目錄是 R 程式的唯一來源；這兩個 Markdown 檔一律由本腳本產生，不要手改
（手改的副本曾造成註解數值與實際輸出不一致）。新增章節時只要改下面的 MANIFEST。

用法：python scripts/build_docs.py          # 重新產生
      python scripts/build_docs.py --check  # 只檢查是否已是最新（CI／提交前用）
"""
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (標題, 教學網頁, R 檔)；順序＝建議教學順序，與 assets/app.js 的 FAS_NAV 一致
MANIFEST = [
    ("Ch0 課程導覽與名詞圖鑑（給初學者）", "ch00.html", None),
    ("Ch1 統計入門：平均數、標準差與變異係數", "ch01.html", "ch01_basics.R"),
    ("Ch2 常態分配與信賴區間", "ch02.html", "ch02_ci_normal.R"),
    ("Ch3 方法能力指標與品質管制圖 (LOD/LOQ/管制圖)", "ch03.html", "ch03_method_qc.R"),
    ("Ch4 標準曲線與線性迴歸", "ch04.html", "ch04_regression.R"),
    ("Ch5 有效數字與異常值檢定 (Q 檢定 / Grubbs)", "ch05.html", "ch05_outliers_sigfig.R"),
    ("Ch15 假說檢定與 t／F 檢定", "ch15.html", "ch15_hypothesis_tests.R"),
    ("Ch16 單因子變異數分析 (One-way ANOVA) 與事後比較", "ch16.html", "ch16_anova_oneway.R"),
    ("Ch6 量測不確定度：概念與 GUM 四步驟", "ch06.html", "ch06_uncertainty_concept.R"),
    ("Ch7 Type A/B 分布轉換", "ch07.html", "ch07_typeAB_distributions.R"),
    ("Ch7 實戰案例(1)：分析天平稱量", "ch07.html", "case_balance.R"),
    ("Ch8 合成與擴展不確定度、報告與符合性", "ch08.html", "ch08_combine_report.R"),
    ("Ch9 Kragten 試算表法與 Monte Carlo", "ch09.html", "ch09_kragten_montecarlo.R"),
    ("Ch10 實戰案例(2)：NaOH 標定滴定 (QUAM Example A2)", "ch10.html", "case_titration.R"),
    ("Ch10 實戰案例(3)：HPLC/GC 農藥殘留 (QUAM Example A4)", "ch10.html", "case_hplc.R"),
    ("Ch11 綜合案例：粗纖維 (A6) 與標準曲線反推不確定度 (E.4)", "ch11.html", "ch11_capstone.R"),
    ("Ch12 進階案例(4)：LC-MS/MS 氯黴素 (基質效應/SIL-IS/加權校正)", "ch12.html", "case_lcmsms.R"),
    ("Ch13 實戰應用：USDA FoodData Central 與配方計算", "ch13.html", "ch13_fdc.R"),
    ("Ch17 ANOVA 進階：雙因子、精密度分解與失擬檢定", "ch17.html", "ch17_anova_advanced.R"),
    ("Ch14 實驗設計與反應曲面法 (DOE & RSM)", "ch14.html", "ch14_doe_rsm.R"),
]
EXTRAS = [
    ("選修：實驗室不確定度延伸案例", None, "extension_lab_uncertainty_cases.R"),
    ("選修：metRology 工具箱（需另裝套件）", None, "extension_metrology_toolbox.R"),
]
NOTES = {   # 顯示在 README 該節標題下的補充說明
    "ch13_fdc.R": [
        "對照業界軟體 TechWizard 的兩大招牌功能：最低成本配方與營養標籤/逆向工程。",
        "原料組成摘錄自 USDA FoodData Central (SR Legacy, CC0)；核心部分完全離線可執行。",
        "有網路時可將 RUN_ONLINE 改為 TRUE，體驗 FDC API 抓取真實資料。",
    ],
    "ch14_doe_rsm.R": [
        "情境：超音波輔助萃取茶葉多酚（DPPH 清除率）。",
        "Part 1–3 完全 base R：2³ 全因子＋中心點 -> CCD -> 二階模型 -> 駐點 -> 驗證實驗。",
        "Part 4 為套件選讀（rsm / FrF2 / desirability），先 install.packages 再將 HAVE_PKGS 改 TRUE。",
        "參考：Lenth (2009) JSS 32:7；Tanaka & Amaliah (2022) arXiv:2206.07532。",
    ],
}
FIGURES = ["figures.R", "figures_ch15.R", "figures_ch16.R", "figures_ch17.R"]


def r_source(name):
    return (ROOT / "R" / name).read_text(encoding="utf-8").rstrip("\n")


def build_readme():
    scripts = [m for m in MANIFEST + EXTRAS if m[2]]
    out = [
        "# 食品分析數據品管統計與量測不確定度 — 課程手冊（R 語言版）",
        "",
        f"> 本手冊收錄全課程 **{len(scripts)} 支 R 程式**。每支程式皆可直接複製到 R / RStudio 執行，",
        "> 或從本頁對應的 .R 檔下載。教學內容請開啟各章 HTML 網頁。",
        "> **完全初學者請先開啟 [ch00.html](ch00.html) 課程導覽與名詞圖鑑**（含全部專有名詞的白話解釋與比喻）。",
        ">",
        "> ⚠ 本檔由 `python scripts/build_docs.py` 自 `R/*.R` 產生，請勿手動修改；要改程式請改 `R/` 內的原始檔後重跑。",
        "",
        "**教材依據**",
        "- Nielsen's Food Analysis, 6th Ed., Chapter 4: *Evaluation of Analytical Data* (J. S. Smith)",
        "- EURACHEM/CITAC Guide CG 4, *Quantifying Uncertainty in Analytical Measurement*, QUAM:2012.P1 (3rd ed.)",
        "",
        "## 目錄（＝建議教學順序）",
        "",
        "章號是檔案的固定編號；Ch15–17（假說檢定與 ANOVA）是後來新增的，教學順序上分別排在 Ch5 與 Ch13 之後。",
        "",
        "| 章 | 教學網頁 | R 檔案 |",
        "|---|---|---|",
    ]
    for title, html, r in MANIFEST + EXTRAS:
        page = f"[{html}]({html})" if html else "—"
        rfile = f"[{r}](R/{r})" if r else "—"
        out.append(f"| {title} | {page} | {rfile} |")
    figs = "、".join(f"[{f}](R/{f})" for f in FIGURES)
    out += [
        f"| 附錄：本站全部教學圖表繪圖程式 | — | {figs} |",
        "",
        "## 如何使用",
        "",
        "1. 安裝 [R](https://cran.r-project.org) 與 [RStudio](https://posit.co/downloads)（皆免費）",
        "2. 開新腳本（Ctrl+Shift+N），貼上任一節程式碼",
        "3. Ctrl+Enter 逐行執行、Ctrl+Alt+R 整段執行",
        "4. 必修章節只用 R 內建函數，**不需安裝任何套件**（選修單元與 Ch14 套件選讀除外）",
        "5. 建議學習順序：依上表由上而下（章章相扣，案例貫穿）",
        "",
        "## 給授課教師：測驗與學習成效",
        "",
        "- 每章有「課前 3 題」與「章末複習測驗」，題目格式見 [docs/QUIZ_SCHEMA.md](docs/QUIZ_SCHEMA.md)，全站共用迷思代碼見 [docs/MISC_SEED.md](docs/MISC_SEED.md)。",
        "- 學生輸入學號後，首次作答、把握程度與「我還不懂的地方」會上傳 Firestore `student_events`；",
        "  以 `python scripts/quiz_dashboard.py` 產生全班成效與迷思報表，說明見 [scripts/README_dashboard.md](scripts/README_dashboard.md)。",
        "",
    ]
    for title, html, r in scripts:
        out += ["---", "", f"## {title}", ""]
        if r in NOTES:
            out += [f"> {line}" for line in NOTES[r]] + [""]
        where = f" ｜ 教學網頁：[{html}]({html})" if html else ""
        out += [f"📄 檔案：`{r}`{where}", "", "```r", r_source(r), "```", ""]
    return "\n".join(out)


def build_download():
    out = [
        "# 食品分析數據品管與量測不確定度：R 程式全集",
        "",
        "> 適用對象：沒有程式基礎的大學生。必修課程與實務案例使用 R 內建函數；選修 metRology 工具箱需要額外套件。",
        "> 本檔由 `python scripts/build_docs.py` 自 `R/*.R` 產生。",
        "",
        "## 使用方式",
        "",
        "1. 安裝 R，開啟 RGui 或 RStudio。",
        "2. 依下列順序（＝建議教學順序），一次複製一小段到 Console 後按 Enter。",
        "3. 先預測輸出，再執行；圖形會出現在 Plots 或新的繪圖視窗。",
        "4. 若中文圖形在舊版 Windows 顯示亂碼，請以 UTF-8 儲存並在 RStudio 執行。",
        "",
        "## 教材來源與界線",
        "",
        "- Nielsen's Food Analysis, Chapter 4, Evaluation of Analytical Data：Ch1–5。",
        "- Eurachem/CITAC Guide CG4, Quantifying Uncertainty in Analytical Measurement, Third Edition (2012)：Ch6–12。",
        "- 假說檢定與 ANOVA（Ch15–17）、DOE/RSM（Ch14）為自編教學範例，數據為教學用設計值。",
        "- CRAN metRology 官方文件：選修延伸單元；版本更新時請重新核對函數說明。",
        "- 程式為教學性改寫；LOD、異常值、涵蓋因子與符合性判定須依實驗室程序與適用法規確認。",
        "",
    ]
    for title, _html, r in [m for m in MANIFEST + EXTRAS if m[2]]:
        out += ["---", "", f"## {title}（{r}）", "", "```r", r_source(r), "```", ""]
    out += [
        "## 建議的期末提交格式",
        "",
        "請提交：原始數據、可重現 R 程式、必要圖形、結果與單位、不確定度及涵蓋資訊、品管判讀、決策規則，以及限制說明。",
        "",
    ]
    return "\n".join(out)


def main():
    check = "--check" in sys.argv
    targets = {
        ROOT / "README.md": build_readme(),
        ROOT / "downloads" / "food-analysis-statistics-R.md": build_download(),
    }
    stale = []
    for path, text in targets.items():
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        if old.replace("\r\n", "\n") != text:
            stale.append(path.name)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(text)
    if check and stale:
        print("過期，請重跑 python scripts/build_docs.py：", ", ".join(stale))
        sys.exit(1)
    print("已更新：" + ", ".join(stale) if stale else "已是最新。")


if __name__ == "__main__":
    main()
