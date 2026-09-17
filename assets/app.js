/* ==================================================================
   app.js — R 程式碼下載/複製、測驗引擎 v2、單一來源導覽列
   ================================================================== */

/* ---------- 1. R 程式碼區塊：加上標題列 + 複製 + 下載按鈕 ---------- */
document.querySelectorAll("pre.rcode").forEach(function (pre) {
  var fname = pre.dataset.file || "example.R";
  var wrap = document.createElement("div");
  wrap.className = "rcodewrap";
  pre.parentNode.insertBefore(wrap, pre);
  var head = document.createElement("div");
  head.className = "rcodehead";
  head.innerHTML =
    '<span class="fname">📄 ' + fname + "</span>" +
    '<span class="spacer"></span>' +
    '<button type="button" class="ghost act-copy">複製程式碼</button>' +
    '<button type="button" class="act-dl">⬇ 下載 .R</button>';
  wrap.appendChild(head);
  wrap.appendChild(pre);
  head.querySelector(".act-copy").addEventListener("click", function () {
    navigator.clipboard.writeText(pre.textContent).then(function () {
      var b = head.querySelector(".act-copy");
      b.textContent = "✓ 已複製";
      setTimeout(function () { b.textContent = "複製程式碼"; }, 1500);
    });
  });
  head.querySelector(".act-dl").addEventListener("click", function () {
    var blob = new Blob([pre.textContent], { type: "text/x-r;charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = fname;
    a.click();
    URL.revokeObjectURL(a.href);
  });
});

/* ---------- 2. 測驗引擎 v2 ----------
   題目格式見 docs/QUIZ_SCHEMA.md。頁面在本檔之前以 classic <script> 宣告：
     const CHAPTER = "ch02"; const MISC = {...}; const QUIZ = [...];
   容器：<div class="quiz" data-phase="pre"></div>（課前）、<div class="quiz" id="quiz"></div>（課後）
   事件先寫進 localStorage 佇列（fas_queue），由 assets/js/assess.js（module）負責上傳 Firestore；
   兩邊只靠佇列溝通，所以沒有載入順序問題，離線時也不掉資料。 */
var FAS = (function () {
  var SID_KEY = "food_analysis_student_id";   // 與本站其他課程共用學號
  var QUEUE_KEY = "fas_queue", LOG_KEY = "fas_log", CLASS_KEY = "fas_class";
  var CONF = ["猜的", "有點把握", "很確定"];
  var sessionId = Date.now().toString(36) + Math.random().toString(36).slice(2, 8);

  function lsGet(k, d) { try { var v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } }
  function lsSet(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* 私密模式或已滿 */ } }
  function rawGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

  function chapter() {
    if (typeof CHAPTER !== "undefined") return CHAPTER;
    var m = (location.pathname.split("/").pop() || "").match(/^(ch\d+)/);
    return m ? m[1] : "index";
  }
  function classId() {
    var c = new URLSearchParams(location.search).get("class");
    if (c) { c = c.replace(/[^A-Za-z0-9_\-]/g, "").slice(0, 10); try { localStorage.setItem(CLASS_KEY, c); } catch (e) {} }
    return c || rawGet(CLASS_KEY) || "A";
  }
  function sid() { return rawGet(SID_KEY); }
  function isGuest() { try { return sessionStorage.getItem("fas_guest") === "1"; } catch (e) { return false; } }

  function emit(ev) {
    var s = sid();
    ev.chapter_id = chapter();
    ev.session_id = sessionId;
    ev.class_id = classId();
    ev.client_ts = new Date().toISOString();
    ev.student_id = s ? s.toUpperCase() : null;
    var log = lsGet(LOG_KEY, []); log.push(ev); if (log.length > 2000) log = log.slice(-2000); lsSet(LOG_KEY, log);
    if (s && !isGuest()) {
      var q = lsGet(QUEUE_KEY, []); q.push(ev); lsSet(QUEUE_KEY, q);
      window.dispatchEvent(new Event("fas-queue"));
    }
  }

  function exportCsv() {
    var cols = ["client_ts", "student_id", "chapter_id", "phase", "event_type", "question_id", "item_version", "qtype",
      "choice_idx", "choice_value", "is_correct", "misconception", "confidence", "attempts", "latency_ms",
      "final_score", "total", "free_text"];
    var rows = lsGet(LOG_KEY, []).map(function (e) {
      return cols.map(function (c) {
        var v = e[c]; if (v === undefined || v === null) v = "";
        return '"' + String(v).replace(/"/g, '""') + '"';
      }).join(",");
    });
    var blob = new Blob(["﻿" + cols.join(",") + "\n" + rows.join("\n")], { type: "text/csv;charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "fas_quiz_" + (sid() || "guest") + ".csv";
    a.click();
    URL.revokeObjectURL(a.href);
  }

  return { sid: sid, isGuest: isGuest, chapter: chapter, emit: emit, exportCsv: exportCsv,
    lsGet: lsGet, lsSet: lsSet, SID_KEY: SID_KEY, CONF: CONF };
})();

function normalizeQuiz(questions) {
  var ch = FAS.chapter();
  return questions.map(function (it, i) {
    var o = {}; for (var k in it) o[k] = it[k];
    if (!o.id) o.id = ch + "-q" + ("0" + (i + 1)).slice(-2);   // 尚未貼標籤的舊題：以位置暫代
    if (!o.v) o.v = 1;
    if (!o.phase) o.phase = "post";
    if (!o.type) o.type = o.num ? "calc" : "concept";
    return o;
  });
}

/* 學號閘門：同頁多個測驗共用，狀態改變時全部重畫 */
var fasGates = [];
function refreshGates() { fasGates.forEach(function (fn) { fn(); }); }

function renderGate(box, body) {
  var gate = document.createElement("div");
  gate.className = "qgate";
  box.insertBefore(gate, body);
  function draw() {
    var s = FAS.sid(), guest = FAS.isGuest();
    if (s || guest) {
      gate.innerHTML = '<span class="qwho">' + (s && !guest ? "🎓 " + s.toUpperCase() : "👤 訪客練習（不記錄）") +
        '</span> <button type="button" class="qlink act-change">' + (s && !guest ? "更換學號" : "改用學號作答") + "</button>";
      gate.querySelector(".act-change").addEventListener("click", function () {
        try { localStorage.removeItem(FAS.SID_KEY); sessionStorage.removeItem("fas_guest"); } catch (e) {}
        refreshGates();
      });
      body.hidden = false;
    } else {
      gate.innerHTML =
        '<label class="qgate-l">請先輸入學號再作答 <input type="text" class="qsid" maxlength="20" autocomplete="off" placeholder="例如 B11234567"></label>' +
        '<button type="button" class="qbtn act-go">開始作答</button> ' +
        '<button type="button" class="qlink act-guest">我不是修課學生，訪客練習</button>' +
        '<div class="qgate-err" role="alert"></div>' +
        '<p class="qnote">學號與作答只提供授課教師了解全班學習成效、調整教學，不會公開，也不影響成績以外的用途。只有<strong>第一次作答</strong>會列入學習成效分析，請先自己想過再作答。</p>';
      var inp = gate.querySelector(".qsid"), err = gate.querySelector(".qgate-err");
      function go() {
        var v = inp.value.trim();
        if (!/^[A-Za-z0-9_\-]{1,20}$/.test(v)) { err.textContent = "學號只能是英文、數字、底線或連字號，1–20 字。"; return; }
        try { localStorage.setItem(FAS.SID_KEY, v); } catch (e) {}
        refreshGates();
      }
      gate.querySelector(".act-go").addEventListener("click", go);
      inp.addEventListener("keydown", function (e) { if (e.key === "Enter") go(); });
      gate.querySelector(".act-guest").addEventListener("click", function () {
        try { sessionStorage.setItem("fas_guest", "1"); } catch (e) {}
        refreshGates();
      });
      body.hidden = true;
    }
  }
  fasGates.push(draw);
  draw();
}

/* opts（選填）：同一頁有第二組題目時用，例如 ch11 的期末總測驗
     renderQuiz(el, FINALEXAM, { set: "final", title: "🎓 期末總測驗", intro: "…", muddy: false }) */
function renderQuiz(container, allQuestions, opts) {
  opts = opts || {};
  var set = opts.set || "main";
  if (opts.set) allQuestions = normalizeQuiz(allQuestions);
  var phase = container.dataset.phase === "pre" ? "pre" : "post";
  var questions = allQuestions.filter(function (it) {
    return phase === "pre" ? it.phase === "pre" : it.phase !== "pre";
  });
  if (!questions.length) return;
  var ch = FAS.chapter();
  var t0 = null;                       // 第一次互動的時間，用來算每題作答延遲
  var attemptNo = 0, warned = false, graded = false;

  var box = document.createElement("div");
  box.className = "quizbox" + (phase === "pre" ? " quizpre" : "");
  box.innerHTML = phase === "pre"
    ? "<h2>🧪 課前 3 題</h2><p>還沒學沒關係，憑直覺作答即可。作答後不顯示答案——學完本章做章末測驗，就能看到自己的進步。</p>"
    : "<h2>" + (opts.title || "📝 章末複習測驗") + "</h2><p>" +
      (opts.intro || "每題請順手點一下「把握程度」。作答後按「批改」，每題都會顯示詳解。") + "</p>";
  var body = document.createElement("div");
  box.appendChild(body);

  var spacedShown = false;
  questions.forEach(function (item, qi) {
    if (item.phase === "spaced" && !spacedShown) {
      spacedShown = true;
      var hd = document.createElement("h3");
      hd.className = "qspaced";
      hd.textContent = "🔁 回溯題：還記得前面章節嗎？";
      body.appendChild(hd);
    }
    var div = document.createElement("div");
    div.className = "qitem";
    div.setAttribute("role", "group");
    div.setAttribute("aria-labelledby", item.id + "-t");
    var name = set + "-" + phase + "-" + qi;
    var html = '<div class="qtext" id="' + item.id + '-t">Q' + (qi + 1) + ". " + item.q + "</div>";
    if (item.num) {
      html += '<label class="qnum">你的答案：<input type="text" inputmode="decimal" class="qnum-in" autocomplete="off"> ' +
        (item.num.unit || "") + "</label>";
    } else {
      item.opts.forEach(function (opt, oi) {
        html += '<label><input type="radio" name="' + name + '" value="' + oi + '">' + opt + "</label>";
      });
    }
    html += '<div class="qconf" role="radiogroup" aria-label="把握程度"><span>把握程度：</span>';
    FAS.CONF.forEach(function (c, ci) {
      html += '<label><input type="radio" name="' + name + '-c" value="' + (ci + 1) + '">' + c + "</label>";
    });
    html += "</div>";
    if (phase !== "pre") html += '<div class="exp">💡 ' + item.exp + "</div>";
    div.innerHTML = html;
    div.addEventListener("input", function () {
      var now = Date.now();
      if (t0 === null) t0 = now;
      div.dataset.last = now;
    });
    body.appendChild(div);
  });

  var btn = document.createElement("button");
  btn.type = "button";
  btn.className = "qbtn";
  btn.textContent = phase === "pre" ? "送出前測" : "批改答案";
  var note = document.createElement("div");
  note.className = "qwarn";
  note.setAttribute("role", "status");
  var score = document.createElement("div");
  score.className = "qscore";
  score.setAttribute("role", "status");

  function readItem(div, item) {
    var r = { answered: false, correct: false, choice_idx: null, choice_value: null, tag: null };
    if (item.num) {
      var raw = div.querySelector(".qnum-in").value.trim().replace(/,/g, "");
      if (raw !== "" && !isNaN(parseFloat(raw))) {
        var x = parseFloat(raw);
        r.answered = true; r.choice_value = x;
        r.correct = Math.abs(x - item.num.ans) <= item.num.tol + 1e-12;
        if (!r.correct) {
          r.tag = "OTHER_NUM";
          (item.errs || []).forEach(function (e) { if (Math.abs(x - e.val) <= e.tol + 1e-12) r.tag = e.tag; });
        }
      }
    } else {
      var sel = div.querySelector('input[type=radio]:not([name$="-c"]):checked');
      if (sel) {
        r.answered = true; r.choice_idx = +sel.value;
        r.correct = r.choice_idx === item.ans;
        if (!r.correct) r.tag = (item.tags && item.tags[r.choice_idx]) || null;
      }
    }
    var c = div.querySelector('input[name$="-c"]:checked');
    r.confidence = c ? +c.value : null;
    return r;
  }

  function grade() {
    var divs = body.querySelectorAll(".qitem");
    var results = questions.map(function (item, qi) { return readItem(divs[qi], item); });
    var noConf = results.filter(function (r) { return r.answered && r.confidence === null; }).length;
    if (noConf && !warned) {
      warned = true;
      note.textContent = "還有 " + noConf + " 題沒選「把握程度」。選一下能幫老師知道大家哪裡不確定；不想選的話，再按一次按鈕即可。";
      return;
    }
    note.textContent = "";
    var attKey = "fas_att:" + (FAS.sid() || "guest") + ":" + ch + ":" + phase + (opts.set ? ":" + set : "");
    attemptNo = FAS.lsGet(attKey, 0) + 1;
    FAS.lsSet(attKey, attemptNo);
    var correct = 0, unanswered = 0, tEnd = Date.now();
    results.forEach(function (r, qi) {
      var item = questions[qi], div = divs[qi];
      if (r.correct) correct++;
      if (!r.answered) unanswered++;
      FAS.emit({
        event_type: "answer", quiz_set: set, phase: item.phase, question_id: item.id, item_version: item.v, qtype: item.type,
        from: item.from || null, is_correct: r.correct, skipped: !r.answered,
        choice_idx: r.choice_idx, choice_value: r.choice_value, misconception: r.tag,
        confidence: r.confidence, attempts: attemptNo,
        latency_ms: t0 !== null && div.dataset.last ? (+div.dataset.last - t0) : null
      });
      div.querySelectorAll("input").forEach(function (i) { i.disabled = true; });
      if (phase === "pre") return;
      div.classList.add("answered", r.correct ? "correct" : "wrong");
      if (!item.num) {
        var labels = div.querySelectorAll("label:not(.qnum)");
        if (r.choice_idx !== null) labels[r.choice_idx].classList.add("sel");
        labels[item.ans].classList.add("sel", "key");
      } else {
        var k = document.createElement("div");
        k.className = "qkey";
        k.textContent = "正確答案：" + item.num.ans + (item.num.unit ? " " + item.num.unit : "") + "（容許 ±" + item.num.tol + "）";
        div.insertBefore(k, div.querySelector(".exp"));
      }
    });
    var n = questions.length;
    FAS.emit({
      event_type: "attempt_complete", quiz_set: set, phase: phase, question_id: null, final_score: correct, total: n,
      answered: n - unanswered, attempts: attemptNo, duration_ms: t0 !== null ? tEnd - t0 : null
    });
    graded = true;
    if (phase === "pre") {
      if (FAS.sid() && !FAS.isGuest()) FAS.lsSet("fas_pre:" + FAS.sid() + ":" + ch, { score: correct, total: n });
      btn.hidden = true;
      score.className = "qscore mid";
      score.textContent = "✅ 前測已記錄。現在開始讀本章，章末見！";
      return;
    }
    var pct = Math.round((correct / n) * 100);
    var pre = FAS.sid() && !opts.set ? FAS.lsGet("fas_pre:" + FAS.sid() + ":" + ch, null) : null;
    score.textContent = "得分：" + correct + " / " + n +
      (unanswered ? "（有 " + unanswered + " 題未作答）" : "") +
      (pre && attemptNo === 1 ? "　｜　課前 " + pre.score + "/" + pre.total + " → 課後 " + correct + "/" + n : "") +
      "　" + (pct >= 80 ? "🎉 太棒了，觀念很清楚！" :
              pct >= 60 ? "👍 不錯，再複習答錯的部分。" :
                          "💪 別氣餒，回到內文重讀一次再挑戰！");
    score.className = "qscore " + (pct >= 80 ? "good" : pct >= 60 ? "mid" : "low");
    btn.textContent = "再練一次（不列入成效）";
  }

  function reset() {
    body.querySelectorAll(".qitem").forEach(function (div) {
      div.classList.remove("answered", "correct", "wrong");
      delete div.dataset.last;
      div.querySelectorAll("label").forEach(function (l) { l.classList.remove("sel", "key"); });
      div.querySelectorAll("input").forEach(function (i) {
        i.disabled = false;
        if (i.type === "radio") i.checked = false; else i.value = "";
      });
      var k = div.querySelector(".qkey"); if (k) k.remove();
    });
    graded = false; warned = false; t0 = null;
    score.textContent = ""; score.className = "qscore";
    btn.textContent = "批改答案";
    box.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  btn.addEventListener("click", function () { if (graded) reset(); else grade(); });
  body.appendChild(note);
  body.appendChild(btn);
  body.appendChild(score);

  if (phase === "post" && opts.muddy !== false) {
    var muddy = document.createElement("div");
    muddy.className = "qmuddy";
    muddy.innerHTML =
      '<label for="' + ch + '-muddy"><strong>🤔 這一章我還不懂的地方</strong>（選填，200 字內；老師下次上課會優先講最多人卡住的點）</label>' +
      '<textarea id="' + ch + '-muddy" maxlength="200" rows="3" placeholder="例如：不懂為什麼 n 很小的時候要用 t 而不是 Z"></textarea>' +
      '<button type="button" class="qbtn ghost act-muddy">送出給老師</button> <span class="qmuddy-msg" role="status"></span>';
    body.appendChild(muddy);
    muddy.querySelector(".act-muddy").addEventListener("click", function () {
      var ta = muddy.querySelector("textarea"), msg = muddy.querySelector(".qmuddy-msg");
      var text = ta.value.trim();
      if (!text) { msg.textContent = "還沒寫內容喔。"; return; }
      FAS.emit({ event_type: "self_check", phase: "post", question_id: ch + "-muddy", free_text: text.slice(0, 200) });
      ta.value = "";
      msg.textContent = FAS.isGuest() || !FAS.sid() ? "訪客模式不會上傳；已存在本機紀錄。" : "✓ 已送出，謝謝！";
    });
    var foot = document.createElement("div");
    foot.className = "qfoot";
    foot.innerHTML = '<button type="button" class="qlink act-csv">⬇ 匯出我在本站的作答紀錄 (CSV)</button> <span class="qsync" data-fas-sync></span>';
    foot.querySelector(".act-csv").addEventListener("click", FAS.exportCsv);
    body.appendChild(foot);
  }

  container.appendChild(box);
  renderGate(box, body);

  // 前測每人每章只做一次；換學號時重新判斷
  if (phase === "pre") {
    var preLock = function () {
      if (graded) return;
      var done = !!(FAS.sid() && !FAS.isGuest() && FAS.lsGet("fas_pre:" + FAS.sid() + ":" + ch, null));
      body.querySelectorAll(".qitem input").forEach(function (i) { i.disabled = done; });
      btn.hidden = done;
      score.className = done ? "qscore mid" : "qscore";
      score.textContent = done ? "✅ 你已完成本章前測。" : "";
    };
    fasGates.push(preLock);
    preLock();
  }
}

if (typeof QUIZ !== "undefined" && QUIZ.length) {
  (function () {
    var all = normalizeQuiz(QUIZ);
    document.querySelectorAll(".quiz").forEach(function (el) { renderQuiz(el, all); });
  })();
}

/* ---------- 3. 導覽列與上下章：單一來源 ----------
   新增章節只要改這個陣列（順序＝建議教學順序，不是檔名順序）。
   檔名是穩定 ID（也是學習紀錄的鍵），不要為了排序去改檔名。 */
var FAS_NAV = [
  { href: "index.html", nav: "首頁" },
  { href: "ch00.html", nav: "Ch0 入門", title: "Ch0 課程導覽與入門" },
  { href: "ch01.html", nav: "Ch1 統計入門", title: "Ch1 統計入門" },
  { href: "ch02.html", nav: "Ch2 常態與CI", title: "Ch2 常態分配與信賴區間" },
  { href: "ch03.html", nav: "Ch3 LOD與QC", title: "Ch3 LOD、LOQ 與品質管制圖" },
  { href: "ch04.html", nav: "Ch4 迴歸", title: "Ch4 標準曲線與迴歸" },
  { href: "ch05.html", nav: "Ch5 有效數字", title: "Ch5 有效數字與異常值" },
  { href: "ch15.html", nav: "Ch15 假說檢定", title: "Ch15 假說檢定與 t／F 檢定" },
  { href: "ch16.html", nav: "Ch16 ANOVA", title: "Ch16 單因子變異數分析 ANOVA" },
  { href: "ch06.html", nav: "Ch6 不確定度概念", title: "Ch6 量測不確定度概念" },
  { href: "ch07.html", nav: "Ch7 分布與天平", title: "Ch7 Type A/B 與天平案例" },
  { href: "ch08.html", nav: "Ch8 合成報告", title: "Ch8 合成、報告與符合性" },
  { href: "ch09.html", nav: "Ch9 模擬法", title: "Ch9 Kragten 與 Monte Carlo" },
  { href: "ch10.html", nav: "Ch10 滴定與HPLC", title: "Ch10 實戰案例：滴定與 HPLC" },
  { href: "ch11.html", nav: "Ch11 總複習", title: "Ch11 綜合案例與期末測驗" },
  { href: "ch12.html", nav: "Ch12 LC-MS/MS", title: "Ch12 LC-MS/MS 進階案例" },
  { href: "ch13.html", nav: "Ch13 FDC配方", title: "Ch13 FDC 與配方計算" },
  { href: "ch17.html", nav: "Ch17 ANOVA進階", title: "Ch17 雙因子、精密度分解與失擬" },
  { href: "ch14.html", nav: "Ch14 DOE/RSM", title: "Ch14 實驗設計與反應曲面法" }
];
function fasBuildNav() {
  var page = location.pathname.split("/").pop() || "index.html";
  var idx = -1;
  FAS_NAV.forEach(function (n, i) { if (n.href === page) idx = i; });

  var nav = document.querySelector(".topnav");
  if (nav) {
    nav.innerHTML = FAS_NAV.map(function (n) {
      return '<a href="' + n.href + '"' + (n.href === page ? ' class="active" aria-current="page"' : "") + ">" + n.nav + "</a>";
    }).join("");
    nav.id = nav.id || "topnav";
    var tog = document.createElement("button");   // 手機版收合
    tog.type = "button";
    tog.className = "navtoggle";
    tog.setAttribute("aria-expanded", "false");
    tog.setAttribute("aria-controls", nav.id);
    tog.textContent = "☰ 章節";
    tog.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      tog.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.parentNode.insertBefore(tog, nav);
  }

  var pager = document.querySelector(".pager");
  if (pager && idx > 0) {                        // 首頁的 pager 維持手寫
    var prev = FAS_NAV[idx - 1], next = FAS_NAV[idx + 1];
    pager.innerHTML =
      '<a href="' + prev.href + '"><small>' + (idx === 1 ? "返回" : "上一章") + "</small>" +
        (idx === 1 ? "課程首頁" : "← " + prev.title) + "</a>" +
      (next ? '<a href="' + next.href + '"><small>下一章</small>' + next.title + " →</a>"
            : '<a href="index.html"><small>返回</small>課程首頁</a>');
  }
}
// 既有章節的 pager 寫在 <script> 之後，所以等 DOM 解析完才產生
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fasBuildNav);
else fasBuildNav();
