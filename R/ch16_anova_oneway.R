# =====================================================================
# Ch16 單因子變異數分析 One-way ANOVA 與事後比較
# aov / TukeyHSD / pairwise.t.test / 前提檢查 / Welch ANOVA / Kruskal-Wallis
# 只用 base R；資料直接寫在腳本裡。
# 執行：Rscript R/ch16_anova_oneway.R
# =====================================================================

if (!interactive()) pdf(NULL)              # 用 Rscript 執行時不要產生 Rplots.pdf（圖另見 figures_ch16.R）

# ---------- 1. 建立資料：三種溶劑萃取總多酚 (mg GAE/g)，各 n = 5 ----------
cat("\n## ---- 16.1 資料與敘述統計 ----\n")
# --- 建立資料：一欄是「組別」(factor)，一欄是「量測值」---
solvent <- factor(rep(c("Methanol", "Ethanol", "Acetone"), each = 5),
                  levels = c("Methanol", "Ethanol", "Acetone"))
tpc <- c(12.4, 13.1, 12.8, 11.9, 12.6,     # 甲醇
         13.0, 12.2, 13.5, 12.9, 13.3,     # 乙醇
         14.8, 15.4, 14.5, 15.1, 15.6)     # 丙酮
dat <- data.frame(solvent, tpc)

grp_mean <- tapply(tpc, solvent, mean)     # 各組平均
grp_sd   <- tapply(tpc, solvent, sd)       # 各組標準差
round(rbind(mean = grp_mean, sd = grp_sd), 3)
mean(tpc)                                  # 總平均 (grand mean)

# ---------- 2. 為什麼不能做三次 t 檢定：模擬整體型一錯誤 ----------
cat("\n## ---- 16.2 多次 t 檢定的 alpha 膨脹 ----\n")
k_pairs <- choose(3, 2)                    # 3 組 -> 3 對
1 - 0.95^k_pairs                           # 若三次檢定互相獨立的理論值
round(1 - 0.95^choose(3:6, 2), 3)          # 3,4,5,6 組時的理論值

set.seed(2026)
B <- 2000                                  # 重複 2000 次「H0 為真」的實驗
g3 <- factor(rep(c("A", "B", "C"), each = 5))
any_t   <- logical(B)                      # 三次 t 檢定「任一」顯著？
aov_sig <- logical(B)                      # ANOVA 顯著？
for (b in 1:B) {
  y <- rnorm(15, mean = 13, sd = 0.5)      # 三組其實來自同一個母體
  p_ab <- t.test(y[g3 == "A"], y[g3 == "B"])$p.value
  p_ac <- t.test(y[g3 == "A"], y[g3 == "C"])$p.value
  p_bc <- t.test(y[g3 == "B"], y[g3 == "C"])$p.value
  any_t[b]   <- min(p_ab, p_ac, p_bc) < 0.05
  aov_sig[b] <- summary(aov(y ~ g3))[[1]][["Pr(>F)"]][1] < 0.05
}
c(three_t_tests = mean(any_t), anova = mean(aov_sig))

# ---------- 3. 手算 ANOVA：把總變異拆成 組間 + 組內 ----------
cat("\n## ---- 16.3 手算 ANOVA ----\n")
N <- length(tpc)                           # 總樣本數 15
k <- nlevels(solvent)                      # 組數 3
n_i <- tapply(tpc, solvent, length)        # 各組 n
grand <- mean(tpc)

SS_between <- sum(n_i * (grp_mean - grand)^2)          # 組間：各組平均離總平均多遠
SS_within  <- sum((tpc - ave(tpc, solvent))^2)         # 組內：每筆離自己組平均多遠
SS_total   <- sum((tpc - grand)^2)                     # 總變異
c(SS_between = SS_between, SS_within = SS_within,
  sum = SS_between + SS_within, SS_total = SS_total)

df_between <- k - 1                        # 2
df_within  <- N - k                        # 12
MS_between <- SS_between / df_between
MS_within  <- SS_within  / df_within
F_value <- MS_between / MS_within
p_value <- pf(F_value, df_between, df_within, lower.tail = FALSE)
round(c(MS_between = MS_between, MS_within = MS_within, F = F_value), 4)
p_value
sqrt(MS_within)                            # 合併標準差 (pooled SD)：方法的組內重複性

# ---------- 4. 一行指令：aov() ----------
cat("\n## ---- 16.4 aov() ----\n")
fit <- aov(tpc ~ solvent, data = dat)      # 讀作「tpc 由 solvent 解釋」
summary(fit)
qf(0.95, df_between, df_within)            # F 臨界值 (alpha = 0.05)

