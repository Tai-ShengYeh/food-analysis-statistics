# =====================================================================
# Ch17 ANOVA 進階：雙因子、精密度分解與失擬檢定
# Two-way ANOVA / Precision decomposition (ISO 5725) / Lack-of-fit
# 先修：Ch15 假說檢定 (t、F)、Ch16 單因子 ANOVA
# 只用 base R；所有資料都直接寫在腳本裡（教學模擬數據），可整份重跑。
# =====================================================================

set.seed(17)                       # 本腳本沒有用到亂數；保留以符合全站慣例
if (!interactive()) pdf(NULL)      # 用 Rscript 批次跑時，不要產生 Rplots.pdf

# =====================================================================
# Part A. 雙因子 ANOVA 與交互作用
# 情境：熱風乾燥芭樂片，乾燥溫度 (50/60/70 °C) × 時間 (4/8 h)
#       反應值 = 維生素 C 保留率 (%)；每一格 (cell) 做 3 個獨立批次
# =====================================================================

# ---------- A1. 資料與各格平均 ----------
vitc <- data.frame(
  temp = factor(rep(rep(c(50, 60, 70), each = 3), times = 2)),
  time = factor(rep(c(4, 8), each = 9)),
  y    = c(90.5, 91.9, 91.7,   83.8, 86.2, 84.8,   75.5, 76.6, 74.4,   # 4 h
           88.5, 89.8, 89.0,   77.9, 76.3, 78.4,   54.9, 56.3, 55.2))  # 8 h
# 注意：temp、time 一定要轉成 factor，否則 R 會把 50/60/70 當成連續數字配直線

cell_mean <- with(vitc, tapply(y, list(temp = temp, time = time), mean))
round(cell_mean, 2)                # 3×2 的「各格平均」表：這是判讀的主角

# ---------- A2. 雙因子 ANOVA：temp * time = temp + time + temp:time ----------
fit_tw <- aov(y ~ temp * time, data = vitc)
summary(fit_tw)
# 讀表順序：先看最下面的交互作用 temp:time！
#   顯著 -> 「時間的影響」隨溫度而不同，主效應不能單獨解讀 (見 A4)

# ---------- A3. 交互作用圖：線不平行 = 有交互作用 ----------
with(vitc, interaction.plot(temp, time, y, type = "b", pch = c(19, 17),
                            col = c("#1565C0", "#C62828"), lwd = 2,
                            xlab = "乾燥溫度 (°C)", ylab = "維生素 C 保留率 (%)",
                            trace.label = "時間 (h)"))

# ---------- A4. 交互作用顯著時：改看 simple effects（各溫度下時間的效應）----------
drop_by_time <- cell_mean[, "4"] - cell_mean[, "8"]   # 每個溫度下：4 h -> 8 h 掉了多少
round(drop_by_time, 2)
round(mean(drop_by_time), 2)       # 「時間主效應」= 三個溫度的平均，誰都不代表
# 用 ANOVA 的共同誤差 MSE 給每個差值一個 95% CI 半寬：t × sqrt(2·MSE/n)
MSE_tw <- summary(fit_tw)[[1]]["Residuals", "Mean Sq"]
round(qt(0.975, df = 12) * sqrt(2 * MSE_tw / 3), 2)

# ---------- A5. 不平衡設計：aov() 的 Type I (循序) SS 會受因子順序影響 ----------
vitc_unbal <- vitc[-18, ]          # 假設最後一批樣品打翻了 -> 70°C/8h 只剩 2 筆
ss <- function(fit) round(summary(fit)[[1]][, "Sum Sq", drop = FALSE], 2)
ss(aov(y ~ temp * time, data = vitc_unbal))   # 先放 temp
ss(aov(y ~ time * temp, data = vitc_unbal))   # 先放 time -> temp、time 的 SS 變了
# 平衡設計 (每格 n 相同) 沒有這個問題：
ss(aov(y ~ time * temp, data = vitc))         # 與 A2 的 SS 完全相同

