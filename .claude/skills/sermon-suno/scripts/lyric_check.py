"""찬양 가사 점검 (수노 입력용)

사용법:
    python3 lyric_check.py <가사.txt> [--title 제목]
        가사 한 편을 점검한다. <가사.txt> 자리에 - 를 쓰면 표준 입력에서 읽는다.
    python3 lyric_check.py --compare <이전.txt> <수정.txt> [--title 제목] [--rushed]
        수정 전후를 줄 단위로 비교한다(멜로디를 지키려면 글자 수가 같아야 한다).
        --rushed: 몰리는 줄을 일부러 줄인 수정이다. 줄어든 줄을 '고침'이 아니라 '줄임'으로 본다.

가사 파일은 수노 Lyrics 칸에 넣는 모양 그대로 쓴다:
    [Verse 1]            ← 대괄호 = 섹션 표시(불리지 않음)
    밤새 던진 그물은 비었고
    (비었고)              ← 소괄호 = 백보컬로 불림(글자 수에서 뺀다)

보고 내용:
    - 섹션 순서, 줄별 글자 수(한글 음절 수), 부르는 글자 수 합계
    - 후렴이 매번 같은 글자인가 / 1절과 2절의 줄별 글자 수가 같은가
    - 마지막 후렴이 첫 후렴과 줄 수·글자 수가 같은가 ('턴'은 단어만 바꾼다)
    - 줄 길이, 줄 끝 받침, 설교 말투, 한 구간 안의 말투 섞임, 제목(훅) 위치, [End] 표시
    - 등급: 고침(반드시 고친다) · 주의(다시 본다) · 참고(알고 넘어간다)

끝낼 때 '고침'이 하나라도 있으면 종료 코드 1, 없으면 0.

아래 숫자 기준은 2026년 조사 자료의 추정치다. 수노에서 실험해 확인되면 여기만 고친다.
"""
import argparse
import re
import sys

# ── 기준값 (추정치 — references/field-notes.md 에 확인 결과가 쌓이면 고친다) ──
VERSE_RANGE = (7, 12)     # 절 한 줄의 알맞은 글자 수
CHORUS_RANGE = (5, 9)     # 후렴 한 줄의 알맞은 글자 수
OTHER_MAX = 12            # 프리코러스·브리지 등 한 줄 권장 상한
HARD_MAX = 14             # 이보다 길면 줄이 랩처럼 몰린다
CHORUS_MAX_LINES = 4      # 후렴 줄 수 상한 (따라 부르기)
KEEP_DIFF = 1             # 멜로디가 유지되는 글자 수 차이
TOTAL_WARN = 350          # 부르는 글자 수 합계 (느린 곡 4분 기준 어림)
MAX_DIRECTIVES = 8        # 섹션 표시가 아닌 연주 지시 태그 개수 상한

STRUCT = {
    "intro": "intro", "verse": "verse",
    "pre-chorus": "pre", "prechorus": "pre", "pre chorus": "pre",
    "chorus": "chorus", "final chorus": "final", "last chorus": "final",
    "bridge": "bridge", "outro": "outro", "end": "end",
    "interlude": "inst", "instrumental": "inst", "break": "inst",
    "post-chorus": "post", "tag": "post", "refrain": "post", "hook": "post",
}
# 울림소리 받침(ㄴ·ㄹ·ㅁ·ㅇ 소리): 길게 끌 수 있다. 나머지 받침은 소리가 막힌다.
SONORANT = {4, 5, 6, 8, 10, 11, 12, 13, 15, 16, 21}

