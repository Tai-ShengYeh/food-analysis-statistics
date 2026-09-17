# =====================================================================
# figures_ch16.R —— 產生 Ch16 (One-way ANOVA) 所需圖片
# 輸出：assets/img/fig_ch16_*.png（寬 1400 px, res = 160）
# 執行：在專案根目錄 Rscript R/figures_ch16.R
# =====================================================================

img_dir <- "assets/img"
dir.create(img_dir, showWarnings = FALSE, recursive = TRUE)
# Windows R 若繼承到無效的 C.UTF-8，中文會變亂碼：先切到繁中 UTF-8
if (.Platform$OS.type == "windows") {
  invisible(suppressWarnings(Sys.setlocale("LC_CTYPE", "Chinese (Traditional)_Taiwan.utf8")))
}
cjk_font <- "Microsoft JhengHei"
save_png <- function(name, expr, w = 1400, h = 860) {
  grDevices::png(file.path(img_dir, name), width = w, height = h,
                 res = 160, type = "cairo", family = cjk_font)
  on.exit(dev.off())
  par(mar = c(4.2, 4.4, 3, 1.5), mgp = c(2.5, 0.7, 0), family = cjk_font)
  expr
}

# ---- 與 ch16_anova_oneway.R 相同的主範例資料 ----
solvent <- factor(rep(c("Methanol", "Ethanol", "Acetone"), each = 5),
                  levels = c("Methanol", "Ethanol", "Acetone"))
tpc <- c(12.4, 13.1, 12.8, 11.9, 12.6,
         13.0, 12.2, 13.5, 12.9, 13.3,
         14.8, 15.4, 14.5, 15.1, 15.6)
fit <- aov(tpc ~ solvent)
grp_mean <- tapply(tpc, solvent, mean)
grand <- mean(tpc)
cols <- c("#1976D2", "#2E7D32", "#E65100")
zh <- c("甲醇 Methanol", "乙醇 Ethanol", "丙酮 Acetone")

# ---- fig 1：分組盒鬚圖 + 原始點 + 平均 ----
save_png("fig_ch16_boxplot.png", {
  boxplot(tpc ~ solvent, names = zh, col = adjustcolor(cols, 0.18),
          border = cols, boxwex = 0.45, outline = FALSE,
          ylim = c(11.5, 16.4), xlab = "萃取溶劑",
          ylab = "總多酚 (mg GAE/g)",
          main = "三種溶劑的總多酚萃取量（各 n = 5）")
  set.seed(1)
  points(jitter(as.numeric(solvent), amount = 0.08), tpc, pch = 19,
         col = cols[as.numeric(solvent)], cex = 1.1)
  points(1:3, grp_mean, pch = 23, bg = "white", col = "black", cex = 1.7, lwd = 2)
  abline(h = grand, lty = 2, col = "grey40")
  text(3.47, grand + 0.13, sprintf("總平均 %.2f", grand), col = "grey30",
       cex = 0.85, adj = 1)
  text(1:3, c(13.32, 13.95, 16.05), c("b", "b", "a"), font = 2, cex = 1.4)
  legend("topleft", bty = "n", cex = 0.85,
         legend = c("單次量測", "組平均", "a, b = Tukey 字母標示"),
         pch = c(19, 23, NA), pt.bg = "white", col = c("grey30", "black", NA))
})

# ---- fig 2：組間 vs 組內變異示意 ----
save_png("fig_ch16_partition.png", h = 900, {
  x <- 1:15
  plot(x, tpc, type = "n", xaxt = "n", ylim = c(11.5, 16.2),
       xlab = "", ylab = "總多酚 (mg GAE/g)",
       main = "總變異 = 組間變異 + 組內變異")
  axis(1, at = c(3, 8, 13), labels = zh, tick = FALSE)
  abline(v = c(5.5, 10.5), col = "grey85")
  abline(h = grand, lty = 2, lwd = 1.5, col = "grey35")
  for (j in 1:3) {
    idx <- ((j - 1) * 5 + 1):(j * 5)
    segments(min(idx) - 0.35, grp_mean[j], max(idx) + 0.35, grp_mean[j],
             col = cols[j], lwd = 3)
    # 組內：每筆到自己組平均（細實線）
    segments(idx, tpc[idx], idx, grp_mean[j], col = cols[j], lwd = 1.6)
    # 組間：組平均到總平均（粗箭頭）
    arrows(max(idx) + 0.32, grand, max(idx) + 0.32, grp_mean[j], length = 0.08,
           code = 3, lwd = 3, col = "#B71C1C")
  }
  points(x, tpc, pch = 19, col = cols[as.numeric(solvent)], cex = 1.2)
  text(0.7, grand + 0.16, sprintf("總平均 %.2f", grand), adj = 0, cex = 0.85,
       col = "grey25")
  legend("topleft", bty = "n", cex = 0.88,
         legend = c("組內變異：每筆數據 到 自己組平均（隨機誤差）",
                    "組間變異：組平均 到 總平均（溶劑效應 + 隨機誤差）"),
         lwd = c(1.6, 3), col = c("grey30", "#B71C1C"))
})

# ---- fig 3：TukeyHSD 95% 信賴區間 ----
save_png("fig_ch16_tukey.png", h = 760, {
  tk <- TukeyHSD(fit)$solvent
  par(mar = c(4.4, 10.5, 3, 1.5))
  yy <- nrow(tk):1
  plot(tk[, "diff"], yy, xlim = range(c(tk[, c("lwr", "upr")], -0.6)),
       ylim = c(0.5, nrow(tk) + 0.5), pch = 19, yaxt = "n", cex = 1.3,
       xlab = "兩組平均的差 (mg GAE/g) 與 95% family-wise 信賴區間",
       ylab = "", main = "TukeyHSD：區間跨過 0 = 兩組差異不顯著")
  sig <- tk[, "p adj"] < 0.05
  segments(tk[, "lwr"], yy, tk[, "upr"], yy, lwd = 3,
           col = ifelse(sig, "#B71C1C", "grey45"))
  points(tk[, "diff"], yy, pch = 19, cex = 1.3,
         col = ifelse(sig, "#B71C1C", "grey45"))
  abline(v = 0, lty = 2)
  axis(2, at = yy, labels = rownames(tk), las = 1)
  text(tk[, "upr"], yy + 0.25, adj = 1, cex = 0.85,
       labels = sprintf("p adj = %s", format.pval(tk[, "p adj"], digits = 2, eps = 1e-4)))
})

# ---- fig 4：QQ 圖——原始 y vs 殘差 ----
save_png("fig_ch16_qq.png", h = 720, {
  par(mfrow = c(1, 2), mar = c(4.2, 4.4, 3, 1), family = cjk_font)
  qqnorm(tpc, pch = 19, col = cols[as.numeric(solvent)],
         main = "錯誤：對原始 y 畫 QQ 圖", xlab = "理論分位數", ylab = "樣本分位數")
  qqline(tpc, lty = 2)
  res <- residuals(fit)
  qqnorm(res, pch = 19, col = cols[as.numeric(solvent)],
         main = "正確：對殘差畫 QQ 圖", xlab = "理論分位數", ylab = "殘差的樣本分位數")
  qqline(res, lty = 2)
})

cat("figures written:\n")
print(list.files(img_dir, pattern = "^fig_ch16_"))
