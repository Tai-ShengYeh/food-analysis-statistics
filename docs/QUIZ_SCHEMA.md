# 測驗題目格式（Quiz Schema v2）

每章 html 在 `assets/app.js` 之前放一段 classic `<script>`，宣告 `QUIZ`（題目）與 `MISC`（本章迷思字典）。
引擎：`assets/app.js`；事件上傳：`assets/js/assess.js`（Firestore `student_events`）。

```html
<div class="quiz" data-phase="pre"></div>   <!-- 放在「學習目標」之後：課前 3 題 -->
...
<div class="quiz" id="quiz"></div>          <!-- 放在章末：課後題 + 回溯題 + 我還不懂的地方 -->
<script>
const CHAPTER = "ch02";
const MISC = {
  CI_TRUE_VALUE_PROB: "以為「真值有 95% 機率落在這個區間」",
  CI_COVERS_DATA:     "把信賴區間當成涵蓋 95% 量測數據的範圍",
  DF_EQUALS_N:        "自由度用 n 而不是 n−1"
};
const QUIZ = [
  { id:"ch02-q04", v:1, type:"concept", phase:"post",
    q:"「95% 信賴區間」的正確解讀是：",
    opts:["真值有 95% 機率在此區間內","此區間涵蓋 95% 的量測數據","用此方法建構的區間，長期約 95% 會蓋住真值","此方法有 95% 的精密度"],
    ans:2,
    tags:["CI_TRUE_VALUE_PROB","CI_COVERS_DATA",null,"CI_IS_PRECISION"],
    exp:"……" },
  { id:"ch02-q10", v:1, type:"calc", phase:"post",
    q:"n=4、SD=0.2927，95% CI 半寬是多少？（取 3 位小數）",
    num:{ ans:0.466, tol:0.002, unit:"%" },
    errs:[ { val:0.287, tol:0.002, tag:"USED_Z_NOT_T" },
           { val:0.931, tol:0.003, tag:"FORGOT_SQRT_N" } ],
    exp:"……" }
];
</script>
```

## 欄位

| 欄位 | 必填 | 說明 |
|---|---|---|
| `id` | ✔ | `chNN-qNN`（課後）、`chNN-pNN`（前測）、`chNN-sNN`（回溯）。**一經上線永不改、永不重用**；刪題就讓編號留空。 |
| `v` | ✔ | 題目版號，從 1 起。題幹/選項/正解有實質修改就 +1（改錯字不用）。分析時 `id+v` 視為同一題。 |
| `type` | ✔ | `concept` 概念辨析 · `calc` 計算 · `rout` R/Excel 輸出判讀 · `misc` 迷思診斷 |
| `phase` | | `pre` 前測 · `post` 課後（預設）· `spaced` 跨章回溯 |
| `q` | ✔ | 題幹，可含 HTML 與 KaTeX `\\( ... \\)`（JS 字串內反斜線要寫兩個） |
| `opts` + `ans` | 選擇題 | 選項陣列與正解索引（0 起算）。**不要每題都把正解放同一位置。** |
| `tags` | 選擇題 ✔ | 與 `opts` 等長；正解位置放 `null`；每個錯誤選項放一個 `MISC` 的 key。錯誤選項若只是湊數、不對應任何迷思，放 `"OTHER"`，但應盡量少。 |
| `num` + `errs` | 數值題 | `num:{ans,tol,unit}`；`errs` 列出「常見錯誤算法會算出的值」與對應迷思 tag，學生填到該值就被診斷。 |
| `exp` | ✔ | 詳解。要說明**為什麼錯誤選項是錯的**，不只說正解。 |
| `from` | 回溯題 | 這題回溯的是哪一章，如 `"ch02"` |

## 每章配額（目標 10 分鐘內）

- `pre` 3 題：與課後題同構但換數字/換情境，測先備迷思；作答後**不顯示詳解**。
- `post` 6–9 題：concept ≥2、calc ≥2、rout ≥1、misc ≥1。
- `spaced` 1 題：回溯 2–3 章之前最重要的迷思（Ch0–Ch2 免）。
- `MISC` 的 key 用全大寫蛇形英文、全站唯一語意（同一迷思跨章請用同一個 key）；value 用一句白話中文描述學生「以為什麼」。

## 引擎行為（出題時要知道）

- 學生先輸入學號才記錄；也可選「訪客練習」（不上傳）。
- 每題附三級信心度（猜的 / 有點把握 / 很確定）。
- **只有第一次作答算成效**；批改後可「再練一次」，事件仍上傳但 `attempts>1`，分析時排除。
- 章末有一格「我還不懂的地方」（≤200 字），以 `self_check` 事件上傳。
