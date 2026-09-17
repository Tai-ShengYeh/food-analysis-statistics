"""Ch08 合成與擴展不確定度、報告與符合性判定。

R 的答案來源：Rscript R/ch08_combine_report.R（QUAM §8.2.8 例題 1/2、§8.3.4 稱重例、果汁鉛案例）。
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
        "ch08_combine_compliance.xlsx",
        "Ch8 合成不確定度、擴展不確定度 U 與符合性判定",
        "ch08.html",
    )
    book.readme([
        "# 這本活頁簿在做什麼",
        "「Rule1_加減」與「Rule2_乘除」分別示範 QUAM §8.2.8 的兩個例題：加減模型直接用絕對 u 的平方和開根號；"
        "乘除模型改用相對 u（u/x）合成，最後再乘回 y。",
        "「擴展不確定度_t值」示範 U = k·u_c：一般情況 k=2（約 95%），但當合成不確定度被自由度很小的"
        "Type A 項主導時，要改用該項自由度查雙尾 t 值。",
        "「符合性判定」用 IF 函數實作 QUAM Figure 2 的保守決策規則，輸出「符合／不符合／無法判定」，"
        "並附上果汁中鉛的完整小案例。",
        "# 怎麼用",
        "1. 每張表黃色都是可以改的輸入（原始測值與各自的標準不確定度 u）。",
        "2.「符合性判定」的測值、U、限值都是黃色——試著把 (ii)(iii) 兩個灰色地帶案例的 U 改小，"
        "看什麼時候會從「無法判定」變成明確的「符合」或「不符合」。",
        "3.「對照R答案」核對所有關鍵結果。",
        "# 這章最重要的兩個觀念",
        "Rule 1（加減）用絕對 u 的平方和開根號；Rule 2（乘除）一定要先換成相對 u（u/x）合成，"
        "算完再乘回 y——絕對值與相對值不能混用。",
        "符合性判定要用約 95% 的擴展不確定度 U，不是只有約 68% 的 u_c；「結果 ± U 的整段區間」"
        "與限值的相對位置才是判準，不是只看測值本身有沒有超標——這就是「灰色地帶」存在的原因，"
        "ISO/IEC 17025:2017 要求事先與客戶約定決策規則。",
        "# Excel 資料分析工具箱：這裡沒有直接對應的工具",
        "合成不確定度、U=k·uc、符合性判定都是「按固定公式填表」，Analysis ToolPak 沒有對應功能；"
        "本章的主角是 SUMSQ（平方和）與 IF（決策規則），兩者都是一般函數，不需要啟用增益集。",
    ])

    # ---------------- Rule 1：加減模型 ----------------
    ws = book.sheet("Rule1_加減", [34, 16, 44, 54])
    book.header(ws, 1, ["項目", "結果", "公式", "白話說明"])
    p = book.calc(ws, 2, "p", 5.02, "QUAM §8.2.8 例題1：y=p−q+r", fmt="0.00")
    book.mark_input(ws, p)
    q = book.calc(ws, 3, "q", 6.45, "", fmt="0.00")
    book.mark_input(ws, q)
    r = book.calc(ws, 4, "r", 9.04, "", fmt="0.00")
    book.mark_input(ws, r)
    up = book.calc(ws, 5, "u(p)", 0.13, "", fmt="0.00")
    book.mark_input(ws, up)
    uq = book.calc(ws, 6, "u(q)", 0.05, "", fmt="0.00")
    book.mark_input(ws, uq)
    ur = book.calc(ws, 7, "u(r)", 0.22, "", fmt="0.00")
    book.mark_input(ws, ur)
    y1 = book.calc(ws, 8, "y = p − q + r", f"={p}-{q}+{r}", "把三項直接代入模型算 y", key=True)
    uc1 = book.calc(ws, 9, "合成 u_c(y) = √(u(p)²+u(q)²+u(r)²)", f"=SQRT(SUMSQ({up},{uq},{ur}))", "Rule 1：絕對 u 直接平方相加再開根號", key=True)
    U1 = book.calc(ws, 10, "擴展不確定度 U = 2·u_c (k=2)", f"=2*{uc1}", "", key=True)
    book.text(ws, 12, 1, "y = 7.61 ± 0.52（k=2）。注意 u_c=0.26 比三項中最大的 u(r)=0.22 只多一點——"
                          "這正是「平方和開根號」比「直接相加」保守但不會過度誇大的原因。", bold=True)

    # ---------------- Rule 2：乘除模型 ----------------
    ws2 = book.sheet("Rule2_乘除", [34, 16, 44, 54])
    book.header(ws2, 1, ["項目", "結果", "公式", "白話說明"])
    o = book.calc(ws2, 2, "o", 2.46, "QUAM §8.2.8 例題2：y = o·p/(q·r)", fmt="0.00")
    book.mark_input(ws2, o)
    p2 = book.calc(ws2, 3, "p", 4.32, "", fmt="0.00")
    book.mark_input(ws2, p2)
    q2 = book.calc(ws2, 4, "q", 6.38, "", fmt="0.00")
    book.mark_input(ws2, q2)
    r2 = book.calc(ws2, 5, "r", 2.99, "", fmt="0.00")
    book.mark_input(ws2, r2)
    uo = book.calc(ws2, 6, "u(o)", 0.02, "", fmt="0.00")
    book.mark_input(ws2, uo)
    up2 = book.calc(ws2, 7, "u(p)", 0.13, "", fmt="0.00")
    book.mark_input(ws2, up2)
    uq2 = book.calc(ws2, 8, "u(q)", 0.11, "", fmt="0.00")
    book.mark_input(ws2, uq2)
    ur2 = book.calc(ws2, 9, "u(r)", 0.07, "", fmt="0.00")
    book.mark_input(ws2, ur2)
    y2 = book.calc(ws2, 10, "y = o·p/(q·r)", f"={o}*{p2}/({q2}*{r2})", "", key=True)
    relu_o = book.calc(ws2, 11, "相對 u(o)/o", f"={uo}/{o}", "乘除模型要先換成相對不確定度", fmt="0.000000")
    relu_p = book.calc(ws2, 12, "相對 u(p)/p", f"={up2}/{p2}", "", fmt="0.000000")
    relu_q = book.calc(ws2, 13, "相對 u(q)/q", f"={uq2}/{q2}", "", fmt="0.000000")
    relu_r = book.calc(ws2, 14, "相對 u(r)/r", f"={ur2}/{r2}", "", fmt="0.000000")
    rel_uc2 = book.calc(ws2, 15, "相對合成 u_c(y)/y", f"=SQRT(SUMSQ({relu_o},{relu_p},{relu_q},{relu_r}))", "Rule 2：相對 u 平方和開根號", key=True)
    uc2 = book.calc(ws2, 16, "合成 u_c(y) = y × 相對合成", f"={y2}*{rel_uc2}", "算完相對合成，要乘回 y 才是絕對 u_c", key=True)
    U2 = book.calc(ws2, 17, "擴展不確定度 U = 2·u_c (k=2)", f"=2*{uc2}", "", key=True)
    book.text(ws2, 19, 1, "y = 0.557 ± 0.047（k=2）。切記：乘除模型絕對不能直接把 u(o),u(p),u(q),u(r) "
                          "平方相加——一定要先各自除以自己的名義值變成相對 u。", bold=True)

    # ---------------- 擴展不確定度：k=2 vs t 值 ----------------
    ws3 = book.sheet("擴展不確定度_t值", [40, 16, 44, 54])
    book.header(ws3, 1, ["項目", "結果", "公式", "白話說明"])
    u_other = book.calc(ws3, 2, "來源1：其他效應合成 u", 0.01, "QUAM §8.3.4 稱重例", fmt="0.0000")
    book.mark_input(ws3, u_other)
    u_sobs = book.calc(ws3, 3, "來源2：重複性 s_obs（Type A，n=5）", 0.08, "同一樣品稱 5 次的標準差", fmt="0.0000")
    book.mark_input(ws3, u_sobs)
    df = book.calc(ws3, 4, "主導項的自由度 df = n−1", 4, "", fmt="0")
    book.mark_input(ws3, df)
    uc_w = book.calc(ws3, 5, "合成 u_c", f"=SQRT(SUMSQ({u_other},{u_sobs}))", "", key=True)
    k2 = book.calc(ws3, 6, "若直接用 k = 2（假設自由度足夠大）", 2, "一般情況的預設值", fmt="0")
    U_k2 = book.calc(ws3, 7, "U（用 k=2 算，可能低估）", f"={k2}*{uc_w}", "當主導項自由度很小時，k=2 不足以達到約 95% 信賴", key=True)
    k_t = book.calc(ws3, 8, "改查主導項 df 的雙尾 95% t 值", f"=T.INV.2T(0.05,{df})", "df=4 → t=2.776，QUAM 表中取 2.8", key=True)
    U_w = book.calc(ws3, 9, "正確做法：U = k_t × u_c", f"={k_t}*{uc_w}", "", key=True)
    book.text(ws3, 11, 1, "u_c 被自由度只有 4 的 Type A 項主導時，常態近似（k=2≈95%）不可靠；"
                          "改用該項自由度查雙尾 t 值，U 從 0.161 修正為 0.224（QUAM 課本數字取 2.8×0.081≈0.23）。", bold=True)

    # ---------------- 符合性判定 ----------------
    ws4 = book.sheet("符合性判定", [30, 18, 16, 16, 24, 30])
    book.header(ws4, 1, ["項目", "結果", "公式", "白話說明"])
    rep_u = book.calc(ws4, 2, "重複性 u（Type A）", 0.006, "果汁中鉛 (Pb) 完整小案例，各分量標準不確定度 (mg/L)", fmt="0.0000")
    book.mark_input(ws4, rep_u)
    cal_u = book.calc(ws4, 3, "校正曲線 u", 0.004, "", fmt="0.0000")
    book.mark_input(ws4, cal_u)
    blank_u = book.calc(ws4, 4, "空白 u", 0.002, "", fmt="0.0000")
    book.mark_input(ws4, blank_u)
    vol_u = book.calc(ws4, 5, "體積 u", 0.0015, "", fmt="0.0000")
    book.mark_input(ws4, vol_u)
    rec_u = book.calc(ws4, 6, "回收率 u", 0.005, "", fmt="0.0000")
    book.mark_input(ws4, rec_u)
    uc_pb = book.calc(ws4, 7, "合成 u_c(Pb)", f"=SQRT(SUMSQ({rep_u},{cal_u},{blank_u},{vol_u},{rec_u}))", "", key=True)
    pb_result = book.calc(ws4, 8, "Pb 測得結果 (mg/L)", 0.085, "", fmt="0.000")
    book.mark_input(ws4, pb_result)
    U_pb = book.calc(ws4, 9, "擴展不確定度 U_Pb = 2·u_c", f"=2*{uc_pb}", "", key=True)
    limit_pb = book.calc(ws4, 10, "法規限值 (mg/L)", 0.10, "", fmt="0.000")
    book.mark_input(ws4, limit_pb)

    book.header(ws4, 12, ["案例", "測值 result", "擴展不確定度 U", "限值 L", "簡單法則", "保守規則（QUAM Fig.2）"])
    cases = [
        (13, "(i)", 11.5, 1.0, 10.0),
        (14, "(ii)", 10.6, 1.0, 10.0),
        (15, "(iii)", 9.6, 1.0, 10.0),
        (16, "(iv)", 8.8, 1.0, 10.0),
    ]
    for r_, label, result, U_, L_ in cases:
        _cell(ws4, r_, 1, label)
        _cell(ws4, r_, 2, result, fmt="0.0", fill=INPUT_FILL)
        _cell(ws4, r_, 3, U_, fmt="0.0", fill=INPUT_FILL)
        _cell(ws4, r_, 4, L_, fmt="0.0", fill=INPUT_FILL)
        _cell(ws4, r_, 5, f'=IF(B{r_}>D{r_},"不符合","符合")')
        _cell(ws4, r_, 6, f'=IF(B{r_}-C{r_}>D{r_},"不符合",IF(B{r_}+C{r_}<=D{r_},"符合","無法判定"))')

    _cell(ws4, 17, 1, "鉛案例")
    _cell(ws4, 17, 2, f"={pb_result}")
    _cell(ws4, 17, 3, f"={U_pb}")
    _cell(ws4, 17, 4, f"={limit_pb}")
    _cell(ws4, 17, 5, '=IF(B17>D17,"不符合","符合")')
    _cell(ws4, 17, 6, '=IF(B17-C17>D17,"不符合",IF(B17+C17<=D17,"符合","無法判定"))')
    _cell(ws4, 19, 1, "(ii)(iii) 在保守規則下都是「無法判定」，簡單法則卻分別判「不符合」與「符合」——"
                       "結論可能相反，所以決策規則要事先約定。鉛案例：0.085+0.018=0.103>0.10，"
                       "但 0.085−0.018=0.067 遠低於 0.10，落在灰色地帶。", note=True)

    book.check("Rule1 y", "Rule1_加減", y1, 7.61)
    book.check("Rule1 uc", "Rule1_加減", uc1, 0.2603843313)
    book.check("Rule1 U(k=2)", "Rule1_加減", U1, 0.5207686627)
    book.check("Rule2 y", "Rule2_乘除", y2, 0.5570920833)
    book.check("Rule2 相對合成", "Rule2_乘除", rel_uc2, 0.04262651539)
    book.check("Rule2 uc", "Rule2_乘除", uc2, 0.02374689427)
    book.check("Rule2 U(k=2)", "Rule2_乘除", U2, 0.04749378855)
    book.check("稱重例 uc", "擴展不確定度_t值", uc_w, 0.08062257748)
    book.check("df=4 雙尾t值", "擴展不確定度_t值", k_t, 2.776445105)
    book.check("稱重例 U(t值)", "擴展不確定度_t值", U_w, 0.2238441606)
    book.check("鉛 uc", "符合性判定", uc_pb, 0.009124143795)
    book.check("鉛 U", "符合性判定", U_pb, 0.01824828759)
    return book
