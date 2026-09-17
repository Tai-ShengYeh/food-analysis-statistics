"""Ch17 ANOVA 進階：雙因子 ANOVA、ISO 5725 精密度分解、標準曲線失擬檢定。

R 的答案來源：Rscript R/ch17_anova_advanced.R（芭樂片乾燥 temp×time、奶粉 QC 5天×3重複、
HPLC 咖啡因標準曲線 5濃度×3重複，數據與該章網頁完全相同）。
"""
from excel_common import Book


def build():
    book = Book("ch17_anova_advanced.xlsx", "Ch17 ANOVA 進階：雙因子、精密度分解、失擬檢定", "ch17.html")
    book.readme([
        "# 這本活頁簿在做什麼",
        "三張計算表對應本章三個主題：「雙因子ANOVA」拆出溫度、時間與交互作用的效應（芭樂片乾燥維生素C保留率）；"
        "「ISO5725精密度分解」把日間、日內變異從一張單因子 ANOVA 表拆成重複性 s_r 與中間精密度 s_I（奶粉QC）；"
        "「失擬檢定」檢查 HPLC 咖啡因標準曲線是不是真的直（純誤差 vs 失擬）。",
        "# 怎麼用",
        "1. 「雙因子ANOVA」左邊黃色是 3 溫度 × 2 時間 × 3 重複＝18 筆數據；右邊照 SS_A（溫度）→SS_B（時間）→SS_AB（交互作用）→SS_error 的順序拆開算。",
        "2. 「ISO5725精密度分解」試著把某一天的三個數值改得很接近，看 s_between 會不會變成需要 MAX(0,…) 保護的負值。",
        "3. 「失擬檢定」把任一濃度的三個重複值改得很分散，看純誤差 SS 變大、F 變小、p 變大（模型看起來更「夠用」，但那是假象——一定要同時看殘差圖）。",
        "4. 「對照R答案」核對所有關鍵結果。",
        "# 觀念提醒",
        "① 雙因子 ANOVA 交互作用顯著時，主效應（單獨看溫度或時間）沒有意義，要看每個溫度下時間的效應（simple effects）。",
        "② s_between² 算出負值不是算錯，是日間變異真的很小時的正常抽樣結果，慣例取 0（Excel 用 MAX(0,…) 處理）。",
        "③ r² 很高不代表直線：失擬檢定才是專門檢查「彎不彎」的工具，而且一定要有重複點才能做（純誤差需要重複）。",
        "# 資料分析工具箱操作步驟",
        "① 啟用：檔案 → 選項 → 增益集 → 管理「Excel 增益集」→ 執行 → 勾選「分析工具箱」。",
        "② 雙因子 ANOVA（有重複，本章 A 部分）：資料排成「列＝溫度水準（每個水準連續 3 列＝重複數）、欄＝時間水準」的矩陣，範圍要包含列/欄標籤；"
        "「資料」→「資料分析」→「雙因子變異數分析：重複試驗」→ 輸入範圍框住整塊（含標籤）、「每一樣本的列數」填 3（＝每格重複數）、α=0.05。"
        "輸出「樣本」＝溫度（列因子）SS、「欄」＝時間 SS、「交互作用」SS、「組內」＝誤差 SS，逐列對應本活頁簿的 SS_A、SS_B、SS_AB、SS_error。",
        "③ 這個工具只接受<b>平衡設計</b>（每格筆數相同）；缺一筆就不能用。",
        "④ 精密度分解（本章 B 部分）：5 天的數據排成 5 欄（每欄 3 筆），工具選「單因子變異數分析」，從輸出表讀「組間 MS」與「組內 MS」，"
        "再用公式手算 s_r=SQRT(組內MS)、s_between=SQRT(MAX(0,(組間MS−組內MS)/3))、s_I=SQRT(SUMSQ(s_r,s_between))——工具箱本身不會幫你拆到這一步。",
        "⑤ 失擬檢定（本章 C 部分）工具箱沒有直接對應的工具；可以用「資料分析→迴歸」取得殘差 SS，再用 DEVSQ 逐濃度加總算純誤差 SS，兩者相減得失擬 SS（見「失擬檢定」工作表）。",
        "⑥ 工具箱輸出一律是靜態表，改數據要重新跑一次「資料分析」；本活頁簿的公式版會自動重算。",
    ])

    # ---------------------------------------------------------------- 1. 雙因子 ANOVA
    ws = book.sheet("雙因子ANOVA", [16, 16, 16, 60, 60])
    book.header(ws, 1, ["溫度(°C)", "4h 保留率(%)", "8h 保留率(%)"])
    temps = [50, 50, 50, 60, 60, 60, 70, 70, 70]
    y4 = [90.5, 91.9, 91.7, 83.8, 86.2, 84.8, 75.5, 76.6, 74.4]
    y8 = [88.5, 89.8, 89.0, 77.9, 76.3, 78.4, 54.9, 56.3, 55.2]
    for i, t in enumerate(temps):
        book.text(ws, 2 + i, 1, t)
    r4 = book.data(ws, 2, 2, y4, fmt="0.0")
    r8 = book.data(ws, 2, 3, y8, fmt="0.0")
    allv = "B2:C10"

    book.header(ws, 12, ["項目", "結果", "公式", "白話說明"])
    grand = book.calc(ws, 13, "總平均 grand mean", f"=AVERAGE({allv})")
    m50 = book.calc(ws, 14, "溫度平均 50°C", f"=(AVERAGEIF(A2:A10,50,{r4})+AVERAGEIF(A2:A10,50,{r8}))/2",
                     "同一溫度下 4h、8h 兩欄各自平均再平均（各 3 筆，等重）")
    m60 = book.calc(ws, 15, "溫度平均 60°C", f"=(AVERAGEIF(A2:A10,60,{r4})+AVERAGEIF(A2:A10,60,{r8}))/2")
    m70 = book.calc(ws, 16, "溫度平均 70°C", f"=(AVERAGEIF(A2:A10,70,{r4})+AVERAGEIF(A2:A10,70,{r8}))/2")
    m4 = book.calc(ws, 17, "時間平均 4h", f"=AVERAGE({r4})", "4h 欄本身就橫跨三個溫度，直接平均即為時間的邊際平均")
    m8 = book.calc(ws, 18, "時間平均 8h", f"=AVERAGE({r8})")
    c50_4 = book.calc(ws, 19, "格平均 50°C×4h", f"=AVERAGEIF(A2:A10,50,{r4})")
    c50_8 = book.calc(ws, 20, "格平均 50°C×8h", f"=AVERAGEIF(A2:A10,50,{r8})")
    c60_4 = book.calc(ws, 21, "格平均 60°C×4h", f"=AVERAGEIF(A2:A10,60,{r4})")
    c60_8 = book.calc(ws, 22, "格平均 60°C×8h", f"=AVERAGEIF(A2:A10,60,{r8})")
    c70_4 = book.calc(ws, 23, "格平均 70°C×4h", f"=AVERAGEIF(A2:A10,70,{r4})")
    c70_8 = book.calc(ws, 24, "格平均 70°C×8h", f"=AVERAGEIF(A2:A10,70,{r8})")

    SStot = book.calc(ws, 26, "SS_total", f"=DEVSQ({allv})", key=True)
    SScells = book.calc(ws, 27, "SS_cells（各格平均離總平均，×n=3）",
                         f"=3*(({c50_4}-{grand})^2+({c50_8}-{grand})^2+({c60_4}-{grand})^2+({c60_8}-{grand})^2+({c70_4}-{grand})^2+({c70_8}-{grand})^2)")
    SSA = book.calc(ws, 28, "SS_A（溫度）＝b×n×Σ(溫度平均−總平均)²，b=2,n=3",
                     f"=6*(({m50}-{grand})^2+({m60}-{grand})^2+({m70}-{grand})^2)", key=True)
    SSB = book.calc(ws, 29, "SS_B（時間）＝a×n×Σ(時間平均−總平均)²，a=3,n=3",
                     f"=9*(({m4}-{grand})^2+({m8}-{grand})^2)", key=True)
    SSAB = book.calc(ws, 30, "SS_AB（交互作用）＝SS_cells−SS_A−SS_B", f"={SScells}-{SSA}-{SSB}", key=True)
    SSerr = book.calc(ws, 31, "SS_error＝SS_total−SS_cells", f"={SStot}-{SScells}")
    dfA = book.calc(ws, 32, "df_A", 2, fmt="0")
    dfB = book.calc(ws, 33, "df_B", 1, fmt="0")
    dfAB = book.calc(ws, 34, "df_AB", 2, fmt="0")
    dfE = book.calc(ws, 35, "df_error", f"=COUNT({allv})-6", "18筆 − 6格 = 12", fmt="0")
    MSA = book.calc(ws, 36, "MS_A", f"={SSA}/{dfA}")
    MSB = book.calc(ws, 37, "MS_B", f"={SSB}/{dfB}")
    MSAB = book.calc(ws, 38, "MS_AB", f"={SSAB}/{dfAB}")
    MSE = book.calc(ws, 39, "MS_error", f"={SSerr}/{dfE}")
    FA = book.calc(ws, 40, "F_A（溫度）", f"={MSA}/{MSE}", key=True)
    FB = book.calc(ws, 41, "F_B（時間）", f"={MSB}/{MSE}", key=True)
    FAB = book.calc(ws, 42, "F_AB（交互作用）", f"={MSAB}/{MSE}", key=True)
    pA = book.calc(ws, 43, "p_A", f"=F.DIST.RT({FA},{dfA},{dfE})", key=True)
    pB = book.calc(ws, 44, "p_B", f"=F.DIST.RT({FB},{dfB},{dfE})")
    pAB = book.calc(ws, 45, "p_AB（交互作用）", f"=F.DIST.RT({FAB},{dfAB},{dfE})", "先看這一列！顯著就不能只看主效應", key=True)
    book.text(ws, 47, 1, "讀表順序：先看交互作用 p_AB。本例交互作用極顯著，代表「時間的效應隨溫度而不同」，主效應（時間平均少 9.9 個百分點）不能單獨解讀。", size=10, color="64748B")

    # ---------------------------------------------------------------- 2. ISO5725 精密度分解
    ws2 = book.sheet("ISO5725精密度分解", [30, 16, 54, 60])
    book.header(ws2, 1, ["day1", "day2", "day3", "day4", "day5"])
    d1 = book.data(ws2, 2, 1, [26.45, 26.35, 26.57], fmt="0.00")
    d2 = book.data(ws2, 2, 2, [26.52, 26.46, 26.70], fmt="0.00")
    d3 = book.data(ws2, 2, 3, [26.40, 26.49, 26.59], fmt="0.00")
    d4 = book.data(ws2, 2, 4, [26.27, 26.26, 26.33], fmt="0.00")
    d5 = book.data(ws2, 2, 5, [26.57, 26.56, 26.44], fmt="0.00")
    all5 = "A2:E4"
    book.header(ws2, 6, ["項目", "結果", "公式", "白話說明"])
    md1 = book.calc(ws2, 7, "日平均 day1", f"=AVERAGE({d1})")
    md2 = book.calc(ws2, 8, "日平均 day2", f"=AVERAGE({d2})")
    md3 = book.calc(ws2, 9, "日平均 day3", f"=AVERAGE({d3})")
    md4 = book.calc(ws2, 10, "日平均 day4", f"=AVERAGE({d4})")
    md5 = book.calc(ws2, 11, "日平均 day5", f"=AVERAGE({d5})")
    grand2 = book.calc(ws2, 12, "總平均", f"=AVERAGE({all5})")
    SSb2 = book.calc(ws2, 13, "SS_between（日間）",
                      f"=3*(({md1}-{grand2})^2+({md2}-{grand2})^2+({md3}-{grand2})^2+({md4}-{grand2})^2+({md5}-{grand2})^2)")
    SSw2 = book.calc(ws2, 14, "SS_within（日內）", f"=DEVSQ({d1})+DEVSQ({d2})+DEVSQ({d3})+DEVSQ({d4})+DEVSQ({d5})")
    dfb2 = book.calc(ws2, 15, "df_between", 4, fmt="0")
    dfw2 = book.calc(ws2, 16, "df_within", 10, fmt="0")
    MSb2 = book.calc(ws2, 17, "MS_between", f"={SSb2}/{dfb2}")
    MSw2 = book.calc(ws2, 18, "MS_within", f"={SSw2}/{dfw2}")
    sr = book.calc(ws2, 19, "重複性 s_r", f"=SQRT({MSw2})", "即 √MS_within", key=True)
    sbet = book.calc(ws2, 20, "日間 s_between", f"=SQRT(MAX(0,({MSb2}-{MSw2})/3))", "MAX(0,…) 處理負值；3=每天重複數", key=True)
    sI = book.calc(ws2, 21, "中間精密度 s_I", f"=SQRT(SUMSQ({sr},{sbet}))", "即 √(s_r² + s_between²)", key=True)
    naive = book.calc(ws2, 22, "✗ 對照：全部15格直接 STDEV.S", f"=STDEV.S({all5})", "既不是 s_r 也不是 s_I，是日間日內混在一起的值", key=True)
    naive_se = book.calc(ws2, 23, "✗ 只用當天重複算 SE（低估）", f"={sr}/SQRT(3)", "忽略了日間變異，會低估「單天平均值」真正的不確定度")
    correct_se = book.calc(ws2, 24, "✓ 正確：當天平均值的不確定度", f"=SQRT(SUMSQ({sbet},{naive_se}))", "日間變異不會因為多測幾次而變小", key=True)
    book.text(ws2, 26, 1, "s_I 一定 ≥ s_r（多了日間這個變異來源）；把 15 筆數據直接丟進 STDEV.S 得到的既不是 s_r 也不是 s_I，是兩者按自由度混合的值。", size=10, color="64748B")

    # ---------------------------------------------------------------- 3. 失擬檢定
    ws3 = book.sheet("失擬檢定", [16, 16, 50, 60])
    book.header(ws3, 1, ["濃度 (mg/L)", "波峰面積"])
    concs = [1, 1, 1, 5, 5, 5, 10, 10, 10, 50, 50, 50, 100, 100, 100]
    areas = [101, 99, 102, 498, 505, 492, 1005, 992, 1018, 4930, 5070, 5005, 9720, 10380, 10040]
    cA = book.data(ws3, 2, 1, concs, fmt="0")
    yA = book.data(ws3, 2, 2, areas, fmt="0")
    xrng, yrng = cA, yA
    groups = {"1": "B2:B4", "5": "B5:B7", "10": "B8:B10", "50": "B11:B13", "100": "B14:B16"}

    book.header(ws3, 18, ["項目", "結果", "公式", "白話說明"])
    slope = book.calc(ws3, 19, "斜率 slope", f"=SLOPE({yrng},{xrng})")
    intercept = book.calc(ws3, 20, "截距 intercept", f"=INTERCEPT({yrng},{xrng})")
    r2 = book.calc(ws3, 21, "r²", f"=RSQ({yrng},{xrng})", "很高，看起來「很直」")
    SSres = book.calc(ws3, 22, "殘差 SS（直線模型）", f"=DEVSQ({yrng})*(1-RSQ({yrng},{xrng}))",
                       "即 SS_total,y × (1−r²)；也可用「資料分析→迴歸」輸出的殘差 SS 對照", key=True)
    SSpe = book.calc(ws3, 23, "純誤差 SS", f"=DEVSQ({groups['1']})+DEVSQ({groups['5']})+DEVSQ({groups['10']})+DEVSQ({groups['50']})+DEVSQ({groups['100']})",
                      "每個濃度各算一次 DEVSQ 再相加：重複點離「自己濃度平均」多遠", key=True)
    SSlof = book.calc(ws3, 24, "失擬 SS", f"={SSres}-{SSpe}", "即 殘差SS − 純誤差SS：各濃度平均離「直線」多遠", key=True)
    dfpe = book.calc(ws3, 25, "df_純誤差", f"=COUNT({yrng})-5", "N − 濃度數 = 15−5", fmt="0")
    dflof = book.calc(ws3, 26, "df_失擬", "=5-2", "濃度數 − 直線參數數(斜率+截距)", fmt="0")
    Flof = book.calc(ws3, 27, "F", f"=({SSlof}/{dflof})/({SSpe}/{dfpe})", key=True)
    plof = book.calc(ws3, 28, "p 值（失擬檢定）", f"=F.DIST.RT({Flof},{dflof},{dfpe})", "p 大才好：不顯著代表看不出直線不夠用（不等於「證明」是直線）", key=True)
    book.text(ws3, 30, 1, "這組資料高濃度時散布明顯較大（詳見 Ch04 的加權迴歸範例）；本檢定看的是「彎不彎」，不是變異是否均齊。", size=10, color="64748B")

    # ---------------------------------------------------------------- checks
    book.check("雙因子：SS_total", "雙因子ANOVA", SStot, 2585.925)
    book.check("雙因子：SS_A（溫度）", "雙因子ANOVA", SSA, 1883.25)
    book.check("雙因子：SS_B（時間）", "雙因子ANOVA", SSB, 441.045)
    book.check("雙因子：SS_AB（交互作用）", "雙因子ANOVA", SSAB, 250.8033333)
    book.check("雙因子：F_A", "雙因子ANOVA", FA, 1043.67303)
    book.check("雙因子：F_AB", "雙因子ANOVA", FAB, 138.9919951)
    book.check("雙因子：p_AB", "雙因子ANOVA", pAB, 5.021614247e-09, tol=1e-12)
    book.check("精密度：s_r", "ISO5725精密度分解", sr, 0.09320228896)
    book.check("精密度：s_between", "ISO5725精密度分解", sbet, 0.09153627089)
    book.check("精密度：s_I", "ISO5725精密度分解", sI, 0.1306352003)
    book.check("精密度：全部丟進STDEV.S", "ISO5725精密度分解", naive, 0.1259705181)
    book.check("精密度：正確的當天平均不確定度", "ISO5725精密度分解", correct_se, 0.1061811869)
    book.check("失擬：殘差SS", "失擬檢定", SSres, 229158.7484, tol=0.5)
    book.check("失擬：純誤差SS", "失擬檢定", SSpe, 228110.6667, tol=0.5)
    book.check("失擬：失擬SS", "失擬檢定", SSlof, 1048.081698, tol=0.2)
    book.check("失擬：F", "失擬檢定", Flof, 0.01531539806)
    book.check("失擬：p", "失擬檢定", plof, 0.9972394847)
    return book
