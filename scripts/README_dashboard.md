# quiz_dashboard.py — 教師端測驗成效報表

**用途**：離線讀取本站（FAS）Firestore `student_events` 測驗紀錄，產生單檔 HTML 報表，
呈現全班學習成效與學生卡關處，不需前端讀取權限（前端只能寫入）。

## 一行指令

```bash
python scripts/quiz_dashboard.py
```

常用參數：`--key PATH`（金鑰路徑，預設讀環境變數 `FAS_SA_KEY`，再退到
`C:\Users\USER\.fb_admin\sa_key.json`）、`--class A`、`--since 2026-09-01`、
`--out report/quiz_report.html`、`--show-id`（顯示學號）、`--include-test`（不排除測試帳號）、
`--dump-json report/raw.json`（存原始事件備用）、`--from-json report/raw.json`（離線重跑，不連線）、
`--demo`（合成假資料跑一次完整流程，輸出 `report/demo_report.html`，方便驗證環境是否正常）。

## 報表怎麼看

1. **總覽**：學生數、事件數、資料期間、各章完成人數。
2. **各章成效**：前測/課後平均答對率，以及 **normalized gain g = (post−pre)/(1−pre)**——
   g 越接近 1 代表原本不會的、學完後幾乎都學會了；g 接近 0 或負值代表教學沒有明顯拉高答對率
   （只計入前測與課後皆有作答、且前測未滿分的學生）。
3. **逐題表**：每題的作答人數、答對率、跳過率、**鑑別度 D**（該章課後總分排序後，
   高分組 27% 與低分組 27% 的答對率差；D 越高代表這題越能分辨「學會」與「沒學會」的學生，
   D < 0.2 通常代表題目設計待調整；作答人數 < 10 時顯示「n 太小」不強行計算）、
   平均信心、最常見的錯誤選項與對應迷思、中位作答時間。答對率 < 50% 或 D < 0.2 的列會標色提醒。
4. **迷思熱區**：全站迷思 tag 在各章被選中的人次與佔比，用來看哪個錯誤觀念最普遍、最該在課堂澄清。
5. **信心 × 對錯**：四象限人次，特別留意「**高信心卻答錯**」——這代表學生很確定但觀念是錯的，
   比「沒把握答錯」更需要優先在課堂上點名處理，報表列出全站前 10 題。
6. **我還不懂的地方**：學生章末填的开放式回饋，預設不顯示學號（加 `--show-id` 才顯示）；
   同時輸出純文字檔 `report/muddiest_points.txt`，方便整份貼給 LLM 做分群摘要。
7. **個別學生表**（`--show-id` 才輸出）：每位學生各章 pre/post 分數，供個別關心用。

## 金鑰安全

- 金鑰路徑只透過 `--key` 或環境變數 `FAS_SA_KEY` 指定，**絕對不要把金鑰檔或金鑰內容複製進本 repo**。
- `--dump-json` 只存事件內容（學號、作答紀錄等教學資料），不含任何憑證，但仍請視為內部資料，
  不要外流；`report/` 建議加進 `.gitignore`（本次未自動修改，請自行加入）。

## Firestore 欄位對照

事件集合 `student_events`，本站以 `site == "fas"`、`game == "fas_quiz"`、
`chapter` 形如 `"FAS-CH02"` 區隔。主要欄位：`student_id`、`class_id`、`session_id`、
`client_ts`（ISO 字串，前端產生）、`event_type ∈ {answer, attempt_complete, self_check}`、
`phase ∈ {pre, post, spaced}`、`question_id`、`attempts`（第幾次作答，**只有 attempts 最小
且 client_ts 最早的一筆列入成效分析**）、`is_correct`、`skipped`、`choice_idx`／`choice_value`、
`misconception`（迷思 tag）、`confidence`（1–3）、`latency_ms`、`final_score`／`total`
（attempt_complete 用）、`free_text`（self_check 用）。詳細定義見 `assets/js/assess.js`
的 `toDoc()` 與 `docs/QUIZ_SCHEMA.md`。
