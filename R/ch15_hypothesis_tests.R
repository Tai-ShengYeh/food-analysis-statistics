# =====================================================================
# Ch15 假說檢定與 t／F 檢定 (Hypothesis Testing, t-test & F-test)
# one-sample t / paired t / Welch t / F 檢定 / 檢定力 / 多重比較
# 只用 base R（stats 套件內建函數）。每段三步驟：建立資料 -> 計算 -> 解讀
# 執行：Rscript R/ch15_hypothesis_tests.R
# =====================================================================

# ---------- 1. one-sample t：用 CRM 檢查方法有沒有偏倚 (ch15_ex1) ----------
# 步驟一：建立資料。奶粉 CRM 粗蛋白認證值 35.10 g/100 g，凱氏法重複 6 次
crm  <- c(34.92, 35.12, 34.85, 35.04, 34.81, 34.98)
cert <- 35.10

# 步驟二：計算。t = (平均 - 認證值) / (SD/sqrt(n))
n    <- length(crm)
bias <- mean(crm) - cert
se   <- sd(crm) / sqrt(n)
t0   <- bias / se
round(c(mean = mean(crm), SD = sd(crm), bias = bias, SE = se, t = t0), 4)
2 * pt(-abs(t0), df = n - 1)            # 雙尾 p 值：兩邊尾巴的面積
qt(0.975, df = n - 1)                   # 臨界值 t(0.975, 5)

# 步驟三：一行指令做完，並解讀
t.test(crm, mu = cert)
round(mean(crm) / cert * 100, 2)        # 回收率 %（Ch06 的真度）

# ---------- 2. 95% CI 與雙尾 p 值是同一件事 (ch15_ex2) ----------
ci <- t.test(crm, mu = cert)$conf.int
round(as.numeric(ci), 4)                # 35.10 不在區間內 <=> p < 0.05
t.test(crm, mu = ci[2])$p.value         # 把假設值放在 CI 邊界 -> p 剛好 0.05
t.test(crm, mu = 35.00)$p.value         # 假設值在 CI 裡面   -> p > 0.05
t.test(crm, mu = 35.20)$p.value         # 假設值在 CI 外面   -> p < 0.05

# ---------- 3. 單尾檢定：事前就決定方向 (ch15_ex3) ----------
# 奶粉水分規格上限 4.00%。品管只關心「有沒有超過」-> 抽樣前就決定用單尾
moist <- c(4.12, 3.98, 4.21, 4.05, 4.16)
t.test(moist, mu = 4.00, alternative = "greater")$p.value   # 單尾
t.test(moist, mu = 4.00)$p.value                            # 雙尾 = 單尾的 2 倍

# ---------- 4. 回扣 Ch05：Grubbs 檢定也是假說檢定 (ch15_ex4) ----------
# H0：82.20 與其他值來自同一個母體；檢定統計量 G；臨界值 G_crit
dry <- c(88.62, 88.74, 89.20, 82.20)
G   <- max(abs(dry - mean(dry))) / sd(dry)
nn  <- length(dry)
t2  <- qt(0.05 / (2 * nn), df = nn - 2)^2
Gcrit <- ((nn - 1) / sqrt(nn)) * sqrt(t2 / (nn - 2 + t2))
round(c(G = G, Gcrit = Gcrit), 3)
G > Gcrit                               # TRUE -> 拒絕 H0（α = 0.05）

# ---------- 5. paired t：凱氏法 vs 杜馬斯法，同 10 個樣品 (ch15_ex5) ----------
# 步驟一：建立資料（粗蛋白 %，每個樣品兩種方法各測一次）
food <- c("鮮乳", "優格", "豆漿", "白米", "麵粉",
          "雞蛋", "豬里肌", "雞胸肉", "黃豆粉", "脫脂奶粉")
kjeldahl <- c(3.12, 3.85, 3.41, 6.92, 11.85, 12.48, 20.35, 23.10, 36.42, 35.18)
dumas    <- c(3.20, 4.07, 3.37, 7.11, 11.95, 12.79, 20.37, 23.36, 36.65, 35.30)

# 步驟二：計算。成對 t 其實就是「對差值做 one-sample t（mu = 0）」
d <- dumas - kjeldahl
d
round(c(mean_d = mean(d), SD_d = sd(d)), 4)
round(c(SD_kjeldahl = sd(kjeldahl), SD_dumas = sd(dumas)), 2)  # 樣品間差異

# 步驟三：正確做法 vs 錯誤做法
t.test(dumas, kjeldahl, paired = TRUE)  # 正確：成對
t.test(dumas, kjeldahl)$p.value         # 錯用：當成兩組獨立樣本

# ---------- 6. 兩獨立樣本：Welch t 當預設 (ch15_ex6) ----------
# 兩條產線醬油的總氮 (g/100 mL)。A 線 4 批、B 線 10 批，批次彼此獨立
lineA <- c(1.52, 1.38, 1.61, 1.45)
lineB <- c(1.41, 1.38, 1.43, 1.39, 1.42, 1.37, 1.40, 1.44, 1.38, 1.41)
round(c(mean_A = mean(lineA), SD_A = sd(lineA),
        mean_B = mean(lineB), SD_B = sd(lineB)), 4)

