# =====================================================================
# Ch13 實戰應用：USDA FoodData Central 開放資料 × 食品配方計算
# 對照業界軟體 TechWizard 的兩大招牌功能：
#   (1) 目標導向配方 + 最低成本配方 (goal-oriented / least-cost formulation)
#   (2) 營養標籤 + 逆向工程 (nutrition labeling & reverse engineering)
# 特色：
#   - 全部使用 R 內建函數，不需安裝任何套件
#   - 核心部分完全離線可執行；原料組成摘錄自 USDA FoodData Central
#     (SR Legacy，公眾領域 CC0 授權)
#   - 情境：香草冰淇淋配方 (對照 TechWizard 官網 Ice Cream 範例的規格：
#     脂肪 12%、MSNF 11%、砂糖 14%、玉米糖漿 3%、安定劑/乳化劑 0.5%)
# =====================================================================

# ---------- 0. 環境旗標 ----------
RUN_ONLINE <- FALSE  # 有網路時改成 TRUE，會示範呼叫 FDC API 抓真資料(見 Part 6)

# ---------- Part 1. 迷你原料資料庫 (摘錄自 USDA FDC / SR Legacy) ----------
# 組成欄位 = 每 100 g 原料的克數 (%)
#   water 水分 | protein 蛋白質 | fat 脂肪 | carb 碳水化合物 | ash 灰分(礦物質)
# NDB = SR Legacy 傳統編號，可在 fdc.nal.usda.gov 搜尋頁查回對應 fdcId
# msnf = 非脂乳固形質 (milk solids-not-fat) = protein + carb + ash，
#        乳品工業的慣用指標（只對乳原料有意義）
ing <- data.frame(
  name    = c("鮮奶油(36%)", "全脂鮮乳", "脫脂奶粉", "砂糖", "玉米糖漿", "安定劑/乳化劑"),
  ndb     = c("01053", "01077", "01095", "19335", NA, NA),
  water   = c(57.71, 88.10,  3.20,  0.00, 20.0, 0),
  protein = c( 2.05,  3.15, 36.16,  0.00,  0.0, 0),
  fat     = c(36.08,  3.25,  0.77,  0.00,  0.0, 0),
  carb    = c( 2.79,  4.80, 51.99, 99.98, 78.0, 0),
  ash     = c( 0.61,  0.70,  7.92,  0.00,  0.0, 0),
  price   = c(230, 38, 280, 42, 55, 850)   # 示教用虛構單價 (元/kg)
)
ing$msnf <- ing$protein + ing$carb + ing$ash
ing[, c("name", "fat", "msnf", "water", "price")]
#> 鮮奶油 fat=36.08 msnf=5.45 | 全脂乳 fat=3.25 msnf=8.65 | 脫脂奶粉 fat=0.77 msnf=96.07

# 教學重點：FDC 對「複合加工原料」(玉米糖漿、安定劑) 覆蓋度低，
# 實務上要向供應商索取規格書 —— 正是 TechWizard「Ingredient Request Wizard」的存在理由！

# ---------- Part 2. 目標導向配方：冰淇淋的質量平衡聯立方程 ----------
# 目標規格 (每 100 kg 配方中的 kg 數)，同 TechWizard Ice Cream 範例：
tgt_fat    <- 12      # 脂肪 12 kg
tgt_msnf   <- 11      # 非脂乳固形 11 kg
w_sugar    <- 14      # 砂糖
w_csyrup   <-  3      # 玉米糖漿
w_stab     <-  0.5    # 安定劑+乳化劑
minor      <- w_sugar + w_csyrup + w_stab
dairy_water <- 100 - minor          # 82.5 kg 由「乳原料 + 水」湊足

# 未知數：c=鮮奶油, m=全脂乳, s=脫脂奶粉, w=水  ->  4 個未知數、只有 3 條方程式
#   (1) 總質量 : c + m + s + w            = 82.5
#   (2) 脂肪   : .3608c + .0325m + .0077s = 12
#   (3) MSNF   : .0545c + .0865m + .9607s = 11
# 缺一條方程式 -> 存在「一個自由度」的整個配方家族！這就是配方的本質。

f_c <- ing$fat[1]/100;   f_m <- ing$fat[2]/100;   f_s <- ing$fat[3]/100
n_c <- ing$msnf[1]/100;  n_m <- ing$msnf[2]/100;  n_s <- ing$msnf[3]/100

A <- rbind(c(1, 1, 1),          # 未知數順序 (cream, milk, water)；smp 移到右邊當參數
           c(f_c, f_m, 0),      # 水不含脂肪
           c(n_c, n_m, 0))      # 水不含乳固形

