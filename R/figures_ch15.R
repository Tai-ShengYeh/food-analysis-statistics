# =====================================================================
# figures_ch15.R —— 產生 Ch15 假說檢定所需圖片 (assets/img/fig_ch15_*.png)
# 執行：在專案根目錄 Rscript R/figures_ch15.R
# 資料與 R/ch15_hypothesis_tests.R 完全相同
# =====================================================================

img_dir <- "assets/img"
dir.create(img_dir, showWarnings = FALSE, recursive = TRUE)
# Windows R 若繼承到無效的 C.UTF-8，中文會變亂碼；先切到繁中 UTF-8
if (.Platform$OS.type == "windows") {
  suppressWarnings(Sys.setlocale("LC_CTYPE", "Chinese (Traditional)_Taiwan.utf8"))
}
cjk_font <- "Microsoft JhengHei"
save_png <- function(name, expr, w = 1400, h = 760) {
  grDevices::png(file.path(img_dir, name), width = w, height = h,
                 res = 160, type = "cairo", family = cjk_font)
  on.exit(dev.off())
  par(mar = c(4.2, 4.2, 3, 1.5), mgp = c(2.4, 0.7, 0), family = cjk_font)
  expr
}
col_blue <- "#1565C0"; col_red <- "#C62828"; col_org <- "#F6A21D"
col_grn  <- "#2E7D32"

# ---- 圖 15-1：t 分布、拒絕域與 p 值（CRM 例：t = -3.07, df = 5）----
crm  <- c(34.92, 35.12, 34.85, 35.04, 34.81, 34.98)
tobs <- (mean(crm) - 35.10) / (sd(crm) / sqrt(6))
tc   <- qt(0.975, 5)
save_png("fig_ch15_tdist.png", {
  x <- seq(-5.5, 5.5, length.out = 800)
  y <- dt(x, 5)
  plot(x, y, type = "n", ylim = c(0, 0.52), yaxs = "i",
       main = "H0 為真時 t 統計量的分布（df = 5）",
       xlab = "t 值", ylab = "機率密度")
  shade <- function(lo, hi, col, ...) {
    xx <- x[x >= lo & x <= hi]
    polygon(c(lo, xx, hi), c(0, dt(xx, 5), 0), col = col, border = NA, ...)
  }
  shade(-5.5, -tc, "#F5B7B1"); shade(tc, 5.5, "#F5B7B1")        # 拒絕域
  shade(-5.5, -abs(tobs), col_red); shade(abs(tobs), 5.5, col_red)  # p 值
  lines(x, y, lwd = 2.2, col = "grey20")
  abline(v = c(-tc, tc), lty = 2, col = col_red)
  abline(v = tobs, lwd = 2.4, col = col_blue)
  text(0, 0.17, "不拒絕 H0\n（中間 95%）", cex = 1.0, col = "grey25")
  text(-tc, 0.385, sprintf("臨界值 -%.2f", tc), col = col_red, cex = 0.9, pos = 4)
  text(tc, 0.385, sprintf("臨界值 +%.2f", tc), col = col_red, cex = 0.9, pos = 2)
  text(tobs, 0.26, sprintf("觀察到的\nt = %.2f", tobs), col = col_blue,
       pos = 2, cex = 0.95)
  text(-4.4, 0.075, "拒絕域\n（α/2 = 2.5%）", col = col_red, cex = 0.85)
  text(4.4, 0.075, "拒絕域\n（α/2 = 2.5%）", col = col_red, cex = 0.85)
  legend("top", bty = "n", cex = 0.85,
         fill = c("#F5B7B1", col_red), border = NA,
         legend = c("拒絕域：兩尾合計 α = 5%",
                    "p 值：比 |t| = 3.07 更極端的面積 = 0.028"))
})

