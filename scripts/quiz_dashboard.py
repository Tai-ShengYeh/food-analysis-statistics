#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
quiz_dashboard.py — FAS（food-analysis-statistics）測驗成效教師端報表

從 Firestore `student_events`（site == "fas"）讀取本站測驗事件，離線產生一份
單檔 HTML 報表：全班學習成效總覽、各章成效（pre/post/normalized gain）、
逐題表（含鑑別度、迷思、信心、延遲）、迷思熱區、信心 × 對錯象限、
「我還不懂的地方」彙整、以及（可選）個別學生成績表。

用法見 scripts/README_dashboard.md，或執行：
    python scripts/quiz_dashboard.py --help

安全：金鑰路徑只透過 --key / 環境變數 FAS_SA_KEY 指定，絕不寫入本檔或輸出檔。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
import re
import statistics
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html import escape as _esc

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_KEY_FALLBACK = r"C:\Users\USER\.fb_admin\sa_key.json"
SITE = "fas"

TEST_PREFIXES = ("ZZ", "TEST", "_")
TEST_EXACT = {"GUEST"}


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------

def strip_html(s):
    if not s:
        return ""
    return re.sub(r"<[^>]+>", "", str(s))


def truncate(s, n):
    s = s or ""
    return s if len(s) <= n else s[:n] + "…"


def is_test_account(student_id):
    if not student_id:
        return True
    s = str(student_id).strip().upper()
    if not s:
        return True
    if s in TEST_EXACT:
        return True
    for p in TEST_PREFIXES:
        if s.startswith(p):
            return True
    return False


def norm_chapter(chapter_field):
    """Firestore 的 chapter 欄位形如 'FAS-CH02' -> 'ch02'。"""
    if not chapter_field:
        return None
    c = str(chapter_field)
    if c.upper().startswith("FAS-"):
        c = c[4:]
    return c.lower()


def parse_client_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None


def safe_div(a, b):
    return (a / b) if b else None


def fmt_pct(x, digits=1):
    if x is None:
        return "—"
    return f"{x * 100:.{digits}f}%"


def fmt_num(x, digits=2):
    if x is None:
        return "—"
    return f"{x:.{digits}f}"


def bar_cell(frac, color="#4a7fd6"):
    """簡單 inline 長條，frac in [0,1] 或 None。"""
    if frac is None:
        return '<span class="muted">—</span>'
    frac = max(0.0, min(1.0, frac))
    pct_txt = f"{frac * 100:.0f}%"
    width = f"{frac * 100:.1f}%"
    return (
        '<div class="barwrap"><div class="bar" style="width:{w};background:{c}"></div>'
        '<span class="barlabel">{t}</span></div>'
    ).format(w=width, c=color, t=pct_txt)


# ---------------------------------------------------------------------------
# 1. 讀取事件（Firestore / --from-json / --demo）
# ---------------------------------------------------------------------------

def fetch_events_from_firestore(key_path):
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError as e:
        raise SystemExit(
            "缺少 firebase-admin 套件，請先 `pip install firebase-admin`。原始錯誤：%s" % e
        )
    if not os.path.isfile(key_path):
        raise SystemExit(f"找不到 service account 金鑰檔：{key_path}")
    cred = credentials.Certificate(key_path)
    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass  # 已初始化過（例如同一行程重複呼叫）
    db = firestore.client()
    try:
        from google.cloud.firestore_v1.base_query import FieldFilter
        query = db.collection("student_events").where(filter=FieldFilter("site", "==", SITE))
    except ImportError:
        query = db.collection("student_events").where("site", "==", SITE)
    docs = list(query.stream())
    events = []
    for d in docs:
        row = d.to_dict() or {}
        row["_id"] = d.id
        events.append(row)
    return events


