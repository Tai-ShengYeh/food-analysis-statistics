"""Ch07 Type A / Type B 分布轉換 + 實戰案例①分析天平稱量。

R 的答案來源：Rscript R/ch07_typeAB_distributions.R 與 R/case_balance.R。
"""
from openpyxl.styles import Font

from excel_common import BOX, FONT, INPUT_FILL, NOTE_FONT, Book, fx


def _cell(ws, r, col, value, fmt=None, fill=None, bold=False, note=False):
    if isinstance(value, str) and value.startswith("="):
        value = fx(value)
    cell = ws.cell(row=r, column=col, value=value)
    cell.font = NOTE_FONT if note else Font(name=FONT, bold=bold)
    cell.border = BOX
    if fmt:
        cell.number_format = fmt
    if fill:
        cell.fill = fill
    return cell


def build():
    book = Book(
        "ch07_typeAB_balance_budget.xlsx",
        "Ch7 Type A/B 分布轉換 ＋ 分析天平稱量不確定度預算",
        "ch07.html",
    )
    book.readme([
        "# 這本活頁簿在做什麼",
        "「TypeA_TypeB對照表」把課本教的六種常見換算（Type A 的 s 與 s/√n；Type B 的矩形÷√3、"
        "三角÷√6、常態÷k）全部排在一張表，重點是「除以哪個數」。",
        "「天平稱量預算」用 QUAM Example A1 的鎘標準液配製案例，把讀值解析度、校正線性、重複性三個來源"
        "合成成 u(m)，再套進 c(Cd)=1000·m·P/V，看質量／純度／體積三者對最終濃度各貢獻多少。",
        "「情境比較_稱量1_10」示範同一台天平、稱樣量從 100 mg 改成 10 mg 時，質量項的貢獻怎麼從次要項"
        "暴增為主導項——這是分析化學裡「稱樣量太小」最經典的地雷。",
        "# 怎麼用",
        "1.「TypeA_TypeB對照表」黃色是各情境的 s 或 ±a，改了會看到對應 u 重算；留意矩形/三角/常態三種"
        "分布的 u 從大到小排列（矩形最保守）。",
        "2.「天平稱量預算」黃色是三個來源的數值（半寬 a 或重複稱重數據），以及最終 m、P、V；"
        "u(m) 算出來後會自動流入下方的濃度貢獻計算。",
        "3.「情境比較_稱量1_10」的 B2（稱樣量）改成別的數字，看質量貢獻怎麼變化。",
        "4.「對照R答案」核對所有關鍵結果。",
        "# 這章最重要的觀念",
        "Type B 不是「一律用矩形分布」：先問「±a 代表什麼」——證書直接給 U 與 k 就直接除以 k；"
        "寫成常態 95% 區間就除以 1.96；只知道界限、界限內同樣可能就除以 √3（矩形，最保守）；"
        "有證據顯示中間值最常見就除以 √6（三角形）。",
        "絕對不確定度不會因為稱樣量變小而變小，但相對不確定度（u/x）會放大——這正是「稱樣量太小」"
        "讓一個原本次要的來源變成主導項的原因。",
        "# Excel 資料分析工具箱：這裡沒有直接對應的工具",
        "不確定度預算表本質是「把每個來源的數字填進固定公式」，Analysis ToolPak 沒有專門的「不確定度合成」"
        "工具；唯一能借用的是「敘述統計」算 Type A 重複量測的標準差（做法見 ch06 說明頁），"
        "其餘 Type B 的換算與最後的平方和合成，都要靠本活頁簿的公式（或 ch08 會用到的 SUMSQ）自己算。",
    ])

    # ---------------- Type A / Type B 轉換表 ----------------
    ws = book.sheet("TypeA_TypeB對照表", [34, 16, 46, 60])
    book.header(ws, 1, ["天平重複稱重 (mg)"])
    rng = book.data(ws, 2, 1, [1001.2, 1000.8, 1001.5, 1001.0, 1000.9], fmt="0.0")

    book.header(ws, 8, ["項目", "結果", "公式", "白話說明"])
    n = book.calc(ws, 9, "n（重複次數）", f"=COUNT({rng})", "", fmt="0")
    u_a = book.calc(ws, 10, "Type A：u(x) = s（單次量測）", f"=STDEV.S({rng})", "直接用重複量測的實驗標準差當標準不確定度", key=True)
    u_a_mean = book.calc(ws, 11, "Type A：若結果是平均，u = s/√n", f"={u_a}/SQRT({n})", "報「5 次平均」才除以 √n；報單次量測不能除", key=True)

    u_cert_num = book.calc(ws, 13, "校正證書 U（擴展不確定度）", 0.20, "校正證書直接給的擴展不確定度", fmt="0.00")
    book.mark_input(ws, u_cert_num)
    k_cert = book.calc(ws, 14, "涵蓋因子 k", 2, "證書上寫的 k", fmt="0")
    book.mark_input(ws, k_cert)
    u_cert = book.calc(ws, 15, "Type B：u = U/k（證書已給 U, k）", f"={u_cert_num}/{k_cert}", "已經是擴展不確定度就直接除以 k，不要再除以 √3", key=True)

    a_rect = book.calc(ws, 17, "矩形分布 ±a（只知道界限）", 0.2, "10 mL 量瓶證書 ±0.2 mL，沒有其他資訊", fmt="0.00")
    book.mark_input(ws, a_rect)
    u_rect = book.calc(ws, 18, "Type B：矩形 u = a/√3", f"={a_rect}/SQRT(3)", "界限內同樣可能出現，最保守", key=True)

    a_tri = book.calc(ws, 19, "三角形分布 ±a（極端值罕見）", 0.2, "同一支量瓶，但內部查核顯示極端值少見", fmt="0.00")
    book.mark_input(ws, a_tri)
    u_tri = book.calc(ws, 20, "Type B：三角形 u = a/√6", f"={a_tri}/SQRT(6)", "中間值最常見，比矩形不保守", key=True)

    a_norm = book.calc(ws, 21, "常態分布 ±a（95% 信賴區間）", 0.2, "天平讀值 ±0.2 mg，證書明確寫 95% 信賴", fmt="0.00")
    book.mark_input(ws, a_norm)
    u_norm = book.calc(ws, 22, "Type B：常態 u = a/1.96", f"={a_norm}/NORM.S.INV(0.975)", "NORM.S.INV(0.975) 就是雙尾 95% 的 1.96", key=True)
    book.text(ws, 24, 1, "同樣的 ±0.2，矩形(0.1155) > 常態95%(0.1020) > 三角形(0.0816)——"
                          "資訊越明確（知道中間值更常見、或直接給了信賴水準），換算出的 u 越小。", bold=True)

    # ---------------- 天平稱量不確定度預算（QUAM Example A1） ----------------
    ws2 = book.sheet("天平稱量預算_100mg", [34, 14, 16, 20, 16, 12, 12, 46])
    book.header(ws2, 1, ["重複稱重 6 次 (mg)"])
    reps_rng = book.data(ws2, 2, 1, [100.03, 100.08, 100.02, 100.09, 100.04, 100.01], fmt="0.00")

    book.header(ws2, 9, ["項目", "結果", "公式", "白話說明"])
    a_read = book.calc(ws2, 10, "讀值解析度半寬 a (mg)", 0.005, "五位天平末位刻度 0.01 mg，半寬 = 0.005 mg", fmt="0.0000")
    book.mark_input(ws2, a_read)
    u_read = book.calc(ws2, 11, "u(讀值解析度) = a/√3", f"={a_read}/SQRT(3)", "數位顯示的捨入屬矩形分布", key=True)
    a_cal = book.calc(ws2, 12, "校正線性半寬 a (mg)", 0.05, "校正證書 ±0.05 mg，極端值罕見", fmt="0.0000")
    book.mark_input(ws2, a_cal)
    u_cal = book.calc(ws2, 13, "u(校正線性) = a/√6", f"={a_cal}/SQRT(6)", "三角形分布：中間值最常見", key=True)
    n_rep = book.calc(ws2, 14, "n（重複稱重次數）", f"=COUNT({reps_rng})", "", fmt="0")
    u_rep = book.calc(ws2, 15, "u(重複性)（Type A，同一物件稱 6 次的 SD）", f"=STDEV.S({reps_rng})", "", key=True)
    u_once = book.calc(ws2, 16, "單次稱重（皮重或毛重）合成 u", f"=SQRT(SUMSQ({u_read},{u_cal},{u_rep}))", "皮重、毛重各稱一次，各自都含這三個來源", key=True)
    u_m = book.calc(ws2, 17, "淨重 u(m)：皮重+毛重兩次稱重合成", f"=SQRT(2)*{u_once}", "淨重 = 毛重 − 皮重，兩次稱重的變異各自獨立要合成", key=True)

    book.header(ws2, 19, ["來源", "數值", "分布", "除數", "標準不確定度 u", "相對 u (u/x)", "u² 占比"])
    _cell(ws2, 20, 1, "質量 m (mg)")
    _cell(ws2, 20, 2, 100.28, fmt="0.0000", fill=INPUT_FILL)
    _cell(ws2, 20, 3, "—（見上方合成）")
    _cell(ws2, 20, 4, "—")
    _cell(ws2, 20, 5, f"={u_m}", fmt="0.000000")
    _cell(ws2, 20, 6, "=E20/B20", fmt="0.000000")
    _cell(ws2, 20, 7, "=F20^2/SUMSQ($F$20:$F$22)", fmt="0.0%")

    _cell(ws2, 21, 1, "純度 P（證書純度分數）")
    _cell(ws2, 21, 2, 0.9999, fmt="0.0000", fill=INPUT_FILL)
    _cell(ws2, 21, 3, "常態（證書）")
    _cell(ws2, 21, 4, "—")
    _cell(ws2, 21, 5, 0.000058, fmt="0.000000", fill=INPUT_FILL)
    _cell(ws2, 21, 6, "=E21/B21", fmt="0.000000")
    _cell(ws2, 21, 7, "=F21^2/SUMSQ($F$20:$F$22)", fmt="0.0%")

    _cell(ws2, 22, 1, "體積 V (mL)")
    _cell(ws2, 22, 2, 100.0, fmt="0.0000", fill=INPUT_FILL)
    _cell(ws2, 22, 3, "常態（含校正+溫度效應）")
    _cell(ws2, 22, 4, "—")
    _cell(ws2, 22, 5, 0.07, fmt="0.000000", fill=INPUT_FILL)
    _cell(ws2, 22, 6, "=E22/B22", fmt="0.000000")
    _cell(ws2, 22, 7, "=F22^2/SUMSQ($F$20:$F$22)", fmt="0.0%")

    book.header(ws2, 24, ["項目", "結果", "公式", "白話說明"])
    c_cd = book.calc(ws2, 25, "c(Cd) = 1000·m·P/V (mg/L)", "=1000*B20*B21/B22", "配製出的標準溶液濃度", key=True)
    rel_uc = book.calc(ws2, 26, "相對合成不確定度 uc(y)/y", "=SQRT(SUMSQ(F20,F21,F22))", "乘除模型：各相對 u 平方和開根號（Rule 2，見 ch08）", key=True)
    uc_abs = book.calc(ws2, 27, "合成標準不確定度 uc (mg/L)", f"={c_cd}*{rel_uc}", "", key=True)
    contrib_m = book.calc(ws2, 28, "質量對濃度的貢獻", f"={c_cd}*F20", "|∂y/∂m|·u(m)，用相對 u 乘回 y", key=True)
    contrib_p = book.calc(ws2, 29, "純度對濃度的貢獻", f"={c_cd}*F21", "", key=True)
    contrib_v = book.calc(ws2, 30, "體積對濃度的貢獻", f"={c_cd}*F22", "", key=True)
    book.text(ws2, 32, 1, "稱 100 mg 時，體積貢獻(0.70) > 質量貢獻(0.55) > 純度貢獻(0.06)——"
                          "先改善量瓶的精密度，天平反而不是瓶頸。", bold=True)

    # ---------------- 情境比較：稱樣量減為 1/10 ----------------
    ws3 = book.sheet("情境比較_稱量1_10", [32, 16, 46, 54])
    book.header(ws3, 1, ["項目", "結果", "公式", "白話說明"])
    m10 = book.calc(ws3, 2, "改稱樣量 (mg)：原本 100 mg，現在只稱 1/10", 10.0, "配製「同樣濃度」的標準液，但只稱 1/10 的量", fmt="0.0")
    book.mark_input(ws3, m10)
    u_m_link = book.calc(ws3, 3, "同一台天平的 u(m)（連結自「天平稱量預算_100mg」）", f"='天平稱量預算_100mg'!{u_m}", "天平的絕對不確定度不會因為稱少而變小")
    c_cd_link = book.calc(ws3, 4, "目標濃度 c(Cd)（連結自上一張表）", "='天平稱量預算_100mg'!B25", "假設配製流程調整後，仍配到同樣的目標濃度")
    contrib_m10 = book.calc(ws3, 5, "稱 1/10 時，質量對濃度的貢獻", f"={c_cd_link}*{u_m_link}/{m10}", "相對不確定度 u(m)/m 放大 10 倍，貢獻也放大約 10 倍", key=True)
    contrib_v_link = book.calc(ws3, 6, "體積貢獻（不變，供對照）", "='天平稱量預算_100mg'!B30", "體積的相對不確定度沒有跟著稱樣量變化")
    ratio = book.calc(ws3, 7, "質量貢獻放大倍數", f"={contrib_m10}/'天平稱量預算_100mg'!B28", "應該接近 10 倍（因為分母 m 直接除以 10）", fmt="0.00")
    book.text(ws3, 9, 1, "稱 100 mg 時質量貢獻(0.55) < 體積貢獻(0.70)；稱 10 mg 時質量貢獻暴增到約 5.48，"
                         "遠超過體積貢獻——原本次要的天平項變成主導項。這就是為什麼配製低濃度標準液時，"
                         "「稱樣量太小」是不確定度預算裡最常見的地雷之一。", bold=True)

    book.check("Type A：u(x)=s", "TypeA_TypeB對照表", u_a, 0.2774887385)
    book.check("Type A：u=s/√n", "TypeA_TypeB對照表", u_a_mean, 0.1240967365)
    book.check("Type B：u=U/k", "TypeA_TypeB對照表", u_cert, 0.1)
    book.check("Type B：矩形 u=a/√3", "TypeA_TypeB對照表", u_rect, 0.1154700538)
    book.check("Type B：三角形 u=a/√6", "TypeA_TypeB對照表", u_tri, 0.08164965809)
    book.check("Type B：常態 u=a/1.96", "TypeA_TypeB對照表", u_norm, 0.1020426914)
    book.check("u(讀值解析度)", "天平稱量預算_100mg", u_read, 0.002886751346)
    book.check("u(校正線性)", "天平稱量預算_100mg", u_cal, 0.02041241452)
    book.check("u(重複性)", "天平稱量預算_100mg", u_rep, 0.03271085447)
    book.check("淨重 u(m)", "天平稱量預算_100mg", u_m, 0.05468089246)
    book.check("c(Cd)", "天平稱量預算_100mg", c_cd, 1002.69972)
    book.check("質量貢獻(100mg)", "天平稱量預算_100mg", contrib_m, 0.5467542437)
    book.check("純度貢獻", "天平稱量預算_100mg", contrib_p, 0.0581624)
    book.check("體積貢獻", "天平稱量預算_100mg", contrib_v, 0.701889804)
    book.check("質量貢獻(稱1/10)", "情境比較_稱量1_10", contrib_m10, 5.482851556)
    return book
