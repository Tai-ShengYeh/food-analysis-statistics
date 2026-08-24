# =====================================================================
# figures.R —— 產生教材 HTML 所需的全部圖片 (assets/img/*.png)
# 執行：setwd 到本專案根目錄後 source("R/figures.R")
# =====================================================================

img_dir <- "assets/img"
dir.create(img_dir, showWarnings = FALSE, recursive = TRUE)
# Windows R 若繼承到無效的 C.UTF-8，中文會被當成位元組而產生亂碼。
# 先切換到 Windows 可用的繁體中文 UTF-8，再由 cairo 的 sans 字型回退處理 CJK。
if (.Platform$OS.type == "windows") {
  suppressWarnings(Sys.setlocale("LC_CTYPE", "Chinese (Traditional)_Taiwan.utf8"))
}
cjk_font <- "Microsoft JhengHei"
save_png <- function(name, expr, w = 900, h = 560) {
  grDevices::png(file.path(img_dir, name), width = w, height = h,
                 res = 130, type = "cairo", family = cjk_font)
  on.exit(dev.off())
  par(mar = c(4.2, 4.2, 3, 1.5), mgp = c(2.4, 0.7, 0),
      family = cjk_font)
  expr
}

# ---- fig01: 準確度 vs 精密度 四個靶 (Nielsen Fig 4.1) ----
save_png("fig_target.png", w = 1680, h = 480, {
  par(mfrow = c(1, 4), mar = c(1.0, 0.8, 1.0, 0.8))
  draw_target <- function(pts) {
    plot(NA, xlim = c(-3, 3), ylim = c(-3, 3), asp = 1, axes = FALSE,
         xlab = "", ylab = "", main = "")
    symbols(0, 0, circles = 2.8, add = TRUE, inches = FALSE,
            fg = "grey60", lwd = 2)
    symbols(0, 0, circles = 1.8, add = TRUE, inches = FALSE, fg = "grey70")
    symbols(0, 0, circles = 0.9, add = TRUE, inches = FALSE, fg = "grey80")
    points(0, 0, pch = 21, cex = 2.4, col = "red", bg = "red")
    points(pts, pch = 19, cex = 1.5, col = "#1565C0")
    box(col = "grey50")
  }
  set.seed(11)
  draw_target(cbind(rnorm(7, 0, .25), rnorm(7, 0, .25)))
  draw_target(cbind(rnorm(7, 1.6, .25), rnorm(7, .9, .25)))
  draw_target(cbind(rnorm(7, 0, 1.15), rnorm(7, 0, 1.15)))
  draw_target(cbind(rnorm(7, 1.5, 1.1), rnorm(7, 1.2, 1.1)))
})

# ---- fig02: 常態分配 68-95-99.7 ----
save_png("fig_normal.png", {
  x <- seq(-4, 4, length.out = 600)
  y <- dnorm(x)
  cols <- c("#BBDEFB", "#64B5F6", "#1976D2")
  plot(x, y, type = "n", main = "常態分配與 68-95-99.7 法則",
       xlab = "偏離平均數的標準差倍數", ylab = "機率密度")
  shade <- function(lo, hi, col) {
    xx <- x[x >= lo & x <= hi]
    polygon(c(xx, rev(xx)), c(dnorm(xx), rev(dnorm(xx))),
            col = col, border = NA)
  }
  shade(-1, 1, cols[3])
  shade(-2, -1, cols[2]); shade(1, 2, cols[2])
  shade(-3, -2, cols[1]); shade(2, 3, cols[1])
  lines(x, y, lwd = 2)
  abline(v = 0, lty = 2, col = "grey30")
  text(0, .13, "68%", col = "white", cex = 1.4, font = 2)
  text(1.55, .05, "95%", col = "black", cex = 1.3, font = 2)
  text(-1.55, .05, "95%", col = "black", cex = 1.3, font = 2)
  text(2.55, .018, "99.7%", cex = 1.05, font = 2)
  text(-2.55, .018, "99.7%", cex = 1.05, font = 2)
})

