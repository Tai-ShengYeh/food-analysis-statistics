# 食品分析數據品管統計與量測不確定度 — 課程手冊（R 語言版）

> 本手冊收錄全課程 **16 支 R 程式**。每支程式皆可直接複製到 R / RStudio 執行，
> 或從本頁對應的 .R 檔下載。教學內容請開啟各章 HTML 網頁。

**教材依據**
- Nielsen's Food Analysis, 4th Ed., Chapter 4: *Evaluation of Analytical Data* (J. S. Smith)
- EURACHEM/CITAC Guide CG 4, *Quantifying Uncertainty in Analytical Measurement*, QUAM:2012.P1 (3rd ed.)

## 目錄

| 章 | 教學網頁 | R 檔案 |
|---|---|---|
| Ch1 統計入門：平均數、標準差與變異係數 | [ch01.html](ch01.html) | [ch01_basics.R](R/ch01_basics.R) |
| Ch2 常態分配與信賴區間 | [ch02.html](ch02.html) | [ch02_ci_normal.R](R/ch02_ci_normal.R) |
| Ch3 方法能力指標與品質管制圖 (LOD/LOQ/管制圖) | [ch03.html](ch03.html) | [ch03_method_qc.R](R/ch03_method_qc.R) |
| Ch4 標準曲線與線性迴歸 | [ch04.html](ch04.html) | [ch04_regression.R](R/ch04_regression.R) |
| Ch5 有效數字與異常值檢定 (Q 檢定 / Grubbs) | [ch05.html](ch05.html) | [ch05_outliers_sigfig.R](R/ch05_outliers_sigfig.R) |
| Ch6 量測不確定度：概念與 GUM 四步驟 | [ch06.html](ch06.html) | [ch06_uncertainty_concept.R](R/ch06_uncertainty_concept.R) |
| Ch7 Type A/B 分布轉換 | [ch07.html](ch07.html) | [ch07_typeAB_distributions.R](R/ch07_typeAB_distributions.R) |
| Ch7 實戰案例(1)：分析天平稱量 | [ch07.html](ch07.html) | [case_balance.R](R/case_balance.R) |
| Ch8 合成與擴展不確定度、報告與符合性 | [ch08.html](ch08.html) | [ch08_combine_report.R](R/ch08_combine_report.R) |
| Ch9 Kragten 試算表法與 Monte Carlo | [ch09.html](ch09.html) | [ch09_kragten_montecarlo.R](R/ch09_kragten_montecarlo.R) |
| Ch10 實戰案例(2)：NaOH 標定滴定 (QUAM Example A2) | [ch10.html](ch10.html) | [case_titration.R](R/case_titration.R) |
| Ch10 實戰案例(3)：HPLC/GC 農藥殘留 (QUAM Example A4) | [ch10.html](ch10.html) | [case_hplc.R](R/case_hplc.R) |
| Ch11 綜合案例：粗纖維 (A6) 與標準曲線反推不確定度 (E.4) | [ch11.html](ch11.html) | [ch11_capstone.R](R/ch11_capstone.R) |
| Ch12 進階案例(4)：LC-MS/MS 氯黴素 (基質效應/SIL-IS/加權校正) | [ch12.html](ch12.html) | [case_lcmsms.R](R/case_lcmsms.R) |
| 附錄：本站全部教學圖表繪圖程式 | — | [R/figures.R](R/figures.R) |

## 如何使用