p_cream <- ing$price[1]; p_milk <- ing$price[2]; p_smp <- ing$price[3]
p_water <- 0.5
minor_cost <- w_sugar * ing$price[4] + w_csyrup * ing$price[5] +
              w_stab  * ing$price[6]

# balance_mix(): 掃描「脫脂奶粉用量 s」，每個 s 解一次 3x3 聯立方程
balance_mix <- function(target_fat, target_msnf,
                        grid = seq(0, 12, by = 0.05)) {
  out <- data.frame(smp = grid, cream = NA_real_, milk = NA_real_,
                    water = NA_real_, ok = FALSE, cost = NA_real_)
  for (i in seq_along(grid)) {
    s <- grid[i]
    b <- c(dairy_water - s,               # 方程(1)
           target_fat  - f_s * s,         # 方程(2)
           target_msnf - n_s * s)         # 方程(3)
    x <- tryCatch(solve(A, b), error = function(e) rep(NA_real_, 3))
    out[i, c("cream", "milk", "water")] <- x
    out$ok[i] <- all(!is.na(x)) && all(x >= -1e-9)   # 用量不能是負的！
    if (out$ok[i]) {
      out$cost[i] <- p_cream * x[1] + p_milk * x[2] +
                     p_smp * s + p_water * max(x[3], 0) + minor_cost
    }
  }
  out
}

sol <- balance_mix(tgt_fat, tgt_msnf)
sum(sol$ok)                          #> 約 82 個網格點可行
range(sol$smp[sol$ok])               #> 可行的 SMP 區間約 5.50 ~ 9.60 kg

# ---------- Part 3. 最低成本配方：在配方家族中找最便宜的 ----------
best  <- sol[which.min(sol$cost), ]
worst <- sol[sol$ok, ][which.max(sol$cost[sol$ok]), ]

round(best[, c("smp", "cream", "milk", "water", "cost")], 2)
#> 最便宜解落在可行區間左端點：SMP≈5.5、水≈0.25、成本≈11,169 元/100kg
round(worst[, c("smp", "cream", "milk", "water", "cost")], 2)
#> 最貴解在右端點：SMP≈9.6、水≈39.9，成本多約 300 元 (+2.8%)

plot(cost ~ smp, data = sol, subset = ok, type = "l", lwd = 2,
     col = "#1565C0",
     main = "最低成本配方：成本隨脫脂奶粉用量單調上升",
     xlab = "脫脂奶粉用量 (kg / 100 kg 配方)",
     ylab = "原料成本 (元 / 100 kg)")
points(best$smp, best$cost, pch = 19, col = "red", cex = 1.5)
text(best$smp, best$cost - 90, sprintf("最便宜 %.0f 元", best$cost),
     col = "red", pos = 4)
abline(v = range(sol$smp[sol$ok]), lty = 2, col = "grey50")

# 為什麼最適解在「端點」？
#   成本是各項用量的線性函數 -> 在可行區域(凸多面體)的極值必出現在頂點。
#   本題只有 1 個自由度 => 可行集合是一條線段 => 最佳解必在兩端之一。
#   這就是線性規劃 (LP) 的核心直覺；TechWizard 的 AI 配方引擎 =
#   同樣邏輯 + 更多原料與限制式時的自動化 (單純法, simplex method)。

# ---------- Part 4. 加權營養計算 -> 營養標籤 ----------
# TechWizard 邏輯：配方加權平均出「每 100 g」營養值，再換算每份並套捨入規則
wt_cream <- best$cream; wt_milk <- best$milk; wt_smp <- best$smp

prot  <- (wt_cream*2.05 + wt_milk*3.15 + wt_smp*36.16)/100
carb  <- (wt_cream*2.79 + wt_milk*4.80 + wt_smp*51.99 +
          w_sugar*99.98 + w_csyrup*78)/100
lact  <- (wt_cream*2.79 + wt_milk*4.80 + wt_smp*51.99)/100   # 乳糖
sugar <- w_sugar + lact + w_csyrup*0.26                      # 標示用「糖」
na_mg <- (wt_cream*30 + wt_milk*43 + wt_smp*1010)/100        # 鈉 (mg)
kcal  <- 4*prot + 4*carb + 9*tgt_fat                         # Atwater 4-4-9
round(c(protein = prot, fat = tgt_fat, carb = carb, sugar = sugar,
        Na_mg = na_mg, kcal_44_9 = kcal), 2)
