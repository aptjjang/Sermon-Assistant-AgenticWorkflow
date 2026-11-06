"""HWP(한글) 파일 → 텍스트 추출

사용법:
    python3 hwp_to_text.py <출력폴더> <입력1> [<입력2> ...]

입력은 둘 중 하나:
    - .hwp 파일
    - 구글 드라이브 download_file_content 결과를 저장한 JSON 파일
      ({"content": base64, "title": "파일명.hwp", ...})
출력: <출력폴더>/<파일명>.txt
필요: pip install olefile
"""
import base64
import json
import os
import struct
import sys
import zlib

import olefile

PARA_TEXT = 67  # HWPTAG_PARA_TEXT


def extract_text(path):
    ole = olefile.OleFileIO(path)
    compressed = bool(ole.openstream("FileHeader").read()[36] & 1)
    sections = sorted((e for e in ole.listdir() if e[0] == "BodyText"),
                      key=lambda e: int(e[1].replace("Section", "")))
    out = []
    for sec in sections:
        data = ole.openstream(sec).read()
        if compressed:
            data = zlib.decompress(data, -15)
        i = 0
        while i < len(data):
            header = struct.unpack_from("<I", data, i)[0]
            tag, size = header & 0x3FF, (header >> 20) & 0xFFF
            i += 4
            if size == 0xFFF:
                size = struct.unpack_from("<I", data, i)[0]
                i += 4
            if tag == PARA_TEXT:
                out.append(_decode_para(data[i:i + size]))
            i += size
    return "\n".join(out)


def _decode_para(rec):
    chars, j = [], 0
    while j < len(rec):
        c = struct.unpack_from("<H", rec, j)[0]
        if c >= 32:
            chars.append(chr(c)); j += 2
        elif c in (10, 13):
            chars.append("\n"); j += 2
        elif c == 9:
            chars.append("\t"); j += 16
        elif c in (0, 24, 25, 26, 27, 28, 29, 30, 31):
            j += 2
        else:
            j += 16  # 표·그림 등 확장 컨트롤
    return "".join(chars).rstrip("\n")


def main():
    outdir, inputs = sys.argv[1], sys.argv[2:]
    os.makedirs(outdir, exist_ok=True)
    for src in inputs:
        if src.lower().endswith(".hwp"):
            hwp, name = src, os.path.basename(src)
        else:
            d = json.load(open(src, encoding="utf-8"))
            name = d["title"]
            hwp = os.path.join(outdir, name)
            open(hwp, "wb").write(base64.b64decode(d["content"]))
        txt = extract_text(hwp)
        out = os.path.join(outdir, os.path.splitext(name)[0] + ".txt")
        open(out, "w", encoding="utf-8").write(txt)
        print(f"{name}: {len(txt)}자 → {out}")


if __name__ == "__main__":
    main()
