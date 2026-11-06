"""설교 원고(.md) → 색상 HTML 한 편 ('설교 html 저장' 1단계)

사용법:
    python3 scripts/sermon_to_html.py <원고.md> [출력폴더=원고와 같은 폴더]

색 규칙 (사용자가 확정한 모양):
    제목(서론·대지·결론·기도) 빨강 / 성경구절 파랑 상자 / 결단 적용(첫째·둘째…) 초록 상자
    전달 표기 (침묵)(천천히) 갈색 기울임 / 글씨는 고딕(md 미리보기와 비슷하게)

출력:
    파일 이름  날짜_설교제목_본문약식.html   (예: 261108_숙제가되어버린감사_눅17장11-19절.html)
    마지막 줄에 아티팩트 제목을 알려 준다     (예: 261108_숙제가되어버린감사_눅17:11-19)
"""
import os
import re
import sys

import markdown

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I 로 실행해도 찾도록
from build_sermon_collection import short_passage  # noqa: E402  (성경 약식 표를 한 곳에서 관리)

CUES = r'\((침묵|천천히|웃으며|고백하듯|성도들을 둘러보며|크게|작게|혼잣말처럼)\)'

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', 'Noto Sans KR', 'Segoe UI', sans-serif;
       background:#ffffff; color:#222; max-width: 760px; margin: 0 auto; padding: 32px 20px 80px;
       line-height: 1.75; font-size: 16px; word-break: keep-all; overflow-wrap: anywhere; }
h1 { text-align:center; font-size: 30px; margin-bottom: 4px; }
h1 + p { text-align:center; color:#666; font-size: 14px; }
h2 { color:#b00000; font-size: 22px;
      margin-top: 48px; border-bottom: 2px solid #e6d9c3; padding-bottom: 6px; }
strong { color:#0b5394; font-weight: 600; }
p > strong:only-child { display:block; background:#eef4fb; border-left: 4px solid #0b5394;
                         padding: 10px 14px; border-radius: 4px; }
p > strong.apply { color:#1e6b34; background:#eaf5ec; border-left-color:#1e6b34; }
.cue { color:#8a6d3b; font-style: italic; font-size: 15px; }
hr { border: none; border-top: 1px solid #ddd; margin: 28px 0; }
li { margin: 6px 0; }
"""


def names(md_path, md):
    """(아티팩트 제목, 파일 이름) — 예: ('261108_제목_눅17:11-19', '261108_제목_눅17장11-19절.html')"""
    lines = md.splitlines()
    ymd = os.path.basename(md_path)[:6]
    title = lines[0].lstrip('# ').strip().replace(' ', '')
    passage = short_passage(lines[2] if len(lines) > 2 else '')
    display = f'{ymd}_{title}' + (f'_{passage}' if passage else '')
    safe = re.sub(r'^(\D+)(\d+):(.+)$', r'\1\2장\3절', passage) if passage else ''
    filename = f'{ymd}_{title}' + (f'_{safe}' if safe else '') + '.html'
    return display, filename


def convert(md):
    body = markdown.markdown(md)
    body = re.sub(CUES, r'<span class="cue">(\1)</span>', body)
    body = re.sub(r'<strong>((첫째|둘째|셋째|넷째),[^<]*)</strong>', r'<strong class="apply">\1</strong>', body)
    title = md.splitlines()[0].lstrip('# ').strip()
    return (f'<!DOCTYPE html>\n<html lang="ko"><head><meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{title}</title>\n<style>{CSS}</style></head><body>\n{body}\n</body></html>')


def main(argv):
    src = argv[0]
    outdir = argv[1] if len(argv) > 1 else os.path.dirname(os.path.abspath(src))
    md = open(src, encoding='utf-8').read()
    display, filename = names(src, md)
    out = os.path.join(outdir, filename)
    open(out, 'w', encoding='utf-8').write(convert(md))
    print(f'saved {out}')
    print(f'아티팩트 제목: {display}')


if __name__ == '__main__':
    main(sys.argv[1:])
