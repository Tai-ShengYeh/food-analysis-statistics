"""Ch10 實戰案例：滴定與 HPLC 的量測不確定度。

R 的答案來源：Rscript R/case_titration.R（NaOH 標定，QUAM Example A2）
           與 Rscript R/case_hplc.R（HPLC/GC 農藥殘留，QUAM Example A4）。
兩個案例都是「乘除模型 -> 相對不確定度合成」，用同一本活頁簿的兩張計算表呈現。
"""
from openpyxl.styles import Font, Alignment

from excel_common import Book, fx, BOX, FONT, NOTE_FONT, HEAD_FILL, INPUT_FILL

BUDGET_HEADERS = ["來源", "數值 x", "分布", "除數", "標準不確定度 u", "相對 u(x)/x", "u²占比 (%)"]


def budget_header(ws, row):
    for i, text in enumerate(BUDGET_HEADERS):
        c = ws.cell(row=row, column=1 + i, value=text)
        c.font = Font(name=FONT, bold=True, color="FFFFFF")
        c.fill = HEAD_FILL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BOX


def budget_cell(ws, row, col, value, fmt=None, bold=False, fill=None):
    c = ws.cell(row=row, column=col, value=fx(value) if isinstance(value, str) else value)
    c.font = Font(name=FONT, bold=bold)
    c.border = BOX
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    return c


