# humanize-korean 스킬 수정 작업 기록

- 작업 브랜치: `claude/ecstatic-hopper-6fzh0s` (저장소 `chaeeun030702/001`)
- 결과물: `humanize-korean.zip` (저장소 루트)
- 목적: 스킬로 문서 파일(.hwpx·.docx·.pptx)을 다듬을 때 **글꼴·크기·굵기·배치 등 다른 것은 바꾸지 않고 텍스트만** 고치도록 한다.

## 1. 작업 경과

| 순서 | 요청 | 한 일 | 커밋 |
|---|---|---|---|
| 1 | 기존 font 및 규격은 손대지 말고 유지하도록 스킬 수정 후 zip 변환 | `SKILL.md`에 원칙 6번(글꼴과 규격 보존)과 "파일을 다듬을 때" 절 추가, 체크리스트에 보존 항목 7개 추가 | `8b3307c` |
| 2 | 스킬 적용 시 폰트 사이즈·배치가 바뀌는 사유 | 원인 6가지 설명 (아래 2절) | — |
| 3 | 폰트 굵기도 바뀜 | 스킬 자체의 "볼드 걷어내기" 규칙과 1차 수정의 "첫 런에 몰아넣기" 규칙이 원인임을 확인. 굵기 보존 규칙 추가, 서식 관련 문체 규칙을 마크다운 전용으로 한정 | `4cadc87` |
| 4 | 바뀐 hwpx 파일 첨부 | 파일 분석: `header.xml` 재저장, 본문 글자 모양 새로 생성, `linesegarray` 전부 제거 흔적 확인. 본문 외 파트 바이트 보존 규칙 추가 | `3322d51` |
| 5 | 원본 hwpx 첨부 | 원본과 비교: 문서가 통째로 재생성됨 (글꼴 함초롬바탕 → 한양신명조/바탕, 크기·굵기·색 변경, 이미지 20개 교체). 생성 스크립트 재실행 금지 규칙 추가 | `128961f` |
| 6 | 다른 것은 바뀌지 않고 텍스트만 수정토록 스킬 수정 | `scripts/textonly.py`(extract/apply/verify) 작성, 파일 작업은 이 스크립트로만 하도록 `SKILL.md`·체크리스트 재작성 | `478bda2` |
| 7 | 원본 파일로 재검정 | 새 스킬 절차로 교정 → 4문장 수정, "검증 통과 — 텍스트 외 변경 없음" | — |

## 2. 서식이 바뀌던 원인

1. **문서를 새로 만듦** — 텍스트만 뽑아 고친 뒤 새 문서에 붙이면 글꼴·크기·여백·스타일이 기본값이 된다.
2. **문단 전체 덮어쓰기** — python-docx `paragraph.text =`, python-pptx `text_frame.text =`는 기존 런과 그 서식(굵게·색·크기)을 지운다. HWPX에서 새 런을 만들 때 `charPrIDRef`를 옮기지 않아도 같다.
3. **한글 글꼴 칸 누락** — python-docx `run.font.name`은 `eastAsia` 칸을 바꾸지 않아 한글만 다른 글꼴이 된다.
4. **분량 변화** — 줄바꿈·쪽 나눔이 바뀌고, PowerPoint 자동 맞춤이 글꼴 크기를 다시 계산한다. 문단 합치기·불릿 제거는 스타일과 번호 서식을 없앤다.
5. **HWPX 줄 배치 캐시** — `hp:linesegarray`를 문서 전체에서 지우면 고치지 않은 문단까지 다시 배치된다.
6. **형식 변환** — LibreOffice·PDF 경유 변환에서 글꼴이 대체된다.
7. **굵기 관련 (3차에서 확인)**
   - 스킬의 `ai-tells.md` "볼드 남용", 체크리스트 "볼드를 걷어냈는가"가 파일에도 적용됨
   - 1차 수정에서 넣은 "여러 런에 걸친 문장은 첫 런에 몰아넣기" 규칙이 굵은 범위를 번지게 하거나 없앰
   - 굵기가 이름에 든 글꼴(`Pretendard SemiBold` 등)의 이름 변경·대체

## 3. 첨부 파일 분석 결과

### 3-1. 바뀐 파일(단독 분석)

| 항목 | 확인 결과 | 의미 |
|---|---|---|
| zip | 이미지는 9/19, `mimetype`은 9/27 22:10 | 스크립트로 다시 묶음 |
| `header.xml`, `settings.xml` | 선언부가 `<?xml version='1.0' ...?>` | 파이썬이 다시 저장 |
| 글자 모양 | 정의 46개 중 본문은 26~41번만 사용 | 본문을 새로 만들며 글자 모양을 새로 붙임 |
| 런 | 문단 3,150개 중 다중 런 53개 | 부분 서식이 합쳐졌을 가능성 |
| 문단 스타일 | 전부 `바탕글` | 스타일 서식 소실 가능 |
| `linesegarray` | 0개 | 전체 줄 배치 재계산 |
| 글꼴 | 한글 `한양신명조`, 영문 `바탕` | PC에 없으면 대체 글꼴로 표시 |

### 3-2. 원본과 비교

- 글꼴: 원본 `함초롬바탕`(한·영) → 바뀐 파일 `한양신명조`/`바탕`
- 같은 문장끼리 대조한 크기·굵기 변화

| 대상 | 원본 | 바뀐 파일 | 수 |
|---|---|---|---|
| 표 본문 | 8.6pt | 8.5pt | 994 |
| 표 머리글 | 8.6pt 굵게 | 9.5pt 굵게 | 74 |
| 표 일부 | 9.5pt | 11.0pt | 22 |
| 소제목(3.2~3.4) | 11.0pt 보통 | 11.5pt 굵게 | 4 |
| 출처·주석 | 9.4pt | 9.0pt | 3 |

