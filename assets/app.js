/* ==================================================================
   app.js — 測驗引擎、R 程式碼下載/複製、導覽列互動
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

/* ---------- 2. 測驗引擎 ---------- */
/* 用法：頁面中放 <div class="quiz" id="quiz"></div> 與
   <script>const QUIZ=[{q,opts,ans,exp},...]</script> 於 app.js 之前 */
function renderQuiz(container, questions) {
  var box = document.createElement("div");
  box.className = "quizbox";
  box.innerHTML = "<h2>📝 隨堂測驗</h2>" +
    "<p>作答後按「批改」，每題都會顯示詳解。</p>";
  var order = questions.map(function (_, i) { return i; });
  order.forEach(function (qi) {
    var item = questions[qi];
    var div = document.createElement("div");
    div.className = "qitem";
    var html = '<div class="qtext">Q' + (qi + 1) + ". " + item.q + "</div>";
    item.opts.forEach(function (opt, oi) {
      html += '<label><input type="radio" name="q' + qi + '" value="' + oi + '">' + opt + "</label>";
    });
    html += '<div class="exp">💡 ' + item.exp + "</div>";
    div.innerHTML = html;
    box.appendChild(div);
  });
  var btn = document.createElement("button");
  btn.className = "qbtn";
  btn.textContent = "批改答案";
  var score = document.createElement("div");
  score.className = "qscore";
  btn.addEventListener("click", function () {
    var correct = 0, unanswered = 0;
    box.querySelectorAll(".qitem").forEach(function (div, qi) {
      var sel = div.querySelector("input:checked");
      var labels = div.querySelectorAll("label");
      labels.forEach(function (l) {
        l.classList.remove("sel");
        l.style.opacity = "";
      });
      if (!sel) { unanswered++; }
      div.classList.remove("correct", "wrong", "answered");
      if (sel) {
        labels[+sel.value].classList.add("sel");
        labels[questions[qi].ans].classList.add("sel");
        labels[questions[qi].ans].style.opacity = .75;
        div.classList.add(+sel.value === questions[qi].ans ? "correct" : "wrong", "answered");
        if (+sel.value === questions[qi].ans) correct++;
      } else {
        labels[questions[qi].ans].classList.add("sel");
        div.classList.add("answered");
      }
    });
    var n = questions.length;
    var pct = Math.round((correct / n) * 100);
    score.textContent = "得分：" + correct + " / " + n +
      (unanswered ? "（有 " + unanswered + " 題未作答）" : "") +
      "　" + (pct >= 80 ? "🎉 太棒了，觀念很清楚！" :
              pct >= 60 ? "👍 不錯，再複習答錯的部分。" :
                          "💪 別氣餒，回到內文重讀一次再挑戰！");
    score.className = "qscore " + (pct >= 80 ? "good" : pct >= 60 ? "mid" : "low");
  });
  box.appendChild(btn);
  box.appendChild(score);
  container.appendChild(box);
}

document.querySelectorAll(".quiz").forEach(function (el) {
  if (window.QUIZ && window.QUIZ.length) renderQuiz(el, window.QUIZ);
});

/* ---------- 3. 導覽列 current 標記 ---------- */
(function () {
  var page = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".topnav a").forEach(function (a) {
    var href = a.getAttribute("href");
    if (href === page) a.classList.add("active");
  });
})();