t.test(lineA, lineB)                    # 預設就是 Welch（不假設變異數相等）
t.test(lineA, lineB, var.equal = TRUE)$p.value   # 硬假設等變異 -> 結論翻盤

# ---------- 7. F 檢定：兩位分析員的精密度 (ch15_ex7) ----------
# 同一罐均質火腿樣品，兩人各獨立稱樣、萃取 8 次，測粗脂肪 (%)
senior <- c(14.52, 14.61, 14.48, 14.57, 14.66, 14.50, 14.59, 14.55)
junior <- c(14.31, 14.82, 14.47, 14.95, 14.20, 14.68, 14.39, 14.77)
round(c(SD_senior = sd(senior), SD_junior = sd(junior),
        F = var(junior) / var(senior)), 4)
var.test(junior, senior)                # F = 變異數比（不是 SD 比）

# F 檢定很怕非常態：兩組其實來自「同一個」右偏母體（對數常態），
# 理論上只該有 5% 誤判，實際上呢？
set.seed(1505)
p_norm <- replicate(5000, var.test(rnorm(10),  rnorm(10))$p.value)
p_skew <- replicate(5000, var.test(rlnorm(10), rlnorm(10))$p.value)
c(normal = mean(p_norm < 0.05), lognormal = mean(p_skew < 0.05))

# ---------- 8. 檢定力與樣本數 (ch15_ex8) ----------
# 問題：兩方法重複性 SD 約 0.15%，想偵測 0.2% 的差異，每組要重複幾次？
power.t.test(delta = 0.2, sd = 0.15, sig.level = 0.05, power = 0.80)

# 反過來：如果每組只做 n 次，抓得到 0.2% 差異的機率（檢定力）是多少？
ns  <- c(3, 5, 8, 10, 15)
pow <- sapply(ns, function(k)
  power.t.test(n = k, delta = 0.2, sd = 0.15)$power)
round(setNames(pow, paste0("n=", ns)), 3)

# 「不顯著 ≠ 相等」：每組只做 3 次的例子
k3 <- c(12.31, 12.52, 12.40)            # 凱氏法
d3 <- c(12.55, 12.71, 12.49)            # 杜馬斯法
r3 <- t.test(d3, k3)
round(c(diff = mean(d3) - mean(k3), p = r3$p.value), 4)
round(as.numeric(r3$conf.int), 3)       # CI 同時包含 0 和 0.2 以上 -> 無法下結論

# ---------- 9. 統計顯著 vs 實務重要 (ch15_ex9) ----------
# 兩台線上水分儀各測 40 包同批奶粉；廠內容許兩台儀器差 ±0.20%
set.seed(1509)
nirA <- round(rnorm(40, mean = 3.52, sd = 0.06), 2)
nirB <- round(rnorm(40, mean = 3.56, sd = 0.06), 2)
r9 <- t.test(nirB, nirA)
round(c(diff = mean(nirB) - mean(nirA), p = r9$p.value), 4)
round(as.numeric(r9$conf.int), 3)       # 整個 CI 都遠小於 0.20 -> 實務上可忽略

# ---------- 10. 多重比較：為什麼三組以上不能兩兩 t 檢定 (ch15_ex10) ----------
groups <- 2:6
pairs  <- choose(groups, 2)             # k 組共有幾對
data.frame(groups = groups, pairs = pairs,
           alpha_family = round(1 - 0.95^pairs, 3))

# 模擬驗證：5 位分析員其實「完全沒差」，兩兩 t 檢定 10 次，
# 至少出現一次 p < 0.05（誤判有人不一樣）的比例？
set.seed(1510)
cmb <- combn(5, 2)
any_sig <- replicate(2000, {
  x <- matrix(rnorm(5 * 4, mean = 12.5, sd = 0.15), nrow = 4)  # 5 人各 4 重複
  p <- apply(cmb, 2, function(j) t.test(x[, j[1]], x[, j[2]])$p.value)
  any(p < 0.05)
})
mean(any_sig)

# ---------- 11. 章末測驗的計算題驗算 ----------
# ch15-q03：認證值 12.50、n = 5、平均 12.38、SD = 0.09 -> |t|
round(abs(12.38 - 12.50) / (0.09 / sqrt(5)), 2)     # 正解 2.98
round(abs(12.38 - 12.50) / 0.09, 2)                 # 忘了除 sqrt(n) -> 1.33
round(abs(12.38 - 12.50) / (0.09 / 5), 2)           # 誤用 SD/n       -> 6.67
qt(0.975, 4)                                        # 臨界值 2.776
# ch15-q04：4 組兩兩比較 6 次
round(c(1 - 0.95^choose(4, 2), 1 - 0.95^4, 6 * 0.05), 3)
