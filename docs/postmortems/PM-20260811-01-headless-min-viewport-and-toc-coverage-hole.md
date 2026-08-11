---
type: postmortem
id: PM-20260811-01
project: son-writer
date: 2026-08-11
severity: P3
duration: 25m
status: resolved
---

# PM-20260811-01: 전자책 조립 게이트가 장 삭제를 통과시키고, 스크린샷 클리핑을 가로 넘침으로 오판했다

## 1. 요약

바이브 코딩 방법론 전자책(17편·30,668자)을 조립하면서 두 건이 났다. 첫째, `book_gate.sh`의 커버리지 락이 제목 문자열의 문서 내 존재만 봐서 장 하나를 통째로 지워도 PASS 했다 — 목차 `<a>`에 남은 제목이 통과시켰다.
둘째, headless Chrome이 `--window-size=390`을 무시하고 최소 500px로 렌더하는데 스크린샷만 390으로 잘려 나와, 있지도 않은 가로 넘침을 진단하고 CSS를 두 번 고쳤다.

## 2. 증상

게이트 음성 테스트에서 4종 중 1종만 못 잡았고, 모바일 렌더는 부제가 잘려 보였다.

```
② 한 장을 통째로 들어냄:
   PASS[book]: b.html — 37,329자, 원고 17편 전량 수록, 외부 요청 0   ← 잡아야 하는데 통과

계측기 주입 후 실측:
   vw=500  scrollW=500  OVERFLOW(0)                                  ← 넘침은 처음부터 0
```

## 3. 타임라인

- 17:20 가설: 게이트가 장 삭제를 잡는다 → 시도: `<section id="ch10">` 정규식 삭제 후 게이트 → 결과: FAIL — exit 0으로 통과
- 17:22 가설: 제목 존재 검사가 목차에서 만족된다 → 시도: 판정 위치를 `<h3>`로 좁히고 section 개수·본문 하한 추가 → 결과: PASS — 음성 테스트 4종 전부 차단
- 17:28 가설: 390px에서 가로 넘침이 있다 → 시도: `nav a`의 `display:flex` 제거 후 재렌더 → 결과: FAIL — 스크린샷이 여전히 잘림
- 17:31 가설: 계측기가 틀렸다 → 시도: 페이지에 스크립트를 주입해 `clientWidth`/`scrollWidth` 표시 → 결과: FAIL — vw=500, 넘침 0. 창 크기 지정이 안 먹었다
- 17:32 가설: iframe으로 폭을 강제하면 진짜 값이 나온다 → 시도: `--allow-file-access-from-files` + iframe 320/390/430/768 프로브 → 결과: PASS — 전 폭 overflow=0, 44px 미만 링크 0

## 4. 근본 원인

첫째는 커버리지 락의 판정 범위가 넓었다. 문서 전체를 대상으로 문자열 포함을 보면 목차·헤더·메타 어디서든 만족되므로, 본문이 비어도 통과한다.
둘째는 계측기의 성질을 확인하지 않았다. macOS headless Chrome은 창 최소 폭이 있어 `--window-size`보다 넓게 렌더하고, 스크린샷은 지정 폭으로 잘린다. 잘린 그림은 레이아웃 증거가 아니다.

## 5. 관점 분석

- 기술: 존재 검사는 판정 위치를 좁히지 않으면 항상 fail-open이다. 그래픽 캡처는 레이아웃 값이 아니라 렌더 결과의 사본일 뿐이다.
- 프로세스: 게이트를 만든 직후 음성 테스트를 돌린 덕분에 첫 건은 배포 전에 잡혔다. 반대로 렌더 검증에는 음성 테스트가 없었고 그래서 두 번 헛고쳤다.
- AI협업: 스크린샷 한 장을 근거로 원인을 단정하고 곧장 CSS를 고쳤다. 고치기 전에 계측기부터 의심했으면 15분이 절약됐다.

## 6. 해결

```bash
# 커버리지 락을 본문 자리로 좁히고 개수·분량 하한을 추가
heads = set(re.findall(r"<h3>(.*?)</h3>", doc, re.S))
secs  = len(re.findall(r'<section id="ch\d+" class="ch">', doc))
body_chars = sum(len(re.sub(r"<[^>]+>", "", p)) for p in re.findall(r"<p>.*?</p>", doc, re.S))

# 레이아웃은 캡처가 아니라 iframe 프로브로 실측
"$CH" --headless --allow-file-access-from-files --virtual-time-budget=8000 ...
# w=320/390/430/768  scrollW==clientW  overflow=0  link<44px=0
```

## 7. 재발 방지

- `~/projects/son-writer/gates/book_gate.sh` — h3 판정 + section 개수 + 본문 28,000자 하한
- `~/projects/son-writer/REQUIREMENTS.md` — R12(자체완결)·R13(커버리지 락) 행 추가
- `~/projects/son-writer/FAILURE_LOG.md` — SW005·SW006 기록

## 8. 다음 세션 룰 후보

스크린샷은 레이아웃 증거가 아니다. 반응형 판정은 `clientWidth`/`scrollWidth` 실측값으로만 하고, 캡처 도구의 최소 렌더 폭을 먼저 확인한다.