- 색: 제목의 남색(`#002A5C`, `#243244`)·회색(`#2B3644`, `#4A5666`) → 검정
- 문단 수 3,097 → 3,150, 글자 모양 정의 27 → 44, 이미지 20개 모두 다른 파일
- 문장은 1,821개 중 1,799개가 동일 → **글은 거의 그대로인데 문서를 생성 스크립트로 다시 만든 것**이 원인

## 4. 재검정 결과 (수정된 스킬 적용)

- 대상: 원본 `...2.hwpx` (재검정용으로 받은 파일과 바이트 단위 동일)
- 텍스트 조각 2,947개 추출, 클리셰 후보 14건 중 논문 문맥상 어색한 4곳만 교정 (강도: 약하게)

| 원문 | 교정 |
|---|---|
| 전기작업의 관점에서 중요한 것은 첫 번째 유형이다. | 전기작업에서 문제가 되는 것은 첫 번째 유형이다. |
| 이 고정이 필수적이다. | 이 고정이 반드시 필요하다. |
| 번역의 정확성보다 중요한 것은 안전에 직결되는 항목의 누락을 막는 일이다. | 번역의 정확성보다 안전에 직결되는 항목이 빠지지 않게 하는 일이 더 중요하다. |
| 이 설계는 자동화가 사용자의 판단을 대체하지 않는다는 연구의 원칙을 구현 수준에서 보장하기 위한 것이다. | 자동화가 사용자의 판단을 대체하지 않는다는 연구 원칙을 구현 수준에서 지키려는 설계다. |

- `textonly.py apply` 결과: **검증 통과 — 텍스트 외 변경 없음**
- zip 항목 53개 중 52개 바이트 동일, 다른 것은 `Contents/section0.xml`뿐 (그 안도 글자만 다름)
- 문단 수·런 수·글자/문단 모양·스타일 번호, 항목 순서·압축 방식 모두 원본과 동일
- 같은 검증을 이전의 바뀐 파일에 돌리면 이미지 20개·`header.xml`·본문 서식 변경이 모두 검출되어 실패
- docx·pptx는 직접 만든 작은 예시 파일로만 확인. 한글·Word·PowerPoint에서 직접 열어 보지는 않음
- 교정본 hwpx는 논문 원고라 저장소에 커밋하지 않았고, 작업 컨테이너가 바뀌며 임시 폴더의 파일은 삭제됨. 필요하면 아래 절차로 다시 만들 수 있다.

```bash
python scripts/textonly.py extract 원본.hwpx segments.json
# segments.json 의 "text" 값만 고친다
python scripts/textonly.py apply   원본.hwpx segments.json 교정본.hwpx
```

## 5. 최종 스킬 파일 전문

`humanize-korean.zip` 안의 파일 6개다.

### `humanize-korean/SKILL.md`