#> protein=4.09  fat=12.00  carb=22.30  sugar=20.74  Na=84.8  kcal=213.6

# 台灣格式：每 100 g；美國 FDA 格式：每份 (冰淇淋 RACC = 2/3 杯 ≈ 66 g，
# 已把 overrun 打入空氣考慮)。捨入規則此處為教學簡化版，實際以最新法規為準。
serv <- 66/100
fda_g   <- function(x) ifelse(x < 0.5, 0, round(x))
fda_cal <- function(k) ifelse(k <= 5, 0, ifelse(k <= 50, round(k/5)*5, round(k/10)*10))
label_tw <- data.frame(
  營養素 = c("熱量(kcal)", "蛋白質(g)", "脂肪(g)", "碳水化合物(g)", "糖(g)", "鈉(mg)"),
  每100g = round(c(kcal, prot, tgt_fat, carb, sugar, na_mg), 1))
label_us <- data.frame(
  營養素 = label_tw$營養素,
  每份66g_fda = c(fda_cal(kcal*serv), fda_g(prot*serv), fda_g(tgt_fat*serv),
                  fda_g(carb*serv), fda_g(sugar*serv),
                  round(na_mg*serv/5)*5))
cbind(label_tw, label_us[2])
#> 每66g: 熱量140 kcal / 蛋白質3g / 脂肪8g / 碳水15g / 糖14g / 鈉55mg
#> —— 和市售香草冰淇淋的標籤幾乎一模一樣！

# Atwater 檢核 (呼應 Ch4 迴歸)：FDC 的 Energy 若與 4-4-9 差很多，
# 通常代表該筆資料用了「特定因子」(如乳品 3.87/4.27/8.79) 或纖維扣除法

# ---------- Part 5. 逆向工程：從競品的檢驗值反推配方 ----------
# TechWizard Reverse Engineering：輸入產品分析結果 -> 反推等效配方
# 情境：買了競品香草冰淇淋送實驗室檢測：
lab_fat     <- 10.8    # 脂肪 (%)
lab_protein <-  4.4    # 蛋白質 (%)
msnf_est    <- lab_protein / 0.36    # 乳蛋白約占非脂固形的 36% -> MSNF 估計
msnf_est                              #> 12.2%

sol_re  <- balance_mix(lab_fat, msnf_est)
best_re <- sol_re[which.min(sol_re$cost), ]

compare <- rbind(
  我方設計  = round(unlist(best [c("cream","milk","smp","water")]), 1),
  競品還原  = round(unlist(best_re[c("cream","milk","smp","water")]), 1))
compare                                # 競品脂肪較低、MSNF較高 -> 更省錢的配方結構
sprintf("競品等效配方成本約 %.0f 元/100kg (我方 %.0f 元)",
        best_re$cost, best$cost)

# 逆向工程的三個不確定來源 (呼應 Ch6~Ch8！)：
#   (1) 標籤/檢驗值的捨入誤差  (2) 各原料組成的批次變異
#   (3) MSNF 由蛋白質反推的模型假設 -> 所以解不是唯一，只是「等效近似」

# ---------- Part 6. 取得真資料：FDC API 與 CSV 下載 ----------
if (RUN_ONLINE) {
  # (a) API：到 https://fdc.nal.usda.gov/api-key-signup 免費申請金鑰換掉 DEMO_KEY
  key  <- "DEMO_KEY"
  qurl <- paste0("https://api.nal.usda.gov/fdc/v1/foods/search",
                 "?api_key=", key,
                 "&query=butter%2Csalted&dataType=SR%20Legacy&pageSize=1")
  txt  <- paste(readLines(url(qurl), warn = FALSE), collapse = "")
  hit  <- regmatches(txt, regexpr(
    '"nutrientName":"Energy","nutrientNumber":"[0-9]+","unitName":"KCAL"[^}]*"value":[0-9.]+',
    txt))
  cat(hit, "\n")     #> 奶油能量 value":717 kcal (與教科書一致)

  # (b) 整包 CSV：到 https://fdc.nal.usda.gov/download-datasets 複製最新連結
  # download.file("<下載頁的zip連結>", destfile = "fdc_sr_legacy.zip")
  # unzip("fdc_sr_legacy.csv.zip")
  # food <- read.csv("food.csv")   # 數十萬列 -> Ch1 的描述統計直接派上用場
}

# ---------- 小結 ----------
cat("TechWizard 兩大招牌功能 = 質量平衡聯立方程 (solve) + 加權平均 (weighted mean)，
    背後沒有魔法，只有你已經學過的統計與代數。\n")
