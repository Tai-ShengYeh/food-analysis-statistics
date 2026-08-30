/* ==================================================================
   showout.js — 為 pre.rcode 加上「執行結果」切換（R console 輸出）
   依賴：app.js 已建立 .rcodewrap > .rcodehead 結構（先載入 app.js）
   注意：app.js 會把 pre 搬進 .rcodewrap，
         因此頁面中寫在 </pre> 之後的 .rout 會變成 wrap 的下一個兄弟。
   ================================================================== */
(function () {
  var CSS_ID = "showout-css";
  if (!document.getElementById(CSS_ID)) {
    var st = document.createElement("style");
    st.id = CSS_ID;
    st.textContent =
      ".rout { display:none; border-top:1px solid #16324B; margin:0; border-radius:0; box-shadow:none; }" +
      ".rout.open { display:block; }" +
      ".act-out { background:#1B4A6B; color:#CDE7F7; margin-left:6px; }";
    document.head.appendChild(st);
  }

  document.querySelectorAll("pre.rcode").forEach(function (pre) {
    var wrap = pre.closest(".rcodewrap");
    var head = wrap && wrap.querySelector(".rcodehead");
    if (!head) return;                                  // app.js 未載入就略過
    if (head.querySelector(".act-out")) return;         // 已加過

    // app.js 已把 pre 包進 wrap → 原本在 </pre> 後面的 .rout 現在在 wrap 後面
    var after = wrap.nextElementSibling;
    var pane = (after && after.classList && after.classList.contains("rout")) ? after : null;
    var out = pane && pane.querySelector(".rout-body")
      ? pane.querySelector(".rout-body").textContent.trim() : "";

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "ghost act-out";
    head.querySelector(".spacer").insertAdjacentElement("afterend", btn);

    if (!out) {                                         // 無輸出資料 → 佔位提示
      btn.textContent = "▶ 執行結果（待補）";
      btn.style.opacity = ".5";
      btn.addEventListener("click", function () {
        btn.textContent = "此範例輸出將於下一批補上";
        setTimeout(function () { btn.textContent = "▶ 執行結果（待補）"; }, 1600);
      });
      return;
    }

    wrap.appendChild(pane);                             // 收進 wrap：程式碼在上、console 在下
    pane.classList.add("open");                         // 預設展開，直接看到結果
    btn.textContent = "▼ 隱藏結果";
    btn.addEventListener("click", function () {
      var open = pane.classList.toggle("open");
      btn.textContent = open ? "▼ 隱藏結果" : "▶ 執行結果";
    });
  });
})();
