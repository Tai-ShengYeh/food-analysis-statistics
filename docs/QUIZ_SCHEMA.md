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
- `post` 6–10 題：concept ≥2、calc ≥2（至少 1 題數值填空）、rout ≥1、misc ≥1。
- `spaced` 1 題：回溯 2–3 章之前最重要的迷思（Ch0–Ch2 免）。
- 出題前先查全站迷思字典 `docs/MISCONCEPTIONS.md`，語意相同就沿用既有 key。
- `MISC` 的 key 用全大寫蛇形英文、全站唯一語意（同一迷思跨章請用同一個 key）；value 用一句白話中文描述學生「以為什麼」。

## 引擎行為（出題時要知道）

- 學生先輸入學號才記錄；也可選「訪客練習」（不上傳）。
- 每題附三級信心度（猜的 / 有點把握 / 很確定）。
- **只有第一次作答算成效**；批改後可「再練一次」，事件仍上傳但 `attempts>1`，分析時排除。
- 章末有一格「我還不懂的地方」（≤200 字），以 `self_check` 事件上傳。

## 上傳的事件欄位（Firestore `student_events`，`site == "fas"`、`schema_v: 2`）

- `answer`：`question_id`、`item_version`、`qtype`、`phase`、`quiz_set`、`is_correct`、`skipped`、`choice_idx`（選擇題，原始選項索引）、`choice_value`（數值題）、`misconception`、`confidence`（1–3）、`attempts`、`latency_ms`、`from_chapter`。
- `attempt_complete`：`final_score`、`total`、`answered`、`attempts`、`duration_ms`。
- `self_check`：`question_id = chNN-muddy`、`free_text`。
- `latency_ms` 的定義是「該題最後一次互動時間 − 整份測驗第一次互動時間」，是**累積**時間，不是單題作答時間；要估單題時間請把同一次作答的各題依 `latency_ms` 排序後取差。
- `attempts` 只存在學生的瀏覽器，換裝置或清快取會重新從 1 起算；分析時以「同一學生同一題 `attempts` 最小、`client_ts` 最早」為首次作答（`scripts/quiz_dashboard.py` 已這樣做）。
- 學號一律轉大寫後上傳；與其他課程站的紀錄比對時，對方的學號也要先轉大寫。

## 同一頁的第二組題目

`ch11.html` 除了章末測驗 `QUIZ`，還有期末總測驗 `FINALEXAM`（id 用 `ch11-q21` 起，與章末題號區隔），以
`renderQuiz(el, FINALEXAM, { set: "final", title: "…", muddy: false })` 渲染；`set` 讓兩組題目各自計算作答次數，事件會帶 `quiz_set`。

## 改完題目之後

```
node scripts/check_quiz.js           # 格式、配額、tag、數值題容許範圍；有 ✗ 就不要上線
python scripts/merge_misc_keys.py    # 有新增迷思 key 時：統一描述、更新 docs/MISCONCEPTIONS.md
```

## 章內小遊戲（`assets/js/games.js`）

每章可在內文中插入互動小遊戲，放一個佔位即可，遊戲定義集中在 `assets/js/games.js` 的 `GAMES` 登錄表：

```html
<div class="game" data-game="ch16-predict"></div>
...
<script src="assets/app.js"></script><script src="assets/js/showout.js"></script><script src="assets/js/games.js"></script>
```

目前有兩個原型：

| id | 章 | 型式 | 內容 |
|---|---|---|---|
| `ch16-predict` | Ch16 §16.1 之後 | 猜猜看再揭曉 | 先猜 ANOVA 的 p 值區間、F 值量級、Tukey 哪幾對顯著，再揭曉 R 輸出與 F 值尺 |
| `ch02-cisim` | Ch2 §2.4 之後 | 猜猜看 + 模擬器 | 先猜 100 個 95% CI 漏掉幾個、n 變 4 倍寬度變幾倍、硬用 Z 的覆蓋率，再親手抽樣（n／信心水準／t 或 Z 可切換） |

設計原則：**不需學號也能玩**（有學號且非訪客時事件才上傳）；預測題重用測驗的 `.qitem` 樣式與迷思 tag；揭曉後可「再猜一次」但 `attempts > 1`。

事件走同一條 `fas_queue → assess.js → student_events` 管線，但用以下欄位與測驗分流（`scripts/quiz_dashboard.py` 目前會略過 `game != "fas_quiz"` 的事件，不影響答對率統計）：

- `game = "fas_game"`、`game_id = "<chNN-xxx>"`、`quiz_set = "game"`、`phase = "game"`。
- 每題預測 → `answer`：`question_id = chNN-gNN-N`（例 `ch16-g01-3`）、`qtype = "predict"`、`is_correct`、`choice_idx`／`choice_value`（複選題為 `"011"` 位元字串、數值題為數字）、`misconception`、`attempts`、`latency_ms`。
- 按下揭曉 → `reveal`；整局結束 → `attempt_complete`（`final_score`、`total`、`answered`、`duration_ms`）。
- 模擬器內的操作（抽樣、切換 n）**不**記錄，避免灌爆事件量。

新增遊戲：在 `games.js` 的 `GAMES["chNN-xxx"]` 加一個函式；預測型遊戲用 `predictGame(box, spec)`（單選／複選／數值三種題型），揭曉內容寫在 `spec.reveal(panel, results)`。題目 id 同樣**一經上線永不改、永不重用**。