SERMON = [  # 설교·권고 말투 → 1인칭 고백으로 바꾼다
    (r"여러분", "여러분"), (r"십시오", "~십시오"), (r"바랍니다", "~바랍니다"),
    (r"권합니다", "~권합니다"), (r"[가-힣]야\s*(합니다|한다|해요|하는|하네|하리|하지|됩니다|된다|돼)|[가-힣]야만", "~해야 한다"),
]
SOFT = [  # 설명·권유 말투 → 다시 본다
    (r"것입니다", "설명 말투 '것입니다' — '-네 · -요 · -리' 같은 고백 어미로"),
    (r"때문입니다", "설명 말투 '때문입니다' — '-네 · -요 · -리' 같은 고백 어미로"),
    (r"합시다", "권유 말투 '합시다' — 듣는 사람에게 권하지 말고 고백으로"),
    (r"세요\s*$", "'-세요' — 듣는 사람에게 권하는 말이면 1인칭 고백으로 (하나님께 드리는 말이면 둔다)"),
    (r"하라\s*$", "명령형 '-하라' — 권하는 말이면 고백으로 (브리지에서 말씀을 풀어 쓴 선포면 둔다)"),
]
EMOTION = r"슬프|슬퍼|슬픔|기쁘|기뻐|기쁨|외롭|외로|두렵|두려|행복|우울|괴롭|괴로|불안"
FILLERS = ["은혜", "영광", "임재", "보혈", "축복", "능력", "거룩", "존귀"]
PARTICLE_END = set("을를은는의에")
PRE_MAX_LINES, BRIDGE_MAX_LINES = 2, 4

TAG = re.compile(r"^\s*\[([^\]]+)\]\s*$")
PAREN = re.compile(r"[(（][^)）]*[)）]")


def hangul(s):
    return [c for c in s if "가" <= c <= "힣"]


def coda(ch):
    """받침 번호. 0이면 받침이 없다."""
    return (ord(ch) - 0xAC00) % 28


def stop_codas(sung):
    """소리가 막히는 받침의 개수. 뒤 글자가 모음으로 시작하면 받침이 넘어가므로 세지 않는다."""
    n = 0
    for word in sung.split():
        chars = hangul(word)
        for i, c in enumerate(chars):
            k = coda(c)
            if not k or k in SONORANT:
                continue
            if i + 1 < len(chars) and (ord(chars[i + 1]) - 0xAC00) // 588 == 11:
                continue
            n += 1
    return n


def ending(sung):
    """줄 끝 말투: '-ㅂ니다' / '-요' / 그 밖은 None"""
    chars = hangul(sung)
    if len(chars) >= 2 and chars[-2] + chars[-1] == "니다":
        return "-ㅂ니다"
    if chars and chars[-1] == "요":
        return "-요"
    return None


def tag_kind(name):
    base = name.split(":")[0].strip().lower()
    base = re.sub(r"\s*\d+$", "", base)
    return STRUCT.get(base)


def parse(text):
    """가사를 섹션 목록으로 나눈다. (섹션 목록, 연주 지시 태그 목록)"""
    secs, directives, cur = [], [], None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = TAG.match(line)
        if m:
            kind = tag_kind(m.group(1))
            if kind:
                cur = {"name": m.group(1).strip(), "kind": kind, "lines": []}
                secs.append(cur)
            else:
                directives.append(m.group(1).strip())
            continue
        if cur is None:
            cur = {"name": "(섹션 표시 없음)", "kind": "none", "lines": []}
            secs.append(cur)
        sung = PAREN.sub("", line).strip()
        cur["lines"].append({
            "raw": line, "sung": sung, "n": len(hangul(sung)),
            "paren": bool(PAREN.search(line)),
        })
    seen = {}
    for s in secs:  # 같은 이름이 또 나오면 번호를 붙인다
        seen[s["name"]] = seen.get(s["name"], 0) + 1
        s["label"] = s["name"] if seen[s["name"]] == 1 else f"{s['name']} #{seen[s['name']]}"
    return secs, directives


def norm(sec):
    return [re.sub(r"\s+", " ", ln["sung"]) for ln in sec["lines"] if ln["sung"]]


def sung_lines(sec):
    return [ln for ln in sec["lines"] if ln["sung"]]


