"""설교 자료 → 텍스트 추출 (HWP · Pages · 구글 문서 · txt/md)

사용법:
    python3 doc_to_text.py <출력폴더> <입력1> [<입력2> ...]

입력으로 받을 수 있는 것:
    - .hwp            한글 문서                    (필요: pip install olefile)
    - .pages          애플 Pages 문서 (2013 이후 형식 · 2009 형식)
    - .txt / .md      일반 텍스트
    - 구글 드라이브 download_file_content 결과를 저장한 JSON
        · HWP·Pages 파일을 내려받은 것  ({"content": base64, "title": "파일.hwp"})
        · 구글 문서를 exportMimeType="text/plain"으로 내려받은 것
          ({"content": base64, "mimeType": "text/plain", "title": "문서 제목"})
      ※ 구글 문서는 드라이브 read_file_content로 바로 읽는 것이 가장 쉽다.
        이 도구는 내려받은 파일을 저장해 두고 다시 쓰거나, 분량 점검 도구에 넘길 때 쓴다.
출력: <출력폴더>/<파일명>.txt

다른 도구에서 가져다 쓰기:
    from doc_to_text import read_any
    title, text = read_any(path)
"""
import base64
import io
import json
import os
import re
import struct
import sys
import zipfile
import zlib


# ───────────────────────── HWP ─────────────────────────
HWP_PARA_TEXT = 67  # HWPTAG_PARA_TEXT


def hwp_text(data):
    import olefile  # HWP에만 필요
    ole = olefile.OleFileIO(io.BytesIO(data))
    compressed = bool(ole.openstream("FileHeader").read()[36] & 1)
    sections = sorted((e for e in ole.listdir() if e[0] == "BodyText"),
                      key=lambda e: int(e[1].replace("Section", "")))
    out = []
    for sec in sections:
        body = ole.openstream(sec).read()
        if compressed:
            body = zlib.decompress(body, -15)
        i = 0
        while i < len(body):
            header = struct.unpack_from("<I", body, i)[0]
            tag, size = header & 0x3FF, (header >> 20) & 0xFFF
            i += 4
            if size == 0xFFF:
                size = struct.unpack_from("<I", body, i)[0]
                i += 4
            if tag == HWP_PARA_TEXT:
                out.append(_hwp_para(body[i:i + size]))
            i += size
    return "\n".join(out)


def _hwp_para(rec):
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


# ───────────────────────── Pages ─────────────────────────
# 2013 이후 Pages: zip 안의 Index/Document.iwa (snappy 압축 + protobuf)
# 본문 글자는 TSWP.StorageArchive(메시지 형식 번호 2001)의 3번 필드에 들어 있다.
TSWP_STORAGE = 2001


def _snappy(buf):
    """snappy 원형(raw) 압축 풀기 — 외부 라이브러리 없이"""
    n, shift, i = 0, 0, 0
    while True:  # 앞머리: 풀린 뒤 길이(varint)
        b = buf[i]; i += 1
        n |= (b & 0x7F) << shift; shift += 7
        if b < 0x80:
            break
    out = bytearray()
    while i < len(buf):
        tag = buf[i]; i += 1
        kind = tag & 3
        if kind == 0:  # 글자 그대로
            ln = tag >> 2
            if ln >= 60:
                extra = ln - 59
                ln = int.from_bytes(buf[i:i + extra], "little"); i += extra
            ln += 1
            out += buf[i:i + ln]; i += ln
            continue
        if kind == 1:
            ln = ((tag >> 2) & 7) + 4
            off = ((tag >> 5) << 8) | buf[i]; i += 1
        elif kind == 2:
            ln = (tag >> 2) + 1
            off = int.from_bytes(buf[i:i + 2], "little"); i += 2
        else:
            ln = (tag >> 2) + 1
            off = int.from_bytes(buf[i:i + 4], "little"); i += 4
        for _ in range(ln):  # 겹치는 복사가 있어 한 글자씩
            out.append(out[-off])
    return bytes(out[:n])


def _iwa_unpack(data):
    """IWA 덩어리들(0x00 + 3바이트 길이 + snappy)을 이어 붙여 풀기"""
    out, i = bytearray(), 0
    while i + 4 <= len(data):
        ln = int.from_bytes(data[i + 1:i + 4], "little")
        out += _snappy(data[i + 4:i + 4 + ln])
        i += 4 + ln
    return bytes(out)


def _varint(b, i):
    n, shift = 0, 0
    while True:
        x = b[i]; i += 1
        n |= (x & 0x7F) << shift; shift += 7
        if x < 0x80:
            return n, i