# ---------- A6. 無重複的雙因子：隨機區集設計 (block) ----------
# 5 個乳製品樣品 (粗脂肪 %)，3 位分析員各測一次。樣品 = 區集 (block)
fat <- data.frame(
  sample  = factor(rep(1:5, times = 3)),
  analyst = factor(rep(c("A", "B", "C"), each = 5)),
  y = c(3.14, 4.11, 5.66, 6.73, 8.36,     # 分析員 A
        3.32, 4.10, 5.75, 7.05, 8.44,     # 分析員 B
        3.18, 3.92, 5.55, 6.84, 8.30))    # 分析員 C
summary(aov(y ~ analyst, data = fat))            # 錯誤示範：忽略區集
summary(aov(y ~ analyst + sample, data = fat))   # 正確：把樣品差異「扣掉」
# 每格只有 1 筆 -> 沒有自由度估交互作用，所以模型用「+」不用「*」

# 只比兩位分析員 (A vs B) 時，區集 ANOVA 的 F 就是 paired t 的平方 (Ch15)
fat_AB <- droplevels(subset(fat, analyst != "C"))
summary(aov(y ~ analyst + sample, data = fat_AB))
tt <- t.test(fat$y[fat$analyst == "A"], fat$y[fat$analyst == "B"], paired = TRUE)
round(c(t = unname(tt$statistic), t_squared = unname(tt$statistic)^2,
        p = tt$p.value), 4)

# =====================================================================
# Part B. 用 ANOVA 分解精密度 (ISO 5725 / 方法確效)
# 情境：同一罐奶粉 QC 樣品，凱氏法粗蛋白 (%)，5 天 × 每天 3 重複
# =====================================================================

# ---------- B1. 資料與單因子 ANOVA ----------
qc <- data.frame(
  day = factor(rep(1:5, each = 3)),
  y   = c(26.45, 26.35, 26.57,    # day 1
          26.52, 26.46, 26.70,    # day 2
          26.40, 26.49, 26.59,    # day 3
          26.27, 26.26, 26.33,    # day 4
          26.57, 26.56, 26.44))   # day 5
round(tapply(qc$y, qc$day, mean), 3)       # 每天的平均
fit_qc <- aov(y ~ day, data = qc)
summary(fit_qc)

# ---------- B2. 由 MS 拆出三個標準差 ----------
tab  <- summary(fit_qc)[[1]]
MS_b <- tab["day", "Mean Sq"]              # 日間 (between-day) 均方
MS_w <- tab["Residuals", "Mean Sq"]        # 日內 (within-day) 均方
n    <- 3                                  # 每天重複數
s_r       <- sqrt(MS_w)                    # 重複性標準差 repeatability
s_between <- sqrt(max(0, (MS_b - MS_w) / n))   # 日間標準差；負值取 0
s_I       <- sqrt(s_r^2 + s_between^2)     # 中間精密度 intermediate precision
round(c(MS_between = MS_b, MS_within = MS_w), 5)
round(c(s_r = s_r, s_between = s_between, s_I = s_I), 4)
round(100 * c(RSD_r = s_r, RSD_I = s_I) / mean(qc$y), 2)   # 換成 RSD (%)

# ---------- B3. 對照：把 15 筆直接丟進 sd() ----------
round(sd(qc$y), 4)
# 既不是 s_r 也不是 s_I：它是 sqrt[(4·MS_b + 10·MS_w)/14]，兩種變異「混在一起」
round(sqrt((4 * MS_b + 10 * MS_w) / 14), 4)

# ---------- B4. 回扣 Ch07 Type A：「當天 3 重複的平均」不確定度是多少？ ----------
round(c(naive_same_day = s_r / sqrt(3),                  # 只用當天重複 -> 低估
        correct        = sqrt(s_between^2 + s_r^2 / 3)), 4)
# 日間變異不會因為「同一天多測幾次」而變小

# ---------- B5. s_between^2 算出負值怎麼辦？ ----------
# 另一個 QC 樣品 (粗脂肪 %)：日與日之間其實沒什麼差別
qc2 <- data.frame(
  day = factor(rep(1:5, each = 3)),
  y   = c(3.52, 3.41, 3.49,   3.44, 3.55, 3.47,   3.50, 3.43, 3.53,
          3.46, 3.54, 3.42,   3.51, 3.45, 3.48))
tab2 <- summary(aov(y ~ day, data = qc2))[[1]]
round(c(MS_between = tab2["day", "Mean Sq"],
        MS_within  = tab2["Residuals", "Mean Sq"]), 5)
