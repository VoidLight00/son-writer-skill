#!/usr/bin/env bash
# 전자책 조립 HARD 게이트. books/*/ 아래 빌드 산출물을 검사한다. exit 0 PASS / 1 FAIL.
# fail-closed: python 이 죽어도 그 종료코드가 그대로 게이트 실패가 된다.
set -u
ROOT="${1:-$(pwd)}"; case "$ROOT" in --*) ROOT="$(pwd)";; esac
BOOKS="$ROOT/books"
[ -d "$BOOKS" ] || { echo "PASS[book]: books/ 없음 (검사 대상 없음)"; exit 0; }

python3 - "$ROOT" <<'PY'
import re, sys
from pathlib import Path

root = Path(sys.argv[1])
books = sorted(p for p in (root / "books").glob("*/*.html"))
rc = 0

def fail(name, msg):
    global rc; rc = 1
    print(f"FAIL[book]: {name} — {msg}")

if not books:
    print("PASS[book]: 빌드된 전자책 0건 (빌더만 있고 산출물 없음)")
    sys.exit(0)

# 원고 대비 커버리지 락 — 장을 빼서 통과하는 최단 경로를 막는다.
manuscripts = sorted((root / "output").glob("vibe-*.md"))

for p in books:
    name = p.name
    doc = p.read_text(encoding="utf-8")

    if len(doc) < 20_000:
        fail(name, f"산출물 {len(doc)}자 — 너무 작다 (최소 20000)")

    # 자체완결: 외부 호스트로 나가는 리소스 참조 0건이어야 한다.
    ext = re.findall(r'(?:src|href)\s*=\s*["\'](https?:)?//[^"\']+', doc)
    if ext:
        fail(name, f"외부 리소스 참조 {len(ext)}건 (자체완결 위반): {ext[:3]}")
    if re.search(r'@import\s+url\(\s*["\']?https?:', doc):
        fail(name, "CSS @import 로 외부 폰트/스타일 로드")

    # 세로줄 금지(전역 규칙) — 조립 단계에서 다시 확인한다.
    if re.search(r'border-(?:left|inline-start)\s*:\s*(?:[3-9]|\d{2,})px', doc):
        fail(name, "좌측 세로 스트라이프(border-left >=3px)")

    if "TODO" in doc:
        fail(name, "TODO 잔재")

    # 테마 3상태 배선 — 셋 중 하나만 빠져도 어느 한 부류의 독자가 못 읽는 화면을 본다.
    theme = {
        "명시 다크 규칙 :root[data-theme=\"dark\"]": '[data-theme="dark"]' in doc,
        "시스템 다크 규칙(라이트 선택 시 무효화)": 'prefers-color-scheme: dark' in doc
                                                and ':root:not([data-theme="light"])' in doc,
        "토글 버튼": 'id="themebtn"' in doc,
        "선택 저장(localStorage)": 'localStorage' in doc and 'vb-theme' in doc,
        "첫 페인트 전 적용 스크립트": doc.index("vb-theme") < doc.index("<style") if "vb-theme" in doc else False,
    }
    miss = [k for k, ok in theme.items() if not ok]
    if miss:
        fail(name, f"테마 배선 누락: {miss}")

    # 커버리지 락 — 목차에 이름만 남기고 본문을 빼는 최단 경로를 막는다.
    # 제목 문자열이 문서 어딘가 있는지가 아니라, 장 제목 자리(h3)에 있는지를 본다.
    heads = set(re.findall(r"<h3>(.*?)</h3>", doc, re.S))
    secs = len(re.findall(r'<section id="ch\d+" class="ch">', doc))
    if secs != len(manuscripts):
        fail(name, f"장 섹션 {secs}개 / 원고 {len(manuscripts)}편 — 개수 불일치")

    missing = []
    for m in manuscripts:
        lines = m.read_text(encoding="utf-8").splitlines()
        t = next((l[len("제목:"):].strip() for l in lines if l.startswith("제목:")), None)
        if t is None:
            fail(name, f"{m.name} 제목 줄 없음")
            continue
        esc = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if esc not in heads:
            missing.append(t[:24])
    if missing:
        fail(name, f"원고 {len(missing)}편이 본문에 없다(목차만 있을 수 있음): {missing[:3]}")

    # 본문 분량 하한 — 섹션 껍데기만 남기고 문단을 비우는 경로도 막는다.
    body_chars = sum(len(re.sub(r"<[^>]+>", "", p)) for p in re.findall(r"<p>.*?</p>", doc, re.S))
    if body_chars < 28_000:
        fail(name, f"본문 {body_chars:,}자 — 하한 28,000자 미달")

    if rc == 0:
        print(f"PASS[book]: {name} — 본문 {body_chars:,}자, 장 {secs}개 전량 수록, 외부 요청 0")

sys.exit(rc)
PY
rc=$?
[ "$rc" -ne 0 ] && exit 1
exit 0
