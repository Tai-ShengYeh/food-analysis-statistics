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
