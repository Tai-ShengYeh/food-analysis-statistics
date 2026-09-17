# =====================================================================
# Ch04 標準曲線與線性迴歸 (Nielsen 4.4)
# lm() 最小平方法 / r 與 r^2 / 殘差 / 信賴帶 / 反推未知濃度
# =====================================================================

# ---------- 1. 資料：原子發射光譜測鈉的標準曲線 ----------
# Nielsen 章末習題 4 Group A：濃度 x (ug/mL) vs 發射值 y (589 nm)
x <- c(1.0, 3.0, 5.0, 10.0, 20.0)
y <- c(0.050, 0.140, 0.242, 0.521, 0.998)

plot(x, y, pch = 19, col = "steelblue",
     main = "鈉標準曲線 (Group A)",
     xlab = "濃度 (ug/mL)", ylab = "發射訊號")

# ---------- 2. 最小平方迴歸：lm(y ~ x) ----------
fit <- lm(y ~ x)
fit
# y = a*x + b -> R 報告 (Intercept)=b 截距，斜率 x 的係數=a
# 預期結果：y = 0.0504*x - 0.0029（Nielsen 習題解答）

slope <- coef(fit)[2]; intercept <- coef(fit)[1]
abline(fit, col = "red", lwd = 2)          # 把迴歸線畫上去

# 判定係數 r^2 與相關係數 r
summary(fit)$r.squared        # -> 0.9990（課本 r^2=0.9990）
cor(x, y)                     # r = +0.9995
# 分析化學經驗法則：標準曲線 r >= 0.997 才算理想

# ---------- 3. 殘差圖：目視檢查直線假設 ----------
resid_df <- data.frame(x = x,
                       residual = residuals(fit))
print(resid_df)               # 每一點離直線的垂直距離
plot(resid_df$x, resid_df$residual, pch = 19, col = "darkorange",
     main = "殘差圖", xlab = "濃度", ylab = "殘差")
abline(h = 0, lty = 2)
# 殘差應隨機散布在 0 附近；若出現彎曲趨勢 => 該用曲線擬合

# ---------- 4. 反推未知樣品濃度 ----------
# 未知樣品發射值 y_obs = 0.555 -> x_pred = (y - b) / a
y_obs <- 0.555
x_pred <- (y_obs - intercept) / slope
round(x_pred, 1)              # -> 11.1 ug/mL（Nielsen 解答）

# ---------- 5. 迴歸的信賴帶 (confidence band) ----------
new_x <- seq(1, 20, length.out = 100)
pred_ci <- predict(fit, newdata = data.frame(x = new_x),
                   interval = "confidence", level = 0.95)
# 重畫校正曲線散佈圖與迴歸線，讓信賴帶疊在正確的圖上（而不是疊在上面的殘差圖）
plot(x, y, pch = 19, col = "steelblue",
     main = "鈉標準曲線與 95% 信賴帶",
     xlab = "濃度 (ug/mL)", ylab = "發射訊號")
abline(fit, col = "red", lwd = 2)
matplot(new_x, pred_ci[, c("lwr","upr")], type = "l", lty = 2,
        col = "grey40", add = TRUE)   # 虛線即 95% 信賴帶
points(x, y, pch = 19); abline(fit, col="red")
# 特性：信賴帶在「平均濃度處」最窄，往兩端變寬
#       所以未知樣品濃度最好落在標準曲線中段！

# 外插警告：不要用範圍外的直線外推 (extrapolation)
# 高濃度可能進入飽和區、低濃度可能偏離原點

# ---------- 6. 咖啡因 HPLC 曲線：反推與練習 ----------
# Nielsen Fig 4.4：咖啡因標準曲線 y(peak area) = 89.994x + 90.727, r^2=0.9989
# 未知咖啡樣品 peak area = 4000 ->
(4000 - 90.727) / 89.994      # -> 43.44 ppm 咖啡因