`````markdown
---
name: humanize-korean
description: 한국어 글에서 AI가 쓴 듯한 흔적(번역체, 과장 수식어, 불릿 남용, 정형화된 도입·마무리, 피동 남용)을 걷어내고 사람이 쓴 것처럼 자연스럽게 다듬는다. 초안 검토, 블로그·보고서·이메일·공지·제품 문구 교정, "AI 같다 / 어색하다 / 자연스럽게 고쳐줘 / 사람처럼 써줘 / 번역체 빼줘 / 딱딱하다"는 요청, 또는 한국어 텍스트를 생성한 직후 자체 점검할 때 사용한다. 사실 관계와 존댓말 수준은 유지하며, .docx·.pptx·.hwpx 등 파일을 다듬을 때도 기존 글꼴과 규격(크기·서식·레이아웃)은 그대로 둔다.
---

# Humanize Korean

한국어 텍스트를 **의미는 그대로 두고** 읽는 사람이 "사람이 썼다"고 느끼게 다듬는다.

## 원칙

1. **사실을 바꾸지 않는다.** 숫자, 고유명사, 인용, 주장, 조건은 그대로. 근거 없는 구체화(없던 통계·일화 추가)는 금지.
2. **삭제가 1순위 도구다.** 대체 표현을 찾기 전에 먼저 지워 본다. AI 문장의 어색함은 대개 과잉에서 온다.
3. **어투를 유지한다.** 원문이 `~습니다`면 `~습니다`로, `~다`면 `~다`로. 존댓말 등급, 격식 수준, 1인칭/3인칭을 임의로 바꾸지 않는다.
4. **일부러 망가뜨리지 않는다.** 오타, 비문, 과한 구어체, 유행어를 넣어 "사람처럼" 보이게 만들지 않는다. 자연스러움은 정확함과 충돌하지 않는다.
5. **전문성은 보존한다.** 업계 용어, 법률·의료·기술 용어는 유지. 다듬는 대상은 포장이지 내용이 아니다.
6. **파일에서는 텍스트만 바꾼다.** 바꾸는 것은 글자뿐이다. 글꼴 종류·크기·굵기·색, 줄·자간 간격, 문단 정렬·들여쓰기, 표·셀 크기, 페이지·슬라이드 크기와 여백, 스타일 이름은 원본 그대로 둔다. 사용자가 명시적으로 요청하지 않는 한 "보기 좋게" 서식을 바꾸지 않는다.

## 작업 순서

1. **읽고 진단한다.** 전체를 훑고 `references/ai-tells.md`의 항목 중 실제로 나타난 것만 꼽는다. 없는 문제를 고치려 하지 않는다.
2. **강도를 정한다.** 사용자가 지정하지 않았으면 **기본**으로 진행하고 결과에 강도를 밝힌다.
   - **약하게** — 명백한 번역체와 과장어만. 문단 구조는 그대로. (계약서, 공문, 인용 많은 글)
   - **기본** — 문장 단위 재작성 허용. 문단 순서와 뼈대는 유지. (대부분의 경우)
   - **강하게** — 문단 통합·분리, 불릿을 산문으로 재구성, 도입·마무리 재작성. (블로그, 소개글, 마케팅)
3. **고친다.** `references/rewrite-patterns.md`의 변환 규칙을 적용한다.
4. **검수한다.** `references/checklist.md`로 점검. 특히 사실 누락과 어미 반복을 확인.
5. **출력한다.** 아래 형식.

## 파일(.hwpx · .docx · .pptx)을 다듬을 때 — 텍스트만 바꾼다

파일 작업에서 바꿔도 되는 것은 **글자뿐**이다. 글꼴, 크기, 굵기, 색, 간격, 정렬, 표, 이미지, 스타일, 쪽 설정, 문단·런 구조는 모두 원본 그대로 둔다. 이를 지키려고 **반드시 `scripts/textonly.py`로만 파일을 고친다.**

```bash
python scripts/textonly.py extract  원본.hwpx  segments.json      # 1. 텍스트 조각 추출
#                                                                   2. segments.json 의 "text" 값만 고침
python scripts/textonly.py apply    원본.hwpx  segments.json  교정본.hwpx   # 3. 적용 + 자동 검증
python scripts/textonly.py verify   원본.hwpx  교정본.hwpx         # (필요 시) 따로 검증
```

- **스크립트가 하는 일.** 원본 zip의 항목 순서·압축 방식을 그대로 복사하고, 본문 XML(`Contents/section*.xml`, `word/document.xml` 등, `ppt/slides/slide*.xml`) 안의 텍스트 조각 문자만 문자열로 교체한다. XML을 파싱해 다시 저장하지 않는다. HWPX는 글자가 바뀐 문단의 `hp:linesegarray`만 지워 한글이 줄 배치를 다시 계산하게 한다.
- **`segments.json`에서 지킬 것.**
  - `text` 값만 고친다. 조각을 추가·삭제하거나 `id`를 바꾸지 않는다. 지우려면 빈 문자열 `""`로 둔다.
  - `fmt`(예: `9.5pt 굵게`)가 다른 조각 사이로 글자를 옮기지 않는다. 굵은 조각의 글자는 굵은 조각 안에서만 고친다. 문장이 여러 조각에 걸쳐 경계를 살려 고칠 수 없으면 원문대로 두고 `확인 필요`에 적는다.
  - 공백만 있는 조각(`" "`)과 번호·기호 조각은 건드리지 않는다.
  - 문단(`p`)을 합치거나 나눌 수 없다. 강도가 "강하게"여도 파일에서는 문장 단위까지만 고친다.
- **검증을 통과해야 끝난다.** `apply`는 끝에 자동으로 `verify`를 돌린다. "검증 통과 — 텍스트 외 변경 없음"이 나와야 교정본을 넘긴다. 실패하면 교정본을 버리고 원인을 고쳐 다시 만든다. 검증 결과 문구를 사용자에게 함께 보고한다.
- **금지.** 아래 방법은 서식을 바꾸므로 쓰지 않는다.
  - 새 문서를 만들어 내용을 옮겨 붙이기 (python-docx `Document()`, python-pptx `Presentation()`, hwpx 새로 생성)
  - 문서를 만든 생성 스크립트를 고친 원고로 다시 실행하기
  - python-docx·python-pptx·lxml·ElementTree 등으로 열어 다시 저장하기 (`paragraph.text =`, `text_frame.text =`, `fit_text()`, `run.font.*` 포함)
  - LibreOffice·PDF 경유 변환, docx↔hwpx 변환
  - 분량이 줄거나 늘었다고 글꼴 크기·상자 크기·간격을 조정하기 (넘칠 것 같으면 문장을 더 줄이고, 안 되면 `확인 필요`에 적는다)
- **서식 관련 문체 규칙은 파일에 적용하지 않는다.** `references/ai-tells.md`의 "볼드 남용·이모지", `references/rewrite-patterns.md`의 "불릿 → 산문"은 마크다운·일반 텍스트 전용이다.
- **지원하지 않는 형식**(.hwp, .doc, .ppt, .pdf, .xlsx 등)은 파일을 직접 고치지 않는다. 다듬은 글을 텍스트로 주고, 사용자가 원본에 붙여 넣도록 안내한다. 변환해서 고치지 않는다.

## 출력 형식

````
## 다듬은 글

(전문. 원문 서식 — 제목 단계, 링크, 코드블록 — 은 유지. 파일 작업이면 `textonly.py`로 만든 교정본 파일을 함께 제공하고, 검증 결과 문구를 적는다)

## 주요 변경

- (무엇을 왜 고쳤는지 3~6줄. 예: "`~할 수 있습니다` 7회 → 단정형으로 교체")

## 확인 필요

- (의미가 달라질 수 있어 판단이 필요한 부분. 없으면 이 절 생략)
````

짧은 문장 하나를 고치는 요청이면 형식을 생략하고 고친 문장만 준다.

## 자주 놓치는 것

- **어미 반복.** 같은 종결어미가 3문장 연속이면 AI 냄새가 난다. 서술어 형태를 섞되 어투 등급은 유지.
- **문장 길이 균일함.** 모든 문장이 40~60자면 사람 글이 아니다. 짧은 문장(10자 이하)을 의도적으로 섞는다.
- **불릿 반사.** 항목이 대등하고 3개 이상이 아니면 불릿이 아니라 문장이다.
- **마무리 요약.** "결론적으로", "정리하면", "도움이 되셨길 바랍니다"는 대개 통째로 삭제 대상.
- **과잉 친절.** "~에 대해 궁금하셨을 텐데요", "좋은 질문입니다" 같은 서론은 지운다.

## 참고 파일

- `references/ai-tells.md` — AI 흔적 목록 (구조 / 어휘 / 문장 / 서식)
- `references/rewrite-patterns.md` — before → after 변환 대조표
- `references/checklist.md` — 제출 전 점검 항목
- `scripts/textonly.py` — .hwpx·.docx·.pptx 파일에서 텍스트만 바꾸고, 텍스트 외 변경이 없는지 검증한다. 파일 작업에서는 필수.
- `scripts/find_tells.py` — 흔한 클리셰 표현을 정규식으로 찾아 위치와 빈도를 보고. 긴 글이나 반복 교정에서 먼저 돌리면 편하다. 판정 도구가 아니라 후보 목록 생성기다.

```bash
python scripts/find_tells.py draft.md
```
`````

