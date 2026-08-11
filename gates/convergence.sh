#!/usr/bin/env bash
# 모델 불변 수렴 게이트 — golden 참조본과 후보의 표면 유사도를 결정론으로 측정.
# 외부 임베딩 API 없음(오프라인, fail-closed). 문자 3-gram Jaccard.
# usage:
#   convergence_gate.sh <golden.md> <candidate.md> [threshold]   # 두 파일 비교
#   convergence_gate.sh --selftest                               # 자가검증
# exit 0 = 유사도 >= threshold(수렴), 1 = 미달/오류.
set -u

if [ "${1:-}" = "--selftest" ]; then
  python3 - <<'PY'
import re
def norm(t): return re.sub(r"\s+", "", t)
def sh(s, k=3): return {s[i:i+k] for i in range(len(s)-k+1)} if len(s) >= k else {s}
def jac(a, b):
    A, B = sh(a), sh(b)
    return 1.0 if not A and not B else len(A & B) / len(A | B)
ident = jac(norm("같은 문장 완전히 동일"), norm("같은 문장 완전히 동일"))
diff  = jac(norm("게이트는 놀이공원 키 재기 막대다"), norm("판정은 자판기와 같다 코인 넣으면 정해진 게 나온다"))
conv  = jac(norm("디렉티브는 주문서다 분량과 문체를 못박는다"), norm("디렉티브는 주문서다 분량과 문체를 선언한다"))
assert ident == 1.0, f"동일본 1.0 아님: {ident}"
assert diff < 0.30, f"다른글 낮아야: {diff}"
assert conv > 0.55, f"수렴본 높아야: {conv}"
print(f"selftest OK: ident={ident:.2f} diff={diff:.2f} conv={conv:.2f}")
PY
  exit $?
fi

GOLDEN="${1:-}"; CAND="${2:-}"; THRESH="${3:-0.80}"
[ -f "$GOLDEN" ] || { echo "FAIL[convergence]: golden 없음: $GOLDEN"; exit 1; }
[ -f "$CAND" ]   || { echo "FAIL[convergence]: candidate 없음: $CAND"; exit 1; }

python3 - "$GOLDEN" "$CAND" "$THRESH" <<'PY'
import sys, re

def normalize(p):
    t = open(p, "rb").read().decode("utf-8", "replace")
    # 마크다운·디렉티브·구두점·공백 제거 → 순수 내용 문자열
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = re.sub(r"[#*`|>_\-\[\](){}!?.,:;\"'/→…·]", " ", t)
    t = re.sub(r"\s+", "", t)
    return t

def shingles(s, k=3):
    return {s[i:i+k] for i in range(len(s) - k + 1)} if len(s) >= k else {s}

def jaccard(a, b):
    A, B = shingles(a), shingles(b)
    if not A and not B: return 1.0
    return len(A & B) / len(A | B)

g, c, th = normalize(sys.argv[1]), normalize(sys.argv[2]), float(sys.argv[3])
sim = jaccard(g, c)
ok = sim >= th
tag = "PASS" if ok else "FAIL"
print(f"{tag}[convergence]: 유사도 {sim:.3f} (임계 {th:.2f}) "
      f"golden={len(g)}자 cand={len(c)}자")
sys.exit(0 if ok else 1)
PY
