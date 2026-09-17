# =====================================================================
# Ch07 不確定度的量化：Type A / Type B 與分布轉換
# (QUAM 2012 第7章 + 附錄 E.1 分布函數)
# =====================================================================

# ---------- 1. Type A：由重複量測的統計得出 ----------
# 直接用實驗標準差當標準不確定度 u(x)
# 例：天平重複稱同一樣品 5 次 (mg)
repeats <- c(1001.2, 1000.8, 1001.5, 1001.0, 1000.9)
u_A <- sd(repeats)          # 單次量測的標準不確定度 = 0.27 mg
u_A
# 若結果是 n 次的平均，則用平均值標準誤：
u_A_mean <- sd(repeats)/sqrt(length(repeats))
u_A_mean

# ---------- 2. Type B：由既有資訊(證書、規格、經驗)推得 ----------
# 關鍵：把「界限 ±a」換算成等效標準差 u(x)
#
# 選擇分布前先問「±a 代表什麼」：
# 1. 證書直接給擴展不確定度 U 與涵蓋因子 k：u = U/k
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
round(items$u, 4)     # 每一項的標準不確定度

# ---------- 5. 相對標準不確定度 ----------
# 很多時候用 RSD (u/x) 表示更方便合成 (乘除模型見 ch08)
c_Cd  <- 1002.7        # QUAM Example A1 的鎘標準液 (mg/L)
rel_u <- c(Purity = 0.000058, Mass = 0.05/100.28, Volume = 0.07/100.0)
round(rel_u, 5)        # 純度、質量、體積的相對標準不確定度