# ---- fig03: Shewhart 管制圖 ----
save_png("fig_shewhart.png", {
  set.seed(7)
  qc <- round(rnorm(25, 12.00, 0.15), 3)
  qc[8:11] <- qc[8:11] + 0.28
  qc[18]   <- 12.62
  days <- 1:25; t0 <- 12; s <- 0.15
  plot(days, qc, type = "b", pch = 19, col = "#1565C0",
       ylim = c(t0-.75, t0+.75), main = "Shewhart 管制圖（蛋白質 QC）",
       xlab = "分析日", ylab = "測值 (%)", xaxt = "n")
  axis(1, at = seq(0, 25, 5))
  abline(h = t0); text(0.4, t0+.04, "CL", adj = 0, cex=.85)
  for (v in c(t0+2*s, t0-2*s)) { abline(h=v, col="orange", lty=2) }
  for (v in c(t0+3*s, t0-3*s)) { abline(h=v, col="red", lty=2) }
  text(0.4, t0+2*s+.04, "+2s 警告界限", adj = 0, col = "orange", cex=.85)
  text(0.4, t0-2*s-.12, "-2s 警告界限", adj = 0, col = "orange", cex=.85)
  text(0.4, t0+3*s+.04, "+3s 行動界限", adj = 0, col = "red", cex=.85)
  text(0.4, t0-3*s-.12, "-3s 行動界限", adj = 0, col = "red", cex=.85)
  bad <- qc > t0+3*s | qc < t0-3*s
  points(days[bad], qc[bad], pch = 1, cex = 3.2, col = "red", lwd = 3)
})

# ---- fig04: CuSum ----
save_png("fig_cusum.png", {
  set.seed(7)
  qc <- rnorm(25, 12.00, 0.15); qc[8:11] <- qc[8:11] + 0.28
  cs <- cumsum(qc - 12)
  plot(1:25, cs, type = "b", pch = 19, col = "#2E7D32",
       main = "CuSum 累積和管制圖（偵測小漂移）",
       xlab = "分析日", ylab = "累積偏差")
  abline(h = 0, lty = 2)
  arrows(8, cs[8]-1.2, 8, cs[8]+0.4, lwd=2, col="firebrick", length=.08)
  text(8, cs[8]-1.5, "第8~11天加入 +0.28 的漂移", col="firebrick", pos=1, cex=.9)
})

# ---- fig05: 鈉標準曲線 + 信賴帶 ----
save_png("fig_calib_ci.png", {
  x <- c(1,3,5,10,20); y <- c(.050,.140,.242,.521,.998)
  fit <- lm(y ~ x)
  nx <- seq(0.5, 20.5, len = 120)
  ci <- predict(fit, data.frame(x = nx), interval = "confidence")
  matplot(nx, ci[, c("lwr","fit","upr")], type = "l",
          lty = c(2,1,2), col = c("grey45","red","grey45"), lwd = c(1.5,2,1.5),
          main = "標準曲線與 95% 信賴帶",
          xlab = "Na 濃度 (ug/mL)", ylab = "發射訊號 (589 nm)")
  points(x, y, pch = 19, col = "#1565C0")
  legend("topleft", bty = "n",
         legend = c("量測點", expression(y == 0.0504*x - 0.0029),
                    "95% 信賴帶"),
         pch = c(19, NA, NA), lty = c(NA,1,2),
         col = c("#1565C0","red","grey45"))
})

# ---- fig06: 殘差圖 ----
save_png("fig_residual.png", {
  x <- c(1,3,5,10,20); y <- c(.050,.140,.242,.521,.998)
  fit <- lm(y ~ x)
  plot(x, residuals(fit), pch = 19, col = "#EF6C00", ylim = c(-.05,.05),
       main = "殘差圖（應隨機分布於 0 附近）",
       xlab = "濃度", ylab = "殘差")
  abline(h = 0, lty = 2)
  # 對照組：把直線硬套在彎曲資料上
  set.seed(3)
  xb <- seq(1, 20, len = 10)
  yb <- 0.05*xb + 0.012*xb^2 + rnorm(10, 0, .05)
  fitb <- lm(yb ~ xb)
  points(xb, residuals(fitb), pch = 17, col = "#7B1FA2")
  legend("bottomright", c("直線資料的殘差", "曲線資料硬配直線"),
         pch = c(19,17), col = c("#EF6C00","#7B1FA2"), bty = "n")
})

# ---- fig07: Type B 三種分布 ----
save_png("fig_distributions.png", {
  xs <- seq(-1, 1, length.out = 500)
  rect_d <- dunif(xs, -.9, .9)
  tri_d  <- ifelse(abs(xs) <= .9, (.9-abs(xs))/.9^2, 0)
  norm_d <- dnorm(xs, sd = .45)
  plot(xs, rect_d, type = "l", lwd = 2.5, col = "#1565C0",
       ylim = c(0, 1.3), main = "Type B 評估的三種分布 (同樣 ±a)",
       xlab = "相對偏移", ylab = "機率密度")
  lines(xs, tri_d, col = "#EF6C00", lwd = 2.5)
  lines(xs, norm_d, col = "#2E7D32", lwd = 2.5)
  legend("topright", inset=.02, c("矩形 u=a/√3 (最保守)",
         "三角形 u=a/√6", "常態 u=a/1.96"),
         col = c("#1565C0","#EF6C00","#2E7D32"), lwd = 2.5, bty="n")
})

