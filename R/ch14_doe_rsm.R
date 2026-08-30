# =====================================================================
# Ch14 實驗設計與反應曲面法 (DOE & RSM)
# 情境：超音波輔助萃取 (UAE) 茶葉多酚，反應值 = DPPH 清除率 (%)
# 因子 (編碼單位 ±1)：
#   A 乙醇濃度  50 ± 10 %   (即 40~60%)
#   B 萃取溫度  50 ± 10 °C  (即 40~60°C)
#   C 超音波時間 22.5 ± 7.5 min (即 15~30 min)
# 學習路徑：
#   Part 1  2^3 全因子 + 中心點 (base R) -> 主效應/交互作用/曲率偵測
#   Part 2  中心複合設計 CCD (base R)    -> 二階模型/駐點/等高線
#   Part 3  預測區間與驗證實驗 (呼應 Ch2/Ch8)
#   Part 4  套件選讀：rsm / FrF2 / desirability (需安裝，見 HAVE_PKGS)
# 參考：Lenth (2009) rsm, J. Stat. Software 32:7；
#       Tanaka & Amaliah (2022) arXiv:2206.07532 (DoE 套件總體檢)
# =====================================================================

HAVE_PKGS <- FALSE   # 改 TRUE 前先 install.packages(c("rsm","FrF2","desirability"))

# ---------- 共用：真實模型 (教學模擬用，學生實作時以實驗數據取代) ----------
# 真實世界存在一個「內部極大值」—— 這正是需要 RSM 的原因
true_y <- function(A, B, C)                       # 編碼單位
  60 + 5*A + 3*B + 2*C - 7*A^2 - 5*B^2 - 6*C^2 + 2.5*A*B

# =====================================================================
# Part 1. 2^3 全因子設計 + 4 個中心點
# =====================================================================
fac <- expand.grid(A = c(-1, 1), B = c(-1, 1), C = c(-1, 1))   # 8 個處理組合
set.seed(14)
fac$y <- round(true_y(fac$A, fac$B, fac$C) + rnorm(8, 0, 1.2), 1)
ctr <- data.frame(A = 0, B = 0, C = 0,
                  y = round(rnorm(4, true_y(0, 0, 0), 1.2), 1))  # 中心點
dat1 <- rbind(fac, ctr)
dat1                                                   # 設計矩陣長這樣

# --- 1a. 配一階+交互作用模型，讀出效應 ---
fit1 <- lm(y ~ (A + B + C)^2, data = dat1)
round(coef(fit1), 2)
#> 效應(effect) = 2*係數。A(乙醇) 最大，A:B 交互作用明顯
#> 注意：模型截距 ~48.8 (因子點平均)，但中心點「實測」平均 ~60.2 —— 差很多！

# --- 1b. 交互作用圖：兩線不平行 = 有交互作用 ---
interaction.plot(dat1$A, dat1$B, dat1$y, type = "b", pch = c(1, 19),
                 col = c("#1565C0", "#C62828"), lwd = 2,
                 xlab = "乙醇濃度 A (編碼)", ylab = "DPPH 清除率 (%)",
                 trace.label = "溫度 B",
                 main = "2^3 因子實驗：A×B 交互作用與中心點曲率")

# --- 1c. 曲率檢定：中心點平均 vs 因子點平均 ---
mean_fac <- mean(fac$y); mean_ctr <- mean(ctr$y)
s_pure   <- sd(ctr$y)                       # 純誤差 (只有中心點重複能給)
t_curv <- (mean_ctr - mean_fac) / (s_pure * sqrt(1/4 + 1/8))
round(c(mean_factorial = mean_fac, mean_center = mean_ctr,
        s_pure = s_pure, t_curv = t_curv,
        p_value = 2 * pt(-abs(t_curv), df = 3)), 4)
#> p 值極小 -> 「反應曲面是彎的！」直線模型不夠用 -> 需要 RSM (Part 2)

# =====================================================================
# Part 2. 中心複合設計 (CCD)：因子點 + 軸點 + 中心點
# =====================================================================
# 旋轉性(rotatable)設計的 alpha = (2^k)^(1/4)；k=3 -> 1.682
# 旋轉性 = 預測變異數在「等半徑」處相等，不偏向任何方向
alpha <- 2^(3/4)
round(alpha, 3)                                          #> 1.682
axi <- data.frame(A = c(-alpha, alpha, rep(0, 4)),
                  B = c(0, 0, -alpha, alpha, 0, 0),
                  C = c(0, 0, 0, 0, -alpha, alpha))
ccd <- rbind(fac[, c("A", "B", "C")], axi,
             data.frame(A = 0, B = 0, C = 0)[rep(1, 6), ])   # 8+6+6 = 20 runs
set.seed(15)
ccd$y <- round(true_y(ccd$A, ccd$B, ccd$C) + rnorm(20, 0, 1.2), 1)

# --- 2a. 二階模型：線性 + 雙因子交互 + 三個平方項 ---
fit2 <- lm(y ~ (A + B + C)^2 + I(A^2) + I(B^2) + I(C^2), data = ccd)
round(coef(fit2), 2)
#> 平方項係數全為負 -> 開口朝下 -> 存在極大值 (呼應曲率檢定的結論)

