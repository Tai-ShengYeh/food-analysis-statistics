"use strict";

const chapters = [
  {
    id: 1, group: "入門", title: "從數據開始：平均、SD 與 CV", level: "入門",
    lead: "先不背公式。把一組漢堡肉水分重複測定，依序變成平均值、標準差與相對標準差，學會回答「結果在哪裡」與「結果有多散」。",
    source: "Nielsen, Food Analysis, Ch. 4.2–4.3.1（集中趨勢、準確度與精密度）",
    goals: ["看懂 R 的資料向量", "計算平均值、SD 與 CV", "用單位與有效位數報告結果"],
    terms: [["R", "R programming language", "R 統計程式語言", "用指令整理資料、計算統計量與繪圖的免費軟體。"], ["mean", "Arithmetic mean", "算術平均值", "把所有數字加總後除以資料筆數，也就是一般說的平均。"], ["SD", "Standard deviation", "標準差", "描述每筆數據離平均值通常有多遠；越小表示結果越集中。"], ["CV／RSD", "Coefficient of variation / Relative standard deviation", "變異係數／相對標準差", "把 SD 除以平均值並寫成百分比，方便比較不同大小的數據。"], ["Accuracy", "Accuracy", "準確度", "量測結果與參考值有多接近。"], ["Precision", "Precision", "精密度", "重複量測結果彼此有多接近。"]],
    image: "assets/img/fig_target.png", caption: "準確度描述接近參考值；精密度描述重複結果彼此接近。",
    visualGuide: {
      title: "先看懂圖，再開始計算",
      lead: "每一格都代表「同一個樣品重複量測多次」。紅點是參考值或目標值；藍點是每一次實際量測結果。",
      questions: [
        ["① 藍點彼此靠近嗎？", "用來判斷精密度。越集中表示重複結果越一致，通常 SD 與 CV 越小。"],
        ["② 整群藍點靠近紅點嗎？", "用來判斷準確度。越接近參考值，代表平均結果的偏差越小。"]
      ]
    },
    visualLabels: ["(a) 準確且精密（理想）", "(b) 精密但偏移（系統誤差）", "(c) 圍繞真值但散開（隨機誤差大）", "(d) 又偏又散（最糟）"],
    visualExplanations: [
      {key:"a", title:"準確且精密", body:"藍點彼此集中，也包圍紅色參考值。重複性好，而且結果接近參考值。", data:"數據表現：SD、CV 小；平均值接近參考值。"},
      {key:"b", title:"精密但不準確", body:"藍點很集中，但整群偏離紅點。常見原因是校正偏差、固定稀釋誤差或回收率修正不當。", data:"數據表現：SD、CV 小；平均值卻偏離參考值。"},
      {key:"c", title:"平均可能準確，但不精密", body:"藍點散得很開，雖然整體圍繞紅點，單次結果仍不穩定。平均值看似正確不能掩蓋重複性不足。", data:"數據表現：SD、CV 大；平均值可能接近參考值。"},
      {key:"d", title:"不準確且不精密", body:"藍點既分散又整體偏離紅點，同時存在明顯偏差與重複性問題。", data:"數據表現：SD、CV 大；平均值也偏離參考值。"}
    ],
    visualBridge: "把圖連回本章：平均值告訴你藍點群的中心；SD 與 CV 告訴你藍點彼此有多分散。只有 SD 或 CV，不能判斷準確度；還需要參考值、標準參考物質或回收率等外部證據。",
    concepts: [["平均值 mean", "代表資料的中心，但不能單獨描述品質。"], ["標準差 SD", "描述單筆結果相對平均值的散布。"], ["變異係數 CV", "SD ÷ 平均值 × 100%，適合比較不同尺度。"]],
    formula: "CV (%) = SD / mean × 100",
    symbols: [["CV (%)", "變異係數，表示相對於平均值的散布大小", "%"], ["SD", "樣本標準差，描述單筆測值的散布", "與原始數據相同"], ["mean", "所有重複測值的算術平均值", "與原始數據相同"], ["× 100", "把比例轉換成百分比", "無單位"]],
    formulaNote: "mean 不可為 0；若平均值非常接近 0，CV 會失去穩定且合理的解釋。",
    warning: "SD 小不等於準確。儀器若整體偏高，結果可以很集中卻離參考值很遠。",
    code: `moisture <- c(64.53, 64.45, 65.10, 64.78)\nmean_m <- mean(moisture)\nsd_m   <- sd(moisture)\ncv_m   <- sd_m / mean_m * 100\nround(c(mean = mean_m, SD = sd_m, CV_percent = cv_m), 3)`,
    steps: [["1 建立資料", "用 c(...) 把重複測定放在一起。"], ["2 描述中心", "mean() 回答平均結果。"], ["3 描述散布", "sd() 與 CV 回答精密度。"]],
    quiz: [
      {q:"同一樣品測 5 次，數值彼此很接近，但都比參考值高。最合理的描述是？", opts:["高精密度、低準確度","低精密度、高準確度","高精密度、高準確度"], a:0, why:"彼此接近代表精密；整體偏離參考值代表準確度不足。"},
      {q:"平均值 50.0、SD 1.0，CV 是多少？", opts:["0.5%","2.0%","50%"], a:1, why:"CV = 1.0 ÷ 50.0 × 100% = 2.0%。"}
    ]
  },
  {
    id: 2, group: "入門", title: "常態分配、SEM 與信賴區間", level: "入門",
    lead: "從鐘形曲線理解：SD 描述個別測值的散布，SEM 描述平均值估計得多穩；樣本少時，95% 信賴區間要使用 t 分配。",
    source: "Nielsen, Ch. 4.3.1（常態分配、信賴水準與 t 值）",
    goals: ["區分 SD 與 SEM", "用 t 分配計算 95% CI", "解讀信賴區間而不誤稱 95% 資料範圍"],
    terms: [["SEM", "Standard error of the mean", "平均值標準誤", "描述樣本平均值估計得有多穩定；不是單筆數據的散布。"], ["CI", "Confidence interval", "信賴區間", "用樣本資料建立的平均值合理範圍。"], ["t distribution", "Student's t-distribution", "Student t 分配", "樣本較少且母體標準差未知時，用來建立平均值信賴區間的分配。"], ["df", "Degrees of freedom", "自由度", "決定 t 分配形狀的資訊量；本章平均值問題通常是 n−1。"], ["Normal distribution", "Normal distribution", "常態分配", "以平均值為中心、左右對稱的鐘形分配。"]],
    image: "assets/img/fig_normal.png", caption: "常態分配下，約 68%、95%、99.7% 位於平均值的 1、2、3 個 SD 內。",
    concepts: [["SD", "個別量測值的散布。"], ["SEM", "平均值的不確定程度；等於 SD/√n。"], ["95% CI", "在重複抽樣下，依此程序建立的區間約 95% 會涵蓋母體平均值。"]],
    formula: "95% CI = mean ± t(0.975, n−1) × SD / √n",
    symbols: [["95% CI", "母體平均值的 95% 信賴區間", "與測值相同"], ["mean", "樣本平均值，也是區間中心", "與測值相同"], ["t(0.975, n−1)", "t 分配在累積機率 0.975、自由度 n−1 的臨界值", "無單位"], ["SD", "樣本標準差", "與測值相同"], ["n", "獨立重複測定的筆數", "筆"], ["√n", "重複數的平方根；SD/√n 就是 SEM", "無單位"]],
    formulaNote: "此式用於以樣本 SD 估計平均值的不確定程度；重複測定應具有代表性且近似獨立。",
    warning: "95% CI 不是『95% 的單筆數據會落在這裡』；那是對平均值估計程序的敘述。",
    code: `x <- c(64.53, 64.45, 65.10, 64.78)\nn <- length(x)\nsem <- sd(x) / sqrt(n)\nt_star <- qt(0.975, df = n - 1)\nmean(x) + c(-1, 1) * t_star * sem`,
    steps: [["1 算 SEM", "重複數 n 增加，平均值估計會更穩。"], ["2 找 t 值", "qt() 會依自由度調整。"], ["3 建立區間", "平均值上下各加一個誤差界。"]],
    quiz: [
      {q:"當 SD 不變、重複數由 4 增至 16，SEM 約變成？", opts:["原來的 1/4","原來的 1/2","原來的 2 倍"], a:1, why:"SEM 與 √n 成反比；√16/√4 = 2，所以 SEM 減半。"},
      {q:"n = 5 時，t 分配的自由度為？", opts:["4","5","6"], a:0, why:"以樣本 SD 建立平均值信賴區間時，自由度 df = n−1。"}
    ]
  },
  {
    id: 3, group: "品管", title: "方法效能與品質管制圖", level: "基礎",
    lead: "把靈敏度、偵測極限、選擇性和管制圖放回實驗流程：方法能否辨識目標物？今天的系統是否仍在受控狀態？",
    source: "Nielsen, Ch. 4.3.2–4.3.5（誤差來源、選擇性、LOD、品質管制）",
    goals: ["區分靈敏度與 LOD", "建立 Shewhart 管制界限", "辨認突發失控與緩慢漂移"],
    terms: [["QC", "Quality control", "品質管制／品管", "用已知或穩定樣品持續確認分析系統今天是否正常。"], ["LOD", "Limit of detection", "偵測極限", "在指定規則下，能與空白背景區分的最低量。"], ["LOQ", "Limit of quantification", "定量極限", "能以足夠可靠程度報出數值的最低量，通常高於 LOD。"], ["Sensitivity", "Sensitivity", "靈敏度", "濃度改變時，儀器訊號改變得有多明顯，常用校正線斜率描述。"], ["Shewhart chart", "Shewhart control chart", "Shewhart 管制圖", "把品管結果依時間排列，用中心線與界限監測失控訊號。"], ["CL", "Center line", "中心線", "管制圖中代表受控狀態中心值的線。"]],
    image: "assets/img/fig_shewhart.png", caption: "管制圖用歷史受控資料建立中心線、警告線與行動線。",
    concepts: [["靈敏度", "訊號對濃度變化的反應大小，常由斜率表示。"], ["LOD", "在指定假設下可與空白區分的最低量；不等於可可靠定量的 LOQ。"], ["管制圖", "監測分析系統隨時間的穩定性，不是法規合格判定圖。"]],
    formula: "教學近似：LOD = blank mean + 3s；LOQ = blank mean + 10s",
    symbols: [["LOD", "偵測極限：在指定規則下可與空白區分的最低訊號", "訊號單位"], ["LOQ", "定量極限：可進行較可靠定量的最低訊號", "訊號單位"], ["blank mean", "多次空白測定訊號的平均值", "訊號單位"], ["s", "空白訊號的樣本標準差", "訊號單位"], ["3、10", "此教學規則採用的標準差倍數", "無單位"]],
    formulaNote: "這裡得到的是訊號尺度的 LOD/LOQ；若要報濃度，還需用校正關係換算。正式定義須依方法與規範。",
    warning: "LOD/LOQ 的定義會依方法、法規與驗證指南不同。正式報告前必須先說明採用的定義。",
    code: `blank <- c(0.010, 0.006, 0.009, 0.011, 0.007, 0.008, 0.010, 0.006)\nblank_mean <- mean(blank)\nblank_sd <- sd(blank)\nc(LOD = blank_mean + 3 * blank_sd,\n  LOQ = blank_mean + 10 * blank_sd)`,
    steps: [["1 蒐集空白", "同一流程測多次空白。"], ["2 估計背景", "計算空白平均與 SD。"], ["3 套用規則", "在報告中同步寫清楚定義。"]],
    quiz: [
      {q:"標準曲線斜率較大，最直接代表？", opts:["靈敏度較高","偵測極限一定較低","選擇性一定較好"], a:0, why:"斜率描述訊號對濃度變化的反應；LOD 與選擇性還受其他因素影響。"},
      {q:"品管樣品超過行動界限，第一步應該？", opts:["刪除該點後繼續","查明原因並暫停放行相關結果","把界限放寬"], a:1, why:"失控訊號需要調查、矯正及評估受影響結果，不能直接刪點或改界限。"}
    ]
  },
  {
    id: 4, group: "品管", title: "標準曲線與線性迴歸", level: "基礎",
    lead: "用濃度與儀器訊號建立校正線，從圖形、殘差與預測區間判斷模型是否能用，而不是只看一個漂亮的 r²。",
    source: "Nielsen, Ch. 4.4（線性迴歸、相關係數與迴歸誤差）；加權迴歸為分析化學校正的延伸教學",
    goals: ["用 lm() 建立校正線", "由訊號內插未知濃度", "辨認異方差並比較 OLS 與 WLS", "以殘差和回算偏差選擇權重"],
    terms: [["Calibration curve", "Calibration curve", "校正曲線／標準曲線", "用已知濃度與儀器訊號建立的關係，用來反推未知濃度。"], ["lm()", "Linear model", "R 的線性模型函數", "在 R 中計算直線斜率、截距與殘差的指令。"], ["OLS", "Ordinary least squares", "普通最小平方法", "每個校正點的重要性相同，是未指定權重時 lm() 使用的方法。"], ["WLS", "Weighted least squares", "加權最小平方法", "讓不同校正點具有不同影響力；通常讓變異較小、資訊較可靠的點有較大權重。"], ["Heteroscedasticity", "Heteroscedasticity", "異方差", "殘差的散布大小會隨濃度或訊號改變，例如高濃度點比低濃度點更分散。"], ["Weight", "Regression weight", "迴歸權重", "控制每個校正點對迴歸線影響力的數值；權重越大，該點的影響通常越大。"], ["R²／r²", "Coefficient of determination", "決定係數", "表示模型解釋資料變異的比例；很高仍不代表方法一定適用。"], ["Residual", "Residual", "殘差", "實際訊號減去模型預測訊號，用來檢查直線是否合適。"], ["Interpolation", "Interpolation", "內插", "在已知校正範圍內估計未知濃度。"], ["Extrapolation", "Extrapolation", "外插", "超出校正範圍推估，風險高且通常應避免。"]],
    image: "assets/img/fig_calib_ci.png", caption: "校正線兩端的預測不確定度通常較大；未知樣品應位於驗證範圍內。",
    concepts: [["斜率", "濃度每增加一單位，訊號平均改變多少。"], ["r²", "線性模型解釋的變異比例，不保證無偏或適用。"], ["殘差", "觀測訊號−模型訊號；應檢查趨勢與離群點。"]],
    formula: "未知濃度 x = (觀測訊號 y − 截距 b₀) / 斜率 b₁",
    symbols: [["x", "由校正線反推的未知樣品濃度", "例如 mg/L"], ["y", "未知樣品的觀測儀器訊號", "例如峰面積或吸光值"], ["b₀", "線性迴歸的截距：x=0 時模型預測訊號", "與 y 相同"], ["b₁", "線性迴歸的斜率：濃度每增加一單位的訊號變化", "y 單位/x 單位"]],
    formulaNote: "只可在已驗證的校正範圍內內插；若樣品另有稀釋，還要把 x 乘上稀釋倍數。",
    weightedRegressionGuide: {
      intro: "當濃度跨越數十倍或數百倍時，高濃度訊號的絕對波動常比低濃度大。此時普通最小平方法（OLS）可能被高濃度點主導，使低濃度回算偏差變大。是否加權要由資料與方法驗證決定，不能只因範圍大就自動套用。",
      equation: "WLS 最小化：Σ wᵢ(yᵢ − ŷᵢ)²；理想情況下 wᵢ ≈ 1/sᵢ²",
      symbols: [["Σ", "把所有校正點的加權平方殘差加總"], ["wᵢ", "第 i 個校正點的權重"], ["yᵢ", "第 i 個校正點實際量到的訊號"], ["ŷᵢ", "迴歸線對第 i 個校正點預測的訊號"], ["sᵢ²", "第 i 個濃度層級重複訊號的變異數"]],
      candidates: [
        ["不加權 OLS", "wᵢ = 1", "各濃度的殘差散布大致相近時。"],
        ["1/x", "wᵢ = 1/xᵢ", "變異隨濃度增加，但增加幅度較溫和時可列為候選。"],
        ["1/x²", "wᵢ = 1/xᵢ²", "相對誤差近似固定、變異約隨濃度平方增加時可列為候選。"],
        ["1/s²", "wᵢ = 1/sᵢ²", "每個濃度有足夠重複測定，可較可靠估計各層級變異數時。"]
      ],
      checks: ["先畫殘差對預測值或濃度圖，查看是否呈漏斗形。", "比較每一濃度層級的回算濃度偏差（%）或回收率，而非只看整體 r²。", "確認最低與最高濃度、品管樣品及獨立驗證樣品都符合方法預先設定的允收標準。", "把候選權重與選擇理由寫入方法文件，並用後續批次持續監測。"],
      caution: "1/x 與 1/x² 是候選經驗模型，不是萬用答案。x = 0 的空白不能直接計算 1/x；應將空白另行評估、使用可解釋的變異模型，或依方法程序處理。每層重複太少時，1/s² 也可能因變異數估計不穩而失真。",
      code: `# HPLC 咖啡因示例：每個濃度做 3 次標準品
conc <- rep(c(1, 5, 10, 50, 100), each = 3)
area <- c(101, 99, 102,
          498, 505, 492,
          1005, 992, 1018,
          4930, 5070, 5005,
          9720, 10380, 10040)

# 建立三個候選模型
fit_ols  <- lm(area ~ conc)
fit_1x   <- lm(area ~ conc, weights = 1 / conc)
fit_1x2  <- lm(area ~ conc, weights = 1 / conc^2)

# 把訊號反推成濃度，再比較各層級平均回算偏差 (%)
backcalc <- function(fit) (area - coef(fit)[1]) / coef(fit)[2]
bias_table <- data.frame(
  conc = conc,
  OLS = 100 * (backcalc(fit_ols) - conc) / conc,
  WLS_1x = 100 * (backcalc(fit_1x) - conc) / conc,
  WLS_1x2 = 100 * (backcalc(fit_1x2) - conc) / conc
)
print(aggregate(. ~ conc, data = bias_table, FUN = mean))

# 殘差圖：OLS 看原始殘差；WLS 看加權後殘差
par(mfrow = c(1, 2))
plot(fitted(fit_ols), residuals(fit_ols),
     xlab = "預測訊號", ylab = "殘差", main = "OLS")
abline(h = 0, lty = 2)
plot(fitted(fit_1x2), sqrt(1 / conc^2) * residuals(fit_1x2),
     xlab = "預測訊號", ylab = "加權殘差", main = "WLS: 1/x^2")
abline(h = 0, lty = 2)`,
    },
    warning: "不要外插。超出校正範圍時，稀釋樣品或重新設計標準濃度。",
    code: `x <- c(1, 3, 5, 10, 20)\ny <- c(0.050, 0.140, 0.242, 0.521, 0.998)\nfit <- lm(y ~ x)\nsummary(fit)\nplot(fitted(fit), residuals(fit))\n(0.555 - coef(fit)[1]) / coef(fit)[2]`,
    steps: [["1 建模", "lm(y ~ x) 讓訊號由濃度解釋。"], ["2 看殘差", "確認沒有彎曲、漏斗或單一異常點。"], ["3 內插", "只在驗證濃度範圍內反推。"]],
    quiz: [
      {q:"r² = 0.999 就能直接證明方法線性良好嗎？", opts:["可以","不可以，還要看殘差、範圍與重複性","只要點數超過 3 就可以"], a:1, why:"高 r² 仍可能掩蓋系統性彎曲、異方差或單一高濃度點的影響。"},
      {q:"未知訊號高於最高標準品，較恰當的做法是？", opts:["直接外插","稀釋後落回校正範圍再測","把截距設為 0"], a:1, why:"外插假設未被資料驗證；應調整樣品使其落在有效範圍。"},
      {q:"殘差圖顯示濃度越高，殘差散布越大。這種現象稱為？", opts:["異方差","外插","常態分布"], a:0, why:"異方差表示誤差變異不是固定值。若高濃度點的散布較大，OLS 的等變異假設可能不合適。"},
      {q:"比較 1/x 與 1/x² 權重時，最恰當的選擇方式是？", opts:["選 r² 最高者即可","選數值最小的權重","比較殘差、各層級回算偏差及獨立驗證結果"], a:2, why:"權重必須改善整個工作範圍的校正表現，尤其是各濃度回算偏差與驗證樣品；r² 通常不足以分辨。"}
    ]
  },
  {
    id: 5, group: "品管", title: "有效數字、異常值與資料倫理", level: "基礎",
    lead: "學會何時四捨五入、如何檢查可疑值，也學會最重要的原則：統計檢定不是刪除不喜歡結果的許可證。",
    source: "Nielsen, Ch. 4.5（結果報告、有效數字、Dixon Q 異常值檢定）",
    goals: ["依不確定度決定報告位數", "理解 Dixon Q 的 gap/range", "保留原始資料與排除理由"],
    terms: [["Significant figures", "Significant figures", "有效數字", "用合理位數呈現量測結果，避免假裝儀器比實際更精確。"], ["Outlier", "Outlier", "離群值／異常值", "與其他資料明顯不同的觀測值，但不同不代表可直接刪除。"], ["Dixon Q", "Dixon's Q test", "Dixon Q 檢定", "針對小樣本端點可疑值的統計檢查方法。"], ["gap", "Nearest-neighbour gap", "相鄰間距", "可疑值與最接近數值之間的距離。"], ["range", "Range", "全距", "資料最大值減最小值。"], ["Qcrit", "Critical Q value", "Q 臨界值", "依資料筆數與信賴水準查表得到的比較門檻。"]],
    image: "assets/img/fig_residual.png", caption: "先畫圖與查核實驗紀錄，再決定是否需要正式異常值檢定。",
    concepts: [["有效數字", "反映量測解析度，不是越多越科學。"], ["Dixon Q", "以相鄰間距除以全距，適合小樣本端點檢查。"], ["資料倫理", "排除需要預先規則、技術理由與完整紀錄。"]],
    formula: "Q = gap / range；若 Q > 對應 n 與信賴水準的臨界值，才有統計排除依據",
    symbols: [["Q", "Dixon Q 檢定統計量", "無單位"], ["gap", "可疑端點值與最近鄰數值的距離", "與測值相同"], ["range", "最大值減最小值的全距", "與測值相同"], ["n", "本次資料筆數，用來選擇臨界值", "筆"], ["Q 臨界值", "依 n 與預先選定信賴水準查表所得門檻", "無單位"]],
    formulaNote: "Q 超過臨界值只提供統計證據；仍須回查實驗紀錄，並依預先規則決定是否排除。",
    warning: "切勿反覆檢定直到數據『變漂亮』。同時呈現含與不含可疑值的敏感度分析更透明。",
    code: `x <- sort(c(88.62, 88.74, 89.20, 82.20))\nQ <- (x[2] - x[1]) / (max(x) - min(x))\nQcrit <- 0.76  # n=4, 90% 教材表值\nc(Q = Q, Qcrit = Qcrit, reject = Q > Qcrit)`,
    steps: [["1 視覺檢查", "確認可疑值位於端點。"], ["2 回查紀錄", "找校正、稀釋、抄錄或樣品問題。"], ["3 記錄決策", "寫下規則、臨界值與處理結果。"]],
    quiz: [
      {q:"某筆結果不符合預期，但查不到技術錯誤。可以直接刪除嗎？", opts:["可以","不可以，需依預先規則與統計/技術證據","只要平均值改善就可以"], a:1, why:"結果不符合預期不是排除理由；資料處理應可追溯且避免選擇性刪除。"},
      {q:"Dixon Q 的分母是？", opts:["標準差","最大值−最小值","平均值"], a:1, why:"Q = 可疑值與最近鄰的 gap ÷ 全距 range。"}
    ]
  },
  {
    id: 6, group: "不準度", title: "量測不準度：從誤差到測量模型", level: "中階",
    lead: "誤差是測得值與真值之差，而真值通常未知；量測不準度則描述可合理歸因於被測量值的散布。先明確定義被測量，再談數字。",
    source: "Eurachem/CITAC QUAM:2012.P1, Ch. 2–4（定義、分析量測、不準度估計流程）",
    goals: ["區分誤差與不準度", "寫出被測量與測量模型", "依四步驟建立估計流程"],
    terms: [["Measurand", "Measurand", "被測量", "真正要報告的量，必須說清楚分析物、食品基質、條件與單位。"], ["Measurement model", "Measurement model", "測量模型", "把稱重、體積、校正與修正因子連到最後結果的計算式。"], ["Measurement uncertainty", "Measurement uncertainty", "量測不準度", "描述哪些數值可合理歸因於被測量的散布範圍。"], ["Error", "Measurement error", "量測誤差", "測得值減真值；真值通常未知，所以單次確切誤差也通常未知。"], ["Bias", "Measurement bias", "量測偏差", "很多次量測的平均結果與參考值之間的系統性差異。"], ["GUM", "Guide to the Expression of Uncertainty in Measurement", "量測不準度表示指南", "建立與報告量測不準度時常用的國際方法架構。"]],
    image: "assets/img/fig_distributions.png", caption: "不準度不是單一錯誤值，而是由資訊與模型描述結果周圍的合理散布。",
    concepts: [["被測量 measurand", "要量的量，須包含基質、分析物、條件與單位。"], ["測量模型", "把輸入量連到最後報告結果的方程式。"], ["四步驟", "定義→找來源→量化→合成與報告。"]],
    formula: "例：c = C_cal × V_final / m_sample × 1/R（須明確寫單位與修正）",
    symbols: [["c", "最後要報告的食品中分析物含量", "例如 mg/kg"], ["C_cal", "由校正曲線得到的待測液濃度", "例如 mg/L"], ["V_final", "樣品前處理後的最終定容體積", "例如 L"], ["m_sample", "進入分析流程的樣品質量", "例如 kg"], ["R", "回收率，以小數表示；若結果已校正才使用 1/R", "無單位"]],
    formulaNote: "這只是示範模型；實際模型須依方法加入稀釋倍數、空白修正、純度或其他必要因子，並先做單位消去檢查。",
    warning: "『儀器誤差 ±0.1』不是完整不準度。抽樣、前處理、校正、回收率與重複性可能更重要。",
    code: `set.seed(123)\ntrue_value <- 100\nresults <- rnorm(30, mean = 102, sd = 3)\nc(observed_mean = mean(results),\n  observed_error = mean(results) - true_value,\n  spread = sd(results))`,
    steps: [["1 定義", "說清楚分析物、基質、條件、單位。"], ["2 列模型", "寫出從原始讀值到結果的方程式。"], ["3 畫來源", "逐項連回模型與實驗流程。"]],
    quiz: [
      {q:"下列何者通常可以從實驗結果直接估計？", opts:["真值","單次量測的確切誤差","重複性造成的標準不準度"], a:2, why:"真值與單次確切誤差通常未知；重複資料可用統計方法估計重複性。"},
      {q:"不準度評估的第一步是？", opts:["直接乘 k=2","明確定義被測量與模型","先做 Monte Carlo"], a:1, why:"若被測量與計算模型不清楚，後續來源與合成都沒有一致邊界。"}
    ]
  },
  {
    id: 7, group: "不準度", title: "Type A、Type B 與分布轉換", level: "中階",
    lead: "Type A 與 Type B 是資訊取得方式，不是『隨機』與『系統』的同義詞。把證書、規格與重複數據都換成相同尺度的標準不準度。",
    source: "QUAM:2012.P1, Ch. 7 與 Appendix E.1（量化來源與分布）",
    goals: ["正確區分 Type A/B 評估", "把 ±a 轉成標準不準度", "選擇矩形、三角形或常態分布"],
    terms: [["Type A", "Type A evaluation", "A 類評估", "利用重複觀測資料與統計分析估計不準度。"], ["Type B", "Type B evaluation", "B 類評估", "利用校正證書、規格、歷史資料或專業判斷估計不準度。"], ["Standard uncertainty", "Standard uncertainty", "標準不準度", "把不準度表示成類似一個標準差的共同尺度。"], ["Rectangular distribution", "Rectangular / uniform distribution", "矩形／均勻分布", "只知道上下界，並假設界限內各值同樣可能。"], ["Triangular distribution", "Triangular distribution", "三角形分布", "中央值最可能，越接近上下界越不可能。"], ["Normal distribution", "Normal distribution", "常態分布", "以中心值為最高點、左右對稱的鐘形分布。"]],
    image: "assets/img/fig_distributions.png", caption: "同一界限 ±a，所選分布不同，換算得到的標準不準度也不同。",
    concepts: [["Type A", "用觀測數據的統計分析評估。"], ["Type B", "用證書、規格、校正歷史或科學判斷評估。"], ["標準化", "所有來源轉成類似標準差的 u(xᵢ)，才能合成。"]],
    formula: "矩形：u=a/√3；三角形：u=a/√6；95% 常態區間：u≈a/1.96",
    symbols: [["u", "換算後的標準不準度，相當於標準差尺度", "與輸入量相同"], ["a", "資料來源所給的正負半寬，例如 ±a", "與輸入量相同"], ["√3", "矩形分布的換算除數", "無單位"], ["√6", "三角形分布的換算除數", "無單位"], ["1.96", "常態分布中央 95% 區間的近似涵蓋因子", "無單位"]],
    formulaNote: "先確認證書上的 ±a 是界限、標準不準度或擴展不準度，再選分布與除數，不能看到 ± 就固定除以 √3。",
    typeBGuide: {
      intro: "三個除數不能任選。先讀證書或規格中 ±a 的真正含義，再決定用哪一個模型。",
      cases: [
        {name:"矩形分布", equation:"u = a/√3", when:"只知道最大允差 ±a；界限內各值可視為同樣可能，界限外近似不可能。", example:"例：容量瓶只標示允差 ±0.10 mL，沒有其他機率資訊。"},
        {name:"三角形分布", equation:"u = a/√6", when:"同樣有 ±a 界限，但有歷史資料或技術理由相信中央值最常見，越接近上下限越少見。", example:"例：長期查核顯示容量誤差大多接近 0，極端允差很少發生。"},
        {name:"95% 常態區間", equation:"u ≈ a/1.96", when:"文件明確說明 ±a 是常態分布的中央 95% 信賴區間或涵蓋區間。", example:"例：校正報告寫『修正值的 95% 區間為 ±0.20 mg』。"}
      ],
      certificate: "如果證書直接提供擴展不準度 U 和涵蓋因子 k，應使用 u = U/k。例如 U=0.20 mg、k=2，則 u=0.10 mg；不要再除以 √3、√6 或 1.96。",
      flow: ["先找證書是否提供 U 與 k：有 → u=U/k。", "沒有 U、k，但明確寫 95% 常態區間 → u≈a/1.96。", "只知道最大允差 ±a → 通常用矩形分布 u=a/√3。", "有證據顯示中央最可能、極端很少 → 可用三角形分布 u=a/√6。"]
    },
    warning: "不要因為 Type B 看起來主觀就省略。若缺資料，應以合理且偏保守的分布記錄判斷依據。",
    code: `u_rect <- function(a) a / sqrt(3)\nu_tri  <- function(a) a / sqrt(6)\nu_norm95 <- function(a) a / qnorm(0.975)\nc(rect = u_rect(0.2),\n  triangular = u_tri(0.2),\n  normal95 = u_norm95(0.2))`,
    steps: [["1 讀資訊", "確認 ±a 是界限、U 或信賴區間。"], ["2 選分布", "依極端值可能性與來源說明。"], ["3 轉成 u", "統一成標準不準度尺度。"]],
    quiz: [
      {q:"只知道容量瓶誤差界限為 ±0.2 mL，界限內各值同樣可能。u 為？", opts:["0.2/√3","0.2/√6","0.2×2"], a:0, why:"均勻可能對應矩形分布，標準不準度為 a/√3。"},
      {q:"Type A 與 Type B 的差別主要是？", opts:["隨機或系統誤差","評估資訊與方法","數值大小"], a:1, why:"分類依據是評估方法；兩者都可描述不同效應，最後都轉成 u。"}
    ]
  },
  {
    id: 8, group: "不準度", title: "合成、擴展與符合性判定", level: "中階",
    lead: "把各來源傳遞到結果，合成為 uᶜ，再以涵蓋因子得到 U。最後把結果、U、單位、k 與決策規則一起報告。",
    source: "QUAM:2012.P1, Ch. 8–9（合成、擴展與報告）及 Fig. 2（限值情境）",
    goals: ["合成獨立不準度來源", "區分 uᶜ 與 U", "用事先約定的決策規則判斷限值"],
    terms: [["uc", "Combined standard uncertainty", "合成標準不準度", "把各來源傳到結果後合成，相當於結果的一個標準差尺度。"], ["U", "Expanded uncertainty", "擴展不準度", "把 uc 乘以涵蓋因子 k，得到較寬且方便報告的區間半寬。"], ["k", "Coverage factor", "涵蓋因子", "由 uc 換成 U 的倍數；常見 k=2 但不是固定真理。"], ["Sensitivity coefficient", "Sensitivity coefficient", "靈敏度係數", "某個輸入量改變一點時，最後結果會改變多少。"], ["Compliance", "Conformity / compliance", "符合性", "判斷結果是否符合規格或法規限值。"], ["Decision rule", "Decision rule", "決策規則", "事先約定如何把量測不準度納入合格或不合格判定。"]],
    image: "assets/img/fig_compliance.png", caption: "結果區間接近限值時，判定取決於事先約定的決策規則。",
    concepts: [["合成 uᶜ", "將各標準不準度經靈敏度係數傳遞後平方和開根號。"], ["擴展 U", "U = k × uᶜ；k 與涵蓋機率、分布和自由度有關。"], ["決策規則", "必須在看結果前約定，並說明錯判風險。"]],
    formula: "uᶜ(y) = √Σ[cᵢu(xᵢ)]²；U = k × uᶜ",
    symbols: [["y", "由測量模型算出的最終結果", "結果單位"], ["xᵢ", "第 i 個輸入量，例如質量、體積或純度", "各自單位"], ["u(xᵢ)", "輸入量 xᵢ 的標準不準度", "與 xᵢ 相同"], ["cᵢ", "靈敏度係數 ∂y/∂xᵢ，把輸入不準度傳到結果", "結果單位/xᵢ 單位"], ["uᶜ(y)", "結果 y 的合成標準不準度", "結果單位"], ["k", "涵蓋因子", "無單位"], ["U", "擴展不準度，等於 k×uᶜ", "結果單位"]],
    formulaNote: "平方和形式假設各輸入獨立；若輸入相關，必須加入共變異項。k=2 常近似 95% 涵蓋，但不是永遠精確。",
    warning: "k=2 只是在常見條件下約對應 95% 涵蓋，並非永遠精確；小自由度或非正態分布要另行評估。",
    code: `u <- c(repeatability=0.006, calibration=0.004,\n       blank=0.002, volume=0.0015, recovery=0.005)\nuc <- sqrt(sum(u^2))\nU <- 2 * uc\nc(uc = uc, U = U)`,
    steps: [["1 傳遞", "把來源換成對結果 y 的貢獻。"], ["2 合成", "獨立來源平方和開根號。"], ["3 報告", "結果 ±U、單位、k、涵蓋資訊與決策規則。"]],
    quiz: [
      {q:"若 uᶜ = 0.07 mg/kg 且 k=2，U 為？", opts:["0.035","0.07","0.14"], a:2, why:"U = k × uᶜ = 2 × 0.07 = 0.14 mg/kg。"},
      {q:"結果區間跨越法規限值時，最嚴謹的做法是？", opts:["永遠判合格","依事先約定的決策規則並揭露風險","只看測得值"], a:1, why:"符合性結論不能脫離決策規則與錯判風險。"}
    ]
  },
  {
    id: 9, group: "進階", title: "不準度預算、Kragten 與 Monte Carlo", level: "進階",
    lead: "當公式複雜或分布不對稱，除了解析傳遞，還可用 Kragten 數值法或 Monte Carlo 模擬。三者是相互核對的工具，不是三套互斥信仰。",
    source: "QUAM:2012.P1, Appendix E.2–E.3（Kragten 與 Monte Carlo）及 Example A1",
    goals: ["建立不準度預算", "理解 Kragten 單因子擾動", "用 Monte Carlo 產生結果分布與涵蓋區間"],
    terms: [["Uncertainty budget", "Uncertainty budget", "不準度預算", "列出所有來源、標準不準度、靈敏度與貢獻的表格。"], ["Kragten", "Kragten numerical method", "Kragten 數值法", "每次只改變一個輸入量，觀察結果變化來估計該來源貢獻。"], ["MC", "Monte Carlo simulation", "Monte Carlo 模擬", "從各輸入分布反覆抽樣，直接觀察輸出結果會如何分布。"], ["Distribution", "Probability distribution", "機率分布", "描述某個輸入可能出現哪些值，以及各值出現的可能性。"], ["Correlation", "Correlation", "相關性", "兩個輸入會一起變動的程度；忽略相關性可能使合成結果錯誤。"], ["seed", "Random seed", "亂數種子", "固定模擬所用亂數序列，讓別人可以重現相同結果。"]],
    image: "assets/img/fig_montecarlo.png", caption: "Monte Carlo 直接由輸入分布模擬輸出分布，適合非線性與不對稱問題。",
    concepts: [["不準度預算", "表列估計值、u、分布、靈敏度係數與貢獻。"], ["Kragten", "每次將一個輸入增加其 u，觀察輸出變化。"], ["Monte Carlo", "反覆從輸入分布抽樣，直接取得輸出分布。"]],
    formula: "c(Cd) = 1000 × m × P / V；比較解析、Kragten 與模擬結果",
    symbols: [["c(Cd)", "配製後鎘標準液的濃度", "mg/L"], ["m", "所稱取鎘材料的質量", "mg"], ["P", "材料純度，以質量分率表示", "無單位"], ["V", "標準液最後體積", "mL"], ["1000", "依本例 mg、mL 與 mg/L 關係使用的單位換算因子", "L/mL"]],
    formulaNote: "執行前先確認 m 與 V 的單位；若改用 g 或 L，1000 的換算關係也必須跟著改變。",
    warning: "Monte Carlo 次數多不代表模型正確。輸入分布、相關性與測量模型若錯，模擬會很精密地給出錯答案。",
    code: `set.seed(2024)\nN <- 100000\nm <- rnorm(N, 100.28, 0.05)\nP <- rnorm(N, 0.9999, 0.000058)\nV <- rnorm(N, 100.0, 0.07)\ny <- 1000 * m * P / V\nc(sd = sd(y), quantile(y, c(.025, .975)))`,
    steps: [["1 建預算", "先確認每個輸入、單位、分布與相關性。"], ["2 模擬", "固定 seed 讓教學結果可重現。"], ["3 比對", "與解析/Kragten 的 u 和區間比較。"]],
    quiz: [
      {q:"Monte Carlo 最適合下列何種情況？", opts:["模型高度非線性或輸出不對稱","只想少寫幾行程式","沒有測量模型"], a:0, why:"模擬能處理非線性和非正態傳遞，但仍需要正確模型與輸入分布。"},
      {q:"設定 set.seed() 的主要目的？", opts:["提高準確度","讓隨機模擬可重現","自動增加樣本數"], a:1, why:"相同 seed 與程式會產生相同隨機序列，便於教學、稽核與除錯。"}
    ]
  },
  {
    id: 10, group: "進階", title: "綜合實務：從原始資料到可辯護報告", level: "綜合",
    lead: "把數據品管、校正、異常值、不準度預算與符合性判定串成一份可追溯的食品分析報告，並用飼料粗纖維與標準曲線案例收尾。",
    source: "Nielsen Ch. 4 綜合應用；QUAM:2012.P1 Examples A1、A6 與 Appendix E.4",
    goals: ["規劃完整分析資料流程", "選擇 top-down 或 bottom-up 證據", "產出含限制與決策規則的結果報告"],
    terms: [["Top-down", "Top-down approach", "由上而下法", "利用方法驗證、長期品管、能力試驗或協同試驗的整體表現估計不準度。"], ["Bottom-up", "Bottom-up approach", "由下而上法", "從測量模型逐項找出、量化並合成每個不準度來源。"], ["Traceability", "Metrological traceability", "計量追溯性", "量測結果可透過有文件的校正鏈連到適當參考標準。"], ["CRM", "Certified reference material", "有證標準參考物質", "具有證書參考值與不準度，可用來檢查方法偏差的材料。"], ["PT", "Proficiency testing", "能力試驗", "不同實驗室分析同類樣品，用來檢查實驗室表現。"], ["Evidence chain", "Evidence chain", "證據鏈", "從原始資料、品管、計算到判定都可追查的完整紀錄。"]],
    image: "assets/img/fig_budget.png", caption: "不準度預算讓主導來源一目了然，也能指引下一步方法改善。",
    concepts: [["證據鏈", "原始資料→品管→計算→不準度→判定均可追溯。"], ["Top-down", "用驗證、能力試驗或協同試驗的整體精密度/偏差資訊。"], ["Bottom-up", "由測量模型逐項量化與合成來源。"]],
    formula: "完整報告 = 結果 ± U + 單位 + k/涵蓋資訊 + 方法/基質 + 決策規則",
    symbols: [["結果", "經必要校正後的被測量估計值", "依分析項目"], ["U", "與結果同單位的擴展不準度", "結果單位"], ["±", "表示以結果為中心呈現擴展不準度半寬", "—"], ["k", "由合成標準不準度換成 U 的涵蓋因子", "無單位"], ["涵蓋資訊", "U 對應的涵蓋機率或其近似說明", "%"], ["決策規則", "結果接近限值時，如何納入不準度判定", "文字規則"]],
    formulaNote: "報告中的結果與 U 應使用一致的小數位；同時註明方法、基質與適用的判定規則。",
    warning: "量測不準度不是品質裝飾。若未納入抽樣、基質或方法定義的主要效應，需在報告限制中明確說明。",
    code: `result <- 1002.7\nuc <- 0.864\nk <- 2\nU <- k * uc\nsprintf("c(Cd) = (%.1f ± %.1f) mg/L, k=%g",\n        result, U, k)`,
    steps: [["1 驗證資料", "檢查品管、校正與異常值決策。"], ["2 估計 U", "選擇與方法成熟度相稱的證據。"], ["3 溝通決策", "報告適用範圍、限制與判定規則。"]],
    quiz: [
      {q:"成熟標準方法已有適切協同試驗資料時，可優先考慮？", opts:["只算天平解析度","Top-down 整體方法表現","完全忽略偏差"], a:1, why:"適切的再現性、偏差與能力試驗資料可涵蓋多個實際來源，但仍須確認適用範圍。"},
      {q:"下列哪一份報告最完整？", opts:["鉛 0.085","鉛 0.085±0.018 mg/L","鉛 (0.085±0.018) mg/L，U，k=2，約95%，並載明方法與決策規則"], a:2, why:"不準度類型、涵蓋資訊、單位、方法脈絡與決策規則共同支持可解讀性。"}
    ]
  },
  {
    id: 11, group: "延伸工具", title: "metRology 專業工具箱", level: "選修", required: false, requiresPackage: "metRology",
    lead: "先用前 10 章理解原理，再用 metRology 把測量模型、標準不準度、相關性與分布轉成可稽核的計算。這一章會讓 GUM、Kragten 與 Monte Carlo 使用同一組鎘標準液輸入，直接比較三種結果。",
    source: "CRAN metRology 0.9-29-2：GUM、uncert 與 uncertMC 官方文件；QUAM:2012.P1 Appendix E.2–E.3",
    goals: ["用命名清單建立 metRology 輸入", "比較 GUM、Kragten 與 Monte Carlo 的 uc", "解讀敏感度、貢獻率、k 與 U"],
    terms: [["metRology", "metRology R package", "R 的計量統計套件", "協助進行不準度傳遞、有效自由度、貢獻與模擬計算的工具。"], ["CRAN", "Comprehensive R Archive Network", "R 綜合套件典藏網", "下載 R 與經檢查套件的官方網路平台。"], ["GUM", "Guide to the Expression of Uncertainty in Measurement", "量測不準度表示指南方法", "以測量模型、標準不準度與靈敏度係數合成結果。"], ["uncert()", "Uncertainty calculation function", "不準度計算函數", "metRology 中以同一介面選擇 GUM、Kragten 或 MC 的函數。"], ["uncertMC()", "Monte Carlo uncertainty function", "Monte Carlo 不準度函數", "依輸入分布模擬輸出分布的專用函數。"], ["B", "Number of Monte Carlo replicates", "模擬次數", "Monte Carlo 要重複抽樣幾次；B 太小時結果可能不穩。"]],
    image: "assets/img/fig_budget.png", caption: "metRology 可把各輸入量對合成標準不準度的貢獻整理成預算，協助辨認改善優先順序。",
    concepts: [["GUM()", "輸出 y、uc、有效自由度、涵蓋因子 k、U、敏感度與貢獻。"], ["uncert()", "以同一介面選擇 GUM、NUM、kragten、k2 或 MC 方法。"], ["uncertMC()", "直接從輸入分布模擬輸出；可明確設定分布、相關性與模擬次數。"]],
    formula: "同一模型、同一輸入 → 比較 uc(GUM)、uc(Kragten)、uc(MC)，差異過大就回查非線性、分布與相關性",
    symbols: [["uc", "合成標準不準度", "結果單位"], ["GUM", "以靈敏度係數進行的一階不準度傳遞", "方法名稱"], ["Kragten", "逐一擾動各輸入量的數值傳遞法", "方法名稱"], ["MC", "Monte Carlo：從輸入分布反覆抽樣的模擬法", "方法名稱"], ["同一輸入", "三種方法須使用相同估計值、u、分布與相關性", "比較前提"]],
    formulaNote: "三者不是用來挑選最小結果；差異是檢查非線性、分布設定、相關性或模擬穩定性的診斷訊號。",
    warning: "套件不會替你判斷被測量、Type A/B 證據或分布是否合理。Monte Carlo 的預設 B=200 只適合快速示範，本例明確使用 B=100000；相關的非正態輸入需另行確認方法限制。",
    code: `if (!requireNamespace("metRology", quietly = TRUE)) {
  stop("請先執行 install.packages('metRology')")
}

x <- list(m = 100.28, P = 0.9999, V = 100.0)
u <- list(m = 0.05, P = 0.000058, V = 0.07)
model <- ~ 1000 * m * P / V

gum <- metRology::uncert(model, x=x, u=u, method="GUM")
kragten <- metRology::uncert(model, x=x, u=u, method="kragten")
set.seed(2024)
mc <- metRology::uncert(model, x=x, u=u,
                        method="MC", B=100000, keep.x=FALSE)

c(GUM=unname(gum$u), Kragten=unname(kragten$u),
  Monte_Carlo=unname(mc$u))`,
    steps: [["1 固定模型與輸入", "三種方法必須使用相同的 x、u、單位與相關性假設。"], ["2 比較 uc", "本案例三種結果都約為 0.863 mg/L。"], ["3 追查差異", "若差距明顯，檢查非線性、分布、相關性與模擬穩定性。"]],
    quiz: [
      {q:"metRology::uncert(..., method=\"MC\") 的預設模擬次數 B=200，正式比較時較適合怎麼做？", opts:["保留 200 且不設 seed","提高 B、設定 seed，並檢查結果穩定性","只改成 method=\"GUM\""], a:1, why:"提高 B 可降低模擬抽樣誤差；固定 seed 讓分析可重現，但模型與分布仍須合理。"},
      {q:"GUM、Kragten 與 Monte Carlo 結果明顯不同時，最合理的下一步？", opts:["只保留數字最小的方法","回查模型非線性、輸入分布、相關性與程式設定","把三個結果直接平均"], a:1, why:"方法差異是診斷訊號，不應用挑選或平均掩蓋；需回到模型與假設查核。"}
    ]
  },
  {
    id: 12, group: "延伸工具", title: "實務案例：天平、滴定與 HPLC 不準度", level: "選修", required: false,
    lead: "把前面學到的測量模型與不準度預算放進三種常見食品分析流程。每個案例都從原始讀值開始，先轉成標準不準度，再合成 uc、計算 U，最後練習用正確單位報告。",
    source: "QUAM:2012.P1 Ch. 6–9 的建模、量化、合成與報告原則；數值為食品分析教學案例",
    goals: ["計算天平兩次讀值相減的不準度", "建立酸鹼滴定的相對不準度預算", "拆解 HPLC 校正、重複性、稀釋與回收率來源"],
    terms: [["HPLC", "High-performance liquid chromatography", "高效液相層析", "先把樣品成分分離，再以偵測器訊號進行定性或定量的儀器分析法。"], ["EW", "Equivalent weight", "當量重", "在指定化學反應中，每一當量所對應的物質質量；本例用於換算檸檬酸。"], ["DF", "Dilution factor", "稀釋倍數", "原液濃度相對於稀釋後溶液濃度的倍數。"], ["External calibration", "External calibration", "外部校正法", "用另外配製的標準液建立校正線，再計算樣品濃度。"], ["Repeatability", "Repeatability", "重複性", "相同人員、設備與短時間條件下，重複結果彼此一致的程度。"], ["Recovery", "Recovery", "回收率", "分析流程實際測回已知添加量的比例，用來評估前處理與基質造成的偏差。"]],
    image: "assets/img/fig_budget.png", caption: "三個案例都使用同一條證據鏈：測量模型 → 標準不準度 → 貢獻率 → uc → U。",
    concepts: [["天平淨重", "毛重與皮重相減；需同時考慮重複性、校正、解析度及兩次讀值的相關性。"], ["酸鹼滴定", "滴定體積、標準液濃度、樣品質量與終點判讀會共同傳遞到酸度。"], ["HPLC 定量", "校正曲線、樣品進樣重複性、稀釋、回收率及基質效應不可只用 r² 取代。"]],
    formula: "獨立來源：uc = √Σuᵢ²；乘除模型可先合成相對不準度；U = k × uc",
    symbols: [["uᵢ", "第 i 個已傳遞到結果單位的標準不準度分量", "結果單位"], ["Σ", "把所有分量的平方加總", "—"], ["uc", "各分量合成後的標準不準度", "結果單位"], ["k", "涵蓋因子；本案例教學取 2", "無單位"], ["U", "擴展不準度 k×uc", "結果單位"], ["相對不準度", "u(x)/x，適合乘除模型合成", "無單位或 %"]],
    formulaNote: "只有在分量近似獨立時才能直接平方和；天平兩次讀值、校正參數或共用器材可能相關，需另加共變異。",
    warning: "案例數值只示範計算流程，不能直接套用到你的方法。正式評估須換成實驗室校正證書、標定、方法驗證、長期品管與基質資料，並檢查相關性與是否重複計入來源。",
    code: `combine_u <- function(estimate, components, k = 2) {
  uc <- sqrt(sum(components^2))
  data.frame(result = estimate, uc = uc, k = k, U = k * uc)
}

# 任一案例都可把「已傳遞到結果單位」的各項 u 放進來
u_demo <- c(repeatability = 0.006,
            calibration = 0.004,
            volume = 0.002)
combine_u(0.085, u_demo)`,
    steps: [["1 寫測量模型", "先決定結果如何由讀值、濃度、體積與質量算出。"], ["2 統一尺度", "把證書、解析度與重複資料換成標準不準度。"], ["3 合成與報告", "傳遞到結果單位後計算 uc、U、貢獻率與限制。"]],
    caseStudies: [
      {
        title: "案例 A｜天平淨重：兩次讀值不能只算一次解析度",
        model: "m_net = m_gross − m_tare（g）",
        note: "以 5 次淨重重複資料估計平均值的 Type A 分量；校正與解析度各有毛重、皮重兩次讀值。若兩次讀值高度相關，共同校正偏差可能抵消，正式作業須處理共變異。",
        code: `net <- c(5.4326, 5.4324, 5.4327, 5.4325, 5.4326)
m_net <- mean(net)
u_repeat <- sd(net) / sqrt(length(net))
u_cal_read <- 0.0004 / 2
u_res_read <- 0.0001 / sqrt(12)
u_mass <- c(repeatability = u_repeat,
            calibration = sqrt(2) * u_cal_read,
            resolution = sqrt(2) * u_res_read)
combine_u(m_net, u_mass)`
      },
      {
        title: "案例 B｜酸鹼滴定：果汁可滴定酸",
        model: "A = V × C × EW ÷ 1000 ÷ m × 100（g/100 g，以檸檬酸計）",
        note: "V 同時含滴定重複性、滴定管證書、解析度與終點判讀；再與 NaOH 標定濃度及樣品質量的相對不準度合成。",
        code: `V_rep <- c(12.44, 12.47, 12.45, 12.48)
V <- mean(V_rep); C <- 0.1002; EW <- 64.04; m <- 10.000
A <- V * C * EW / 1000 / m * 100
u_V <- sqrt((sd(V_rep)/sqrt(length(V_rep)))^2 +
            (0.030/2)^2 + (0.01/sqrt(12))^2 +
            (0.020/sqrt(3))^2)
rel_u <- c(volume = u_V/V,
           standardization = 0.00020/C,
           sample_mass = (0.001/sqrt(3))/m)
combine_u(A, A * rel_u)`
      },
      {
        title: "案例 C｜HPLC：咖啡因外部校正與稀釋",
        model: "c_sample = [(ȳ_sample − b₀) ÷ b₁] × DF（mg/L）",
        note: "將校正曲線殘差、樣品重複進樣、稀釋器材與回收率分開估計。此處是入門近似；正式方法還要檢查斜率與截距共變異、異方差、萃取及基質效應。",
        code: `x <- c(5,10,20,30,40,50)
y <- c(512,1007,2018,2996,4015,5004)
fit <- lm(y ~ x)
y_sample <- c(2528,2539,2522); DF <- 5
x_hat <- (mean(y_sample)-coef(fit)[1])/coef(fit)[2]
caffeine <- x_hat * DF
Sxx <- sum((x-mean(x))^2)
u_curve <- sigma(fit)/abs(coef(fit)[2]) *
  sqrt(1/length(x)+(x_hat-mean(x))^2/Sxx) * DF
u_repeat <- sd(y_sample)/sqrt(length(y_sample)) /
  abs(coef(fit)[2]) * DF
rel_DF <- sqrt((0.006/1.000)^2+(0.08/5.00)^2)
u_hplc <- c(curve=u_curve, repeatability=u_repeat,
            dilution=caffeine*rel_DF,
            recovery=caffeine*0.010)
combine_u(caffeine, u_hplc)`
      }
    ],
    quiz: [
      {q:"天平以毛重減皮重得到淨重時，解析度分量通常涉及幾次讀值？", opts:["一次","兩次，並應考慮兩讀值的相關性","完全不用考慮"], a:1, why:"毛重與皮重各有一次顯示讀值；若假設獨立可平方和合成，但同一台天平的共同效應可能相關。"},
      {q:"HPLC 校正曲線 r² 很高時，是否能忽略校正曲線的不準度？", opts:["可以","不可以，仍要評估殘差、校正參數、範圍與樣品位置","只有稀釋倍數大時可以"], a:1, why:"r² 不是預測不準度；曲線殘差、參數共變異與樣品在校正範圍的位置都可能影響結果。"}
    ]
  }
];