def check(secs, directives, title=None, allowed=frozenset()):
    """allowed: 몰림 처방으로 일부러 줄인 줄의 (섹션 종류, 줄 번호) 모음"""
    out = []

    def add(level, where, msg):
        out.append((level, where, msg))

    by = lambda kind: [s for s in secs if s["kind"] == kind]
    verses, choruses, finals = by("verse"), by("chorus"), by("final")

    # 1. 구조
    if by("none"):
        add("주의", "구조", "섹션 표시([Verse 1] 등) 없이 시작하는 줄이 있습니다")
    if not secs or secs[-1]["kind"] != "end":
        add("주의", "구조", "맨 끝에 [End] 가 없습니다 (곡 끝의 군소리를 막아 줍니다)")
    if len(directives) > MAX_DIRECTIVES:
        add("주의", "구조", f"연주 지시 태그가 {len(directives)}개입니다 ({MAX_DIRECTIVES}개 이내 권장)")
    n_ch = len(choruses) + len(finals)
    if n_ch == 0:
        add("고침", "후렴", "[Chorus] 가 없습니다")
    elif n_ch == 1:
        add("고침", "후렴", "후렴이 한 번뿐입니다 — 두 번째 후렴이 있어야 따라 부릅니다")
    elif n_ch == 2:
        add("참고", "후렴", "후렴이 두 번입니다 (세 번이면 회중이 더 쉽게 익힙니다)")

    # 2. 후렴은 매번 같은 글자
    if choruses:
        first = norm(choruses[0])
        if len(first) > CHORUS_MAX_LINES:
            add("주의", choruses[0]["label"], f"후렴이 {len(first)}줄입니다 ({CHORUS_MAX_LINES}줄 이하 권장)")
        for c in choruses[1:]:
            cur = norm(c)
            if cur != first:
                bad = [str(i + 1) for i in range(max(len(first), len(cur)))
                       if i >= len(first) or i >= len(cur) or first[i] != cur[i]]
                add("고침", c["label"], f"첫 후렴과 글자가 다릅니다 ({', '.join(bad)}줄) — 후렴은 매번 똑같이")
        for f in finals:  # 마지막 후렴: 단어 하나 바꾸는 '턴'만 허용
            changed = [ln for ln in norm(f) if ln not in first]
            if not changed:
                add("참고", f["label"], "첫 후렴과 같습니다 — 단어 하나를 바꾸는 '턴'이 없습니다")
            elif len(changed) > 2:
                add("주의", f["label"], f"첫 후렴과 다른 줄이 {len(changed)}개입니다 ('턴'은 한두 줄만)")
            fl, cl = sung_lines(f), sung_lines(choruses[0])
            if len(fl) != len(cl):
                add("주의", f["label"], f"줄 수가 첫 후렴과 다릅니다 ({len(cl)}줄 ↔ {len(fl)}줄) — '턴'은 줄을 더하지 않고 단어만 바꿉니다")
            else:
                for i, (a, b) in enumerate(zip(cl, fl), 1):
                    d = abs(a["n"] - b["n"])
                    if d > KEEP_DIFF:
                        add("고침", f"{f['label']} {i}줄", f"첫 후렴은 {a['n']}자, 여기는 {b['n']}자 — 같은 선율에 얹히지 않습니다")
                    elif d:
                        add("주의", f"{f['label']} {i}줄", f"첫 후렴은 {a['n']}자, 여기는 {b['n']}자 (1자 차이) — 같은 글자 수의 말로 바꿔 봅니다")

    # 3. 1절과 나머지 절의 줄별 글자 수
    for kind_secs in (verses, by("pre")):
        if len(kind_secs) < 2:
            continue
        base = sung_lines(kind_secs[0])
        for v in kind_secs[1:]:
            cur = sung_lines(v)
            if norm(v) == norm(kind_secs[0]):
                continue
            if len(cur) != len(base):
                add("고침", v["label"], f"줄 수가 다릅니다 ({kind_secs[0]['label']} {len(base)}줄 ↔ {len(cur)}줄)")
                continue
            for i, (a, b) in enumerate(zip(base, cur), 1):
                d = abs(a["n"] - b["n"])
                if d > KEEP_DIFF and (v["kind"], i) in allowed:
                    add("주의", f"{v['label']} {i}줄", f"{kind_secs[0]['label']}은 {a['n']}자, 여기는 {b['n']}자 — 몰림 처방으로 줄인 줄. 처음부터 다시 생성할 때는 두 절을 맞춥니다")
                elif d > KEEP_DIFF:
                    add("고침", f"{v['label']} {i}줄", f"{kind_secs[0]['label']}은 {a['n']}자, 여기는 {b['n']}자 ({d}자 차이)")
                elif d:
                    add("주의", f"{v['label']} {i}줄", f"{kind_secs[0]['label']}은 {a['n']}자, 여기는 {b['n']}자 (1자 차이)")

    # 4. 줄 길이 · 줄 끝 소리 · 말투
    seen_line, stops, particles, parens, dense = set(), [], [], [], []
    for s in secs:
        n_sung = len(sung_lines(s))
        if s["kind"] == "pre" and n_sung > PRE_MAX_LINES:
            add("참고", s["label"], f"{n_sung}줄입니다 (프리코러스는 {PRE_MAX_LINES}줄 이하)")
        if s["kind"] == "bridge" and n_sung > BRIDGE_MAX_LINES:
            add("참고", s["label"], f"{n_sung}줄입니다 (브리지는 {BRIDGE_MAX_LINES}줄 이하)")
        ends = {e for e in (ending(ln["sung"]) for ln in s["lines"]) if e}
        if len(ends) > 1:
            add("주의", s["label"], "한 구간 안에 '-ㅂ니다'와 '-요'가 섞였습니다 — 한 말투로 맞춥니다")
        for i, ln in enumerate(s["lines"], 1):
            where = f"{s['label']} {i}줄"
            key = re.sub(r"\s+", " ", ln["raw"])
            if key in seen_line:  # 똑같이 반복되는 줄은 한 번만 본다
                continue
            seen_line.add(key)
            if ln["paren"]:
                parens.append(where)
            if not ln["sung"]:
                continue
            n, chars = ln["n"], hangul(ln["sung"])
            if re.search(r"[A-Za-z0-9]", ln["sung"]):
                add("주의", where, "영문·숫자가 있습니다 — 한글로 풀어 쓰면 발음이 안정됩니다")
            if n == 0:
                continue
            if n > HARD_MAX:
                add("고침", where, f"{n}자 — {HARD_MAX}자를 넘으면 줄이 몰립니다. 덜어내거나 두 줄로")
            elif s["kind"] == "verse" and not VERSE_RANGE[0] <= n <= VERSE_RANGE[1]:
                add("주의", where, f"{n}자 (절은 {VERSE_RANGE[0]}~{VERSE_RANGE[1]}자 권장)")
            elif s["kind"] in ("chorus", "final") and not CHORUS_RANGE[0] <= n <= CHORUS_RANGE[1]:
                add("주의", where, f"{n}자 (후렴은 {CHORUS_RANGE[0]}~{CHORUS_RANGE[1]}자 권장)")
            elif s["kind"] not in ("verse", "chorus", "final") and n > OTHER_MAX:
                add("주의", where, f"{n}자 ({OTHER_MAX}자 이하 권장)")
            last = coda(chars[-1])
            if last and last not in SONORANT:
                if s["kind"] in ("chorus", "final", "outro"):
                    add("주의", where, f"줄 끝 '{chars[-1]}'의 받침이 소리를 막습니다 — 긴 음에는 받침 없는 말을")
                else:
                    stops.append(where)
            if chars[-1] in PARTICLE_END:
                particles.append(where)
            sc = stop_codas(ln["sung"])
            if sc >= 3 or (n >= 5 and sc / n > 0.4):
                dense.append(where)
            for pat, label in SERMON:
                if re.search(pat, ln["sung"]):
                    add("고침", where, f"설교 말투 '{label}' — 하나님께 드리는 1인칭 고백으로 바꿉니다")
            for pat, msg in SOFT:
                if re.search(pat, ln["sung"]):
                    add("주의", where, msg)
            if s["kind"] == "verse" and re.search(EMOTION, ln["sung"]):
                add("참고", where, "감정 이름이 있습니다 — 그 감정이 보이는 장면으로 바꿀 수 있는지 봅니다")
    if stops:
        add("참고", "줄 끝", "막히는 받침으로 끝나는 줄: " + ", ".join(stops))
    if particles:
        add("참고", "줄 끝", "'을/를/은/는/의/에'로 끝나는 줄(조사면 긴 음에 걸려 어색할 수 있음): " + ", ".join(particles))
    if dense:
        add("참고", "발음", "막히는 받침이 몰린 줄: " + ", ".join(dense))
    if parens:
        add("참고", "소괄호", "소괄호 안은 백보컬로 불립니다: " + ", ".join(parens))

    # 5. 상투어
    body = " ".join(" ".join(norm(s)) for s in secs)
    used = [w for w in FILLERS if w in body and not (title and w in title)]
    if len(used) >= 3:
        add("주의", "상투어", f"{' · '.join(used)} — 다른 찬양에 그대로 옮겨도 말이 되는 줄이 아닌지 봅니다")

    # 6. 제목 = 훅
    if title:
        t = re.sub(r"\s+", "", title)
        flat = lambda sec: [re.sub(r"\s+", "", x) for x in norm(sec)]
        if choruses:
            lines = flat(choruses[0])
            if not any(t in x for x in lines):
                add("고침", "제목", f"후렴에 제목 '{title}'이(가) 없습니다 — 제목이 곧 훅입니다")
            elif lines and t not in lines[0] and t not in lines[-1]:
                add("주의", "제목", "제목이 후렴의 첫 줄이나 끝 줄에 오면 더 잘 남습니다")
        for o in by("outro"):
            if o["lines"] and not any(t in x for x in flat(o)):
                add("참고", o["label"], "아웃트로에 제목이 없습니다 (제목 한 줄로 끝내면 훅이 남습니다)")
        th = hangul(t)
        if th and coda(th[-1]) and coda(th[-1]) not in SONORANT:
            add("주의", "제목", f"제목 끝 '{th[-1]}'의 받침이 소리를 막습니다")

    # 7. 분량
    total = sum(ln["n"] for s in secs for ln in s["lines"])
    if total > TOTAL_WARN:
        add("주의", "분량", f"부르는 글자가 {total}자입니다 ({TOTAL_WARN}자를 넘으면 느린 곡에서 몰리거나 4분을 넘습니다)")
    return out, total


