#!/usr/bin/env python3
"""統一全站迷思 key：合併同義 key、讓同一個 key 在各章的中文描述逐字相同，
並產生全站字典 docs/MISCONCEPTIONS.md（key、描述、使用章節）。

各章題目是分頭撰寫的，難免出現同義不同名的 key；儀表板的「迷思熱區」是跨章彙整，
同義 key 不合併就會被拆成兩列。發現新的同義 key 時，加進 RENAME 後重跑即可（可重複執行）。

    python scripts/merge_misc_keys.py
    node scripts/check_quiz.js          # 跑完後務必再檢查一次
"""
import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 舊 key -> 全站統一的 key
RENAME = {
    "PSEUDOREPLICATION": "PSEUDO_REPLICATION",
    "DELETE_DATA_TO_LOOK_GOOD": "OUTLIER_DELETE_FOR_PRECISION",
    "OUTLIER_TEST_ALONE_DELETE": "OUTLIER_DELETE_BY_TEST_ONLY",
    "SS_NOT_MS": "F_FORGOT_DF",
    "R2_HIGH_MEANS_LINEAR": "R2_PROVES_LINEAR",
    "INTERACTION_IGNORED_MAIN_EFFECT": "INTERACTION_IGNORED",
    "KRAGTEN_MC_CONFUSION": "KRAGTEN_MC_CONFUSED",
    "U_VS_EXPANDED_U": "U_VS_UC",
    "ADD_SD_LINEARLY": "UNC_LINEAR_ADD",
    "CAL_UNC_CONSTANT": "CONF_BAND_UNIFORM",
    "SR_AS_INTERMEDIATE": "REPEATABILITY_AS_INTERMEDIATE",
    "EMPIRICAL_HAS_TRUE_VALUE": "EMPIRICAL_METHOD_BIAS",
    "COMPLIANCE_RULE_REVERSED": "COMPLIANCE_RULE_MISAPPLIED",
}

# 指定描述（未列者採用第一個出現的章節的寫法）
CANON = {
    "OTHER": "不對應特定迷思的湊數選項（盡量少用）",
    "PSEUDO_REPLICATION": "把同一樣品溶液的重複注射／重複讀值當成獨立重複",
    "SD_VS_SEM": "分不清標準差 SD 與平均數標準誤 SEM",
    "FORGOT_SQRT_N": "算 SEM／CI 時忘了除以 √n",
    "UNC_LINEAR_ADD": "把不確定度（或標準差）分量直接相加而不是平方和開根號",
    "U_VS_UC": "分不清（合成）標準不確定度 u 與擴展不確定度 U = k·u",
    "R2_PROVES_LINEAR": "以為 r²（或 r）很高就證明線性、不用看殘差圖",
    "CONF_BAND_UNIFORM": "以為標準曲線各處反推的不確定度都一樣（不知道信賴帶中段最窄、兩端變寬）",
    "COMPLIANCE_RULE_MISAPPLIED": "保守決策規則用錯：區間跨過限值的灰色地帶卻直接判成符合或不符合",
    "EMPIRICAL_METHOD_BIAS": "不知道經驗（操作定義）方法的結果由方法本身定義，仍以為有獨立的真值要去修正偏倚",
    "REPEATABILITY_AS_INTERMEDIATE": "以為短期重複性（同一天、同一批的重複）就能代表長期的中間精密度",
    "OUTLIER_DELETE_FOR_PRECISION": "為了讓 SD 變小、配適變漂亮或結果變顯著而刪除數據",
    "OUTLIER_DELETE_BY_TEST_ONLY": "以為檢定顯著就可以直接刪除數據，不必找原因與記錄",
    "INTERACTION_IGNORED": "交互作用顯著時仍單獨解讀（或只報告）主效應",
}

ENTRY = re.compile(r'^(\s*)([A-Z][A-Z0-9_]*)(\s*:\s*)"((?:[^"\\]|\\.)*)"(\s*,?\s*)$')
BLOCK = re.compile(r'(const MISC\s*=\s*\{)(.*?)(\n\};?)', re.S)


def main():
    files = sorted(ROOT.glob("ch[0-9][0-9].html"))
    texts = {}
    for f in files:                                   # 1) 合併同義 key
        s = io.open(f, encoding="utf-8", newline="").read()
        for old, new in RENAME.items():
            s = re.sub(r"(?<![A-Z0-9_])" + old + r"(?![A-Z0-9_])", new, s)
        texts[f] = s

    canon = dict(CANON)                               # 2) 決定每個 key 的標準描述
    for f in files:
        m = BLOCK.search(texts[f])
        if not m:
            continue
        for line in m.group(2).splitlines():
            e = ENTRY.match(line.rstrip("\r"))
            if e:
                canon.setdefault(e.group(2), e.group(4))

    used = {}
    for f in files:                                   # 3) 重寫各章 MISC：去重複、套標準描述
        s = texts[f]
        m = BLOCK.search(s)
        if m:
            eol = "\r\n" if "\r\n" in m.group(2) else "\n"
            seen, out = set(), []
            for line in m.group(2).split(eol):
                e = ENTRY.match(line)
                if not e:
                    out.append(line)
                    continue
                key = e.group(2)
                if key in seen:
                    continue
                seen.add(key)
                used.setdefault(key, []).append(f.stem)
                out.append(f'{e.group(1)}{key}{e.group(3)}"{canon[key]}",')
            # 最後一個項目不留逗號也合法，但統一留著比較好維護
            s = s[:m.start(2)] + eol.join(out) + s[m.end(2):]
        io.open(f, "w", encoding="utf-8", newline="").write(s)

    lines = [                                         # 4) 全站字典
        "# 全站迷思字典（Misconception keys）",
        "",
        "本檔由 `python scripts/merge_misc_keys.py` 自各章 `const MISC` 產生，請勿手改。",
        "出題時**先在這裡找有沒有語意相同的 key**，有就沿用；沒有才新增（全大寫蛇形英文，描述用一句白話寫學生「以為什麼」）。",
        "新增或發現同義 key 後重跑腳本，再跑 `node scripts/check_quiz.js`。",
        "",
        f"共 {len(used)} 個 key。",
        "",
        "| key | 學生「以為」 | 使用章節 |",
        "|---|---|---|",
    ]
    for key in sorted(used):
        lines.append(f"| `{key}` | {canon[key]} | {', '.join(used[key])} |")
    io.open(ROOT / "docs" / "MISCONCEPTIONS.md", "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print(f"{len(files)} 章、{len(used)} 個迷思 key；已更新 docs/MISCONCEPTIONS.md")


if __name__ == "__main__":
    main()