const stateKey = "food-analysis-qc-course-v1";
const defaultState = { current: 1, completed: [], answers: {}, largeType: false, startedAt: new Date().toISOString() };
let state = loadState();

function loadState() {
  try { return { ...defaultState, ...JSON.parse(localStorage.getItem(stateKey) || "{}") }; }
  catch { return { ...defaultState }; }
}
function saveState() { localStorage.setItem(stateKey, JSON.stringify(state)); }
function escapeHtml(text) { return String(text).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]); }

function renderNav() {
  const nav = document.querySelector("#chapterNav");
  let group = "";
  nav.innerHTML = chapters.map(ch => {
    const heading = ch.group !== group ? `<p class="nav-group">${group = ch.group}</p>` : "";
    const done = state.completed.includes(ch.id);
    return `${heading}<button class="chapter-link ${state.current === ch.id ? "active" : ""}" data-chapter="${ch.id}" type="button" aria-current="${state.current === ch.id ? "page" : "false"}"><span class="chapter-number">${ch.id}</span><span class="chapter-title">${ch.title}</span><span class="done-mark">${done ? "✓" : ""}</span></button>`;
  }).join("");
  nav.querySelectorAll("[data-chapter]").forEach(btn => btn.addEventListener("click", () => goToChapter(Number(btn.dataset.chapter))));
}

