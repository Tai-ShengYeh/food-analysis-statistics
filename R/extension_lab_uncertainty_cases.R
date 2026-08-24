# =====================================================================
# 選修案例庫：天平、酸鹼滴定與 HPLC 量測不準度
# 教學用 bottom-up 範例；正式數值須換成實驗室證書、驗證與品管資料
# =====================================================================

combine_u <- function(estimate, components, k = 2) {
  uc <- sqrt(sum(components^2))
  data.frame(result = estimate, uc = uc, k = k, U = k * uc)
}

# ---------- 案例 1：天平淨重（兩次讀值相減） ----------
# 被測量：m_net = m_gross - m_tare，單位 g
net_repeats <- c(5.4326, 5.4324, 5.4327, 5.4325, 5.4326)
m_net <- mean(net_repeats)
u_repeat_m <- sd(net_repeats) / sqrt(length(net_repeats))
u_cal_read <- 0.0004 / 2        # 校正證書 U=0.0004 g, k=2
u_res_read <- 0.0001 / sqrt(12) # 數位解析度 d 的四捨五入：d/sqrt(12)
u_mass <- c(
  repeatability = u_repeat_m,
  calibration_two_readings = sqrt(2) * u_cal_read,
  resolution_two_readings = sqrt(2) * u_res_read
)
mass_result <- combine_u(m_net, u_mass)
print(mass_result)

# 注意：同一台天平的毛重與皮重可能相關；共同校正偏差可部分抵消。
# 正式評估應依校正證書與稱量程序處理共變異，不能一律假設獨立。

# ---------- 案例 2：果汁可滴定酸（以檸檬酸計） ----------
# A (g/100 g) = V * C * EW / 1000 / m * 100
V_rep <- c(12.44, 12.47, 12.45, 12.48) # NaOH mL
V <- mean(V_rep)
C_NaOH <- 0.1002                        # mol/L
EW_citric <- 64.04                      # g/eq，視反應當量定義
m_sample <- 10.000                      # g
acidity <- V * C_NaOH * EW_citric / 1000 / m_sample * 100

u_V_repeat <- sd(V_rep) / sqrt(length(V_rep))
u_V_cert <- 0.030 / 2                   # 滴定管證書 U, k=2
u_V_res <- 0.01 / sqrt(12)
u_endpoint <- 0.020 / sqrt(3)           # 終點判讀界限 ±0.020 mL
u_V <- sqrt(u_V_repeat^2 + u_V_cert^2 + u_V_res^2 + u_endpoint^2)
u_C <- 0.00020                          # NaOH 標定標準不準度 mol/L
u_m <- 0.001 / sqrt(3)                  # 天平界限 ±0.001 g
rel_acidity <- c(volume = u_V / V, standardization = u_C / C_NaOH,
                  sample_mass = u_m / m_sample)
u_acidity <- acidity * rel_acidity
acidity_result <- combine_u(acidity, u_acidity)
print(acidity_result)

# ---------- 案例 3：HPLC 咖啡因（外部校正＋稀釋） ----------
# 標準品濃度 (mg/L) 與峰面積
std_conc <- c(5, 10, 20, 30, 40, 50)
std_area <- c(512, 1007, 2018, 2996, 4015, 5004)
fit <- lm(std_area ~ std_conc)

sample_area <- c(2528, 2539, 2522)
DF <- 5
x_vial <- (mean(sample_area) - coef(fit)[1]) / coef(fit)[2]
caffeine <- x_vial * DF

# 分開估計校正曲線、樣品重複性、稀釋與回收率的標準不準度
s_yx <- sigma(fit)
Sxx <- sum((std_conc - mean(std_conc))^2)
u_curve_vial <- s_yx / abs(coef(fit)[2]) *
  sqrt(1 / length(std_conc) + (x_vial - mean(std_conc))^2 / Sxx)
u_repeat_vial <- sd(sample_area) / sqrt(length(sample_area)) /
  abs(coef(fit)[2])
u_DF_rel <- sqrt((0.006 / 1.000)^2 + (0.08 / 5.00)^2) # 移液管與容量瓶
u_recovery_rel <- 0.010                               # 驗證資料的回收率標準不準度
u_hplc <- c(
  calibration_curve = u_curve_vial * DF,
  sample_repeatability = u_repeat_vial * DF,
  dilution = caffeine * u_DF_rel,
  recovery = caffeine * u_recovery_rel
)
hplc_result <- combine_u(caffeine, u_hplc)
print(hplc_result)

# 這是適合入門的簡化預算。正式 HPLC 評估還要確認：
# 校正參數共變異、異方差、基質效應、萃取、純度、穩定性與批間精密度。

# ---------- 三個案例的摘要與貢獻率 ----------
summary_table <- rbind(
  transform(mass_result, case = "天平淨重", unit = "g"),
  transform(acidity_result, case = "可滴定酸", unit = "g/100 g"),
  transform(hplc_result, case = "HPLC 咖啡因", unit = "mg/L")
)
print(summary_table[, c("case", "result", "uc", "U", "unit")])

contribution_percent <- function(components) {
  round(100 * components^2 / sum(components^2), 1)
}
print(contribution_percent(u_mass))
print(contribution_percent(u_acidity))
print(contribution_percent(u_hplc))

stopifnot(all(is.finite(summary_table$U)), all(summary_table$U > 0))
