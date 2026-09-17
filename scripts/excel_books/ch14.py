"""Ch14 實驗設計與反應曲面法 DOE/RSM —— 2^3 因子設計效應、曲率檢定、CCD 二階模型與失擬。

R 的答案來源：Rscript R/ch14_doe_rsm.R（超音波輔助萃取茶葉多酚 DPPH 清除率；
2^3 因子＋4 中心點的 dat1，與 CCD 20 個 run 的 ccd，數值與該章網頁完全相同，
set.seed(14)／set.seed(15) 產生，這裡原樣重建）。
"""
from excel_common import Book


def build():
    book = Book("ch14_doe_rsm.xlsx", "Ch14 DOE/RSM：2^3 因子效應、曲率檢定、CCD 二階模型", "ch14.html")
    book.readme([
        "# 這本活頁簿在做什麼",
        "情境：超音波輔助萃取茶葉多酚，反應值＝DPPH 清除率(%)。因子：A 乙醇濃度、B 萃取溫度、C 超音波時間（都用 ±1 編碼）。",
        "「2^3因子設計」用 8 個角落點＋4 個中心點，算出主效應、交互作用，並用中心點做「曲率檢定」（反應曲面是不是彎的）。",
        "「CCD二階模型」在 8 角落點外加 6 個軸點＋6 個中心點（共 20 run），配二階（含平方項）模型，"
        "算出某條件下的預測值、殘差 SS、中心點純誤差 SS，以及失擬檢定（模型夠不夠用）。",
        "# 怎麼用",
        "1. 「2^3因子設計」左邊黃色是編碼 A/B/C 與實測 y；右邊先算 6 個效應（A、B、C、AB、AC、BC），再做曲率檢定。",
        "2. 「CCD二階模型」用 LINEST 一次配出 10 個係數（用 INDEX 逐一取值）；下面「預測條件」區塊的 a/b/c 是黃格，改了就能看模型怎麼預測不同條件下的清除率。",
        "3. 試著把中心點的某個 y 改得離群一點，看純誤差 SS 變大、失擬檢定的 F 變小（模型看起來「更夠用」，這其實是假象，要小心解讀）。",
        "4. 「對照R答案」核對所有關鍵結果。",
        "# 觀念提醒",
        "① 效應＝高水準平均－低水準平均（對比÷4）；迴歸係數＝效應的一半——這是初學者最容易混淆的一步。",
        "② 曲率檢定的 H0 是「中心點平均＝因子點平均」；顯著就代表 2 水準的直線模型不夠用，需要 CCD 這種二階設計。",
        "③ LINEST 回傳的係數順序和 X 欄位順序<b>相反</b>（最後一欄的係數最先出現，截距永遠最後一個），INDEX(LINEST(...),1,k) 要對照清楚，不然會取錯係數。",
        "# 資料分析工具箱（Analysis ToolPak）操作步驟",
        "DOE 的效應計算本質上是加減平均，工具箱沒有專門的「因子設計」工具，但 CCD 的二階模型可以用工具箱的<b>迴歸</b>取代 LINEST：",
        "① 啟用：檔案 → 選項 → 增益集 → 管理「Excel 增益集」→ 執行 → 勾選「分析工具箱」。",
        "② 先在資料表右邊排好 A、B、C、A²、B²、C²、A×B、A×C、B×C 九欄（本活頁簿已經排好），「資料」→「資料分析」→「迴歸」。",
        "③ 「輸入 Y 範圍」放 y（DPPH）欄；「輸入 X 範圍」框住上述九欄（必須緊鄰）；若含標題文字，勾選「標記」。",
        "④ 輸出的「係數」欄從上到下依序對應 Intercept、A、B、C、A²、B²、C²、A×B、A×C、B×C——順序就是 X 範圍原本的欄位順序，"
        "<b>不像</b> LINEST 會反過來，這是兩者最大的差別；「殘差輸出」表可直接讀每一列的殘差，平方加總就是殘差 SS。",
        "⑤ 工具箱的迴歸輸出是靜態表；本活頁簿用 LINEST／INDEX 寫成公式，改黃色數據會自動重算。",
    ])

    # ================================================================ 1. 2^3 因子設計
    ws = book.sheet("2^3因子設計", [26, 14, 44, 60, 12, 12, 12])
    book.header(ws, 1, ["A(乙醇)", "B(溫度)", "C(時間)", "AB", "AC", "BC", "y(DPPH%)"])
    facA = [-1, 1, -1, 1, -1, 1, -1, 1]
    facB = [-1, -1, 1, 1, -1, -1, 1, 1]
    facC = [-1, -1, -1, -1, 1, 1, 1, 1]
    facY = [33.7, 41.6, 38.0, 52.3, 38.5, 45.0, 39.4, 55.8]
    rA = book.data(ws, 2, 1, facA, fmt="0")
    rB = book.data(ws, 2, 2, facB, fmt="0")
    rC = book.data(ws, 2, 3, facC, fmt="0")
    for i in range(8):
        r = 2 + i
        ws.cell(row=r, column=4, value=f"=A{r}*B{r}").number_format = "0"
        ws.cell(row=r, column=5, value=f"=A{r}*C{r}").number_format = "0"
        ws.cell(row=r, column=6, value=f"=B{r}*C{r}").number_format = "0"
    rY = book.data(ws, 2, 7, facY, fmt="0.0")
    rAB, rAC, rBC = "D2:D9", "E2:E9", "F2:F9"

    book.text(ws, 11, 1, "中心點 y（A=B=C=0，4 次獨立重複萃取）", bold=True)
    ctrY = book.data(ws, 12, 1, [59.5, 61.3, 59.5, 60.4], fmt="0.0")

    book.header(ws, 18, ["項目", "結果", "公式", "白話說明"])
    contrA = book.calc(ws, 19, "對比 contrast_A", f"=SUMPRODUCT({rA},{rY})", "Σ(A欄 × y)")
    effA = book.calc(ws, 20, "效應 effect_A", f"={contrA}/4", "對比 ÷ (N/2) = 對比 ÷ 4（N=8）", key=True)
    coefA = book.calc(ws, 21, "係數 coef_A", f"={effA}/2", "效應的一半")
    contrB = book.calc(ws, 22, "對比 contrast_B", f"=SUMPRODUCT({rB},{rY})")
    effB = book.calc(ws, 23, "效應 effect_B", f"={contrB}/4", key=True)
    coefB = book.calc(ws, 24, "係數 coef_B", f"={effB}/2")
    contrC = book.calc(ws, 25, "對比 contrast_C", f"=SUMPRODUCT({rC},{rY})")
    effC = book.calc(ws, 26, "效應 effect_C", f"={contrC}/4", key=True)
    coefC = book.calc(ws, 27, "係數 coef_C", f"={effC}/2")
    contrAB = book.calc(ws, 28, "對比 contrast_AB", f"=SUMPRODUCT({rAB},{rY})")
    effAB = book.calc(ws, 29, "效應 effect_AB（交互作用）", f"={contrAB}/4", key=True)
    coefAB = book.calc(ws, 30, "係數 coef_AB", f"={effAB}/2")
    contrAC = book.calc(ws, 31, "對比 contrast_AC", f"=SUMPRODUCT({rAC},{rY})")
    effAC = book.calc(ws, 32, "效應 effect_AC", f"={contrAC}/4")
    contrBC = book.calc(ws, 33, "對比 contrast_BC", f"=SUMPRODUCT({rBC},{rY})")
    effBC = book.calc(ws, 34, "效應 effect_BC", f"={contrBC}/4")

    book.text(ws, 36, 1, "曲率檢定：中心點平均 vs 因子點平均", bold=True)
    meanFac = book.calc(ws, 37, "因子點平均", f"=AVERAGE({rY})")
    meanCtr = book.calc(ws, 38, "中心點平均", f"=AVERAGE({ctrY})")
    sPure = book.calc(ws, 39, "純誤差 s_pure", f"=STDEV.S({ctrY})", "只有中心點重複能給出的誤差估計")
    tCurv = book.calc(ws, 40, "曲率 t 值", f"=({meanCtr}-{meanFac})/({sPure}*SQRT(1/4+1/8))", key=True)
    pCurv = book.calc(ws, 41, "曲率 p 值（雙尾）", f"=T.DIST.2T(ABS({tCurv}),3)",
                       "H0：中心點平均＝因子點平均（曲面沒有彎）", key=True)
    book.text(ws, 43, 1, "p 值極小 → 反應曲面是彎的，直線模型不夠用，需要升級到 CCD（見「CCD二階模型」）。", size=10, color="64748B")

    # ================================================================ 2. CCD 二階模型
    ws2 = book.sheet("CCD二階模型", [26, 14, 44, 60, 12, 12, 12, 12, 12, 12, 14, 14])
    alpha = 1.681792831
    book.header(ws2, 1, ["A", "B", "C", "A²", "B²", "C²", "AB", "AC", "BC", "y(DPPH%)", "ŷ（模型預測）", "殘差 y−ŷ"])
    A_vals = [-1, 1, -1, 1, -1, 1, -1, 1, -alpha, alpha, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    B_vals = [-1, -1, 1, 1, -1, -1, 1, 1, 0, 0, -alpha, alpha, 0, 0, 0, 0, 0, 0, 0, 0]
    C_vals = [-1, -1, -1, -1, 1, 1, 1, 1, 0, 0, 0, 0, -alpha, alpha, 0, 0, 0, 0, 0, 0]
    y_vals = [34.8, 41.7, 35.1, 51.6, 39.1, 42.0, 39.5, 55.8,
              31.6, 47.3, 41.8, 50.5, 39.9, 44.9,
              61.8, 60.0, 60.0, 60.0, 58.6, 59.4]
    book.data(ws2, 2, 1, A_vals, fmt="0.000")
    book.data(ws2, 2, 2, B_vals, fmt="0.000")
    book.data(ws2, 2, 3, C_vals, fmt="0.000")
    for i in range(20):
        r = 2 + i
        ws2.cell(row=r, column=4, value=f"=A{r}^2").number_format = "0.0000"
        ws2.cell(row=r, column=5, value=f"=B{r}^2").number_format = "0.0000"
        ws2.cell(row=r, column=6, value=f"=C{r}^2").number_format = "0.0000"
        ws2.cell(row=r, column=7, value=f"=A{r}*B{r}").number_format = "0.0000"
        ws2.cell(row=r, column=8, value=f"=A{r}*C{r}").number_format = "0.0000"
        ws2.cell(row=r, column=9, value=f"=B{r}*C{r}").number_format = "0.0000"
    book.data(ws2, 2, 10, y_vals, fmt="0.0")
    Xrng, Yrng = "A2:I21", "J2:J21"

    book.header(ws2, 23, ["係數（LINEST）", "值", "公式", "白話說明"])
    coef_int = book.calc(ws2, 24, "Intercept", f"=INDEX(LINEST({Yrng},{Xrng}),1,10)",
                          "LINEST 係數順序與 X 欄位相反：截距永遠是最後一個", key=True)
    coef_A = book.calc(ws2, 25, "coef_A", f"=INDEX(LINEST({Yrng},{Xrng}),1,9)",
                        "X 第1欄(A)的係數在陣列倒數第2位", key=True)
    coef_B = book.calc(ws2, 26, "coef_B", f"=INDEX(LINEST({Yrng},{Xrng}),1,8)")
    coef_C = book.calc(ws2, 27, "coef_C", f"=INDEX(LINEST({Yrng},{Xrng}),1,7)")
    coef_A2 = book.calc(ws2, 28, "coef_A²", f"=INDEX(LINEST({Yrng},{Xrng}),1,6)")
    coef_B2 = book.calc(ws2, 29, "coef_B²", f"=INDEX(LINEST({Yrng},{Xrng}),1,5)")
    coef_C2 = book.calc(ws2, 30, "coef_C²", f"=INDEX(LINEST({Yrng},{Xrng}),1,4)")
    coef_AB = book.calc(ws2, 31, "coef_AB", f"=INDEX(LINEST({Yrng},{Xrng}),1,3)")
    coef_AC = book.calc(ws2, 32, "coef_AC", f"=INDEX(LINEST({Yrng},{Xrng}),1,2)")
    coef_BC = book.calc(ws2, 33, "coef_BC", f"=INDEX(LINEST({Yrng},{Xrng}),1,1)",
                         "X 最後一欄(BC)的係數在陣列第1位")

    # 每列的 ŷ 與殘差（引用上面的係數格：Intercept=B24, coef_A=B25 ... coef_BC=B33）
    for i in range(20):
        r = 2 + i
        yhat_f = (f"=$B$24+A{r}*$B$25+B{r}*$B$26+C{r}*$B$27+D{r}*$B$28+E{r}*$B$29"
                  f"+F{r}*$B$30+G{r}*$B$31+H{r}*$B$32+I{r}*$B$33")
        ws2.cell(row=r, column=11, value=yhat_f).number_format = "0.0000"
        ws2.cell(row=r, column=12, value=f"=J{r}-K{r}").number_format = "0.0000"

    book.text(ws2, 35, 1, "殘差、純誤差與失擬檢定", bold=True)
    book.header(ws2, 36, ["項目", "結果", "公式", "白話說明"])
    SSres = book.calc(ws2, 37, "殘差 SS", "=SUMSQ(L2:L21)", "模型 ŷ 與實測 y 的差，逐列平方加總", key=True)
    SSpe = book.calc(ws2, 38, "中心點純誤差 SS", "=DEVSQ(J16:J21)", "只有 6 個中心點重複能提供純誤差（df=5）", key=True)
    SSlof = book.calc(ws2, 39, "失擬 SS", f"={SSres}-{SSpe}", key=True)
    dfres = book.calc(ws2, 40, "df_殘差", "=20-10", "20 個 run − 10 個模型參數", fmt="0")
    dfpe = book.calc(ws2, 41, "df_純誤差", "=6-1", "6 個中心點", fmt="0")
    dflof = book.calc(ws2, 42, "df_失擬", f"={dfres}-{dfpe}", fmt="0")
    Flof = book.calc(ws2, 43, "F（失擬檢定）", f"=({SSlof}/{dflof})/({SSpe}/{dfpe})", key=True)
    plof = book.calc(ws2, 44, "p 值", f"=F.DIST.RT({Flof},{dflof},{dfpe})",
                      "p 大才好：不顯著＝在純誤差的尺度下看不出模型不足", key=True)

    book.text(ws2, 46, 1, "在特定條件下用二階模型預測（a/b/c 是黃格，可以改）", bold=True)
    book.header(ws2, 47, ["項目", "結果", "公式", "白話說明"])
    a_in = book.calc(ws2, 48, "a（A 編碼，預設＝駐點）", 0.4425692885, fmt="0.0000")
    book.mark_input(ws2, a_in)
    b_in = book.calc(ws2, 49, "b（B 編碼，預設＝駐點）", 0.4454640128, fmt="0.0000")
    book.mark_input(ws2, b_in)
    c_in = book.calc(ws2, 50, "c（C 編碼，預設＝駐點）", 0.1302946816, fmt="0.0000")
    book.mark_input(ws2, c_in)
    a2 = book.calc(ws2, 51, "a²", f"={a_in}^2", fmt="0.0000")
    b2 = book.calc(ws2, 52, "b²", f"={b_in}^2", fmt="0.0000")
    c2 = book.calc(ws2, 53, "c²", f"={c_in}^2", fmt="0.0000")
    ab = book.calc(ws2, 54, "a×b", f"={a_in}*{b_in}", fmt="0.0000")
    ac = book.calc(ws2, 55, "a×c", f"={a_in}*{c_in}", fmt="0.0000")
    bc = book.calc(ws2, 56, "b×c", f"={b_in}*{c_in}", fmt="0.0000")
    yhat0 = book.calc(ws2, 57, "預測 ŷ（DPPH 清除率%）",
                       f"={coef_int}+{a_in}*{coef_A}+{b_in}*{coef_B}+{c_in}*{coef_C}"
                       f"+{a2}*{coef_A2}+{b2}*{coef_B2}+{c2}*{coef_C2}+{ab}*{coef_AB}+{ac}*{coef_AC}+{bc}*{coef_BC}",
                       "代入二階模型的 10 個係數與這個條件的 a/b/c", key=True)
    book.text(ws2, 59, 1, "駐點座標與特徵值需要解 3×3 矩陣，Excel 用 MINVERSE/MMULT 或 Solver 也能做但很繁瑣；"
              "本章用 R 的 solve()、eigen() 一步到位，這正是「何時該升級到 R」的示範。", size=10, color="64748B")

    # ---------------------------------------------------------------- checks
    book.check("2^3：效應 effect_A", "2^3因子設計", effA, 11.275)
    book.check("2^3：效應 effect_B", "2^3因子設計", effB, 6.675)
    book.check("2^3：效應 effect_AB", "2^3因子設計", effAB, 4.075)
    book.check("2^3：曲率 t 值", "2^3因子設計", tCurv, 32.47757579)
    book.check("2^3：曲率 p 值", "2^3因子設計", pCurv, 6.415635344e-05, tol=1e-9)
    book.check("CCD：Intercept", "CCD二階模型", coef_int, 59.939778091)
    book.check("CCD：coef_A", "CCD二階模型", coef_A, 5.052711714)
    book.check("CCD：coef_BC", "CCD二階模型", coef_BC, 0.5)
    book.check("CCD：預測 ŷ0（駐點）", "CCD二階模型", yhat0, 61.79752003)
    book.check("CCD：殘差 SS", "CCD二階模型", SSres, 11.80544438)
    book.check("CCD：純誤差 SS", "CCD二階模型", SSpe, 5.553333333)
    book.check("CCD：失擬 SS", "CCD二階模型", SSlof, 6.252111046)
    book.check("CCD：F（失擬）", "CCD二階模型", Flof, 1.12583032)
    book.check("CCD：p（失擬）", "CCD二階模型", plof, 0.449844969)
    return book