function renderLesson() {
  const ch = chapters[state.current - 1];
  const code = escapeHtml(ch.code);
  document.querySelector("#lessonContent").innerHTML = `
    <p class="breadcrumb">${ch.group}　›　第 ${ch.id} 章　›　${ch.level}</p>
    <h1>${ch.title}</h1>
    <p class="lesson-lead">${ch.lead}</p>
    <p class="source-line">內容依據：${ch.source}。文字為教學性改寫，正式作業請回查原始來源與實驗室程序。</p>
    ${renderTermGuide(ch)}
    ${renderVisualGuide(ch)}
    <figure class="visual"><img src="${ch.image}" alt="${ch.caption}" loading="eager">${ch.visualLabels ? `<div class="visual-labels">${ch.visualLabels.map(label => `<span>${label}</span>`).join("")}</div>` : ""}<figcaption>${ch.caption}</figcaption></figure>
    ${renderVisualExplanations(ch)}
    <h2>先掌握三個核心概念</h2>
    <div class="concept-grid">${ch.concepts.map(c => `<div class="concept"><strong>${c[0]}</strong><p>${c[1]}</p></div>`).join("")}</div>
    <div class="formula">${ch.formula}</div>
    ${renderFormulaHelp(ch)}
    ${renderWeightedRegressionGuide(ch)}
    ${renderTypeBGuide(ch)}
    <div class="callout"><strong>容易踩雷：</strong> ${ch.warning}</div>
    <h2>R 入門實作：三步驟看資料</h2>
    <p>${ch.requiresPackage ? `本選修單元需要 ${ch.requiresPackage}；若尚未安裝，程式會顯示明確的安裝提示。建議先完成前 10 章再執行。` : "先逐行貼到 R Console（指令輸入區）；看到結果後，再一次執行整段。本章範例只使用 R 內建函數，不必安裝套件。"}</p>
    <section class="r-lab" aria-label="R 程式範例">
      <div class="r-lab-header"><strong>第 ${ch.id} 章最小可執行範例</strong><button class="copy-code" data-copy-scope="main" type="button">複製程式</button></div>
      <pre><code>${code}</code></pre>
      <div class="r-steps">${ch.steps.map(s => `<div class="r-step"><strong>${s[0]}</strong><br>${s[1]}</div>`).join("")}</div>
    </section>
    <div class="download-row"><a href="R/${String(ch.id).padStart(2,"0") === "01" ? "ch01_basics" : chapterFile(ch.id)}.R" download>下載本章 R 程式檔</a><a href="downloads/food-analysis-statistics-R.md" download>下載全部 R 程式（Markdown 純文字檔）</a></div>
    ${renderCaseStudies(ch)}
    <section class="quiz" aria-labelledby="quizTitle"><h2 id="quizTitle">本章學習檢核</h2><p>選擇答案後立即顯示理由；答案會保存在這台裝置。</p>${ch.quiz.map((q,i) => renderQuestion(ch,q,i)).join("")}</section>
    <div class="lesson-actions"><span class="completion-note">答完本章所有題目後，將${ch.required === false ? "選修單元" : "本章"}標記完成。</span><button class="button button-primary" id="completeChapter" type="button">${state.completed.includes(ch.id) ? (ch.required === false ? "已完成選修單元 ✓" : "已完成本章 ✓") : (ch.id === 10 ? "完成必修並前往選修工具箱" : ch.required === false ? "完成選修單元" : "完成本章並前往下一章")}</button></div>`;

  document.querySelectorAll(".copy-code").forEach(button => button.addEventListener("click", copyCode));
  document.querySelectorAll("input[type=radio]").forEach(input => input.addEventListener("change", answerQuestion));
  document.querySelector("#completeChapter").addEventListener("click", completeChapter);
  document.querySelector("#goalList").innerHTML = ch.goals.map(g => `<li>${g}</li>`).join("");
  restoreAnswers(ch);
}

