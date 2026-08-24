# =====================================================================
# Ch09 進階：Kragten 試算表法 與 Monte Carlo 模擬
# (QUAM 2012 附錄 E.2, E.3) — 以 QUAM Example A1 鎘標準液為例
# =====================================================================

# ---------- 0. 案例：配製鎘標準溶液 ----------
# c(Cd) = 1000 * m * P / V   [mg/L]
#   m = 100.28 mg  (u = 0.05 mg)
#   P = 0.9999     (u = 0.000058，證書純度)
#   V = 100.0 mL   (u = 0.07 mL，含校正+溫度效應)
m <- 100.28; u_m <- 0.05
P <- 0.9999; u_P <- 0.000058
V <- 100.0;  u_V <- 0.07

conc <- function(m, P, V) 1000 * m * P / V
c_Cd <- conc(m, P, V)
round(c_Cd, 1)                 # -> 1002.7 mg/L（與 QUAM Table A1.1 一致）

# ---------- 1. 方法一：解析法 (Rule 2 相對合成) ----------
rel_uc <- sqrt((u_m/m)^2 + (u_P/P)^2 + (u_V/V)^2)
uc_analytic <- c_Cd * rel_uc
round(uc_analytic, 2)          # -> 0.86 ~ 0.9 mg/L

# 各成分貢獻 |dy/dxi|*u(xi)
contrib <- c(
  mass    = c_Cd * u_m / m,
  purity  = c_Cd * u_P / P,
  volume  = c_Cd * u_V / V)
round(contrib, 3)              # 體積貢獻最大！

barplot(contrib, col = c("tomato","gold","steelblue"),
        main = "不準度預算 (uncertainty budget)",
        ylab = "|u(y,x_i)| (mg/L)", las = 1)

# ---------- 2. 方法二：Kragten 數值微分法 ----------
# 原理：把每個輸入量輪流加上自己的 u(xi)，重算 y，
#       y 的變化量就是該成分的貢獻 (相當於試算表的 Kragten 表)
kragten <- function(f, x_list, u_list) {
  y0 <- f(x_list)                       # 名義結果
  contrib <- sapply(seq_along(x_list), function(i) {
    xi <- x_list; xi[[i]] <- xi[[i]] + u_list[[i]]
    f(xi) - y0                          # 有號差 -> 取絕對值
  })
  uc <- sqrt(sum(contrib^2))
  list(y0 = y0, contributions = contrib, uc = uc)
}

res_k <- kragten(function(x) conc(x$m, x$P, x$V),
                 list(m = m, P = P, V = V),
                 list(u_m, u_P, u_V))
round(res_k$contributions, 3)          # 與解析法幾乎相同!
round(res_k$uc, 2)

# ---------- 3. 方法三：Monte Carlo 模擬 (GUM Supplement 1) ----------
# 把每個輸入量視為「分布」，隨機抽樣 N 次，算出 N 個可能的 y，
# 直接用 y 的分布敘述不準度 —— 完全不需要偏微分！
set.seed(2024)
N <- 100000
m_sim <- rnorm(N, m, u_m)      # Type A/常態來源用常態抽樣
P_sim <- rnorm(N, P, u_P)      # 證書資訊以常態近似（也可用矩形分布）
V_sim <- rnorm(N, V, u_V)

y_mc <- conc(m_sim, P_sim, V_sim)

hist(y_mc, breaks = 100, col = "lightblue", freq = FALSE,
     main = "Monte Carlo：100000 次虛擬配製的 c(Cd) 分布",
     xlab = "c(Cd) mg/L", ylab = "密度")
abline(v = c_Cd, col = "red", lwd = 2)             # GUM 點估計

mc_mean <- mean(y_mc)
mc_interval <- quantile(y_mc, c(0.025, 0.975))
round(mc_interval, 1)          # 95% 涵蓋區間
sd(y_mc)                       # MC 的標準不準度 ~ 解析法 uc

# 三種方法比較
cat(sprintf("解析法   : %.3f mg/L\n", uc_analytic))
cat(sprintf("Kragten  : %.3f mg/L\n", res_k$uc))
cat(sprintf("MonteCarlo SD : %.3f mg/L\n", sd(y_mc)))
cat(sprintf("MC 95%% 區間 : [%.1f, %.1f]\n",
            mc_interval[1], mc_interval[2]))

# ---------- 4. 什麼時候該用 Monte Carlo？ ----------
# - 模型高度非線性（解析法線性假設失效）
# - 分布明顯不對稱（如接近 0 的回收率、低濃度計數）
# - 想直接拿到「涵蓋區間」而不糾結有效自由度 k
