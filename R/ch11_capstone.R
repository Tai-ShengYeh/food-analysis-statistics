# =====================================================================
# Ch10 綜合案例：把所有工具串起來
# 案例1 鎘標準液不準度預算 | 案例2 飼料粗纖維(QUAM A6)
# 案例3 標準曲線內插的不準度(QUAM 附錄 E.4)
# =====================================================================

# =============== 案例 2：粗纖維 (QUAM Example A6) ===============
# C_fibre = (b - c)/a * 100  [% m/m]
#   a = 樣品重 ~1 g, b = 灰化失重, c = 空白灰化失重
# 實證方法(empirical method)：結果由方法定義，直接採用
# 協同試驗 (collaborative trial) 的再現性標準差 sR
sR_table <- data.frame(
  sample = LETTERS[1:5],
  fibre  = c(2.3, 12.1, 5.4, 3.4, 10.1),
  sR     = c(0.293, 0.563, 0.390, 0.347, 0.575),
  s_r    = c(0.198, 0.358, 0.264, 0.232, 0.391))
print(sR_table)

# 觀察：sR 約為纖維含量的線性函數 -> 相對標準不準度隨含量遞減
plot(sR_table$fibre, sR_table$sR, pch = 19, col = "brown",
     main = "粗纖維：再現性標準差與含量的關係",
     xlab = "纖維含量 (% m/m)", ylab = "sR (% m/m)")
fit_sr <- lm(sR ~ fibre, data = sR_table)
abline(fit_sr, col = "red")
# 結論(QUAM A6)：低含量時乾燥條件的固定貢獻 0.115 不可忽略
#   u_c = sqrt(sR^2 + 0.115^2)  (2.5% 樣品)
uc_25 <- sqrt(0.292^2 + 0.115^2)
U_25  <- 2 * uc_25
round(c(uc_25, U_25), 2)     # uc=0.31, U=0.62 (25% of 2.5) 與 QUAM A6.4/A6.5 一致

# 高含量時 sR 主導：U 約 2*0.4=0.8 (5%), 2*0.6=1.2 (10%)
fibre_levels <- c(2.5, 5, 10)
uc_levels <- sqrt(c(0.292, 0.4, 0.6)^2 + 0.115^2)
U_levels  <- 2 * uc_levels
data.frame(fibre = fibre_levels,
           uc = round(uc_levels, 2),
           U  = round(U_levels, 2),
           U_percent = round(U_levels/fibre_levels*100))

# =============== 案例 3：標準曲線內插的不準度 ===============
# QUAM 附錄 E.4 Eq.E3.5：反推濃度的變異數
# var(x_pred) = (S^2/b1^2) * ( 1/p + 1/n + (x_pred - xbar)^2 / Sxx )
#   S  = 迴歸殘差標準差, b1 = 斜率, p = 未知樣品重複測定次數,
#   n  = 校正點數, Sxx = sum((xi-xbar)^2)
# 以鈉標準曲線為例 (ch04 的 Group A 資料)
x <- c(1.0, 3.0, 5.0, 10.0, 20.0)
y <- c(0.050, 0.140, 0.242, 0.521, 0.998)
fit <- lm(y ~ x)
b1 <- coef(fit)[2]
S  <- summary(fit)$sigma          # 殘差標準差
n  <- length(x); p_reps <- 3      # 未知樣品測 3 次
xbar <- mean(x); Sxx <- sum((x - xbar)^2)

y_obs_mean <- 0.555               # 未知樣品 3 次平均發射值
x_pred <- (y_obs_mean - coef(fit)[1]) / b1
var_xpred <- (S^2/b1^2) * (1/p_reps + 1/n + (x_pred - xbar)^2/Sxx)
u_xpred <- sqrt(var_xpred)
c(x_pred = x_pred, u = u_xpred, U_k2 = 2*u_xpred)
# 報告：Na = 11.1 ± 0.4 ug/mL (k=2) 之類的格式

# 畫出「內插濃度的不準度」隨濃度的變化 —— 兩端最寬!
new_x <- seq(1, 20, length = 50)
u_curve <- sapply(new_x, function(xp) {
  sqrt((S^2/b1^2) * (1/p_reps + 1/n + (xp - xbar)^2/Sxx))
})
plot(new_x, 2*u_curve, type = "l", lwd = 2, col = "purple",
     main = "標準曲線反推濃度的 95% 不準度 (k=2)",
     xlab = "濃度 ug/mL", ylab = "±U (ug/mL)")
abline(v = x_pred, lty = 2, col = "grey")

# =============== 案例 1 總複習：完整 GUM 流程 (鎘標準液) ===============
# Step1 measurand: c = 1000*m*P/V
# Step2 sources  : m(重複性+校正), P(證書), V(校正+溫度)
# Step3 quantify : Type A/B -> u(x_i)
m <- 100.28; u_m <- 0.05; P <- 0.9999; u_P <- 0.000058
V <- 100.0;  u_V <- 0.07
c_Cd <- 1000*m*P/V
uc <- c_Cd * sqrt((u_m/m)^2 + (u_P/P)^2 + (u_V/V)^2)
U  <- 2*uc
cat(sprintf("Step4 報告: c(Cd) = (%.1f ± %.1f) mg/L (k=2, 95%%)\n",
            c_Cd, U))

# =============== 期末自我檢核 ===============
# 1. 給你一份 5 重複數據，你會算 mean/SD/CV/95%CI 嗎？(ch01-02)
# 2. 空白 SD=0.003，LOD/LOQ 各是多少？(ch03)
# 3. 標準曲線 r=0.995 能接受嗎？殘差圖看什麼？(ch04)
# 4. n=6 時 Q-test 臨界值多少？(ch05)
# 5. 證書 ±0.15 mL 沒給信賴水準 -> u=? 用什麼分布？(ch07)
# 6. 乘除模型怎麼合成？k=2 代表什麼？(ch08)
# 7. Kragten 法與 Monte Carlo 各解決什麼問題？(ch09)
# 8. 結果 9.8±1.2、限值 10 -> 依保守決策規則如何判定？(ch08)
