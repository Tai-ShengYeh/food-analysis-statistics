#!/usr/bin/env node
/* 檢查全站各章測驗是否符合 docs/QUIZ_SCHEMA.md。改完題目後執行：
     node scripts/check_quiz.js          # 檢查，有錯誤時 exit 1
     node scripts/check_quiz.js --keys   # 另外列出全站迷思 key 與使用章節（找重複語意的 key 用）
     node scripts/check_quiz.js --json   # 輸出題庫 JSON（給 quiz_dashboard.py 或其他工具用） */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "..");
const NO_PRE = new Set(["ch00", "ch11"]);            // 導覽章與期末總測驗不需要前測
const NO_SPACED = new Set(["ch00", "ch01", "ch02", "ch11"]);
const TYPES = new Set(["concept", "calc", "rout", "misc"]);
const PHASES = new Set(["pre", "post", "spaced"]);

function load(file) {
  const html = fs.readFileSync(path.join(ROOT, file), "utf8");
  const m = html.match(/<script>((?:(?!<\/script>)[\s\S])*?const QUIZ\s*=[\s\S]*?)<\/script>/);
  if (!m) return null;
  const ctx = {};
  // 同頁的第二組題目（ch11 的期末總測驗 FINALEXAM）併入一起檢查
  const extra = html.match(/<script>((?:(?!<\/script>)[\s\S])*?const FINALEXAM\s*=[\s\S]*?)<\/script>/);
  vm.runInNewContext(m[1] + "\n" + (extra ? extra[1] : "") + "\n;this.__out = {" +
    "CHAPTER: typeof CHAPTER !== 'undefined' ? CHAPTER : null," +
    "MISC: typeof MISC !== 'undefined' ? MISC : null," +
    "QUIZ: QUIZ.concat(typeof FINALEXAM !== 'undefined' ? FINALEXAM : [])};", ctx, { filename: file });
  return Object.assign({ html }, ctx.__out);
}

const files = fs.readdirSync(ROOT).filter((f) => /^ch\d\d\.html$/.test(f)).sort();
const errors = [], warnings = [], bank = {}, keyUse = {}, keyText = {}, allIds = new Set();
let total = 0;

