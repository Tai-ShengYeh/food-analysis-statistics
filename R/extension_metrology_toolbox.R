# =====================================================================
# 延伸單元：metRology 專業工具箱
# GUM / Kragten / Monte Carlo / 不準度貢獻比較
# =====================================================================

# 本單元是選修；前 10 章仍只使用 base R。
if (!requireNamespace("metRology", quietly = TRUE)) {
  stop("尚未安裝 metRology。請先執行 install.packages('metRology')，再重新執行本檔。")
}

cat("metRology version:",
    as.character(utils::packageVersion("metRology")), "\n")

# ---------- 1. 鎘標準液：沿用第 9–10 章資料 ----------
# 測量模型 c(Cd) = 1000 * m * P / V  [mg/L]
x <- list(
  m = 100.28,       # 鎘金屬質量，mg
  P = 0.9999,       # 純度，無因次
  V = 100.0         # 定容量積，mL
)

u <- list(
  m = 0.05,         # u(m)，mg
  P = 0.000058,     # u(P)
  V = 0.07          # u(V)，mL
)

model <- ~ 1000 * m * P / V

# ---------- 2. GUM 一階傳遞 ----------
gum <- metRology::uncert(
  model,
  x = x,
  u = u,
  method = "GUM"
)

gum                     # 完整輸出
gum$y                   # 測量結果，約 1002.7 mg/L
gum$u                   # 合成標準不準度 uc，約 0.864 mg/L
metRology::contribs(gum) # 各來源的變異貢獻

# GUM() 介面另外提供有效自由度、k 與擴展不準度 U。
gum_report <- metRology::GUM(
  var.name = c("m", "P", "V"),
  x.i = unlist(x),
  u.i = unlist(u),
  nu.i = c(9999, 9999, 9999),
  measurement.fnc = "1000*m*P/V",
  cl = 0.95
)

c(y = gum_report$y,
  uc = gum_report$uc,
  nu_eff = gum_report$nu.eff,
  k = gum_report$k,
  U = gum_report$U)

# ---------- 3. Kragten 數值法 ----------
kragten <- metRology::uncert(
  model,
  x = x,
  u = u,
  method = "kragten"
)

# ---------- 4. Monte Carlo ----------
# 套件預設 B=200 只適合快速示範；正式比較明確提高 B 並固定 seed。
set.seed(2024)
mc <- metRology::uncert(
  model,
  x = x,
  u = u,
  method = "MC",
  B = 100000,
  keep.x = FALSE
)

# ---------- 5. 三種方法比較 ----------
comparison <- c(
  GUM = unname(gum$u),
  Kragten = unname(kragten$u),
  Monte_Carlo = unname(mc$u)
)
print(comparison)

# 此近線性案例三種 uc 應非常接近。
stopifnot(max(comparison) - min(comparison) < 0.002)

# ---------- 6. 不準度預算視覺化 ----------
variance_contributions <- metRology::contribs(gum)
standard_contributions <- sqrt(variance_contributions)

barplot(standard_contributions,
        col = c("tomato", "gold", "steelblue"),
        main = "metRology：鎘標準液不準度貢獻",
        ylab = "標準不準度貢獻 (mg/L)",
        las = 1)

# ---------- 7. 相關性示範 ----------
# cor 預設是單位矩陣，即假設輸入彼此獨立。
# 若兩個輸入共享校正來源，必須用有依據的相關係數，而非任意猜測。
cor_mat <- diag(3)
dimnames(cor_mat) <- list(names(x), names(x))
cor_mat["m", "V"] <- cor_mat["V", "m"] <- 0.30

gum_correlated <- metRology::uncert(
  model,
  x = x,
  u = u,
  method = "GUM",
  cor = cor_mat
)

c(independent_uc = unname(gum$u),
  correlated_uc = unname(gum_correlated$u))

# 重點：
# 1. 套件能計算，但不會替你定義被測量或判斷 Type A/B 資訊是否合理。
# 2. GUM、Kragten 與 MC 差異明顯時，要回查非線性、分布、相關性與程式設定。
# 3. 使用 metRology::函數() 可避免 library(metRology) 遮蔽 base::cbind/rbind。