### `humanize-korean/references/ai-tells.md`

`````markdown
# AI 흔적 목록

진단용 체크리스트. **실제로 나타난 항목만** 고친다.

## 1. 구조

| 흔적 | 설명 |
|---|---|
| 정형 3단 구성 | 도입 한 문단 → 불릿 3개 → 요약 한 문단이 모든 글에 반복 |
| 질문 되풀이 서론 | "~에 대해 궁금하셨을 텐데요", "~이 무엇인지 알아보겠습니다" |
| 3의 법칙 과다 | 항목·예시·형용사가 늘 3개. 실제로는 2개거나 5개인 경우가 많다 |
| 대칭 문단 | 모든 문단이 3~4문장, 길이가 거의 같음 |
| 마무리 요약 | "결론적으로", "정리하면", "종합해 보면", "요약하자면" |
| 맺음 인사 | "도움이 되셨길 바랍니다", "참고하시기 바랍니다", "함께 알아보았습니다" |
| 불필요한 소제목 | 200자 분량에 `##` 제목이 4개 |
| 양비론 마무리 | "장점도 있지만 단점도 있으므로 상황에 맞게 판단해야 합니다" |

## 2. 어휘

**과장 수식어** — 대개 삭제 대상
혁신적인 · 획기적인 · 강력한 · 압도적인 · 눈부신 · 폭발적인 · 필수적인 · 핵심적인 · 매우 중요한 · 놀라운 · 완벽한 · 최적의 · 차원이 다른 · 진정한

**공허한 명사화**
효율성 증대 · 최적화 · 극대화 · 활성화 · 고도화 · 유기적 연계 · 시너지 · 인사이트 · 니즈 · 밸류 · 솔루션 · 패러다임

**`~적(的)` 남용**
전략적 접근 · 효과적 활용 · 체계적 관리 · 긍정적 영향 · 실질적 도움
→ 구체 동작으로: "전략적으로 접근한다" → "무엇을 먼저 할지 정한다"

**정형 문형**
- "단순히 A가 아니라 B입니다" / "A일 뿐만 아니라 B이기도 합니다"
- "중요한 것은 ~라는 점입니다"
- "~라고 할 수 있습니다" / "~인 셈입니다" / "~라 볼 수 있습니다"
- "~에 대한 이해를 높이는 데 도움이 됩니다"
- "~의 세계로 함께 들어가 봅시다"
- "오늘은 ~에 대해 이야기해 보려 합니다"
- "A는 B의 핵심입니다"

**접속부사 과다**
또한 · 게다가 · 더불어 · 아울러 · 나아가 · 한편 · 그러나 · 따라서 · 이처럼 · 이렇듯
→ 문단마다 하나씩 붙어 있으면 절반은 지운다.

## 3. 문장

**번역체**
| 흔적 | 원인 |
|---|---|
| "우리는 ~해야 합니다" | we 직역. 한국어는 주어를 생략한다 |
| "당신의 ~를" | your 직역. "고객의", 또는 생략 |
| "~를 통해" | through/via 직역. "~로", "~해서" |
| "~에 있어서" | in terms of 직역. "~에서", 삭제 |
| "~와 관련하여" | regarding 직역. "~는" |
| "~의 경우에는" | in the case of 직역. 대개 삭제 |
| "~하는 것이 가능합니다" | it is possible to 직역. "~할 수 있다", 또는 단정 |
| "가장 ~한 것 중 하나" | one of the most. 순위를 밝히거나 삭제 |
| "~함에 따라" | as 직역 |

**피동·사동 남용**
~되어집니다 (이중 피동, 비문) · ~지게 됩니다 · ~로 여겨집니다 · ~것으로 보여집니다 (비문) · ~시켜 줍니다 · ~하도록 해 줍니다
→ 능동으로. "개선되어집니다" → "개선된다" / "나아진다"

**자신 없는 완충 표현**
~일 수 있습니다 · ~할 수 있습니다 · 경우에 따라 · 일반적으로 · 대체로 · ~인 편입니다
→ 실제로 불확실할 때만 남기고, 아니면 단정한다.

**지시어 반복**
"이는", "이것은", "그것은"으로 문장을 시작하는 습관. 지시 대상을 명사로 되살린다.

**주술 거리 과다**
"A가 B를 C하는 D를 E하여 F한 G는 H이다" 식의 긴 관형절 사슬. 두 문장으로 쪼갠다.

