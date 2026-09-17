"""Ch16 單因子變異數分析 One-way ANOVA —— 逐步公式、Tukey HSD、變異不等的醬油案例。

R 的答案來源：Rscript R/ch16_anova_oneway.R（三種溶劑萃取總多酚 tpc；四品牌醬油總氮 tn，
數據與該章網頁完全相同）。qtukey(0.95,3,12) 用 R 實算後當常數寫入（Excel 無此函數）。
"""
from excel_common import Book


def build():
    book = Book("ch16_anova_oneway.xlsx", "Ch16 單因子變異數分析：逐步 ANOVA 與 Tukey HSD", "ch16.html")
    book.readme([
        "# 這本活頁簿在做什麼",
        "三種溶劑（甲醇、乙醇、丙酮）萃取總多酚，各獨立萃取 5 次。「ANOVA逐步」把總變異拆成"
        "「組間」與「組內」，一步步算出 F 與 p；「TukeyHSD」接著問「哪兩組不一樣」；"
        "「醬油總氮」示範各組變異不等（heteroscedastic）時傳統 ANOVA 為什�麼會誤導。",
        "# 怎麼用",
        "1. 「ANOVA逐步」左邊三欄黃色是三個溶劑的原始數據，右邊每一列一個公式，對照 SS_between/SS_within 怎麼一步步加總出來。",
        "2. 試著把丙酮欄隨便一個數字改小，看 F、p、η² 怎麼變。",
        "3. 「TukeyHSD」的臨界值 q（studentized range）Excel 沒有對應函數，已用 R 的 qtukey(0.95,3,12) 算好填在黃格——這格改了就不對，只是讓你知道它是「外部查表值」。",
        "4. 「醬油總氮」示範四品牌批次變異差很大（C、D 是 A、B 的 8~12 倍），傳統 ANOVA（假設等變異）會被稀釋掉，看起來「沒有差異」，但這個假設本身就不成立。",
        "# 觀念提醒",
        "① SS_between 用「各組平均離總平均多遠」（n×(組平均−總平均)²加總）；SS_within 用「組內每個數據離自己組平均多遠」（DEVSQ 逐組加總）；兩者相加＝SS_total。",
        "② Tukey HSD 的臨界值 q 來自 studentized range 分布，Excel 沒有內建函數，只能用 R 的 qtukey() 或查表；HSD = q × √(MS_within / n)，兩組平均差超過 HSD 才算顯著。",
        "③ Excel 工具箱完全沒有 Welch ANOVA；一旦各組變異明顯不等（如醬油案例），請改用 R 的 oneway.test()（不假設等變異）。",
        "# 資料分析工具箱操作步驟",
        "① 啟用：檔案 → 選項 → 增益集 → 管理「Excel 增益集」→ 執行 → 勾選「分析工具箱」。",
        "② 把各組數據排成並排的欄（每欄一組，如 A、B、C 各放一種溶劑）；「資料」→「資料分析」→「單因子變異數分析」（Anova: Single Factor）。",
        "③ 輸入範圍框住含標題列的全部數據、分組方式選「逐欄」、勾選「類別軸標記是在第一列上」、α = 0.05 → 確定。",
        "④ 輸出表對照：來源(組間/組內)→ SS/df/MS/F/P-值/臨界值 F crit，逐欄對應本活頁簿「ANOVA逐步」的 SS_between/SS_within、df、MS、F、p(F.DIST.RT)、F 臨界值(F.INV.RT)。",
        "⑤ 工具箱<b>沒有</b> Tukey HSD、Welch ANOVA 或殘差診斷；輸出也是靜態表，改數據要重跑一次「資料分析」才會更新——本活頁簿的公式版會自動重算。",
    ])

    # ---------------------------------------------------------------- 1. ANOVA 逐步
    ws = book.sheet("ANOVA逐步", [26, 16, 50, 60])
    book.header(ws, 1, ["甲醇 Methanol", "乙醇 Ethanol", "丙酮 Acetone"])
    rngM = book.data(ws, 2, 1, [12.4, 13.1, 12.8, 11.9, 12.6], fmt="0.0")
    rngE = book.data(ws, 2, 2, [13.0, 12.2, 13.5, 12.9, 13.3], fmt="0.0")
    rngA = book.data(ws, 2, 3, [14.8, 15.4, 14.5, 15.1, 15.6], fmt="0.0")
    all_rng = "A2:C6"

    book.header(ws, 8, ["項目", "結果", "公式", "白話說明"])
    nM = book.calc(ws, 9, "n 甲醇", f"=COUNT({rngM})", fmt="0")
    nE = book.calc(ws, 10, "n 乙醇", f"=COUNT({rngE})", fmt="0")
    nA = book.calc(ws, 11, "n 丙酮", f"=COUNT({rngA})", fmt="0")
    meanM = book.calc(ws, 12, "組平均 甲醇", f"=AVERAGE({rngM})")
    meanE = book.calc(ws, 13, "組平均 乙醇", f"=AVERAGE({rngE})")
    meanA = book.calc(ws, 14, "組平均 丙酮", f"=AVERAGE({rngA})")
    grand = book.calc(ws, 15, "總平均 grand mean", f"=AVERAGE({all_rng})", "15 筆數據的總平均")
    k = book.calc(ws, 16, "k（組數）", 3, fmt="0")
    N = book.calc(ws, 17, "N（總筆數）", f"=COUNT({all_rng})", fmt="0")
    SSb = book.calc(ws, 18, "SS_between",
                     f"={nM}*({meanM}-{grand})^2+{nE}*({meanE}-{grand})^2+{nA}*({meanA}-{grand})^2",
                     "各組 n×(組平均−總平均)² 加總", key=True)
    SSw = book.calc(ws, 19, "SS_within", f"=DEVSQ({rngM})+DEVSQ({rngE})+DEVSQ({rngA})",
                     "各組 DEVSQ（離均差平方和）加總", key=True)
    SSt = book.calc(ws, 20, "SS_total", f"=DEVSQ({all_rng})", "應該等於 SS_between + SS_within（核對用）")
    dfb = book.calc(ws, 21, "df_between", f"={k}-1", fmt="0")
    dfw = book.calc(ws, 22, "df_within", f"={N}-{k}", fmt="0")
    MSb = book.calc(ws, 23, "MS_between", f"={SSb}/{dfb}")
    MSw = book.calc(ws, 24, "MS_within", f"={SSw}/{dfw}")
    Fv = book.calc(ws, 25, "F 值", f"={MSb}/{MSw}", key=True)
    p = book.calc(ws, 26, "p 值（右尾）", f"=F.DIST.RT({Fv},{dfb},{dfw})", "F.DIST.RT 的 RT=right tail，對應 R 的 pf(...,lower.tail=FALSE)", key=True)
    Fcrit = book.calc(ws, 27, "F 臨界值 (α=0.05)", f"=F.INV.RT(0.05,{dfb},{dfw})")
    eta2 = book.calc(ws, 28, "效果量 η²", f"={SSb}/{SSt}", "總變異中有多少比例可用「溶劑不同」解釋", key=True)
    book.text(ws, 30, 1, "檢查：SS_between + SS_within 應該等於 SS_total（B18+B19 = B20）。", size=10, color="64748B")

    # ---------------------------------------------------------------- 2. Tukey HSD
    ws2 = book.sheet("TukeyHSD", [30, 16, 54, 60])
    book.header(ws2, 1, ["項目", "結果", "公式", "白話說明"])
    qcrit = book.calc(ws2, 2, "臨界值 q (α=0.05, k=3, df=12)", 3.772928959,
                       "studentized range 分布，Excel 沒有函數，用 R 的 qtukey(0.95,3,12) 實算填入")
    book.mark_input(ws2, qcrit)
    npg = book.calc(ws2, 3, "每組 n", 5, fmt="0")
    book.mark_input(ws2, npg)
    MSw_ref = book.calc(ws2, 4, "MS_within（引用 ANOVA逐步）", f"='ANOVA逐步'!{MSw}")
    HSD = book.calc(ws2, 5, "HSD = q × √(MS_within/n)", f"={qcrit}*SQRT({MSw_ref}/{npg})",
                     "兩組平均至少要差這麼多才顯著", key=True)
    meanM_ref = book.calc(ws2, 7, "組平均 甲醇（引用）", f"='ANOVA逐步'!{meanM}")
    meanE_ref = book.calc(ws2, 8, "組平均 乙醇（引用）", f"='ANOVA逐步'!{meanE}")
    meanA_ref = book.calc(ws2, 9, "組平均 丙酮（引用）", f"='ANOVA逐步'!{meanA}")
    diff_AM = book.calc(ws2, 10, "丙酮 − 甲醇", f"={meanA_ref}-{meanM_ref}", key=True)
    diff_AE = book.calc(ws2, 11, "丙酮 − 乙醇", f"={meanA_ref}-{meanE_ref}", key=True)
    diff_EM = book.calc(ws2, 12, "乙醇 − 甲醇", f"={meanE_ref}-{meanM_ref}", key=True)
    book.calc(ws2, 13, "丙酮 vs 甲醇 顯著？", f'=IF(ABS({diff_AM})>{HSD},"顯著","不顯著")', fmt="@")
    book.calc(ws2, 14, "丙酮 vs 乙醇 顯著？", f'=IF(ABS({diff_AE})>{HSD},"顯著","不顯著")', fmt="@")
    book.calc(ws2, 15, "乙醇 vs 甲醇 顯著？", f'=IF(ABS({diff_EM})>{HSD},"顯著","不顯著")', fmt="@")
    book.text(ws2, 17, 1, "Excel 資料分析工具箱沒有 Tukey HSD；q 值必須從 R（qtukey）或統計表查得，不能用 Excel 現成函數算出。", size=10, color="64748B")

    # ---------------------------------------------------------------- 3. 醬油總氮（變異不等）
    ws3 = book.sheet("醬油總氮(變異不等)", [26, 16, 50, 60])
    book.header(ws3, 1, ["A 大廠", "B 大廠", "C 小廠", "D 小廠"])
    rA = book.data(ws3, 2, 1, [1.42, 1.45, 1.43, 1.46, 1.44, 1.41], fmt="0.00")
    rB = book.data(ws3, 2, 2, [1.52, 1.50, 1.55, 1.51, 1.53, 1.49], fmt="0.00")
    rC = book.data(ws3, 2, 3, [1.38, 1.62, 1.25, 1.71, 1.49, 1.30], fmt="0.00")
    rD = book.data(ws3, 2, 4, [1.60, 1.33, 1.78, 1.41, 1.69, 1.22], fmt="0.00")
    all3 = "A2:D7"
    book.header(ws3, 9, ["項目", "結果", "公式", "白話說明"])
    mA = book.calc(ws3, 10, "組平均 A", f"=AVERAGE({rA})")
    mB = book.calc(ws3, 11, "組平均 B", f"=AVERAGE({rB})")
    mC = book.calc(ws3, 12, "組平均 C", f"=AVERAGE({rC})")
    mD = book.calc(ws3, 13, "組平均 D", f"=AVERAGE({rD})")
    sA = book.calc(ws3, 14, "組 SD A", f"=STDEV.S({rA})")
    sB = book.calc(ws3, 15, "組 SD B", f"=STDEV.S({rB})")
    sC = book.calc(ws3, 16, "組 SD C", f"=STDEV.S({rC})", "C、D 的批次變異明顯比 A、B 大很多")
    sD = book.calc(ws3, 17, "組 SD D", f"=STDEV.S({rD})")
    ratio = book.calc(ws3, 18, "最大SD ÷ 最小SD", f"=MAX({sA},{sB},{sC},{sD})/MIN({sA},{sB},{sC},{sD})",
                       "粗略檢查變異是否等質；差太多就不該用傳統 ANOVA 的等變異假設")
    grand3 = book.calc(ws3, 19, "總平均", f"=AVERAGE({all3})")
    k3 = book.calc(ws3, 20, "k（組數）", 4, fmt="0")
    N3 = book.calc(ws3, 21, "N（總筆數）", f"=COUNT({all3})", fmt="0")
    SSb3 = book.calc(ws3, 22, "SS_between",
                      f"=6*({mA}-{grand3})^2+6*({mB}-{grand3})^2+6*({mC}-{grand3})^2+6*({mD}-{grand3})^2",
                      "各組 n×(組平均−總平均)² 加總（n=6）", key=True)
    SSw3 = book.calc(ws3, 23, "SS_within", f"=DEVSQ({rA})+DEVSQ({rB})+DEVSQ({rC})+DEVSQ({rD})", key=True)
    dfb3 = book.calc(ws3, 24, "df_between", f"={k3}-1", fmt="0")
    dfw3 = book.calc(ws3, 25, "df_within", f"={N3}-{k3}", fmt="0")
    MSb3 = book.calc(ws3, 26, "MS_between", f"={SSb3}/{dfb3}")
    MSw3 = book.calc(ws3, 27, "MS_within", f"={SSw3}/{dfw3}")
    Fv3 = book.calc(ws3, 28, "傳統 ANOVA F（假設等變異）", f"={MSb3}/{MSw3}", key=True)
    p3 = book.calc(ws3, 29, "傳統 ANOVA p", f"=F.DIST.RT({Fv3},{dfb3},{dfw3})", key=True)
    book.text(ws3, 31, 1,
              "傳統 ANOVA 得到 p ≈ 0.73「沒有差異」，但這是因為 C、D 的巨大批次變異把組間差異淹沒、又違反等變異假設。"
              "R 的 Welch ANOVA（oneway.test，不假設等變異）算出 F ≈ 14.46、p ≈ 0.00057——結論完全相反！"
              "Excel 資料分析工具箱沒有 Welch ANOVA，這種情況務必回到 R。", size=10, color="B91C1C")

    # ---------------------------------------------------------------- checks
    book.check("ANOVA：總平均", "ANOVA逐步", grand, 13.54)
    book.check("ANOVA：SS_between", "ANOVA逐步", SSb, 18.228)
    book.check("ANOVA：SS_within", "ANOVA逐步", SSw, 2.588)
    book.check("ANOVA：F 值", "ANOVA逐步", Fv, 42.25965997)
    book.check("ANOVA：p 值", "ANOVA逐步", p, 3.6931926e-06, tol=1e-9)
    book.check("ANOVA：η²", "ANOVA逐步", eta2, 0.8756725596)
    book.check("Tukey：HSD", "TukeyHSD", HSD, 0.7835832407)
    book.check("Tukey：丙酮−甲醇", "TukeyHSD", diff_AM, 2.52)
    book.check("Tukey：丙酮−乙醇", "TukeyHSD", diff_AE, 2.10)
    book.check("Tukey：乙醇−甲醇", "TukeyHSD", diff_EM, 0.42)
    book.check("醬油：組平均 C", "醬油總氮(變異不等)", mC, 1.458333333)
    book.check("醬油：組 SD C", "醬油總氮(變異不等)", sC, 0.1817048889)
    book.check("醬油：傳統 ANOVA F", "醬油總氮(變異不等)", Fv3, 0.436043747)
    book.check("醬油：傳統 ANOVA p", "醬油總氮(變異不等)", p3, 0.7296087661)
    return book