1. 安裝 [R](https://cran.r-project.org) 與 [RStudio](https://posit.co/downloads)（皆免費）
2. 開新腳本（Ctrl+Shift+N），貼上任一節程式碼
3. Ctrl+Enter 逐行執行、Ctrl+Alt+R 整段執行
4. 全部範例只用 R 內建函數，**不需安裝任何套件**
5. 建議學習順序：Ch1 → Ch11（章章相扣，案例貫穿）

---

## Ch1 統計入門：平均數、標準差與變異係數

📄 檔案：`ch01_basics.R` ｜ 教學網頁：[ch01.html](ch01.html)

```r
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
```

---

## Ch2 常態分配與信賴區間

📄 檔案：`ch02_ci_normal.R` ｜ 教學網頁：[ch02.html](ch02.html)

```r
# =====================================================================
# Ch02 常態分配、標準誤與信賴區間 (Nielsen 4.3.1 後半)
# 學習目標：68-95-99.7 法則 / Z 值與 t 值 / 信賴區間 CI 的計算
# =====================================================================

# ---------- 1. 常態分配：68-95-99.7 法則 ----------
# 大多數隨機量測誤差服從常態分配（鐘形曲線）
#   ±1 SD 內約 68% 的數據
#   ±2 SD 內約 95%
#   ±3 SD 內約 99.7%
# R 可以用 pnorm() 直接算「小於某值的機率」

pnorm(1) - pnorm(-1)    # P(-1SD < X < +1SD)  -> 0.6827 (68%)
pnorm(2) - pnorm(-2)    # -> 0.9545 (95%)
pnorm(3) - pnorm(-3)    # -> 0.9973 (99.7%)

# ---------- 2. Z 值：大樣本(n>30)時的信賴區間 ----------
# CI = x_bar ± Z * SD / sqrt(n)
# Nielsen Table 4.2：信心水準對應 Z 值
#   80%->1.29, 90%->1.64, 95%->1.96, 99%->2.58, 99.9%->3.29
# R 用 qnorm(p) 可反查（p = 中央面積）
qnorm(0.80 + 0.10)      # 1.2816 ~ 1.29
qnorm(0.90 + 0.05)      # 1.6449 ~ 1.64
qnorm(0.95 + 0.025)     # 1.9600 = 1.96
qnorm(0.99 + 0.005)     # 2.5758 ~ 2.58

# 課本範例：假設水分測了 25 次，x_bar=64.72, SD=0.2927
n_big <- 25; xbar <- 64.72; s <- 0.2927
ci_z <- xbar + c(-1, 1) * qnorm(0.975) * s / sqrt(n_big)
round(ci_z, 2)          # -> 64.60  64.84，即 64.72 ± 0.115%

# 標準誤 (Standard Error of the Mean, SEM)
sem <- s / sqrt(n_big)
sem                     # 平均數的「不準度」，n 越大 SEM 越小

# ---------- 3. t 值：小樣本(n<30)才是食品分析的日常 ----------
# 分析通常只做 3~5 次重複，必須用 t 分布代替常態
# CI = x_bar ± t * SD / sqrt(n)，df = n - 1
# R 用 qt(p, df) 反查 t 值表（Nielsen Table 4.3）
qt(0.975, 1)   # df=1, 95% -> 12.706（課本 12.7）
qt(0.975, 2)   # -> 4.303（課本 4.30）
qt(0.975, 3)   # -> 3.182（課本 3.18）
qt(0.975, 9)   # -> 2.262（課本 2.26）

# 回到真正的 4 次水分測定
moisture <- c(64.53, 64.45, 65.10, 64.78)
xbar <- mean(moisture); s <- sd(moisture); n <- length(moisture)
t_crit <- qt(0.975, df = n - 1)         # 3.182
half_width <- t_crit * s / sqrt(n)
half_width                              # -> 0.4646（課本 0.465）
c(xbar - half_width, xbar + half_width) # 65.185 ~ 64.255

cat(sprintf("95%% CI = %.2f ± %.3f %%", xbar, half_width))

# ---------- 4. 模擬實驗：親眼看看「重複抽樣」 ----------
# 我們模擬「每次抽 n=4 個樣本算平均」1000 次，
# 看看 95% CI 是否真的蓋住真實平均值約 95 次/100 次
set.seed(2024)                    # 設定亂數種子讓結果可重現
true_mu <- 65.05                  # 假設的真值 (%)
hits <- 0                         # 計數：CI 有蓋住真值的次數
for (i in 1:1000) {
  samp <- rnorm(4, mean = true_mu, sd = 0.293)  # 抽 4 個樣本
  ci <- mean(samp) + c(-1, 1) * qt(0.975, 3) * sd(samp)/sqrt(4)
  if (true_mu >= ci[1] && true_mu <= ci[2]) hits <- hits + 1
}
hits / 1000        # 大約 0.94~0.96，證明「95% 信心」不是口號！

# n 越大，CI 越窄（更精確）— 試著把 n 改成 16 再跑一次：
n <- 16
samp <- rnorm(n, mean = true_mu, sd = 0.293)
mean(samp) + c(-1,1) * qt(0.975, n-1) * sd(samp)/sqrt(n)

# ---------- 5. 小結 ----------
# 報告結果的專業寫法：平均值 ± 半寬 (信心水準)
cat(sprintf("水分含量 = %.2f ± %.2f %% (95%%, n=%d)",
            xbar, half_width, n))
```

---

## Ch3 方法能力指標與品質管制圖 (LOD/LOQ/管制圖)

📄 檔案：`ch03_method_qc.R` ｜ 教學網頁：[ch03.html](ch03.html)

```r
# =====================================================================
# Ch03 方法評估指標與品質管制圖 (Nielsen 4.3.3~4.3.5)
# LOD / LOQ / MDL、靈敏度與專一性、Shewhart 與 CuSum 管制圖
# =====================================================================

# ---------- 1. 偵測極限 LOD 與定量極限 LOQ ----------
# LOD = 空白訊號平均值 + 3 * 空白標準差   (Nielsen 式 4.19)
# LOQ = 空白訊號平均值 + 10 * 空白標準差
# 模擬：對空白樣品(不含分析物)測 20 次，儀器讀值如下 (mg/L)
set.seed(42)
blank <- round(rnorm(20, mean = 0.008, sd = 0.0022), 4)

x_blk <- mean(blank); s_blk <- sd(blank)
LOD <- x_blk + 3 * s_blk
LOQ <- x_blk + 10 * s_blk
round(c(blank_mean = x_blk, blank_sd = s_blk, LOD = LOD, LOQ = LOQ), 4)

# 解讀：低於 LOD -> 「測不到」；高於 LOQ 才能可靠「報數字」
# 中間地帶 (LOD~LOQ) 只能定性不能精準定量

# 另一個常用定義：儀器的訊噪比 S/N >= 3 為偵測極限

# ---------- 2. 方法偵測極限 MDL (EPA 定義, 進階) ----------
# 將含分析物的基質樣品重複分析 n 次(n>=7)，MDL = t(n-1, 0.99) * SD
spiked <- c(1.02, 0.98, 1.05, 0.99, 1.01, 0.97, 1.03)  # 7 次加標樣品
n <- length(spiked)
mdl <- qt(0.99, n - 1) * sd(spiked)
round(mdl, 3)      # -> 約 0.068 mg/L（涵蓋整個方法流程的變異）

# ---------- 3. Shewhart 管制圖 ----------
# 情境：實驗室每天用標準品(蛋白質 12.0%)監控方法是否穩定
set.seed(7)
qc_days <- 1:25
qc_value <- round(rnorm(25, mean = 12.00, sd = 0.15), 3)
# 人為加入兩個異常事件：第10天偏高(系統性漂移)、第18天爆表
qc_value[8:11] <- qc_value[8:11] + 0.28     # 小漂移
qc_value[18]   <- 12.62                     # 超過行動界限

target <- 12.00
cl    <- target                              # 中心線 CL
uwl <- target + 2*0.15; lwl <- target - 2*0.15   # 警告界限 ±2s
ual <- target + 3*0.15; lal <- target - 3*0.15   # 行動界限 ±3s

plot(qc_days, qc_value, type = "b", pch = 19, col = "steelblue",
     ylim = c(target-0.75, target+0.75),
     main = "Shewhart 管制圖：蛋白質 QC 標準品",
     xlab = "分析日", ylab = "測值 (%)")
abline(h = c(cl, uwl, lwl, ual, lal),
       col = c("black","orange","orange","red","red"), lty = c(1,2,2,2,2))
legend("bottomright", c("CL","±2s 警告","±3s 行動"),
       col=c("black","orange","red"), lty=c(1,2,2), cex=0.8)

# 自動找出失控點
out_of_control <- qc_value[qc_value > ual | qc_value < lal]
out_of_control          # 第10與18天超出 ±3s 行動界限（漂移累積+爆表）
which(qc_value > ual | qc_value < lal)

# 判讀口訣：
#  - 點超出 ±3s 或連續規則違反 -> 停下來找根本原因(root cause)
#  - 連續 7 點同側 / 連續上升下降 -> 有系統性變因

# ---------- 4. CuSum 累積和管制圖 (偵測微小漂移更靈敏) ----------
csum <- cumsum(qc_value - target)
plot(qc_days, csum, type = "b", pch = 19, col = "darkgreen",
     main = "CuSum 管制圖",
     xlab = "分析日", ylab = "累積偏差 (CuSum)")
abline(h = 0, lty = 2)
# 解讀：第 8~11 天的 +0.28 漂移在 Shewhart 圖上只是「靠近警告線」，
# 但 CuSum 的斜率明顯轉正 —— 小而持續的偏移無所遁形。

# ---------- 5. 其他日常 QC 手段（名詞認識）----------
# 空白試驗 blank        : 抓污染與背景干擾
# 加標回收 recovery     : (加標測值-原測值)/添加量*100%，通常要求 80~120%
recovery <- function(spike_total, native, added) {
  (spike_total - native) / added * 100
}
recovery(spike_total = 9.6, native = 5.1, added = 5.0)   # 90% 合格

# 重複樣品 replicate     : 同一樣品平行測定，看 RSD
# 查核樣品/CRM           : 用已知濃度標準物質確認準確度
```

---

## Ch4 標準曲線與線性迴歸

📄 檔案：`ch04_regression.R` ｜ 教學網頁：[ch04.html](ch04.html)

```r
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

# 選權重時，應比較：
# 1. 殘差是否仍有濃度相關趨勢或漏斗形。
# 2. 每一濃度的回算偏差或回收率是否符合預設允收標準。
# 3. 獨立品管與驗證樣品在整個工作範圍是否通過。
# 不要只選 r^2 最高的模型。
#
# 注意：x = 0 的空白無法直接使用 1/x 或 1/x^2。
#       1/s^2 需要每個濃度有足夠重複，否則 s^2 可能很不穩定。

stopifnot(all(is.finite(c(coef(fit_ols), coef(fit_1x), coef(fit_1x2)))))
```

---

## Ch5 有效數字與異常值檢定 (Q 檢定 / Grubbs)

📄 檔案：`ch05_outliers_sigfig.R` ｜ 教學網頁：[ch05.html](ch05.html)

```r
# =====================================================================
# Ch05 有效數字與異常值檢定 (Nielsen 4.5)
# 有效數字規則 / Dixon Q-test / Grubbs test
# =====================================================================

# ---------- 1. 有效數字 ----------
# R 的 signif() 可以直接做「取有效位數」
signif(9566.172, 2)     # 36.54*238*1.1 -> 只保留2位 -> 9600
signif(0.01672, 3)      # -> 0.0167
round(16.175, 2)        # 加法看小數位: 7.45+8.725=16.175 -> 16.18

# 判斷一個數的有效位數（教學用小函數）
n_sig <- function(x_str) {
  x <- gsub("^[+-]", "", x_str)
  x <- sub("^0+", "", x)          # 去掉前導零
  x <- sub("\\.", "", x)          # 去掉小數點
  nchar(sub("0+$", "", x))        # 去尾零後的字元數（近似規則）
}
n_sig("0.0072")    # 2
n_sig("64.72")     # 4
n_sig("6.407")     # 4

# ---------- 2. Dixon Q-test (90% 信賴, Nielsen Table 4.4) ----------
# Q = gap / range ; gap = 可疑值與最近鄰的距離, range = 最大-最小
q_critical <- c("3" = 0.94, "4" = 0.76, "5" = 0.64, "6" = 0.56,
                "7" = 0.51, "8" = 0.47, "9" = 0.44, "10" = 0.41)

q_test <- function(x) {
  x <- sort(x); n <- length(x)
  # 檢查兩端，誰更可疑？
  gap_low  <- x[2] - x[1]          # 最小值可疑
  gap_high <- x[n] - x[n-1]        # 最大值可疑
  rng <- x[n] - x[1]
  if (gap_low > gap_high) {
    Q <- gap_low / rng; suspect <- x[1]; side <- "最低值"
  } else {
    Q <- gap_high / rng; suspect <- x[n]; side <- "最高值"
  }
  Qcrit <- q_critical[[as.character(n)]]
  list(n = n, Q = round(Q, 3), Qcrit = Qcrit,
       suspect_value = suspect, side = side,
       reject = Q > Qcrit)
}

# 範例 1：水分測定出現可疑低值 55.31 (Nielsen 式 4.27)
moisture_bad <- c(64.53, 64.45, 65.10, 64.78, 55.31)
q_test(moisture_bad)
# Q = (64.45-55.31)/(64.78-55.31) = 0.97 > 0.76 (n=5? 注意!)
# 課本原例是「先算好4筆正常值的平均」情境，此處示範含異常值的5筆版本。
# 若只拿 55.31 + 三筆最近值做 n=4 檢驗：
moisture_4 <- c(64.78, 64.53, 64.45, 55.31)
q_test(moisture_4)               # Q=0.969 > 0.76 -> 捨棄 55.31

# 範例 2：乾物質數據 (Nielsen 習題 3)
dry <- c(88.62, 88.74, 89.20, 82.20)
qt_res <- q_test(dry)
qt_res                            # Q=0.917 > 0.76 -> 可捨棄 82.20

# 捨棄後重新計算：
dry_clean <- dry[-which.min(dry)]
mean(dry_clean); sd(dry_clean)    # mean=88.85, SD=0.31
cat(sprintf("捨棄後: mean=%.2f, SD=%.3f, CV=%.2f%%\n",
            mean(dry_clean), sd(dry_clean),
            sd(dry_clean)/mean(dry_clean)*100))

# ---------- 3. Grubbs test (進階，95% 雙尾) ----------
grubbs_crit <- function(n, alpha = 0.05) {
  # Grubbs 臨界值的 t 分布近似公式
  t2 <- qt(alpha/(2*n), df = n - 2)^2
  ((n - 1)/sqrt(n)) * sqrt(t2/(n - 2 + t2))
}
grubbs_test <- function(x, alpha = 0.05) {
  G <- max(abs(x - mean(x))) / sd(x)
  Gc <- grubbs_crit(length(x), alpha)
  list(G = round(G, 3), Gcrit = round(Gc, 3),
       outlier = G > Gc,
       value = x[which.max(abs(x - mean(x)))])
}

grubbs_test(dry)                  # G=2.60 > 1.46 -> 82.20 是異常值
sapply(3:10, grubbs_crit)         # 看看不同 n 的臨界值

# ---------- 4. 學術倫理提醒 ----------
# 「非常罕見」才能刪數據！只有：
#   (1) 有明確可追溯的操作失誤紀錄（如漏加試劑）
#   (2) 客觀統計檢定支持
# 兩者兼備才可考慮剔除，且必須在報告中註明。
# 為了讓精密度變漂亮而刪數據 = 學術不端。
```

---

## Ch6 量測不確定度：概念與 GUM 四步驟

📄 檔案：`ch06_uncertainty_concept.R` ｜ 教學網頁：[ch06.html](ch06.html)

```r
# =====================================================================
# Ch06 量測不準度的概念：誤差 vs 不確定度 (QUAM 2012 第2章)
# EURACHEM/CITAC Guide CG4 "Quantifying Uncertainty in Analytical Measurement"
# =====================================================================

# ---------- 1. 用模擬理解「誤差」與「不準度」的差別 ----------
# 誤差 error    : 單一結果與真值的差（一個數，有正負，實務上未知）
# 不準度 uncertainty: 描述「真值可能落在哪個範圍」的參數（一個區間）
#
# 模擬情境：真值 = 100.0 mg/L，方法有 +2 的系統誤差(偏倚)，
#           隨機誤差 SD = 3
set.seed(123)
true_value <- 100.0
bias       <- 2.0          # 系統性偏移(例如校正沒做好)
random_sd  <- 3.0

results <- rnorm(30, mean = true_value + bias, sd = random_sd)

mean(results)              # 觀測平均 ~102 -> 與真值差約 +2 = 誤差
sd(results)                # 散布程度 ~3   -> 隨機效應的大小

# 畫圖看「誤差」與「不準度」
hist(results, breaks = 8, col = "lightblue",
     main = "誤差 vs 不準度",
     xlab = "量測結果 (mg/L)", freq = FALSE)
abline(v = true_value, col = "darkgreen", lwd = 3)      # 真值
abline(v = mean(results), col = "red", lwd = 2, lty = 2) # 測得平均
u <- sd(results)
arrows(mean(results) - 2*u, 0.08, mean(results) + 2*u, 0.08,
       code = 3, angle = 90, length = 0.05, lwd = 2, col="purple")
text(mean(results), 0.10, "±U (不準度區間)", col = "purple", pos = 3)

# 重點：
# - 誤差是單點、不可知；不準度是區間、可估計
# - 隨機誤差可用增加重複次數縮小；系統誤差不行，必須校正/加回收修正
# - spurious error (人為疏失如抄錄數字) 一經確認應整筆捨棄，
#   不可以納入任何統計處理！

# ---------- 2. ISO/IEC 17025 為什麼要求不準度 ----------
# 實驗室報告若無不準度，「12.5 mg/kg 是否超標 10 mg/kg」根本無從判定。
# 合規判定需要知道：結果 ± U 與法規限值的相對位置（見 ch08）。

# ---------- 3. GUM 四步驟流程預覽 (QUAM 第4章 Figure 1) ----------
# Step 1 Specify the measurand     明確定義被測量(寫出計算式!)
# Step 2 Identify uncertainty sources 列出所有不準度來源(魚骨圖)
# Step 3 Quantify components        把每個來源換算成標準差 u(x_i)
# Step 4 Calculate combined U       合成 uc 再乘涵蓋因子 k 得 U
cat("GUM 流程: Step1 定義 -> Step2 找來源 -> Step3 量化 -> Step4 合成\n")

# ---------- 4. 小練習：寫出你的被測量 ----------
# 例：以 HPLC 測咖啡飲料之咖啡因含量
# c(mg/L) = (由標準曲線內插濃度) * 稀釋倍數 / 樣品體積
# 想想看哪些參數會帶進不準度？
#   校正曲線斜率截距、稀釋用容量瓶/移液管、進樣重複性、基質效應...
```

---

## Ch7 Type A/B 分布轉換

📄 檔案：`ch07_typeAB_distributions.R` ｜ 教學網頁：[ch07.html](ch07.html)

```r
# =====================================================================
# Ch07 不準度的量化：Type A / Type B 與分布轉換
# (QUAM 2012 第7章 + 附錄 E.1 分布函數)
# =====================================================================

# ---------- 1. Type A：由重複量測的統計得出 ----------
# 直接用實驗標準差當標準不準度 u(x)
# 例：天平重複稱同一樣品 5 次 (mg)
repeats <- c(1001.2, 1000.8, 1001.5, 1001.0, 1000.9)
u_A <- sd(repeats)          # 單次量測的標準不準度 = 0.27 mg
u_A
# 若結果是 n 次的平均，則用平均值標準誤：
u_A_mean <- sd(repeats)/sqrt(length(repeats))
u_A_mean

# ---------- 2. Type B：由既有資訊(證書、規格、經驗)推得 ----------
# 關鍵：把「界限 ±a」換算成等效標準差 u(x)
#
# 選擇分布前先問「±a 代表什麼」：
# 1. 證書直接給擴展不準度 U 與涵蓋因子 k：u = U/k
# 2. 明確寫成常態分布的中央 95% 區間：u 約為 a/1.96
# 3. 只知道最大允差 ±a，界限內各值同樣可能：u = a/sqrt(3)
# 4. 有證據顯示中央最可能、越靠近界限越少見：u = a/sqrt(6)
# Type B 是資訊來源的評估方式，不等於固定使用矩形分布。

# 例：校正證書直接寫 U = 0.20 mg、k = 2
U_cert <- 0.20
k_cert <- 2
u_cert <- U_cert / k_cert
u_cert                         # -> 0.10 mg；不要再除以 sqrt(3)

# (a) 矩形分布 rectangular: 只知道 ±a，機率均勻 -> u = a/sqrt(3)
u_rect <- function(a) a / sqrt(3)

# 例 QUAM 8.1.4：10 mL A級容量瓶，證書 ±0.2 mL（極端值可能出現）
u_rect(0.2)                 # -> 0.115 mL

# (b) 三角形分布 triangular: ±a 且中間值最可能 -> u = a/sqrt(6)
u_tri <- function(a) a / sqrt(6)
# 例 QUAM 8.1.5：同上容量瓶，但內部查核顯示極端值罕見
u_tri(0.2)                  # -> 0.0816 mL

# (c) 常態分布: 已知 95% 信賴區間 ±a -> u = a/1.96
u_norm95 <- function(a) a / qnorm(0.975)
# 例 QUAM 8.1.3：天平讀值 ±0.2 mg (95% 信賴)
u_norm95(0.2)               # -> 0.102 mg

# ---------- 3. 三種分布長什麼樣？ ----------
x_seq <- seq(-1, 1, length.out = 500)
rect_d <- dunif(x_seq, min = -0.9, max = 0.9)
tri_d  <- ifelse(abs(x_seq) <= 0.9, (0.9 - abs(x_seq))/0.9^2, 0)
norm_d <- dnorm(x_seq, sd = 0.45)

plot(x_seq, rect_d, type = "l", lwd = 2, col = "steelblue",
     ylim = c(0, 1.25), main = "Type B 的三種常用分布",
     xlab = "偏移量 (相對尺度)", ylab = "機率密度")
lines(x_seq, tri_d, col = "darkorange", lwd = 2)
lines(x_seq, norm_d, col = "darkgreen", lwd = 2)
legend("topright", c("矩形 ±a", "三角形 ±a", "常態"),
       col = c("steelblue","darkorange","darkgreen"), lwd = 2)
# 同樣的 ±a，矩形分布的尾巴最寬 => 換算出的 u 最大（最保守）

# ---------- 4. 實戰小題庫 ----------
items <- data.frame(
  item      = c("容量瓶10mL(證書±0.2mL,極端少見)",
                "容量瓶10mL(僅知±0.2mL)",
                "天平(±0.2mg, 95%信賴)",
                "滴定管讀數(±0.05mL, 憑經驗估計)"),
  a         = c(0.2, 0.2, 0.2, 0.05),
  dist      = c("triangular","rect","normal95","rect"),
  u         = NA_real_
)
for (i in seq_len(nrow(items))) {
  items$u[i] <- switch(items$dist[i],
    triangular = u_tri(items$a[i]),
    rect       = u_rect(items$a[i]),
    normal95   = u_norm95(items$a[i]))
}
round(items$u, 4)     # 每一項的標準不準度

# ---------- 5. 相對標準不準度 ----------
# 很多時候用 RSD (u/x) 表示更方便合成 (乘除模型見 ch08)
c_Cd  <- 1002.7        # QUAM Example A1 的鎘標準液 (mg/L)
rel_u <- c(Purity = 0.000058, Mass = 0.05/100.28, Volume = 0.07/100.0)
round(rel_u, 5)        # 純度、質量、體積的相對標準不準度
```

---

## Ch7 實戰案例(1)：分析天平稱量

📄 檔案：`case_balance.R` ｜ 教學網頁：[ch07.html](ch07.html)

```r
# =====================================================================
# 案例①：分析天平稱量的量測不準度 (依 QUAM 2012 Example A1 架構)
# 情境：精確稱取約 100 mg 的純金屬(如 Cd)配製標準溶液
# 學習目標：把天平的三種不準度來源換算成 u，並用 Rule 2 合成
# =====================================================================

# ---------- 1. 天平稱量的三大不準度來源 ----------
# (1) 讀值解析度 readability : 末位數字的最小刻度
# (2) 校正/線性 calibration  : 校正證書給的 ± 界限
# (3) 重複性 repeatability   : 同一樣品反覆稱重的變異 (Type A)
#
# QUAM A1 的作法：把「淨重 = 皮重(tare)與毛重(gross)之差」的
# 每個成分都算出來，再合成。本腳本簡化為「一次淨重」的預算。

# ---------- 2. 各成分的標準不準度 ----------
# (1) 讀值解析度：五位天平最後一位 0.01 mg -> 半寬 a = 0.005 mg
#     數位顯示的捨入屬「矩形分布」-> u = a/sqrt(3)
a_read <- 0.005
u_read <- a_read / sqrt(3)
round(u_read, 5)          # -> 0.00289 mg

# (2) 校正線性：校正證書 ±0.05 mg，極端值罕見 -> 三角形 u = a/sqrt(6)
#     (若證書寫「±0.05 mg (95% 信賴)」則改用 a/1.96)
a_cal <- 0.05
u_cal  <- a_cal / sqrt(6)
round(u_cal, 5)           # -> 0.02041 mg

# (3) 重複性：對同一 100 mg 物件稱 6 次的標準差 (Type A)
reps <- c(100.03, 100.08, 100.02, 100.09, 100.04, 100.01)
u_rep <- sd(reps)
round(u_rep, 4)           # -> 約 0.032 mg

# ---------- 3. 合成：淨重 m = m_gross - m_tare (加減模型 Rule 1) ----------
# 皮重與毛重各經歷一次完整稱重，故每項都含三成分：
u_weigh_once <- sqrt(u_read^2 + u_cal^2 + u_rep^2)
u_m <- sqrt(2) * u_weigh_once        # 兩次稱重 (皮+毛)
round(c(u_weigh_once = u_weigh_once, u_m = u_m), 4)
# -> u(m) 約 0.054 mg，量級與 QUAM Table A1.1 的 u(m)=0.05 mg 相符

# ---------- 4. 對最終濃度的影響 (Rule 2) ----------
# c(Cd) = 1000 * m * P / V
m <- 100.28; P <- 0.9999; V <- 100.0
c_Cd <- 1000 * m * P / V
contrib_m <- c_Cd * u_m / m          # |dy/dm| * u(m)
round(contrib_m, 3)                    # -> 0.55 mg/L

# 比較：體積與純度的貢獻
u_V <- 0.07; u_P <- 0.000058
c(contrib_m   = contrib_m,
  contrib_V   = c_Cd * u_V / V,
  contrib_P   = c_Cd * u_P / P) |> round(3)

# ---------- 5. 結論 ----------
# 稱量 100 mg 時，天平不準度對 c(Cd) 的貢獻 (0.55 mg/L)
# 小於體積的貢獻 (0.70 mg/L) —— 但若只稱 10 mg，
# 質量的相對不準度會放大 10 倍，立刻變成主導項！
m10 <- 10.0
c_Cd10 <- 1000 * m10 * P / V
round(c_Cd10 * u_m / m10, 3)   # -> 5.0 mg/L，稱太少樣本不準度爆增
```

---

## Ch8 合成與擴展不確定度、報告與符合性

📄 檔案：`ch08_combine_report.R` ｜ 教學網頁：[ch08.html](ch08.html)

```r
# =====================================================================
# Ch08 合成與擴展不準度、結果報告與符合性判定
# (QUAM 2012 第8章 Step4 + 第9章 Reporting)
# =====================================================================

# ---------- 1. 合成規則 Rule 1：加減模型 ----------
# y = p + q + r (+/-) -> uc(y) = sqrt( u(p)^2 + u(q)^2 + u(r)^2 )

# QUAM 8.2.8 Example 1: y = p - q + r
p <- 5.02; q <- 6.45; r <- 9.04
u_p <- 0.13; u_q <- 0.05; u_r <- 0.22
y1 <- p - q + r
uc1 <- sqrt(u_p^2 + u_q^2 + u_r^2)
y1                 # 7.61
round(uc1, 2)      # 0.26

# ---------- 2. 合成規則 Rule 2：乘除模型 (用相對不準度) ----------
# y = p*q/r -> uc(y)/y = sqrt( (u(p)/p)^2 + (u(q)/q)^2 + (u(r)/r)^2 )

# QUAM 8.2.8 Example 2: y = o*p/(q*r)
o <- 2.46; p <- 4.32; q <- 6.38; r <- 2.99
u_o <- 0.02; u_p <- 0.13; u_q <- 0.11; u_r <- 0.07
y2 <- o * p / (q * r)
rel_uc2 <- sqrt((u_o/o)^2 + (u_p/p)^2 + (u_q/q)^2 + (u_r/r)^2)
uc2 <- y2 * rel_uc2
y2                          # 0.557
round(uc2, 3)               # 0.024

# ---------- 3. 擴展不準度 Expanded uncertainty U = k * uc ----------
U1 <- 2 * uc1               # k = 2, 信賴水準約 95%
cat(sprintf("y1 = %.2f ± %.2f  (k=2)\n", y1, U1))

# 何時 k 不用 2？當合成不準度被「自由度很少」的項主導時
# QUAM 8.3.4 範例：稱重 uc = sqrt(0.01^2 + 0.08^2) = 0.081 mg
#   其中 s_obs=0.08 由 n=5 次觀測而來 (df = 5-1 = 4)
uc_w <- sqrt(0.01^2 + 0.08^2)
k_t <- qt(0.975, df = 4)    # t 值 -> 2.776，QUAM 表1取 2.8
U_w <- k_t * uc_w
round(c(uc_weighing = uc_w, k = k_t, U = U_w), 3)
# U = 2.8 * 0.081 = 0.23 mg（課本數字）

# ---------- 4. 報告格式 (QUAM 第9章) ----------
report_expanded <- function(x, U, unit, k = 2) {
  cat(sprintf("(%s ± %s) %s\n", format(x), format(U), unit))
  cat(sprintf("所述不確定度為擴展不確定度，涵蓋因子 k=%d，", k))
  cat("信賴水準約 95%。\n")
}
report_expanded(3.52, 0.14, "g/100g")   # QUAM 氮含量範例
# U 與 uc 通常取至多 2 位有效數字；結果位數須與 U 對齊

# ---------- 5. 符合性判定 compliance against limits ----------
# QUAM Figure 2：結果+不準度 與上限 L 的四種關係
judge_compliance <- function(result, U, limit,
                             rule = c("conservative","simple")) {
  rule <- match.arg(rule)
  if (rule == "simple") {
    # 簡單法則：測值 > 限值 即不合格
    ifelse(result > limit, "不符合", "符合")
  } else {
    # 保守決策規則：result - U > limit 才判不符（高信賴）
    # 用 ifelse() 才能同時處理一筆或多筆結果。
    ifelse(result - U > limit, "不符合",
           ifelse(result + U <= limit, "符合",
                  "灰色地帶（無法判定，需複驗）"))
  }
}

L <- 10.0     # 法規上限 mg/kg
cases <- data.frame(
  case = paste0("(", c("i","ii","iii","iv"), ")"),
  result = c(11.5, 10.6, 9.6, 8.8),
  U      = rep(1.0, 4))
cases$verdict_simple <- judge_compliance(cases$result, cases$U, L, "simple")
cases$verdict_consv  <- judge_compliance(cases$result, cases$U, L, "conservative")
print(cases)

# ---------- 6. 完整小案例：果汁中鉛 (自編數據練習) ----------
Pb_result <- 0.085   # mg/L
u_components <- c(
  repeatability = 0.006,          # 重複性，Type A
  calibration   = 0.004,          # 校正曲線
  blank         = 0.002,          # 空白
  volume        = 0.0015,         # 體積
  recovery      = 0.005)          # 回收率
uc_Pb <- sqrt(sum(u_components^2))
U_Pb <- 2 * uc_Pb
cat(sprintf("Pb = (%.3f ± %.3f) mg/L (k=2)\n", Pb_result, U_Pb))
judge_compliance(Pb_result, U_Pb, limit = 0.10, "conservative")
```

---

## Ch9 Kragten 試算表法與 Monte Carlo

📄 檔案：`ch09_kragten_montecarlo.R` ｜ 教學網頁：[ch09.html](ch09.html)

```r
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
```

---

## Ch10 實戰案例(2)：NaOH 標定滴定 (QUAM Example A2)

📄 檔案：`case_titration.R` ｜ 教學網頁：[ch10.html](ch10.html)

```r
# =====================================================================
# 案例②：NaOH 標定滴定的量測不準度 (QUAM 2012 Example A2 完整重現)
# 情境：以一級標準物 KHP(鄰苯二甲酸氫鉀)標定 ~0.1 M NaOH
# 模型：c(NaOH) = 1000 * m(KHP) * P(KHP) / ( M(KHP) * V_T )  [mol/L]
# =====================================================================

# ---------- 1. Step 1 定義被測量 ----------
# 輸入量與 QUAM Table A2.1 相同：
m_KHP  <- 0.3888      # g   稱取的 KHP 質量
P_KHP  <- 1.0         #     KHP 純度(證書)
M_KHP  <- 204.2212    # g/mol  KHP 莫耳質量
V_T    <- 18.64       # mL  滴定消耗的 NaOH 體積

c_NaOH <- 1000 * m_KHP * P_KHP / (M_KHP * V_T)
round(c_NaOH, 5)      # -> 0.10214 mol/L（與 QUAM 完全一致）

# ---------- 2. Step 2/3 各成分的標準不準度 (QUAM Table A2.2) ----------
u_rep   <- 0.0005     # 重複性(相對)：整個滴定實驗的重複變異
u_mKHP  <- 0.00013    # g    稱重：淨重 0.3888 g 的合成不準度
u_PKHP  <- 0.00029    #     純度：證書 ±0.0005 矩形 -> 0.0005/sqrt(3)
u_MKHP  <- 0.0038     # g/mol 莫耳質量：由 IUPAC 原子量不確定度推得
u_VT    <- 0.013      # mL   滴定體積：校正+溫度+終點判讀合成

# 滴定體積 0.013 mL 是怎麼來的？(QUAM A2.4)
#   滴定管校正 ±0.01 mL (A級, 三角形) -> 0.01/sqrt(6) = 0.0041
#   溫度效應 ±4°C: 18.64 * 2.1e-4 * 4 /sqrt(3) = 0.009
#   終點判讀偏移約 ±0.003 mL (矩形)  -> 0.0017
u_cal_t  <- 0.01/sqrt(6)
u_temp_t <- 18.64 * 2.1e-4 * 4 / sqrt(3)   # 2.1e-4 = 玻璃膨脹係數/°C
u_ep     <- 0.003/sqrt(3)
u_VT_check <- sqrt(u_cal_t^2 + u_temp_t^2 + u_ep^2)
round(u_VT_check, 4)   # -> 約 0.010 mL，QUAM 取 0.013 (較保守，含重複誤差)

# ---------- 3. Step 4 合成 (乘除模型 Rule 2，用相對不準度) ----------
rel <- c(rep = u_rep, m = u_mKHP/m_KHP, P = u_PKHP,
         M = u_MKHP/M_KHP, V = u_VT/V_T)
rel_uc <- sqrt(sum(rel^2))
uc  <- c_NaOH * rel_uc
round(rel_uc, 5)      # -> 0.00097（QUAM Table A2.1）
round(uc, 5)          # -> 0.000099 ≈ 0.00010 mol/L

# 擴展不準度與報告
U <- 2 * uc
cat(sprintf("c(NaOH) = (%.5f ± %.5f) mol/L (k=2, 約95%%)\n",
            c_NaOH, round(U, 5)))

# ---------- 4. 不準度預算：誰是老大？ ----------
contrib_rel <- rel^2 / sum(rel^2) * 100   # 各成分變異占比 %
data.frame(component = names(rel),
           rel_u = round(rel, 5),
           variance_pct = round(contrib_rel, 1))
# 排序：V_T(52%) > 重複性(27%) > 稱重(12%) > 純度(9%) > 莫耳質量(0%)
barplot(sort(contrib_rel, decreasing = TRUE),
        col = c("#1E88E5","#43A047","#FDD835","#FB8C00","#8E24AA"),
        las = 1, border = NA, ylab = "變異數占比 (%)",
        main = "滴定標定的不準度預算：V_T 與重複性主導")

# ---------- 5. 改善策略（工程師思維）----------
# 想把 U 減半？先攻擊最大項！
#  (a) V_T 太小 -> 多稱一點 KHP 讓滴定體積接近 50 mL 滿管程
#      試算：V_T=49 mL 時相對貢獻從 0.0007 降到 0.00027
u_VT_50 <- 0.013; V50 <- 49
rel2 <- c(u_rep, u_mKHP/(m_KHP*2.6), u_PKHP, u_MKHP/M_KHP, u_VT_50/V50)
round(sqrt(sum(rel2^2)), 5)   # -> 0.00065，uc 從 0.00010 降到 0.000066

#  (b) 重複性：增加平行滴定次數取平均
#  (c) 稱重：改用更大質量 (但 KHP 太多會超過 50 mL，需權衡)
```

---

## Ch10 實戰案例(3)：HPLC/GC 農藥殘留 (QUAM Example A4)

📄 檔案：`case_hplc.R` ｜ 教學網頁：[ch10.html](ch10.html)

```r
# =====================================================================
# 案例③：HPLC/GC 分析農藥殘留的量測不準度
# (QUAM 2012 Example A4：麵包中有機磷農藥，採內部驗證數據法)
# 模型：P_op = (I_op * c_ref * V) / (I_ref * Rec * m_sample) * F_hom [mg/kg]
# =====================================================================

# ---------- 1. Step 1 定義被測量 ----------
# P_op : 麵包中農藥殘留量 (mg/kg)
# I_op / I_ref : 樣品萃取液與參考標準品的層析波峰面積
# c_ref : 參考標準品濃度 (ug/mL)
# V     : 萃取液最終體積 (mL)
# m     : 樣品取樣量 (g)
# Rec   : 回收率 (小數)；F_hom : 樣品均勻性修正因子
#
# 儀器訊號比 I_op/I_ref 已吸收大部分儀器校正因素，
# 所以「儀器校正」不再是主項 —— 主項變成「方法」的表現！

# ---------- 2. 內部驗證給我們什麼？(QUAM Table A4.4) ----------
# (1) Precision 精密度：不同類型樣品雙重複分析的變異
#     相對標準不準度 = 0.27  (中間精密度, 含均勻化、萃取、進樣)
# (2) Bias 偏倚(回收率)：加標回收實驗平均回收率 Rec = 0.9 (90%)，
#     其相對標準不準度 = 0.043/0.9 = 0.048
#     (0.043 來自回收率數據的標準差與校正顯著性檢定)
# (3) Homogeneity 均勻性：模型估計最壞情境 = 0.2
#     (農藥可能只分布在麵包表面 -> 取樣代表性)

# ---------- 3. Step 4 合成：全乘除模型 -> 相對不準度平方和 ----------
rel_prec  <- 0.27
rel_bias  <- 0.043 / 0.9
rel_homog <- 0.20
rel_uc <- sqrt(rel_prec^2 + rel_bias^2 + rel_homog^2)
round(rel_uc, 2)          # -> 0.34（QUAM Table A4.4）

# 數值範例：儀器測得未修正結果 1.00 mg/kg
P_raw <- 1.00
P_op  <- P_raw / 0.9      # 回收率修正 (90% 回收 -> 除以 0.9)
uc_op <- P_op * rel_uc
U_op  <- 2 * uc_op
cat(sprintf("P_op = %.2f mg/kg, uc = %.3f, U = ±%.2f mg/kg (k=2)\n",
            P_op, uc_op, U_op))
# -> P_op = 1.11 ± 0.75 mg/kg（與 QUAM Table A4.5 的 1.1111/0.377 一致）

# ---------- 4. 不準度預算視覺化 ----------
contrib <- c(Precision = rel_prec^2, Bias = rel_bias^2,
             Homogeneity = rel_homog^2)
pct <- contrib / sum(contrib) * 100
round(pct, 1)             # 精密度 63% / 均勻性 35% / 偏倚 2%
barplot(pct, names.arg = c("精密度", "均勻性", "回收率偏倚"),
        col = c("#1E88E5", "#43A047", "#FDD835"),
        border = NA, las = 1, ylab = "變異數占比 (%)",
        main = "HPLC/GC 農藥分析：內部驗證法的不準度預算")

# ---------- 5. 進階：用「雙重複對數據」自己算精密度項 ----------
# 驗證時對 n 對樣品做雙重複(duplicate)分析，log 差可用來估 RSD
# RSD = sqrt( sum(d^2) / (2n) )，d 為成對結果的相對差
dup_pairs <- data.frame(
  sample = paste0("B", 1:8),
  a = c(0.42, 1.13, 0.27, 0.88, 0.55, 1.62, 0.31, 0.74),
  b = c(0.39, 0.97, 0.30, 0.71, 0.60, 1.28, 0.35, 0.80))
d2 <- with(dup_pairs, ((a - b) / ((a + b)/2))^2)
RSD_dup <- sqrt(sum(d2) / (2 * nrow(dup_pairs)))
round(RSD_dup, 2)         # -> 約 0.15，與長期中間精密度 0.27 同一量級
# 注意：雙重複只反映「短時間」變異，長期中間精密度通常更大

# ---------- 6. 報告與符合性 ----------
# 法規上限(MRL) = 2.0 mg/kg，判斷 1.11 ± 0.75 是否合格？
result <- 1.11; U <- 0.75; L <- 2.0
if (result + U <= L) {
  verdict <- "符合 (result+U <= L)"
} else if (result - U > L) {
  verdict <- "不符合"
} else {
  verdict <- "灰色地帶：測值低於限值但 result+U 超過限值"
}
verdict
# 1.11+0.75=1.86 <= 2.0 -> 即使保守規則也「符合」
# 若 MRL=1.5 mg/kg，同樣的結果就會落入灰色地帶（需複驗）
```

---

## Ch11 綜合案例：粗纖維 (A6) 與標準曲線反推不確定度 (E.4)

📄 檔案：`ch11_capstone.R` ｜ 教學網頁：[ch11.html](ch11.html)

```r
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
```

---

## Ch12 進階案例(4)：LC-MS/MS 氯黴素 (基質效應/SIL-IS/加權校正)

📄 檔案：`case_lcmsms.R` ｜ 教學網頁：[ch12.html](ch12.html)

```r
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
```

---