## 4. 서식

> 이 절은 마크다운·일반 텍스트에만 적용한다. .docx·.pptx·.hwpx 파일의 굵게·불릿·표·이모지는 원본대로 둔다.

- 소제목 앞 이모지 (📌 ✨ 🚀 💡)
- 볼드 남용: 한 문단에 **강조**가 세 곳
- 화살표 `→`, `em dash(—)`, 불릿 안 콜론 `항목: 설명` 의 기계적 반복
- 표를 쓸 필요 없는 2행 비교를 표로 만듦
- 모든 불릿이 같은 품사·같은 길이로 정렬됨
`````

### `humanize-korean/references/rewrite-patterns.md`

`````markdown
# 변환 대조표

## 문장 단위

| Before | After |
|---|---|
| 우리는 데이터를 효과적으로 관리해야 합니다. | 데이터를 제대로 관리해야 한다. |
| 이 기능을 통해 생산성을 극대화할 수 있습니다. | 이 기능을 쓰면 일이 빨라진다. |
| 해당 이슈는 다음 릴리스에서 해결될 것으로 보여집니다. | 다음 릴리스에서 고친다. |
| 성능이 개선되어지는 효과가 있습니다. | 성능이 빨라진다. |
| 이는 단순히 속도 문제가 아니라 구조의 문제입니다. | 속도가 아니라 구조가 문제다. |
| 비용 절감에 있어서 중요한 역할을 합니다. | 비용을 줄여 준다. |
| 사용자의 니즈를 파악하는 것이 핵심입니다. | 사용자가 뭘 원하는지 알아야 한다. |
| 다양한 방법을 활용하여 최적화를 수행할 수 있습니다. | 몇 가지 방법으로 최적화할 수 있다. |
| 결론적으로, 이 전략은 매우 효과적인 접근이라고 할 수 있습니다. | (삭제) |
| API 호출과 관련하여 주의할 점이 있습니다. | API 호출에 주의할 점이 있다. |
| 보고서 작성의 경우에는 시간이 오래 걸립니다. | 보고서 작성은 오래 걸린다. |
| 가장 널리 쓰이는 도구 중 하나입니다. | 많이 쓰는 도구다. |
| 테스트를 수행하는 것이 가능합니다. | 테스트할 수 있다. |
| 팀 간 유기적인 협업이 요구됩니다. | 팀끼리 손발이 맞아야 한다. |

## 삭제 목록

문장 앞뒤에 붙어 아무 정보도 더하지 않는 것들. 조건 없이 지운다.

- 좋은 질문입니다 / 흥미로운 지점입니다
- ~에 대해 궁금하셨을 텐데요
- 지금부터 하나씩 살펴보겠습니다
- 아래 내용을 참고해 보세요
- 도움이 되셨길 바랍니다
- 결론적으로 / 정리하면 / 종합해 보면 / 요약하자면
- 앞서 언급했듯이 (바로 위 문단을 가리킬 때)
- 무엇보다 중요한 것은
- 다시 말해 (뜻이 바뀌지 않는 반복일 때)

## 불릿 → 산문

> 마크다운·일반 텍스트 전용. 파일에서는 불릿과 번호 매기기를 원본대로 두고 문장만 다듬는다.

불릿을 유지할 조건: 항목이 **대등**하고, **3개 이상**이고, **순서나 선택**을 나타낸다.
아니면 문장으로 되돌린다.

**Before**
```
캐시 도입의 효과:
- **응답 속도**: 크게 개선됩니다
- **서버 부하**: 감소합니다
```

**After**
```
캐시를 붙이면 응답이 빨라지고 서버 부하도 줄어든다.
```

## 리듬 만들기

AI 문장은 길이가 균일하다. 짧은 문장을 섞어 호흡을 만든다.

**Before**
> 이번 개편에서는 검색 정확도를 높이기 위해 색인 구조를 변경했으며, 이를 통해 평균 응답 시간이 단축되는 효과를 얻을 수 있었습니다. 또한 오타 보정 기능을 추가하여 사용자 경험이 개선되었습니다.

**After**
> 이번 개편에서 색인 구조를 바꿨다. 검색이 빨라졌다. 오타 보정도 붙였다. 예전에는 "결재"로 검색하면 아무것도 안 나왔다.

마지막 문장 같은 구체적 예시는 **원문에 근거가 있을 때만** 추가한다. 없으면 만들지 말고 `확인 필요`에 적는다.

## 어미 다양화 (어투 등급 유지)

`~습니다` 체를 유지하면서도 반복을 피하는 법:

- 평서: ~합니다 / ~입니다
- 명사 종결: ~기 때문입니다 / ~라는 뜻입니다
- 의문: ~일까요? (남용 금지, 문단당 최대 1회)
- 청유: ~해 보세요 / ~하면 됩니다
- 부정: ~하지 않습니다 / ~할 필요는 없습니다

`~다` 체:
- ~한다 / ~이다 / ~았다 / ~지 않는다 / ~일 뿐이다 / ~면 된다

## 격식 수준별 허용 범위

| 문서 | 허용 |
|---|---|
| 공문·계약·약관 | 어휘 교정만. 문장 구조와 법적 표현 유지 |
| 보고서·제안서 | 번역체 제거, 과장어 삭제. 구어체 도입은 금지 |
| 블로그·뉴스레터 | 구어체 허용. 문단 재구성 허용 |
| 이메일·메신저 | 짧게. 인사말 한 줄, 본문 바로 |
| UI 문구·에러 메시지 | 짧고 능동. 사용자가 할 행동을 먼저 |
`````

### `humanize-korean/references/checklist.md`

`````markdown
# 제출 전 점검

