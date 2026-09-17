# =====================================================================
# figures_ch17.R —— 產生 ch17.html 所需圖片 (assets/img/fig_ch17_*.png)
# 執行：在專案根目錄下  Rscript R/figures_ch17.R
# 資料與 R/ch17_anova_advanced.R 完全相同（直接寫在腳本裡）；只用 base R。
# =====================================================================

img_dir <- "assets/img"
dir.create(img_dir, showWarnings = FALSE, recursive = TRUE)
# 與 R/figures.R 相同的中文處理：切到繁中 UTF-8 locale，cairo + 微軟正黑體
if (.Platform$OS.type == "windows") {
  suppressWarnings(Sys.setlocale("LC_CTYPE", "Chinese (Traditional)_Taiwan.utf8"))
}
cjk_font <- "Microsoft JhengHei"
save_png <- function(name, expr, w = 1400, h = 860) {
  grDevices::png(file.path(img_dir, name), width = w, height = h,
                 res = 160, type = "cairo", family = cjk_font)
  on.exit(dev.off())
  par(mar = c(4.2, 4.4, 2.6, 1.2), mgp = c(2.5, 0.7, 0), family = cjk_font)
  expr
}
BLUE <- "#1565C0"; RED <- "#C62828"; GREY <- "#607D8B"; ORANGE <- "#EF6C00"

# ---- 圖 17-1：雙因子交互作用圖（維生素 C 保留率）----
vitc <- data.frame(
  temp = factor(rep(rep(c(50, 60, 70), each = 3), times = 2)),
  time = factor(rep(c(4, 8), each = 9)),
  y    = c(90.5, 91.9, 91.7,   83.8, 86.2, 84.8,   75.5, 76.6, 74.4,
           88.5, 89.8, 89.0,   77.9, 76.3, 78.4,   54.9, 56.3, 55.2))
save_png("fig_ch17_interaction.png", {
  m <- with(vitc, tapply(y, list(temp, time), mean))
  plot(NA, xlim = c(0.8, 3.45), ylim = c(50, 96), xaxt = "n",
       xlab = "乾燥溫度 (°C)", ylab = "維生素 C 保留率 (%)",
       main = "交互作用圖：兩條線不平行 = 有交互作用")
  axis(1, at = 1:3, labels = c("50", "60", "70"))
  grid(nx = NA, ny = NULL, col = "grey88")
  xj <- as.numeric(vitc$temp) + ifelse(vitc$time == "4", -0.04, 0.04)
  points(xj, vitc$y, pch = ifelse(vitc$time == "4", 1, 2),
         col = ifelse(vitc$time == "4", BLUE, RED), cex = 0.9)
  lines(1:3, m[, "4"], type = "b", pch = 19, col = BLUE, lwd = 2.5, cex = 1.3)
  lines(1:3, m[, "8"], type = "b", pch = 17, col = RED,  lwd = 2.5, cex = 1.3)
  d <- m[, "4"] - m[, "8"]
  for (i in 1:3) {
    arrows(i + 0.13, m[i, "4"], i + 0.13, m[i, "8"], code = 3, length = 0.06,
           col = GREY, lwd = 1.4)
    lab <- sprintf("差 %.1f", d[i]); ym <- (m[i, "4"] + m[i, "8"]) / 2
    rect(i + 0.15, ym - 1.3, i + 0.17 + strwidth(lab, cex = 0.95), ym + 1.3,
         col = "white", border = NA)              # 白底，避免字被線壓到
    text(i + 0.16, ym, lab, adj = 0, col = "grey20", cex = 0.95)
  }
  legend("bottomleft", c("4 h（各格平均）", "8 h（各格平均）", "空心 = 個別批次"),
         pch = c(19, 17, 1), col = c(BLUE, RED, GREY), lwd = c(2.5, 2.5, NA),
         bty = "n", cex = 0.95)
})

# ---- 圖 17-2：精密度分解示意（5 天 × 3 重複，含日平均）----
qc <- data.frame(
  day = rep(1:5, each = 3),
  y   = c(26.45, 26.35, 26.57,  26.52, 26.46, 26.70,  26.40, 26.49, 26.59,
          26.27, 26.26, 26.33,  26.57, 26.56, 26.44))
save_png("fig_ch17_precision.png", {
  dm <- tapply(qc$y, qc$day, mean); gm <- mean(qc$y)
  plot(NA, xlim = c(0.6, 6.4), ylim = c(26.20, 26.76), xaxt = "n",
       xlab = "分析日 (day)", ylab = "粗蛋白 (%)",
       main = "同一個 QC 樣品：日內散布 vs 日平均的漂移")
  axis(1, at = 1:5)
  grid(nx = NA, ny = NULL, col = "grey88")
  abline(h = gm, lty = 2, col = GREY, lwd = 1.5)
  text(5.55, gm, sprintf("總平均 %.3f", gm), adj = c(0, -0.4), col = GREY, cex = 0.9)
  points(qc$day, qc$y, pch = 19, col = BLUE, cex = 1.2)
  segments(1:5 - 0.28, dm, 1:5 + 0.28, dm, col = RED, lwd = 3.5)
  # 標示：日內 (重複性) 與 日間
  arrows(2.36, min(qc$y[qc$day == 2]), 2.36, max(qc$y[qc$day == 2]),
         code = 3, length = 0.06, col = BLUE, lwd = 1.5)
  text(2.42, 26.665, "日內散布\n→ s_r", adj = 0, col = BLUE, cex = 0.95)
  arrows(4.36, dm[4], 4.36, gm, code = 3, length = 0.06, col = RED, lwd = 1.5)
  text(4.42, (dm[4] + gm) / 2, "日平均偏離\n→ s_between", adj = 0, col = RED, cex = 0.95)
  legend("topright", c("單次測值", "當日平均"), pch = c(19, NA), lty = c(NA, 1),
         lwd = c(NA, 3.5), col = c(BLUE, RED), bty = "n", cex = 0.95)
})