def _fields(b):
    """protobuf 필드 목록 [(번호, 형식, 값)]"""
    i, out = 0, []
    while i < len(b):
        key, i = _varint(b, i)
        num, wt = key >> 3, key & 7
        if wt == 0:
            v, i = _varint(b, i)
        elif wt == 1:
            v = b[i:i + 8]; i += 8
        elif wt == 2:
            ln, i = _varint(b, i)
            v = b[i:i + ln]; i += ln
        elif wt == 5:
            v = b[i:i + 4]; i += 4
        else:
            raise ValueError("protobuf 형식 오류")
        out.append((num, wt, v))
    return out


def _iwa_storages(raw):
    """풀린 IWA에서 TSWP.StorageArchive의 글자들을 순서대로 꺼낸다"""
    texts, i = [], 0
    while i < len(raw):
        ln, i = _varint(raw, i)
        info, i = raw[i:i + ln], i + ln
        for num, _, msg in _fields(info):
            if num != 2:  # ArchiveInfo.message_infos
                continue
            mfields = _fields(msg)
            mtype = next((v for n, _, v in mfields if n == 1), None)
            mlen = next((v for n, _, v in mfields if n == 3), 0)
            payload, i = raw[i:i + mlen], i + mlen
            if mtype == TSWP_STORAGE:
                parts = [v.decode("utf-8", "replace") for n, wt, v in _fields(payload)
                         if n == 3 and wt == 2]
                if parts:
                    texts.append("".join(parts))
    return texts


def pages_text(data):
    z = zipfile.ZipFile(io.BytesIO(data))
    names = z.namelist()
    if "Index.zip" in names:  # 일부 Pages: 안쪽에 zip이 한 번 더
        z = zipfile.ZipFile(io.BytesIO(z.read("Index.zip")))
        names = z.namelist()
    if "Index/Document.iwa" in names:
        texts = _iwa_storages(_iwa_unpack(z.read("Index/Document.iwa")))
        texts.sort(key=len, reverse=True)  # 가장 긴 것이 본문, 나머지는 글상자·머리말 등
        body = "\n\n".join(t for t in texts if t.strip())
        # Pages의 줄바꿈 기호(U+2028/2029)와 개체 자리표(U+FFFC)를 정리
        body = body.replace(" ", "\n").replace(" ", "\n").replace("￼", "")
        return re.sub(r"\n{3,}", "\n\n", body).strip()
    for name in ("index.xml", "index.xml.gz"):  # 2009 형식
        if name in names:
            xml = z.read(name)
            if name.endswith(".gz"):
                import gzip
                xml = gzip.decompress(xml)
            xml = xml.decode("utf-8", "replace")
            xml = re.sub(r"</sf:p>|<sf:br/>|<sf:lnbr/>", "\n", xml)
            return re.sub(r"<[^>]+>", "", xml).strip()
    raise ValueError("Pages 본문을 찾지 못함 — Pages에서 PDF나 Word로 내보내 다시 주세요")


# ───────────────────────── 공통 ─────────────────────────
def _plain(data):
    return data.decode("utf-8-sig", "replace").replace("\r\n", "\n")


def read_any(path):
    """(제목, 텍스트)를 돌려준다. 입력 형식은 확장자와 내용으로 판단한다."""
    name = os.path.basename(path)
    data, title, mime = open(path, "rb").read(), name, ""
    # 드라이브 download_file_content 결과 JSON (도구가 .txt 이름으로 저장하기도 한다)
    if data[:1] == b"{":
        try:
            d = json.loads(data.decode("utf-8"))
            if isinstance(d, dict) and "content" in d:
                data, title, mime = base64.b64decode(d["content"]), d.get("title", name), d.get("mimeType", "")
        except ValueError:
            pass
    low = title.lower()
    if low.endswith(".hwp") or data[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return title, hwp_text(data)
    if low.endswith(".pages") or "iwork-pages" in mime:
        return title, pages_text(data)
    return title, _plain(data)  # 구글 문서(text/plain 내보내기)·txt·md


def main():
    outdir, inputs = sys.argv[1], sys.argv[2:]
    os.makedirs(outdir, exist_ok=True)
    for src in inputs:
        title, text = read_any(src)
        base = re.sub(r"\.(hwp|pages|txt|md)$", "", title, flags=re.I)
        base = re.sub(r'[\\/:*?"<>|]', "_", base)  # 파일 이름에 못 쓰는 글자
        out = os.path.join(outdir, base + ".txt")
        open(out, "w", encoding="utf-8").write(text)
        print(f"{title}: {len(text)}자 → {out}")


if __name__ == "__main__":
    main()
