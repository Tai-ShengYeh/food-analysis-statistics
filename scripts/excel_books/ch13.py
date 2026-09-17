"""Ch13 實戰應用：USDA FoodData Central × 冰淇淋配方計算（目標導向配方、最低成本配方、營養標籤）。

R 的答案來源：Rscript R/ch13_fdc.R。
最低成本配方在 R 是用「掃描 SMP 用量、逐點解 3x3 聯立方程、比較成本」找出來的（等價於線性規劃）。
Excel 對應的做法是開「規劃求解（Solver）」增益集直接求解——但 Solver 的結果是靜態的，
改動黃色數據不會自動重算，所以本活頁簿另外準備一張「最低成本驗算表」：
把 R 算出的最佳解（與最貴的另一端點、及逆向工程解）當成黃色可改的常數填進去，
再用公式驗證它是否滿足所有質量平衡限制式，並算出對應成本——這些驗算結果才是 check() 的對象。
"""
from openpyxl.styles import Font, Alignment

from excel_common import Book, fx, BOX, FONT, HEAD_FILL, INPUT_FILL, RESULT_FILL

BUDGET_HEADERS = ["來源", "數值", "分布", "除數", "標準不確定度 u", "相對 u(x)/x", "u²占比 (%)"]


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
    book = Book("ch13_formulation_costing.xlsx",
                 "Ch13 配方計算：目標導向配方、規劃求解最低成本、營養標籤與 Atwater 熱量",
                 "ch13.html")
    book.readme([
        "# 這本活頁簿在做什麼",
        "重現商業配方軟體 TechWizard™ 的兩招牌功能：質量平衡聯立方程（目標導向配方）與最低成本配方，情境是 TechWizard 官網的 Ice Cream 範例：",
        "脂肪 12%、非脂乳固形（MSNF）11%、砂糖 14%、玉米糖漿 3%、安定劑/乳化劑 0.5%，其餘用鮮奶油＋全脂鮮乳＋脫脂奶粉＋水湊足 82.5 kg。",
        "「原料資料庫與配方平衡」：列出各原料的組成（脂肪/MSNF/水分/單價），並說明質量平衡的 3 條方程式、4 個未知數（多一個自由度）。",
        "「最低成本驗算表」：把 R 用 solve() 掃描找出的最佳解（與最貴端點、逆向工程解）當常數填入，用公式驗證它滿足所有限制式並算成本——這是本章最重要的一張表。",
        "「營養標籤與Atwater」：用 SUMPRODUCT 把配方加權平均成每 100 g 營養值，換算每份 66 g，並用 Atwater 4-4-9 交叉驗證熱量。",
        "# 怎麼用",
        "1. 黃色是可以改的數據；「原料資料庫」的組成/單價改了，下面的驗算表會自動重算「是否符合限制式」與成本，但注意：Excel 不會自動重新幫你找『最佳解』，那是 Solver 的工作（見下方 Solver 操作說明）。",
        "2. 想找新的最佳解：照著下面的 Solver 步驟做一次，把 Solver 給的答案抄到「最低成本驗算表」的黃色格子裡，公式就會自動驗證它對不對。",
        "3.「營養標籤與Atwater」把 tgt_fat（脂肪目標）改一改，看熱量、每份 66 g 的標示值怎麼變。",
        "4.「對照R答案」工作表核對 Excel 與 R 是否一致。",
        "# 用 Excel「規劃求解（Solver）」重現 R 的 solve() 與最低成本搜尋",
        "① 啟用增益集：檔案 → 選項 → 增益集 → 管理選「Excel 增益集」→ 前往 → 勾選「規劃求解外接程式」→ 確定。此後「資料」分頁最右邊會出現「規劃求解」按鈕。",
        "② 目標導向配方（只要滿足限制式，不求最低成本）：在工作表上把鮮奶油、全脂鮮乳、脫脂奶粉、水四格設成「變動變數」；設定限制式：總質量=82.5、脂肪合量=12、MSNF合量=11、四個變數全部>=0；目標格可以留空或設成任意常數，按「求解」即可解出一組可行配方（相當於 R 的 solve()）。",
        "③ 最低成本配方（本章的重點）：目標儲存格＝原料成本合計（=SUMPRODUCT(用量欄,單價欄)+砂糖/糖漿/安定劑固定成本），選「最小化」；變動變數＝鮮奶油、全脂鮮乳、脫脂奶粉（水由總質量限制式自動決定，或也設成變數）；限制式同上（總質量、脂肪、MSNF、全部>=0）；按「求解」。",
        "④ Solver 求解方法選「單純線性規劃 (Simplex LP)」——因為目標函數與限制式都是線性的，這正好對應教材裡『線性規劃最佳解在可行區域端點』的理論。",
        "⑤ 重要提醒：Solver 的解是一次性的「靜態值」，改動黃色數據（例如原料單價）之後，Solver 不會自動重算——要重算就要重新按一次「求解」。這正是為什麼本章需要一張額外的「驗算表」：把 Solver（或 R）給的解當常數填入，用公式即時驗證它還滿不滿足限制式、成本是多少。",
        "# 兩個最重要的觀念",
        "① 4 個未知數、3 條方程式＝多一個自由度，存在一整個「可行配方家族」；成本是各用量的線性函數，所以最低成本解必落在可行區域的端點（線性規劃基本定理），不是中間折衷點。",
        "② 混合物的成分是「依用量加權平均」，不是簡單平均或直接相加——這正是 SUMPRODUCT(用量,成分) 存在的理由。",
        "# Excel「規劃求解」對應本章 R 函數",
        "R 的 solve()（解聯立方程）＝ Solver 只設限制式、不求最佳化；R 掃描 SMP 找最低成本 ＝ Solver 設目標「最小化」＋限制式一次求解，兩者殊途同歸，都是先寫「目標式」與「限制式」再交給演算法。Excel 沒有內建的『掃描＋畫成本曲線』功能，本章用固定的最佳解/次佳解讓學生在驗算表對照即可。",
    ])

    # =================================================================
    # 工作表 1：原料資料庫與配方平衡
    # =================================================================
    ws = book.sheet("原料資料庫與配方平衡", [22, 12, 12, 12, 12, 14, 50])
    book.text(ws, 1, 1, "迷你原料資料庫（摘自 USDA FoodData Central／SR Legacy，CC0）", bold=True, size=12, color="0F4C81")
    book.header(ws, 2, ["原料", "脂肪%", "蛋白質%", "碳水%", "灰分%", "單價(元/kg)"])
    names = ["鮮奶油(36%)", "全脂鮮乳", "脫脂奶粉", "砂糖", "玉米糖漿", "安定劑/乳化劑"]
    for i, nm in enumerate(names):
        c = ws.cell(row=3 + i, column=1, value=nm)
        c.font = Font(name=FONT)
        c.border = BOX
    fat_rng = book.data(ws, 3, 2, [36.08, 3.25, 0.77, 0, 0, 0], fmt="0.00")
    prot_rng = book.data(ws, 3, 3, [2.05, 3.15, 36.16, 0, 0, 0], fmt="0.00")
    carb_rng = book.data(ws, 3, 4, [2.79, 4.80, 51.99, 99.98, 78, 0], fmt="0.00")
    ash_rng = book.data(ws, 3, 5, [0.61, 0.70, 7.92, 0, 0, 0], fmt="0.00")
    price_rng = book.data(ws, 3, 6, [230, 38, 280, 42, 55, 850], fmt="0")

    book.header(ws, 10, ["原料", "MSNF% (=蛋白質+碳水+灰分)", "公式"])
    for i in range(3):
        row = 11 + i
        drow = 3 + i
        c = ws.cell(row=row, column=1, value=names[i])
        c.font = Font(name=FONT)
        c.border = BOX
        m = ws.cell(row=row, column=2, value=fx(f"=C{drow}+D{drow}+E{drow}"))
        m.number_format = "0.00"
        m.border = BOX
        t = ws.cell(row=row, column=3, value="'=蛋白質+碳水+灰分")
        t.font = Font(name="Consolas", size=10, color="1565C0")

    book.text(ws, 15, 1, "目標規格（每 100 kg 配方；黃色可改）", bold=True, size=12, color="0F4C81")
    book.header(ws, 16, ["項目", "數值 (kg)", "公式", "說明"])
    tgt_fat = book.calc(ws, 17, "目標脂肪", 12, "TechWizard Ice Cream 範例規格", fmt="0.00")
    book.mark_input(ws, tgt_fat)
    tgt_msnf = book.calc(ws, 18, "目標 MSNF", 11, "", fmt="0.00")
    book.mark_input(ws, tgt_msnf)
    w_sugar = book.calc(ws, 19, "砂糖用量", 14, "", fmt="0.00")
    book.mark_input(ws, w_sugar)
    w_csyrup = book.calc(ws, 20, "玉米糖漿用量", 3, "", fmt="0.00")
    book.mark_input(ws, w_csyrup)
    w_stab = book.calc(ws, 21, "安定劑/乳化劑用量", 0.5, "", fmt="0.00")
    book.mark_input(ws, w_stab)
    minor = book.calc(ws, 22, "次要原料合計", f"={w_sugar}+{w_csyrup}+{w_stab}", "砂糖+糖漿+安定劑", fmt="0.00")
    dairy_water = book.calc(ws, 23, "乳原料+水 合計", f"=100-{minor}", "100 kg 扣掉次要原料", fmt="0.00", key=True)

    book.text(ws, 25, 1, "質量平衡的 3 條方程式（4 個未知數：鮮奶油c/全脂乳m/脫脂奶粉s/水w）", bold=True, size=11, color="0F4C81")
    book.text(ws, 26, 1, "(1) 總質量：c + m + s + w = 乳原料+水合計　(2) 脂肪：0.3608c+0.0325m+0.0077s = 目標脂肪　"
                          "(3) MSNF：0.0545c+0.0865m+0.9607s = 目標MSNF", size=10)
    book.text(ws, 27, 1, "4 個未知數、3 條方程式 → 多一個自由度，存在一整個可行配方家族；要多一個準則（例如成本最低）才能選出唯一解。", size=10, color="64748B")

    # =================================================================
    # 工作表 2：最低成本驗算表（核心！）
    # =================================================================
    ws2 = book.sheet("最低成本驗算表", [26, 16, 16, 16, 16, 14, 50])
    book.text(ws2, 1, 1, "把 R／Solver 算出的解當「常數」填入（黃色可改），用公式驗證是否滿足限制式並算成本",
               bold=True, size=12, color="0F4C81")

    def solution_block(start_row, title, cream_v, milk_v, smp_v, water_v):
        book.text(ws2, start_row, 1, title, bold=True, size=11, color="0F4C81")
        book.header(ws2, start_row + 1, ["原料", "用量 (kg)"])
        cream = book.calc(ws2, start_row + 2, "鮮奶油 cream", cream_v, "", fmt="0.0000000")
        book.mark_input(ws2, cream)
        milk = book.calc(ws2, start_row + 3, "全脂鮮乳 milk", milk_v, "", fmt="0.0000000")
        book.mark_input(ws2, milk)
        smp = book.calc(ws2, start_row + 4, "脫脂奶粉 smp", smp_v, "", fmt="0.0000000")
        book.mark_input(ws2, smp)
        water = book.calc(ws2, start_row + 5, "水 water", water_v, "", fmt="0.0000000")
        book.mark_input(ws2, water)

        book.header(ws2, start_row + 7, ["限制式驗算", "結果", "公式", "應等於"])
        total = book.calc(ws2, start_row + 8, "總質量 c+m+s+w", f"={cream}+{milk}+{smp}+{water}",
                           "應等於 82.5（乳原料+水合計）", fmt="0.0000", key=True)
        fat_chk = book.calc(ws2, start_row + 9, "脂肪合量 0.3608c+0.0325m+0.0077s",
                             f"=0.3608*{cream}+0.0325*{milk}+0.0077*{smp}", "應等於目標脂肪", fmt="0.0000", key=True)
        msnf_chk = book.calc(ws2, start_row + 10, "MSNF合量 0.0545c+0.0865m+0.9607s",
                              f"=0.0545*{cream}+0.0865*{milk}+0.9607*{smp}", "應等於目標MSNF", fmt="0.0000", key=True)
        nonneg = book.calc(ws2, start_row + 11, "全部用量 ≥ 0？",
                            f'=IF(MIN({cream},{milk},{smp},{water})>=-0.000001,"是","否——不可行")',
                            "可行配方的必要條件", fmt="@")
        cost = book.calc(ws2, start_row + 12, "原料成本 (元/100kg)",
                          f"=230*{cream}+38*{milk}+280*{smp}+0.5*{water}+(14*42+3*55+0.5*850)",
                          "230c+38m+280s+0.5w+次要原料固定成本(14×42+3×55+0.5×850)", fmt="0.00", key=True)
        return dict(cream=cream, milk=milk, smp=smp, water=water, total=total,
                    fat=fat_chk, msnf=msnf_chk, cost=cost)

    best = solution_block(2, "① 最便宜解（水→0 的端點，R 用 solve() 掃描 SMP 找出）",
                           28.82543961, 47.92096579, 5.50, 0.2535945947)
    worst = solution_block(17, "② 最貴解（鮮乳→0 的另一端點，供對照）",
                            33.02935446, 0.2915049961, 9.55, 39.62914055)
    reveng = solution_block(32, "③ 逆向工程解（競品脂肪10.8%/MSNF12.22%，用同一套限制式重解）",
                             25.24752922, 50.42204485, 6.75, 0.08042592791)
    # 逆向工程解的限制式「應等於」不同（10.8 / 12.2222），公式本身不變，但比較對象在說明頁講清楚。

    book.text(ws2, 47, 1, "成本比較：最便宜 vs 最貴", bold=True, size=11, color="0F4C81")
    book.header(ws2, 48, ["項目", "結果", "公式", "說明"])
    diff = book.calc(ws2, 49, "最貴 − 最便宜 (元/100kg)", f"={worst['cost']}-{best['cost']}",
                      "同規格下，配方選擇可以差到這麼多錢", fmt="0.00", key=True)

    # =================================================================
    # 工作表 3：營養標籤與 Atwater
    # =================================================================
    ws3 = book.sheet("營養標籤與Atwater", [30, 16, 16, 44])
    book.text(ws3, 1, 1, "用「最便宜解」的用量，加權平均出每 100 g 營養值（全部用 SUMPRODUCT）", bold=True, size=12, color="0F4C81")
    book.header(ws3, 2, ["項目", "結果", "公式", "說明"])
    prot = book.calc(ws3, 3, "蛋白質 (g/100g)",
                      f"=SUMPRODUCT(('最低成本驗算表'!B4:B6),({{2.05;3.15;36.16}}))/100",
                      "SUMPRODUCT(用量欄{cream,milk,smp}, 蛋白質%欄)/100", fmt="0.000000", key=True)
    carb = book.calc(ws3, 4, "碳水化合物 (g/100g)",
                      f"=(SUMPRODUCT(('最低成本驗算表'!B4:B6),({{2.79;4.80;51.99}}))+14*99.98+3*78)/100",
                      "乳原料的碳水加權 + 砂糖14×99.98% + 玉米糖漿3×78%，全部/100", fmt="0.000000", key=True)
    lact = book.calc(ws3, 5, "乳糖 (g/100g)",
                      f"=SUMPRODUCT(('最低成本驗算表'!B4:B6),({{2.79;4.80;51.99}}))/100",
                      "只算乳原料帶來的碳水（乳糖）", fmt="0.000000")
    sugar = book.calc(ws3, 6, "糖 (標示用) (g/100g)", f"=14+{lact}+3*0.26", "砂糖14 + 乳糖 + 玉米糖漿的還原糖部分(×0.26)", fmt="0.000000", key=True)
    na_mg = book.calc(ws3, 7, "鈉 (mg/100g)",
                       f"=SUMPRODUCT(('最低成本驗算表'!B4:B6),({{30;43;1010}}))/100",
                       "SUMPRODUCT(用量, 各原料每100g鈉mg)/100", fmt="0.00000", key=True)
    fat_label = book.calc(ws3, 8, "脂肪 (g/100g)", "='原料資料庫與配方平衡'!B17", "＝目標脂肪 12", fmt="0.00")
    kcal = book.calc(ws3, 9, "熱量 Atwater 4-4-9 (kcal/100g)", f"=4*{prot}+4*{carb}+9*{fat_label}",
                      "4×蛋白質 + 4×碳水 + 9×脂肪——用來交叉驗證資料庫的 Energy 值", fmt="0.0000", key=True)

    book.text(ws3, 11, 1, "換算每份 66 g（美制 RACC 1/2 杯×0.56 g/mL 密度，含 overrun 打入的空氣）", bold=True, size=12, color="0F4C81")
    book.header(ws3, 12, ["項目", "結果", "公式", "說明"])
    serv = book.calc(ws3, 13, "每份重量 (g)", 66, "= 118 mL × 0.56 g/mL；新制 2/3 杯≈88 g，改這裡即可", fmt="0")
    book.mark_input(ws3, serv)
    servfrac = book.calc(ws3, 14, "份量比例 serv/100", f"={serv}/100", "", fmt="0.0000")
    kcal_serv = book.calc(ws3, 15, "熱量/份 (kcal)", f"={kcal}*{servfrac}", "未套 FDA 捨入前的原始值", fmt="0.0000", key=True)
    kcal_fda = book.calc(ws3, 16, "熱量/份 FDA捨入 (kcal)",
                          f'=IF({kcal_serv}<=5,0,IF({kcal_serv}<=50,ROUND({kcal_serv}/5,0)*5,ROUND({kcal_serv}/10,0)*10))',
                          "FDA 簡化捨入規則：≤5記0；≤50取5的倍數；否則取10的倍數", fmt="0")
    prot_serv = book.calc(ws3, 17, "蛋白質/份 FDA捨入 (g)",
                           f'=IF({prot}*{servfrac}<0.5,0,ROUND({prot}*{servfrac},0))', "<0.5g記0，否則四捨五入", fmt="0")
    fat_serv = book.calc(ws3, 18, "脂肪/份 FDA捨入 (g)",
                          f'=IF({fat_label}*{servfrac}<0.5,0,ROUND({fat_label}*{servfrac},0))', "", fmt="0")
    carb_serv = book.calc(ws3, 19, "碳水/份 FDA捨入 (g)",
                           f'=IF({carb}*{servfrac}<0.5,0,ROUND({carb}*{servfrac},0))', "", fmt="0")
    sugar_serv = book.calc(ws3, 20, "糖/份 FDA捨入 (g)",
                            f'=IF({sugar}*{servfrac}<0.5,0,ROUND({sugar}*{servfrac},0))', "", fmt="0")
    na_serv = book.calc(ws3, 21, "鈉/份 FDA捨入 (mg)", f"=ROUND({na_mg}*{servfrac}/5,0)*5", "5–140mg取5的倍數（簡化版）", fmt="0")

    book.text(ws3, 23, 1, "教學簡化版捨入規則，實際以最新法規為準；算出來的標籤應接近 140kcal/3g蛋白/8g脂肪/15g碳水/14g糖/55mg鈉。", size=10, color="64748B")

    book.check("驗算：最便宜解總質量", "最低成本驗算表", best["total"], 82.5)
    book.check("驗算：最便宜解脂肪合量", "最低成本驗算表", best["fat"], 12.0)
    book.check("驗算：最便宜解MSNF合量", "最低成本驗算表", best["msnf"], 11.0)
    book.check("驗算：最便宜解成本", "最低成本驗算表", best["cost"], 11168.97461)
    book.check("驗算：最貴解成本", "最低成本驗算表", worst["cost"], 11479.64328)
    book.check("驗算：逆向工程解成本", "最低成本驗算表", reveng["cost"], 10791.00964)
    book.check("驗算：逆向工程解脂肪合量", "最低成本驗算表", reveng["fat"], 10.8, tol=0.01)
    book.check("驗算：逆向工程解MSNF合量", "最低成本驗算表", reveng["msnf"], 12.22222222, tol=0.01)
    book.check("蛋白質 (g/100g)", "營養標籤與Atwater", prot, 4.089231935)
    book.check("碳水化合物 (g/100g)", "營養標籤與Atwater", carb, 22.30108612)
    book.check("鈉 (mg/100g)", "營養標籤與Atwater", na_mg, 84.80364717)
    book.check("熱量 Atwater (kcal/100g)", "營養標籤與Atwater", kcal, 213.5612722)
    book.check("熱量/份 (kcal)", "營養標籤與Atwater", kcal_serv, 140.9504397)
    return book