# ---- 圖 17-3：失擬檢定（彎曲的標準曲線：直線 vs 各濃度平均；殘差圖）----
conc2 <- rep(c(2, 4, 6, 8, 10, 12), each = 3)
resp2 <- c(197, 191, 200,   371, 375, 371,   541, 548, 547,
           705, 698, 699,   847, 835, 855,   977, 980, 978)
fit_l2 <- lm(resp2 ~ conc2)
fit_q2 <- lm(resp2 ~ conc2 + I(conc2^2))
save_png("fig_ch17_lof.png", w = 1500, h = 700, {
  par(mfrow = c(1, 2), mar = c(4.2, 4.4, 2.6, 1.0))
  lv <- sort(unique(conc2)); mu <- tapply(resp2, conc2, mean)
  # 左：資料 + 直線 + 各濃度平均
  plot(conc2, resp2, pch = 1, col = BLUE, cex = 1.0,
       xlab = "濃度 (mg/L)", ylab = "反應值 (吸光度×1000)",
       main = sprintf("直線配適：r² = %.4f", summary(fit_l2)$r.squared))
  abline(fit_l2, col = RED, lwd = 2)
  points(lv, mu, pch = 18, col = ORANGE, cex = 1.7)
  legend("topleft", c("重複點", "各濃度平均", "迴歸直線"),
         pch = c(1, 18, NA), lty = c(NA, NA, 1), lwd = c(NA, NA, 2),
         col = c(BLUE, ORANGE, RED), bty = "n", cex = 0.9)
  # 右：殘差圖（直線 vs 二次）
  r1 <- residuals(fit_l2); r2 <- residuals(fit_q2)
  plot(conc2 - 0.12, r1, pch = 1, col = RED, ylim = range(c(r1, r2)) * 1.15,
       xlab = "濃度 (mg/L)", ylab = "殘差", main = "殘差圖：直線（紅）vs 加二次項（藍）")
  abline(h = 0, lty = 2, col = GREY)
  lines(lv - 0.12, tapply(r1, conc2, mean), col = RED, lwd = 2, type = "b", pch = 18, cex = 1.4)
  points(conc2 + 0.12, r2, pch = 2, col = BLUE)
  lines(lv + 0.12, tapply(r2, conc2, mean), col = BLUE, lwd = 2, type = "b", pch = 18, cex = 1.4)
  text(7, max(r1) * 1.08, "失擬：平均殘差呈倒 U 形", col = RED, cex = 0.9)
  text(7, min(r1) * 0.55, "純誤差：同濃度重複點\n彼此的上下差距", col = "grey25", cex = 0.85)
})

# ---- 圖 17-4：殘差 SS 的拆解（長條圖：純誤差 vs 失擬；三個模型）----
save_png("fig_ch17_ss_split.png", w = 1400, h = 760, {
  conc <- rep(c(1, 5, 10, 50, 100), each = 3)     # Ch04 咖啡因標準曲線
  area <- c(101, 99, 102, 498, 505, 492, 1005, 992, 1018,
            4930, 5070, 5005, 9720, 10380, 10040)
  split_ss <- function(fit, y, g) {
    pe <- sum((y - ave(y, g))^2); c(純誤差 = pe, 失擬 = sum(residuals(fit)^2) - pe)
  }
  S <- cbind("Ch04 咖啡因\n直線"   = split_ss(lm(area ~ conc), area, conc),
             "飽和曲線\n直線"      = split_ss(fit_l2, resp2, conc2),
             "飽和曲線\n加二次項"  = split_ss(fit_q2, resp2, conc2))
  P <- 100 * sweep(S, 2, colSums(S), "/")
  bp <- barplot(P, col = c("#90CAF9", "#EF9A9A"), border = NA, ylim = c(0, 118),
                ylab = "佔殘差平方和的比例 (%)",
                main = "殘差 SS = 純誤差 SS + 失擬 SS", names.arg = rep("", 3))
  axis(1, at = bp, labels = colnames(P), tick = FALSE, line = 0.9, cex.axis = 0.95)
  text(bp, 104, sprintf("失擬佔 %.1f%%", P["失擬", ]), cex = 0.95)
  legend("top", rownames(P), fill = c("#90CAF9", "#EF9A9A"), border = NA,
         bty = "n", horiz = TRUE, inset = -0.02, cex = 0.95)
})

cat("done: ", paste(list.files(img_dir, pattern = "^fig_ch17_"), collapse = ", "), "\n")