# ---- 圖 15-2：成對設計（凱氏法 vs 杜馬斯法）----
kjeldahl <- c(3.12, 3.85, 3.41, 6.92, 11.85, 12.48, 20.35, 23.10, 36.42, 35.18)
dumas    <- c(3.20, 4.07, 3.37, 7.11, 11.95, 12.79, 20.37, 23.36, 36.65, 35.30)
d <- dumas - kjeldahl
save_png("fig_ch15_paired.png", h = 720, {
  par(mfrow = c(1, 2), mar = c(4.2, 4.4, 3.2, 1.2))
  # 左：原始值，樣品間差異巨大，方法差異幾乎看不到
  plot(NA, xlim = c(0.6, 2.4), ylim = c(0, 40), xaxt = "n",
       xlab = "", ylab = "粗蛋白 (%)", main = "原始數據：線幾乎是平的")
  axis(1, at = 1:2, labels = c("凱氏法", "杜馬斯法"))
  segments(1, kjeldahl, 2, dumas, col = "grey55", lwd = 1.6)
  points(rep(1, 10), kjeldahl, pch = 19, col = col_blue, cex = 1.2)
  points(rep(2, 10), dumas, pch = 19, col = col_org, cex = 1.2)
  text(1.5, 29.5, "樣品間 SD 約 12.6%\n方法差只有 0.15%", cex = 0.85, col = "grey25")
  # 右：差值，把樣品間差異消掉之後
  plot(d, 1:10, xlim = c(-0.15, 0.46), ylim = c(0.5, 11.6), pch = 19,
       col = col_grn, cex = 1.3,
       yaxt = "n", xlab = "差值 d = 杜馬斯 - 凱氏 (%)", ylab = "樣品編號",
       main = "每個樣品自己跟自己比")
  axis(2, at = 1:10, las = 1, cex.axis = 0.8)
  abline(v = 0, lty = 2, col = col_red, lwd = 1.8)
  ci <- t.test(d)$conf.int
  rect(ci[1], 0.5, ci[2], 10.5, col = adjustcolor(col_grn, 0.15), border = NA)
  abline(v = mean(d), col = col_grn, lwd = 2.2)
  text(0, 11.2, "H0：d = 0", col = col_red, cex = 0.8, pos = 2)
  text(mean(d) + 0.008, 11.2, "平均 0.149，95% CI 不含 0", col = col_grn, cex = 0.8,
       pos = 4, offset = 0)
})

# ---- 圖 15-3：檢定力曲線（delta = 0.2, sd = 0.15）----
save_png("fig_ch15_power.png", {
  ns  <- 2:20
  p20 <- sapply(ns, function(k) power.t.test(n = k, delta = 0.2, sd = 0.15)$power)
  p10 <- sapply(ns, function(k) power.t.test(n = k, delta = 0.1, sd = 0.15)$power)
  plot(ns, p20, type = "b", pch = 19, col = col_blue, lwd = 2, ylim = c(0, 1),
       xlab = "每組重複次數 n", ylab = "檢定力（抓到真實差異的機率）",
       main = "重複次數與檢定力（SD = 0.15%，α = 0.05，雙尾兩樣本 t）")
  lines(ns, p10, type = "b", pch = 17, col = col_org, lwd = 2)
  abline(h = 0.8, lty = 2, col = col_red)
  text(2, 0.84, "慣用目標：檢定力 0.80", col = col_red, cex = 0.85, pos = 4)
  points(3, p20[ns == 3], cex = 2.4, col = col_red, lwd = 2)
  text(3.3, p20[ns == 3] - 0.02, "n = 3：只有 24%", col = col_red, cex = 0.85, pos = 4)
  points(10, p20[ns == 10], cex = 2.4, col = col_grn, lwd = 2)
  text(10.2, p20[ns == 10] - 0.06, "n = 10：80%", col = col_grn, cex = 0.85, pos = 4)
  legend("bottomright", bty = "n", cex = 0.9, lwd = 2, pch = c(19, 17),
         col = c(col_blue, col_org),
         legend = c("想偵測的差異 = 0.2%", "想偵測的差異 = 0.1%"))
})
cat("done: fig_ch15_tdist.png, fig_ch15_paired.png, fig_ch15_power.png\n")
