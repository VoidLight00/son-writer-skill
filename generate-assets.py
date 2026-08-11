#!/usr/bin/env python3
"""SOn Writer 공개 저장소용 정보 그래픽 6장을 결정론적으로 만든다."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent / "assets"
ROOT.mkdir(parents=True, exist_ok=True)

INK = "#101010"
PAPER = "#F7F7F5"
SURFACE = "#FFFFFF"
MUTED = "#6D6D68"
RULE = "#DEDED9"
ACCENT = "#F5A623"
TEAL = "#0F766E"
RED = "#B42318"


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size, index=8 if bold and path.endswith(".ttc") else 0)
        except OSError:
            continue
    return ImageFont.load_default()


def canvas(size):
    return Image.new("RGB", size, PAPER), ImageDraw.Draw(Image.new("RGB", (1, 1)))


def make(size):
    image = Image.new("RGB", size, PAPER)
    return image, ImageDraw.Draw(image)


def text(draw, xy, value, size, color=INK, bold=False, anchor=None):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor, spacing=int(size * 0.35))


def rounded(draw, box, fill=SURFACE, outline=RULE, radius=28, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def dot(draw, x, y, color=ACCENT, radius=7):
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)


def hero():
    im, d = make((1600, 900))
    text(d, (110, 90), "SOn WRITER", 28, MUTED, True)
    text(d, (110, 190), "선언은 증거가 아니다", 82, INK, True)
    text(d, (110, 300), "한국어 글쓰기 감각을 열한 가지 규칙과\n종료코드로 판정하는 Claude Code 스킬", 38, MUTED)
    rounded(d, (110, 530, 670, 705), fill=INK, outline=INK, radius=34)
    text(d, (155, 580), "원고", 26, "#FFFFFF", True)
    text(d, (155, 625), "사람처럼 써줘", 34, "#FFFFFF")
    d.line((700, 618, 850, 618), fill=ACCENT, width=8)
    d.polygon([(850, 600), (885, 618), (850, 636)], fill=ACCENT)
    rounded(d, (915, 500, 1490, 735), radius=34)
    dot(d, 970, 560, TEAL, 9)
    text(d, (1000, 540), "VERIFY PASS", 28, TEAL, True)
    text(d, (970, 605), "exit 0", 64, INK, True)
    text(d, (970, 682), "자가보고가 아닌 실측 증거", 24, MUTED)
    im.save(ROOT / "hero.png")


def architecture():
    im, d = make((1600, 900))
    text(d, (100, 80), "SOn Writer · 검증 폐루프", 46, INK, True)
    labels = [
        ("01", "요청", "페르소나 · 분량 · 목적"),
        ("02", "집필", "SOn 규칙으로 초안 생성"),
        ("03", "판정", "11개 규칙 · 종료코드"),
        ("04", "공개", "통과한 산출물만 배포"),
    ]
    x_positions = [90, 470, 850, 1230]
    for i, ((no, title, sub), x) in enumerate(zip(labels, x_positions)):
        rounded(d, (x, 285, x+285, 610), radius=30)
        dot(d, x+45, 335, ACCENT if i != 2 else TEAL, 8)
        text(d, (x+70, 316), no, 22, MUTED, True)
        text(d, (x+40, 395), title, 46, INK, True)
        text(d, (x+40, 475), sub, 24, MUTED)
        if i < 3:
            d.line((x+300, 450, x+360, 450), fill=INK, width=4)
            d.polygon([(x+360, 438), (x+382, 450), (x+360, 462)], fill=INK)
    text(d, (800, 735), "FAIL이면 원고로 돌아가 수정 · PASS일 때만 다음 단계", 28, RED, True, "mm")
    im.save(ROOT / "architecture.png")


def og():
    im, d = make((1200, 630))
    d.rectangle((0, 0, 1200, 630), fill=INK)
    dot(d, 90, 88, ACCENT, 10)
    text(d, (120, 70), "SOn WRITER", 25, "#D7D7D2", True)
    text(d, (90, 185), "사람처럼 썼다는 말보다", 55, "#FFFFFF", True)
    text(d, (90, 265), "종료코드 0을 보여주세요.", 55, "#FFFFFF", True)
    rounded(d, (90, 430, 500, 535), fill=ACCENT, outline=ACCENT, radius=24)
    text(d, (295, 482), "FAIL-CLOSED KOREAN WRITING", 22, INK, True, "mm")
    text(d, (1110, 520), "VOIDLIGHT", 22, "#A8A8A3", True, "rm")
    im.save(ROOT / "og.png")


def gallery_one():
    im, d = make((1000, 1000))
    text(d, (70, 70), "01 · REQUIREMENTS", 24, MUTED, True)
    text(d, (70, 145), "막연한 감각을\n측정 가능한 조건으로", 54, INK, True)
    checks = ["글자수 범위", "번역투·금지어", "문장 리듬", "어미 일관성", "반복 어휘 상한"]
    y = 390
    for item in checks:
        rounded(d, (70, y, 930, y+88), radius=20)
        dot(d, 118, y+44, TEAL, 7)
        text(d, (150, y+26), item, 27, INK, True)
        y += 105
    im.save(ROOT / "gallery-1.png")


def gallery_two():
    im, d = make((1000, 1000))
    text(d, (70, 70), "02 · HARD GATE", 24, MUTED, True)
    text(d, (70, 145), "판정은 모델의 감상이 아니라\n프로세스의 종료코드", 50, INK, True)
    rounded(d, (70, 370, 930, 760), fill=INK, outline=INK, radius=30)
    text(d, (115, 420), "$ bash gates/verify_son.sh .", 28, "#D7D7D2", True)
    text(d, (115, 525), "FAIL[son_text]", 42, "#FF8A80", True)
    text(d, (115, 590), "번역투 표현 2건 · 반복 어휘 상한 초과", 25, "#FFFFFF")
    text(d, (115, 690), "exit 1", 32, ACCENT, True)
    text(d, (70, 850), "실패를 숨기지 않고 수정 루프로 돌려보냅니다.", 27, MUTED)
    im.save(ROOT / "gallery-2.png")


def gallery_three():
    im, d = make((1000, 1000))
    text(d, (70, 70), "03 · VERIFIED OUTPUT", 24, MUTED, True)
    text(d, (70, 145), "통과한 글만\n책과 공개본에 들어갑니다", 54, INK, True)
    rounded(d, (70, 380, 930, 770), radius=30)
    dot(d, 135, 450, TEAL, 10)
    text(d, (170, 425), "VERIFY PASS", 32, TEAL, True)
    text(d, (120, 535), "17편", 70, INK, True)
    text(d, (390, 535), "30,668자", 70, INK, True)
    text(d, (120, 650), "자체완결 HTML 전자책 · 외부 요청 0", 29, MUTED)
    text(d, (70, 855), "선언은 증거가 아니다", 32, INK, True)
    im.save(ROOT / "gallery-3.png")


if __name__ == "__main__":
    hero()
    architecture()
    og()
    gallery_one()
    gallery_two()
    gallery_three()
    print("generated 6 PNG assets")