round((tab2["day", "Mean Sq"] - tab2["Residuals", "Mean Sq"]) / 3, 5)   # 負的！
# 不是算錯：日間變異很小時，MS_between 只是碰巧比 MS_within 小
# 慣例：s_between = 0，此時 s_I = s_r
round(sqrt(tab2["Residuals", "Mean Sq"]), 4)

# =====================================================================
# Part C. 失擬檢定 Lack-of-fit
# =====================================================================

# ---------- C1. Ch04 的 HPLC 咖啡因標準曲線 (5 濃度 × 3 重複) ----------
# 數值出處：R/ch04_regression.R 第 7 節 (WLS 範例)，原樣複製
conc <- rep(c(1, 5, 10, 50, 100), each = 3)
area <- c(101, 99, 102,
          498, 505, 492,
          1005, 992, 1018,
          4930, 5070, 5005,
          9720, 10380, 10040)
fit_line <- lm(area ~ conc)            # 直線模型：2 個參數
fit_cell <- lm(area ~ factor(conc))    # 「每個濃度各給一個平均」：5 個參數
round(summary(fit_line)$r.squared, 5)
anova(fit_line, fit_cell)              # 第 2 列就是失擬檢定

# 手算對照：殘差 SS = 純誤差 SS + 失擬 SS
SS_res <- sum(residuals(fit_line)^2)
SS_pe  <- sum((area - ave(area, conc))^2)     # 重複點離「自己濃度平均」多遠
SS_lof <- SS_res - SS_pe                      # 各濃度平均離「直線」多遠
df_pe  <- length(area) - 5                    # N - 濃度數 = 15 - 5
df_lof <- 5 - 2                               # 濃度數 - 直線參數數
F_lof  <- (SS_lof / df_lof) / (SS_pe / df_pe)
round(c(SS_res = SS_res, SS_pe = SS_pe, SS_lof = SS_lof), 1)
round(c(F = F_lof, p = pf(F_lof, df_lof, df_pe, lower.tail = FALSE)), 4)
# 提醒：這組資料高濃度的散布明顯較大 (Ch04 用它示範加權)。
# 同樣的兩模型比較也可以帶權重做：
w <- 1 / conc^2
anova(lm(area ~ conc, weights = w), lm(area ~ factor(conc), weights = w))

# ---------- C2. r^2 很高但其實是彎的：高濃度飽和的標準曲線 ----------
# 分光光度法，6 濃度 (mg/L) × 3 重複，反應值 = 吸光度 × 1000
conc2 <- rep(c(2, 4, 6, 8, 10, 12), each = 3)
resp2 <- c(197, 191, 200,   371, 375, 371,   541, 548, 547,
           705, 698, 699,   847, 835, 855,   977, 980, 978)
fit_l2 <- lm(resp2 ~ conc2)
fit_c2 <- lm(resp2 ~ factor(conc2))
round(summary(fit_l2)$r.squared, 4)    # r^2 > 0.99，看起來「很直」
anova(fit_l2, fit_c2)                  # 失擬極顯著 -> 直線模型不對
round(tapply(residuals(fit_l2), conc2, mean), 1)   # 殘差：負 -> 正 -> 負 (倒 U)

fit_q2 <- lm(resp2 ~ conc2 + I(conc2^2))   # 加二次項
anova(fit_q2, fit_c2)                  # 失擬不顯著 -> 二次模型足夠

# ---------- C3. 沒有重複就沒有純誤差 ----------
one_each <- !duplicated(conc2)         # 每個濃度只留第 1 筆
fit_l3 <- lm(resp2[one_each] ~ conc2[one_each])
fit_c3 <- lm(resp2[one_each] ~ factor(conc2[one_each]))
round(summary(fit_l3)$r.squared, 4)
df.residual(fit_c3)                    # 純誤差自由度 = 0 -> F 的分母不存在
# anova(fit_l3, fit_c3) 只會給 NA：沒有重複 = 無法做失擬檢定