def build():
    book = Book("ch10_titration_hplc.xlsx",
                 "Ch10 實戰案例：滴定標定與 HPLC 農藥殘留的量測不確定度預算",
                 "ch10.html")
    book.readme([
        "# 這本活頁簿在做什麼",
        "重現教科書兩個國際範例：①用 KHP 標定 NaOH 濃度（QUAM Example A2）；②HPLC/GC 測麵包中農藥殘留（QUAM Example A4）。",
        "兩者都是「乘除模型」——所以不確定度合成一律用「相對不確定度」（u(x)/x，沒有單位），公式是：相對合成 = SQRT(SUMSQ(各項相對u))。",
        "「滴定NaOH標定」工作表：先算出濃度，再一項一項列出不確定度預算，看誰是老大（V_T 占 52%）。",
        "「HPLC農藥殘留」工作表：內部驗證法的三大成分（精密度／回收率偏倚／均勻性），加上符合性判定。",
        "# 怎麼用",
        "1. 黃色是可以改的數據；改了以後，右邊所有公式（包含 u²占比）都會自動重算。",
        "2. 試著把 V_T 從 18.64 改成 49（滴定管接近滿管程），看 u_c 怎麼變小——這就是「改善策略」那一段在算的事。",
        "3. HPLC 工作表把 MRL（法規限量）改一改，看「符合／不符合／灰色地帶」怎麼變。",
        "4.「對照R答案」工作表核對 Excel 與 R 是否一致。",
        "# 兩個最重要的觀念",
        "① u²占比（不確定度預算）是用「變異數」（u 的平方）算占比，不是把 u 直接相除——這是本章測驗最愛考的地方。",
        "② 乘除模型合成用「相對」不確定度；加減模型合成才用「絕對」不確定度——兩者不能混用。",
        "# 本章沒有對應的資料分析工具箱功能",
        "不確定度預算是逐項代公式，屬於「量測不確定度評估」而不是統計檢定或迴歸，Excel 的資料分析工具箱（t 檢定/F 檢定/ANOVA/迴歸）用不上；本活頁簿全部用一般函數（SQRT、SUMSQ、IF）現場計算。",
    ])

    # =================================================================
    # 工作表 1：滴定 NaOH 標定
    # =================================================================
    ws = book.sheet("滴定NaOH標定", [30, 16, 14, 12, 16, 14, 12, 46])
    book.text(ws, 1, 1, "Step 1：量測模型的各輸入量（黃色可改）", bold=True, size=12, color="0F4C81")
    book.header(ws, 2, ["項目", "數值", "公式", "說明"])
    m = book.calc(ws, 3, "m(KHP)：KHP 質量 (g)", 0.3888, "稱取的 KHP 淨重", fmt="0.0000")
    book.mark_input(ws, m)
    P = book.calc(ws, 4, "P(KHP)：純度", 1.0, "證書純度（小數）", fmt="0.0000")
    book.mark_input(ws, P)
    M = book.calc(ws, 5, "M(KHP)：莫耳質量 (g/mol)", 204.2212, "由 IUPAC 原子量計算", fmt="0.0000")
    book.mark_input(ws, M)
    V = book.calc(ws, 6, "V_T：滴定體積 (mL)", 18.64, "自動滴定儀 pH 電極判定終點", fmt="0.0000")
    book.mark_input(ws, V)
    c_naoh = book.calc(ws, 7, "c(NaOH)：標定濃度 (mol/L)", f"=1000*{m}*{P}/({M}*{V})",
                        "量測模型：1000×m×P/(M×V_T)", fmt="0.00000", key=True)

    book.text(ws, 9, 1, "u(V_T) 的解剖：滴定體積的三個不確定度來源", bold=True, size=12, color="0F4C81")
    book.header(ws, 10, ["項目", "數值", "公式", "說明"])
    a_cal = book.calc(ws, 11, "① 滴定管校正 半寬 a (mL)", 0.01, "A 級滴定管證書 ±0.01 mL", fmt="0.0000")
    book.mark_input(ws, a_cal)
    u_cal = book.calc(ws, 12, "u(校正)：三角形分布 (mL)", f"={a_cal}/SQRT(6)", "三角形分布除數 √6", fmt="0.0000")
    coef = book.calc(ws, 13, "② 水的體積膨脹係數 (/℃)", 0.00021, "查表常數", fmt="0.00000")
    book.mark_input(ws, coef)
    dT = book.calc(ws, 14, "溫度變動 ±ΔT (℃)", 4, "實驗室溫度變動範圍", fmt="0")
    book.mark_input(ws, dT)
    a_temp = book.calc(ws, 15, "溫度效應 半寬 a (mL)", f"={V}*{coef}*{dT}", "V_T × 膨脹係數 × ΔT", fmt="0.0000")
    u_temp = book.calc(ws, 16, "u(溫度)：矩形分布 (mL)", f"={a_temp}/SQRT(3)", "矩形分布除數 √3", fmt="0.0000")
    a_ep = book.calc(ws, 17, "③ 終點判讀 半寬 a (mL)", 0.003, "pH 曲線轉折與理論當量點的偏差", fmt="0.0000")
    book.mark_input(ws, a_ep)
    u_ep = book.calc(ws, 18, "u(終點)：矩形分布 (mL)", f"={a_ep}/SQRT(3)", "矩形分布除數 √3", fmt="0.0000")
    u_vt_calc = book.calc(ws, 19, "u(V_T) 三項合成 (mL)", f"=SQRT(SUMSQ({u_cal},{u_temp},{u_ep}))",
                           "SQRT(SUMSQ(校正,溫度,終點)) ≈ 0.0101，QUAM 保守取 0.013（見下方採用值）", fmt="0.0000")
    u_vt = book.calc(ws, 20, "u(V_T)：採用值 (mL)", 0.013, "QUAM 原文較保守的取值，下方主預算表採用這一個", fmt="0.0000")
    book.mark_input(ws, u_vt)

    book.text(ws, 22, 1, "Step 3/4：不確定度預算表（乘除模型，用相對不確定度）", bold=True, size=12, color="0F4C81")
    budget_header(ws, 23)
    u_rep = book.calc(ws, 24, "u_rep：重複性 相對標準不確定度", 0.0005,
                       "過往滴定的重複變異（合併所有操作），先佔一列避免與下面預算表衝突", fmt="0.00000")
    book.mark_input(ws, u_rep)
    u_m = book.calc(ws, 25, "u(m)：質量標準不確定度 (g)", 0.00013, "第7章天平案例：解析度+校正+重複", fmt="0.00000")
    book.mark_input(ws, u_m)
    a_P = book.calc(ws, 26, "a(P)：純度半寬（矩形）", 0.0005, "證書 ±0.0005", fmt="0.00000")
    book.mark_input(ws, a_P)
    u_P_calc = book.calc(ws, 27, "u(P) 計算值：矩形分布", f"={a_P}/SQRT(3)",
                          "u(P) = a/√3 ≈ 0.0002887；下方主預算表採用教材/QUAM 取值 0.00029", fmt="0.0000000")
    u_M = book.calc(ws, 28, "u(M)：莫耳質量標準不確定度 (g/mol)", 0.0038, "IUPAC 原子量不確定度表", fmt="0.0000")
    book.mark_input(ws, u_M)

    r = 29
    budget_cell(ws, r, 1, "重複性 rep")
    budget_cell(ws, r, 2, 1.0, fmt="0.0000")
    budget_cell(ws, r, 3, "直接給定（歷史滴定重複變異）")
    budget_cell(ws, r, 4, "—")
    urep_c = budget_cell(ws, r, 5, f"={u_rep}", fmt="0.000000")
    relrep = budget_cell(ws, r, 6, f"={u_rep}/1", fmt="0.000000")
    pct_rep = budget_cell(ws, r, 7, None, fmt="0.0")

    r = 30
    budget_cell(ws, r, 1, "質量 m(KHP)")
    budget_cell(ws, r, 2, f"={m}", fmt="0.0000")
    budget_cell(ws, r, 3, "合成（天平：解析度+校正+重複）")
    budget_cell(ws, r, 4, "—")
    um_c = budget_cell(ws, r, 5, f"={u_m}", fmt="0.000000")
    relm = budget_cell(ws, r, 6, f"={u_m}/{m}", fmt="0.000000")
    pct_m = budget_cell(ws, r, 7, None, fmt="0.0")

    r = 31
    budget_cell(ws, r, 1, "純度 P(KHP)")
    budget_cell(ws, r, 2, f"={P}", fmt="0.0000")
    budget_cell(ws, r, 3, "矩形 ±0.0005（=0.0005/√3≈0.0002887，教材採用 0.00029）")
    budget_cell(ws, r, 4, "√3")
    uP_c = budget_cell(ws, r, 5, 0.00029, fmt="0.000000", fill=INPUT_FILL)
    relP = budget_cell(ws, r, 6, f"={uP_c.coordinate}/{P}", fmt="0.000000")
    pct_P = budget_cell(ws, r, 7, None, fmt="0.0")

    r = 32
    budget_cell(ws, r, 1, "莫耳質量 M(KHP)")
    budget_cell(ws, r, 2, f"={M}", fmt="0.0000")
    budget_cell(ws, r, 3, "常態（IUPAC 給定為 u）")
    budget_cell(ws, r, 4, "1")
    uM_c = budget_cell(ws, r, 5, f"={u_M}", fmt="0.000000")
    relM = budget_cell(ws, r, 6, f"={u_M}/{M}", fmt="0.000000")
    pct_M = budget_cell(ws, r, 7, None, fmt="0.0")

    r = 33
    budget_cell(ws, r, 1, "滴定體積 V_T")
    budget_cell(ws, r, 2, f"={V}", fmt="0.0000")
    budget_cell(ws, r, 3, "合成（校正+溫度+終點，見上表）")
    budget_cell(ws, r, 4, "1")
    uV_c = budget_cell(ws, r, 5, f"={u_vt}", fmt="0.000000")
    relV = budget_cell(ws, r, 6, f"={u_vt}/{V}", fmt="0.000000")
    pct_V = budget_cell(ws, r, 7, None, fmt="0.0")

    rel_uc = book.calc(ws, 35, "相對合成不確定度 u_c(c)/c",
                        f"=SQRT(SUMSQ({relrep.coordinate},{relm.coordinate},{relP.coordinate},{relM.coordinate},{relV.coordinate}))",
                        "SQRT(SUMSQ(五項相對 u))——先平方、加總、再開根號", fmt="0.000000", key=True)
    uc = book.calc(ws, 36, "u_c(c)：合成標準不確定度 (mol/L)", f"={c_naoh}*{rel_uc}", "c(NaOH) × 相對合成", fmt="0.000000", key=True)
    U = book.calc(ws, 37, "U：擴展不確定度 (k=2)", f"=2*{uc}", "k=2，約 95%", fmt="0.000000", key=True)
    book.text(ws, 38, 1, "報告：c(NaOH) = (0.10214 ± 0.00020) mol/L（k=2）", bold=True)

    # 補上 u²占比（放在合成算出來之後，Excel 不在意公式先後順序）
    for cell, relcell in [(pct_rep, relrep), (pct_m, relm), (pct_P, relP), (pct_M, relM), (pct_V, relV)]:
        cell.value = fx(f"={relcell.coordinate}^2/{rel_uc}^2*100")

    book.text(ws, 40, 1, "改善策略：讓滴定體積接近 50 mL 滿管程（多稱 KHP）", bold=True, size=12, color="0F4C81")
    book.header(ws, 41, ["項目", "數值", "公式", "說明"])
    V2 = book.calc(ws, 42, "V_T 改善後 (mL)", 49, "多稱約 2.6 倍 KHP，滴定體積接近滿管程", fmt="0.00")
    book.mark_input(ws, V2)
    m_scale = book.calc(ws, 43, "m(KHP) 放大倍數", 2.6, "配合 V_T 加大，同比例多稱 KHP", fmt="0.00")
    book.mark_input(ws, m_scale)
    relV2 = book.calc(ws, 44, "V_T 改善後的相對 u", f"={u_vt}/{V2}", "u(V_T) 不變，只是 V_T 變大", fmt="0.000000")
    relm2 = book.calc(ws, 45, "m 改善後的相對 u", f"={u_m}/({m}*{m_scale})", "u(m) 不變，質量變大", fmt="0.000000")
    rel_uc2 = book.calc(ws, 46, "改善後相對合成", f"=SQRT(SUMSQ({relrep.coordinate},{relm2},{relP.coordinate},{relM.coordinate},{relV2}))",
                         "同樣的 SQRT(SUMSQ())，只是 m、V 兩項變小", fmt="0.000000", key=True)
    uc2 = book.calc(ws, 47, "改善後 u_c (mol/L)", f"={c_naoh}*{rel_uc2}", "從 0.000099 降到約 0.000066（改善約 34%）", fmt="0.000000", key=True)

    # =================================================================
    # 工作表 2：HPLC 農藥殘留（內部驗證法）
    # =================================================================
    ws2 = book.sheet("HPLC農藥殘留", [30, 16, 14, 12, 16, 14, 12, 46])
    book.text(ws2, 1, 1, "Step 3：內部驗證法的三大成分（QUAM Table A4.4）", bold=True, size=12, color="0F4C81")
    budget_header(ws2, 2)
    r = 3
    budget_cell(ws2, r, 1, "精密度 Precision")
    prec_v = budget_cell(ws2, r, 2, 1.0, fmt="0.00")
    budget_cell(ws2, r, 3, "直接給定（不同類型樣品雙重複分析的中間精密度）")
    budget_cell(ws2, r, 4, "—")
    u_prec = budget_cell(ws2, r, 5, 0.27, fmt="0.0000", fill=INPUT_FILL)
    rel_prec = budget_cell(ws2, r, 6, f"={u_prec.coordinate}/{prec_v.coordinate}", fmt="0.0000")
    pct_prec = budget_cell(ws2, r, 7, None, fmt="0.0")

    r = 4
    budget_cell(ws2, r, 1, "偏倚 Bias（回收率）")
    rec_v = budget_cell(ws2, r, 2, 0.9, fmt="0.00")
    rec_v.fill = INPUT_FILL
    budget_cell(ws2, r, 3, "加標回收實驗：平均回收 90%，其 SD 與顯著性檢定")
    budget_cell(ws2, r, 4, "—")
    a_bias = budget_cell(ws2, r, 5, 0.043, fmt="0.0000")
    a_bias.fill = INPUT_FILL
    rel_bias = budget_cell(ws2, r, 6, f"={a_bias.coordinate}/{rec_v.coordinate}", fmt="0.0000")
    pct_bias = budget_cell(ws2, r, 7, None, fmt="0.0")

    r = 5
    budget_cell(ws2, r, 1, "均勻性 Homogeneity")
    homog_v = budget_cell(ws2, r, 2, 1.0, fmt="0.00")
    budget_cell(ws2, r, 3, "模型估計最壞情境（農藥可能只在麵包表面）")
    budget_cell(ws2, r, 4, "—")
    u_homog = budget_cell(ws2, r, 5, 0.20, fmt="0.0000")
    u_homog.fill = INPUT_FILL
    rel_homog = budget_cell(ws2, r, 6, f"={u_homog.coordinate}/{homog_v.coordinate}", fmt="0.0000")
    pct_homog = budget_cell(ws2, r, 7, None, fmt="0.0")

    book.header(ws2, 7, ["項目", "結果", "公式", "說明"])
    rel_uc_h = book.calc(ws2, 8, "相對合成不確定度",
                          f"=SQRT(SUMSQ({rel_prec.coordinate},{rel_bias.coordinate},{rel_homog.coordinate}))",
                          "三大成分平方和開根號", fmt="0.0000", key=True)
    for cell, relc in [(pct_prec, rel_prec), (pct_bias, rel_bias), (pct_homog, rel_homog)]:
        cell.value = fx(f"={relc.coordinate}^2/{rel_uc_h}^2*100")

    P_raw = book.calc(ws2, 10, "P_raw：儀器測得未修正結果 (mg/kg)", 1.00, "層析儀讀值", fmt="0.0000")
    book.mark_input(ws2, P_raw)
    Rec = book.calc(ws2, 11, "Rec：回收率", 0.9, "同上表回收率", fmt="0.0000")
    book.mark_input(ws2, Rec)
    P_op = book.calc(ws2, 12, "P_op：回收率修正後結果 (mg/kg)", f"={P_raw}/{Rec}", "除以回收率修正偏倚", fmt="0.0000", key=True)
    uc_op = book.calc(ws2, 13, "u_c(P_op) (mg/kg)", f"={P_op}*{rel_uc_h}", "P_op × 相對合成", fmt="0.0000", key=True)
    U_op = book.calc(ws2, 14, "U：擴展不確定度 (k=2, mg/kg)", f"=2*{uc_op}", "k=2，約 95%", fmt="0.0000", key=True)
    book.text(ws2, 15, 1, "報告：P_op = (1.11 ± 0.75) mg/kg（k=2）——與 QUAM Table A4.5 一致", bold=True)

    book.text(ws2, 17, 1, "進階：用雙重複對數據自己算精密度項（估短期重複性 RSD）", bold=True, size=12, color="0F4C81")
    book.header(ws2, 18, ["樣品 a", "樣品 b", "相對差 d=(a-b)/((a+b)/2)", "d²"])
    a_vals = [0.42, 1.13, 0.27, 0.88, 0.55, 1.62, 0.31, 0.74]
    b_vals = [0.39, 0.97, 0.30, 0.71, 0.60, 1.28, 0.35, 0.80]
    a_rng = book.data(ws2, 19, 1, a_vals, fmt="0.00")
    b_rng = book.data(ws2, 19, 2, b_vals, fmt="0.00")
    for i in range(8):
        row = 19 + i
        d = ws2.cell(row=row, column=3, value=fx(f"=(A{row}-B{row})/((A{row}+B{row})/2)"))
        d.number_format = "0.0000"
        d.border = BOX
        d2 = ws2.cell(row=row, column=4, value=fx(f"=C{row}^2"))
        d2.number_format = "0.000000"
        d2.border = BOX
    sum_d2 = book.calc(ws2, 27, "Σd²", "=SUM(D19:D26)", "8 對雙重複的相對差平方和", fmt="0.000000")
    n_dup = book.calc(ws2, 28, "對數 n", "=COUNT(A19:A26)", "共 8 對", fmt="0")
    rsd_dup = book.calc(ws2, 29, "RSD（短期重複性）", f"=SQRT({sum_d2}/(2*{n_dup}))",
                         "SQRT(Σd²/(2n))——只反映短期變異，比長期中間精密度 0.27 小得多", fmt="0.0000", key=True)

    book.text(ws2, 31, 1, "符合性判定（保守決策規則）", bold=True, size=12, color="0F4C81")
    book.header(ws2, 32, ["項目", "結果", "公式", "說明"])
    MRL = book.calc(ws2, 33, "MRL：法規限量 (mg/kg)", 2.0, "可改成 1.5 看灰色地帶", fmt="0.00")
    book.mark_input(ws2, MRL)
    lo = book.calc(ws2, 34, "下限 = P_op − U", f"={P_op}-{U_op}", "", fmt="0.0000")
    hi = book.calc(ws2, 35, "上限 = P_op + U", f"={P_op}+{U_op}", "", fmt="0.0000")
    verdict = book.calc(ws2, 36, "判定",
                         f'=IF({lo}>{MRL},"不符合",IF({hi}<={MRL},"符合","灰色地帶"))',
                         "下限超過限量才判不符合；上限沒超過才判符合；其餘是灰色地帶", fmt="@", key=True)

    book.check("c(NaOH) 標定濃度", "滴定NaOH標定", c_naoh, 0.1021361597)
    book.check("滴定相對合成不確定度", "滴定NaOH標定", rel_uc, 0.0009657358605)
    book.check("滴定 u_c", "滴定NaOH標定", uc, 9.863655208e-05)
    book.check("滴定 U (k=2)", "滴定NaOH標定", U, 0.0001972731042)
    book.check("V_T 三項合成 u(V_T)", "滴定NaOH標定", u_vt_calc, 0.01006910188)
    book.check("V_T 對變異數占比 (%)", "滴定NaOH標定", pct_V.coordinate, 52.15286509)
    book.check("改善後相對合成", "滴定NaOH標定", rel_uc2, 0.0006491315283)
    book.check("HPLC 相對合成不確定度", "HPLC農藥殘留", rel_uc_h, 0.3393857924)
    book.check("HPLC P_op", "HPLC農藥殘留", P_op, 1.111111111)
    book.check("HPLC u_c(P_op)", "HPLC農藥殘留", uc_op, 0.3770953248)
    book.check("HPLC U (k=2)", "HPLC農藥殘留", U_op, 0.7541906497)
    book.check("雙重複 RSD", "HPLC農藥殘留", rsd_dup, 0.1027196196)
    return book
