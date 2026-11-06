"""설교 원고 분량·형식 점검 (md · HWP · Pages · 구글 문서 · txt)

사용법:
    python3 sermon_length.py <원고> [제한분=15]

<원고>는 md 최종 원고 외에도 doc_to_text.py가 읽는 모든 형식을 받는다:
    .hwp / .pages / .txt / 구글 드라이브 download_file_content JSON(HWP·Pages·구글 문서)
    - md 원고: '## 서론'~'## <기도>' 구간을 설교로, 봉독·기도를 따로 계산
    - 그 밖의 자료(설교 초안 등): 구간 구분 없이 전체를 설교로 계산

보고 내용:
    - 본문 봉독 / 설교(서론~결론) / 기도 글자 수(공백 제외)와 예상 시간(분당 280~320자)
    - 평어체("~다.")로 끝나는 설교 문장 (성경 인용·따옴표 안은 제외)
    - 자료 언급 설명구("자료", "슬라이드", "진행자" 등)
    - 세 줄(약 120자)이 넘는 긴 문장
    - 표시 이름 제안: 날짜_제목_본문약식
"""
import os
import re
import sys

BOOKS = [  # (정식 이름, 약식) — 긴 이름부터 비교
    ("예레미야애가", "애"), ("데살로니가전서", "살전"), ("데살로니가후서", "살후"),
    ("고린도전서", "고전"), ("고린도후서", "고후"), ("디모데전서", "딤전"), ("디모데후서", "딤후"),
    ("베드로전서", "벧전"), ("베드로후서", "벧후"), ("요한계시록", "계"), ("요한일서", "요일"),
    ("요한이서", "요이"), ("요한삼서", "요삼"), ("갈라디아서", "갈"), ("열왕기상", "왕상"),
    ("열왕기하", "왕하"), ("사무엘상", "삼상"), ("사무엘하", "삼하"), ("출애굽기", "출"),
    ("마태복음", "마"), ("마가복음", "막"), ("누가복음", "눅"), ("요한복음", "요"),
    ("사도행전", "행"), ("에베소서", "엡"), ("빌립보서", "빌"), ("골로새서", "골"),
    ("빌레몬서", "몬"), ("히브리서", "히"), ("야고보서", "약"), ("느헤미야", "느"),
    ("여호수아", "수"), ("예레미야", "렘"), ("창세기", "창"), ("레위기", "레"), ("민수기", "민"),
    ("신명기", "신"), ("사사기", "삿"), ("역대상", "대상"), ("역대하", "대하"), ("에스라", "스"),
    ("에스더", "에"), ("전도서", "전"), ("이사야", "사"), ("에스겔", "겔"), ("다니엘", "단"),
    ("호세아", "호"), ("아모스", "암"), ("오바댜", "옵"), ("하박국", "합"), ("스바냐", "습"),
    ("스가랴", "슥"), ("말라기", "말"), ("로마서", "롬"), ("디도서", "딛"), ("유다서", "유"),
    ("룻기", "룻"), ("욥기", "욥"), ("시편", "시"), ("잠언", "잠"), ("아가", "아"),
    ("요엘", "욜"), ("요나", "욘"), ("미가", "미"), ("나훔", "나"), ("학개", "학"),
]
SOURCE_WORDS = ["자료", "슬라이드", "진행자", "해설", "문헌", "전사"]


def nchars(s):
    return len(re.sub(r"\s|\*|#|-", "", s))