# ---------- C4. 銜接 Ch14：CCD 的 6 個中心點就是純誤差的來源 ----------
# 數值出處：R/ch14_doe_rsm.R Part 2 (set.seed(15) 產生的 20 個 run)，原樣重建
alpha <- 2^(3/4)                       # 1.682
ccd <- data.frame(
  A = c(-1, 1, -1, 1, -1, 1, -1, 1, -alpha, alpha, 0, 0, 0, 0, rep(0, 6)),
  B = c(-1, -1, 1, 1, -1, -1, 1, 1, 0, 0, -alpha, alpha, 0, 0, rep(0, 6)),
  C = c(-1, -1, -1, -1, 1, 1, 1, 1, 0, 0, 0, 0, -alpha, alpha, rep(0, 6)),
  y = c(34.8, 41.7, 35.1, 51.6, 39.1, 42.0, 39.5, 55.8,      # 因子點
        31.6, 47.3, 41.8, 50.5, 39.9, 44.9,                  # 軸點
        61.8, 60.0, 60.0, 60.0, 58.6, 59.4))                 # 中心點 ×6
ccd$pt <- factor(paste(ccd$A, ccd$B, ccd$C))   # 15 個不同的設計點
fit1_ccd <- lm(y ~ (A + B + C)^2, data = ccd)                        # 一階+交互
fit2_ccd <- lm(y ~ (A + B + C)^2 + I(A^2) + I(B^2) + I(C^2), data = ccd)  # 二階
fit_pt   <- lm(y ~ pt, data = ccd)                                   # 每點一個平均
round(sd(ccd$y[15:20]), 3)             # 中心點的 s = 純誤差標準差 (df = 5)
anova(fit1_ccd, fit_pt)                # 一階模型：失擬顯著 (曲面是彎的)
anova(fit2_ccd, fit_pt)                # 二階模型：失擬不顯著 -> 可以拿去找駐點

# =====================================================================
# Part D. 章末測驗計算題的驗算
# =====================================================================

# ---------- D1. ch17-q04：MS_between = 0.0450、MS_within = 0.0120、每天 n = 4 ----------
q_MSb <- 0.0450; q_MSw <- 0.0120; q_n <- 4
q_sr <- sqrt(q_MSw); q_sb <- sqrt((q_MSb - q_MSw) / q_n)
round(c(s_r = q_sr, s_between = q_sb,
        s_I = sqrt(q_sr^2 + q_sb^2),                  # 正解 0.142
        forgot_n   = sqrt(q_MSw + (q_MSb - q_MSw)),   # 忘了除以 n -> 0.212
        add_linear = q_sr + q_sb,                     # 標準差直接相加 -> 0.200
        sd_all_24  = sqrt((5 * q_MSb + 18 * q_MSw) / 23)), 4)   # 24 筆全丟進 sd() -> 0.138

# ---------- D2. ch17-q05：SS_res = 500、SS_pe = 200、6 濃度 × 3 重複、直線模型 ----------
q_lof <- 500 - 200; q_df_lof <- 6 - 2; q_df_pe <- 18 - 6
round(c(F = (q_lof / q_df_lof) / (200 / q_df_pe),              # 正解 4.5
        used_total_resid = (500 / 16) / (200 / q_df_pe),       # 分子誤用整個殘差
        ss_ratio   = q_lof / 200,                              # 忘了除自由度
        df_swapped = (q_lof / q_df_pe) / (200 / q_df_lof)), 3) # 自由度放反
round(pf(4.5, 4, 12, lower.tail = FALSE), 4)

# ---------- 自我檢查 ----------
stopifnot(abs(F_lof - anova(fit_line, fit_cell)$F[2]) < 1e-8,
          abs(unname(tt$statistic)^2 -
              summary(aov(y ~ analyst + sample, data = fat_AB))[[1]]["analyst", "F value"]) < 1e-8,
          s_I > s_r)

cat("
練習 1：把 vitc 的 70°C/8h 三筆改成 66.0, 67.2, 65.9 重跑 A2–A3，
        交互作用還顯著嗎？兩條線變得比較平行了嗎？
練習 2：B 部分若每天做 6 重複而不是 3 重複，公式裡的 n 要改成多少？
        s_r 的自由度變成多少？
練習 3：對 C2 的資料畫 plot(conc2, residuals(fit_l2))，
        再畫 residuals(fit_q2)，比較兩張殘差圖的形狀。
")
