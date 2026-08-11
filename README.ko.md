[English](README.md) | [한국어](README.ko.md)

<div align="center">

# SOn Writer

![SOn Writer 대표 이미지](assets/hero.png)

**“사람처럼”이라는 감각을 종료코드로 판정하는 한국어 글쓰기 스킬**

![License](https://img.shields.io/badge/License-MIT-yellow.svg) ![Language](https://img.shields.io/badge/language-Korean-0f766e.svg) ![Claude%20Code](https://img.shields.io/badge/Claude%20Code-skill-f5a623.svg) ![QA](https://img.shields.io/badge/QA-fail--closed-111111.svg)

</div>

SOn Writer는 글쓰기 페르소나와 열한 가지 문체 요구사항을 재사용 가능한 Claude Code 스킬로 묶습니다. 모델이 “자연스럽다”고 자평하는 것은 증거로 인정하지 않으며, HARD 게이트가 종료코드 0을 반환한 원고만 통과시킵니다.

## 들어 있는 것

- `SKILL.md` — 설치 가능한 Claude Code 스킬 계약
- `REQUIREMENTS.md` — 글쓰기 규칙의 단일 진실 원천
- `gates/` — 글자수·금지어·번역투·리듬·어미·반복·시크릿·전자책 검증 게이트
- `references/` — 재배포 가능한 한국어 글쓰기 참고자료와 출처 원장
- `evidence/convergence/` — 모델이 달라도 같은 방향으로 수렴하는지 측정한 증거
- `books/vibe-coding/vibe-coding.html` — 같은 엔진으로 집필한 17편짜리 자체완결 전자책

## 스킬 설치

```bash
git clone https://github.com/VoidLight00/son-writer-skill.git
mkdir -p ~/.claude/skills/son-writer
cp son-writer-skill/SKILL.md ~/.claude/skills/son-writer/SKILL.md
```

기본 스킬은 이 저장소가 `~/projects/son-writer`에 있다고 가정합니다. 다른 위치를 쓰면 로컬 스킬 설정에서 경로만 바꾸면 됩니다.

## 글을 쓰고 판정하기

`output/` 아래에 Markdown 파일을 만들고 첫 줄에 허용 글자수 범위를 선언합니다.

```md
<!-- son: min=1200 max=1800 -->
제목: 골목 끝의 지도 앱

본문을 여기에 씁니다.
```

그다음 판정기를 실행합니다.

```bash
bash gates/verify_son.sh .
```

종료코드 0만 통과입니다. 실패하면 `FAIL[게이트]: 이유` 토큰이 출력되어 수정 루프가 어느 부분을 고쳐야 하는지 알 수 있습니다.

## 열한 가지 규칙을 다루는 방식

기계가 확인할 수 있는 것은 기계가 판정하고, 의미 판단은 명시적으로 남깁니다. 글자수, 빈 부사, 번역투, AI 특유의 금지 어휘, 순수 산문 여부, 문장 길이의 폭, 문두 접속사, 어미 일관성, 반복 어휘 상한, 시크릿, 공개본 완전성을 HARD 게이트로 확인합니다.

![SOn Writer 구조](assets/architecture.png)

## 결과 예시

함께 들어 있는 전자책 **선언은 증거가 아니다**는 17편·30,668자 분량입니다. 외부 요청이 없는 단일 HTML이며 라이트·다크·시스템 테마를 지원합니다.

브라우저에서 `books/vibe-coding/vibe-coding.html`을 열면 됩니다.

## 검증 증거

| 규칙 | Fail-closed 판정 | 통과 산출물 |
|---|---|---|
| ![감각을 측정 가능한 조건으로 바꿉니다](assets/gallery-1.png) | ![종료코드가 0이 아니면 원고를 거절합니다](assets/gallery-2.png) | ![검증된 글만 공개본에 들어갑니다](assets/gallery-3.png) |

## 안전과 라이선스

공개 배포본에는 개인 코퍼스와 재배포할 수 없는 참고 코드를 넣지 않았습니다. `ksanyok/TextHumanize`는 출처 원장에 아이디어의 근거로 기록하지만, 상업 이용 조건이 MIT와 다르므로 원본 코드를 포함하지 않습니다.

[보안 정책](.github/SECURITY.md), [지원 안내](.github/SUPPORT.md), [기여 안내](.github/CONTRIBUTING.md)를 확인해 주세요.

## 라이선스

MIT © 2026 VOIDLIGHT. 자세한 내용은 [LICENSE](LICENSE)를 확인해 주세요.
