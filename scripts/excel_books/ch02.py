"""Ch02 常態分配與信賴區間 —— 範本模組（其他章照這個寫法）。

R 的答案來源：Rscript R/ch02_ci_normal.R（moisture 四次測定）。
"""
from excel_common import Book


def build():
    book = Book("ch02_confidence_interval.xlsx", "Ch2 常態分配與信賴區間：用 Excel 算 95% 信賴區間", "ch02.html")
    book.readme([
        "# 這本活頁簿在做什麼",
        "漢堡生肉水分含量測了 4 次（Nielsen Table 4.1）。我們要回答：真值最可能落在哪個範圍？",
        "「CI計算」工作表一步一步算出平均、標準差、標準誤、t 值、95% 信賴區間；「68-95-99.7」驗證常態分配的面積口訣。",
        "# 怎麼用",
        "1. 先看「CI計算」：左邊黃色是原始數據，右邊每一列都是一個公式，C 欄把公式原文印出來給你對照。",
        "2. 試著把黃色數據改成你自己實驗的 4 次重複，所有結果會自動重算。",
        "3. 把 B13 的信心水準 0.95 改成 0.99，看區間變寬還是變窄。",
        "4.「對照R答案」工作表會核對 Excel 與 R 算出來是否一致。",
        "# 為什麼 n 很小要用 t 而不是 Z",
        "只測 4 次時，樣本標準差本身就不太準；t 分布用比較大的乘數（3.182 而不是 1.96）把這份不確定補回來。",
    ])

    ws = book.sheet("CI計算", [22, 14, 44, 60])
    book.header(ws, 1, ["水分 (%)"])
    rng = book.data(ws, 2, 1, [64.53, 64.45, 65.10, 64.78], fmt="0.00")
    book.header(ws, 7, ["項目", "結果", "公式", "白話說明"])
    n = book.calc(ws, 8, "n（重複次數）", f"=COUNT({rng})", "數一數有幾個數據", fmt="0")
    mean = book.calc(ws, 9, "平均 x̄", f"=AVERAGE({rng})", "結果「在哪裡」")
    sd = book.calc(ws, 10, "標準差 SD", f"=STDEV.S({rng})", "數據有多散；分母是 n−1")
    sem = book.calc(ws, 11, "標準誤 SEM", f"={sd}/SQRT({n})", "平均值本身有多不確定：SD ÷ √n")
    df = book.calc(ws, 12, "自由度 df", f"={n}-1", "n − 1", fmt="0")
    conf = book.calc(ws, 13, "信心水準", 0.95, "可以改成 0.90 或 0.99 試試", fmt="0.00")
    book.mark_input(ws, conf)
    t = book.calc(ws, 14, "t 值（雙尾）", f"=T.INV.2T(1-{conf},{df})", "T.INV.2T 直接給雙尾的 t；α = 1 − 信心水準")
    half = book.calc(ws, 15, "CI 半寬", f"={t}*{sem}", "t × SEM", key=True)
    lo = book.calc(ws, 16, "CI 下限", f"={mean}-{half}", "", key=True)
    hi = book.calc(ws, 17, "CI 上限", f"={mean}+{half}", "", key=True)
    book.calc(ws, 18, "用 Z=1.96 會算成", f"=NORM.S.INV(0.975)*{sem}", "小樣本誤用 Z 會讓區間窄得不合理（這是常見迷思）")
    book.text(ws, 20, 1, "報告寫法：64.72 ± 0.47 %（95%, n=4）。一定要附信心水準與 n。", bold=True)

    ws2 = book.sheet("68-95-99.7", [22, 14, 50, 50])
    book.header(ws2, 1, ["範圍", "面積", "公式", "白話說明"])
    a1 = book.calc(ws2, 2, "±1 SD", "=NORM.S.DIST(1,TRUE)-NORM.S.DIST(-1,TRUE)", "約 68%")
    a2 = book.calc(ws2, 3, "±2 SD", "=NORM.S.DIST(2,TRUE)-NORM.S.DIST(-2,TRUE)", "約 95%")
    book.calc(ws2, 4, "±3 SD", "=NORM.S.DIST(3,TRUE)-NORM.S.DIST(-3,TRUE)", "約 99.7%")

    book.check("平均", "CI計算", mean, 64.715)
    book.check("標準差 SD", "CI計算", sd, 0.2926317)
    book.check("t 值 (df=3, 95%)", "CI計算", t, 3.182446)
    book.check("95% CI 半寬", "CI計算", half, 0.4656424)
    book.check("CI 下限", "CI計算", lo, 64.24936)
    book.check("CI 上限", "CI計算", hi, 65.18064)
    book.check("±1 SD 面積", "68-95-99.7", a1, 0.6826895)
    book.check("±2 SD 面積", "68-95-99.7", a2, 0.9544997)
    return book