# --- 2b. 矩陣代數找駐點：x0 = -0.5 * B^-1 * b ---
# ŷ = b0 + x'b + x'Bx (B 對角線放平方項、非對角線放交互係數的一半)
b    <- coef(fit2)
blin <- b[c("A", "B", "C")]
Bmat <- matrix(c(b["I(A^2)"], b["A:B"]/2,  b["A:C"]/2,
                 b["A:B"]/2,  b["I(B^2)"], b["B:C"]/2,
                 b["A:C"]/2,  b["B:C"]/2,  b["I(C^2)"]), 3, byrow = TRUE)
x0 <- as.numeric(-0.5 * solve(Bmat, blin))     # 駐點 (編碼單位)
eigen(Bmat)$values                            # 三個特徵值全負 -> 極大值
y0 <- as.numeric(b[1] + t(x0) %*% blin + t(x0) %*% Bmat %*% x0)
round(c(A = x0[1], B = x0[2], C = x0[3], DPPH_pred = y0), 2)
#> 駐點約 (0.4, 0.4, 0.2)，預測 DPPH ~ 62% —— 與真實模型幾乎一致！

# --- 2c. 換回實際單位 (這才是操作員要的答案) ---
unc <- c(乙醇濃度 = 50 + 10 * x0[1],          # %
         萃取溫度 = 50 + 10 * x0[2],          # °C
         超音波時間 = 22.5 + 7.5 * x0[3])     # min
round(unc, 1)

# --- 2d. 等高線圖：A-B 平面 (固定 C 在駐點) ---
gA <- seq(-1.7, 1.7, length.out = 60)
gB <- seq(-1.7, 1.7, length.out = 60)
grid <- expand.grid(A = gA, B = gB)
grid$C <- x0[3]
grid$yhat <- as.numeric(predict(fit2, grid))
contour(50 + 10 * gA, 50 + 10 * gB,
        matrix(grid$yhat, nrow = length(gA)),
        xlab = "乙醇濃度 (%)", ylab = "萃取溫度 (°C)",
        main = sprintf("RSM 等高線 (超音波時間 = %.1f min)", unc[3]),
        col = "#455A64", lwd = 1.5)
points(unc[1], unc[2], pch = 19, col = "red", cex = 1.6)
text(unc[1], unc[2], sprintf(" 最適 (預測 %.1f%%)", y0),
     col = "red", adj = 0, font = 2)

# =====================================================================
# Part 3. 預測區間與驗證實驗 (呼應 Ch2 的 CI 與 Ch8 的符合性思維)
# =====================================================================
newp  <- data.frame(A = x0[1], B = x0[2], C = x0[3])
pred  <- predict(fit2, newp, interval = "prediction")
round(pred, 1)
#> 報告寫法：「在最適條件下，DPPH 清除率預期 (下限~上限)%」—— 單點預測必附區間！

set.seed(16)
verify <- round(true_y(x0[1], x0[2], x0[3]) + rnorm(3, 0, 1.2), 1)
verify                                    # 模擬「照最適條件重做 3 次」
verdict <- if (mean(verify) >= pred[2] && mean(verify) <= pred[3])
  "驗證通過：實測落在 95% 預測區間內" else "驗證失敗：模型需重新檢討"
verdict

# =====================================================================
# Part 4. 套件選讀：業界標準做法 (HAVE_PKGS <- TRUE 時執行)
# =====================================================================
if (HAVE_PKGS) {
  # install.packages(c("rsm", "FrF2", "desirability"))
  library(rsm)      # Lenth (2009) JSS 32:7 —— RSM 教學與實務的標準套件
  fit_rsm <- rsm(y ~ SO(A, B, C), data = ccd)   # SO = second-order
  summary(fit_rsm)$canonical     # 駐點 + 特徵值 + 特徵向量 (canonical 分析)
  steepest(fit_rsm)              # 最陡上升路徑表 (Part 1 之後的下一步)
  contour(fit_rsm, ~ A + B, image = TRUE)       # 一行畫出等高線+填色

  library(FrF2)     # Grömping (2014) JSS 56:1 —— 2 水準部分因子/篩選設計
  FrF2(8, 4, randomize = FALSE)   # 2^(4-1) 解析度 IV 半因子：4 因子只做 8 run
  pb(12, 5)                       # Plackett-Burman 12 runs 篩 5 個變因

  library(desirability)  # 多反應同時最佳化：產率最高 & 乙醇消耗最少
  d1 <- dMax(40, 65)     # DPPH：40% 最差、65% 最好
  d2 <- dMin(30, 60)     # 溶劑用量：越少越好
  # 將各反應的 desirability 幾何平均後，在等高線上找 D 最大的點
}

# ---------- 小結與延伸練習 ----------
cat("
練習 1：把 I(C^2) 從模型移除，駐點與預測值怎麼變？(提示：C 的曲率本來就較弱)
練習 2：alpha 改成 1 (face-centered CCD，軸點貼在邊界) 重跑 Part 2，
        預測區間變寬還是變窄？為什麼？(提示：旋轉性沒了)
練習 3：用 cranlogs 套件抓 ExperimentalDesign 任務視圖套件的下載量，
        重現 Tanaka & Amaliah (2022) 的 Lorenz curve 與 Gini index。
")
