# =====================================================================
# Ch01 食品分析數據的開始：集中趨勢與離散程度
# 教材來源：Nielsen's Food Analysis, Chap.4 "Evaluation of Analytical Data"
# 對象：無程式基礎的大學生
# 執行方式：在 RStudio 中全選 (Ctrl+Alt+R) 或逐行執行 (Ctrl+Enter)
# =====================================================================

# ---------- 0. R 就像一台超強計算機 ----------
2 + 3            # 加法
10 / 4           # 除法
sqrt(2)          # 開根號
pi               # 內建常數圓周率

# ---------- 1. 把量測數據存進「向量」(c = combine) ----------
# 例：漢堡生肉水分含量 4 次重複測定 (%)，Nielsen 第4章 Table 4.1
moisture <- c(64.53, 64.45, 65.10, 64.78)
moisture          # 輸入 moisture 後按 Enter，R 會把內容印出來

length(moisture)  # 有幾個數據？ -> 4

# ---------- 2. 中央趨勢：平均數 mean() 與中位數 median() ----------
xbar <- mean(moisture)      # 平均數 x-bar
xbar                        # -> 64.715，四捨五入即課本的 64.72%
round(xbar, 2)              # round(x, n) 取到小數第 n 位

median(moisture)            # 中位數：由小到大排在中間的值

# 手動重現平均數公式 x_bar = sum(xi)/n
sum(moisture) / length(moisture)

# ---------- 3. 離散程度：標準差 SD 與變異係數 CV ----------
# R 的 sd() 用的是 n-1 的樣本標準差（Nielsen 式 4.5）
s <- sd(moisture)
s                                        # -> 0.2927（課本 SD = 0.293）
var(moisture)                            # 變異數 s^2 = SD^2

# 手動計算驗證：SD = sqrt( sum((xi - xbar)^2) / (n-1) )
deviations <- moisture - xbar            # 每個值對平均數的偏差
deviations^2                             # 偏差平方
sum(deviations^2) / (length(moisture) - 1)   # 變異數
sqrt(sum(deviations^2) / (length(moisture) - 1)) # 就是 sd()

# 全距 range（最大-最小），參考用
range(moisture)                # 最小與最大
diff(range(moisture))          # 全距 = 0.65

# 變異係數 CV% = SD / mean * 100 （又稱相對標準偏差 RSD%）
cv <- s / xbar * 100
cv                              # -> 0.4525%，遠小於 5%，精密度良好
round(cv, 3)

# 經驗法則：CV < 5% 通常可接受（依分析方法而定）

# ---------- 4. 練習：換你算算看 ----------
# 乾物質含量 4 次測定 (%)，Nielsen 章末習題 3
dry_matter <- c(88.62, 88.74, 89.20, 82.20)
mean(dry_matter)    # 87.19
sd(dry_matter)      # 3.34
sd(dry_matter) / mean(dry_matter) * 100   # CV% = 3.83%

# 注意：82.20 看起來特別低，是不是異常值？
# 先別急著刪！下一章會學 Q 檢定（ch05）來客觀判斷。

# ---------- 5. 小結 ----------
# 一組重複數據的基本報告格式：
cat(sprintf("結果報告：mean = %.2f %%，SD = %.3f，CV = %.2f %%",
            mean(moisture), sd(moisture), sd(moisture)/mean(moisture)*100))
