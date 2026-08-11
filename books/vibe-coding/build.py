#!/usr/bin/env python3
"""output/vibe-*.md 를 자체완결 단일 HTML 전자책으로 조립한다.

ponytail: 템플릿 엔진 없이 f-string. 외부 요청 0 — 폰트·스크립트·이미지 전부 인라인 또는 시스템.
소스는 son 게이트를 통과한 원고만 쓴다. 여기서 본문을 고치지 않는다(고칠 곳은 원고다).
"""
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]   # ~/projects/son-writer
SRC = ROOT / "output"
OUT = pathlib.Path(__file__).parent / "vibe-coding.html"

BOOK_TITLE = "선언은 증거가 아니다"
BOOK_SUB = "하네스와 검증 게이트로 세운 바이브 코딩 방법론"

# 부 구분 — 파일 slug 접두 번호로 묶는다.
PARTS = [
    (["00"], None, None),
    (["01", "02", "03"], "1부", "무엇이 우리를 속이는가"),
    (["04", "05", "06", "07", "08"], "2부", "하네스 — 반복되는 일의 레일"),
    (["09", "10", "11"], "3부", "게이트 — 판정을 기계로 옮기기"),
    (["12", "13", "14"], "4부", "컨텍스트와 여러 에이전트"),
    (["15"], "5부", "사람은 어디에 남는가"),
    (["99"], None, None),
]