def print_lines(secs):
    shown = {}
    for s in secs:
        if s["kind"] == "end":
            continue
        key = (s["kind"], tuple(norm(s)))
        if s["lines"] and key in shown:
            print(f"[{s['label']}]  (앞의 [{shown[key]}]와 같음)")
            continue
        shown[key] = s["label"]
        if not s["lines"]:
            print(f"[{s['label']}]  (가사 없음)")
            continue
        print(f"[{s['label']}]  " + " · ".join(str(ln["n"]) for ln in sung_lines(s)))
        for ln in s["lines"]:
            mark = f"{ln['n']:>4}" if ln["sung"] else "  백"
            print(f"  {mark} | {ln['raw']}")


def report(text, title=None, allowed=frozenset()):
    secs, directives = parse(text)
    issues, total = check(secs, directives, title, allowed)
    n_lines = sum(len(sung_lines(s)) for s in secs)
    print("== 구조 ==")
    print(" → ".join(s["name"] for s in secs) or "(비어 있음)")
    print(f"부르는 글자 수: {total}자 · {n_lines}줄" + (f" · 제목: {title}" if title else ""))
    print("\n== 줄별 글자 수 ==")
    print_lines(secs)
    count = lambda lv: sum(1 for i in issues if i[0] == lv)
    print(f"\n== 점검 ==  고침 {count('고침')} · 주의 {count('주의')} · 참고 {count('참고')}")
    for level in ("고침", "주의", "참고"):
        for lv, where, msg in issues:
            if lv == level:
                print(f"[{lv}] {where}: {msg}")
    if not issues:
        print("걸리는 곳이 없습니다. 이제 소리 내어 읽어 봅니다.")
    return count("고침")


