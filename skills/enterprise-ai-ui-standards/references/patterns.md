# UI 패턴 골격

1. 공통 문서 셀업
2. 앱·문서 쉐
3. 헤더 락업
4. 버튼·카드·테이블
5. 보고서 본문 구성
6. 인쇄
7. 자주 하는 실수

## 1. 공통 문서 셀업

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>서비스명</title>
  <style>/* references/design-tokens.css 내용을 그대로 삽입 */</style>
</head>
<body>...</body>
</html>
```

```css
body {
  margin: 0;
  font-family: var(--font-sans);
  font-size: var(--fs-body-2);      /* 18px */
  line-height: var(--lh-body);      /* 1.7 — 본문 전용 */
  color: var(--color-text-primary);
  background: var(--color-bg-content);
  -webkit-font-smoothing: antialiased;
}
:focus-visible { outline: 2px solid var(--color-action-primary); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }

/* 타이포 리듬 — 큰 글자는 본문 1.7 을 상속하지 않도록 계열별 line-height 를 강제한다.
   2단계 상향된 스케일에서 줄간격·간격 붕괴를 막는 핵심 규칙. */
h1, h2, h3, h4 { margin: 0 0 var(--space-3); font-weight: 700; text-wrap: balance; }
h1 { font-size: var(--fs-title-1); line-height: var(--lh-title);   letter-spacing: var(--tracking-title); }
h2 { font-size: var(--fs-title-3); line-height: var(--lh-title);   letter-spacing: var(--tracking-title); }
h3 { font-size: var(--fs-heading-1); line-height: var(--lh-heading); }
h4 { font-size: var(--fs-heading-3); line-height: var(--lh-heading); }
:where(.display) { line-height: var(--lh-display); letter-spacing: var(--tracking-display); }
p { margin: 0 0 var(--space-4); max-width: 840px; }        /* 본문 줄길이 70~80자 제한 */
* + h2, * + h3 { margin-top: var(--space-7); }             /* 섹션 제목 위 리듬 */
```

## 2. 앱·문서 쉐

```html
<div class="app">
  <header class="app-header">...</header>
  <div class="app-body">
    <nav class="side-nav" aria-label="목차">...</nav>
    <main class="app-content">...</main>
  </div>
</div>
```

```css
.app { min-height: 100vh; display: flex; flex-direction: column; }
.app-header {
  position: sticky; top: 0; z-index: 50; height: 64px;
  display: flex; align-items: center; gap: 16px; padding: 0 24px;
  background: var(--color-bg-surface); border-bottom: 1px solid var(--color-border-default);
}
.app-body { flex: 1; display: flex; min-height: 0; }
.side-nav {
  width: 300px; flex: none; overflow-y: auto;
  background: var(--color-bg-surface); border-right: 1px solid var(--color-border-default);
}
.side-nav a { display: flex; align-items: center; min-height: var(--nav-row-h); padding: 8px 20px; gap: 10px;
  font-size: var(--fs-body-3); line-height: var(--lh-dense);
  color: var(--color-text-secondary); text-decoration: none; }
.side-nav .depth2 a { min-height: var(--nav-row-h-sub); }
.side-nav a:hover { background: var(--color-bg-surface-alt-1); }
.side-nav a[aria-current="page"] { color: var(--color-action-primary); font-weight: 600; background: var(--color-bg-surface-alt-1); }
.app-content { flex: 1; overflow-y: auto; padding: 24px; background: var(--color-bg-content); }
```

사이드내비는 띄우지 않고 쉐에 붙이며, 서브 항목 행 높이는 44px.

## 3. 헤더 락업

```html
<div class="brand">
  <!-- 공식 로고 SVG가 제공된 경우에만 삽입. 없으면 비워둔다. -->
  <span class="brand-divider" aria-hidden="true"></span>
  <span class="brand-name">서비스명</span>
</div>
<div class="header-actions">
  <input type="search" class="field" placeholder="검색" aria-label="검색" />
  <button type="button" class="icon-btn" aria-label="알림">...</button>
</div>
```

```css
.brand { display: flex; align-items: center; gap: 12px; min-width: 0; }
.brand-divider { width: 1px; height: 20px; background: var(--color-border-strong); }
.brand-name { font-size: var(--fs-body-1); line-height: var(--lh-dense); font-weight: 600; white-space: nowrap; }
.header-actions { margin-left: auto; display: flex; align-items: center; gap: 8px; }
.icon-btn { width: 44px; height: 44px; display: inline-flex; align-items: center; justify-content: center;
  border: 0; border-radius: var(--radius-sm); background: transparent; color: var(--color-text-secondary); cursor: pointer; }
.icon-btn:hover { background: var(--color-bg-surface-alt-1); }
```

## 4. 버튼·카드·테이블

```css
.btn { min-height: var(--control-h); padding: 6px 18px; display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  font: inherit; font-size: var(--fs-body-3); line-height: var(--lh-dense); font-weight: 600;
  border-radius: var(--radius-sm); cursor: pointer;
  border: 1px solid var(--color-border-default); background: var(--color-bg-surface); color: var(--color-text-secondary); }
