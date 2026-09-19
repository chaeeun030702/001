# enterprise-ai-ui-standards — 줄간격·배치 안정화 보완본

텍스트 스케일을 **2단계 상향**한 뒤 생긴 **줄간격 벌어짐·배치 흔들림**을 바로잡은 스킬 보완본이다.

## 원인

- 스킬이 정의한 줄간격이 **본문 `1.7` 하나뿐**이었다. Title(40px)·Display(최대 80px) 같은 큰
  글자가 이 값을 상속해 줄 높이가 68~136px까지 벌어지고, 줄바꿈된 제목이 무너졌다. → **줄간격 불안**
- 버튼·인풋·테이블 행·사이드내비 행이 **고정 `height`**여서 커진 글자·줄바꿈이 잘렸다. → **배치 불안**
- 크기에 맞춘 **간격(spacing) 토큰**이 없어 리듬이 어긋났다. depth1 행 높이도 48px/52px로 불일치.

## 보완 내용

| 파일 | 변경 |
| --- | --- |
| `references/design-tokens.css` | 타이포 크기 토큰(`--fs-*`) + **계열별 line-height 토큰**(`--lh-display/title/heading/lede/body/dense/caption`) + 간격(`--space-1~9`) + 컨트롤 최소높이(`--control-h`·`--row-h`·`--nav-row-h`) 추가 |
| `references/patterns.md` | `body`·제목 리듬 규칙 추가, 큰 글자에 계열별 line-height 강제, 버튼·인풋·행·사이드내비를 고정 height → **`min-height`**로 전환 |
| `references/visualization.md` | KPI·플로우·계층도 수치/제목에 line-height 지정, 공통 규칙에 "큰 수치는 line-height 1.0~1.2" 추가 |
| `SKILL.md` | 타이포 표에 **Line-height 열** 추가, "1.7은 본문 전용" `[Must]` 규칙, `min-height` `[Must]` 규칙, `--space-*` 리듬 규칙, depth1 52px로 통일, 체크리스트 2항목 추가 |

핵심 규칙: **큰 글자일수록 줄간격을 좁힌다.** Title/Display 1.1~1.2 · Heading 1.3 · 본문 1.7 ·
라벨/표 셀 1.4. 컨트롤·행은 `height`가 아니라 `min-height`.

## 보완 2차 — 박스·도형 글자 크기 연동

박스·도형이 글자 크기에 맞춰 함께 커지고, 내부 글자·줄간격도 동일 규정을 따르도록 추가 보완했다.

| 파일 | 변경 |
| --- | --- |
| `design-tokens.css` | **em 기반 내부 여백 토큰**(`--pad-chip/-btn/-box/-card`)과 `--circle-size` 추가 → 글자 크기에 박스가 비례 |
| `patterns.md` | 「6. 박스·도형」 절 신설(콜아웃·칩·숫자 원형·stretch 정렬), 버튼·배지를 em 여백으로 전환, SVG 텍스트 대신 HTML/CSS 원칙 |
| `visualization.md` | 스택바·계층도·플로우 원형·태그를 em/`min-height`로 스케일, 텍스트 도형 HTML 원칙 |
| `SKILL.md` | "박스·도형은 글자에 연동" · "텍스트 도형은 HTML" `[Must]` 규칙, 체크리스트 2항목 추가 |

원칙: **텍스트가 든 박스·도형은 고정 px 크기 금지.** `em` 여백·`min-height`·`--circle-size`로 크기를 내면
글자를 키울 때 박스·여백·줄간격이 조화롭게 함께 조정된다. 텍스트가 든 도형은 리플로우가 되는 HTML/CSS로 그린다.

## 검증

`spacing-fix-proof.html`을 브라우저로 열면 동일 크기의 Before(결함 재현)/After(규격) 비교를 볼 수 있다.

## 재설치 방법

이 세션에서는 스킬을 계정에 직접 저장하는 도구가 없다. 아래 중 한 가지로 반영한다.

1. **claude.ai 설정 → Skills**에서 `enterprise-ai-ui-standards` 스킬을 이 폴더의 내용으로 갱신
   (`SKILL.md` + `references/` 3개 파일)한다.
2. 스킬을 플러그인/Notion으로 관리 중이면 해당 소스의 파일을 이 폴더 내용으로 교체 후 재동기화한다.

동기화 시 계정 원본이 로컬 사본을 덮어쓸 수 있으므로, 반드시 원본(계정/소스) 쪽을 갱신해야 영구 반영된다.
