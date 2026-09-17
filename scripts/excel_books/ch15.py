"""Ch15 假說檢定與 t／F 檢定 —— one-sample t／paired t／Welch t／F 檢定。

R 的答案來源：Rscript R/ch15_hypothesis_tests.R（CRM 偏倚、凱氏/杜馬斯成對、醬油兩產線 Welch、
資深/新人分析員 F 檢定，數據與該章網頁完全相同）。
"""
from excel_common import Book


def build():
    book = Book("ch15_hypothesis_tests.xlsx", "Ch15 假說檢定：t 檢定與 F 檢定", "ch15.html")
    book.readme([
        "# 這本活頁簿在做什麼",
        "本章比較「一組數據 vs 一個已知值」（one-sample t）、「同一批樣品測兩次」（paired t）、"
        "「兩組互相獨立的樣品」（Welch t）、「兩組精密度誰比較好」（F 檢定）四種最常用的檢定。",
        "四張計算表都先「逐步公式版」（看得到 t、p、df 每一步怎麼來），再放「一格函數版」"
        "（T.TEST／F.TEST）互相對照，數字要一樣才對。",
        "# 怎麼用",
        "1. 每張表左邊黃色是原始數據，右邊每一列是一個公式，C 欄印出公式原文。",
        "2. 「Welch t」表把 Welch–Satterthwaite 自由度拆成三步（see the 分子/分母 rows）——這是本章最容易被跳過的計算。",
        "3. 試著把「paired t」表的杜馬斯數據改一兩個值，看 p 值怎麼變；也試試把 paired 的兩欄硬套進「兩獨立樣本」公式，體會 15.5 節「誤用」的後果。",
        "4. 「對照R答案」工作表核對 Excel 與 R 是否一致。",
        "# 觀念提醒",
        "T.TEST 和 F.TEST 只回傳「雙尾 p 值」，不會給你 t／F 統計量、自由度或信賴區間；"
        "要完整報告，仍要用本活頁簿的「逐步公式版」或回到 R。",
        "T.TEST 第 4 個引數（type）：1＝成對（paired）、2＝兩獨立樣本且假設變異數相等、3＝兩獨立樣本且不假設變異數相等（Welch，預設應選這個）。",
        "# 資料分析工具箱（Analysis ToolPak）操作步驟",
        "① 啟用：檔案 → 選項 → 增益集 → 管理「Excel 增益集」→ 執行 → 勾選「分析工具箱」→ 確定。之後「資料」分頁會出現「資料分析」按鈕。",
        "② 三種 t 檢定：「資料」→「資料分析」→ 依情境選：",
        "　・成對數據（如凱氏 vs 杜馬斯同一樣品各測一次）→「t 檢定：成對母體平均差異檢定」；「變數 1 範圍」放杜馬斯、「變數 2 範圍」放凱氏、"
        "「假設的均值差」填 0。輸出的 t、自由度、雙尾 P 值分別對應 R 的 t.test(paired=TRUE) 的 t、df、p-value。",
        "　・兩獨立樣本、不假設變異數相等（醬油兩產線）→「t 檢定：兩個母體平均數差的檢定，假設變異數不相等」（Welch）。輸出的 t Stat、自由度（注意是小數！）、"
        "P(T<=t) 雙尾就是 R 的 t、df、p。",
        "　・兩獨立樣本、假設變異數相等 → 「t 檢定：兩個母體平均數差的檢定，假設變異數相等」——本章刻意示範這個假設不成立時結論會翻盤（見「Welch t」表）。",
        "　・one-sample t（CRM 認證值）Excel 工具箱<b>沒有</b>這個選項，只能用本活頁簿「逐步公式版」自己算，或把認證值當成配對的另一欄硬湊成對比較（不建議，容易搞混）。",
        "③ F 檢定（兩個常態母體變異數）：「資料分析」→「F 檢定：兩個常態母體變異數的檢定」；「變數 1 範圍」放新人、「變數 2 範圍」放資深、α = 0.05。"
        "輸出的 F 值對應 VAR.S(新人)/VAR.S(資深)；「F 單尾」是單尾臨界值與 p；若要雙尾 p 要自己乘 2（或直接用 F.TEST，見計算表）。",
        "④ 工具箱輸出是<strong>靜態貼上的數字</strong>：改了原始數據，工具箱的表不會自動重算，要重新跑一次「資料分析」；本活頁簿的公式版會自動重算，這是兩者最大的差別。",
    ])

    # ---------------------------------------------------------------- 1. one-sample t
    ws = book.sheet("one-sample t", [26, 16, 46, 62])
    book.header(ws, 1, ["奶粉CRM粗蛋白 (g/100 g)"])
    crm = book.data(ws, 2, 1, [34.92, 35.12, 34.85, 35.04, 34.81, 34.98], fmt="0.00")
    book.header(ws, 9, ["項目", "結果", "公式", "白話說明"])
    n = book.calc(ws, 10, "n（重複次數）", f"=COUNT({crm})", "數一數測了幾次", fmt="0")
    mean = book.calc(ws, 11, "平均 x̄", f"=AVERAGE({crm})", "6 次凱氏法的平均")
    sd = book.calc(ws, 12, "標準差 SD", f"=STDEV.S({crm})", "分母 n−1")
    cert = book.calc(ws, 13, "CRM 認證值 μ₀", 35.10, "可以改成別的認證值試試", fmt="0.00")
    book.mark_input(ws, cert)
    bias = book.calc(ws, 14, "偏倚 bias = x̄ − μ₀", f"={mean}-{cert}", "平均離認證值多遠")
    se = book.calc(ws, 15, "標準誤 SEM", f"={sd}/SQRT({n})", "SD ÷ √n")
    t0 = book.calc(ws, 16, "t 值", f"={bias}/{se}", "bias ÷ SEM", key=True)
    df = book.calc(ws, 17, "自由度 df", f"={n}-1", "n − 1", fmt="0")
    p2t = book.calc(ws, 18, "雙尾 p 值", f"=T.DIST.2T(ABS({t0}),{df})", "t 要先取絕對值，T.DIST.2T 才是雙尾", key=True)
    tcrit = book.calc(ws, 19, "雙尾臨界值 t(0.975,5)", f"=T.INV.2T(0.05,{df})", "|t| 超過這個值就顯著")
    recov = book.calc(ws, 20, "回收率 (%)", f"={mean}/{cert}*100", "呼應 Ch06 的真度 (trueness)")
    book.text(ws, 22, 1, "Excel 的資料分析工具箱沒有 one-sample t 檢定，只能像這樣自己拼公式；T.TEST 只能比較兩組數據。", size=10, color="64748B")

    # ---------------------------------------------------------------- 2. paired t
    ws2 = book.sheet("paired t", [16, 16, 16, 16, 46, 46])
    book.header(ws2, 1, ["食品", "凱氏法 (%)", "杜馬斯法 (%)", "差值 d=杜−凱"])
    foods = ["鮮乳", "優格", "豆漿", "白米", "麵粉", "雞蛋", "豬里肌", "雞胸肉", "黃豆粉", "脫脂奶粉"]
    kjeldahl = [3.12, 3.85, 3.41, 6.92, 11.85, 12.48, 20.35, 23.10, 36.42, 35.18]
    dumas = [3.20, 4.07, 3.37, 7.11, 11.95, 12.79, 20.37, 23.36, 36.65, 35.30]
    for i, food in enumerate(foods):
        book.text(ws2, 2 + i, 1, food)
    krng = book.data(ws2, 2, 2, kjeldahl, fmt="0.00")
    drng_col = book.data(ws2, 2, 3, dumas, fmt="0.00")
    for i in range(len(foods)):
        r = 2 + i
        cell = ws2.cell(row=r, column=4, value=f"=C{r}-B{r}")
        cell.number_format = "0.0000"
    dvals = f"D2:D{1+len(foods)}"

    book.header(ws2, 13, ["項目", "結果", "公式", "白話說明"], col=1)
    n2 = book.calc(ws2, 14, "n（配對數）", f"=COUNT({dvals})", "10 個樣品各測 2 次", fmt="0")
    mean_d = book.calc(ws2, 15, "平均差 d̄", f"=AVERAGE({dvals})", "成對 t 其實就是對差值做 one-sample t")
    sd_d = book.calc(ws2, 16, "差值標準差 SD_d", f"=STDEV.S({dvals})")
    se_d = book.calc(ws2, 17, "標準誤 SE_d", f"={sd_d}/SQRT({n2})")
    df2 = book.calc(ws2, 18, "自由度 df", f"={n2}-1", fmt="0")
    t2 = book.calc(ws2, 19, "t 值", f"={mean_d}/{se_d}", "d̄ ÷ SE_d", key=True)
    p2 = book.calc(ws2, 20, "雙尾 p 值（逐步公式版）", f"=T.DIST.2T(ABS({t2}),{df2})", key=True)
    p2_fn = book.calc(ws2, 21, "雙尾 p 值（T.TEST，type=1 成對）", f"=T.TEST({krng},{drng_col},2,1)",
                       "與上一列應該完全相同", key=True)
    p2_wrong = book.calc(ws2, 22, "✗ 誤用：當成兩獨立樣本（type=3）", f"=T.TEST({krng},{drng_col},2,3)",
                          "p 值變得完全不同（p≈0.98）——這就是 15.5 節的誤用示範，成對資料不能拆開比")
    book.text(ws2, 24, 1, "正確：成對設計一定要用「差值」或 T.TEST(...,type=1)；把兩欄當獨立樣本會把「樣品間本來就有的大差異」誤當成誤差，嚴重低估檢定力。",
              size=10, color="64748B")

    # ---------------------------------------------------------------- 3. Welch t
    ws3 = book.sheet("Welch t", [30, 16, 50, 60])
    book.header(ws3, 1, ["A 產線總氮 (g/100 mL)", "B 產線總氮 (g/100 mL)"])
    rngA = book.data(ws3, 2, 1, [1.52, 1.38, 1.61, 1.45], fmt="0.00")
    rngB = book.data(ws3, 2, 2, [1.41, 1.38, 1.43, 1.39, 1.42, 1.37, 1.40, 1.44, 1.38, 1.41], fmt="0.00")
    book.header(ws3, 13, ["項目", "結果", "公式", "白話說明"])
    nA = book.calc(ws3, 14, "n_A", f"=COUNT({rngA})", fmt="0")
    nB = book.calc(ws3, 15, "n_B", f"=COUNT({rngB})", fmt="0")
    meanA = book.calc(ws3, 16, "平均 x̄_A", f"=AVERAGE({rngA})")
    meanB = book.calc(ws3, 17, "平均 x̄_B", f"=AVERAGE({rngB})")
    varA = book.calc(ws3, 18, "變異數 s²_A", f"=VAR.S({rngA})")
    varB = book.calc(ws3, 19, "變異數 s²_B", f"=VAR.S({rngB})")
    seA2 = book.calc(ws3, 20, "s²_A / n_A", f"={varA}/{nA}")
    seB2 = book.calc(ws3, 21, "s²_B / n_B", f"={varB}/{nB}")
    se = book.calc(ws3, 22, "合併標準誤 SE = √(s²_A/n_A + s²_B/n_B)", f"=SQRT({seA2}+{seB2})", "兩組互相獨立，變異數要先分別除 n 再相加")
    diff = book.calc(ws3, 23, "平均差 x̄_A − x̄_B", f"={meanA}-{meanB}")
    tW = book.calc(ws3, 24, "Welch t 值", f"={diff}/{se}", key=True)
    df_num = book.calc(ws3, 25, "Welch–Satterthwaite df 分子 = (s²_A/n_A+s²_B/n_B)²", f"=({seA2}+{seB2})^2")
    df_denA = book.calc(ws3, 26, "分母第一項 = (s²_A/n_A)²/(n_A−1)", f"=({seA2})^2/({nA}-1)")
    df_denB = book.calc(ws3, 27, "分母第二項 = (s²_B/n_B)²/(n_B−1)", f"=({seB2})^2/({nB}-1)")
    dfW = book.calc(ws3, 28, "Welch df", f"={df_num}/({df_denA}+{df_denB})", "小數自由度是正常的，不是算錯", key=True)
    p_fn = book.calc(ws3, 29, "雙尾 p 值（T.TEST，type=3 Welch）", f"=T.TEST({rngA},{rngB},2,3)",
                      "T.DIST.2T 對非整數 df 會自動截斷，用 T.TEST 比較準", key=True)
    p_eqvar = book.calc(ws3, 30, "✗ 硬假設等變異（type=2）的 p 值", f"=T.TEST({rngA},{rngB},2,2)",
                         "結論翻盤：p 從「不顯著」變「顯著」——這正是本章強調『Welch 當預設』的原因")
    book.text(ws3, 32, 1, "A、B 兩產線的變異數看起來差很多（s²_A 遠大於 s²_B），硬套等變異假設會低估真正的不確定性，讓 p 值變得過小。", size=10, color="64748B")

    # ---------------------------------------------------------------- 4. F 檢定
    ws4 = book.sheet("F檢定", [26, 16, 50, 60])
    book.header(ws4, 1, ["資深分析員 粗脂肪 (%)", "新人分析員 粗脂肪 (%)"])
    rngS = book.data(ws4, 2, 1, [14.52, 14.61, 14.48, 14.57, 14.66, 14.50, 14.59, 14.55], fmt="0.00")
    rngJ = book.data(ws4, 2, 2, [14.31, 14.82, 14.47, 14.95, 14.20, 14.68, 14.39, 14.77], fmt="0.00")
    book.header(ws4, 11, ["項目", "結果", "公式", "白話說明"])
    sdS = book.calc(ws4, 12, "SD 資深", f"=STDEV.S({rngS})")
    sdJ = book.calc(ws4, 13, "SD 新人", f"=STDEV.S({rngJ})")
    varS = book.calc(ws4, 14, "變異數 資深", f"=VAR.S({rngS})")
    varJ = book.calc(ws4, 15, "變異數 新人", f"=VAR.S({rngJ})")
    Fv = book.calc(ws4, 16, "F = 新人變異數 / 資深變異數", f"={varJ}/{varS}", "F 檢定比的是「變異數比」，不是 SD 比", key=True)
    df1 = book.calc(ws4, 17, "分子 df（新人）", f"=COUNT({rngJ})-1", fmt="0")
    df2 = book.calc(ws4, 18, "分母 df（資深）", f"=COUNT({rngS})-1", fmt="0")
    p_manual = book.calc(ws4, 19, "雙尾 p（逐步公式版）", f"=2*MIN(F.DIST.RT({Fv},{df1},{df2}),F.DIST.RT(1/{Fv},{df2},{df1}))",
                          "雙尾 = 2 × 較小的那一尾機率", key=True)
    p_fn2 = book.calc(ws4, 20, "雙尾 p（F.TEST 函數）", f"=F.TEST({rngJ},{rngS})", "應與上一列相同", key=True)
    book.text(ws4, 22, 1, "F 檢定對「非常態」很敏感：兩組若其實來自同一個右偏母體，理論上只該有 5% 誤判機率，實際模擬常遠高於 5%（見 R 腳本第 7 節）。", size=10, color="64748B")

    # ---------------------------------------------------------------- checks
    book.check("one-sample t：平均", "one-sample t", mean, 34.95333333)
    book.check("one-sample t：SD", "one-sample t", sd, 0.1169045194)
    book.check("one-sample t：bias", "one-sample t", bias, -0.1466666667)
    book.check("one-sample t：t 值", "one-sample t", t0, -3.073093301)
    book.check("one-sample t：雙尾 p", "one-sample t", p2t, 0.02768619388)
    book.check("one-sample t：回收率%", "one-sample t", recov, 99.58214625)
    book.check("paired t：平均差 d̄", "paired t", mean_d, 0.149)
    book.check("paired t：t 值", "paired t", t2, 4.225828679)
    book.check("paired t：T.TEST(type=1) p", "paired t", p2_fn, 0.002220247911)
    book.check("paired t：誤用 type=3 p", "paired t", p2_wrong, 0.9792777325)
    book.check("Welch t：t 值", "Welch t", tW, 1.750495538)
    book.check("Welch t：df", "Welch t", dfW, 3.133646009)
    book.check("Welch t：T.TEST(type=3) p", "Welch t", p_fn, 0.1744118509)
    book.check("Welch t：誤用 type=2 p", "Welch t", p_eqvar, 0.01694716946)
    book.check("F 檢定：F 值", "F檢定", Fv, 20.07093254)
    book.check("F 檢定：F.TEST p", "F檢定", p_fn2, 0.0007897245359)
    return book