## 사실 보존 (최우선)

- [ ] 숫자, 날짜, 금액, 단위가 원문과 같은가
- [ ] 고유명사(제품·회사·인명)와 표기가 그대로인가
- [ ] 인용문과 코드블록을 건드리지 않았는가
- [ ] 원문에 없던 주장·통계·일화를 더하지 않았는가
- [ ] 조건·예외("단, ~인 경우", "~를 제외하고")를 빠뜨리지 않았는가
- [ ] 링크와 각주가 살아 있는가

## 자연스러움

- [ ] 같은 종결어미가 3문장 연속으로 나오지 않는가
- [ ] 가장 긴 문장과 가장 짧은 문장의 길이 차이가 나는가
- [ ] `~적`, `~성`, `~화`로 끝나는 명사가 문단당 2개 이하인가
- [ ] 접속부사로 시작하는 문단이 절반 이하인가
- [ ] "이는 / 이것은"으로 시작하는 문장이 2개 이하인가
- [ ] 과장 수식어가 남아 있지 않은가
- [ ] 이중 피동(`~되어집니다`, `~보여집니다`)이 없는가

## 형식

- [ ] 원문의 어투 등급(`~습니다` / `~다` / 반말)을 유지했는가
- [ ] 제목 단계, 표, 코드블록 등 서식이 유지됐는가
- [ ] 불릿으로 남긴 것이 정말 대등한 목록인가
- [ ] (마크다운·일반 텍스트만) 불필요한 이모지와 볼드를 걷어냈는가
- [ ] 마무리 요약·인사 문단을 지웠는가

## 텍스트만 바꿨는가 (파일 작업 시)

- [ ] `scripts/textonly.py`의 extract → apply 로만 고쳤는가 (새 문서 생성, 생성 스크립트 재실행, 라이브러리로 다시 저장, 형식 변환을 하지 않았는가)
- [ ] `segments.json`에서 `text` 값만 고쳤고, 조각 추가·삭제나 `id` 변경이 없는가
- [ ] `fmt`가 다른 조각(굵게·크기 차이) 사이로 글자를 옮기지 않았는가
- [ ] `apply` 결과가 "검증 통과 — 텍스트 외 변경 없음"인가 (실패면 교정본을 넘기지 않는다)

## 마지막 확인

- [ ] 소리 내어 읽었을 때 걸리는 곳이 없는가
- [ ] 분량이 원문보다 줄었는가 (대개 10~25% 줄어드는 게 정상)
- [ ] 판단이 필요한 부분을 `확인 필요`에 적었는가
`````

### `humanize-korean/scripts/textonly.py`

`````python
#!/usr/bin/env python3
"""Edit only the text of .hwpx / .docx / .pptx files, never the formatting.

    python textonly.py extract  원본.hwpx  segments.json
    (segments.json 의 "text" 값만 고친다)
    python textonly.py apply    원본.hwpx  segments.json  교정본.hwpx
    python textonly.py verify   원본.hwpx  교정본.hwpx

extract  본문 XML의 텍스트 조각(segment)을 문단별로 JSON에 뽑는다.
apply    원본 zip을 항목 순서·압축 방식 그대로 복사하면서, 바뀐 텍스트 조각의
         문자만 원본 XML 문자열 안에서 교체한다. XML을 파싱해 다시 저장하지 않으므로
         글꼴·크기·굵기·색·스타일 참조·이미지·header 등은 바이트 단위로 유지된다.
         HWPX는 텍스트가 바뀐 문단의 <hp:linesegarray>만 지워 줄 배치를 다시 계산하게 한다.
verify   두 파일을 비교해 텍스트 외의 차이가 있으면 목록을 출력하고 종료 코드 1을 돌려준다.
"""

import html
import json
import re
import sys
import zipfile
from xml.sax.saxutils import escape

FORMATS = {
    "hwpx": dict(p="hp:p", r="hp:run", t="hp:t", lineseg="hp:linesegarray",
                 parts=re.compile(r"^Contents/section\d+\.xml$")),
    "docx": dict(p="w:p", r="w:r", t="w:t", lineseg=None,
                 parts=re.compile(r"^word/(document|header\d*|footer\d*|footnotes|endnotes|comments)\.xml$")),
    "pptx": dict(p="a:p", r="a:r", t="a:t", lineseg=None,
                 parts=re.compile(r"^ppt/(slides/slide|notesSlides/notesSlide)\d+\.xml$")),
}
TAG = re.compile(r"<(/?)([A-Za-z_][\w.-]*:?[\w.-]*)([^>]*?)(/?)>|<\?[^>]*\?>|<!--.*?-->", re.S)


def fmt_of(path):
    ext = path.rsplit(".", 1)[-1].lower()
    if ext not in FORMATS:
        sys.exit(f"지원하지 않는 형식: .{ext} (hwpx, docx, pptx만 가능)")
    return ext, FORMATS[ext]


