# 全站迷思字典（Misconception keys）

本檔由 `python scripts/merge_misc_keys.py` 自各章 `const MISC` 產生，請勿手改。
出題時**先在這裡找有沒有語意相同的 key**，有就沿用；沒有才新增（全大寫蛇形英文，描述用一句白話寫學生「以為什麼」）。
新增或發現同義 key 後重跑腳本，再跑 `node scripts/check_quiz.js`。

共 192 個 key。

| key | 學生「以為」 | 使用章節 |
|---|---|---|
| `ABS_VS_REL_ERROR` | 分不清絕對誤差與相對誤差 | ch01 |
| `ACC_PREC_SWAP` | 把準確度與精密度的定義弄反 | ch00 |
| `ALPHA_ADDS_LINEAR` | 以為整體 α 就是直接相加 k × α | ch15, ch16 |
| `ALPHA_BETA_SWAP` | 把型一錯誤（誤判有差）和型二錯誤（漏掉真差異）弄反 | ch15 |
| `ANOVA_SIG_ALL_DIFFER` | 以為 ANOVA 顯著就代表每一組彼此都不同 | ch16 |
| `ANOVA_TESTS_VARIANCE` | 以為 ANOVA 是在檢定各組的變異數是否相等 | ch16 |
| `ASSUME_EQUAL_VAR` | 以為兩樣本 t 檢定一定要（或可以隨意）假設變異數相等 | ch15 |
| `ATWATER_FACTOR_MIX` | Atwater 係數用錯（脂肪該乘 9 卻乘 4，或碳水與脂肪的係數對調） | ch13 |
| `BLANK_NOISE_IGNORED` | 以為儀器讀值不為 0 就代表有測到（忽略空白雜訊） | ch03 |
| `BLOCK_F_IS_THE_FINDING` | 把區集因子（樣品）的顯著當成研究發現，忽略真正要比較的處理 | ch17 |
| `BRANDED_LABEL_AS_TRUTH` | 把市售標籤值（廠商自報、經過捨入）當成精確的分析真值 | ch13 |
| `BUDGET_SHARE_LINEAR` | 以為不確定度預算的占比是 u 直接相除，而不是變異數（u²）占比 | ch10, ch12 |
| `CAL_P_VS_N` | 分不清未知樣品的重複測定數 p 與校正點數 n 各影響公式的哪一項 | ch11 |
| `CENTER_POINTS_USELESS` | 不知道中心點重複是用來估純誤差與檢查曲率 | ch14 |
| `CHEAPEST_INGREDIENT_GREEDY` | 以為最低成本配方就是盡量多用單價最便宜的原料，忽略規格限制的連動 | ch13 |
| `CI_COVERS_DATA` | 把信賴區間當成涵蓋 95% 量測數據的範圍 | ch02, ch04, ch15 |
| `CI_IS_PRECISION` | 以為 95% 指的是方法的精密度或準確率 | ch02, ch15 |
| `CI_OVERLAP_AS_TEST` | 以為看兩組各自的信賴區間有沒有重疊就能代替檢定 | ch15 |
| `CI_TRUE_VALUE_PROB` | 以為「真值有 95% 機率落在這個區間」 | ch02, ch04, ch11, ch14, ch15 |
| `CODED_UNIT_CONVERSION` | 編碼值換回實際單位時算錯（忘了乘半範圍、忘了加中心值，或把軸點當成 ±1） | ch14 |
| `COMMERCIAL_SOFTWARE_MAGIC` | 以為商業配方軟體有無法重現的專有魔法，而不是質量平衡＋加權平均這類基礎代數 | ch13 |
| `COMPLIANCE_IGNORE_U` | 判定是否符合限值時只看測值、不看不確定度 | ch08, ch10, ch11, ch12 |
| `COMPLIANCE_RULE_MISAPPLIED` | 保守決策規則用錯：區間跨過限值的灰色地帶卻直接判成符合或不符合 | ch08, ch10, ch11, ch12 |
| `CONF_BAND_UNIFORM` | 以為標準曲線各處反推的不確定度都一樣（不知道信賴帶中段最窄、兩端變寬） | ch04, ch11 |
| `CONTROL_LIMIT_IS_SPEC` | 把管制界限（製程自己的 ±3s）當成規格／法規限值 | ch03, ch11 |
| `CORRELATION_IGNORED` | 忽略輸入量之間的相關（共變異） | ch09 |
| `CV_INVERTED` | 把 CV 算成「平均 ÷ 標準差」（分子分母顛倒） | ch01 |
| `CV_UNIT` | 以為 CV 有單位，或忘了乘 100／除以平均 | ch00, ch01, ch11 |
| `DF_EQUALS_N` | 自由度用 n 而不是 n−1 | ch02, ch05, ch08, ch11, ch15 |
| `DF_MISREAD_AS_N` | 把 ANOVA 表的自由度直接當成樣本數或組數 | ch16 |
| `DF_MUST_INTEGER` | 以為自由度一定是整數，Welch 的小數 df 代表算錯 | ch15 |
| `DF_WRONG_K_N` | 自由度用 k 與 N，而不是 k−1 與 N−k | ch16 |
| `DROP_SIGNIFICANT_TERM` | 以為顯著的交互作用項可以直接從模型拿掉，好讓主效應比較好解讀 | ch17 |
| `EFFECT_NOT_AVERAGED` | 算效應時只把高、低水準的反應值相減加總，忘了各自取平均 | ch14 |
| `EFFECT_VS_COEF` | 分不清效應（高水準平均−低水準平均）與編碼係數（效應的一半） | ch14 |
| `EIGEN_SIGN_SWAP` | 特徵值符號與極大／極小／鞍點的對應弄反或弄錯 | ch14 |
| `EMPIRICAL_METHOD_BIAS` | 不知道經驗（操作定義）方法的結果由方法本身定義，仍以為有獨立的真值要去修正偏倚 | ch06, ch11 |
| `EMPIRICAL_NO_UNC` | 以為經驗方法沒有真值，所以不需要（或無法）評估不確定度 | ch11 |
| `ERROR_EQUALS_UNCERTAINTY` | 把誤差（單一差值）與不確定度（範圍）當成同一件事 | ch00, ch06, ch10, ch11, ch12 |
| `ERROR_TYPE_CONFUSION` | 分不清系統誤差、隨機誤差與疏失 | ch01, ch03, ch04 |
| `ETA2_USED_WITHIN` | 算 η² 時把組內 SS 放在分子，算成「沒被解釋的比例」 | ch16 |
| `ETA2_WRONG_DENOM` | 算 η² 時分母用 SS_within 而不是 SS_total | ch16 |
| `EXCEL_FUNCTION_CONFUSION` | Excel 函數用錯（如 T.INV vs T.INV.2T、STDEV.P vs STDEV.S） | ch01, ch02, ch03, ch04, ch05, ch07, ch10, ch11, ch12, ch13, ch14 |
| `EXTRAPOLATION_SAFE` | 以為標準曲線可以外插到最高標準品以外 | ch04, ch07, ch11, ch14 |
| `FDC_COVERS_ALL` | 以為公開資料庫涵蓋所有原料，不需要供應商規格書（COA） | ch13 |
| `FIRST_ORDER_FINDS_OPTIMUM` | 以為兩水準／一階（直線、平面）模型就能決定最適點 | ch14 |
| `FORGOT_DIVIDE_N` | 算日間變異時忘了把 (MS_between − MS_within) 除以每天重複數 n | ch17 |
| `FORGOT_SQRT_N` | 算 SEM／CI 時忘了除以 √n | ch02, ch05, ch11, ch15 |
| `FORWARD_NOT_INVERSE` | 反推濃度時把訊號直接代入 x 去算 y（方向弄反） | ch04 |
| `F_FORGOT_DF` | 算 F 時直接拿兩個 SS 相除，忘了先各自除以自由度 | ch16, ch17 |
| `F_FOR_MEANS` | 以為 F 檢定（var.test）是用來比較兩組平均值 | ch15 |
| `GUM_STEP_ORDER` | GUM 四步驟順序弄錯（沒先定義被測量與模型就開始找來源或計算） | ch06 |
| `H0_ABOUT_SAMPLE` | 以為假說講的是樣本平均，而不是母體平均 | ch16 |
| `INSTRUMENT_DECIDES_UNC` | 以為不確定度主要由儀器等級決定（儀器好就可忽略、要改善就換儀器），忽略方法與取樣 | ch10, ch11, ch12, ch13 |
| `INTERACTION_IGNORED` | 交互作用顯著時仍單獨解讀（或只報告）主效應 | ch14, ch17 |
| `INTERACTION_IS_ARTIFACT` | 以為交互作用圖的線不平行是實驗失誤，線「應該」要平行 | ch17 |
| `INTERACTION_IS_CORRELATION` | 把「交互作用」當成兩個因子彼此相關或互相影響對方的設定 | ch14, ch17 |
| `INTERACTION_WITHOUT_REPLICATES` | 以為每格只有一筆（或把重複先平均成一筆）也能檢定交互作用 | ch17 |
| `INTERCEPT_SIGN_ERROR` | 截距的正負號處理錯（該減卻加、減負數沒有變成加） | ch04 |
| `IS_ANY_COMPOUND` | 以為任何化合物都能當內標補償基質效應（不需共析出、化學性質相近） | ch12 |
| `IS_FIXES_EVERYTHING` | 以為加了內標準就不必評估基質效應／回收率 | ch12 |
| `IS_ONLY_INJECTION` | 以為內標只是用來修正進樣體積（或確認有進樣），與基質／電離效應無關 | ch12 |
| `K2_ALWAYS_95` | 以為 k=2 永遠恰好是 95%（忽略有效自由度） | ch08, ch09, ch11 |
| `KRAGTEN_MC_CONFUSED` | 把 Kragten（逐項加 u 重算）與 Monte Carlo（隨機抽樣）弄混 | ch09, ch11 |
| `KRAGTEN_NEEDS_CALCULUS` | 以為不會偏微分就無法評估各來源的貢獻（不知道數值法可以取代） | ch09 |
| `LOD_EQUALS_LOQ` | 分不清 LOD（偵測得到）與 LOQ（可以定量） | ch03, ch06, ch11 |
| `LOD_FORGOT_BLANK` | 算 LOD/LOQ 時忘了加上空白平均值 | ch03 |
| `LOD_WRONG_MULTIPLIER` | LOD/LOQ 的 3 倍、10 倍倍數用錯 | ch03, ch06, ch11 |
| `LOF_DF_SWAPPED` | 失擬與純誤差的自由度放反 | ch17 |
| `LOF_P_SMALL_IS_GOOD` | 把失擬檢定讀反：以為 p 值小代表模型配得好 | ch17 |
| `LOF_USED_TOTAL_RESID` | 把直線模型的整個殘差（含純誤差）當成失擬 | ch17 |
| `LOF_WITHOUT_REPLICATES` | 以為每個濃度沒有重複也能做失擬檢定 | ch17 |
| `LP_INTERIOR_OPTIMUM` | 不知道線性目標的最佳解必在可行範圍的端點（以為在中間折衷點、要微分或逐一試算） | ch13 |
| `MATRIX_EFFECT_IGNORED` | 以為溶劑標準曲線可直接用於複雜基質樣品 | ch03, ch12 |
| `MC_MORE_ACCURATE_ALWAYS` | 以為 Monte Carlo 一定比 GUM 公式法「更正確」 | ch09, ch11, ch12 |
| `MC_RANDOM_UNUSABLE` | 以為 Monte Carlo 用亂數、每次結果略有不同，所以不可信、不能用 | ch09 |
| `MC_REPLACES_DATA` | 以為模擬可以取代或補足真實的實驗數據 | ch09 |
| `MC_TOO_FEW_TRIALS` | 以為模擬幾百次就夠、不知結果會隨次數／種子波動 | ch09, ch11, ch12 |
| `MDL_EQUALS_LOD` | 以為 MDL 與 LOD 是同一件事（都只看空白／儀器噪音） | ch03 |
| `MEAN_VS_MEDIAN` | 分不清平均數與中位數 | ch01 |
| `MEMORIZE_BEFORE_LEARN` | 以為要先把名詞與公式全部背熟才能開始學 | ch00 |
| `ME_RATIO_INVERTED` | 基質效應比值的分子分母放反（A/B），或把正負號解讀相反（壓制當增強） | ch12 |
| `ME_VS_RE` | 分不清 Matuszewski 三個比值：ME（B/A，電離）、RE（C/B，萃取回收）、PE（C/A，整體） | ch12 |
| `MORE_CONFIDENCE_NARROWER` | 以為信心水準越高區間越窄 | ch02 |
| `MORE_MEASUREMENTS_REPLACE_REPLICATES` | 以為同一天／同一批多測幾次，就能取代不同天／不同批的獨立重複 | ch17 |
| `MORE_REPEATS_MORE_ERROR` | 以為重複次數越多，累積的誤差越大（平均值越不準） | ch02 |
| `MORE_TERMS_ALWAYS_LOWER_P` | 以為模型多放因子 p 值就一定變小，把區集當成過度配適 | ch17 |
| `MULTI_T_NO_INFLATION` | 以為多組兩兩 t 檢定時，整體型一錯誤率仍是 0.05 | ch15, ch16 |
| `NEGATIVE_SOLUTION_OK` | 以為聯立方程數學上解得出來就是可行配方，忽略用量不能為負 | ch13 |
| `NEGATIVE_VARIANCE_ABS` | 把負的變異數估計值取絕對值再開根號 | ch17 |
| `NEGATIVE_VARIANCE_IS_ERROR` | 以為 s_between² 算出負值一定是算錯 | ch17 |
| `NEGATIVE_VARIANCE_LITERAL` | 把負的變異數估計值當真，解讀成「隔天做反而更精密」 | ch17 |
| `NEWER_DATA_BETTER` | 以為資料越新品質就越好，忽略採樣與分析方法等後設資料 | ch13 |
| `NONPARAM_FIXES_INDEPENDENCE` | 以為換成無母數或 Welch 方法、或增加讀值次數，就能補救不獨立的實驗設計 | ch16 |
| `NONSIG_MEANS_EQUAL` | 以為「不顯著」就證明兩者相等、沒有差異 | ch15, ch16 |
| `NORMALITY_ON_RAW_Y` | 對混在一起的原始 y（而不是殘差）檢查常態性 | ch16 |
| `N_MINUS_1_OVERAPPLIED` | 以為平均數也要除以 n−1 | ch01 |
| `OFAT_IS_ENOUGH` | 以為一次改一個因子（OFAT）就能找到最適條件，不需要因子設計 | ch14 |
| `ONE_TAIL_TWO_TAIL` | 單尾／雙尾機率用錯（如 qt(0.95) 當雙尾 95%） | ch02, ch07, ch08, ch11 |
| `OPTIMUM_OUTSIDE_REGION` | 把落在實驗範圍外的駐點當成可信的最適條件 | ch14 |
| `OTHER` | 不對應特定迷思的湊數選項（盡量少用） | ch00, ch01, ch02, ch03, ch04, ch06, ch07, ch08, ch09, ch10, ch11, ch12, ch13, ch14 |
| `OUTLIER_DELETE_BY_EYE` | 看起來怪就刪，不做檢定也不記錄 | ch01, ch03, ch04, ch05, ch09, ch11 |
| `OUTLIER_DELETE_BY_TEST_ONLY` | 以為檢定顯著就可以直接刪除數據，不必找原因與記錄 | ch05, ch08, ch11, ch16 |
| `OUTLIER_DELETE_FOR_PRECISION` | 為了讓 SD 變小、配適變漂亮或結果變顯著而刪除數據 | ch05, ch08, ch16, ch17 |
| `OUTLIER_NEVER_DELETE` | 以為任何情況刪數據都是學術不端（即使有確認的失誤紀錄） | ch06 |
| `OUTLIER_QUOTA` | 以為每組數據都有固定可以刪除的名額 | ch05, ch16 |
| `OUTLIER_TEST_REPEAT` | 對同一組數據反覆做異常值檢定直到滿意 | ch05, ch08, ch11 |
| `PAIRED_AS_INDEPENDENT` | 成對設計的數據卻用兩獨立樣本 t 檢定 | ch15, ch17 |
| `PAIRS_EQUALS_GROUPS` | 把兩兩比較的次數當成組數（k 組其實有 k(k−1)/2 對） | ch15, ch16 |
| `PE_LOF_SWAPPED` | 把純誤差與失擬弄反：以為各濃度平均離迴歸線的距離是純誤差 | ch17 |
| `POOLED_SD_AS_INTERMEDIATE` | 把全部數據直接丟進 sd()，當成中間精密度 | ch17 |
| `POSTHOC_CHERRY_PICK` | 看完數據才挑最大和最小的兩組做 t 檢定，以為這樣不算多重比較 | ch16 |
| `POSTHOC_ONE_TAIL` | 看到數據方向（或 p 值）之後才決定改用單尾檢定 | ch15 |
| `POWER_AS_ERROR` | 把檢定力當成一種錯誤（其實是正確偵測到差異的機率） | ch15 |
| `PRECISION_IS_ACCURACY` | 以為重複性好（SD/CV 小）就代表結果準確 | ch00, ch01, ch03, ch05, ch06, ch10, ch11 |
| `PSEUDO_REPLICATION` | 把同一樣品溶液的重複注射／重複讀值當成獨立重複 | ch10, ch13, ch14, ch15, ch16, ch17 |
| `P_COMPLEMENT_PROB_H1` | 以為 1 − p 是「H1 為真（差異是真的）的機率」 | ch15 |
| `P_HACKING` | 為了得到想要的 p 值而挑選分析方法、尾數或樣本數 | ch15 |
| `P_IS_PROB_H0` | 以為 p 值是「H0 為真（沒有差異）的機率」 | ch15 |
| `P_SMALL_BIG_EFFECT` | 以為 p 值越小代表差異（效果）越大 | ch15 |
| `Q_CRIT_MISREAD` | Q 檢定的判定基準弄錯（拿 Q 跟 1 比、查錯 n 的臨界值或方向弄反） | ch05 |
| `Q_GAP_RANGE_WRONG` | Dixon Q 的 gap／全距取錯（分子分母顛倒、取到非可疑端的間距、或用到平均值） | ch05 |
| `Q_VS_GRUBBS` | 把 Dixon Q（gap÷全距）與 Grubbs G（離均差÷SD）的算法混用 | ch05 |
| `R2_IS_ACCURACY` | 以為 r² 是準確率（多少比例的樣品測對、誤差多少 %） | ch04 |
| `R2_PROVES_LINEAR` | 以為 r²（或 r）很高就證明線性、不用看殘差圖 | ch04, ch07, ch11, ch12, ch14, ch17 |
| `RECOVERY_CORRECTION_CONFUSION` | 回收率修正的方向或次數弄錯（該除卻乘、重複修正或忘了修正） | ch10, ch12 |
| `RECT_WRONG_DIVISOR` | 矩形／三角／常態分布轉標準不確定度時除數用錯（√3、√6、k） | ch07, ch09, ch10, ch11 |
| `REJECT_WHEN_P_LARGE` | 把判定方向弄反：以為 p 大於 α 才拒絕 H0 | ch15 |
| `REL_ERROR_DENOMINATOR` | 相對誤差除以測得值而不是真值 | ch01 |
| `REL_ERROR_SIGN` | 相對誤差的正負號弄反或丟掉（用真值減測值） | ch01 |
| `REL_UNC_CONSTANT` | 以為相對不確定度在所有含量層級都一樣 | ch11 |
| `REPEATABILITY_AS_INTERMEDIATE` | 以為短期重複性（同一天、同一批的重複）就能代表長期的中間精密度 | ch10, ch13, ch17 |
| `REPEATABILITY_VS_REPRODUCIBILITY` | 分不清重複性 s_r（同實驗室短期）與再現性 s_R（跨實驗室） | ch11 |
| `RETEST_UNTIL_PASS` | 以為結果不理想就重測到滿意為止 | ch03 |
| `REVERSE_ENG_UNIQUE` | 以為逆向工程反推出來的配方就是競品唯一的真實配方 | ch13 |
| `RULE_68_95_997_MIXUP` | 68–95–99.7 法則的 ±1／±2／±3 SD 對應記錯 | ch02 |
| `R_ERROR_MEANS_BROKEN` | 看到 R 的紅字錯誤訊息就以為軟體壞了或數據有問題（不會先讀訊息找原因） | ch00 |
| `R_FUNCTION_CONFUSION` | R 函數或參數用錯（如 pnorm/qnorm、qt 的機率參數） | ch01, ch07, ch08, ch09, ch10, ch11, ch13, ch14 |
| `R_THRESHOLD_REPLACES_RESIDUALS` | 以為只要 r ≥ 0.997 就不必再看殘差圖 | ch17 |
| `R_VS_R2` | 分不清相關係數 r 與決定係數 r² | ch04, ch11 |
| `SBETWEEN_AS_INTERMEDIATE` | 只拿日間分量 s_between 當中間精密度，漏掉重複性 s_r | ch17 |
| `SCREENING_SKIPPED` | 以為因子很多時不必先篩選，全部直接上完整的全因子／反應曲面設計 | ch14 |
| `SD_N_NOT_N_MINUS_1` | 樣本標準差用 n 而不是 n−1 當分母 | ch01, ch11 |
| `SD_VS_SEM` | 分不清標準差 SD 與平均數標準誤 SEM | ch02, ch03, ch04, ch07, ch09, ch10, ch11, ch17 |
| `SEM_IS_CI_HALFWIDTH` | 以為 SEM 本身就是 95% 信賴區間半寬（忘了乘 t） | ch02 |
| `SENSITIVITY_IS_LOD` | 以為靈敏度就是偵測極限，或靈敏度調高 LOD 就一定變好 | ch03 |
| `SERVING_VOLUME_WEIGHT_MIX` | 把體積份量直接當成重量，忽略密度與打入的空氣（overrun） | ch13 |
| `SE_DIVIDE_BY_N` | 標準誤用 SD/n 而不是 SD/√n | ch07, ch15, ch17 |
| `SHEWHART_ONLY_OUT_OF_LIMIT` | 以為管制圖只要沒有點超出 ±3s 就沒問題（忽略趨勢與連串） | ch03, ch11 |
| `SIGFIG_ADD_MUL_RULE` | 加減法（看小數位）與乘除法（看有效位數）規則混用 | ch05 |
| `SIGFIG_DECIMAL_PLACES` | 把小數位數當成有效位數（連前導零也算進去） | ch05 |
| `SIGFIG_KEEP_ALL_DIGITS` | 把計算機／軟體顯示的位數全部報出來 | ch00, ch05, ch11, ch13 |
| `SIGFIG_MECHANICAL_RULE` | 機械套用有效數字規則，不看數字背後的器皿依據（如把稀釋倍數 50 當 1 位） | ch05 |
| `SIGFIG_NOT_LEAST` | 乘除取位時沒有以有效位數最少的那一項為準 | ch05 |
| `SIGFIG_TRAILING_ZERO` | 末端零的規則弄錯：整數末端的零當成有效、或小數點後末端的零不算 | ch05 |
| `SIG_MEANS_CERTAIN` | 以為達到顯著（p 小於 0.05）的結論就一定不會錯 | ch15 |
| `SIG_MEANS_IMPORTANT` | 以為統計顯著就等於實務上重要、一定要處理 | ch15, ch16 |
| `SIMPLE_AVERAGE_NOT_WEIGHTED` | 混合物的成分用簡單平均或直接相加，而不是依用量加權平均 | ch13 |
| `SLOPE_INTERCEPT_SWAP` | 反推濃度時斜率、截距位置弄反或忘了減截距 | ch04, ch12 |
| `SMALL_COMPONENT_MATTERS` | 以為每個小分量都要花力氣精算（不知道平方和由最大分量主導） | ch06, ch09, ch10, ch11 |
| `SMALL_N_SHAPIRO_OK` | 以為 n 很小時 Shapiro 不顯著就證明了資料是常態 | ch16 |
| `SMALL_QUANTITY_SMALL_ERROR` | 以為取用量（體積、質量）越少誤差就越小，忽略相對誤差反而變大 | ch10 |
| `SPURIOUS_AS_RANDOM` | 把人為疏失（抄錯、儀器故障）當成一般誤差，留在數據裡做統計 | ch06 |
| `SR_USED_WITHOUT_CHECK` | 以為協同試驗的 s_R 不必先確認自家實驗室表現相當，就可以直接沿用 | ch11 |
| `STATS_NEEDS_ADVANCED_MATH` | 以為學統計需要高深數學（微積分、心算）才學得會 | ch00 |
| `SYSTEMATIC_FIXED_BY_REPEATS` | 以為多做幾次重複就能消除系統誤差 | ch01, ch02, ch03, ch06, ch07, ch11, ch14 |
| `TOLERANCE_IS_STD_UNC` | 直接把規格容許差 ±a 當成標準不確定度 | ch07, ch09, ch10, ch11 |
| `TOOL_OVER_CONCEPT` | 以為會操作軟體、複製程式跑出數字就夠了，不需要懂觀念 | ch00 |
| `TOPDOWN_DISTRUSTED` | 以為只有逐項拆解才算正確，內部驗證／協同試驗等整體法是偷懶、漏算了分量 | ch10, ch11 |
| `TUKEY_LETTER_MISREAD` | 誤讀字母標示：以為 ab 是另一個顯著不同的等級，或忽略「共用字母＝不顯著」的規則 | ch16 |
| `TYPEA_ALWAYS_DIVIDE_SQRT_N` | 不管報告的是單次值還是平均，Type A 一律用 s/√n | ch07, ch17 |
| `TYPEA_RANDOM_TYPEB_SYSTEMATIC` | 以為 Type A＝隨機誤差、Type B＝系統誤差 | ch07 |
| `TYPEB_ALWAYS_RECT` | 以為 Type B 一律除以 √3（不看有沒有分布形狀、k 或信賴水準的資訊） | ch07 |
| `TYPEB_INFERIOR` | 以為 Type B（證書、規格、經驗）是次等或不可靠的估計，只有重複實驗才算數 | ch07 |
| `UNC_ABS_REL_MIX` | 乘除模型該用相對不確定度卻用絕對值（或相反） | ch07, ch08, ch09, ch10, ch11 |
| `UNC_CANCELS_OUT` | 以為輸入量相加減時，不確定度會跟著相減、互相抵消、變小或維持不變 | ch07, ch08, ch09 |
| `UNC_LINEAR_ADD` | 把不確定度（或標準差）分量直接相加而不是平方和開根號 | ch06, ch07, ch08, ch09, ch10, ch11, ch12, ch17 |
| `UNC_MEANS_MISTAKE` | 以為不確定度大代表實驗做錯了 | ch00, ch06, ch08, ch10, ch11, ch12 |
| `UNC_ONLY_REPEATABILITY` | 以為不確定度就只是重複量測的 SD（忽略校正、純度、體積等其他來源） | ch06 |
| `UNC_SQUARE_STEP_WRONG` | 合成時平方／開根號的步驟弄錯（忘了先平方，或忘了最後開根號） | ch06, ch07, ch08, ch09 |
| `UNC_TOO_MANY_DIGITS` | 不確定度報太多位數，或結果與不確定度位數不一致 | ch08, ch11 |
| `UNC_USED_AS_CORRECTION` | 以為不確定度可以拿來修正結果（像偏倚一樣加減回去） | ch06 |
| `UNDERDETERMINED_MISREAD` | 未知數多於方程式時，誤以為無解或仍然只有唯一解 | ch13 |
| `UNIT_CONVERSION` | 單位換算錯誤（mg/kg、%、ppm…） | ch11, ch13 |
| `USED_Z_NOT_T` | 小樣本仍用 Z=1.96 而不是 t | ch02, ch05, ch08, ch11 |
| `U_VS_UC` | 分不清（合成）標準不確定度 u 與擴展不確定度 U = k·u | ch00, ch08, ch09, ch10, ch11, ch12, ch17 |
| `VALIDATION_MUST_EQUAL` | 以為驗證實驗的實測值必須等於預測值才算通過（忽略預測區間） | ch14 |
| `VAR_VS_SD` | 分不清變異數與標準差（忘了開根號） | ch01 |
| `WARNING_VS_ACTION` | 分不清 ±2s 警告界限與 ±3s 行動界限（該做的處置） | ch03 |
| `WEIGHTING_UNNEEDED` | 以為跨多個數量級的校正曲線不需要加權 | ch04, ch12 |
| `WEIGHT_DIRECTION` | 以為 1/x 加權是加重高濃度點（其實是讓低濃度點有足夠份量） | ch12 |
| `XY_AXIS_SWAP` | 標準曲線的 x（濃度）與 y（訊號）角色弄反，或以為兩軸可互換 | ch04 |
