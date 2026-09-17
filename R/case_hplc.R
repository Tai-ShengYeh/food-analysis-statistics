# =====================================================================
# 案例③：HPLC/GC 分析農藥殘留的量測不確定度
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
#     相對標準不確定度 = 0.27  (中間精密度, 含均勻化、萃取、進樣)
# (2) Bias 偏倚(回收率)：加標回收實驗平均回收率 Rec = 0.9 (90%)，
#     其相對標準不確定度 = 0.043/0.9 = 0.048
#     (0.043 來自回收率數據的標準差與校正顯著性檢定)
# (3) Homogeneity 均勻性：模型估計最壞情境 = 0.2
#     (農藥可能只分布在麵包表面 -> 取樣代表性)

# ---------- 3. Step 4 合成：全乘除模型 -> 相對不確定度平方和 ----------
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

# ---------- 4. 不確定度預算視覺化 ----------
contrib <- c(Precision = rel_prec^2, Bias = rel_bias^2,
             Homogeneity = rel_homog^2)
pct <- contrib / sum(contrib) * 100
round(pct, 1)             # 精密度 63% / 均勻性 35% / 偏倚 2%
barplot(pct, names.arg = c("精密度", "均勻性", "回收率偏倚"),
        col = c("#1E88E5", "#43A047", "#FDD835"),
        border = NA, las = 1, ylab = "變異數占比 (%)",
        main = "HPLC/GC 農藥分析：內部驗證法的不確定度預算")

# ---------- 5. 進階：用「雙重複對數據」自己算精密度項 ----------
# 驗證時對 n 對樣品做雙重複(duplicate)分析，log 差可用來估 RSD
# RSD = sqrt( sum(d^2) / (2n) )，d 為成對結果的相對差
dup_pairs <- data.frame(
  sample = paste0("B", 1:8),
  a = c(0.42, 1.13, 0.27, 0.88, 0.55, 1.62, 0.31, 0.74),
  b = c(0.39, 0.97, 0.30, 0.71, 0.60, 1.28, 0.35, 0.80))
d2 <- with(dup_pairs, ((a - b) / ((a + b)/2))^2)
RSD_dup <- sqrt(sum(d2) / (2 * nrow(dup_pairs)))
round(RSD_dup, 2)         # -> 0.10（實際 0.1027196），與長期中間精密度 0.27 同一量級
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