function chapterFile(id) {
  return ({2:"ch02_ci_normal",3:"ch03_method_qc",4:"ch04_regression",5:"ch05_outliers_sigfig",6:"ch06_uncertainty_concept",7:"ch07_typeAB_distributions",8:"ch08_combine_report",9:"ch09_kragten_montecarlo",10:"ch10_capstone",11:"extension_metrology_toolbox",12:"extension_lab_uncertainty_cases"})[id];
}
function renderTermGuide(ch) {
  if (!ch.terms?.length) return "";
  const terms = ch.source.includes("QUAM") && !ch.terms.some(term => term[0] === "QUAM")
    ? [["QUAM", "Quantifying Uncertainty in Analytical Measurement", "分析量測不準度定量指南", "Eurachem/CITAC 發布的化學分析實務指南，本課程量測不準度章節的主要參考資料。"], ...ch.terms]
    : ch.terms;
  return `<section class="term-guide" aria-labelledby="termGuideTitle">
    <div class="term-guide-heading"><div><p class="eyebrow">初學者詞彙表</p><h2 id="termGuideTitle">英文與縮寫先讀懂</h2></div><p>本章第一次遇到這些詞時，先看中文與白話解釋，不需要先背英文。</p></div>
    <div class="term-grid">${terms.map(term => `
      <article class="term-card">
        <div class="term-name"><strong>${term[0]}</strong><span>${term[2]}</span></div>
        <p class="term-english">${term[1]}</p>
        <p>${term[3]}</p>
      </article>`).join("")}</div>
  </section>`;
}
function renderFormulaHelp(ch) {
  if (!ch.symbols?.length) return "";
  return `<section class="formula-help" aria-labelledby="formulaHelpTitle">
    <h3 id="formulaHelpTitle">公式符號怎麼看？</h3>
    <div class="symbol-table" role="table" aria-label="公式符號、意義與單位">
      <div class="symbol-row symbol-header" role="row"><span role="columnheader">符號</span><span role="columnheader">代表意義</span><span role="columnheader">單位</span></div>
      ${ch.symbols.map(item => `<div class="symbol-row" role="row"><code role="cell">${item[0]}</code><span role="cell">${item[1]}</span><span class="symbol-unit" role="cell">${item[2]}</span></div>`).join("")}
    </div>
    ${ch.formulaNote ? `<p class="formula-condition"><strong>使用條件：</strong> ${ch.formulaNote}</p>` : ""}
  </section>`;
}
function renderTypeBGuide(ch) {
  if (!ch.typeBGuide) return "";
  return `<section class="typeb-guide" aria-labelledby="typeBGuideTitle">
    <div class="typeb-heading"><p class="eyebrow">選擇分布，不是選最小答案</p><h3 id="typeBGuideTitle">Type B 分布適用在什麼情況？</h3><p>${ch.typeBGuide.intro}</p></div>
    <div class="distribution-grid">${ch.typeBGuide.cases.map(item => `
      <article class="distribution-card">
        <h4>${item.name}</h4>
        <p class="distribution-equation">${item.equation}</p>
        <p><strong>適用：</strong>${item.when}</p>
        <p class="distribution-example">${item.example}</p>
      </article>`).join("")}</div>
    <div class="certificate-rule"><strong>證書已給 U 與 k 時：</strong> ${ch.typeBGuide.certificate}</div>
    <div class="decision-flow"><h4>初學者判斷流程</h4><ol>${ch.typeBGuide.flow.map(step => `<li>${step}</li>`).join("")}</ol></div>
    <p class="typeb-summary"><strong>核心觀念：</strong>Type B 是「資訊來源的評估方式」，不是某一種固定分布。分布要依 ±a 的來源與含義選擇。</p>
  </section>`;
}
function renderWeightedRegressionGuide(ch) {
  const guide = ch.weightedRegressionGuide;
  if (!guide) return "";
  return `<section class="weighted-guide" aria-labelledby="weightedGuideTitle">
    <div class="weighted-heading"><p class="eyebrow">寬濃度範圍的校正策略</p><h3 id="weightedGuideTitle">何時需要加權迴歸？</h3><p>${guide.intro}</p></div>
    <div class="weighted-equation">${guide.equation}</div>
    <div class="weighted-symbols" aria-label="加權迴歸公式符號">${guide.symbols.map(item => `<div><code>${item[0]}</code><span>${item[1]}</span></div>`).join("")}</div>
    <h4>常見候選權重</h4>
    <div class="weight-grid">${guide.candidates.map(item => `<article class="weight-card"><h5>${item[0]}</h5><p class="weight-equation">${item[1]}</p><p>${item[2]}</p></article>`).join("")}</div>
    <div class="weight-checks"><h4>權重怎麼選？</h4><ol>${guide.checks.map(item => `<li>${item}</li>`).join("")}</ol></div>
    <div class="weight-caution"><strong>重要限制：</strong>${guide.caution}</div>
    <div class="weighted-example"><h4>R 實作：HPLC 咖啡因寬範圍校正</h4><p>比較 OLS、1/x 與 1/x² 後，觀察各濃度回算偏差；不要只挑 r² 最大的模型。</p><pre><code>${escapeHtml(guide.code)}</code></pre></div>
  </section>`;
}
function renderVisualGuide(ch) {
  if (!ch.visualGuide) return "";
  return `<section class="visual-guide" aria-labelledby="visualGuideTitle">
    <h2 id="visualGuideTitle">${ch.visualGuide.title}</h2>
    <p>${ch.visualGuide.lead}</p>
    <div class="dot-legend" aria-label="圖例"><span><i class="dot dot-reference" aria-hidden="true"></i>紅點：參考值／目標值</span><span><i class="dot dot-measurement" aria-hidden="true"></i>藍點：重複量測結果</span></div>
    <div class="reading-questions">${ch.visualGuide.questions.map(item => `<div><strong>${item[0]}</strong><p>${item[1]}</p></div>`).join("")}</div>
    <p class="look-first"><strong>看圖順序：</strong>先看藍點之間的距離，再看整群藍點與紅點的距離。</p>
  </section>`;
}
function renderVisualExplanations(ch) {
  if (!ch.visualExplanations?.length) return "";
  return `<section class="visual-explanations" aria-labelledby="visualExplainTitle">
    <h2 id="visualExplainTitle">逐格判讀：圖形如何對應統計數字？</h2>
    <div class="panel-explanation-grid">${ch.visualExplanations.map(item => `
      <article class="panel-explanation">
        <span class="panel-key">(${item.key})</span>
        <h3>${item.title}</h3>
        <p>${item.body}</p>
        <p class="data-link">${item.data}</p>
      </article>`).join("")}</div>
    <div class="concept-bridge"><strong>圖與數據的連結：</strong> ${ch.visualBridge}</div>
  </section>`;
}
function renderCaseStudies(ch) {
  if (!ch.caseStudies?.length) return "";
  return `<section class="case-library" aria-labelledby="caseLibraryTitle">
    <h2 id="caseLibraryTitle">三個食品分析量測不準度完整案例</h2>
    <p>每一例先讀測量模型，再逐行執行 R；比較各分量時，請確認它們已換成相同的結果單位。</p>
    ${ch.caseStudies.map((item, index) => `
      <article class="case-study">
        <div class="case-heading"><div><span class="case-tag">案例 ${index + 1}</span><h3>${item.title}</h3></div><button class="copy-code case-copy" data-case-index="${index}" type="button">複製案例程式</button></div>
        <p class="case-model"><strong>測量模型：</strong>${item.model}</p>
        <p>${item.note}</p>
        <pre><code>${escapeHtml(item.code)}</code></pre>
      </article>`).join("")}
  </section>`;
}
function renderQuestion(ch, q, index) {
  return `<fieldset class="question" data-question="${index}"><legend>${index + 1}. ${q.q}</legend>${q.opts.map((o,j) => `<label class="option"><input type="radio" name="q${ch.id}-${index}" value="${j}"><span>${o}</span></label>`).join("")}<div class="feedback" role="status" aria-live="polite"></div></fieldset>`;
}
function answerQuestion(event) {
  const field = event.target.closest(".question");
  const index = Number(field.dataset.question);
  const ch = chapters[state.current - 1];
  const selected = Number(event.target.value);
  const correct = selected === ch.quiz[index].a;
  state.answers[`${ch.id}-${index}`] = { selected, correct, answeredAt: new Date().toISOString() };
  saveState();
  showFeedback(field, correct, ch.quiz[index].why);
}
function showFeedback(field, correct, why) {
  const feedback = field.querySelector(".feedback");
  feedback.className = `feedback show ${correct ? "correct" : "incorrect"}`;
  feedback.textContent = `${correct ? "答對了。" : "再想一下。"} ${why}`;
}
function restoreAnswers(ch) {
  ch.quiz.forEach((q,i) => {
    const answer = state.answers[`${ch.id}-${i}`];
    if (!answer) return;
    const field = document.querySelector(`[data-question="${i}"]`);
    const radio = field.querySelector(`input[value="${answer.selected}"]`);
    if (radio) radio.checked = true;
    showFeedback(field, answer.correct, q.why);
  });
}
async function copyCode(event) {
  const ch = chapters[state.current - 1];
  const caseIndex = event.target.dataset.caseIndex;
  const text = caseIndex === undefined ? ch.code : ch.caseStudies[Number(caseIndex)].code;
  try { await navigator.clipboard.writeText(text); event.target.textContent = "已複製 ✓"; }
  catch { event.target.textContent = "請手動選取程式"; }
  const original = caseIndex === undefined ? "複製程式" : "複製案例程式";
  setTimeout(() => event.target.textContent = original, 1800);
}
function completeChapter() {
  const ch = chapters[state.current - 1];
  const answered = ch.quiz.every((_,i) => state.answers[`${ch.id}-${i}`]);
  if (!answered) { document.querySelector(".quiz").scrollIntoView({behavior:"smooth"}); alert("請先回答本章所有題目，再標記完成。"); return; }
  if (!state.completed.includes(ch.id)) state.completed.push(ch.id);
  state.completed.sort((a,b) => a-b);
  saveState();
  if (ch.id < chapters.length) goToChapter(ch.id + 1); else { renderAll(); document.querySelector("#completeChapter").textContent = "已完成選修單元 ✓"; }
}
function goToChapter(id) {
  state.current = id; saveState(); renderAll();
  document.querySelector("#lesson").focus({preventScroll:true}); window.scrollTo({top:0, behavior:"smooth"});
}
function updateProgress() {
  const requiredChapters = chapters.filter(ch => ch.required !== false);
  const n = requiredChapters.filter(ch => state.completed.includes(ch.id)).length;
  const percent = Math.round(n / requiredChapters.length * 100);
  document.querySelector("#progressPercent").textContent = `${percent}%`;
  document.querySelector("#progressCount").textContent = `必修已完成 ${n} / ${requiredChapters.length} 章`;
  document.querySelector("#progressRing").style.setProperty("--progress", `${percent * 3.6}deg`);
  document.querySelector("#progressRing").setAttribute("aria-label", `整體學習進度 ${percent}%`);
  document.querySelector("#navProgressText").textContent = `${n} / ${requiredChapters.length}`;
  document.querySelector("#navProgressBar").style.width = `${percent}%`;
}
function exportResults() {
  const rows = [["章","章名","題號","作答","是否正確","作答時間","章節完成"]];
  chapters.forEach(ch => ch.quiz.forEach((q,i) => {
    const a = state.answers[`${ch.id}-${i}`];
    rows.push([ch.id,ch.title,i+1,a ? q.opts[a.selected] : "未作答",a ? (a.correct ? "是" : "否") : "",a?.answeredAt || "",state.completed.includes(ch.id) ? "是" : "否"]);
  }));
  const csv = "\ufeff" + rows.map(row => row.map(cell => `"${String(cell).replaceAll('"','""')}"`).join(",")).join("\r\n");
  const url = URL.createObjectURL(new Blob([csv], {type:"text/csv;charset=utf-8"}));
  const a = Object.assign(document.createElement("a"), {href:url, download:`食品分析學習成果_${new Date().toISOString().slice(0,10)}.csv`});
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  document.querySelector("#exportStatus").textContent = "已建立 CSV 下載檔。";
}
function renderAll() { renderNav(); renderLesson(); updateProgress(); }

document.querySelector("#fontToggle").addEventListener("click", () => { state.largeType = !state.largeType; document.body.classList.toggle("large-type", state.largeType); saveState(); });
document.querySelector("#exportResults").addEventListener("click", exportResults);
document.querySelector("#resetProgress").addEventListener("click", () => { if (confirm("確定要清除所有作答與完成紀錄嗎？")) { state = {...defaultState, startedAt:new Date().toISOString()}; saveState(); renderAll(); } });
document.body.classList.toggle("large-type", state.largeType);
renderAll();