def compare(old_text, new_text, rushed=False):
    """수정 전후를 줄 단위로 비교한다. 글자 수가 2자 이상 달라지면 고침.

    rushed=True 이면 줄어든 줄은 몰림 처방으로 보고 '줄임'으로 표시한다.
    (고침 개수, 일부러 줄인 줄의 (섹션 종류, 줄 번호) 모음)을 돌려준다.
    """
    old, _ = parse(old_text)
    new, _ = parse(new_text)
    fixes = changed = 0
    allowed = set()
    print("== 수정 전후 비교 ==")
    if [s["kind"] for s in old] != [s["kind"] for s in new]:
        print("[주의] 섹션 순서가 달라졌습니다 — 곡 전체를 다시 만들어야 할 수 있습니다")
    for a, b in zip(old, new):
        la, lb = sung_lines(a), sung_lines(b)
        if len(la) != len(lb):
            print(f"[고침] {b['label']}: 줄 수가 {len(la)}줄 → {len(lb)}줄로 바뀌었습니다")
            fixes += 1
            continue
        for i, (x, y) in enumerate(zip(la, lb), 1):
            if x["sung"] == y["sung"]:
                continue
            changed += 1
            d = y["n"] - x["n"]
            if abs(d) <= KEEP_DIFF:
                mark, note = "유지", ""
            elif rushed and d < 0:
                mark, note = "줄임", " — 몰림 처방. 이 구간의 멜로디는 새로 나옵니다"
                allowed.add((b["kind"], i))
            else:
                mark, note = "고침", " — 멜로디가 달라질 수 있습니다"
                fixes += 1
            print(f"[{mark}] {b['label']} {i}줄: {x['n']}자 → {y['n']}자 ({d:+d}){note}")
            print(f"       전 | {x['raw']}")
            print(f"       후 | {y['raw']}")
    if not changed and not fixes:
        print("달라진 줄이 없습니다.")
    print()
    return fixes, allowed


def read(path):
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    ap = argparse.ArgumentParser(description="찬양 가사 점검 (수노 입력용)")
    ap.add_argument("files", nargs="+", help="가사 파일 (--compare 일 때는 이전 수정 순서로 두 개)")
    ap.add_argument("--title", help="곡 제목 — 후렴에 들어 있는지 확인한다")
    ap.add_argument("--compare", action="store_true", help="수정 전후 비교")
    ap.add_argument("--rushed", action="store_true", help="--compare 와 함께: 몰리는 줄을 일부러 줄였다")
    args = ap.parse_args()
    if args.compare:
        if len(args.files) != 2:
            ap.error("--compare 에는 파일 두 개(이전, 수정)가 필요합니다")
        fixes, allowed = compare(read(args.files[0]), read(args.files[1]), args.rushed)
        fixes += report(read(args.files[1]), args.title, frozenset(allowed))
    else:
        if len(args.files) != 1:
            ap.error("가사 파일은 하나만 줍니다")
        fixes = report(read(args.files[0]), args.title)
    sys.exit(1 if fixes else 0)


if __name__ == "__main__":
    main()