def short_passage(text):
    """'누가복음 17:11-19' 또는 '누가복음 17장 11-19절' → ('눅17:11-19', '눅17장11-19절')"""
    verses = r"(\d+(?:\s*[-~,]\s*\d+(?!\d*\s*[:장]))*)"  # 뒤따르는 다른 장:절은 붙이지 않음
    found = []  # (글 속 위치, 표시용, 파일용) — 가장 앞에 나온 본문을 쓴다
    for full, short in BOOKS:
        for pat in (full + r"\s*(\d+):" + verses, full + r"\s*(\d+)장\s*" + verses):
            m = re.search(pat, text)
            if m:
                v = re.sub(r"\s", "", m.group(2))
                found.append((m.start(), f"{short}{m.group(1)}:{v}", f"{short}{m.group(1)}장{v}절"))
        m = re.search(full + r"\s*(\d+)(편|장)(?!\s*\d)", text)  # 장 전체 (예: 시편 23편)
        if m:
            found.append((m.start(), f"{short}{m.group(1)}{m.group(2)}", f"{short}{m.group(1)}{m.group(2)}"))
    if not found:
        return "", ""
    _, disp, fname = min(found)
    return disp, fname


def section(text, start, end):
    i = text.find(start)
    j = text.find(end, i + 1) if end else -1
    return "" if i < 0 else text[i:j if j > 0 else None]


def main():
    path = sys.argv[1]
    limit = float(sys.argv[2]) if len(sys.argv) > 2 else 15
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I 로 실행해도 찾도록
    from doc_to_text import read_any  # 같은 폴더의 자료 읽기 도구
    src_title, t = read_any(path)
    is_md = "## 서론" in t
    if is_md:  # md 최종 원고
        reading = t[t.find("**"):t.find("## 서론")]
        sermon = section(t, "## 서론", "## <기도>")
        prayer = section(t, "## <기도>", "## 기도제목")
    else:  # 초안·해설 등 구간 표시가 없는 자료
        print("※ 구간(## 서론 등) 표시가 없어 전체를 설교로 계산합니다\n")
        reading, sermon, prayer = "", t, ""

    print("[분량] 공백 제외, 분당 280~320자 기준")
    if is_md:
        total = 0
        for label, part in (("본문 봉독", reading), ("설교(서론~결론)", sermon), ("기도", prayer)):
            n = nchars(part); total += n
            print(f"  {label}: {n}자  {n/320:.1f}~{n/280:.1f}분")
        print(f"  합계: {total}자  {total/320:.1f}~{total/280:.1f}분")
    else:
        n = nchars(sermon)
        print(f"  전체: {n}자  {n/320:.1f}~{n/280:.1f}분")
    n = nchars(sermon)
    if n / 300 > limit:
        print(f"  ⚠ 설교가 {limit:.0f}분을 넘을 수 있음 → 약 {int(n - limit*300)}자 줄이기 권장")

    plain = re.sub(r"\*\*.*?\*\*", "", sermon)
    plain = re.sub(r'"[^"]*"', "", plain)
    sentences = re.split(r"(?<=[.?!])\s+", plain)
    flat = [s.strip() for s in sentences if re.search(r"[^니]다\.$", s.strip())]
    print(f"\n[평어체 문장] {len(flat)}개")
    for s in flat[:10]:
        print("  -", s[-60:])

    hits = [w for w in SOURCE_WORDS if w in plain]
    print(f"\n[자료 언급 설명구] {', '.join(hits) if hits else '없음'}")

    longs = [s.strip() for s in sentences if nchars(s) > 120]
    print(f"\n[긴 문장(120자 초과)] {len(longs)}개")
    for s in longs[:5]:
        print("  -", s[:50] + "…")

    if not is_md:  # 이름 제안은 md 최종 원고에만
        return
    lines = [x for x in t.splitlines() if x.strip()]
    title = (lines[0] if lines else "").lstrip("# ").replace(" ", "")
    disp, fname = short_passage("\n".join(lines[:6]))
    m = re.match(r"(\d{6})", src_title) or re.match(r"(\d{6})", path.split("/")[-1])
    ymd = m.group(1) if m else "YYMMDD"
    print(f"\n[이름 제안] 표시: {ymd}_{title}_{disp}   파일: {ymd}_{title}_{fname}.md")


if __name__ == "__main__":
    main()