def parse(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("<!-- son:"):
        sys.exit(f"디렉티브 없음: {path}")
    ti = next((i for i, l in enumerate(lines) if l.startswith("제목:")), None)
    if ti is None:
        sys.exit(f"제목 줄 없음: {path}")
    title = lines[ti][len("제목:"):].strip()
    body = "\n".join(lines[ti + 1:]).strip()
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    if not paras:
        sys.exit(f"본문 없음: {path}")
    return title, paras


def main():
    files = sorted(SRC.glob("vibe-*.md"))
    if not files:
        sys.exit("원고 없음: output/vibe-*.md")
    by_no = {re.search(r"vibe-(\d+)", f.name).group(1): f for f in files}

    chapters, toc, chars = [], [], 0
    for nums, part_no, part_name in PARTS:
        if part_no:
            toc.append(f'<li class="toc-part">{html.escape(part_no)} · {html.escape(part_name)}</li>')
            chapters.append(
                f'<div class="part"><span>{html.escape(part_no)}</span>'
                f'<h2>{html.escape(part_name)}</h2></div>'
            )
        for n in nums:
            f = by_no.get(n)
            if f is None:
                sys.exit(f"원고 누락: vibe-{n}-*.md")
            title, paras = parse(f)
            chars += sum(len(p.replace("\n", "")) for p in paras)
            cid = f"ch{n}"
            toc.append(f'<li><a href="#{cid}">{html.escape(title)}</a></li>')
            ps = "\n".join(f"<p>{html.escape(p)}</p>" for p in paras)
            chapters.append(
                f'<section id="{cid}" class="ch">'
                f'<h3>{html.escape(title)}</h3>{ps}</section>'
            )

    doc = TEMPLATE.format(
        title=html.escape(BOOK_TITLE),
        sub=html.escape(BOOK_SUB),
        count=len(files),
        chars=f"{chars:,}",
        toc="\n".join(toc),
        body="\n".join(chapters),
    )
    OUT.write_text(doc, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB) — {len(files)}편 / {chars:,}자")


TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<title>{title} — {sub}</title>
<script>
/* 첫 페인트 전에 저장된 테마를 붙인다 — 안 그러면 다크 사용자에게 흰 화면이 한 번 번쩍인다. */
(function(){{try{{var m=localStorage.getItem("vb-theme");
if(m==="light"||m==="dark")document.documentElement.setAttribute("data-theme",m);}}catch(e){{}}}})();
</script>
<style>
  /* 팔레트 출처: gyeongjun-ai-day/app/globals.css (:root 및 .method-section 다크 계열) */
  :root {{
    --paper:#f7f7f5; --surface:#ffffff; --soft:#efefec;
    --ink:#101010; --muted:#6d6d68; --rule:#deded9;
    --accent:#f5a623; --accent-ink:#7e5a13;
    --serif:"AppleMyungjo","Nanum Myeongjo","Noto Serif KR",serif;
    --sans:Arial,"Apple SD Gothic Neo",sans-serif;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --paper:#101010; --surface:#1b1b1b; --soft:#222222;
      --ink:#f3f3ef; --muted:#90908b; --rule:#2b2b2b;
      --accent:#f5a623; --accent-ink:#f5a623;
    }}
  }}
  :root[data-theme="dark"] {{
    --paper:#101010; --surface:#1b1b1b; --soft:#222222;
    --ink:#f3f3ef; --muted:#90908b; --rule:#2b2b2b;
    --accent:#f5a623; --accent-ink:#f5a623;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0 }}
  body {{ background:var(--paper); color:var(--ink); font-family:var(--serif);
         -webkit-font-smoothing:antialiased; word-break:keep-all; }}
  .wrap {{ display:grid; grid-template-columns:1fr; max-width:1180px; margin:0 auto; }}
  .coverwrap {{ max-width:1180px; margin:0 auto; padding:0 1.5rem; }}

  /* 테마 토글 — 라이트 / 다크 / 시스템 3상태 순환 */
  .themebtn {{ position:fixed; z-index:40; top:1rem; right:1rem;
    display:inline-flex; align-items:center; gap:.45rem; cursor:pointer;
    min-height:44px; padding:.6rem .95rem; border-radius:999px;
    border:1px solid var(--rule); background:var(--surface); color:var(--muted);
    font-family:var(--sans); font-size:.74rem; font-weight:700; letter-spacing:.02em;
    box-shadow:0 6px 20px rgba(16,16,16,.08); }}
  .themebtn:hover {{ color:var(--ink); }}
  .themebtn i {{ width:.5rem; height:.5rem; border-radius:50%;
                background:var(--accent); display:inline-block; }}

  nav {{ font-family:var(--sans); padding:2rem 1.5rem; border-bottom:1px solid var(--rule); }}
  nav h4 {{ font-size:.72rem; letter-spacing:.22em; color:var(--muted); font-weight:700;
           text-transform:uppercase; margin-bottom:1rem; }}
  nav ol {{ list-style:none; font-size:.86rem; line-height:1.6; }}
  nav li {{ margin:.36rem 0; }}
  /* ponytail: display:flex 를 쓰면 익명 플렉스 아이템이 min-width:auto 라 긴 제목이
     줄바꿈 없이 넘친다. 터치 타깃 44px 은 padding 으로 채운다. */
  nav a {{ color:var(--muted); text-decoration:none; display:block;
          padding:.72rem .5rem; border-radius:10px; min-height:2.75rem;
          overflow-wrap:break-word; transition:background .2s, color .2s; }}
  nav a:hover {{ color:var(--ink); background:var(--soft); }}
  .toc-part {{ font-size:.72rem; letter-spacing:.14em; color:var(--accent-ink);
              margin:1.4rem 0 .5rem; font-weight:700; }}

  main {{ padding:2rem 1.5rem 6rem; }}
  header.cover {{ padding:5rem 0 4rem; }}
  header.cover h1 {{ font-size:clamp(1.85rem,1.3rem + 2.8vw,3.1rem); line-height:1.3;
                    font-weight:400; letter-spacing:-.035em; text-wrap:balance;
                    overflow-wrap:break-word; }}
  header.cover p.sub {{ margin-top:1.1rem; font-size:clamp(1rem,.95rem + .3vw,1.15rem);
                       color:var(--muted); line-height:1.7; overflow-wrap:break-word; }}
  header.cover dl {{ display:flex; flex-wrap:wrap; gap:.6rem; margin-top:2.4rem;
                    font-family:var(--sans); }}
  header.cover dl > div {{ padding:.85rem 1.05rem; border-radius:14px;
                          background:var(--surface); border:1px solid var(--rule); }}
  header.cover dt {{ letter-spacing:.12em; text-transform:uppercase; font-size:.64rem;
                    color:var(--muted); font-weight:700; }}
  header.cover dd {{ color:var(--ink); font-size:.88rem; font-weight:700; margin-top:.3rem; }}

  .part {{ margin:5.5rem 0 2.5rem; padding-bottom:1.2rem; border-bottom:1px solid var(--rule); }}
  .part span {{ font-family:var(--sans); font-size:.72rem; letter-spacing:.2em; font-weight:700;
               color:var(--accent-ink); display:block; margin-bottom:.5rem; }}
  .part h2 {{ font-size:clamp(1.3rem,1.1rem + 1vw,1.75rem); font-weight:400; letter-spacing:-.02em; }}

  section.ch {{ max-width:37rem; margin:4rem 0; }}
  section.ch h3 {{ font-size:clamp(1.15rem,1.05rem + .55vw,1.42rem); font-weight:400;
                  line-height:1.5; letter-spacing:-.02em; margin-bottom:1.9rem; }}
  section.ch p {{ font-size:clamp(1rem,.97rem + .22vw,1.09rem); line-height:2.0;
                 letter-spacing:-.003em; }}
  section.ch p + p {{ margin-top:1.35em; }}

  footer {{ max-width:37rem; margin-top:6rem; padding:1.6rem; border-radius:18px;
           background:var(--surface); border:1px solid var(--rule);
           font-family:var(--sans); font-size:.8rem; color:var(--muted); line-height:1.9; }}

  @media (min-width:1000px) {{
    .wrap {{ grid-template-columns:16rem 1fr; gap:3rem; padding:0 1.5rem; }}
    nav {{ position:sticky; top:0; align-self:start; max-height:100vh; overflow-y:auto;
          border-bottom:0; border-right:1px solid var(--rule); padding:3rem 1rem 3rem 0; }}
    main {{ padding:3rem 1rem 8rem 0; }}
    header.cover {{ padding:6rem 0 4rem; }}
    .coverwrap {{ border-bottom:1px solid var(--rule); }}
  }}
  @media print {{
    .themebtn, nav {{ display:none }}
    body {{ background:#fff; color:#000 }}
    section.ch {{ break-inside:avoid-page }}
  }}
  @media (prefers-reduced-motion:reduce) {{ * {{ transition-duration:.01ms !important }} }}
</style>
</head>
<body>
<button class="themebtn" id="themebtn" type="button" aria-label="화면 테마 전환">
  <i></i><span id="themelabel">시스템</span>
</button>
<div class="coverwrap">
  <header class="cover">
    <h1>{title}</h1>
    <p class="sub">{sub}</p>
    <dl>
      <div><dt>분량</dt><dd>{count}편 · {chars}자</dd></div>
      <div><dt>집필</dt><dd>SON</dd></div>
      <div><dt>판정</dt><dd>게이트 종료코드 0</dd></div>
    </dl>
  </header>
</div>
<div class="wrap">
<nav>
  <h4>목차</h4>
  <ol>
{toc}
  </ol>
</nav>
<main>
{body}
  <footer>
    이 책의 모든 장은 집필 규칙 열한 가지를 종료코드로 검사하는 게이트를 통과했다.
    글자수 범위, 빈 부사, 번역투, 금지어, 순수 산문 여부, 문장 길이의 폭, 문두 접속사,
    어미 일관성, 반복 어휘 상한이 그 열한 가지다. 통과하지 못한 원고는 이 책에 실리지 않았다.
  </footer>
</main>
</div>
<script>
(function(){{
  var order = ["system", "dark", "light"];
  var label = {{ system:"시스템", dark:"다크", light:"라이트" }};
  var root = document.documentElement;
  var btn = document.getElementById("themebtn");
  var txt = document.getElementById("themelabel");
  function read(){{ try {{ return localStorage.getItem("vb-theme") || "system"; }} catch(e) {{ return "system"; }} }}
  function apply(mode){{
    if (mode === "system") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", mode);
    txt.textContent = label[mode];
    btn.setAttribute("aria-label", "화면 테마 전환 (현재 " + label[mode] + ")");
    try {{ if (mode === "system") localStorage.removeItem("vb-theme");
           else localStorage.setItem("vb-theme", mode); }} catch(e) {{}}
  }}
  apply(read());
  btn.addEventListener("click", function(){{
    apply(order[(order.indexOf(read()) + 1) % order.length]);
  }});
}})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
