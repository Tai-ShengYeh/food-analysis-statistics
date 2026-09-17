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
round(mdl, 3)      # -> 約 0.090 mg/L（涵蓋整個方法流程的變異）

# ---------- 3. Shewhart 管制圖 ----------
# 情境：實驗室每天用標準品(蛋白質 12.0%)監控方法是否穩定
set.seed(7)
qc_days <- 1:25
qc_value <- round(rnorm(25, mean = 12.00, sd = 0.15), 3)
# 人為加入兩個異常事件：第8~11天連續偏高(系統性漂移，qc_value[8:11] 都加 0.28)、
# 第18天單點爆表(直接設成 12.62)
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
out_of_control          # 第10、18天超出 ±3s 行動界限（漂移累積+爆表）
which(qc_value > ual | qc_value < lal)

# 只超出 ±2s 警告界限、但還沒超過 ±3s 行動界限的天數
warn_only <- which((qc_value > uwl | qc_value < lwl) & !(qc_value > ual | qc_value < lal))
warn_only                # 第1、9、11、12、13天：只觸發警告，尚未達行動界限

# 判讀規則②：連續多點落在中心線同一側，即使沒人超出 ±3s 也代表有系統性變因
above_cl <- qc_value > cl
run_info <- rle(above_cl)
run_info                 # 第7~16天(連續10點)都在中心線上方，正是規則②抓得到、
                          # 但只看「有沒有點超出±3s」會完全漏掉的訊號

# 判讀口訣：
#  - 點超出 ±3s 或連續規則違反 -> 停下來找根本原因(root cause)
#  - 連續 7 點同側 / 連續上升下降 -> 有系統性變因（本例第7~16天共10點同側）

# ---------- 4. CuSum 累積和管制圖 (偵測微小漂移更靈敏) ----------
csum <- cumsum(qc_value - target)
plot(qc_days, csum, type = "b", pch = 19, col = "darkgreen",
     main = "CuSum 管制圖",
     xlab = "分析日", ylab = "累積偏差 (CuSum)")
abline(h = 0, lty = 2)
# 解讀：第 8~11 天的 +0.28 漂移，在 Shewhart 圖上第 9 天先觸及 ±2s 警告線、
# 第 10 天已衝出 ±3s 行動界限；但 CuSum 的斜率早在第 8 天就明顯轉正並持續攀升 ——
# 比 Shewhart 更早、更清楚地顯示這是小而持續的系統性偏移，而非單點雜訊。

# ---------- 5. 其他日常 QC 手段（名詞認識）----------
# 空白試驗 blank        : 抓污染與背景干擾
# 加標回收 recovery     : (加標測值-原測值)/添加量*100%，通常要求 80~120%
recovery <- function(spike_total, native, added) {
  (spike_total - native) / added * 100
}
recovery(spike_total = 9.6, native = 5.1, added = 5.0)   # 90% 合格

# 重複樣品 replicate     : 同一樣品平行測定，看 RSD
# 查核樣品/CRM           : 用已知濃度標準物質確認準確度
