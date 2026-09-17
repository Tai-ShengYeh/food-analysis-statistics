# 全站共用迷思 key（種子表）

同一個迷思跨章請用同一個 key；這裡沒有的再自行新增（全大寫蛇形英文）。各章 `MISC` 只需列出該章用到的 key。

| key | 學生「以為」 |
|---|---|
| PRECISION_IS_ACCURACY | 以為重複性好（SD/CV 小）就代表結果準確 |
| SD_VS_SEM | 分不清標準差 SD 與平均數標準誤 SEM |
| SD_N_NOT_N_MINUS_1 | 樣本標準差用 n 而不是 n−1 當分母 |
| CV_UNIT | 以為 CV 有單位，或忘了乘 100／除以平均 |
| SYSTEMATIC_FIXED_BY_REPEATS | 以為多做幾次重複就能消除系統誤差 |
| CI_TRUE_VALUE_PROB | 以為「真值有 95% 機率落在這個區間」 |
| CI_COVERS_DATA | 把信賴區間當成涵蓋 95% 量測數據的範圍 |
| DF_EQUALS_N | 自由度用 n 而不是 n−1 |
| USED_Z_NOT_T | 小樣本仍用 Z=1.96 而不是 t |
| FORGOT_SQRT_N | 算 SEM／CI 時忘了除以 √n |
| MORE_CONFIDENCE_NARROWER | 以為信心水準越高區間越窄 |
| ONE_TAIL_TWO_TAIL | 單尾／雙尾機率用錯（如 qt(0.95) 當雙尾 95%） |
| LOD_EQUALS_LOQ | 分不清 LOD（偵測得到）與 LOQ（可以定量） |
| LOD_WRONG_MULTIPLIER | LOD/LOQ 的 3 倍、10 倍倍數用錯 |
| CONTROL_LIMIT_IS_SPEC | 把管制界限（製程自己的 ±3s）當成規格／法規限值 |
| SHEWHART_ONLY_OUT_OF_LIMIT | 以為管制圖只要沒有點超出 ±3s 就沒問題（忽略趨勢與連串） |
| R2_PROVES_LINEAR | 以為 r² 很高就證明線性、不用看殘差圖 |
| R_VS_R2 | 分不清相關係數 r 與決定係數 r² |
| EXTRAPOLATION_SAFE | 以為標準曲線可以外插到最高標準品以外 |
| SLOPE_INTERCEPT_SWAP | 反推濃度時斜率、截距位置弄反或忘了減截距 |
| SIGFIG_KEEP_ALL_DIGITS | 把計算機／軟體顯示的位數全部報出來 |
| SIGFIG_ADD_MUL_RULE | 加減法（看小數位）與乘除法（看有效位數）規則混用 |
| ROUND_INTERMEDIATE | 在中間步驟就先四捨五入 |
| OUTLIER_DELETE_BY_TEST_ONLY | 以為檢定顯著就可以直接刪除數據，不必找原因與記錄 |
| OUTLIER_DELETE_BY_EYE | 看起來怪就刪，不做檢定也不記錄 |
| OUTLIER_TEST_REPEAT | 對同一組數據反覆做異常值檢定直到滿意 |
| ERROR_EQUALS_UNCERTAINTY | 把誤差（單一差值）與不確定度（範圍）當成同一件事 |
| UNC_MEANS_MISTAKE | 以為不確定度大代表實驗做錯了 |
| TYPEA_RANDOM_TYPEB_SYSTEMATIC | 以為 Type A＝隨機誤差、Type B＝系統誤差 |
| RECT_WRONG_DIVISOR | 矩形／三角／常態分布轉標準不確定度時除數用錯（√3、√6、k） |
| TOLERANCE_IS_STD_UNC | 直接把規格容許差 ±a 當成標準不確定度 |
| UNC_LINEAR_ADD | 把不確定度分量直接相加而不是平方和開根號 |
| UNC_ABS_REL_MIX | 乘除模型該用相對不確定度卻用絕對值（或相反） |
| SMALL_COMPONENT_MATTERS | 以為每個小分量都要花力氣精算（不知道平方和由最大分量主導） |
| K2_ALWAYS_95 | 以為 k=2 永遠恰好是 95%（忽略有效自由度） |
| U_VS_UC | 分不清合成標準不確定度 u_c 與擴展不確定度 U |
| COMPLIANCE_IGNORE_U | 判定是否符合限值時只看測值、不看不確定度 |
| UNC_TOO_MANY_DIGITS | 不確定度報太多位數，或結果與不確定度位數不一致 |
| MC_MORE_ACCURATE_ALWAYS | 以為 Monte Carlo 一定比 GUM 公式法「更正確」 |
| MC_TOO_FEW_TRIALS | 以為模擬幾百次就夠、不知結果會隨次數／種子波動 |
| CORRELATION_IGNORED | 忽略輸入量之間的相關（共變異） |
| MATRIX_EFFECT_IGNORED | 以為溶劑標準曲線可直接用於複雜基質樣品 |
| IS_FIXES_EVERYTHING | 以為加了內標準就不必評估基質效應／回收率 |
| WEIGHTING_UNNEEDED | 以為跨多個數量級的校正曲線不需要加權 |
| P_VALUE_IS_PROB_H0 | 以為 p 值是「H0 為真的機率」 |
| NONSIG_MEANS_EQUAL | 以為不顯著就等於相等 |
| SIG_MEANS_IMPORTANT | 以為統計顯著就等於實務上重要 |
| PSEUDO_REPLICATION | 把同一樣品溶液的重複注射／重複讀值當成獨立重複 |
| MULTIPLE_T_OK | 以為三組以上可以兩兩做 t 檢定取代 ANOVA |
| OFAT_IS_ENOUGH | 以為一次改一個因子（OFAT）就能找到最適條件，不需要因子設計 |
| INTERACTION_IGNORED | 交互作用顯著時仍單獨解讀主效應 |
| CENTER_POINTS_USELESS | 不知道中心點重複是用來估純誤差與檢查曲率 |
| OPTIMUM_OUTSIDE_REGION | 把落在實驗範圍外的駐點當成可信的最適條件 |
| R_FUNCTION_CONFUSION | R 函數或參數用錯（如 pnorm/qnorm、qt 的機率參數） |
| EXCEL_FUNCTION_CONFUSION | Excel 函數用錯（如 T.INV vs T.INV.2T、STDEV.P vs STDEV.S） |
| UNIT_CONVERSION | 單位換算錯誤（mg/kg、%、ppm…） |
| OTHER | 不對應特定迷思的湊數選項（盡量少用） |