def scan(xml, f):
    """Return (segments, paragraphs, linesegs).

    segments: [{start, end, para, run_attrs, run_raw}]  -- text chunk spans inside <t>
    linesegs: [(start, end, para)]                       -- HWPX line layout caches
    """
    segs, linesegs = [], []
    pstack, para_count = [], 0
    in_t = 0
    run_attrs, run_start = "", 0
    ls_start = None
    last_end = 0
    for m in TAG.finditer(xml):
        if in_t and m.start() > last_end:
            segs.append(dict(start=last_end, end=m.start(), para=pstack[-1] if pstack else -1,
                             run_attrs=run_attrs, run_raw=xml[run_start:m.start()]))
        last_end = m.end()
        close, name, attrs, selfclose = m.group(1), m.group(2), m.group(3), m.group(4)
        if name is None:
            continue
        if name == f["p"]:
            if close:
                pstack.pop()
            elif not selfclose:
                pstack.append(para_count)
                para_count += 1
        elif name == f["r"] and not close:
            run_attrs, run_start = attrs or "", m.start()
        elif name == f["t"] and not selfclose:
            in_t += -1 if close else 1
        elif f["lineseg"] and name == f["lineseg"]:
            if selfclose:
                linesegs.append((m.start(), m.end(), pstack[-1] if pstack else -1))
            elif close and ls_start is not None:
                linesegs.append((ls_start, m.end(), pstack[-1] if pstack else -1))
                ls_start = None
            else:
                ls_start = m.start()
    return segs, linesegs


def char_props(z):
    """HWPX charPr id -> (pt size, bold)."""
    try:
        h = z.read("Contents/header.xml").decode("utf-8")
    except KeyError:
        return {}
    out = {}
    for i, body in re.findall(r'<hh:charPr id="(\d+)"(.*?)</hh:charPr>', h, re.S):
        size = re.search(r'height="(\d+)"', body)
        out[i] = (int(size.group(1)) / 100 if size else None, "<hh:bold" in body)
    return out


def describe(ext, seg, cprops):
    if ext == "hwpx":
        m = re.search(r'charPrIDRef="(\d+)"', seg["run_attrs"])
        if m and m.group(1) in cprops:
            size, bold = cprops[m.group(1)]
            return f"{size:g}pt" + (" 굵게" if bold else "")
        return ""
    raw = seg["run_raw"]
    if ext == "docx":
        return "굵게" if re.search(r'<w:b(\s(?![^>]*w:val="(0|false)")[^>]*)?/>', raw) else ""
    return "굵게" if re.search(r'<a:rPr[^>]*\sb="(1|true)"', raw) else ""


def body_parts(z, f):
    return [n for n in z.namelist() if f["parts"].match(n)]


def extract(src, out):
    ext, f = fmt_of(src)
    with zipfile.ZipFile(src) as z:
        cprops = char_props(z) if ext == "hwpx" else {}
        result = {"source": src, "note": "text 값만 고친다. 조각을 추가·삭제하거나 id를 바꾸지 않는다. "
                  "서식이 다른 조각 사이로 글자를 옮기지 않는다. 지우려면 빈 문자열로 둔다.", "parts": {}}
        total = 0
        for part in body_parts(z, f):
            xml = z.read(part).decode("utf-8")
            segs, _ = scan(xml, f)
            paras = {}
            for i, s in enumerate(segs):
                item = {"id": i, "text": html.unescape(xml[s["start"]:s["end"]])}
                d = describe(ext, s, cprops)
                if d:
                    item["fmt"] = d
                paras.setdefault(s["para"], []).append(item)
            result["parts"][part] = [{"p": p, "segs": v} for p, v in paras.items()]
            total += len(segs)
    with open(out, "w", encoding="utf-8") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=1)
    print(f"{total}개 텍스트 조각 → {out}")


def apply(src, seg_json, dst):
    ext, f = fmt_of(src)
    edits = json.load(open(seg_json, encoding="utf-8"))["parts"]
    changed_total = 0
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w") as zout:
        parts = set(body_parts(zin, f))
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename in parts and info.filename in edits:
                xml = data.decode("utf-8")
                segs, linesegs = scan(xml, f)
                new = {s["id"]: s["text"] for p in edits[info.filename] for s in p["segs"]}
                if set(new) != set(range(len(segs))):
                    sys.exit(f"{info.filename}: 조각 id가 원본과 다르다 (추가·삭제 금지). 다시 extract 하라.")
                cuts, dirty = [], set()
                for i, s in enumerate(segs):
                    old_raw = xml[s["start"]:s["end"]]
                    if new[i] != html.unescape(old_raw):
                        if ext == "docx" and new[i] != new[i].strip() and "xml:space" not in s["run_raw"][-200:]:
                            print(f"경고: {info.filename} 조각 {i} 앞뒤 공백이 Word에서 사라질 수 있음")
                        cuts.append((s["start"], s["end"], escape(new[i])))
                        dirty.add(s["para"])
                cuts += [(a, b, "") for a, b, p in linesegs if p in dirty]
                for a, b, rep in sorted(cuts, reverse=True):
                    xml = xml[:a] + rep + xml[b:]
                changed_total += len(dirty)
                data = xml.encode("utf-8")
            zout.writestr(info, data, compress_type=info.compress_type)
    print(f"텍스트가 바뀐 문단 {changed_total}개 → {dst}")
    return verify(src, dst)


def skeleton(xml, f):
    segs, linesegs = scan(xml, f)
    cuts = [(s["start"], s["end"]) for s in segs] + [(a, b) for a, b, _ in linesegs]
    for a, b in sorted(cuts, reverse=True):
        xml = xml[:a] + xml[b:]
    return xml


