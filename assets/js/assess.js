// assess.js — 把測驗事件上傳到 Firestore `student_events`（專案 my-teaching-tools-517a0）
//
// 與 assets/app.js 只靠 localStorage 佇列 `fas_queue` 溝通：app.js 寫入、這裡送出並移除。
// 好處：沒有 module／classic script 的載入順序問題；離線或 Firebase 被擋時事件留在佇列，下次開頁補送。
//
// 沿用既有 firestore.rules 的 student_events 白名單（不需改規則）：
//   course_id ∈ 白名單、event_type ∈ {answer, attempt_complete, self_check, …}、timestamp == request.time
// 本站事件以 chapter 前綴 "FAS-"、game "fas_quiz"、site "fas" 與其他課程區隔。
// 前端只能 create、不能 read；讀取用教師端 scripts/quiz_dashboard.py（service account）。

import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.13.0/firebase-app.js';
import { getFirestore, addDoc, collection, serverTimestamp }
  from 'https://www.gstatic.com/firebasejs/10.13.0/firebase-firestore.js';

const CONFIG = {
  apiKey: "AIzaSyCTLhRf7jcJH_AwUzbV4MawkrKNPrIVG5Y",
  authDomain: "my-teaching-tools-517a0.firebaseapp.com",
  projectId: "my-teaching-tools-517a0",
  storageBucket: "my-teaching-tools-517a0.firebasestorage.app",
  messagingSenderId: "244288457011",
  appId: "1:244288457011:web:4b3ff8a846a6c50b169646"
};
const COURSE_ID = '4y_food_analysis';
const GAME = 'fas_quiz';
const QUEUE_KEY = 'fas_queue', DEAD_KEY = 'fas_dead';

let db = null;
try { db = getFirestore(initializeApp(CONFIG, 'fas')); }
catch (e) { console.warn('[FAS] Firestore 初始化失敗：', e.message); }

const read = (k) => { try { return JSON.parse(localStorage.getItem(k)) || []; } catch (e) { return []; } };
const write = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* 已滿或私密模式 */ } };

function toDoc(ev) {
  const nz = (v) => (v === undefined ? null : v);
  return {
    // 規則檢查的欄位
    student_id: String(ev.student_id).slice(0, 20),
    course_id: COURSE_ID,
    class_id: String(ev.class_id || 'A').slice(0, 10),
    chapter: ('FAS-' + String(ev.chapter_id || '').toUpperCase()).slice(0, 20),
    game: GAME,
    event_type: ev.event_type,
    timestamp: serverTimestamp(),
    // 與既有 student_events 相容的欄位
    question_id: nz(ev.question_id), is_correct: nz(ev.is_correct), attempts: nz(ev.attempts),
    final_score: nz(ev.final_score), total: nz(ev.total), qtype: nz(ev.qtype),
    confidence: nz(ev.confidence), misconception: nz(ev.misconception),
    user_agent: (navigator.userAgent || '').slice(0, 200),
    // 本站新增
    site: 'fas', schema_v: 2, quiz_set: nz(ev.quiz_set), phase: nz(ev.phase), item_version: nz(ev.item_version), from_chapter: nz(ev.from),
    choice_idx: nz(ev.choice_idx), choice_value: nz(ev.choice_value), skipped: nz(ev.skipped),
    latency_ms: nz(ev.latency_ms), duration_ms: nz(ev.duration_ms), answered: nz(ev.answered),
    free_text: ev.free_text ? String(ev.free_text).slice(0, 200) : null,
    session_id: nz(ev.session_id), client_ts: nz(ev.client_ts)
  };
}

function status(text) {
  document.querySelectorAll('[data-fas-sync]').forEach((el) => { el.textContent = text; });
}

let flushing = false;
async function flush() {
  if (flushing || !db) return;
  flushing = true;
  try {
    for (;;) {
      const q = read(QUEUE_KEY);
      if (!q.length) { status(''); break; }
      const ev = q[0];
      let drop = true;
      try {
        if (ev.student_id) await addDoc(collection(db, 'student_events'), toDoc(ev));
      } catch (e) {
        // 規則拒絕或格式錯誤重試也不會成功 → 移到 fas_dead 留底；網路類錯誤則保留、下次再送
        if (e.code === 'permission-denied' || e.code === 'invalid-argument') {
          console.error('[FAS] 事件被拒：', e.code, ev);
          const dead = read(DEAD_KEY);
          dead.push({ ev, code: e.code, tries: (ev._tries || 0) + 1 });
          write(DEAD_KEY, dead.slice(-500));
          status('⚠ 作答紀錄暫時無法上傳，已保留在這台裝置上；請告訴老師，並可用下方按鈕匯出 CSV。');
        } else {
          drop = false;
        }
      }
      if (!drop) { status('⏳ 有 ' + q.length + ' 筆紀錄尚未上傳，連上網路後會自動補送。'); break; }
      // 重新讀一次再移除第一筆：等待上傳期間 app.js 可能又加了新事件
      const cur = read(QUEUE_KEY);
      if (cur.length && cur[0].client_ts === ev.client_ts && cur[0].question_id === ev.question_id) cur.shift();
      write(QUEUE_KEY, cur);
    }
  } finally {
    flushing = false;
  }
}

// 被拒的事件不一定是事件本身有錯（例如 API key 的網域限制或規則暫時設錯，回傳的也是 permission-denied），
// 所以每次開頁把 fas_dead 裡重試未滿 5 次的事件放回佇列再試一次，設定修好後資料會自動補送。
(function revive() {
  const dead = read(DEAD_KEY);
  const retry = dead.filter((d) => (d.tries || 1) < 5);
  if (!retry.length) return;
  write(DEAD_KEY, dead.filter((d) => (d.tries || 1) >= 5));
  write(QUEUE_KEY, retry.map((d) => Object.assign({}, d.ev, { _tries: d.tries || 1 })).concat(read(QUEUE_KEY)));
})();

window.addEventListener('fas-queue', flush);
window.addEventListener('online', flush);
flush();
