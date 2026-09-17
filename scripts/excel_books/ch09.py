"""Ch09 進階：Kragten 試算表法與 Monte Carlo 模擬。

R 的答案來源：Rscript R/ch09_kragten_montecarlo.R（QUAM Appendix E.2/E.3，鎘標準液案例）。
Kragten 試算表法本來就是為 Excel 設計的，這裡完整實作；Monte Carlo 用 NORM.INV(RAND(),...)
示範表（~1000 列）不登記 book.check()——每次按 F9 都會變。
"""
from openpyxl.styles import Font

from excel_common import BOX, FONT, INPUT_FILL, NOTE_FONT, RESULT_FILL, Book, fx

N_MC = 1000


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
        "ch09_kragten_montecarlo.xlsx",
        "Ch9 進階：Kragten 試算表法與 Monte Carlo 模擬",
        "ch09.html",
    )
    book.readme([
        "# 這本活頁簿在做什麼",
        "案例：配製鎘標準溶液 c(Cd) = 1000·m·P/V（m=質量, P=純度, V=體積），與 ch07 天平案例同一個情境"
        "（QUAM Appendix A1）。同一個問題用三種方法各算一次，比較它們是否互相吻合：",
        "「解析法_Rule2」：偏微分／相對不確定度合成公式（就是 ch08 的 Rule 2）。",
        "「Kragten表」：完全不用微分——每個輸入量各自加上自己的 u 重新算一次 y，"
        "y 的變化量就是那個來源的貢獻，這正是試算表法（Kragten method）的精神，本來就是為 Excel 設計的。",
        "「MonteCarlo示範」：把每個輸入量當成一個分布，用 NORM.INV(RAND(),μ,σ) 隨機抽 1000 組，"
        "直接看 y 的 1000 個模擬結果分布，完全不需要偏微分或除以哪個根號。",
        "# 怎麼用",
        "1.「解析法_Rule2」與「Kragten表」最上面的 m、u(m)、P、u(P)、V、u(V) 都是黃色，改了兩張表都可以"
        "各自重算，比較兩種方法算出的 u_c 是否還是幾乎相同。",
        "2.「Kragten表」的結構：先算「基準」那一列（y0），再看「m+u(m)」「P+u(P)」「V+u(V)」三列各自"
        "只改一個輸入重算出的 y，與 y0 的差就是那個來源的貢獻，平方相加開根號就是合成 u_c。",
        "3.「MonteCarlo示範」每次開檔或按 F9 都會重新抽樣，1000 列的 y_sim 會整批變動——這是正常的，"
        "不是公式錯誤。表格下方的平均、標準差、95% 涵蓋區間也會跟著小幅跳動，但應該落在"
        "「解析法_Rule2」算出的 u_c≈0.86 附近。",
        "4. 這張示範表**不放進**「對照R答案」——因為它本質上每次都不一樣，沒有單一個「正確答案」可以核對。",
        "# 這章最重要的觀念",
        "三種方法算的是同一個不確定度傳播問題：模型線性、輸入不太離散時，解析法、Kragten、Monte Carlo"
        "應該互相吻合（本例三者都在 0.86 mg/L 附近）——這正是最好的自我驗證。Monte Carlo 的真正價值"
        "在模型高度非線性、分布明顯不對稱，或你想直接拿到「涵蓋區間」而不糾結有效自由度的時候；"
        "抽再多次，若輸入分布本身給錯，結果依然是錯的。",
        "# Excel 資料分析工具箱：這裡沒有直接對應的工具",
        "Kragten 法與 Monte Carlo 本來就是試算表原生的做法（複製一欄改一格；NORM.INV(RAND())"
        "灌整欄再用 STDEV.S/PERCENTILE 讀出結果），Analysis ToolPak 沒有專門功能可以取代，"
        "但工具箱的「敘述統計」可以用來讀 MonteCarlo示範表 y_sim 欄的平均與標準差（做法見 ch06 說明頁），"
        "差別是工具箱只會算「當下按下去那一刻」的結果，不會跟著 F9 重新抽樣一起變動。",
    ])

    # ---------------- 解析法（Rule 2） ----------------
    ws1 = book.sheet("解析法_Rule2", [40, 16, 44, 54])
    book.header(ws1, 1, ["項目", "結果", "公式", "白話說明"])
    m = book.calc(ws1, 2, "m：質量 (mg)", 100.28, "QUAM Table A1.1 鎘標準液案例", fmt="0.0000")
    book.mark_input(ws1, m)
    u_m = book.calc(ws1, 3, "u(m)", 0.05, "", fmt="0.0000")
    book.mark_input(ws1, u_m)
    P = book.calc(ws1, 4, "P：純度（分數）", 0.9999, "", fmt="0.0000")
    book.mark_input(ws1, P)
    u_P = book.calc(ws1, 5, "u(P)", 0.000058, "", fmt="0.000000")
    book.mark_input(ws1, u_P)
    V = book.calc(ws1, 6, "V：體積 (mL)", 100.0, "", fmt="0.0000")
    book.mark_input(ws1, V)
    u_V = book.calc(ws1, 7, "u(V)", 0.07, "", fmt="0.0000")
    book.mark_input(ws1, u_V)
    c_cd = book.calc(ws1, 8, "c(Cd) = 1000·m·P/V (mg/L)", f"=1000*{m}*{P}/{V}", "", key=True)
    relu_m = book.calc(ws1, 9, "相對 u(m)/m", f"={u_m}/{m}", "乘除模型先換成相對不確定度", fmt="0.000000")
    relu_P = book.calc(ws1, 10, "相對 u(P)/P", f"={u_P}/{P}", "", fmt="0.000000")
    relu_V = book.calc(ws1, 11, "相對 u(V)/V", f"={u_V}/{V}", "", fmt="0.000000")
    rel_uc = book.calc(ws1, 12, "相對合成 u_c(y)/y", f"=SQRT(SUMSQ({relu_m},{relu_P},{relu_V}))", "", key=True)
    uc_analytic = book.calc(ws1, 13, "合成 u_c（解析法）(mg/L)", f"={c_cd}*{rel_uc}", "", key=True)
    contrib_m = book.calc(ws1, 14, "質量貢獻", f"={c_cd}*{relu_m}", "", key=True)
    contrib_P = book.calc(ws1, 15, "純度貢獻", f"={c_cd}*{relu_P}", "", key=True)
    contrib_V = book.calc(ws1, 16, "體積貢獻", f"={c_cd}*{relu_V}", "", key=True)
    book.text(ws1, 18, 1, "體積貢獻(0.70) > 質量貢獻(0.50) > 純度貢獻(0.06)——與 ch07 天平案例一致。", bold=True)

    # ---------------- Kragten 試算表法 ----------------
    ws2 = book.sheet("Kragten表", [22, 16, 16, 16, 20, 16, 16, 14])
    book.text(ws2, 1, 1, "m (mg)", bold=True)
    _cell(ws2, 1, 2, 100.28, fmt="0.0000", fill=INPUT_FILL)
    book.text(ws2, 2, 1, "u(m)", bold=True)
    _cell(ws2, 2, 2, 0.05, fmt="0.0000", fill=INPUT_FILL)
    book.text(ws2, 3, 1, "P", bold=True)
    _cell(ws2, 3, 2, 0.9999, fmt="0.0000", fill=INPUT_FILL)
    book.text(ws2, 4, 1, "u(P)", bold=True)
    _cell(ws2, 4, 2, 0.000058, fmt="0.000000", fill=INPUT_FILL)
    book.text(ws2, 5, 1, "V (mL)", bold=True)
    _cell(ws2, 5, 2, 100.0, fmt="0.0000", fill=INPUT_FILL)
    book.text(ws2, 6, 1, "u(V)", bold=True)
    _cell(ws2, 6, 2, 0.07, fmt="0.0000", fill=INPUT_FILL)

    book.header(ws2, 8, ["情況", "m", "P", "V", "y=1000·m·P/V", "y − y0", "(y − y0)²", "u² 占比"])
    _cell(ws2, 9, 1, "基準 y0")
    _cell(ws2, 9, 2, "=B1", fmt="0.0000")
    _cell(ws2, 9, 3, "=B3", fmt="0.0000")
    _cell(ws2, 9, 4, "=B5", fmt="0.0000")
    _cell(ws2, 9, 5, "=1000*B9*C9/D9", fmt="0.0000")
    _cell(ws2, 9, 6, "—")
    _cell(ws2, 9, 7, "—")
    _cell(ws2, 9, 8, "—")

    _cell(ws2, 10, 1, "m + u(m)")
    _cell(ws2, 10, 2, "=B1+B2", fmt="0.0000")
    _cell(ws2, 10, 3, "=B3", fmt="0.0000")
    _cell(ws2, 10, 4, "=B5", fmt="0.0000")
    _cell(ws2, 10, 5, "=1000*B10*C10/D10", fmt="0.0000")
    _cell(ws2, 10, 6, "=E10-E9", fmt="0.0000")
    _cell(ws2, 10, 7, "=F10^2", fmt="0.0000")
    _cell(ws2, 10, 8, "=G10/$G$14", fmt="0.0%")

    _cell(ws2, 11, 1, "P + u(P)")
    _cell(ws2, 11, 2, "=B1", fmt="0.0000")
    _cell(ws2, 11, 3, "=B3+B4", fmt="0.0000")
    _cell(ws2, 11, 4, "=B5", fmt="0.0000")
    _cell(ws2, 11, 5, "=1000*B11*C11/D11", fmt="0.0000")
    _cell(ws2, 11, 6, "=E11-E9", fmt="0.0000")
    _cell(ws2, 11, 7, "=F11^2", fmt="0.0000")
    _cell(ws2, 11, 8, "=G11/$G$14", fmt="0.0%")

    _cell(ws2, 12, 1, "V + u(V)")
    _cell(ws2, 12, 2, "=B1", fmt="0.0000")
    _cell(ws2, 12, 3, "=B3", fmt="0.0000")
    _cell(ws2, 12, 4, "=B5+B6", fmt="0.0000")
    _cell(ws2, 12, 5, "=1000*B12*C12/D12", fmt="0.0000")
    _cell(ws2, 12, 6, "=E12-E9", fmt="0.0000")
    _cell(ws2, 12, 7, "=F12^2", fmt="0.0000")
    _cell(ws2, 12, 8, "=G12/$G$14", fmt="0.0%")

    _cell(ws2, 14, 1, "合成 Σ(y−y0)²", bold=True)
    _cell(ws2, 14, 7, "=SUM(G10:G12)", fmt="0.0000", bold=True)
    _cell(ws2, 15, 1, "合成標準不確定度 u_c = √Σ(y−y0)²", bold=True)
    _cell(ws2, 15, 5, "=SQRT(G14)", fmt="0.0000", bold=True, fill=RESULT_FILL)
    _cell(ws2, 17, 1, "每一欄只改一個輸入（加上它自己的 u）重新算 y，y 與基準的差就是那個來源的貢獻——"
                       "這正是「Kragten 試算表法」的全部內容：不需要偏微分，只需要複製欄、改一格、重算。", note=True)

    # ---------------- Monte Carlo 示範（不登記 check） ----------------
    ws3 = book.sheet("MonteCarlo示範", [18, 18, 18, 24])
    book.text(ws3, 1, 1, "m (mg)", bold=True)
    _cell(ws3, 1, 2, 100.28, fmt="0.0000", fill=INPUT_FILL)
    book.text(ws3, 2, 1, "u(m)", bold=True)
    _cell(ws3, 2, 2, 0.05, fmt="0.0000", fill=INPUT_FILL)
    book.text(ws3, 3, 1, "P", bold=True)
    _cell(ws3, 3, 2, 0.9999, fmt="0.0000", fill=INPUT_FILL)
    book.text(ws3, 4, 1, "u(P)", bold=True)
    _cell(ws3, 4, 2, 0.000058, fmt="0.000000", fill=INPUT_FILL)
    book.text(ws3, 5, 1, "V (mL)", bold=True)
    _cell(ws3, 5, 2, 100.0, fmt="0.0000", fill=INPUT_FILL)
    book.text(ws3, 6, 1, "u(V)", bold=True)
    _cell(ws3, 6, 2, 0.07, fmt="0.0000", fill=INPUT_FILL)

    header_row = 8
    book.header(ws3, header_row, ["m_sim", "P_sim", "V_sim", "y_sim = 1000·m_sim·P_sim/V_sim (mg/L)"])
    first = header_row + 1
    last = first + N_MC - 1
    for i in range(N_MC):
        r_ = first + i
        _cell(ws3, r_, 1, "=NORM.INV(RAND(),$B$1,$B$2)", fmt="0.0000")
        _cell(ws3, r_, 2, "=NORM.INV(RAND(),$B$3,$B$4)", fmt="0.0000")
        _cell(ws3, r_, 3, "=NORM.INV(RAND(),$B$5,$B$6)", fmt="0.0000")
        _cell(ws3, r_, 4, f"=1000*A{r_}*B{r_}/C{r_}", fmt="0.0000")

    sum_row = last + 2
    _cell(ws3, sum_row, 1, "N（模擬次數）", bold=True)
    _cell(ws3, sum_row, 4, f"=COUNT(D{first}:D{last})", fmt="0")
    _cell(ws3, sum_row + 1, 1, "平均 mean(y_sim)", bold=True)
    _cell(ws3, sum_row + 1, 4, f"=AVERAGE(D{first}:D{last})", fmt="0.0000")
    _cell(ws3, sum_row + 2, 1, "標準差 STDEV.S(y_sim) ≈ u_c", bold=True)
    _cell(ws3, sum_row + 2, 4, f"=STDEV.S(D{first}:D{last})", fmt="0.0000")
    _cell(ws3, sum_row + 3, 1, "95% 涵蓋區間下限 (2.5% 分位數)", bold=True)
    _cell(ws3, sum_row + 3, 4, f"=PERCENTILE.INC(D{first}:D{last},0.025)", fmt="0.0000")
    _cell(ws3, sum_row + 4, 1, "95% 涵蓋區間上限 (97.5% 分位數)", bold=True)
    _cell(ws3, sum_row + 4, 4, f"=PERCENTILE.INC(D{first}:D{last},0.975)", fmt="0.0000")
    _cell(ws3, sum_row + 6, 1,
          "這張表每次開檔、每次按 F9 都會重新抽樣，1000 列的數字與上面的平均/標準差/涵蓋區間都會小幅跳動——"
          "這是 RAND() 的正常行為，不是公式錯誤，也不會與 R 的數字完全相同。"
          "但只要模擬次數夠多，標準差應該穩定落在「解析法_Rule2」算出的 u_c ≈ 0.86 mg/L 附近，"
          "95% 涵蓋區間半寬也應該接近 k=2 的 U。", note=True)

    book.check("c(Cd)", "解析法_Rule2", c_cd, 1002.69972)
    book.check("解析法 uc", "解析法_Rule2", uc_analytic, 0.8637025902)
    book.check("質量貢獻", "解析法_Rule2", contrib_m, 0.49995)
    book.check("純度貢獻", "解析法_Rule2", contrib_P, 0.0581624)
    book.check("體積貢獻", "解析法_Rule2", contrib_V, 0.701889804)
    book.check("Kragten y0", "Kragten表", "E9", 1002.69972)
    book.check("Kragten y(m+u)", "Kragten表", "E10", 1003.19967)
    book.check("Kragten y(P+u)", "Kragten表", "E11", 1002.757882)
    book.check("Kragten y(V+u)", "Kragten表", "E12", 1001.998321)
    book.check("Kragten uc", "Kragten表", "E15", 0.8633036423)
    return book
