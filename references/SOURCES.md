# references — 원본 규칙 소스 원장 (vendored 2026-07-04)

| repo | commit | license | vendored files | 엔진 반영 |
|---|---|---|---|---|
| dotoricode/korean-humanizer | 7dff5b4 | MIT | PROMPT.md, CHEATSHEET.md | 12 카테고리 → R2~R4 절대금지 + R10 캡 어휘 + SOFT 치환 지침 |
| devswha/patina | 2280f3d | MIT | patterns/ko-*.md 7종 | §7 고빈도 AI 어휘(발화조건: 문단당 3+) → R10 캡, MPS 의미보존 → SOFT |
| ksanyok/TextHumanize | c536af4 | Dual (개인/비상업 무료, 상업 별도) | (미포함 — 아래 주석 참조) | 문장 리듬·오프라인 자연화 아이디어 → R6 문장 다양화. **상업 사용 시 라이선스 재확인 필요** |
| NYT ai-writing-quiz (2026-03-09) | — | 뉴스 인용 (요약만 보관, 원문 미복제) | nyt-ai-writing-quiz-2026-03-09.md | Claude 시그니처 대구 → R11 캡, 아포리즘 클로저·비숍 원칙 → SOFT |

원칙: 게이트(`gates/son_text_gate.sh`)는 위 소스 중 기계 검증 가능한 부분만 exit code로 강제하고,
빈도 판단·치환 같은 변환 로직은 집필 시 SOFT 지침으로 따른다. 규칙 갱신 시 이 원장의 commit을 함께 올린다.


## 공개본 주석 — 재배포하지 않는 것

`ksanyok/TextHumanize` 의 `lang/ko.py` 는 개인·비상업 무료, 상업 사용 별도 조건인 이중 라이선스다. 이 저장소는 MIT 이므로 해당 파일을 함께 배포하지 않는다. 필요하면 원본 저장소에서 직접 받는다. 엔진에 반영된 것은 파일이 아니라 아이디어(문장 리듬 다양화)이고, 그 강제는 `gates/son_text_gate.sh` 의 R6 가 한다.
