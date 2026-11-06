"""설교 모음 페이지 생성기 (claude.ai 아티팩트용 단일 HTML)

설교 원고 .md 파일들을 받아, 목록 + 원고 본문을 모두 담은 HTML 한 장을 만든다.
목록에서 설교를 누르면 같은 페이지 안에서 원고가 펼쳐진다 (외부 링크 없음).

사용법:
    python3 scripts/build_sermon_collection.py 출력.html 원고1.md 원고2.md ...

원고 .md 규칙:
    - 파일명: YYMMDD_설교제목.md   (날짜는 파일명 앞 6자리에서 읽음)
    - 1행:    # 설교 제목
    - 3행:    날짜 / 성경본문(예: 누가복음 17:11-19) / 결단 찬양 ...
"""
import html
import os
import re
import sys

import markdown

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
CUES = r'\((침묵|천천히|웃으며|고백하듯|성도들을 둘러보며|크게|작게|혼잣말처럼)\)'


def short_passage(text):
    """'누가복음 17:11-19' → '눅17:11-19'"""
    for full, short in BOOKS:
        m = re.search(full + r'\s*(\d[\d:,\-~ ]*\d)', text)
        if m:
            return short + m.group(1).replace(' ', '')
    return ''


def load(path):
    md = open(path, encoding='utf-8').read()
    lines = md.splitlines()
    ymd = os.path.basename(path)[:6]
    title = lines[0].lstrip('# ').strip()
    passage = short_passage(lines[2] if len(lines) > 2 else '')
    body = markdown.markdown('\n'.join(lines[1:]))
    body = re.sub(CUES, r'<span class="cue">(\1)</span>', body)
    body = re.sub(r'<strong>((첫째|둘째|셋째|넷째),[^<]*)</strong>',
                  r'<strong class="apply">\1</strong>', body)
    return {'id': 's-' + ymd, 'ymd': ymd, 'title': title, 'passage': passage, 'body': body}


CSS = """
/* 레이아웃: 목록 화면과 원고 화면을 같은 페이지 안에서 #해시로 전환 */
:root {
  --bg: #ffffff; --ink: #1f2328; --muted: #6a6f76; --line: #ece8e6;
  --accent: #a3141b; --scripture: #0b5394; --scripture-bg: #eef4fb;
  --apply: #1e6b34; --apply-bg: #eaf5ec; --cue: #8a6d3b; --hover: #faf5f4;
  --font-body: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', 'Noto Sans KR', 'Segoe UI', sans-serif;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #17181a; --ink: #ecebea; --muted: #a2a3a6; --line: #2c2d30;
    --accent: #ff7a7f; --scripture: #8cc0f5; --scripture-bg: #1c2633;
    --apply: #8fd6a2; --apply-bg: #1b2a20; --cue: #d4b483; --hover: #212225; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #17181a; --ink: #ecebea; --muted: #a2a3a6; --line: #2c2d30;
  --accent: #ff7a7f; --scripture: #8cc0f5; --scripture-bg: #1c2633;
  --apply: #8fd6a2; --apply-bg: #1b2a20; --cue: #d4b483; --hover: #212225; color-scheme: dark;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink);
       font-family: var(--font-body); font-size: 16px; line-height: 1.75;
       word-break: keep-all; overflow-wrap: anywhere; }
main { max-width: 680px; margin: 0 auto; padding: 24px 18px 64px; }
.view[hidden] { display: none; }
header.top { border-bottom: 2px solid var(--accent); padding-bottom: 12px; margin-bottom: 8px; }
header.top h1 { margin: 0; font-size: 26px; text-wrap: balance; }
header.top p { margin: 4px 0 0; color: var(--muted); font-size: 14px; }
ul.list { list-style: none; margin: 0; padding: 0; }
ul.list li + li { border-top: 1px solid var(--line); }
a.row { display: grid; grid-template-columns: 4.2em 1fr; gap: 2px 14px; padding: 14px 6px;
        color: inherit; text-decoration: none; border-radius: 6px; }
a.row:hover { background: var(--hover); }
a.row:focus-visible, a.back:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.date { grid-row: span 2; font-variant-numeric: tabular-nums; font-weight: 700;
        color: var(--accent); font-size: 15px; }
.title { font-size: 17px; font-weight: 600; }
.meta { color: var(--muted); font-size: 14px; }
a.back { display: inline-block; margin-bottom: 12px; padding: 6px 12px; border: 1px solid var(--line);
         border-radius: 999px; color: var(--accent); text-decoration: none; font-size: 14px; font-weight: 600; }
article h1 { text-align: center; font-size: 26px; margin: 8px 0 4px; text-wrap: balance; }
article h1 + p { text-align: center; color: var(--muted); font-size: 14px; }
article h2 { color: var(--accent); font-size: 20px; margin-top: 40px;
             border-bottom: 2px solid var(--line); padding-bottom: 6px; text-wrap: balance; }
article strong { color: var(--scripture); font-weight: 600; }
article p > strong:only-child { display: block; background: var(--scripture-bg);
             border-left: 4px solid var(--scripture); padding: 10px 14px; border-radius: 4px; }
article p > strong.apply { color: var(--apply); background: var(--apply-bg); border-left-color: var(--apply); }
.cue { color: var(--cue); font-style: italic; font-size: 15px; }
article hr { border: none; border-top: 1px solid var(--line); margin: 24px 0; }
"""

JS = """
function show() {
  var id = location.hash.slice(1);
  var target = id && document.getElementById(id);
  document.querySelectorAll('.view').forEach(function (v) { v.hidden = true; });
  (target || document.getElementById('list')).hidden = false;
  window.scrollTo(0, 0);
}
window.addEventListener('hashchange', show);
show();
"""


def build(out, paths):
    sermons = sorted((load(p) for p in paths), key=lambda s: s['ymd'], reverse=True)
    rows, articles = [], []
    for s in sermons:
        y, m, d = s['ymd'][:2], s['ymd'][2:4], s['ymd'][4:]
        name = f"{s['ymd']}_{s['title'].replace(' ', '')}" + (f"_{s['passage']}" if s['passage'] else '')
        rows.append(
            f'<li><a class="row" href="#{s["id"]}"><span class="date">{m}.{d}</span>'
            f'<span class="title">{html.escape(name)}</span>'
            f'<span class="meta">20{y}년 {int(m)}월 {int(d)}일 주일</span></a></li>')
        articles.append(
            f'<section class="view" id="{s["id"]}" hidden><a class="back" href="#list">← 설교 모음</a>'
            f'<article><h1>{html.escape(s["title"])}</h1>{s["body"]}</article></section>')
    page = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>설교 모음</title><style>{CSS}</style></head>
<body><main>
<section class="view" id="list">
<header class="top"><h1>설교 모음</h1><p>좋은나무교회 주일 설교 원고 · 최신순 · 누르면 원고가 열립니다</p></header>
<ul class="list">{''.join(rows)}</ul>
</section>
{''.join(articles)}
</main><script>{JS}</script></body></html>"""
    open(out, 'w', encoding='utf-8').write(page)
    print(f'saved {out} ({len(sermons)}편)')


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2:])
