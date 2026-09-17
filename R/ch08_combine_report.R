# =====================================================================
# Ch08 合成與擴展不確定度、結果報告與符合性判定
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

# ---------- 2. 合成規則 Rule 2：乘除模型 (用相對不確定度) ----------
# y = p*q/r -> uc(y)/y = sqrt( (u(p)/p)^2 + (u(q)/q)^2 + (u(r)/r)^2 )

# QUAM 8.2.8 Example 2: y = o*p/(q*r)
o <- 2.46; p <- 4.32; q <- 6.38; r <- 2.99
u_o <- 0.02; u_p <- 0.13; u_q <- 0.11; u_r <- 0.07
y2 <- o * p / (q * r)
rel_uc2 <- sqrt((u_o/o)^2 + (u_p/p)^2 + (u_q/q)^2 + (u_r/r)^2)
uc2 <- y2 * rel_uc2
y2                          # 0.557
round(uc2, 3)               # 0.024

# ---------- 3. 擴展不確定度 Expanded uncertainty U = k * uc ----------
U1 <- 2 * uc1               # k = 2, 信賴水準約 95%
cat(sprintf("y1 = %.2f ± %.2f  (k=2)\n", y1, U1))

# 何時 k 不用 2？當合成不確定度被「自由度很少」的項主導時
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
# QUAM Figure 2：結果+不確定度 與上限 L 的四種關係
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