# 用 R 對自己的資料做同樣的事：
# conc  <- c(...)   # 你的標準品濃度
# area  <- c(...)   # 對應波峰面積
# fit2  <- lm(area ~ conc)
# (unknown_area - coef(fit2)[1]) / coef(fit2)[2]

# ---------- 7. 寬濃度範圍：加權最小平方法 (WLS) ----------
# OLS = ordinary least squares，普通最小平方法：所有點的權重都是 1。
# WLS = weighted least squares，加權最小平方法：不同點可有不同權重。
#
# 當高濃度的殘差散布明顯大於低濃度時，稱為異方差
# (heteroscedasticity)。寬範圍常出現這個現象，但「範圍大」本身
# 不是自動加權的理由；仍要用殘差、回算偏差與驗證樣品判斷。
#
# WLS 最小化 sum[w_i * (y_i - yhat_i)^2]
#   w_i    = 第 i 點的權重
#   y_i    = 實際訊號
#   yhat_i = 模型預測訊號
# 理想上 w_i 約等於 1/s_i^2，其中 s_i^2 是該濃度層級的變異數。

# HPLC 咖啡因示例：5 個濃度，每個濃度做 3 次標準品
conc <- rep(c(1, 5, 10, 50, 100), each = 3)
area <- c(101, 99, 102,
          498, 505, 492,
          1005, 992, 1018,
          4930, 5070, 5005,
          9720, 10380, 10040)

# 診斷：每個濃度 3 次重複的 SD，是不是隨濃度一路變大？
round(tapply(area, conc, sd), 1)

# 三個候選模型：不加權、1/x、1/x^2
fit_ols <- lm(area ~ conc)
fit_1x  <- lm(area ~ conc, weights = 1 / conc)
fit_1x2 <- lm(area ~ conc, weights = 1 / conc^2)

coef(fit_ols)
coef(fit_1x)
coef(fit_1x2)

# 反推每筆標準品濃度，計算各濃度的平均回算偏差 (%)
backcalc <- function(fit) {
  (area - coef(fit)[1]) / coef(fit)[2]
}

bias_table <- data.frame(
  conc = conc,
  OLS = 100 * (backcalc(fit_ols) - conc) / conc,
  WLS_1x = 100 * (backcalc(fit_1x) - conc) / conc,
  WLS_1x2 = 100 * (backcalc(fit_1x2) - conc) / conc
)
print(aggregate(. ~ conc, data = bias_table, FUN = mean))

# 圖 1：若 OLS 殘差隨預測訊號張開，表示等變異假設可能不合適。
# 圖 2：WLS 要看 sqrt(weight) * residual 的加權殘差。
par(mfrow = c(1, 2))
plot(fitted(fit_ols), residuals(fit_ols), pch = 19,
     xlab = "預測訊號", ylab = "殘差", main = "OLS")
abline(h = 0, lty = 2)
plot(fitted(fit_1x2), sqrt(1 / conc^2) * residuals(fit_1x2), pch = 19,
     xlab = "預測訊號", ylab = "加權殘差", main = "WLS: 1/x^2")
abline(h = 0, lty = 2)
par(mfrow = c(1, 1))

# 補充：三個模型的 r^2 幾乎一樣 -> 不能用 r^2 選權重
round(sapply(list(OLS = fit_ols, WLS_1x = fit_1x, WLS_1x2 = fit_1x2),
             function(f) summary(f)$r.squared), 4)

# 選權重時，應比較：
# 1. 殘差是否仍有濃度相關趨勢或漏斗形。
# 2. 每一濃度的回算偏差或回收率是否符合預設允收標準。
# 3. 獨立品管與驗證樣品在整個工作範圍是否通過。
# 不要只選 r^2 最高的模型。
#
# 注意：x = 0 的空白無法直接使用 1/x 或 1/x^2。
#       1/s^2 需要每個濃度有足夠重複，否則 s^2 可能很不穩定。

stopifnot(all(is.finite(c(coef(fit_ols), coef(fit_1x), coef(fit_1x2)))))
