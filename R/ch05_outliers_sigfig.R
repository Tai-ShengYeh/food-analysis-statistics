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
