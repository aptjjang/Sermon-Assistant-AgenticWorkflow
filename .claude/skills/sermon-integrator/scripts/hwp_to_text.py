"""(이전 이름) — 이제 doc_to_text.py가 HWP·Pages·구글 문서·txt를 모두 읽는다.
이 파일은 예전 사용법을 그대로 쓰기 위한 연결 고리다.

사용법은 doc_to_text.py와 같다:
    python3 hwp_to_text.py <출력폴더> <입력1> [<입력2> ...]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doc_to_text import main  # noqa: E402

if __name__ == "__main__":
    main()
