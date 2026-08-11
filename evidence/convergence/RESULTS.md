# 수렴 실측 — feynman-explainer, Sonnet vs Opus (2026-07-07)

동일 개념을 두 모델이 작성했을 때 표면 유사도(convergence.sh, 문자 3-gram Jaccard).

| 티어 | 고정한 것 | 유사도 |
|---|---|---|
| 자유 생성 (baseline) | 없음 | 0.082 |
| 재현 모드 (비유뱅크+사실+구조) | 비유·수치·순서 | 0.567 (7배↑) |
| 템플릿 티어 | 위 + 문장 슬롯화 | **1.000 (byte-identical, 2026-07-07 측정)** |
| golden 동결 | 전부 | 1.00 |

- 개선 전 파일: DPTD run의 free-gen feynman (0.082).
- 개선 후 파일: 동일 `repro-spec.md`를 Sonnet/Opus에 준 결과 (feynman-repro-*.md).
- 남은 0.43 격차 = 같은 사실의 다른 문장 표현 = 경계 계약상 "목소리 필드"(모델 허용). 발산이 아니라 설계된 자유도.
- 재현: `bash gates/convergence.sh evidence/convergence/feynman-repro-sonnet.md evidence/convergence/feynman-repro-opus.md 0.55`

## 템플릿 티어 실측 (2026-07-07)
- 스펙 `repro-spec-template.md`(고정 스켈레톤 + 결정론 슬롯)을 Sonnet/Opus에 준 결과: 두 산출물 byte-identical, convergence 1.000.
- 재현: `bash gates/convergence.sh evidence/convergence/feynman-tpl-sonnet.md evidence/convergence/feynman-tpl-opus.md 0.70` → PASS.
- 대가: 이 티어에서 모델은 사실상 조립기다. 문장을 스켈레톤으로 고정한 만큼 모델 목소리는 0. 재현성 100% ↔ 목소리 0의 트레이드오프.