for (const file of files) {
  const ch = file.slice(0, 4);
  const err = (msg) => errors.push(`${file}: ${msg}`);
  const warn = (msg) => warnings.push(`${file}: ${msg}`);
  let d;
  try { d = load(file); } catch (e) { err("QUIZ script 無法執行：" + e.message); continue; }
  if (!d) { warn("沒有 QUIZ"); continue; }
  if (d.CHAPTER !== ch) err(`CHAPTER 應為 "${ch}"，目前是 ${JSON.stringify(d.CHAPTER)}`);
  if (!d.MISC) { err("缺少 MISC 字典"); d.MISC = {}; }
  bank[ch] = { MISC: d.MISC, QUIZ: d.QUIZ };
  Object.entries(d.MISC).forEach(([k, v]) => {
    if (!/^[A-Z][A-Z0-9_]*$/.test(k)) err(`MISC key 格式錯誤：${k}`);
    if (keyText[k] && keyText[k] !== v) warn(`MISC.${k} 的中文描述與其他章不同：「${v}」vs「${keyText[k]}」`);
    keyText[k] = keyText[k] || v;
  });
  const used = new Set(), count = { pre: 0, post: 0, spaced: 0 }, types = {}, pos = [0, 0, 0, 0, 0, 0];
  let nums = 0, other = 0;
  const tagOk = (t, where) => {
    if (!(t in d.MISC)) err(`${where}: tag ${t} 不在 MISC`);
    used.add(t); (keyUse[t] = keyUse[t] || new Set()).add(ch);
    if (t === "OTHER") other++;
  };
  d.QUIZ.forEach((it, i) => {
    const w = it.id || `#${i + 1}`;
    total++;
    if (!it.id || !new RegExp(`^${ch}-[pqs]\\d\\d$`).test(it.id)) err(`${w}: id 格式應為 ${ch}-q01 / -p01 / -s01`);
    if (allIds.has(it.id)) err(`${w}: id 重複`);
    allIds.add(it.id);
    if (!Number.isInteger(it.v) || it.v < 1) err(`${w}: 缺少版號 v`);
    if (!TYPES.has(it.type)) err(`${w}: type 不合法（${it.type}）`);
    const phase = it.phase || "post";
    if (!PHASES.has(phase)) err(`${w}: phase 不合法（${it.phase}）`);
    else count[phase]++;
    if (it.id && { p: "pre", q: "post", s: "spaced" }[it.id.slice(5, 6)] !== phase) err(`${w}: id 字母與 phase（${phase}）不一致`);
    if (phase === "spaced" && !/^ch\d\d$/.test(it.from || "")) err(`${w}: 回溯題缺少 from`);
    if (phase === "post") types[it.type] = (types[it.type] || 0) + 1;
    if (!it.q || !it.exp) err(`${w}: 缺少 q 或 exp`);
    if (it.num) {
      nums++;
      if (typeof it.num.ans !== "number" || !(it.num.tol > 0)) err(`${w}: num.ans / num.tol 不合法`);
      const ranges = [[it.num.ans - it.num.tol, it.num.ans + it.num.tol, "正解"]];
      (it.errs || []).forEach((e) => {
        if (typeof e.val !== "number" || !(e.tol > 0)) err(`${w}: errs 的 val/tol 不合法`);
        tagOk(e.tag, w);
        ranges.forEach((r) => {
          if (e.val - e.tol <= r[1] && e.val + e.tol >= r[0]) err(`${w}: errs ${e.val} 的容許範圍與 ${r[2]} 重疊`);
        });
        ranges.push([e.val - e.tol, e.val + e.tol, "errs " + e.val]);
      });
      if (!(it.errs || []).length) warn(`${w}: 數值題沒有 errs，答錯時無法診斷迷思`);
    } else {
      if (!Array.isArray(it.opts) || it.opts.length < 2) { err(`${w}: 缺少 opts`); return; }
      if (!(it.ans >= 0 && it.ans < it.opts.length)) err(`${w}: ans 超出範圍`);
      if (!Array.isArray(it.tags) || it.tags.length !== it.opts.length) { err(`${w}: tags 長度須與 opts 相同`); return; }
      it.tags.forEach((t, oi) => {
        if (oi === it.ans) { if (t !== null) err(`${w}: 正解位置的 tag 必須是 null`); }
        else if (!t) err(`${w}: 選項 ${oi} 沒有 tag`);
        else tagOk(t, w);
      });
      if (new Set(it.opts).size !== it.opts.length) err(`${w}: 有重複的選項文字`);
      if (phase !== "pre") pos[it.ans]++;
    }
  });
  Object.keys(d.MISC).forEach((k) => { if (!used.has(k)) warn(`MISC.${k} 未被任何題目使用`); });
  if (!NO_PRE.has(ch) && count.pre !== 3) err(`前測應為 3 題，目前 ${count.pre}`);
  if (!NO_SPACED.has(ch) && count.spaced < 1) err("缺少回溯題");
  if (ch !== "ch00") {
    if (count.post < 6) err(`課後題太少（${count.post}）`);
    ["concept", "calc"].forEach((t) => { if ((types[t] || 0) < 2) warn(`課後 ${t} 題少於 2（${types[t] || 0}）`); });
    ["rout", "misc"].forEach((t) => { if (!types[t]) warn(`課後沒有 ${t} 題`); });
    if (!nums) warn("沒有數值填空題");
  }
  if (other > 3) warn(`OTHER 用了 ${other} 次（建議 ≤3）`);
  const mcq = pos.reduce((a, b) => a + b, 0);
  if (mcq >= 6 && Math.max(...pos) / mcq > 0.5) warn(`正解位置過度集中：${pos.slice(0, 4).join("/")}`);
  // 頁面接線
  if (!/<div class="quiz" id="quiz">/.test(d.html)) err("缺少章末測驗容器");
  if (count.pre && !/data-phase="pre"/.test(d.html)) err("有前測題但缺少 data-phase=\"pre\" 容器");
  if (!/assets\/js\/assess\.js/.test(d.html)) err("未載入 assets/js/assess.js");
  console.log(`${ch}  pre ${count.pre}  post ${count.post}  spaced ${count.spaced}  num ${nums}  正解位置 ${pos.slice(0, 4).join("/")}  迷思 ${Object.keys(d.MISC).length}`);
}

if (process.argv.includes("--json")) {
  fs.writeFileSync(path.join(ROOT, "docs", "quiz_bank.json"), JSON.stringify(bank, null, 1));
}
if (process.argv.includes("--keys")) {
  console.log("\n全站迷思 key（使用章節）：");
  Object.keys(keyUse).sort().forEach((k) => console.log(`  ${k}  [${[...keyUse[k]].join(",")}]  ${keyText[k] || ""}`));
}
console.log(`\n共 ${files.length} 章、${total} 題、${Object.keys(keyUse).length} 個迷思 key。`);
warnings.forEach((w) => console.log("⚠ " + w));
errors.forEach((e) => console.log("✗ " + e));
console.log(errors.length ? `\n${errors.length} 個錯誤、${warnings.length} 個警告。` : `\n✓ 無錯誤（${warnings.length} 個警告）。`);
process.exit(errors.length ? 1 : 0);