# ---------- 5. 事後比較 ----------
cat("\n## ---- 16.5a TukeyHSD ----\n")
tk <- TukeyHSD(fit)
tk
qtukey(0.95, k, df_within) * sqrt(MS_within / 5)   # HSD：兩組平均至少要差這麼多才顯著
plot(tk)                                   # 畫出三個差值的 95% 信賴區間

cat("\n## ---- 16.5b pairwise.t.test (Holm) ----\n")
pairwise.t.test(tpc, solvent, p.adjust.method = "holm")

cat("\n## ---- 16.5c 字母標示 (compact letter display) ----\n")
# 適用「各組 n 相同」的 Tukey 結果：
#  (1) 平均由大到小排序；(2) 找出「彼此全部不顯著」的最長連續區段；
#  (3) 每個區段發一個字母；一組可同時屬於兩個區段 -> 得到 "ab"
cld_simple <- function(fit_aov, alpha = 0.05) {
  fac <- names(fit_aov$xlevels)[1]
  y   <- fit_aov$model[[1]]; g <- fit_aov$model[[2]]
  m   <- sort(tapply(y, g, mean), decreasing = TRUE)      # (1) 由大到小
  nm  <- names(m); kk <- length(nm)
  tkp <- TukeyHSD(fit_aov)[[fac]][, "p adj"]
  ns  <- matrix(TRUE, kk, kk, dimnames = list(nm, nm))   # TRUE = 不顯著
  for (pair in names(tkp)) {
    ab <- strsplit(pair, "-")[[1]]
    ns[ab[1], ab[2]] <- ns[ab[2], ab[1]] <- tkp[[pair]] >= alpha
  }
  runs <- list()
  for (i in 1:kk) {                        # (2) 從第 i 組往下延伸，直到出現顯著差異
    j <- i
    while (j < kk && all(ns[i:(j + 1), i:(j + 1)])) j <- j + 1
    runs[[length(runs) + 1]] <- i:j
  }
  keep <- sapply(seq_along(runs), function(a)             # 丟掉被別的區段完全包住的
    !any(sapply(seq_along(runs), function(b)
      b != a && all(runs[[a]] %in% runs[[b]]) &&
        length(runs[[b]]) > length(runs[[a]]))))
  runs <- runs[keep]
  lab <- setNames(rep("", kk), nm)
  for (r in seq_along(runs)) lab[runs[[r]]] <- paste0(lab[runs[[r]]], letters[r])  # (3) 發字母
  data.frame(mean = round(as.numeric(m), 2), letter = lab)
}
cld_simple(fit)

# 第三組小資料：乾燥溫度對維生素 C 保留率 (%)，示範 "ab"
temp <- factor(rep(c("T40", "T50", "T60"), each = 5))
vitc <- c(86.9, 84.2, 87.6, 85.1, 86.3,    # 40 °C
          85.4, 82.8, 86.0, 83.5, 84.9,    # 50 °C
          83.6, 81.4, 84.3, 82.0, 83.1)    # 60 °C
fit_vc <- aov(vitc ~ temp)
summary(fit_vc)
round(TukeyHSD(fit_vc)$temp, 4)
cld_simple(fit_vc)

# ---------- 6. 前提檢查 ----------
cat("\n## ---- 16.6a 常態性：檢查殘差，不是原始 y ----\n")
res <- residuals(fit)                      # 殘差 = 每筆 - 自己那組的平均
shapiro.test(res)                          # 正確：對殘差
shapiro.test(tpc)                          # 錯誤示範：對原始 y（三組平均不同 -> 本來就不像一個鐘形）
qqnorm(res); qqline(res)                   # 殘差 QQ 圖：點大致沿直線 = OK

# 把 n 加大到每組 20 就看得很清楚：每一組都是「完美常態」，只是平均不同
set.seed(61)
g_demo <- factor(rep(c("G1", "G2", "G3"), each = 20))
y_demo <- rnorm(60, mean = rep(c(12.5, 13.0, 15.0), each = 20), sd = 0.45)
c(raw_y     = shapiro.test(y_demo)$p.value,                      # 對原始 y：被判「非常態」
  residuals = shapiro.test(residuals(aov(y_demo ~ g_demo)))$p.value)  # 對殘差：沒問題

cat("\n## ---- 16.6b n 很小時 Shapiro 幾乎抓不到非常態 ----\n")
set.seed(16)
shapiro_power <- function(n, B = 2000)     # 資料明明是右偏的指數分布
  mean(replicate(B, shapiro.test(rexp(n))$p.value < 0.05))
round(sapply(c(n3 = 3, n5 = 5, n15 = 15, n50 = 50), shapiro_power), 3)

cat("\n## ---- 16.6c 等變異：Bartlett 與手刻 Brown-Forsythe ----\n")
bartlett.test(tpc ~ solvent, data = dat)
# Brown-Forsythe (Levene 的中位數版)：對「離組中位數的絕對距離」再做一次 ANOVA
z <- abs(tpc - ave(tpc, solvent, FUN = median))
summary(aov(z ~ solvent))

