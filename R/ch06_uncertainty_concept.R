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
