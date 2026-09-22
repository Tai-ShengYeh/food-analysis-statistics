/* ==================================================================
   games.js — 章內互動小遊戲（猜猜看再揭曉 / 模擬器）
   依賴：assets/app.js（FAS.emit、FAS.sid、FAS.isGuest、FAS.lsGet/lsSet）
   用法：章內放 <div class="game" data-game="ch16-predict"></div>，
         本檔的 GAMES 登錄表依 id 渲染；遊戲定義集中在這裡，章節 html 只放佔位。
   事件：與測驗同一條 Firestore 管線（fas_queue → assess.js），但
         game = "fas_game"、quiz_set = "game"、phase = "game"、另帶 game_id，
         讓 scripts/quiz_dashboard.py 能與 fas_quiz 分流，不汙染答對率統計。
         每題預測 → answer；按下揭曉 → reveal；整局結束 → attempt_complete。
   設計原則：不需學號也能玩（降低門檻）；有學號且非訪客時事件才會上傳。
   ================================================================== */
(function () {
  if (typeof FAS === "undefined") { console.warn("[games] 找不到 FAS，請先載入 assets/app.js"); return; }
  var GAMES = {};
  var GAME = "fas_game";

  /* ---------------- 共用工具 ---------------- */
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  var SVG_NS = "http://www.w3.org/2000/svg";
  function svg(tag, attrs, text) {
    var e = document.createElementNS(SVG_NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function fmt(x, d) { return Number(x).toFixed(d); }
  function whoText() {
    var s = FAS.sid(), g = FAS.isGuest();
    return s && !g ? "🎓 " + s + "：你的猜測會和章末測驗一起讓老師看到全班的分布（只有第一次算），放心大膽猜。"
                   : "👤 尚未輸入學號（或訪客模式）：猜測只存在這台裝置，不會上傳。";
  }
  function attKey(gid) { return "fas_game_att:" + (FAS.sid() || "anon") + ":" + gid; }

  /* ---------------- 猜猜看再揭曉：共用流程 ----------------
     spec = { gid, title, intro, questions:[...], reveal(panelEl, results), revealLabel }
     question 三種型態：
       { id, q, opts, ans, tags, exp }                     單選
       { id, q, opts, ans:[i,j], multi:true, tagFn, exp }  複選（tagFn(選到的索引陣列) → 迷思 key 或 null）
       { id, q, num:{lo,hi,okLo,okHi,unit,placeholder}, tagFn, exp }  數值填空
       { id, q, mount(div) → { read(), showKey(r), reset() }, exp }   自訂互動（點圖、選點等）
         read() 回傳 { answered, correct, idx, value, tag }；showKey 在批改後顯示解答並鎖定；reset 還原
  */
  function predictGame(box, spec) {
    var wrap = el("div", "gamebox");
    var head = el("div", "gamehead");
    head.appendChild(el("span", "badge game", "🎮 " + (spec.badge || "猜猜看再揭曉")));
    head.appendChild(el("h3", null, spec.title));
    var who = el("div", "gwho", whoText());
    head.appendChild(who);
    wrap.appendChild(head);
    if (spec.intro) wrap.appendChild(el("div", "gintro", spec.intro));

    var items = [], ctrls = [];
    var stepWord = spec.stepWord || "預測";
    spec.questions.forEach(function (q, qi) {
      var div = el("div", "qitem");
      div.appendChild(el("div", "qtext", stepWord + " " + (qi + 1) + "／" + spec.questions.length + "　" + q.q));
      if (q.mount) {
        ctrls[qi] = q.mount(div);
      } else if (q.num) {
        var lab = el("label", "qnum");
        var inp = document.createElement("input");
        inp.type = "number"; inp.className = "qnum-in"; inp.step = q.num.step || 1;
        inp.min = q.num.lo; inp.max = q.num.hi; inp.placeholder = q.num.placeholder || "";
        inp.setAttribute("inputmode", "numeric");
        lab.appendChild(inp);
        if (q.num.unit) lab.appendChild(document.createTextNode(" " + q.num.unit));
        div.appendChild(lab);
      } else {
        q.opts.forEach(function (o, oi) {
          var lab = document.createElement("label");
          var inp = document.createElement("input");
          inp.type = q.multi ? "checkbox" : "radio";
          inp.name = spec.gid + "-" + q.id; inp.value = oi;
          lab.appendChild(inp);
          lab.appendChild(el("span", null, " " + o));   // 選項文字由本檔撰寫，可含 <sub> 等 HTML
          div.appendChild(lab);
        });
      }
      var ex = el("div", "exp", q.exp);
      div.appendChild(ex);
      wrap.appendChild(div);
      items.push(div);
    });

    var warn = el("div", "qwarn");
    var row = el("div", "gbtn-row");
    var btn = el("button", "qbtn", spec.revealLabel || "送出預測並揭曉");
    btn.type = "button";
    row.appendChild(btn);
    var score = el("div", "qscore");
    var panel = el("div", "gpanel");
    panel.hidden = true;
    wrap.appendChild(warn); wrap.appendChild(row); wrap.appendChild(score); wrap.appendChild(panel);
    box.appendChild(wrap);

    var graded = false, warned = false, t0 = null;
    ["input", "click"].forEach(function (evn) { wrap.addEventListener(evn, function () { if (t0 === null) t0 = Date.now(); }); });   // 點圖類互動沒有 input 事件

    function readItem(div, q, qi) {
      var r = { answered: false, correct: false, idx: null, value: null, tag: null };
      if (q.mount) {
        var c0 = ctrls[qi].read();
        for (var k in c0) r[k] = c0[k];
      } else if (q.num) {
        var v = div.querySelector("input").value.trim();
        if (v === "") return r;
        var x = parseFloat(v);
        if (isNaN(x)) return r;
        r.answered = true; r.value = x;
        r.correct = x >= q.num.okLo && x <= q.num.okHi;
        if (!r.correct && q.tagFn) r.tag = q.tagFn(x);
      } else if (q.multi) {
        var sel = [];
        div.querySelectorAll("input").forEach(function (i, oi) { if (i.checked) sel.push(oi); });
        if (!sel.length) return r;
        r.answered = true;
        r.value = q.opts.map(function (_, oi) { return sel.indexOf(oi) >= 0 ? "1" : "0"; }).join("");
        r.correct = sel.length === q.ans.length && q.ans.every(function (a) { return sel.indexOf(a) >= 0; });
        if (!r.correct && q.tagFn) r.tag = q.tagFn(sel);
      } else {
        var c = div.querySelector("input:checked");
        if (!c) return r;
        r.answered = true; r.idx = parseInt(c.value, 10);
        r.correct = r.idx === q.ans;
        if (!r.correct && q.tags) r.tag = q.tags[r.idx] || null;
      }
      return r;
    }

    function grade() {
      var results = spec.questions.map(function (q, qi) { return readItem(items[qi], q, qi); });
      var nAns = results.filter(function (r) { return r.answered; }).length;
      if (nAns < results.length && !warned) {
        warned = true;
        warn.textContent = "還有 " + (results.length - nAns) + " 題沒作答。答錯不扣分，先想再揭曉學得最多；確定要跳過就再按一次。";
        return;
      }
      warn.textContent = "";
      var attempts = (FAS.lsGet(attKey(spec.gid), 0) || 0) + 1;
      if (spec.beforeGrade) spec.beforeGrade(results);
      FAS.lsSet(attKey(spec.gid), attempts);
      var tEnd = Date.now(), correct = 0;
      results.forEach(function (r, qi) {
        var q = spec.questions[qi], div = items[qi];
        if (r.correct) correct++;
        div.classList.add("answered", r.correct ? "correct" : "wrong");
        var labels = div.querySelectorAll("label:not(.qnum)");
        if (q.mount) {
          ctrls[qi].showKey(r);
        } else if (q.num) {
          var k = el("div", "qkey", "實際約 " + q.num.keyText);
          div.insertBefore(k, div.querySelector(".exp"));
        } else if (q.multi) {
          labels.forEach(function (l, oi) {
            if (l.querySelector("input").checked) l.classList.add("sel");
            if (q.ans.indexOf(oi) >= 0) l.classList.add("key");
          });
        } else {
          if (r.idx !== null) labels[r.idx].classList.add("sel");
          labels[q.ans].classList.add("key");
        }
        div.querySelectorAll("input").forEach(function (i) { i.disabled = true; });
        FAS.emit({
          event_type: "answer", game: GAME, game_id: spec.gid, quiz_set: "game", phase: "game",
          qtype: q.mount ? "interact" : "predict",
          question_id: q.id, item_version: q.v || 1,
          is_correct: r.answered ? r.correct : null, skipped: !r.answered,
          choice_idx: r.idx, choice_value: r.value, misconception: r.tag, attempts: attempts,
          latency_ms: t0 !== null ? tEnd - t0 : null
        });
      });
      FAS.emit({ event_type: "reveal", game: GAME, game_id: spec.gid, quiz_set: "game", phase: "game", question_id: null, attempts: attempts });
      FAS.emit({
        event_type: "attempt_complete", game: GAME, game_id: spec.gid, quiz_set: "game", phase: "game", question_id: null,
        final_score: correct, total: results.length, answered: nAns, attempts: attempts,
        duration_ms: t0 !== null ? tEnd - t0 : null
      });
      var n = results.length;
      score.textContent = (spec.scoreWord || "猜對") + " " + correct + " / " + n + "　" +
        (correct === n ? "🎯 全中！你的統計直覺很準。" : correct >= n / 2 ? "👍 不錯，看看猜錯的那題為什麼。" : "🔍 沒關係，猜錯正是學會的開始——往下看揭曉。");
      score.className = "qscore " + (correct === n ? "good" : correct >= n / 2 ? "mid" : "low");
      panel.innerHTML = "";
      spec.reveal(panel, results);
      panel.hidden = false;
      graded = true;
      btn.textContent = "再猜一次（不列入成效）";
      panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    function reset() {
      items.forEach(function (div, qi) {
        div.classList.remove("answered", "correct", "wrong");
        if (ctrls[qi]) ctrls[qi].reset();
        div.querySelectorAll("label").forEach(function (l) { l.classList.remove("sel", "key"); });
        div.querySelectorAll("input").forEach(function (i) {
          i.disabled = false;
          if (i.type === "radio" || i.type === "checkbox") i.checked = false; else i.value = "";
        });
        var k = div.querySelector(".qkey"); if (k) k.remove();
      });
      graded = false; warned = false; t0 = null;
      score.textContent = ""; score.className = "qscore"; warn.textContent = "";
      panel.hidden = true; panel.innerHTML = "";
      btn.textContent = spec.revealLabel || "送出預測並揭曉";
      wrap.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    btn.addEventListener("click", function () { if (graded) reset(); else grade(); });
    if (typeof fasGates !== "undefined") fasGates.push(function () { who.textContent = whoText(); });
  }

  /* ==================================================================
     Ch16：三種溶劑的總多酚 — 先猜 p、F、哪幾對不同，再揭曉 aov() 與 Tukey
     數字來自本頁 16.4／16.5 節的 R 輸出（Rscript 實跑）。
     ================================================================== */
  GAMES["ch16-predict"] = function (box) {
    var F_OBS = 42.26, F_CRIT = 3.885, P_OBS = "3.69 × 10⁻⁶";
    var guessF = [1, 5, 40, 400];
    predictGame(box, {
      gid: "ch16-predict",
      title: "三種溶劑真的有差嗎？先下注，再跑 ANOVA",
      intro: "上面的表格和圖 16-1 你都看過了：甲醇 12.56、乙醇 12.98、丙酮 15.08（mg GAE/g），組內 SD 都在 0.45 左右。" +
             "在看到 R 輸出之前，先憑直覺回答三個問題——這是統計學家在按 Enter 之前都會做的事。",
      questions: [
        { id: "ch16-g01-1", v: 1,
          q: "整體 ANOVA（H<sub>0</sub>：三組母體平均全部相等）的 p 值會落在哪一區？",
          opts: ["p > 0.05：資料有重疊，沒有顯著差異", "0.01 < p ≤ 0.05：勉強顯著", "0.001 < p ≤ 0.01：相當顯著", "p ≤ 0.001：非常顯著"],
          ans: 3, tags: [null, null, null, null],
          exp: "實際 p = " + P_OBS + "。丙酮比另兩組高出約 2.5，而組內 SD 只有約 0.45——差距是雜訊的 5 倍以上，只要有一組明顯脫隊，整體 F 就會很大、p 就會很小。" +
               "但請記住：p 很小只說「<strong>至少有一組</strong>不同」，不代表三組彼此都不同（見預測 3）。" },
        { id: "ch16-g01-2", v: 1,
          q: "F 值 = 組間均方 ÷ 組內均方。H<sub>0</sub> 為真時 F 平均約等於 1。你猜本例的 F 大約是？",
          opts: ["約 1（和 H<sub>0</sub> 為真時差不多）", "約 5（剛超過臨界值）", "約 40", "約 400"],
          ans: 2, tags: [null, null, null, null],
          exp: "F = 9.114 ÷ 0.216 = <strong>42.26</strong>。F(2, 12) 在 α = 0.05 的臨界值是 3.89，觀測值是臨界值的 10 倍以上。" +
               "F 約 1 才是「沒差」的長相；約 400 則要組間差距再大 3 倍、或雜訊再小 3 倍才會出現。" },
        { id: "ch16-g01-3", v: 1, multi: true,
          q: "Tukey 事後比較會判定哪幾對溶劑「有」顯著差異？（可複選）",
          opts: ["乙醇 vs 甲醇", "丙酮 vs 甲醇", "丙酮 vs 乙醇"],
          ans: [1, 2],
          tagFn: function (sel) { return sel.length === 3 ? "ANOVA_SIG_ALL_DIFFER" : null; },
          exp: "乙醇 − 甲醇 = 0.42，95% 信賴區間 −0.36 ~ 1.20 <strong>含 0</strong>，p adj = 0.36 → 不顯著；丙酮對另兩者 p adj 都 < 0.0001。" +
               "所以字母標示是丙酮 <b>a</b>、乙醇 <b>b</b>、甲醇 <b>b</b>。ANOVA 顯著 ≠ 每一對都不同——這是 16.5 節要處理的事。" }
      ],
      reveal: function (panel, results) {
        panel.appendChild(el("h4", null, "揭曉：R 怎麼說"));
        panel.appendChild(el("div", "gtablewrap",
          '<table class="gtable"><thead><tr><th></th><th class="num">Df</th><th class="num">Sum Sq</th><th class="num">Mean Sq</th><th class="num">F value</th><th class="num">Pr(&gt;F)</th></tr></thead>' +
          '<tbody><tr class="hl"><td>solvent（組間）</td><td class="num">2</td><td class="num">18.228</td><td class="num">9.114</td><td class="num"><strong>42.26</strong></td><td class="num"><strong>3.69e-06</strong> ***</td></tr>' +
          '<tr><td>Residuals（組內）</td><td class="num">12</td><td class="num">2.588</td><td class="num">0.216</td><td></td><td></td></tr></tbody></table>'));

        // F 值尺：H0 期望 1、臨界值 3.89、觀測 42.26、你的猜測
        var W = 640, H = 120, x0 = 40, x1 = 600, maxF = 60;
        function X(f) { return x0 + Math.min(f, maxF) / maxF * (x1 - x0); }
        var s = svg("svg", { viewBox: "0 0 " + W + " " + H, class: "gsvg", role: "img", "aria-label": "F 值尺：H0 期望值 1、臨界值 3.89、觀測值 42.26 與你的猜測" });
        s.appendChild(svg("line", { x1: x0, y1: 70, x2: x1, y2: 70, stroke: "#64748B", "stroke-width": 2 }));
        [0, 10, 20, 30, 40, 50, 60].forEach(function (t) {
          s.appendChild(svg("line", { x1: X(t), y1: 70, x2: X(t), y2: 76, stroke: "#64748B" }));
          s.appendChild(svg("text", { x: X(t), y: 92, "text-anchor": "middle", "font-size": 12, fill: "#64748B" }, String(t)));
        });
        s.appendChild(svg("text", { x: x1 + 6, y: 74, "font-size": 12, fill: "#64748B" }, "F"));
        // 接受區（F < 臨界值）淡灰底
        s.appendChild(svg("rect", { x: x0, y: 40, width: X(F_CRIT) - x0, height: 30, fill: "#E2E8F0" }));
        s.appendChild(svg("line", { x1: X(1), y1: 40, x2: X(1), y2: 70, stroke: "#64748B", "stroke-width": 2 }));
        s.appendChild(svg("text", { x: X(1), y: 32, "text-anchor": "start", "font-size": 12, fill: "#64748B" }, "H₀ 為真時 F≈1"));
        s.appendChild(svg("line", { x1: X(F_CRIT), y1: 40, x2: X(F_CRIT), y2: 70, stroke: "#C62828", "stroke-width": 2, "stroke-dasharray": "4 3" }));
        s.appendChild(svg("text", { x: X(F_CRIT) + 4, y: 58, "font-size": 12, fill: "#C62828" }, "臨界值 3.89（α=0.05）"));
        s.appendChild(svg("line", { x1: X(F_OBS), y1: 36, x2: X(F_OBS), y2: 70, stroke: "#2E7D32", "stroke-width": 4 }));
        s.appendChild(svg("text", { x: X(F_OBS), y: 28, "text-anchor": "middle", "font-size": 13, "font-weight": 700, fill: "#2E7D32" }, "觀測 F = 42.26"));
        var r2 = results[1];
        if (r2.idx !== null) {
          var g = guessF[r2.idx], gx = g > maxF ? x1 + 2 : X(g);
          s.appendChild(svg("polygon", { points: (gx - 7) + ",108 " + (gx + 7) + ",108 " + gx + ",96", fill: "#F6A21D" }));
          s.appendChild(svg("text", { x: Math.min(gx, x1 - 30), y: 118, "text-anchor": "middle", "font-size": 12, fill: "#8A5A00" },
            "你猜：約 " + g + (g > maxF ? "（超出尺外 →）" : "")));
        }
        s.style.minWidth = "520px";                       // 手機上可左右捲動，文字不縮到看不見
        var sw = el("div", "gsvgwrap"); sw.appendChild(s); panel.appendChild(sw);
        panel.appendChild(el("p", "gverdict", "整體結論：p ≪ 0.05，拒絕 H₀——三種溶劑的總多酚平均<strong>不全相等</strong>。但哪幾對不同？要看事後比較："));
        panel.appendChild(el("div", "gtablewrap",
          '<table class="gtable"><thead><tr><th>Tukey HSD</th><th class="num">diff</th><th class="num">lwr</th><th class="num">upr</th><th class="num">p adj</th><th>判定</th></tr></thead><tbody>' +
          '<tr><td>Ethanol − Methanol</td><td class="num">0.42</td><td class="num">−0.36</td><td class="num">1.20</td><td class="num">0.357</td><td>區間含 0 → <strong>不顯著</strong></td></tr>' +
          '<tr class="hl"><td>Acetone − Methanol</td><td class="num">2.52</td><td class="num">1.74</td><td class="num">3.30</td><td class="num">0.0000051</td><td>顯著</td></tr>' +
          '<tr class="hl"><td>Acetone − Ethanol</td><td class="num">2.10</td><td class="num">1.32</td><td class="num">2.88</td><td class="num">0.0000322</td><td>顯著</td></tr>' +
          '</tbody></table>' +
          '<p>字母標示：丙酮 <b>15.08 a</b>、乙醇 <b>12.98 b</b>、甲醇 <b>12.56 b</b>（共用字母＝不顯著）。' +
          '接下來 16.2–16.5 節會告訴你這些數字是怎麼算出來的，以及為什麼不能直接做三次 t 檢定。</p>'));
      }
    });
  };

  /* ==================================================================
     Ch2：信賴區間抽樣模擬器 — 先猜 100 個 95% CI 有幾個漏掉真值，再自己抽
     母體：μ = 65.05%、σ = 0.293%（與 2.4 節 R 模擬相同）。
     t 分位數用 R 的 qt() 實算後寫死（Rscript 4.6.1，2026-09-22）。
     ================================================================== */
  GAMES["ch02-cisim"] = function (box) {
    var MU = 65.05, SIGMA = 0.293;
    var T = { // qt(1 - (1-level)/2, df = n-1)
      90: { 2: 6.3138, 3: 2.9200, 4: 2.3534, 5: 2.1318, 8: 1.8946, 16: 1.7531, 30: 1.6991 },
      95: { 2: 12.7062, 3: 4.3027, 4: 3.1824, 5: 2.7764, 8: 2.3646, 16: 2.1314, 30: 2.0452 },
      99: { 2: 63.6567, 3: 9.9248, 4: 5.8409, 5: 4.6041, 8: 3.4995, 16: 2.9467, 30: 2.7564 }
    };
    var Z = { 90: 1.6449, 95: 1.9600, 99: 2.5758 };
    var NS = [2, 3, 4, 5, 8, 16, 30];

    function randn() { // Box–Muller
      var u = 0, v = 0;
      while (u === 0) u = Math.random();
      while (v === 0) v = Math.random();
      return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
    }

    predictGame(box, {
      gid: "ch02-cisim",
      title: "100 個 95% 信賴區間，有幾個會漏掉真值？",
      intro: "上面 R 已經替你跑了 1000 次。現在換你：母體真值 μ = 65.05%、σ = 0.293%，每次抽 n = 4 個水分量測值、算一個 95% CI。" +
             "先猜，再親手抽樣驗證——把 n、信心水準、t／Z 切來切去，看看哪個猜測是對的。",
      questions: [
        { id: "ch02-g01-1", v: 1,
          q: "抽 100 次（每次 n = 4）、算 100 個 95% 信賴區間，你猜大約有幾個區間會<strong>漏掉</strong>真值 65.05%？",
          num: { lo: 0, hi: 100, okLo: 2, okHi: 10, unit: "個（0–100）", placeholder: "填整數", keyText: "5 個（100 × 5%；隨機起伏下 2~10 個都正常）" },
          tagFn: function (x) { return x === 0 ? "CI_TRUE_VALUE_PROB" : null; },
          exp: "「95%」描述的是<strong>方法的長期表現</strong>：100 個區間裡平均約 5 個會漏掉真值，模擬有隨機起伏，2~10 個都在合理範圍。" +
               "猜 0 個的同學常是把「95%」想成「這個區間一定對」；猜很多的同學則低估了這個方法——用模擬器多按幾次「抽 100 次」看看。" },
        { id: "ch02-g01-2", v: 1,
          q: "其他條件不變，n 從 4 增加到 16，CI 的寬度大約變成原來的？",
          opts: ["一樣寬：n 只影響平均值，不影響區間", "一半", "四分之一", "兩倍：數據越多、累積的誤差越大"],
          ans: 1, tags: ["SD_VS_SEM", null, "FORGOT_SQRT_N", "MORE_REPEATS_MORE_ERROR"],
          exp: "半寬 = t × SD ÷ √n。√16 ÷ √4 = 2，所以光看 √n 寬度就<strong>減半</strong>；t 值又從 3.18 降到 2.13，兩個效果相乘，實際約剩三分之一。" +
               "以為變四分之一是把 √n 想成 n；要再減半得做到 n = 64——報酬遞減。把模擬器的 n 切到 16 對照一下。" },
        { id: "ch02-g01-3", v: 1,
          q: "n = 4 卻硬用 Z = 1.96（而不是 t = 3.18）來算「95%」CI，長期的覆蓋率會是？",
          opts: ["還是 95%：Z 和 t 只是查表方式不同", "低於 95%", "高於 95%"],
          ans: 1, tags: ["USED_Z_NOT_T", null, null],
          exp: "用 R 算：P(|T<sub>3</sub>| < 1.96) = <strong>85.5%</strong>。小樣本的 SD 本身很不準，t 分布把這份額外的不確定度算進去；" +
               "用 Z 等於假裝 σ 已知，區間太窄、只有約 86% 蓋得到真值。在模擬器把方法切到「Z」就看得到。" }
      ],
      revealLabel: "送出預測，開始抽樣",
      reveal: function (panel) {
        panel.appendChild(el("h4", null, "抽樣模擬器：每一條橫線是一個信賴區間，紅色＝漏掉真值"));
        var ctrl = el("div", "gctrl");
        var selN = document.createElement("select");
        NS.forEach(function (n) { var o = document.createElement("option"); o.value = n; o.textContent = "n = " + n; if (n === 4) o.selected = true; selN.appendChild(o); });
        var selL = document.createElement("select");
        [90, 95, 99].forEach(function (l) { var o = document.createElement("option"); o.value = l; o.textContent = l + "% 信心"; if (l === 95) o.selected = true; selL.appendChild(o); });
        var labN = el("label", null, "每次抽 "); labN.appendChild(selN);
        var labL = el("label", null, "信心水準 "); labL.appendChild(selL);
        var mT = el("label"), mZ = el("label");
        var rT = document.createElement("input"), rZ = document.createElement("input");
        rT.type = rZ.type = "radio"; rT.name = rZ.name = "ch02-cisim-method"; rT.value = "t"; rZ.value = "z"; rT.checked = true;
        mT.appendChild(rT); mT.appendChild(document.createTextNode(" t 分布（正確）"));
        mZ.appendChild(rZ); mZ.appendChild(document.createTextNode(" 硬用 Z（假裝 σ 已知）"));
        ctrl.appendChild(labN); ctrl.appendChild(labL); ctrl.appendChild(mT); ctrl.appendChild(mZ);
        panel.appendChild(ctrl);

        var row = el("div", "gbtn-row");
        var b1 = el("button", "qbtn ghost", "抽 1 次"), b100 = el("button", "qbtn", "抽 100 次"), bR = el("button", "qbtn ghost", "重來");
        b1.type = b100.type = bR.type = "button";
        row.appendChild(b1); row.appendChild(b100); row.appendChild(bR);
        panel.appendChild(row);

        var stats = el("div", "gstats");
        panel.appendChild(stats);

        var W = 640, H = 330, x0 = 30, x1 = 610, top = 24, bottom = 306, ROWS = 100;
        var lo = MU - 1.0, hi = MU + 1.0;
        function X(v) { return x0 + (Math.min(Math.max(v, lo), hi) - lo) / (hi - lo) * (x1 - x0); }
        var s = svg("svg", { viewBox: "0 0 " + W + " " + H, class: "gsvg", role: "img", "aria-label": "信賴區間抽樣模擬圖" });
        var gLines = svg("g", {});
        s.appendChild(gLines);
        s.appendChild(svg("line", { x1: X(MU), y1: top - 8, x2: X(MU), y2: bottom + 4, stroke: "#0F4C81", "stroke-width": 2, "stroke-dasharray": "5 3" }));
        s.appendChild(svg("text", { x: X(MU), y: 12, "text-anchor": "middle", "font-size": 12, fill: "#0F4C81", "font-weight": 700 }, "真值 μ = 65.05%"));
        s.appendChild(svg("line", { x1: x0, y1: bottom + 6, x2: x1, y2: bottom + 6, stroke: "#64748B" }));
        [64.2, 64.6, 65.05, 65.5, 65.9].forEach(function (t) {
          s.appendChild(svg("text", { x: X(t), y: bottom + 22, "text-anchor": "middle", "font-size": 11, fill: "#64748B" }, fmt(t, 2)));
        });
        panel.appendChild(s);
        var hint = el("p", "qnote", "橫軸是水分 %（只畫 64.05–66.05 範圍，太寬的區間會被截斷）。畫面只顯示最近 100 條，統計數字會一直累計。");
        panel.appendChild(hint);

        var total = 0, hits = 0, sumHalf = 0, recent = [];
        function crit() {
          var n = parseInt(selN.value, 10), l = parseInt(selL.value, 10);
          return rZ.checked ? Z[l] : T[l][n];
        }
        function drawOne() {
          var n = parseInt(selN.value, 10), c = crit();
          var xs = [], mean = 0;
          for (var i = 0; i < n; i++) { var v = MU + SIGMA * randn(); xs.push(v); mean += v; }
          mean /= n;
          var ss = 0; xs.forEach(function (v) { ss += (v - mean) * (v - mean); });
          var sd = Math.sqrt(ss / (n - 1)), half = c * sd / Math.sqrt(n);
          var hit = MU >= mean - half && MU <= mean + half;
          total++; if (hit) hits++; sumHalf += half;
          recent.push({ m: mean, h: half, hit: hit });
          if (recent.length > ROWS) recent.shift();
        }
        function render() {
          while (gLines.firstChild) gLines.removeChild(gLines.firstChild);
          var rowH = (bottom - top) / ROWS;
          recent.forEach(function (r, i) {
            var y = top + i * rowH + rowH / 2;
            var col = r.hit ? "#5B8DB8" : "#C62828";
            gLines.appendChild(svg("line", { x1: X(r.m - r.h), y1: y, x2: X(r.m + r.h), y2: y, stroke: col, "stroke-width": r.hit ? 1.6 : 2.4, "stroke-opacity": r.hit ? 0.8 : 1 }));
            gLines.appendChild(svg("circle", { cx: X(r.m), cy: y, r: 1.6, fill: col }));
          });
          var miss = total - hits, cov = total ? hits / total * 100 : null;
          var l = parseInt(selL.value, 10);
          var covCls = cov === null ? "" : Math.abs(cov - l) <= 3 ? "ok" : "bad";
          stats.innerHTML =
            '<div class="gstat"><b>' + total + '</b><span>抽樣次數</span></div>' +
            '<div class="gstat"><b>' + hits + '</b><span>蓋到真值</span></div>' +
            '<div class="gstat' + (miss && total >= 20 && miss / total > (100 - l) / 100 * 1.6 ? " bad" : "") + '"><b>' + miss + '</b><span>漏掉真值</span></div>' +
            '<div class="gstat ' + covCls + '"><b>' + (cov === null ? "–" : fmt(cov, 1) + "%") + '</b><span>覆蓋率（目標 ' + l + '%）</span></div>' +
            '<div class="gstat"><b>' + (total ? "±" + fmt(sumHalf / total, 3) : "–") + '</b><span>平均半寬（%）</span></div>' +
            '<div class="gstat"><b>' + fmt(crit(), 3) + '</b><span>' + (rZ.checked ? "Z 值" : "t 值 (df=" + (parseInt(selN.value, 10) - 1) + ")") + '</span></div>';
        }
        function resetSim() { total = 0; hits = 0; sumHalf = 0; recent = []; render(); }
        b1.addEventListener("click", function () { drawOne(); render(); });
        b100.addEventListener("click", function () { for (var i = 0; i < 100; i++) drawOne(); render(); });
        bR.addEventListener("click", resetSim);
        [selN, selL, rT, rZ].forEach(function (c) { c.addEventListener("change", resetSim); });
        render();
        panel.appendChild(el("div", "callout ok",
          '<span class="t">🔬 三個實驗</span>' +
          '① 維持 n = 4、95%、t：按「抽 100 次」幾回，漏掉的通常在 2~10 之間，長期逼近 5%。' +
          '② 把 n 改成 16：看「平均半寬」是不是差不多減半。' +
          '③ 切到「硬用 Z」：覆蓋率會掉到 86% 左右——這就是小樣本要用 t 的理由。'));
      }
    });
  };

  /* ==================================================================
     Ch3：管制圖巡檢員 — 下一個月 25 天的 QC 標準品資料，換你判讀
     資料由 R 產生（set.seed(31)、rnorm(25, 12, 0.15)，第 5–16 天人為壓到中心線下方、
     第 17 天 12.34、第 21 天 12.55），規則答案以 R 實算：規則① 第 21 天；規則③ 第 17 天；
     規則② 第 5–16 天連續 12 點在中心線下方。
     ================================================================== */
  GAMES["ch03-qcpatrol"] = function (box) {
    var QC = [12.008, 11.972, 12.239, 12.145, 11.714, 11.873, 11.881, 11.802, 11.749, 11.830, 11.780, 11.890, 11.914,
              11.843, 11.851, 11.862, 12.340, 12.128, 12.005, 11.862, 12.550, 11.970, 12.093, 12.114, 11.982];
    var CL = 12.00, S = 0.15, N = QC.length;
    var ACTION = [21], WARN = [17], RUN = [5, 16];
    function setEq(a, b) { if (a.length !== b.length) return false; return a.every(function (x) { return b.indexOf(x) >= 0; }); }

    // 共用畫圖：mode = "play"（可點）| "key"（顯示解答與學生標記的對錯）
    function chart(state, mode, onClick) {
      var W = 680, H = 300, L = 46, R = 70, T = 22, B = 34, yLo = 11.45, yHi = 12.65;
      function X(i) { return L + i / (N - 1) * (W - L - R); }
      function Y(v) { return T + (yHi - v) / (yHi - yLo) * (H - T - B); }
      var s = svg("svg", { viewBox: "0 0 " + W + " " + H, class: "gsvg", role: "img", "aria-label": "Shewhart 管制圖，25 天 QC 標準品測值" });
      s.style.minWidth = "560px";
      [[CL, "#1F2937", "", "CL 12.00"], [CL + 2 * S, "#F6A21D", "5 3", "+2s 12.30"], [CL - 2 * S, "#F6A21D", "5 3", "−2s 11.70"],
       [CL + 3 * S, "#C62828", "5 3", "+3s 12.45"], [CL - 3 * S, "#C62828", "5 3", "−3s 11.55"]].forEach(function (ln) {
        s.appendChild(svg("line", { x1: L, y1: Y(ln[0]), x2: W - R + 4, y2: Y(ln[0]), stroke: ln[1], "stroke-width": ln[2] ? 1.4 : 1.8, "stroke-dasharray": ln[2] }));
        s.appendChild(svg("text", { x: W - R + 8, y: Y(ln[0]) + 4, "font-size": 11, fill: ln[1] }, ln[3]));
      });
      [11.5, 11.7, 12.0, 12.3, 12.5].forEach(function (v) {
        s.appendChild(svg("text", { x: L - 6, y: Y(v) + 4, "text-anchor": "end", "font-size": 11, fill: "#64748B" }, fmt(v, 1)));
      });
      s.appendChild(svg("line", { x1: L, y1: H - B + 6, x2: W - R + 4, y2: H - B + 6, stroke: "#64748B" }));
      for (var i = 0; i < N; i++) {
        if ((i + 1) % 2 === 1) s.appendChild(svg("text", { x: X(i), y: H - B + 22, "text-anchor": "middle", "font-size": 11, fill: "#64748B" }, String(i + 1)));
      }
      s.appendChild(svg("text", { x: (L + W - R) / 2, y: H - 2, "text-anchor": "middle", "font-size": 11, fill: "#64748B" }, "分析日"));
      var pts = QC.map(function (v, i) { return X(i) + "," + Y(v); }).join(" ");
      s.appendChild(svg("polyline", { points: pts, fill: "none", stroke: "#5B8DB8", "stroke-width": 1.5 }));
      if (mode === "key") {
        // 規則②：連續同側的區段
        s.appendChild(svg("rect", { x: X(RUN[0] - 1) - 8, y: Y(CL) + 2, width: X(RUN[1] - 1) - X(RUN[0] - 1) + 16, height: Y(yLo) - Y(CL) - 30, fill: "#6A3FA0", "fill-opacity": 0.08, stroke: "#6A3FA0", "stroke-dasharray": "4 3", rx: 6 }));
        s.appendChild(svg("text", { x: (X(RUN[0] - 1) + X(RUN[1] - 1)) / 2, y: Y(yLo) - 34, "text-anchor": "middle", "font-size": 12, fill: "#4A2A80", "font-weight": 700 }, "規則②：第 5–16 天連續 12 點在 CL 下方"));
      }
      QC.forEach(function (v, i) {
        var d = i + 1, g = svg("g", { style: mode === "play" ? "cursor:pointer" : "" });
        var truth = ACTION.indexOf(d) >= 0 ? 1 : WARN.indexOf(d) >= 0 ? 2 : 0;
        var mark = state[i];
        if (mode === "key") {
          if (truth) g.appendChild(svg("circle", { cx: X(i), cy: Y(v), r: 10, fill: "none", stroke: truth === 1 ? "#C62828" : "#F6A21D", "stroke-width": 3 }));
          if (mark !== truth) {
            g.appendChild(svg("text", { x: X(i), y: Y(v) - 13, "text-anchor": "middle", "font-size": 13, "font-weight": 700, fill: "#C62828" }, mark && !truth ? "✗ 多標" : mark ? "✗ 類別錯" : "✗ 漏標"));
          } else if (truth) {
            g.appendChild(svg("text", { x: X(i), y: Y(v) - 13, "text-anchor": "middle", "font-size": 13, "font-weight": 700, fill: "#2E7D32" }, "✓"));
          }
        } else if (mark) {
          g.appendChild(svg("circle", { cx: X(i), cy: Y(v), r: 10, fill: "none", stroke: mark === 1 ? "#C62828" : "#F6A21D", "stroke-width": 3 }));
          g.appendChild(svg("text", { x: X(i), y: Y(v) - 13, "text-anchor": "middle", "font-size": 12, "font-weight": 700, fill: mark === 1 ? "#C62828" : "#8A5A00" }, mark === 1 ? "停線" : "警覺"));
        }
        g.appendChild(svg("circle", { cx: X(i), cy: Y(v), r: 4.5, fill: "#0F4C81" }));
        if (mode === "play") {
          g.appendChild(svg("circle", { cx: X(i), cy: Y(v), r: 13, fill: "transparent" }));
          g.appendChild(svg("title", {}, "第 " + d + " 天：" + fmt(v, 3) + "%"));
          g.addEventListener("click", function () { onClick(i); });
        }
        s.appendChild(g);
      });
      return s;
    }

    predictGame(box, {
      gid: "ch03-qcpatrol",
      badge: "管制圖巡檢員",
      stepWord: "任務", scoreWord: "答對",
      title: "下一個月的 25 天，換你當巡檢員",
      intro: "上面那個月的圖你已經跟著判讀過了。這是<strong>下一個月</strong>同一個 QC 標準品（蛋白質 12.00%，s = 0.15%）的 25 天測值，" +
             "中心線與 ±2s、±3s 界限都相同。請照 3.3 節的三條規則巡檢一遍，再按下揭曉對答案。",
      questions: [
        { id: "ch03-g01-1", v: 1,
          q: "在圖上直接標記：點一下＝🔴 <strong>停線</strong>（超出 ±3s，規則①），再點一下＝🟠 <strong>警覺加測</strong>（超出 ±2s 但未達 ±3s，規則③），再點一下取消。只標這兩類，規則②留到下一題。",
          mount: function (div) {
            var state = QC.map(function () { return 0; }), locked = false, holder = el("div", "gsvgwrap");
            function draw(mode) { holder.innerHTML = ""; holder.appendChild(chart(state, mode, function (i) { if (locked) return; state[i] = (state[i] + 1) % 3; draw("play"); })); }
            var legend = el("p", "qnote", "提示：滑鼠移到點上可看當天數值。界限：+3s = 12.45、+2s = 12.30、−2s = 11.70、−3s = 11.55。");
            div.appendChild(holder); div.appendChild(legend); draw("play");
            var key = null;
            return {
              read: function () {
                var A = [], Wn = [];
                state.forEach(function (m, i) { if (m === 1) A.push(i + 1); else if (m === 2) Wn.push(i + 1); });
                var answered = A.length + Wn.length > 0;
                var correct = setEq(A, ACTION) && setEq(Wn, WARN);
                var tag = null;
                if (answered && !correct && setEq(A.concat(Wn), ACTION.concat(WARN))) tag = "WARNING_VS_ACTION";
                return { answered: answered, correct: correct, idx: null, value: state.join(""), tag: tag };
              },
              showKey: function () {
                locked = true; draw("key");
                key = el("div", "qkey", "解答：第 21 天 12.55 超出 +3s → 🔴 停線；第 17 天 12.34 超出 +2s 未達 +3s → 🟠 警覺加測。其餘各天都在 ±2s 內。");
                div.insertBefore(key, div.querySelector(".exp"));
              },
              reset: function () { locked = false; state = QC.map(function () { return 0; }); if (key) { key.remove(); key = null; } draw("play"); }
            };
          },
          exp: "只有兩天需要依界限處置。但先別鬆一口氣——這個月真正的問題不在「有沒有點超線」，看下一題。" },
        { id: "ch03-g01-2", v: 1,
          q: "規則②：這個月有沒有「連續 7 點以上在中心線同一側」的系統性漂移？",
          opts: ["沒有，這個月只有第 21 天出問題", "有：第 5–16 天連續 12 點都在中心線下方", "有：第 1–4 天連續在中心線上方", "有：第 17–21 天連續在中心線上方"],
          ans: 1, tags: ["SHEWHART_ONLY_OUT_OF_LIMIT", null, null, null],
          exp: "第 5 到 16 天共 12 個點全部低於 12.00%，其中沒有任何一點碰到 −2s。只盯界限會完全漏掉它——但連續 12 點同側，若真的沒有偏移，機率只有 (1/2)<sup>11</sup> ≈ 0.05%，" +
               "這就是系統性偏低（可能是標準品保存、校正或試劑批次改變）。第 1–4 天有 2 點在上、2 點在下；第 17–21 天第 20 天在下方，都不成立。" },
        { id: "ch03-g01-3", v: 1,
          q: "第 21 天 12.55% 衝出 +3s 行動界限，當天正確的處置是？",
          opts: ["重測一次 QC，沒超界就照常出報告", "停線：當天樣品結果暫不發出，找根本原因並記錄，排除後才恢復", "把行動界限放寬到法規允許的 ±0.6%，這樣就沒超界", "把第 21 天這一點刪掉，管制圖就正常了"],
          ans: 1, tags: ["RETEST_UNTIL_PASS", null, "CONTROL_LIMIT_IS_SPEC", "OUTLIER_DELETE_BY_EYE"],
          exp: "±3s 是製程自己的能力界限，超出代表「今天的系統和平常不一樣」，重測到過關只是把警訊蓋掉；放寬到規格限值是把管制界限和法規限值混為一談；" +
               "刪點更是把證據銷毀。正確做法是停線、查根本原因（校正、試劑、儀器、人員）、記錄、確認排除後再恢復，當天樣品要重做。" }
      ],
      revealLabel: "送出巡檢結果並揭曉",
      reveal: function (panel, results) {
        panel.appendChild(el("h4", null, "這個月的巡檢報告"));
        var cs = [], acc = 0;
        QC.forEach(function (v) { acc += v - CL; cs.push(acc); });
        var W = 680, H = 200, L = 46, R = 70, T = 16, B = 30, yLo = -1.8, yHi = 0.6;
        function X(i) { return L + i / (N - 1) * (W - L - R); }
        function Y(v) { return T + (yHi - v) / (yHi - yLo) * (H - T - B); }
        var s = svg("svg", { viewBox: "0 0 " + W + " " + H, class: "gsvg", role: "img", "aria-label": "CuSum 累積偏差圖" });
        s.style.minWidth = "560px";
        s.appendChild(svg("line", { x1: L, y1: Y(0), x2: W - R + 4, y2: Y(0), stroke: "#1F2937", "stroke-dasharray": "5 3" }));
        [-1.5, -1.0, -0.5, 0, 0.5].forEach(function (v) { s.appendChild(svg("text", { x: L - 6, y: Y(v) + 4, "text-anchor": "end", "font-size": 11, fill: "#64748B" }, fmt(v, 1))); });
        for (var i = 0; i < N; i += 2) s.appendChild(svg("text", { x: X(i), y: H - B + 18, "text-anchor": "middle", "font-size": 11, fill: "#64748B" }, String(i + 1)));
        s.appendChild(svg("polyline", { points: cs.map(function (v, i) { return X(i) + "," + Y(v); }).join(" "), fill: "none", stroke: "#2E7D32", "stroke-width": 2 }));
        cs.forEach(function (v, i) { s.appendChild(svg("circle", { cx: X(i), cy: Y(v), r: 3.5, fill: "#2E7D32" })); });
        s.appendChild(svg("text", { x: X(4), y: Y(cs[4]) - 10, "font-size": 12, fill: "#4A2A80", "font-weight": 700 }, "第 5 天起一路下滑"));
        s.appendChild(svg("text", { x: W - R + 8, y: Y(0) + 4, "font-size": 11, fill: "#1F2937" }, "CuSum 0"));
        var wrap = el("div", "gsvgwrap"); wrap.appendChild(s); panel.appendChild(wrap);
        panel.appendChild(el("p", "qnote", "CuSum（每天偏差 qc − 12.00 的累積和）：Shewhart 圖上第 5–16 天看起來只是「偏低一點」，CuSum 卻從第 5 天就明顯轉向、一路下滑到 −1.65，第 17 天才因為那個 +2s 的點反彈。"));
        panel.appendChild(el("div", "gtablewrap",
          '<table class="gtable"><thead><tr><th>發現</th><th>依據</th><th>處置</th></tr></thead><tbody>' +
          '<tr class="hl"><td>第 21 天 12.55%</td><td>規則①：超出 +3s（12.45）</td><td>停線、找根本原因、當天樣品重做</td></tr>' +
          '<tr><td>第 17 天 12.34%</td><td>規則③：超出 +2s（12.30）未達 +3s</td><td>提高警覺、加測一次 QC 確認</td></tr>' +
          '<tr class="hl"><td>第 5–16 天</td><td>規則②：連續 12 點在中心線下方（沒有任何一點超界）</td><td>當成系統性偏移調查：標準品保存、校正、試劑批次；不必等到超界</td></tr>' +
          '</tbody></table>'));
        panel.appendChild(el("div", "callout warn", '<span class="t">🧭 巡檢員的心法</span>管制圖不是「有沒有紅點」的遊戲。單點超界（規則①③）抓的是<strong>突發</strong>事件，連串同側（規則②）與 CuSum 抓的是<strong>緩慢漂移</strong>——後者更常見、也更容易被忽略。3.4 節的其他 QC 手段（空白、加標回收、重複樣）都是為了讓這張圖有東西可畫。'));
      }
    });
  };

  /* ==================================================================
     Ch5：異常值獵人 — 四組食品分析數據，找出可疑值並用 Dixon Q（90%）判定能不能捨棄
     臨界值沿用 5.2 節表格；Q、平均與 SD 皆以 R 核算過。
     ================================================================== */
  GAMES["ch05-outlier"] = function (box) {
    var QCRIT = { 3: 0.94, 4: 0.76, 5: 0.64, 6: 0.56, 7: 0.51, 8: 0.47 };
    var ROUNDS = [
      { id: "ch05-g01-1", name: "水分 %（n = 4，課本範例）", x: [64.78, 64.53, 64.45, 55.31], d: 2 },
      { id: "ch05-g01-2", name: "灰分 %（n = 5）", x: [2.31, 2.35, 2.29, 2.33, 2.45], d: 2 },
      { id: "ch05-g01-3", name: "粗蛋白 %（n = 6）", x: [12.1, 12.4, 12.2, 12.3, 12.0, 13.1], d: 1 },
      { id: "ch05-g01-4", name: "粗脂肪 %（n = 5）", x: [3.42, 3.51, 3.47, 3.38, 3.55], d: 2 }
    ];
    function stats(x) {
      var m = 0; x.forEach(function (v) { m += v; }); m /= x.length;
      var ss = 0; x.forEach(function (v) { ss += (v - m) * (v - m); });
      return { mean: m, sd: x.length > 1 ? Math.sqrt(ss / (x.length - 1)) : NaN };
    }
    function dixon(x) {
      var srt = x.slice().sort(function (a, b) { return a - b; }), n = srt.length;
      var gLo = srt[1] - srt[0], gHi = srt[n - 1] - srt[n - 2];
      var lowEnd = gLo > gHi, gap = lowEnd ? gLo : gHi, range = srt[n - 1] - srt[0];
      var Q = gap / range, crit = QCRIT[n];
      var suspect = lowEnd ? srt[0] : srt[n - 1];
      return { sorted: srt, n: n, gap: gap, range: range, Q: Q, crit: crit, reject: Q > crit,
               suspect: suspect, suspectIdx: x.indexOf(suspect), lowEnd: lowEnd,
               before: stats(x), after: stats(x.filter(function (v) { return v !== suspect; })) };
    }
    ROUNDS.forEach(function (r) { r.t = dixon(r.x); });

    function roundMount(r) {
      return function (div) {
        var sel = null, locked = false;
        var strip = el("div", "gsvgwrap"), chips = el("div", "gchips");
        function draw() {
          strip.innerHTML = ""; chips.innerHTML = "";
          var W = 640, H = 90, L = 34, R = 34, AX = 46;
          var lo = Math.min.apply(null, r.x), hi = Math.max.apply(null, r.x), pad = (hi - lo) * 0.08 || 1;
          function X(v) { return L + (v - lo + pad) / (hi - lo + 2 * pad) * (W - L - R); }
          var s = svg("svg", { viewBox: "0 0 " + W + " " + H, class: "gsvg", role: "img", "aria-label": r.name + " 數據點" });
          s.appendChild(svg("line", { x1: L, y1: AX, x2: W - R, y2: AX, stroke: "#94A3B8" }));
          // 數值標籤：太靠近就改放軸下方，再擠就略過（數字另有下方的籌碼可看）
          var labelY = {}, lastTop = -1e9, lastBot = -1e9;
          r.x.map(function (v, i) { return [v, i]; }).sort(function (a, b) { return a[0] - b[0]; }).forEach(function (p) {
            var x = X(p[0]);
            if (x - lastTop >= 40) { labelY[p[1]] = AX - 18; lastTop = x; }
            else if (x - lastBot >= 40) { labelY[p[1]] = AX + 26; lastBot = x; }
          });
          r.x.forEach(function (v, i) {
            var isSel = sel === i, isKey = locked && i === r.t.suspectIdx;
            var g = svg("g", { style: locked ? "" : "cursor:pointer" });
            if (isKey) g.appendChild(svg("circle", { cx: X(v), cy: AX, r: 12, fill: "none", stroke: r.t.reject ? "#C62828" : "#2E7D32", "stroke-width": 3, "stroke-dasharray": r.t.reject ? "" : "4 3" }));
            g.appendChild(svg("circle", { cx: X(v), cy: AX, r: isSel ? 8 : 6, fill: isSel ? "#F6A21D" : "#0F4C81", stroke: isSel ? "#8A5A00" : "none", "stroke-width": 2 }));
            if (labelY[i]) g.appendChild(svg("text", { x: X(v), y: labelY[i], "text-anchor": "middle", "font-size": 11, fill: "#1F2937" }, fmt(v, r.d)));
            g.appendChild(svg("circle", { cx: X(v), cy: AX, r: 14, fill: "transparent" }));
            if (!locked) g.addEventListener("click", function () { sel = sel === i ? null : i; draw(); });
            s.appendChild(g);
          });
          strip.appendChild(s);
          r.x.forEach(function (v, i) {
            var c = el("button", "gchip" + (sel === i ? " sel" : "") + (locked && i === r.t.suspectIdx ? " key" : ""), fmt(v, r.d));
            c.type = "button"; c.disabled = locked;
            c.addEventListener("click", function () { sel = sel === i ? null : i; draw(); });
            chips.appendChild(c);
          });
        }
        div.appendChild(el("div", "gintro", "點選你認為可疑的那個值（點圖上的點或下面的數字），再選判定："));
        div.appendChild(strip); div.appendChild(chips);
        var dec = el("div", "gdec");
        var opts = [["r", "可捨棄：Q > 臨界值"], ["k", "不可捨棄：Q ≤ 臨界值"], ["n", "根本沒有可疑值，不必檢定"]];
        var radios = [];
        opts.forEach(function (o) {
          var lab = document.createElement("label"), inp = document.createElement("input");
          inp.type = "radio"; inp.name = "ch05-outlier-" + r.id; inp.value = o[0];
          lab.appendChild(inp); lab.appendChild(el("span", null, " " + o[1]));
          dec.appendChild(lab); radios.push(inp);
        });
        div.appendChild(dec);
        draw();
        var key = null;
        return {
          read: function () {
            var d = null; radios.forEach(function (i) { if (i.checked) d = i.value; });
            if (!d) return { answered: false, correct: false, idx: null, value: null, tag: null };
            if (d !== "n" && sel === null) return { answered: false, correct: false, idx: null, value: null, tag: null };
            var t = r.t, correct, tag = null;
            if (t.reject) correct = d === "r" && sel === t.suspectIdx;
            else correct = d === "n" || (d === "k" && sel === t.suspectIdx);
            if (!correct) {
              if (d === "r" && !t.reject) tag = "OUTLIER_DELETE_BY_EYE";
              else if (d !== "n" && sel !== null && sel !== t.suspectIdx && ((d === "r") === t.reject)) tag = "Q_GAP_RANGE_WRONG";
            }
            return { answered: true, correct: correct, idx: null, value: "s=" + (sel === null ? "-" : sel) + ";d=" + d, tag: tag };
          },
          showKey: function () {
            locked = true; draw(); radios.forEach(function (i) { i.disabled = true; });
            var t = r.t;
            key = el("div", "gtablewrap",
              '<table class="gtable"><tbody>' +
              "<tr><th>排序</th><td>" + t.sorted.map(function (v) { return fmt(v, r.d); }).join("、") + "</td></tr>" +
              "<tr><th>可疑端</th><td>" + fmt(t.suspect, r.d) + "（" + (t.lowEnd ? "最小值" : "最大值") + "，與最近鄰的間距較大）</td></tr>" +
              "<tr><th>Q = gap ÷ 全距</th><td>" + fmt(t.gap, r.d) + " ÷ " + fmt(t.range, r.d) + " = <strong>" + fmt(t.Q, 3) + "</strong></td></tr>" +
              "<tr><th>Q<sub>0.90</sub>（n = " + t.n + "）</th><td>" + fmt(t.crit, 2) + "</td></tr>" +
              "<tr><th>判定</th><td>" + (t.reject ? '<strong style="color:#C62828">Q > 臨界值 → 統計上可捨棄</strong>' : '<strong style="color:#2E7D32">Q ≤ 臨界值 → 不可捨棄，' + fmt(t.suspect, r.d) + ' 只是運氣不好的正常值</strong>') + "</td></tr>" +
              (t.reject ? "<tr><th>捨棄前 → 後</th><td>平均 " + fmt(t.before.mean, r.d) + " → " + fmt(t.after.mean, r.d) + "；SD " + fmt(t.before.sd, r.d) + " → " + fmt(t.after.sd, r.d) + "</td></tr>" : "") +
              "</tbody></table>");
            key.classList.add("qkeybox");
            div.insertBefore(key, div.querySelector(".exp"));
          },
          reset: function () { locked = false; sel = null; radios.forEach(function (i) { i.disabled = false; i.checked = false; }); if (key) { key.remove(); key = null; } draw(); }
        };
      };
    }

    predictGame(box, {
      gid: "ch05-outlier",
      badge: "異常值獵人",
      stepWord: "關卡", scoreWord: "答對",
      title: "四組數據、四個決定：這個值能不能刪？",
      intro: "每一關給你一組重複分析的結果。先指出可疑值，再用 5.2 節的 Dixon Q 檢定（90% 信賴）判定能不能捨棄；" +
             "臨界值：n=3 → 0.94、n=4 → 0.76、n=5 → 0.64、n=6 → 0.56。心算就好，揭曉時會列出完整計算。最後兩關考的是「檢定之後」該怎麼做。",
      questions: [
        { id: ROUNDS[0].id, v: 1, q: ROUNDS[0].name, mount: roundMount(ROUNDS[0]),
          exp: "55.31 離最近鄰 9.14，占全距 9.47 的 97%：Q = 0.965 ≫ 0.76。這就是課本範例，統計上支持捨棄。但要不要真的刪，看第 6 關。" },
        { id: ROUNDS[1].id, v: 1, q: ROUNDS[1].name, mount: roundMount(ROUNDS[1]),
          exp: "2.45 看起來明顯偏高，但 Q = 0.10 ÷ 0.16 = 0.625，<strong>沒有</strong>超過 n=5 的臨界值 0.64。「看起來怪」不是理由——這就是要做檢定的原因。" },
        { id: ROUNDS[2].id, v: 1, q: ROUNDS[2].name, mount: roundMount(ROUNDS[2]),
          exp: "13.1 的 Q = 0.70 ÷ 1.10 = 0.636 > 0.56，統計上可捨棄；捨棄後 SD 從 0.39 掉到 0.16。注意：剩下的 5 個值<strong>不能</strong>再做一次 Q 檢定（第 5 關）。" },
        { id: ROUNDS[3].id, v: 1, q: ROUNDS[3].name, mount: roundMount(ROUNDS[3]),
          exp: "兩端間距都只有 0.04，Q = 0.235，遠低於 0.64——這組數據很正常。選「沒有可疑值」或「不可捨棄」都對；重點是不要為了讓 SD 更漂亮而動它。" },
        { id: "ch05-g01-5", v: 1,
          q: "第 3 關捨棄 13.1 之後，剩下的 5 個粗蛋白值可以再做一次 Q 檢定嗎？",
          opts: ["可以，一直做到沒有異常值為止", "不可以：Q 檢定設計上一次只處理一個可疑值，重複做會越刪越多、SD 越縮越小", "可以，但每組數據最多只能刪一個"],
          ans: 1, tags: ["OUTLIER_TEST_REPEAT", null, "OUTLIER_QUOTA"],
          exp: "刪掉一個極端值後全距變小，下一個值的 Q 自然變大，重複檢定就是把正常散布一層層剝掉。Nielsen 說異常值捨棄「非常罕見」；若一組數據有兩個以上可疑值，該懷疑的是方法或操作，不是數據。" },
        { id: "ch05-g01-6", v: 1,
          q: "第 1 關的 Q 檢定說「可捨棄」。接下來正確的做法是？",
          opts: ["直接刪掉，報告用剩下 3 個值算平均就好", "先查實驗紀錄：有可追溯的操作失誤（漏加試劑、樣品灑落）且統計支持，才刪除，並在報告中揭露檢定方法與理由", "只要刪了之後 SD 明顯變小，就代表刪得對", "看起來怪的值本來就該先刪，檢定只是形式"],
          ans: 1, tags: ["OUTLIER_DELETE_BY_TEST_ONLY", null, "OUTLIER_DELETE_FOR_PRECISION", "OUTLIER_DELETE_BY_EYE"],
          exp: "檢定只說「它很可疑」，刪除需要「操作失誤紀錄 ＋ 統計支持」兩者兼備，而且要揭露。QUAM §2.4.13：純粹以統計理由拒絕數值通常不明智。SD 變小不是理由，那正是扭曲結果的動機。" }
      ],
      revealLabel: "送出判定並揭曉",
      reveal: function (panel, results) {
        panel.appendChild(el("h4", null, "四關總表"));
        var rows = ROUNDS.map(function (r, i) {
          var t = r.t;
          return "<tr" + (t.reject ? ' class="hl"' : "") + "><td>" + (i + 1) + "</td><td>" + r.name + "</td><td class=\"num\">" + fmt(t.suspect, r.d) + "</td><td class=\"num\">" + fmt(t.Q, 3) +
                 "</td><td class=\"num\">" + fmt(t.crit, 2) + "</td><td>" + (t.reject ? "可捨棄" : "不可捨棄") + "</td><td>" + (results[i].correct ? "✓" : "✗") + "</td></tr>";
        }).join("");
        panel.appendChild(el("div", "gtablewrap",
          '<table class="gtable"><thead><tr><th>關</th><th>數據</th><th class="num">可疑值</th><th class="num">Q</th><th class="num">Q<sub>0.90</sub></th><th>判定</th><th>你</th></tr></thead><tbody>' + rows + "</tbody></table>"));
        panel.appendChild(el("div", "callout danger", '<span class="t">⚖️ 記住順序</span>看圖 → 算 Q（或 Grubbs G）→ 查實驗紀錄 → 兩者都支持才刪 → 報告揭露。任何一步跳過，都是在替自己的數據「美容」。'));
      }
    });
  };

  /* ---------------- 啟動 ---------------- */
  document.querySelectorAll(".game").forEach(function (box) {
    var id = box.dataset.game, g = GAMES[id];
    if (g) { try { g(box); } catch (e) { console.error("[games] " + id + " 渲染失敗：", e); } }
    else console.warn("[games] 找不到小遊戲：" + id);
  });
})();