# ---- fig08: 不準度預算長條圖 (Cd 案例) ----
save_png("fig_budget.png", {
  contrib <- c("體積 V"=1002.7*0.07/100, "質量 m"=1002.7*0.05/100.28,
               "純度 P"=1002.7*0.000058/0.9999)
  bp <- barplot(contrib, col = c("#1E88E5","#43A047","#FDD835"),
                ylim = c(0, .85), las = 1, border = NA,
                main = "鎘標準液的不準度預算 (uncertainty budget)",
                ylab = "貢獻量 |u(y,x)| mg/L")
  text(bp[,1], contrib + .04, sprintf("%.2f", contrib), font = 2)
  uc <- sqrt(sum(contrib^2))
  mtext(sprintf("uc = √(Σ貢獻²) = %.2f mg/L -> U(k=2) = %.1f mg/L",
                uc, 2*uc), side = 1, line = -1.5, cex = .95, outer = FALSE)
})

# ---- fig09: Monte Carlo 直方圖 ----
save_png("fig_montecarlo.png", {
  set.seed(2024); N <- 100000
  y <- 1000 * rnorm(N, 100.28, .05) * rnorm(N, .9999, .000058) /
       rnorm(N, 100, .07)
  hist(y, breaks = 120, col = "#90CAF9", freq = FALSE, border = "white",
       main = "Monte Carlo 模擬 100000 次配製鎘標準液",
       xlab = "c(Cd) mg/L", ylab = "密度")
  q <- quantile(y, c(.025,.975))
  abline(v = mean(y), col = "red", lwd = 2)
  abline(v = q, col = "#6A1B9A", lty = 2, lwd = 2)
  text(mean(y)+.4, max(density(y)$y)*.95, paste0("GUM 點估計 ", round(mean(y),1)), col="red", adj=0)
  text(q[2]+.4, max(density(y)$y)*.82, sprintf("MC 95%% 區間 [%.1f, %.1f]", q[1], q[2]),
       col="#6A1B9A", adj=0)
})

# ---- fig10: 符合性判定四情境 (QUAM Figure 2) ----
save_png("fig_compliance.png", {
  par(mfrow = c(1, 4)); U <- 1; L <- 10
  cases <- list(c(i = 11.5), c(ii = 10.6), c(iii = 9.6), c(iv = 8.8))
  verdicts <- c("不符合", "灰色地帶", "灰色地帶", "符合")
  cols     <- c("firebrick", "darkorange", "darkorange", "forestgreen")
  for (k in 1:4) {
    res <- as.numeric(cases[[k]])
    plot(NA, xlim = c(6, 14), ylim = c(0, 1), axes = FALSE,
         xlab = "", ylab = "",
         main = names(cases[[k]]))
    axis(1, at = 6:14)
    abline(v = L, col = "black", lwd = 2)
    text(L, 1.06, "法規上限 L", pos = 2, cex = .9, xpd = TRUE)
    arrows(res - U, .5, res + U, .5, code = 3, angle = 90,
           length = .08, lwd = 3, col = cols[k])
    points(res, .5, pch = 19, cex = 1.6, col = cols[k])
    mtext(sprintf("result=%.1f ±%.1f", res, U), side = 1, line = 2.4, cex = .85)
    mtext(verdicts[k], side = 3, line = -1.6, col = cols[k], font = 2)
    box(col = "grey60")
  }
})

# ---- fig11: 內插濃度不準度隨濃度變化 (E.4) ----
save_png("fig_pred_unc.png", {
  x <- c(1,3,5,10,20); y <- c(.050,.140,.242,.521,.998)
  f <- lm(y ~ x); b1 <- coef(f)[2]; S <- summary(f)$sigma
  n <- 5; p <- 3; xb <- mean(x); Sxx <- sum((x-xb)^2)
  nx <- seq(1, 20, len = 60)
  Ux <- 2*sapply(nx, function(xp) sqrt((S^2/b1^2)*(1/p + 1/n + (xp-xb)^2/Sxx)))
  plot(nx, Ux, type = "l", lwd = 2.5, col = "#6A1B9A",
       main = "由標準曲線反推濃度的 95% 不準度",
       xlab = "反推濃度 (ug/mL)", ylab = "±U (ug/mL)")
  rug(x, lwd = 2, col = "#1565C0")   # 校正點位置
  text(mean(x), max(Ux)*.92,
       "校正點越密集處、靠近中心 => 反推最可靠", cex = .95)
})