.btn:hover { background: var(--color-bg-surface-alt-1); border-color: var(--color-border-strong); }
.btn-primary { background: var(--color-action-primary); border-color: var(--color-action-primary); color: #fff; }
.btn-primary:hover { background: var(--color-action-primary-hover); border-color: var(--color-action-primary-hover); }
.btn[disabled] { color: var(--color-text-disabled); background: var(--color-bg-surface-alt-1); cursor: not-allowed; }

.card { background: var(--color-bg-surface); border: 1px solid var(--color-border-default);
  border-radius: var(--radius-md); padding: var(--space-5); box-shadow: var(--shadow-level-1); }
.card-title { margin: 0 0 var(--space-1); font-size: var(--fs-heading-3); line-height: var(--lh-heading); font-weight: 700; }
.card-sub { margin: 0 0 var(--space-4); font-size: var(--fs-label-2); line-height: var(--lh-caption); color: var(--color-text-muted); }

.field { min-height: var(--control-h); padding: 8px 14px; font: inherit; font-size: var(--fs-body-3);
  line-height: var(--lh-dense); color: var(--color-text-primary);
  background: var(--color-bg-surface); border: 1px solid var(--color-border-default); border-radius: var(--radius-sm); }

table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
th { text-align: left; font-size: var(--fs-label-1); line-height: var(--lh-dense); font-weight: 600;
  color: var(--color-text-secondary);
  background: var(--color-bg-surface-alt-1); border-bottom: 1px solid var(--color-border-strong); }
th, td { padding: var(--space-4) var(--space-3); font-size: var(--fs-body-3); line-height: var(--lh-dense);
  border-bottom: 1px solid var(--color-divider-default); vertical-align: middle; }
tbody tr { min-height: var(--row-h); }   /* 고정 height 금지 — 줄바꿈된 셀이 잘리지 않게 */
.badge { display: inline-flex; align-items: center; padding: 4px 12px; font-size: var(--fs-label-2);
  line-height: var(--lh-dense); font-weight: 600;
  border-radius: var(--radius-pill); background: var(--color-bg-surface-alt-1); color: var(--color-text-muted); }
```

상태 배지는 색과 텍스트를 함께 쓴다(success/warning/danger 토큰 + 라벨).

## 5. 보고서 본문 구성

순서: 상단 요약(KPI/핵심 카드) → 섹션별 「한 줄 결론 + 그래픽 + 짧은 해석」 → 부록(원문·출처).

```html
<section class="section">
  <h2 class="section-title"><span class="section-no">01</span> 섹션명</h2>
  <p class="lede">한 줄 결론을 먼저 쓴다. 60자 내외.</p>
  <div class="card"><!-- 차트·도식 --></div>
  <p class="note">차트 해석 한 줄.</p>
  <details><summary>근거 원문 보기</summary><p>긴 원문은 접힘 안에.</p></details>
</section>
```

```css
.section { max-width: 1040px; margin: 0 auto var(--space-9); }
.section-title { display: flex; align-items: center; gap: 10px; margin: 0 0 var(--space-4);
  font-size: var(--fs-title-3); line-height: var(--lh-title); letter-spacing: var(--tracking-title); font-weight: 700; }
.section-no { flex: none; display: inline-flex; align-items: center; justify-content: center;
  min-width: 40px; min-height: 30px; padding: 0 8px;
  font-size: var(--fs-label-2); line-height: var(--lh-dense); border-radius: var(--radius-pill);
  background: color-mix(in srgb, var(--color-action-primary) 12%, transparent); color: var(--color-action-primary); }
.lede { margin: 0 0 var(--space-5); font-size: var(--fs-body-1); line-height: var(--lh-lede);
  font-weight: 600; color: var(--color-text-strong); }
.note { margin: var(--space-3) 0 0; font-size: var(--fs-label-2); line-height: var(--lh-caption); color: var(--color-text-muted); }
.grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-4); }
@media (max-width: 720px) { .grid-2 { grid-template-columns: 1fr; } }
```

## 6. 인쇄

```css
@page { size: A4 portrait; margin: 14mm; }
@media print {
  .app-header, .side-nav, .btn { display: none !important; }
  body { background: #fff; }
  .card { box-shadow: none; break-inside: avoid; }
  .section { break-inside: avoid-page; }
}
```

## 7. 자주 하는 실수

- 시스템 폰트(맑은 고딕·Arial) 방치 → Pretendard 스택으로 교체
- pt 단위·임의 폰트 크기 → 승인 px 스케일만 사용(본문 18px 기준)
- 작은 웹 기본값(13~14px) 본문 → 2단계 상향된 스케일 적용
- 큰 제목·수치에 본문 줄간격(1.7) 상속 → 줄간격 벌어짐·배치 붕괴. 계열별 `--lh-*` 지정
- 버튼·인풋·행에 고정 `height` → 큰 글자/줄바꿈 잘림. `min-height`(`--control-h`·`--row-h`) 사용
- 베이지·움그레이 팔레트, 임의 hex → 시맨틱 토큰 변수
- 이모지·외부 아이콘 라이브러리 혼용 → inline SVG 단일 패밀리
- 그라데이션 배경·컬러 그림자 → 보더·여백으로 위계 표현
- 원문 통째 복붙, 5문장 문단 → 요약 + 도식으로 분해
- 샘플 데이터에 실명·부서명·이메일 → 가명·일반명사로 대체