# ---------- 7. 前提不成立：四個品牌醬油總氮 (g/100 mL)，各 n = 6 ----------
cat("\n## ---- 16.7 變異不等：三種方法比一比 ----\n")
brand <- factor(rep(c("A", "B", "C", "D"), each = 6))
tn <- c(1.42, 1.45, 1.43, 1.46, 1.44, 1.41,    # A 大廠，批次很穩
        1.52, 1.50, 1.55, 1.51, 1.53, 1.49,    # B 大廠，批次很穩
        1.38, 1.62, 1.25, 1.71, 1.49, 1.30,    # C 小廠，批次差異大
        1.60, 1.33, 1.78, 1.41, 1.69, 1.22)    # D 小廠，批次差異大
round(rbind(mean = tapply(tn, brand, mean), sd = tapply(tn, brand, sd)), 3)

bartlett.test(tn ~ brand)                              # 等變異？
summary(aov(abs(tn - ave(tn, brand, FUN = median)) ~ brand))   # Brown-Forsythe

summary(aov(tn ~ brand))                   # (1) 傳統 ANOVA（假設等變異）
oneway.test(tn ~ brand)                    # (2) Welch ANOVA（不假設等變異）
kruskal.test(tn ~ brand)                   # (3) Kruskal-Wallis（以等級為基礎）
pairwise.t.test(tn, brand, p.adjust.method = "holm", pool.sd = FALSE)  # Welch 版事後比較

# ---------- 8. 效果量 eta^2 與「統計顯著 vs 實務重要」 ----------
cat("\n## ---- 16.8 效果量 ----\n")
eta2 <- SS_between / SS_total
round(eta2, 3)

# 大樣本示範：真實差異最多只有 0.2 mg GAE/g，但每組 n = 100
set.seed(8)
g_big <- factor(rep(c("S1", "S2", "S3"), each = 100))
y_big <- rnorm(300, mean = rep(c(12.6, 12.8, 12.7), each = 100), sd = 0.45)
tab_big <- summary(aov(y_big ~ g_big))[[1]]
tab_big
round(tapply(y_big, g_big, mean), 2)
round(tab_big[["Sum Sq"]][1] / sum(tab_big[["Sum Sq"]]), 3)    # eta^2

# ---------- 9. 報告用表：平均 ± SD 加字母 ----------
cat("\n## ---- 16.9 報告用表 ----\n")
# 用 R 直接排出報告用的表
lt <- cld_simple(fit)
data.frame(solvent = levels(solvent),
           n = as.integer(n_i),
           mean_sd = sprintf("%.2f ± %.2f", grp_mean, grp_sd),
           letter = lt[levels(solvent), "letter"])

# ---------- 10. Excel 對照：F.DIST.RT 與 F.INV.RT ----------
cat("\n## ---- 16.10 Excel 對照 ----\n")
pf(42.26, 2, 12, lower.tail = FALSE)       # = F.DIST.RT(42.26, 2, 12)
qf(0.05, 2, 12, lower.tail = FALSE)        # = F.INV.RT(0.05, 2, 12)

# ---------- 11. 章末測驗計算題的驗算 ----------
cat("
## ---- 16.11 測驗題驗算 ----
")
# ch16-p02（前測）：k = 3, N = 12, SS_between = 8.0, SS_within = 9.0 -> F ?
c(correct = (8.0 / 2) / (9.0 / 9), no_df = 8.0 / 9.0, df_k_N = (8.0 / 3) / (9.0 / 12))
# ch16-q03：k = 4, N = 20, SS_between = 5.40, SS_within = 4.80 -> F ?
c(correct = (5.40 / 3) / (4.80 / 16), no_df = 5.40 / 4.80, df_k_N = (5.40 / 4) / (4.80 / 20))
pf(6, 3, 16, lower.tail = FALSE)           # 對應的 p 值
# ch16-q04：同一張表的 eta^2 ?
c(correct = 5.40 / (5.40 + 4.80), over_within = 5.40 / 4.80, within_on_top = 4.80 / (5.40 + 4.80))
# ch16-q05：5 組兩兩比較的對數與「至少一次假警報」的理論機率
c(pairs = choose(5, 2), fw = 1 - 0.95^choose(5, 2), fw_if_5_tests = 1 - 0.95^5, add_up = 0.05 * choose(5, 2))
# ch16-s01（回溯 Ch05）：乙醇組的 12.2 算不算異常值？Dixon Q (n = 5, Q0.90 = 0.64)
eth <- sort(tpc[solvent == "Ethanol"])
(eth[2] - eth[1]) / (eth[5] - eth[1])      # Q < 0.64 -> 連統計上都不能刪
