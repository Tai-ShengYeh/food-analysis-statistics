# =====================================================================
# 案例④：LC-MS/MS 串聯質譜的量測不確定度
# 情境：電噴灑電離(ESI) LC-MS/MS 測蝦仁中氯黴素 (chloramphenicol)
#       管制界限 (MRPL) = 0.3 ug/kg —— 痕量層級
# LC-MS/MS 特有的三大議題：
#   (1) 基質效應 (離子壓制/增強)  -> Matuszewski 三組實驗
#   (2) 同位素內標 SIL-IS 補償    -> 同位素稀釋
#   (3) 痕量級異質變異            -> 1/x 加權校正
# =====================================================================

# ---------- Part A. Matuszewski 基質效應實驗 ----------
# 文獻來源：Matuszewski, B. K.; Constanzer, M. L.; Chavez-Eng, C. M.
#   Anal. Chem. 2003, 75(13), 3019-3030. DOI: 10.1021/ac020361s
# 三組校正線（波峰面積對濃度的斜率）：
#   A: 溶液標準品 (solvent standard)
#   B: 空白基質萃取「後」添加 (post-extraction spike)
#   C: 添加「後」萃取 (pre-extraction spike)
slope_solvent <- 45200
slope_post    <- 38400
slope_pre     <- 34600

ME <- slope_post / slope_solvent - 1   # 基質效應 (matrix effect)
RE <- slope_pre  / slope_post    - 1   # 萃取回收 (recovery)
PE <- slope_pre  / slope_solvent - 1   # 流程效率 (process efficiency)
round(c(ME = ME, RE = RE, PE = PE), 3)
#> ME=-0.150 (離子壓制15%)  RE=-0.099  PE=-0.235

# 加入同位素內標 (SIL-IS, 氯黴素-d5) 後，用「面積比」做校正線：
s_solvent_is <- 1.020; s_post_is <- 0.980; s_pre_is <- 0.972
round(c(ME_IS = s_post_is/s_solvent_is - 1,
        RE_IS = s_pre_is /s_post_is    - 1), 3)
#> ME_IS=-0.039  RE_IS=-0.008  -> 基質效應從 -15% 縮到 -4%！

# ---------- Part B. 1/x 加權校正：痕量級必備 ----------
# 痕量分析的量測誤差常與濃度成比例 (相對誤差固定)，
# 普通最小平方 (OLS) 會讓高濃度點主宰迴歸 -> 低濃度反推偏倚。
conc  <- c(0.02, 0.05, 0.10, 0.20, 0.50)          # 校正標準品 ug/kg
set.seed(11)
ratio <- 0.001 + 2 * conc + rnorm(5, 0, sqrt(4e-4 * conc))
#                              ^ 變異數與濃度成正比 (比例誤差)

fit_ols <- lm(ratio ~ conc)
fit_w   <- lm(ratio ~ conc, weights = 1 / conc)   # 1/x 加權

# 用「回算濃度」檢查兩種作法在低濃度的偏倚 (%)
backcalc <- function(fit, y) (y - coef(fit)[1]) / coef(fit)[2]
found_ols <- backcalc(fit_ols, ratio)
found_w   <- backcalc(fit_w,   ratio)
data.frame(nominal = conc,
           RE_ols  = round((found_ols/conc - 1) * 100, 1),
           RE_w    = round((found_w  /conc - 1) * 100, 1))
#> 低濃度 (0.02) 處：OLS 的回算誤差明顯大於 1/x 加權

# 未知樣品 (面積比 0.0405) 反推 + Monte Carlo 求不確定度：
y_obs <- 0.0405
x_ols <- backcalc(fit_ols, y_obs)
x_w   <- backcalc(fit_w,   y_obs)
round(c(OLS = x_ols, Weighted = x_w), 3)

set.seed(1); N <- 5000
x_mc <- replicate(N, {
  y_star <- fitted(fit_w) + rnorm(5, 0, sqrt(4e-4 * conc)) # 比例誤差
  bw <- lm(y_star ~ conc, weights = 1/conc)
  backcalc(bw, y_obs)
})
round(c(mean = mean(x_mc), sd = sd(x_mc),
        CI_low = quantile(x_mc, .025), CI_high = quantile(x_mc, .975)), 3)
#> 加權反推的 95% 區間 —— 直接由模擬取得，不需加權偏微分公式

# ---------- Part C. 不確定度預算 (內部驗證法, SANTE 風格) ----------
# 成分                    相對標準不確定度   來源
rel <- c(
  precision   = 0.22,   # 中間精密度：不同天/人/校正週期的驗證數據
  cal_matrix  = 0.08,   # 校正+基質殘餘：SIL-IS + 基質匹配校正後的殘餘
  recovery    = 0.06,   # 回收率偏倚：加標回收 90%，平均值的標準誤
  homogeneity = 0.15    # 樣品均勻性：痕量污染物在組織中的分布
)
rel_uc <- sqrt(sum(rel^2))
round(rel_uc, 3)                        #> 0.284

# 數值例：儀器 (同位素稀釋) 讀值 0.19 ug/kg，回收率修正
raw <- 0.19; Rec <- 0.90
result <- raw / Rec                     #> 0.211 ug/kg
U <- 2 * rel_uc * result
sprintf("氯黴素 = (%.2f ± %.2f) ug/kg (k=2)", result, U)
#> "氯黴素 = (0.21 ± 0.12) ug/kg (k=2)"

# 變異數占比：精密度 60% > 均勻性 28% > 校正 8% > 回收率 4%
pct <- rel^2 / sum(rel^2) * 100
round(sort(pct, decreasing = TRUE), 1)

# ---------- Part D. 符合性判定與決策支持 ----------
MRL <- 0.3
judge <- if (result - U > MRL) "不符合" else
         if (result + U <= MRL) "符合" else "灰色地帶"
judge                                   #> 0.21+0.12=0.33 > 0.3 -> 灰色地帶

# Monte Carlo 決策支持：「真值超過限量的機率有多大？」
set.seed(2)
sim <- rnorm(200000, result, rel_uc * result)
mean(sim > MRL)                         #> 約 0.07 -> 超標機率 ~7%

# ---------- 附：SANTE 定性確認準則 (與定量不確定度互補) ----------
ion_ratio_sample   <- 0.85   # 兩支離子對的面積比 (樣品)
ion_ratio_standard <- 0.95   # 標準品的離子比
tol <- 0.30 * ion_ratio_standard      # SANTE 容許差 ±30% (相對)
ion_ratio_sample > ion_ratio_standard - tol &&
ion_ratio_sample < ion_ratio_standard + tol     #> TRUE -> 離子比合格
# 滯留時間差 |5.42 - 5.40| = 0.02 min < 0.1 min -> 合格
# 定性「確認」成立，才輪得到上面的定量不確定度登場！