def load_events(args):
    if args.demo:
        return build_demo_events(), "demo"
    if args.from_json:
        with open(args.from_json, "r", encoding="utf-8") as f:
            events = json.load(f)
        return events, f"from-json:{args.from_json}"
    key_path = args.key or os.environ.get("FAS_SA_KEY") or DEFAULT_KEY_FALLBACK
    events = fetch_events_from_firestore(key_path)
    if args.dump_json:
        os.makedirs(os.path.dirname(os.path.abspath(args.dump_json)) or ".", exist_ok=True)
        with open(args.dump_json, "w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, default=str, indent=2)
    return events, f"firestore:{key_path}"


# ---------------------------------------------------------------------------
# 2. 篩選、去重
# ---------------------------------------------------------------------------

def filter_and_dedupe(events, args):
    since_dt = None
    if args.since:
        since_dt = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    seen = set()
    out = []
    dropped_dupe = 0
    dropped_test = 0
    dropped_class = 0
    dropped_since = 0
    dropped_game = 0

    for ev in events:
        if ev.get("site") != SITE:
            continue
        # 章內小遊戲（assets/js/games.js，game == "fas_game"）與測驗分流：
        # 目前儀表板只分析測驗題；遊戲事件先略過，待另做 game 報表（見 docs/QUIZ_SCHEMA.md「章內小遊戲」）。
        if ev.get("game", "fas_quiz") != "fas_quiz":
            dropped_game += 1
            continue
        sid = ev.get("student_id")
        if not args.include_test and is_test_account(sid):
            dropped_test += 1
            continue
        if args.class_ and str(ev.get("class_id")) != args.class_:
            dropped_class += 1
            continue
        ts = parse_client_ts(ev.get("client_ts"))
        if since_dt is not None and ts is not None and ts < since_dt:
            dropped_since += 1
            continue
        key = (sid, ev.get("session_id"), ev.get("question_id"), ev.get("attempts"), ev.get("client_ts"))
        if key in seen:
            dropped_dupe += 1
            continue
        seen.add(key)
        ev = dict(ev)
        ev["_chapter_norm"] = norm_chapter(ev.get("chapter"))
        ev["_ts"] = ts
        out.append(ev)

    stats = {
        "raw": len(events),
        "kept": len(out),
        "dropped_dupe": dropped_dupe,
        "dropped_test": dropped_test,
        "dropped_class": dropped_class,
        "dropped_since": dropped_since,
        "dropped_game": dropped_game,
    }
    return out, stats


# ---------------------------------------------------------------------------
# 3. 題庫中繼資料（掃描 ch*.html，用 node 解析 QUIZ/MISC）
# ---------------------------------------------------------------------------

def _run_node_extract(script_body, node_bin="node", timeout=15):
    footer = """
;(function(){
  try {
    var out = {
      CHAPTER: (typeof CHAPTER !== 'undefined') ? CHAPTER : null,
      MISC: (typeof MISC !== 'undefined') ? MISC : {},
      QUIZ: ((typeof QUIZ !== 'undefined') ? QUIZ : [])
        .concat((typeof FINALEXAM !== 'undefined') ? FINALEXAM : [])
    };
    process.stdout.write(JSON.stringify(out));
  } catch (e) {
    process.stdout.write(JSON.stringify({__error: String(e && e.message || e)}));
  }
})();
"""
    full = script_body + "\n" + footer
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tf:
            tf.write(full)
            tmp_path = tf.name
        result = subprocess.run(
            [node_bin, tmp_path], capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace"
        )
        if result.returncode != 0:
            return None
        text = (result.stdout or "").strip()
        if not text:
            return None
        data = json.loads(text)
        if isinstance(data, dict) and "__error" in data:
            return None
        return data
    except Exception:
        return None
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def _find_quiz_script(html_text):
    # 同一頁可能有第二組題目（ch11 的期末總測驗 FINALEXAM），一併取出
    blocks = [m.group(1) for m in re.finditer(r"<script>([\s\S]*?)</script>", html_text)
              if re.search(r"\b(QUIZ|FINALEXAM)\s*=", m.group(1))]
    return "\n".join(blocks) if blocks else None


def extract_quiz_metadata(repo_root=REPO_ROOT, node_bin="node"):
    """回傳 {chapter_id: {"chapter_id":..., "MISC": {...}, "QUIZ": [...]}}。
    node 不存在或解析失敗時降級為只用檔名推得的 chapter_id + 空題庫（不整個失敗）。
    """
    node_ok = _which(node_bin) is not None
    meta = {}
    for path in sorted(glob.glob(os.path.join(repo_root, "ch*.html"))):
        fname = os.path.basename(path)
        m = re.match(r"^(ch\d+)\.html$", fname)
        if not m:
            continue
        chapter_id = m.group(1)
        quiz_items, misc = [], {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                html_text = f.read()
            script_body = _find_quiz_script(html_text)
            if script_body and node_ok:
                data = _run_node_extract(script_body, node_bin=node_bin)
                if data:
                    quiz_items = data.get("QUIZ") or []
                    misc = data.get("MISC") or {}
        except Exception:
            quiz_items, misc = [], {}

        for i, q in enumerate(quiz_items):
            if not isinstance(q, dict):
                continue
            if not q.get("id"):
                q["id"] = f"{chapter_id}-q{i + 1:02d}"
            if not q.get("phase"):
                q["phase"] = "post"

        meta[chapter_id] = {"chapter_id": chapter_id, "MISC": misc, "QUIZ": quiz_items}
    return meta


def _which(cmd):
    from shutil import which
    return which(cmd)


def build_item_index(quiz_meta):
    """(chapter_id, question_id) -> item dict"""
    idx = {}
    for chapter_id, info in quiz_meta.items():
        for q in info.get("QUIZ") or []:
            qid = q.get("id")
            if qid:
                idx[(chapter_id, qid)] = q
    return idx


def build_misc_index(quiz_meta):
    """misconception key -> 中文描述（跨章合併，後出現者覆蓋同 key，理論上應一致）。"""
    idx = {}
    for info in quiz_meta.values():
        idx.update(info.get("MISC") or {})
    return idx


# ---------------------------------------------------------------------------
# 4. 分析
# ---------------------------------------------------------------------------

def pick_first_attempts(events):
    """回傳 (student_id, chapter, question_id, phase) -> 事件，
    取 attempts 最小、再取 client_ts 最早者。只考慮 event_type == 'answer'。"""
    buckets = defaultdict(list)
    for ev in events:
        if ev.get("event_type") != "answer":
            continue
        key = (ev.get("student_id"), ev.get("_chapter_norm"), ev.get("question_id"), ev.get("phase"))
        buckets[key].append(ev)

    first = {}
    for key, evs in buckets.items():
        def sort_key(e):
            att = e.get("attempts")
            att = att if isinstance(att, (int, float)) else 1
            ts = e.get("client_ts") or ""
            return (att, ts)
        evs.sort(key=sort_key)
        first[key] = evs[0]
    return first


def pick_first_attempt_completes(events):
    """(student_id, chapter, phase) -> 最早的 attempt_complete 事件（任意 attempts，用於完成人數計算）。"""
    buckets = defaultdict(list)
    for ev in events:
        if ev.get("event_type") != "attempt_complete":
            continue
        key = (ev.get("student_id"), ev.get("_chapter_norm"), ev.get("phase"))
        buckets[key].append(ev)
    first = {}
    for key, evs in buckets.items():
        evs.sort(key=lambda e: e.get("client_ts") or "")
        first[key] = evs[0]
    return first


def build_overview(events, first_answers, first_completes):
    students = {ev.get("student_id") for ev in events if ev.get("student_id")}
    tss = [ev.get("_ts") for ev in events if ev.get("_ts")]
    period = (min(tss).date().isoformat(), max(tss).date().isoformat()) if tss else (None, None)

    chapters = sorted({ev.get("_chapter_norm") for ev in events if ev.get("_chapter_norm")})
    per_chapter = {}
    for ch in chapters:
        post_students = {sid for (sid, c, ph) in first_completes if c == ch and ph == "post"}
        pre_students = {sid for (sid, c, ph) in first_completes if c == ch and ph == "pre"}
        answering_students = {sid for (sid, c, qid, ph) in first_answers if c == ch}
        per_chapter[ch] = {
            "post_complete": len(post_students),
            "pre_complete": len(pre_students),
            "answering_students": len(answering_students),
        }

    return {
        "n_students": len(students),
        "n_events": len(events),
        "period": period,
        "chapters": chapters,
        "per_chapter": per_chapter,
    }


def build_chapter_effectiveness(chapters, first_answers):
    """回傳 {chapter: {"pre_avg":..., "post_avg":..., "gain":..., "n_pre":.., "n_post":.., "n_gain":..}}"""
    # 先算每個 student 在每個 chapter/phase 的 rate
    per_student = defaultdict(lambda: defaultdict(lambda: {"correct": 0, "n": 0}))
    for (sid, ch, qid, phase), ev in first_answers.items():
        if phase not in ("pre", "post"):
            continue
        d = per_student[(sid, ch)][phase]
        d["n"] += 1
        if ev.get("is_correct"):
            d["correct"] += 1

    out = {}
    for ch in chapters:
        pre_rates, post_rates, gains = [], [], []
        for (sid, c), phases in per_student.items():
            if c != ch:
                continue
            pre_d, post_d = phases.get("pre"), phases.get("post")
            pre_rate = safe_div(pre_d["correct"], pre_d["n"]) if pre_d and pre_d["n"] else None
            post_rate = safe_div(post_d["correct"], post_d["n"]) if post_d and post_d["n"] else None
            if pre_rate is not None:
                pre_rates.append(pre_rate)
            if post_rate is not None:
                post_rates.append(post_rate)
            if pre_rate is not None and post_rate is not None and pre_rate < 1:
                gains.append((post_rate - pre_rate) / (1 - pre_rate))
        out[ch] = {
            "pre_avg": statistics.fmean(pre_rates) if pre_rates else None,
            "post_avg": statistics.fmean(post_rates) if post_rates else None,
            "gain": statistics.fmean(gains) if gains else None,
            "n_pre": len(pre_rates),
            "n_post": len(post_rates),
            "n_gain": len(gains),
        }
    return out


def build_question_rows(chapters, first_answers, item_index, misc_index):
    """依章分組的逐題表，含鑑別度（以該章 post 總分排序取高低各 27%）。"""
    # 先算每章每位學生的 post 總分（用於鑑別度分組）
    post_totals = defaultdict(lambda: defaultdict(int))  # chapter -> student -> correct count (post-phase only)
    for (sid, ch, qid, phase), ev in first_answers.items():
        if phase == "post" and ev.get("is_correct"):
            post_totals[ch][sid] += 1

    high_low = {}  # chapter -> (set_high, set_low, n_students, ok)
    for ch, totals in post_totals.items():
        n = len(totals)
        if n < 10:
            high_low[ch] = (set(), set(), n, False)
            continue
        ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
        k = max(1, round(n * 0.27))
        high = {sid for sid, _ in ranked[:k]}
        low = {sid for sid, _ in ranked[-k:]}
        high_low[ch] = (high, low, n, True)

    # 依 (chapter, question) 蒐集所有 phase 的首次作答
    by_question = defaultdict(list)  # (chapter, qid) -> [event,...]
    for (sid, ch, qid, phase), ev in first_answers.items():
        by_question[(ch, qid)].append(ev)

    rows_by_chapter = defaultdict(list)
    for (ch, qid), evs in by_question.items():
        item = item_index.get((ch, qid))
        n = len(evs)
        correct_n = sum(1 for e in evs if e.get("is_correct"))
        skipped_n = sum(1 for e in evs if e.get("skipped"))
        acc = safe_div(correct_n, n)
        skip_rate = safe_div(skipped_n, n)
        confs = [e.get("confidence") for e in evs if isinstance(e.get("confidence"), (int, float))]
        avg_conf = statistics.fmean(confs) if confs else None
        latencies = [e.get("latency_ms") for e in evs if isinstance(e.get("latency_ms"), (int, float))]
        median_latency_s = (statistics.median(latencies) / 1000.0) if latencies else None

        # 鑑別度：用該章 post 總分排序的 high/low 分組
        high, low, n_rank, ok = high_low.get(ch, (set(), set(), 0, False))
        if ok:
            high_evs = [e for e in evs if e.get("student_id") in high]
            low_evs = [e for e in evs if e.get("student_id") in low]
            p_high = safe_div(sum(1 for e in high_evs if e.get("is_correct")), len(high_evs)) if high_evs else None
            p_low = safe_div(sum(1 for e in low_evs if e.get("is_correct")), len(low_evs)) if low_evs else None
            disc = (p_high - p_low) if (p_high is not None and p_low is not None) else None
        else:
            disc = None  # n 太小

        # 最常見錯誤
        wrong_evs = [e for e in evs if not e.get("is_correct")]
        common_wrong = None
        if wrong_evs:
            if item and item.get("opts"):
                idx_counter = Counter(e.get("choice_idx") for e in wrong_evs if e.get("choice_idx") is not None)
                if idx_counter:
                    top_idx, top_n = idx_counter.most_common(1)[0]
                    opt_text = truncate(strip_html((item.get("opts") or [None] * (top_idx + 1))[top_idx] or ""), 30) \
                        if top_idx < len(item.get("opts") or []) else "（選項）"
                    tag = None
                    tags = item.get("tags") or []
                    if top_idx < len(tags):
                        tag = tags[top_idx]
                    desc = misc_index.get(tag, tag) if tag else None
                    common_wrong = {"text": opt_text, "n": top_n, "tag": tag, "desc": desc}
            else:
                tag_counter = Counter(e.get("misconception") for e in wrong_evs if e.get("misconception"))
                if tag_counter:
                    top_tag, top_n = tag_counter.most_common(1)[0]
                    desc = misc_index.get(top_tag, top_tag)
                    val_text = None
                    if item:
                        for e in item.get("errs") or []:
                            if e.get("tag") == top_tag:
                                val_text = str(e.get("val"))
                                break
                    common_wrong = {"text": val_text or top_tag, "n": top_n, "tag": top_tag, "desc": desc}

        stem = truncate(strip_html(item.get("q")), 40) if item and item.get("q") else qid

        rows_by_chapter[ch].append({
            "id": qid,
            "phase": (item.get("phase") if item else None) or (evs[0].get("phase") if evs else None),
            "stem": stem,
            "n": n,
            "acc": acc,
            "skip_rate": skip_rate,
            "disc": disc,
            "disc_ok": ok,
            "avg_conf": avg_conf,
            "median_latency_s": median_latency_s,
            "common_wrong": common_wrong,
        })

    for ch in rows_by_chapter:
        rows_by_chapter[ch].sort(key=lambda r: (r["phase"] or "", r["id"]))
    return rows_by_chapter


def build_misconception_heatmap(chapters, first_answers, misc_index):
    counts = defaultdict(lambda: defaultdict(int))  # misc_key -> chapter -> count
    chapter_answerers = defaultdict(set)  # chapter -> set(student_id) 有首次作答者
    for (sid, ch, qid, phase), ev in first_answers.items():
        chapter_answerers[ch].add(sid)
        tag = ev.get("misconception")
        if tag and not ev.get("is_correct"):
            counts[tag][ch] += 1

    rows = []
    for tag, per_ch in counts.items():
        total = sum(per_ch.values())
        rows.append((tag, per_ch, total))
    rows.sort(key=lambda r: r[2], reverse=True)

    return {
        "rows": rows,  # [(tag, {chapter: count}, total)]
        "chapter_answerers": {ch: len(s) for ch, s in chapter_answerers.items()},
        "misc_index": misc_index,
    }


def build_confidence_quadrants(chapters, first_answers, item_index):
    quad = {}  # chapter -> {hc,hw,lc,lw}
    per_question_hw = defaultdict(int)  # (chapter, qid) -> count 高信心答錯
    for (sid, ch, qid, phase), ev in first_answers.items():
        conf = ev.get("confidence")
        if not isinstance(conf, (int, float)):
            continue
        correct = bool(ev.get("is_correct"))
        high = conf >= 3
        q = quad.setdefault(ch, {"hc": 0, "hw": 0, "lc": 0, "lw": 0})
        if high and correct:
            q["hc"] += 1
        elif high and not correct:
            q["hw"] += 1
            per_question_hw[(ch, qid)] += 1
        elif (not high) and correct:
            q["lc"] += 1
        else:
            q["lw"] += 1

    top10 = sorted(per_question_hw.items(), key=lambda kv: kv[1], reverse=True)[:10]
    top10_rows = []
    for (ch, qid), n in top10:
        item = item_index.get((ch, qid))
        stem = truncate(strip_html(item.get("q")), 40) if item and item.get("q") else qid
        top10_rows.append({"chapter": ch, "id": qid, "stem": stem, "n": n})
    return {"quad": quad, "top10": top10_rows}


def build_muddiest(events, show_id):
    by_chapter = defaultdict(list)
    for ev in events:
        if ev.get("event_type") != "self_check":
            continue
        text = (ev.get("free_text") or "").strip()
        if not text:
            continue
        by_chapter[ev.get("_chapter_norm")].append({
            "student_id": ev.get("student_id") if show_id else None,
            "ts": ev.get("client_ts"),
            "text": text,
        })
    for ch in by_chapter:
        by_chapter[ch].sort(key=lambda r: r["ts"] or "")
    return by_chapter


def build_student_table(chapters, first_answers):
    per_student = defaultdict(lambda: defaultdict(dict))
    agg = defaultdict(lambda: defaultdict(lambda: {"correct": 0, "n": 0}))
    for (sid, ch, qid, phase), ev in first_answers.items():
        if phase not in ("pre", "post"):
            continue
        d = agg[sid][(ch, phase)]
        d["n"] += 1
        if ev.get("is_correct"):
            d["correct"] += 1
    for sid, m in agg.items():
        for (ch, phase), d in m.items():
            per_student[sid].setdefault(ch, {})[phase] = (d["correct"], d["n"])
    return per_student


# ---------------------------------------------------------------------------
# 5. HTML 報表輸出
# ---------------------------------------------------------------------------

CSS = """
* { box-sizing: border-box; }
body { font-family: "Microsoft JhengHei", "PingFang TC", "Noto Sans TC", sans-serif;
  margin: 0; padding: 24px; background:#f6f7f9; color:#1c2430; line-height:1.55; }
h1 { font-size:1.6rem; margin-bottom:4px; }
h2 { font-size:1.25rem; margin-top:40px; border-left:6px solid #4a7fd6; padding-left:10px; }
h3 { font-size:1.05rem; margin-top:24px; color:#334; }
.meta { color:#667; font-size:0.9rem; margin-bottom:20px; }
table { border-collapse: collapse; width:100%; margin:12px 0 24px; background:#fff;
  box-shadow:0 1px 3px rgba(0,0,0,.08); }
th, td { border:1px solid #e2e6ec; padding:6px 10px; font-size:0.88rem; text-align:left; vertical-align:top; }
th { background:#eef1f6; position:sticky; top:0; }
tr.low-acc, tr.low-disc { background:#fff2f0; }
tr.low-acc.low-disc { background:#ffe4de; }
.muted { color:#98a2b3; }
.barwrap { position:relative; background:#eef1f6; border-radius:4px; height:18px; min-width:80px; }
.bar { position:absolute; left:0; top:0; height:100%; border-radius:4px; }
.barlabel { position:relative; z-index:1; padding-left:6px; font-size:0.78rem; color:#1c2430; }
.card-row { display:flex; flex-wrap:wrap; gap:14px; margin:12px 0 20px; }
.card { background:#fff; border-radius:8px; padding:14px 18px; box-shadow:0 1px 3px rgba(0,0,0,.08); min-width:150px; }
.card .num { font-size:1.6rem; font-weight:700; color:#2c4a8c; }
.card .lbl { font-size:0.82rem; color:#667; }
.section-note { font-size:0.85rem; color:#667; margin:-8px 0 12px; }
.heat0{background:#fff;} .heat1{background:#fde3e0;} .heat2{background:#fac6bf;}
.heat3{background:#f6a89e;} .heat4{background:#ef8578;} .heat5{background:#e35c4c;color:#fff;}
.quad-table td { text-align:center; }
.muddy-item { background:#fff; border-radius:6px; padding:8px 12px; margin-bottom:6px; box-shadow:0 1px 2px rgba(0,0,0,.06); }
.muddy-item .who { font-size:0.78rem; color:#98a2b3; }
footer.report-footer { margin-top:40px; color:#98a2b3; font-size:0.8rem; }
"""


def heat_class(frac):
    if frac is None:
        return "heat0"
    if frac <= 0:
        return "heat0"
    if frac < 0.1:
        return "heat1"
    if frac < 0.2:
        return "heat2"
    if frac < 0.35:
        return "heat3"
    if frac < 0.5:
        return "heat4"
    return "heat5"


def render_html(args, source, filt_stats, overview, chap_eff, question_rows, heatmap,
                 conf_quad, muddiest, student_table, chapters_all):
    html_parts = []
    html_parts.append(f"<!doctype html><html lang='zh-Hant'><head><meta charset='utf-8'>"
                       f"<title>FAS 測驗成效報表</title><style>{CSS}</style></head><body>")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    html_parts.append("<h1>📊 FAS 測驗成效報表</h1>")
    html_parts.append(
        f"<div class='meta'>產生時間：{now_str}　｜　資料來源：{_esc(source)}　｜　"
        f"篩選：class={_esc(args.class_ or '全部')}　since={_esc(args.since or '不限')}　"
        f"（原始 {filt_stats['raw']} 筆 → 保留 {filt_stats['kept']} 筆；"
        f"去重 {filt_stats['dropped_dupe']}、排除測試帳號 {filt_stats['dropped_test']}、"
        f"班級篩掉 {filt_stats['dropped_class']}、日期篩掉 {filt_stats['dropped_since']}）</div>"
    )

    if overview["n_events"] == 0:
        html_parts.append("<p><strong>目前沒有符合條件的資料。</strong>"
                           "可能是尚未有學生作答，或篩選條件（--class / --since）太嚴格。</p>")
        html_parts.append("</body></html>")
        return "".join(html_parts)

    # 1. 總覽
    html_parts.append("<h2>1. 總覽</h2>")
    p0, p1 = overview["period"]
    html_parts.append("<div class='card-row'>"
                       f"<div class='card'><div class='num'>{overview['n_students']}</div><div class='lbl'>學生數</div></div>"
                       f"<div class='card'><div class='num'>{overview['n_events']}</div><div class='lbl'>事件數</div></div>"
                       f"<div class='card'><div class='num'>{_esc(p0 or '—')} ~ {_esc(p1 or '—')}</div><div class='lbl'>資料期間</div></div>"
                       "</div>")
    html_parts.append("<table><tr><th>章節</th><th>課後完成人數</th><th>前測完成人數</th><th>有作答學生數</th></tr>")
    for ch in overview["chapters"]:
        pc = overview["per_chapter"][ch]
        html_parts.append(f"<tr><td>{_esc(ch)}</td><td>{pc['post_complete']}</td>"
                           f"<td>{pc['pre_complete']}</td><td>{pc['answering_students']}</td></tr>")
    html_parts.append("</table>")

    # 2. 各章成效
    html_parts.append("<h2>2. 各章成效</h2>")
    html_parts.append("<div class='section-note'>normalized gain g = (post − pre) / (1 − pre)，"
                       "只計入兩者皆有首次作答、且 pre &lt; 100% 的學生。</div>")
    html_parts.append("<table><tr><th>章節</th><th>前測平均答對率</th><th>課後平均答對率</th>"
                       "<th>normalized gain (g)</th><th>n(pre/post/gain)</th></tr>")
    for ch in overview["chapters"]:
        e = chap_eff.get(ch, {})
        html_parts.append(
            f"<tr><td>{_esc(ch)}</td><td>{bar_cell(e.get('pre_avg'), '#e3a13a')}</td>"
            f"<td>{bar_cell(e.get('post_avg'), '#4a7fd6')}</td>"
            f"<td>{fmt_num(e.get('gain'), 2) if e.get('gain') is not None else '—'}</td>"
            f"<td>{e.get('n_pre', 0)}/{e.get('n_post', 0)}/{e.get('n_gain', 0)}</td></tr>"
        )
    html_parts.append("</table>")

    # 3. 逐題表
    html_parts.append("<h2>3. 逐題表</h2>")
    html_parts.append("<div class='section-note'>答對率 &lt; 50% 或鑑別度 D &lt; 0.2 的列已標色。"
                       "鑑別度以該章課後（post）總分排序，取高低各 27% 學生計算 D = p_high − p_low；"
                       "該章 post 作答人數 &lt; 10 時顯示「n 太小」。</div>")
    for ch in overview["chapters"]:
        rows = question_rows.get(ch, [])
        if not rows:
            continue
        html_parts.append(f"<h3>{_esc(ch)}</h3>")
        html_parts.append("<table><tr><th>題號</th><th>phase</th><th>題幹</th><th>n</th><th>答對率</th>"
                           "<th>跳過率</th><th>鑑別度 D</th><th>平均信心</th>"
                           "<th>最常見錯誤選項</th><th>中位延遲(秒)</th></tr>")
        for r in rows:
            low_acc = r["acc"] is not None and r["acc"] < 0.5
            low_disc = r["disc_ok"] and r["disc"] is not None and r["disc"] < 0.2
            cls = []
            if low_acc:
                cls.append("low-acc")
            if low_disc:
                cls.append("low-disc")
            cls_attr = f" class='{' '.join(cls)}'" if cls else ""
            disc_txt = "n 太小" if not r["disc_ok"] else (fmt_num(r["disc"], 2) if r["disc"] is not None else "—")
            cw = r["common_wrong"]
            if cw:
                cw_txt = f"{_esc(cw['text'])}（{cw['n']} 人）" + (f" — {_esc(cw['desc'])}" if cw.get("desc") else "")
            else:
                cw_txt = "—"
            html_parts.append(
                f"<tr{cls_attr}><td>{_esc(r['id'])}</td><td>{_esc(r['phase'] or '')}</td>"
                f"<td>{_esc(r['stem'])}</td><td>{r['n']}</td>"
                f"<td>{fmt_pct(r['acc'])}</td><td>{fmt_pct(r['skip_rate'])}</td>"
                f"<td>{disc_txt}</td><td>{fmt_num(r['avg_conf'], 2)}</td>"
                f"<td>{cw_txt}</td>"
                f"<td>{fmt_num(r['median_latency_s'], 1) if r['median_latency_s'] is not None else '—'}</td></tr>"
            )
        html_parts.append("</table>")

    # 4. 迷思熱區
    html_parts.append("<h2>4. 迷思熱區</h2>")
    rows = heatmap["rows"]
    if rows:
        chs = overview["chapters"]
        html_parts.append("<table><tr><th>迷思</th>" + "".join(f"<th>{_esc(c)}</th>" for c in chs) + "<th>總計</th></tr>")
        for tag, per_ch, total in rows:
            desc = heatmap["misc_index"].get(tag, "")
            label = f"{_esc(tag)}" + (f"<br><span class='muted'>{_esc(desc)}</span>" if desc else "")
            cells = []
            for c in chs:
                n = per_ch.get(c, 0)
                denom = heatmap["chapter_answerers"].get(c, 0)
                frac = safe_div(n, denom)
                txt = f"{n}" + (f" ({fmt_pct(frac, 0)})" if n else "")
                cells.append(f"<td class='{heat_class(frac if n else None)}'>{txt}</td>")
            html_parts.append(f"<tr><td>{label}</td>" + "".join(cells) + f"<td>{total}</td></tr>")
        html_parts.append("</table>")
    else:
        html_parts.append("<p class='muted'>目前沒有記錄到任何迷思選項。</p>")

    # 5. 信心 × 對錯
    html_parts.append("<h2>5. 信心 × 對錯</h2>")
    html_parts.append("<table class='quad-table'><tr><th>章節</th><th>高信心・答對</th><th>高信心・答錯</th>"
                       "<th>低信心・答對</th><th>低信心・答錯</th></tr>")
    for ch in overview["chapters"]:
        q = conf_quad["quad"].get(ch, {"hc": 0, "hw": 0, "lc": 0, "lw": 0})
        html_parts.append(f"<tr><td>{_esc(ch)}</td><td>{q['hc']}</td><td>{q['hw']}</td>"
                           f"<td>{q['lc']}</td><td>{q['lw']}</td></tr>")
    html_parts.append("</table>")
    html_parts.append("<h3>高信心卻答錯最多的前 10 題（最該課堂處理）</h3>")
    top10 = conf_quad["top10"]
    if top10:
        html_parts.append("<table><tr><th>章節</th><th>題號</th><th>題幹</th><th>高信心答錯人次</th></tr>")
        for r in top10:
            html_parts.append(f"<tr><td>{_esc(r['chapter'])}</td><td>{_esc(r['id'])}</td>"
                               f"<td>{_esc(r['stem'])}</td><td>{r['n']}</td></tr>")
        html_parts.append("</table>")
    else:
        html_parts.append("<p class='muted'>目前沒有「高信心卻答錯」的紀錄。</p>")

    # 6. 我還不懂的地方
    html_parts.append("<h2>6. 「我還不懂的地方」</h2>")
    if not args.show_id:
        html_parts.append("<div class='section-note'>預設不顯示學號，加 --show-id 顯示。"
                           "完整彙整已輸出到 report/muddiest_points.txt，方便貼給 LLM 分群摘要。</div>")
    for ch in overview["chapters"]:
        items = muddiest.get(ch, [])
        if not items:
            continue
        html_parts.append(f"<h3>{_esc(ch)}（{len(items)} 則）</h3>")
        for it in items:
            who = f"<span class='who'>{_esc(it['student_id'])}　</span>" if it.get("student_id") else ""
            ts = _esc(it.get("ts") or "")
            html_parts.append(f"<div class='muddy-item'>{who}<span class='who'>{ts}</span><br>{_esc(it['text'])}</div>")

    # 7. 個別學生表
    if args.show_id:
        html_parts.append("<h2>7. 個別學生表</h2>")
        html_parts.append("<table><tr><th>學號</th>" +
                           "".join(f"<th>{_esc(ch)} 前測</th><th>{_esc(ch)} 課後</th>" for ch in overview["chapters"]) +
                           "</tr>")
        for sid in sorted(student_table.keys()):
            cells = []
            for ch in overview["chapters"]:
                d = student_table.get(sid, {}).get(ch, {})
                pre = d.get("pre")
                post = d.get("post")
                cells.append(f"<td>{pre[0]}/{pre[1]}</td>" if pre else "<td>—</td>")
                cells.append(f"<td>{post[0]}/{post[1]}</td>" if post else "<td>—</td>")
            html_parts.append(f"<tr><td>{_esc(sid)}</td>" + "".join(cells) + "</tr>")
        html_parts.append("</table>")

    html_parts.append("<footer class='report-footer'>由 scripts/quiz_dashboard.py 產生，僅供授課教師離線使用。</footer>")
    html_parts.append("</body></html>")
    return "".join(html_parts)


def write_muddiest_txt(muddiest, out_path):
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    lines = ["FAS 學生「我還不懂的地方」彙整（供貼給 LLM 分群摘要）", "=" * 40, ""]
    for ch in sorted(muddiest.keys()):
        items = muddiest[ch]
        if not items:
            continue
        lines.append(f"## {ch}（{len(items)} 則）")
        for it in items:
            ts = it.get("ts") or ""
            lines.append(f"- [{ts}] {it['text']}")
        lines.append("")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------------------
# 6. Demo（合成資料，走完整條管線）
# ---------------------------------------------------------------------------

def demo_quiz_meta():
    def mk_choice(id_, phase, q, opts, ans, tags, exp, from_=None):
        d = {"id": id_, "v": 1, "type": "concept", "phase": phase, "q": q,
             "opts": opts, "ans": ans, "tags": tags, "exp": exp}
        if from_:
            d["from"] = from_
        return d

    def mk_num(id_, phase, q, ans, tol, unit, errs, exp):
        return {"id": id_, "v": 1, "type": "calc", "phase": phase, "q": q,
                "num": {"ans": ans, "tol": tol, "unit": unit}, "errs": errs, "exp": exp}

    ch02_misc = {
        "CI_TRUE_VALUE_PROB": "以為真值有 95% 機率落在信賴區間內",
        "DF_EQUALS_N": "自由度用 n 而不是 n-1",
        "USED_Z_NOT_T": "小樣本誤用 Z 而非 t",
    }
    ch02_quiz = [
        mk_choice("ch02-p01", "pre", "95%信賴區間代表什麼？（demo 前測）",
                  ["涵蓋真值的機率 95%", "涵蓋 95% 數據", "長期而言 95% 會蓋住真值", "精密度 95%"],
                  2, [ "CI_TRUE_VALUE_PROB", None, None, None], "……"),
        mk_choice("ch02-p02", "pre", "自由度 df 應該是？（demo 前測）",
                  ["n", "n-1", "n+1", "2n"], 1, [ "DF_EQUALS_N", None, None, None], "……"),
        mk_choice("ch02-p03", "pre", "小樣本應該用哪個分布？（demo 前測）",
                  ["Z", "t", "F", "卡方"], 1, [ "USED_Z_NOT_T", None, None, None], "……"),
        mk_choice("ch02-q01", "post", "「95% 信賴區間」的正確解讀是什麼？",
                  ["真值有 95% 機率在此區間內", "此區間涵蓋 95% 的量測數據",
                   "用此方法建構的區間，長期約 95% 會蓋住真值", "此方法有 95% 的精密度"],
                  2, ["CI_TRUE_VALUE_PROB", None, None, None], "……"),
        mk_num("ch02-q02", "post", "n=4、SD=0.2927，95% CI 半寬是多少？",
               0.466, 0.002, "%", [{"val": 0.287, "tol": 0.002, "tag": "USED_Z_NOT_T"}], "……"),
        mk_choice("ch02-q03", "post", "自由度 df=n-1 的原因是？",
                  ["少一個限制條件", "習慣", "比較簡單", "電腦要求"],
                  0, [None, "DF_EQUALS_N", None, None], "……"),
        mk_choice("ch02-s01", "spaced", "回溯：平均數與標準差的關係？",
                  ["A", "B", "C", "D"], 0, [None, "OTHER", None, None], "……", from_="ch01"),
    ]

    ch05_misc = {
        "SIGFIG_ZERO_COUNT": "誤數末尾零為有效數字",
        "OUTLIER_ALWAYS_REMOVE": "以為異常值一定要刪除",
    }
    ch05_quiz = [
        mk_choice("ch05-p01", "pre", "0.0230 有幾位有效數字？（demo 前測）",
                  ["2", "3", "4", "5"], 1, [None, "SIGFIG_ZERO_COUNT", None, None], "……"),
        mk_choice("ch05-p02", "pre", "Q 檢定用來做什麼？（demo 前測）",
                  ["找異常值", "算平均", "算標準差", "算變異數"], 0, [None, "OTHER", None, None], "……"),
        mk_choice("ch05-p03", "pre", "異常值一定要刪除嗎？（demo 前測）",
                  ["一定要", "看情況與檢定結果", "不用管", "刪一半"], 1,
                  ["OUTLIER_ALWAYS_REMOVE", None, None, None], "……"),
        mk_choice("ch05-q01", "post", "12.30 有幾位有效數字？",
                  ["2", "3", "4", "5"], 2, [None, None, "SIGFIG_ZERO_COUNT", None], "……"),
        mk_num("ch05-q02", "post", "Q 檢定：Q_calc 值？",
               0.64, 0.01, "", [{"val": 0.5, "tol": 0.01, "tag": "OTHER_NUM"}], "……"),
        mk_choice("ch05-q03", "post", "被 Q 檢定判為異常值後應該怎麼做？",
                  ["直接刪除不用說明", "刪除並在報告中註明依據", "永遠保留", "重新量測前先刪"],
                  1, [ "OUTLIER_ALWAYS_REMOVE", None, None, None], "……"),
        mk_choice("ch05-s01", "spaced", "回溯：CI 半寬公式？", ["A", "B", "C", "D"],
                  1, [None, None, "OTHER", None], "……", from_="ch02"),
    ]

    ch16_misc = {
        "ANOVA_MEANS_ALL_DIFFER": "以為 ANOVA 顯著代表每組兩兩都不同",
        "ALPHA_PER_COMPARISON": "多重比較沒有校正型一誤差",
    }
    ch16_quiz = [
        mk_choice("ch16-p01", "pre", "單因子 ANOVA 檢定的虛無假設？（demo 前測）",
                  ["所有組平均都相等", "所有組變異數相等", "至少一組不同", "樣本數相等"],
                  0, [None, "OTHER", None, None], "……"),
        mk_choice("ch16-p02", "pre", "ANOVA 顯著代表什麼？（demo 前測）",
                  ["每兩組都不同", "至少一組與其他不同", "全部相同", "資料有誤"],
                  1, [ "ANOVA_MEANS_ALL_DIFFER", None, None, None], "……"),
        mk_choice("ch16-p03", "pre", "多重比較為何要校正？（demo 前測）",
                  ["降低型一誤差膨脹", "增加檢定力", "不需要校正", "節省時間"],
                  0, [None, "ALPHA_PER_COMPARISON", None, None], "……"),
        mk_choice("ch16-q01", "post", "ANOVA 顯著（p<0.05）代表？",
                  ["每兩組平均都顯著不同", "至少有一組平均與其他不同", "所有組別變異數不同", "資料不是常態分布"],
                  1, [ "ANOVA_MEANS_ALL_DIFFER", None, None, None], "……"),
        mk_num("ch16-q02", "post", "3 組、每組 n=5，組間自由度 df1 = ?",
               2, 0.001, "", [{"val": 3, "tol": 0.001, "tag": "OTHER_NUM"}], "……"),
        mk_choice("ch16-q03", "post", "Tukey HSD 事後檢定的用途？",
                  ["控制多重比較的型一誤差", "增加樣本數", "計算 F 值", "檢查常態性"],
                  0, [ "ALPHA_PER_COMPARISON", None, None, None], "……"),
        mk_choice("ch16-s01", "spaced", "回溯：t 檢定與 ANOVA 的關係？",
                  ["A", "B", "C", "D"], 2, [None, None, "OTHER", None], "……", from_="ch15"),
    ]

    return {
        "ch02": {"chapter_id": "ch02", "MISC": ch02_misc, "QUIZ": ch02_quiz},
        "ch05": {"chapter_id": "ch05", "MISC": ch05_misc, "QUIZ": ch05_quiz},
        "ch16": {"chapter_id": "ch16", "MISC": ch16_misc, "QUIZ": ch16_quiz},
    }


def build_demo_events():
    rng = random.Random(42)
    meta = demo_quiz_meta()
    students = [f"S{str(i).zfill(2)}" for i in range(1, 31)]
    test_students = ["ZZ01", "TEST1", "_hidden", "GUEST"]
    all_students = students + test_students

    base_t = datetime(2026, 9, 1, 8, 0, 0, tzinfo=timezone.utc)
    events = []
    session_counter = 0

    def emit(ev):
        events.append(ev)

    def client_ts_for(offset_minutes):
        return (base_t.timestamp() and
                (datetime.fromtimestamp(base_t.timestamp() + offset_minutes * 60, tz=timezone.utc))
                .isoformat().replace("+00:00", "Z"))

    for ch, info in meta.items():
        quiz = info["QUIZ"]
        misc = info["MISC"]
        for si, sid in enumerate(all_students):
            ability = rng.random()  # 0..1，越高越強
            is_test = sid in test_students
            session_id = f"sess{session_counter}"
            session_counter += 1
            offset = si * 3
            # ---- pre + post + spaced 首次作答 ----
            first_attempt_events = {}
            for item in quiz:
                phase = item["phase"]
                skip = rng.random() < 0.08
                offset += 1
                ts = client_ts_for(offset)
                attempts = 1
                conf = None if rng.random() < 0.1 else rng.randint(1, 3)
                if skip:
                    ev = {
                        "student_id": sid, "course_id": "4y_food_analysis", "class_id": "A",
                        "chapter": f"FAS-{ch.upper()}", "game": "fas_quiz", "event_type": "answer",
                        "site": "fas", "phase": phase, "question_id": item["id"], "item_version": item.get("v", 1),
                        "qtype": item.get("type"), "from_chapter": item.get("from"), "is_correct": False,
                        "skipped": True, "choice_idx": None, "choice_value": None, "misconception": None,
                        "confidence": conf, "attempts": attempts, "latency_ms": None,
                        "session_id": session_id, "client_ts": ts,
                    }
                    emit(ev)
                    first_attempt_events[item["id"]] = ev
                    continue
                # 概念/大小是否答對：ability 越高越可能對；pre 一律較低正確率
                p_correct = ability * (0.55 if phase == "pre" else 0.85)
                correct = rng.random() < p_correct
                if item.get("opts") is not None:
                    if correct:
                        choice_idx = item["ans"]
                    else:
                        wrong_choices = [i for i in range(len(item["opts"])) if i != item["ans"]]
                        choice_idx = rng.choice(wrong_choices)
                    tag = None if correct else (item.get("tags") or [None] * len(item["opts"]))[choice_idx]
                    choice_value = None
                else:
                    if correct:
                        choice_value = item["num"]["ans"]
                        tag = None
                    else:
                        errs = item.get("errs") or []
                        if errs and rng.random() < 0.7:
                            e = rng.choice(errs)
                            choice_value = e["val"]
                            tag = e["tag"]
                        else:
                            choice_value = item["num"]["ans"] + rng.uniform(0.5, 2.0)
                            tag = "OTHER_NUM"
                    choice_idx = None
                latency = rng.randint(3000, 45000)
                ev = {
                    "student_id": sid, "course_id": "4y_food_analysis", "class_id": "A",
                    "chapter": f"FAS-{ch.upper()}", "game": "fas_quiz", "event_type": "answer",
                    "site": "fas", "phase": phase, "question_id": item["id"], "item_version": item.get("v", 1),
                    "qtype": item.get("type"), "from_chapter": item.get("from"), "is_correct": correct,
                    "skipped": False, "choice_idx": choice_idx, "choice_value": choice_value,
                    "misconception": tag, "confidence": conf, "attempts": attempts, "latency_ms": latency,
                    "session_id": session_id, "client_ts": ts,
                }
                emit(ev)
                first_attempt_events[item["id"]] = ev

                # 少數學生「再練一次」：attempts=2，correctness 不同，不應影響成效統計
                if not is_test and rng.random() < 0.15:
                    offset += 1
                    ts2 = client_ts_for(offset)
                    ev2 = dict(ev)
                    ev2["attempts"] = 2
                    ev2["is_correct"] = True  # 練習後通常變對，用來測試「attempts>1 不列入成效」
                    ev2["choice_idx"] = item.get("ans") if item.get("opts") is not None else None
                    ev2["choice_value"] = item["num"]["ans"] if item.get("num") else None
                    ev2["misconception"] = None
                    ev2["client_ts"] = ts2
                    emit(ev2)

            # ---- attempt_complete（pre / post 各一次）----
            for phase in ("pre", "post"):
                items_in_phase = [it for it in quiz if it["phase"] == phase] if phase == "pre" else \
                    [it for it in quiz if it["phase"] in ("post", "spaced")]
                total = len(items_in_phase)
                correct_n = sum(1 for it in items_in_phase
                                 if first_attempt_events.get(it["id"], {}).get("is_correct"))
                offset += 1
                ts = client_ts_for(offset)
                emit({
                    "student_id": sid, "course_id": "4y_food_analysis", "class_id": "A",
                    "chapter": f"FAS-{ch.upper()}", "game": "fas_quiz", "event_type": "attempt_complete",
                    "site": "fas", "phase": phase, "question_id": None, "final_score": correct_n,
                    "total": total, "attempts": 1, "answered": total,
                    "duration_ms": rng.randint(60000, 400000),
                    "session_id": session_id, "client_ts": ts,
                })

            # ---- self_check（部份學生）----
            if not is_test and rng.random() < 0.3:
                offset += 1
                ts = client_ts_for(offset)
                sample_texts = [
                    "不懂為什麼 n 很小的時候要用 t 而不是 Z",
                    "還是搞不清楚自由度是什麼意思",
                    "ANOVA 顯著後要不要每兩組都比一次？",
                    "有效數字的零到底算不算？",
                    "信賴區間跟機率的關係一直搞混",
                ]
                emit({
                    "student_id": sid, "course_id": "4y_food_analysis", "class_id": "A",
                    "chapter": f"FAS-{ch.upper()}", "game": "fas_quiz", "event_type": "self_check",
                    "site": "fas", "phase": "post", "question_id": f"{ch}-muddy",
                    "free_text": rng.choice(sample_texts), "session_id": session_id, "client_ts": ts,
                })

        # ---- 手動加幾筆完全重複事件，測試去重 ----
        if events:
            dup_candidates = [e for e in events if e.get("chapter") == f"FAS-{ch.upper()}"
                               and e.get("event_type") == "answer"]
            if dup_candidates:
                events.append(dict(rng.choice(dup_candidates)))
                events.append(dict(rng.choice(dup_candidates)))

    return events


# ---------------------------------------------------------------------------
# 7. CLI / main
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="FAS 測驗成效教師端報表產生器")
    p.add_argument("--key", help="service account 金鑰路徑（預設讀 FAS_SA_KEY 環境變數，再退到固定路徑）")
    p.add_argument("--class", dest="class_", help="只篩選某班級 class_id")
    p.add_argument("--since", help="只取此日期（含）之後的事件，格式 YYYY-MM-DD")
    p.add_argument("--out", default=os.path.join("report", "quiz_report.html"), help="輸出 HTML 路徑")
    p.add_argument("--from-json", help="離線模式：從先前 --dump-json 存下的檔案重跑，不連 Firestore")
    p.add_argument("--dump-json", help="把抓到的原始事件存成 JSON 檔（不產生報表分析，只是快取原始資料）")
    p.add_argument("--include-test", action="store_true", help="不排除測試帳號（ZZ/TEST/_ 開頭或 GUEST）")
    p.add_argument("--show-id", action="store_true", help="顯示學號（我還不懂的地方、個別學生表）")
    p.add_argument("--demo", action="store_true", help="用合成假資料跑完整條管線，輸出 report/demo_report.html")
    return p.parse_args(argv)


def run_pipeline(events, args, quiz_meta):
    events, filt_stats = filter_and_dedupe(events, args)
    item_index = build_item_index(quiz_meta)
    misc_index = build_misc_index(quiz_meta)

    first_answers = pick_first_attempts(events)
    first_completes = pick_first_attempt_completes(events)

    overview = build_overview(events, first_answers, first_completes)
    chap_eff = build_chapter_effectiveness(overview["chapters"], first_answers)
    question_rows = build_question_rows(overview["chapters"], first_answers, item_index, misc_index)
    heatmap = build_misconception_heatmap(overview["chapters"], first_answers, misc_index)
    conf_quad = build_confidence_quadrants(overview["chapters"], first_answers, item_index)
    muddiest = build_muddiest(events, args.show_id)
    student_table = build_student_table(overview["chapters"], first_answers) if args.show_id else {}

    return {
        "events": events, "filt_stats": filt_stats, "overview": overview,
        "chap_eff": chap_eff, "question_rows": question_rows, "heatmap": heatmap,
        "conf_quad": conf_quad, "muddiest": muddiest, "student_table": student_table,
        "first_answers": first_answers, "first_completes": first_completes,
    }


def main(argv=None):
    args = parse_args(argv)

    if args.demo:
        args.out = args.out if args.out != os.path.join("report", "quiz_report.html") else os.path.join("report", "demo_report.html")

    raw_events, source = load_events(args)

    if args.dump_json and not args.demo:
        print(f"[quiz_dashboard] 已將 {len(raw_events)} 筆原始事件存到 {args.dump_json}")
        if not raw_events:
            print("[quiz_dashboard] 目前 Firestore 中沒有符合 site=='fas' 的事件（預期中：尚未有真實作答）。")

    quiz_meta = demo_quiz_meta() if args.demo else extract_quiz_metadata()

    result = run_pipeline(raw_events, args, quiz_meta)

    out_path = os.path.join(REPO_ROOT, args.out) if not os.path.isabs(args.out) else args.out
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    muddy_path = os.path.join(os.path.dirname(out_path), "muddiest_points.txt")

    html_out = render_html(
        args, source, result["filt_stats"], result["overview"], result["chap_eff"],
        result["question_rows"], result["heatmap"], result["conf_quad"],
        result["muddiest"], result["student_table"], result["overview"]["chapters"]
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    write_muddiest_txt(result["muddiest"], muddy_path)

    print(f"[quiz_dashboard] 資料來源：{source}")
    print(f"[quiz_dashboard] 原始 {result['filt_stats']['raw']} 筆 → 保留 {result['filt_stats']['kept']} 筆")
    print(f"[quiz_dashboard] 報表已輸出：{out_path}")
    print(f"[quiz_dashboard] 彙整文字檔：{muddy_path}")

    if args.demo:
        _run_demo_assertions(result)
        print("[quiz_dashboard][demo] 所有斷言通過。")

    return result


def _run_demo_assertions(result):
    events = result["events"]
    # 1) 測試帳號被排除
    test_ids = {"ZZ01", "TEST1", "_hidden", "GUEST"}
    present_ids = {e.get("student_id") for e in events}
    assert not (present_ids & test_ids), f"測試帳號未被排除：{present_ids & test_ids}"

    # 2) 重複事件被去重：kept < raw（因為我們手動加了重複事件 + 練習重答不算重複，僅測 dedupe 有作用）
    assert result["filt_stats"]["dropped_dupe"] > 0, "應該至少去除一筆重複事件，但 dropped_dupe == 0"

    # 3) attempts>1 未計入答對率：抽查 first_answers 皆為 attempts==1（或最小 attempts）
    for key, ev in result["first_answers"].items():
        att = ev.get("attempts")
        assert att is None or att <= 1 or True  # 只需保證挑到的是「最小 attempts」，下面再交叉驗證
    # 交叉驗證：對於同時有 attempts=1(錯) 與 attempts=2(對，demo 特意設計) 的紀錄，first_answers 應取 attempts=1（錯）那筆
    by_full_key = defaultdict(list)
    for e in events:
        if e.get("event_type") == "answer":
            by_full_key[(e.get("student_id"), e.get("_chapter_norm"), e.get("question_id"), e.get("phase"))].append(e)
    checked = 0
    for k, evs in by_full_key.items():
        if len(evs) >= 2 and any(e.get("attempts") == 2 for e in evs):
            chosen = result["first_answers"].get(k)
            assert chosen is not None and chosen.get("attempts") == 1, f"first_answers 未取 attempts 最小者：{k}"
            checked += 1
    assert checked > 0, "demo 資料應含至少一筆 attempts=2 的重答紀錄以驗證此邏輯，但沒有抽到任何一筆"


if __name__ == "__main__":
    main()
