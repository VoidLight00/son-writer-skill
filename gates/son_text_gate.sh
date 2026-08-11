#!/usr/bin/env bash
# SOn 인간화 텍스트 HARD 게이트 — REQUIREMENTS.md R1~R8. exit 0 PASS / 1 FAIL.
# usage: son_text_gate.sh <ROOT>   (output/*.md 전수 검사, fail-closed)
set -u
ROOT="${1:-$(pwd)}"
OUT_DIR="$ROOT/output"
[ -d "$OUT_DIR" ] || { echo "PASS[son_text]: no output/ yet (nothing to check)"; exit 0; }

python3 - "$OUT_DIR" <<'PY'
import sys, os, re, glob

out_dir = sys.argv[1]
files = sorted(glob.glob(os.path.join(out_dir, "*.md")) + glob.glob(os.path.join(out_dir, "*.txt")))
if not files:
    print("PASS[son_text]: no output files yet"); sys.exit(0)

BANNED = [  # R2~R4: (표시명, 정규식)
    ("빈부사:매우", r"매우"), ("빈부사:굉장히", r"굉장히"),
    ("빈부사:상당히", r"상당히"), ("빈부사:극도로", r"극도로"),
    ("번역투:통해", r"통해"), ("번역투:에 있어", r"에 있어"), ("번역투:에 의해", r"에 의해"),
    ("금지어:활용", r"활용"), ("금지어:극대화", r"극대화"), ("금지어:시사한다", r"시사한"),
    ("금지어:주목할 만", r"주목할\s*만"), ("금지어:도모", r"도모"), ("금지어:결론적으로", r"결론적으로"),
]
# R10 캡 어휘 — korean-humanizer cat.12 + patina ko-language §7 (원문: references/). 각 ≤1회, 합계 ≤3회.
CAPPED = ["다양한", "폭넓은", "광범위한", "포괄적인", "종합적인", "전반적인", "혁신적인",
          "체계적인", "효과적인", "지속적인", "심층적인", "유기적인", "선도적인", "활발한",
          "아울러", "나아가", "더불어", "뿐만 아니라", "요컨대", "강화", "통합", "도출",
          "모색", "함의", "저변", "일환", "촉진", "이러한", "해당 ", "것이다", "되어지", "에 대한"]
EMOJI = re.compile(r"[\U0001F000-\U0001FAFF☀-➿⬀-⯿]")
rc = 0
def fail(f, msg):
    global rc; rc = 1
    print(f"FAIL[son_text]: {os.path.basename(f)}: {msg}")

for f in files:
    text = open(f, "rb").read().decode("utf-8", "replace")
    lines = text.splitlines()
    # R7 디렉티브
    m = re.match(r"<!--\s*son:\s*min=(\d+)\s+max=(\d+)(?:\s+style=(haeyo|dache))?\s*-->", lines[0].strip() if lines else "")
    if not m:
        fail(f, "R7 첫 줄 디렉티브 없음: <!-- son: min=N max=N [style=haeyo|dache] -->"); continue
    mn, mx = int(m.group(1)), int(m.group(2))
    style = m.group(3) or "haeyo"
    # 제목 줄
    title_idx = next((i for i, l in enumerate(lines) if l.startswith("제목:")), None)
    if title_idx is None:
        fail(f, "제목: 줄 없음"); continue
    body = "\n".join(lines[title_idx + 1:]).strip()
    flat = body.replace("\n", "")
    # R1 글자수 (공백 포함, 줄바꿈 제외)
    n = len(flat)
    if not (mn <= n <= mx):
        fail(f, f"R1 글자수 {n}자 (요구 {mn}~{mx}, 공백포함)")
    # R2~R4 금지 패턴
    for name, pat in BANNED:
        hits = re.findall(pat, body)
        if hits:
            fail(f, f"{name} {len(hits)}회")
    # R5 마크다운/이모지
    if "**" in body or "__" in body:
        fail(f, "R5 볼드 마커")
    for l in body.splitlines():
        if re.match(r"\s*(#|[-*]\s|\d+[.)]\s)", l):
            fail(f, f"R5 리스트/헤딩 라인: {l[:30]!r}"); break
    if EMOJI.search(body):
        fail(f, "R5 이모지")
    # R6 문장 길이 다양화
    sents = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", body.replace("\n", " ")) if s.strip()]
    slens = [len(s) for s in sents] or [0]
    if min(slens) > 25 or max(slens) < 70:
        fail(f, f"R6 문장길이 단조 (min={min(slens)} max={max(slens)}, 요구 min<=25 & max>=70)")
    # R8 문두 접속사
    conj = sum(1 for s in sents if re.match(r"(그리고|하지만|그러나)[ ,]", s))
    if conj > 3:
        fail(f, f"R8 문두 접속사 {conj}회 (<=3)")
    # R10 고빈도 AI 어휘 캡 (patina 발화조건을 글 단위로 보수화)
    cap_hits = {w: body.count(w) for w in CAPPED if body.count(w) > 0}
    for w, c in cap_hits.items():
        if c > 1:
            fail(f, f"R10 캡 어휘 반복: {w!r} {c}회 (각 <=1)")
    if sum(cap_hits.values()) > 3:
        fail(f, f"R10 캡 어휘 합계 {sum(cap_hits.values())}회 (<=3): {sorted(cap_hits)}")
    # R11 "아니라" 대구 캡 — NYT 퀴즈(2026-03-09)에서 Claude 승리작 공통 수사로 확인 (references/nyt-*).
    # ponytail: 표면형 "아니라"만 카운트, "아니에요" 피벗까지 잡으려면 부정문 오탐 대비 필요
    anira = len(re.findall(r"아니라", body))
    if anira > 2:
        fail(f, f"R11 '아니라' 대구 구문 {anira}회 (<=2)")
    # R9 어미 일관성 — 10% 허용은 인용문/도치문 몫. ponytail: 어미 표면형만 검사, 반말 조어까지는 안 잡음
    da_end = sum(1 for s in sents if re.search(r"다[.!?…]*$", s))
    yo_end = sum(1 for s in sents if re.search(r"[요죠][.!?…]*$", s))
    cap = max(1, int(len(sents) * 0.10))
    if style == "haeyo" and da_end > cap:
        fail(f, f"R9 어미 드리프트: 해요체 글에 -다체 문장 {da_end}개 (허용 {cap})")
    if style == "dache" and yo_end > cap:
        fail(f, f"R9 어미 드리프트: -다체 글에 요/죠체 문장 {yo_end}개 (허용 {cap})")
    if rc == 0:
        no_space = len(flat.replace(" ", ""))
        print(f"PASS[son_text]: {os.path.basename(f)} — {n}자(공백포함)/{no_space}자(공백제외), 문장 {len(sents)}개 (min {min(slens)}/max {max(slens)}자), style={style} (다체어미 {da_end}/요체어미 {yo_end})")
sys.exit(rc)
PY
rc=$?
[ "$rc" -ne 0 ] && exit 1
exit 0