def verify(orig, edited):
    ext, f = fmt_of(orig)
    problems = []
    with zipfile.ZipFile(orig) as a, zipfile.ZipFile(edited) as b:
        na, nb = a.namelist(), b.namelist()
        if na != nb:
            problems.append(f"zip 항목 목록·순서가 다름: 추가 {sorted(set(nb) - set(na))}, 빠짐 {sorted(set(na) - set(nb))}")
        parts = set(body_parts(a, f))
        for info in a.infolist():
            n = info.filename
            if n not in nb:
                continue
            if b.getinfo(n).compress_type != info.compress_type:
                problems.append(f"{n}: 압축 방식이 다름")
            da, db = a.read(n), b.read(n)
            if da == db:
                continue
            if n in parts:
                if skeleton(da.decode("utf-8"), f) != skeleton(db.decode("utf-8"), f):
                    problems.append(f"{n}: 텍스트 외 서식·구조(문단·런·속성·참조)가 바뀜")
            else:
                problems.append(f"{n}: 본문이 아닌 파트가 바뀜 (글꼴·스타일·이미지 등)")
    if problems:
        print("검증 실패 — 텍스트 외 변경:")
        for p in problems:
            print("  -", p)
        return 1
    print("검증 통과 — 텍스트 외 변경 없음")
    return 0


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    cmds = {"extract": (extract, 2), "apply": (apply, 3), "verify": (verify, 2)}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds or len(sys.argv) != cmds[sys.argv[1]][1] + 2:
        sys.exit(__doc__)
    fn, _ = cmds[sys.argv[1]]
    return fn(*sys.argv[2:]) or 0


if __name__ == "__main__":
    sys.exit(main())
`````

### `humanize-korean/scripts/find_tells.py`

`````python
#!/usr/bin/env python3
"""Scan Korean text for common AI-writing tells.

Usage:
    python find_tells.py draft.md
    cat draft.md | python find_tells.py

Reports line numbers and counts for cliche phrases, translationese,
double passives and hedges. Candidates only -- a hit is not a verdict,
and clean output does not mean the text reads naturally.
"""

import re
import sys
from collections import defaultdict

PATTERNS = [
    # (category, regex, note)
    ("과장 수식어", r"혁신적|획기적|압도적|눈부신|폭발적|필수적|핵심적|매우 중요|놀라운|차원이 다른|진정한", "대개 삭제"),
    ("공허한 명사", r"효율성|극대화|고도화|활성화|유기적|시너지|인사이트|니즈|솔루션|패러다임", "구체어로 교체"),
    ("정형 문형", r"단순히 .{1,20}(가|이) 아니라|뿐만 아니라|중요한 (것|점)은|라고 할 수 있|인 셈|볼 수 있습니다", "재작성"),
    ("번역체", r"우리는|당신의|를 통해|을 통해|에 있어서|와 관련하여|과 관련하여|의 경우에는|것이 가능|중 하나(입니다|이다)|함에 따라", "직역 흔적"),
    ("이중 피동", r"되어지|보여집니다|불려집니다|쓰여집니다|잊혀집니다", "비문"),
    ("완충 표현", r"할 수 있습니다|일 수 있습니다|경우에 따라|일반적으로|대체로|인 편입니다", "단정 검토"),
    ("맺음 클리셰", r"결론적으로|정리하(면|자면)|종합해 보면|요약하자면|도움이 되셨|참고하시기 바랍니다|알아보겠습니다|알아보았습니다|살펴보겠습니다", "삭제 검토"),
    ("서론 클리셰", r"좋은 질문|궁금하셨|이야기해 보려|함께 들어가", "삭제"),
    ("지시어 시작", r"^\s*(이는|이것은|그것은|이처럼|이렇듯)", "지시 대상 복원"),
    ("접속부사 시작", r"^\s*(또한|게다가|더불어|아울러|나아가|한편|따라서|그러나|하지만)", "절반은 삭제"),
    ("이모지", r"[\U0001F300-\U0001FAFF☀-➿]", "제거"),
]

ENDING = re.compile(r"(습니다|입니다|합니다|됩니다|한다|이다|였다|았다|었다)\s*[.!?]?\s*$")


def main() -> int:
    for stream in (sys.stdout, sys.stdin):
        try:
            stream.reconfigure(encoding="utf-8")  # Windows consoles default to cp949
        except (AttributeError, ValueError):
            pass

    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        source = sys.argv[1]
    else:
        lines = sys.stdin.read().splitlines()
        source = "stdin"

    hits = defaultdict(list)
    in_code = False

    for num, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for category, pattern, note in PATTERNS:
            for m in re.finditer(pattern, line, re.MULTILINE):
                hits[(category, note)].append((num, m.group(0)))

    # repeated sentence endings
    endings = []
    for num, line in enumerate(lines, 1):
        for sent in re.split(r"(?<=[.!?])\s+", line):
            m = ENDING.search(sent.strip())
            if m:
                endings.append((num, m.group(1)))
    runs = []
    streak = 1
    for i in range(1, len(endings)):
        if endings[i][1] == endings[i - 1][1]:
            streak += 1
        else:
            if streak >= 3:
                runs.append((endings[i - 1][0], endings[i - 1][1], streak))
            streak = 1
    if streak >= 3 and endings:
        runs.append((endings[-1][0], endings[-1][1], streak))

    print(f"== {source} ==")
    if not hits and not runs:
        print("클리셰 후보 없음. 리듬과 구조는 직접 확인할 것.")
        return 0

    total = 0
    for (category, note), found in sorted(hits.items(), key=lambda kv: -len(kv[1])):
        total += len(found)
        shown = ", ".join(f"L{n}:{t}" for n, t in found[:8])
        more = f" (+{len(found) - 8})" if len(found) > 8 else ""
        print(f"\n[{category}] {len(found)}건 — {note}")
        print(f"  {shown}{more}")

    if runs:
        print(f"\n[어미 반복] {len(runs)}곳 — 서술어 형태 섞기")
        for line_no, ending, count in runs[:8]:
            print(f"  ~L{line_no}: '{ending}' {count}회 연속")

    print(f"\n총 {total}건. 실제로 어색한 것만 고칠 것.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
`````