# ---- fig12: 滴定魚骨圖 (QUAM Figure A2.6 簡化版) ----
save_png("fig_fishbone.png", w = 1500, h = 780, {
  plot(NA, xlim = c(0, 10), ylim = c(0, 6), axes = FALSE,
       xlab = "", ylab = "", main = "滴定標定的因果(魚骨)圖：不準度來源")
  segments(0.3, 3, 8.2, 3, lwd = 3)                     # 主骨
  text(8.55, 3, "c(NaOH)\n相對不準度", font = 2, cex = 1.15)
  rib <- function(x0, y0, x1, y1, label, side) {
    segments(x0, y0, x1, y1, lwd = 2)
    text(x0 - 0.12, (y0 + y1)/2, label, pos = side, cex = 0.95)
  }
  # 上方三根：重複性 / 稱重 / 純度
  rib(2.0, 3, 2.6, 5.0, "重複性 rep\n(u=0.0005)", 2)
  rib(3.6, 3, 4.4, 5.0, "稱重 m(KHP)\n校正+線性+重複\n(u=0.00013 g)", 2)
  rib(5.2, 3, 5.8, 5.0, "純度 P(KHP)\n證書 ±0.0005\n矩形 -> 0.00029", 2)
  # 下方兩根：莫耳質量 / 滴定體積
  rib(1.8, 3, 2.4, 1.0, "莫耳質量 M\nIUPAC 原子量\n(0.000019, 可忽略)", 1)
  rib(4.6, 3, 5.4, 1.0,
      "滴定體積 V_T\n校正 0.004 + 溫度 0.009\n+ 終點 0.002 -> 0.013 mL", 1)
  # 小骨裝飾
  for (xx in seq(1.2, 7.8, by = 0.8))
    segments(xx, 3 - 0.35, xx + 0.3, 3, lwd = 1, col = "grey70")
  text(5.4, 0.55,
       "最大主因：滴定體積 V_T (52%) 與重複性 (27%)",
       col = "firebrick", font = 2, cex = 1.05)
})

# ---- fig13: 三大案例預算比較 ----
save_png("fig_cases.png", w = 1500, h = 620, {
  par(mfrow = c(1, 3))
  # (1) 天平 (對 c(Cd) 的貢獻, mg/L)
  b <- c("體積 V" = 0.702, "質量 m" = 0.547, "純度 P" = 0.058)
  barplot(b, col = "#1E88E5", border = NA, las = 1, ylim = c(0, .85),
          main = "案例① 天平稱量\n(c=1000mP/V 的貢獻)",
          ylab = "|u(y,x)| mg/L")
  text(1.6, b + .05, sprintf("%.2f", b), font = 2)
  # (2) 滴定 (變異數占比 %)
  t <- c("V_T" = 52.2, "重複性" = 26.8, "稱重" = 12.0, "純度" = 9.0)
  barplot(sort(t, decreasing = TRUE), col = "#43A047", border = NA,
          las = 1, ylim = c(0, 60), main = "案例② NaOH 滴定標定\n(變異數占比)",
          ylab = "%")
  # (3) HPLC (變異數占比 %)
  h <- c("精密度" = 63.3, "均勻性" = 34.7, "回收率" = 2.0)
  barplot(sort(h, decreasing = TRUE), col = "#F6A21D", border = NA,
          las = 1, ylim = c(0, 70), main = "案例③ HPLC/GC 農藥\n(變異數占比)",
          ylab = "%")
})
# ---- fig14: LC-MS/MS 基質效應與預算 ----
save_png("fig_lcmsms.png", w = 1500, h = 620, {
  par(mfrow = c(1, 2))
  # (a) Matuszewski 三條校正線
  cc <- c(0, 0.1, 0.2, 0.3, 0.4, 0.5)
  plot(cc, 45200*cc, type = "b", pch = 17, col = "#2E7D32", lwd = 2,
       ylim = c(0, 24000), xlab = "氯黴素 (ug/kg)",
       ylab = "波峰面積",
       main = "Matuszewski 基質效應實驗")
  lines(cc, 38400*cc, type = "b", pch = 16, col = "#1565C0", lwd = 2)
  lines(cc, 34600*cc, type = "b", pch = 15, col = "#C62828", lwd = 2)
  legend("topleft", inset = c(0.02, 0.02), bty = "n", cex = 0.85,
         legend = c("溶液標準 (斜率45200)",
                    "萃取後添加 (38400) -> ME -15%",
                    "添加後萃取 (34600) -> RE -10%"),
         col = c("#2E7D32", "#1565C0", "#C62828"),
         pch = c(17, 16, 15), lwd = 2)
  # (b) 預算
  h <- c("中間精密度" = 59.8, "樣品均勻性" = 27.8,
         "校正+基質" = 7.9, "回收率" = 4.4)
  barplot(h, col = c("#1E88E5", "#43A047", "#F6A21D", "#8E24AA"),
          border = NA, las = 1, ylim = c(0, 70),
          main = "LC-MS/MS 氯黴素：變異數占比",
          ylab = "%")
})