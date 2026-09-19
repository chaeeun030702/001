# 시각화 레시피 (inline SVG / CSS)

모든 그래픽은 외부 라이브러리 없이 이 골격을 복사해 데이터만 바꿔 쓴다.
색은 `--chart-1`~`--chart-5`, 텍스트는 시맨틱 토큰을 사용한다.
폰트 크기는 승인 스케일(캡션 13px / 라벨 15px / 본문 18px 기준)을 따른다.

## 1. KPI 카드

```html
<div class="kpi-grid">
  <div class="kpi">
    <p class="kpi-label">총 적용 법령</p>
    <p class="kpi-value">12<span class="kpi-unit">건</span></p>
    <p class="kpi-delta up">▲ 2건 (전년 대비)</p>
  </div>
</div>
```

```css
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
.kpi { background: var(--color-bg-surface); border: 1px solid var(--color-border-default);
  border-radius: var(--radius-md); padding: 20px; }
.kpi-label { margin: 0 0 8px; font-size: 15px; font-weight: 600; color: var(--color-text-muted); }
.kpi-value { margin: 0; font-size: 44px; font-weight: 700; line-height: 1.1;
  font-variant-numeric: tabular-nums; color: var(--color-text-strong); }
.kpi-unit { margin-left: 4px; font-size: 20px; font-weight: 600; color: var(--color-text-secondary); }
.kpi-delta { margin: 8px 0 0; font-size: 14px; font-weight: 600; }
.kpi-delta.up { color: var(--color-status-success); }
.kpi-delta.down { color: var(--color-status-danger); }
```

## 2. 가로 막대 (CSS만, 항목 비교의 기본형)

```html
<ul class="hbar" role="img" aria-label="항목별 비율: 소방시설법 42%, 전기설비기준 31%, 건축법 27%">
  <li><span class="hbar-name">소방시설법</span>
      <span class="hbar-track"><span class="hbar-fill" style="width:42%"></span></span>
      <span class="hbar-val">42%</span></li>
</ul>
```

```css
.hbar { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; }
.hbar li { display: grid; grid-template-columns: 160px 1fr 56px; align-items: center; gap: 12px; font-size: 16px; }
.hbar-name { color: var(--color-text-secondary); }
.hbar-track { height: 12px; border-radius: var(--radius-pill); background: var(--color-bg-surface-alt-1); }
.hbar-fill { display: block; height: 100%; border-radius: var(--radius-pill); background: var(--chart-1); }
.hbar-val { text-align: right; font-weight: 700; font-variant-numeric: tabular-nums; }
```

## 3. 세로 막대 (SVG)

```html
<svg viewBox="0 0 480 220" width="100%" role="img" aria-label="연도별 건수: 2023년 8건, 2024년 11건, 2025년 14건">
  <line x1="40" y1="180" x2="460" y2="180" stroke="var(--chart-grid)" />
  <g font-family="var(--font-sans)" font-size="14" fill="var(--chart-axis)" text-anchor="middle">
    <rect x="70"  y="96"  width="56" height="84"  rx="6" fill="var(--chart-1)" />
    <text x="98"  y="86"  font-size="16" font-weight="700" fill="var(--color-text-strong)">8</text>
    <text x="98"  y="202">2023</text>
    <rect x="200" y="64"  width="56" height="116" rx="6" fill="var(--chart-1)" />
    <text x="228" y="54"  font-size="16" font-weight="700" fill="var(--color-text-strong)">11</text>
    <text x="228" y="202">2024</text>
    <rect x="330" y="32"  width="56" height="148" rx="6" fill="var(--chart-1)" />
    <text x="358" y="22"  font-size="16" font-weight="700" fill="var(--color-text-strong)">14</text>
    <text x="358" y="202">2025</text>
  </g>
</svg>
```

막대 높이 = 값 / 최댓값 x 축 길이. 값 라벨은 항상 막대 위에 표기한다.

## 4. 라인/영역 (추세)

```html
<svg viewBox="0 0 480 200" width="100%" role="img" aria-label="월별 추세 상승">
  <g stroke="var(--chart-grid)">
    <line x1="40" y1="40" x2="460" y2="40" /><line x1="40" y1="100" x2="460" y2="100" />
    <line x1="40" y1="160" x2="460" y2="160" />
  </g>
  <polyline fill="none" stroke="var(--chart-1)" stroke-width="2.5" stroke-linejoin="round"
            points="60,150 160,120 260,128 360,80 450,56" />
  <polygon fill="var(--chart-1)" opacity="0.10" points="60,150 160,120 260,128 360,80 450,56 450,160 60,160" />
  <g fill="var(--chart-1)"><circle cx="450" cy="56" r="4" /></g>
  <g font-family="var(--font-sans)" font-size="14" fill="var(--chart-axis)" text-anchor="middle">
    <text x="60" y="182">1월</text><text x="260" y="182">3월</text><text x="450" y="182">5월</text>
  </g>
</svg>
```

## 5. 도넛 (항목 3개 이하)

```html
<svg viewBox="0 0 160 160" width="160" role="img" aria-label="진행률 68%">
  <circle cx="80" cy="80" r="64" fill="none" stroke="var(--color-bg-surface-alt-1)" stroke-width="18" />
  <circle cx="80" cy="80" r="64" fill="none" stroke="var(--chart-1)" stroke-width="18"
          stroke-linecap="round" stroke-dasharray="273 402" transform="rotate(-90 80 80)" />
  <text x="80" y="88" text-anchor="middle" font-family="var(--font-sans)" font-size="32"
        font-weight="700" fill="var(--color-text-strong)">68%</text>
</svg>
```

`stroke-dasharray` 첫 값 = 2 x pi x r x 비율 (r=64이면 둘레 402).

## 6. 100% 스택바 (구성비)

```html
<div class="stack" role="img" aria-label="구성비: A 50%, B 30%, C 20%">
  <span style="width:50%;background:var(--chart-1)">A 50%</span>
  <span style="width:30%;background:var(--chart-2)">B 30%</span>
  <span style="width:20%;background:var(--chart-3)">C 20%</span>
</div>
```

```css
.stack { display: flex; height: 40px; border-radius: var(--radius-sm); overflow: hidden; }
.stack span { display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 600; color: #fff; }
```

## 7. 계층·체계도 (법령 체계, 조직 위계)

```html
<div class="tier">
  <div class="tier-row lv1"><span class="tier-tag">법률</span><span class="tier-name">상위 법률</span></div>
  <div class="tier-arrow" aria-hidden="true"></div>
  <div class="tier-row lv2"><span class="tier-tag">시행령</span><span class="tier-name">대통령령</span></div>
  <div class="tier-arrow" aria-hidden="true"></div>
  <div class="tier-row lv3"><span class="tier-tag">기준</span><span class="tier-name">고시·기술기준</span></div>
</div>
```

```css
.tier { display: grid; justify-items: center; gap: 0; }
.tier-row { display: flex; align-items: center; gap: 12px; width: 100%; max-width: 560px;
  padding: 16px 20px; border-radius: var(--radius-md);
  border: 1px solid var(--color-border-default); background: var(--color-bg-surface); font-size: 18px; }
.tier-row.lv1 { border-left: 4px solid var(--chart-1); }
.tier-row.lv2 { border-left: 4px solid var(--chart-2); }
.tier-row.lv3 { border-left: 4px solid var(--chart-3); }
.tier-tag { font-size: 14px; font-weight: 600; padding: 3px 10px; border-radius: var(--radius-pill);
  background: var(--color-bg-surface-alt-1); color: var(--color-text-muted); }
.tier-name { line-height: var(--lh-heading); font-weight: 700; }
.tier-arrow { width: 2px; height: 20px; background: var(--color-border-strong); }
```

## 8. 절차 플로우 / 타임라인

```html
<ol class="flow">
  <li><span class="flow-no">1</span><div><p class="flow-t">설계 검토</p><p class="flow-d">기준 적합성 확인</p></div></li>
  <li><span class="flow-no">2</span><div><p class="flow-t">인허가</p><p class="flow-d">관할 기관 협의</p></div></li>
</ol>
```

```css
.flow { list-style: none; margin: 0; padding: 0; display: grid; gap: 0; }
.flow li { display: grid; grid-template-columns: 40px 1fr; gap: 16px; padding: 0 0 24px;
  border-left: 2px solid var(--color-border-default); margin-left: 19px; padding-left: 24px; position: relative; }
.flow li:last-child { border-left-color: transparent; padding-bottom: 0; }
.flow-no { position: absolute; left: -20px; top: 0; width: 38px; height: 38px; border-radius: var(--radius-pill);
  display: inline-flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 700;
  color: #fff; background: var(--chart-1); }
.flow-t { margin: 6px 0 2px; font-size: 18px; line-height: var(--lh-heading); font-weight: 700; }
.flow-d { margin: 0; font-size: 15px; line-height: var(--lh-dense); color: var(--color-text-muted); }
```

가로 타임라인이 필요하면 같은 토큰으로 `display:flex` + 상단 연결선으로 바꾼다.

## 9. 매트릭스 / 비교표

행=항목, 열=기준. 값은 텍스트 + 상태 점으로 표기하고 색만으로 구분하지 않는다.

```html
<td><span class="dot ok" aria-hidden="true"></span>적합</td>
```

```css
.dot { display: inline-block; width: 10px; height: 10px; border-radius: var(--radius-pill); margin-right: 8px; }
.dot.ok { background: var(--color-status-success); }
.dot.warn { background: var(--color-status-warning); }
.dot.bad { background: var(--color-status-danger); }
```

## 10. 공통 규칙

- 큰 수치·제목(KPI 값, 도넛 중앙 수치 등)은 `line-height` 를 1.0~1.2 로 지정해 본문 1.7 상속을 막는다.
- SVG는 `viewBox` + `width="100%"`로 반응형 처리, 고정 px 폭 지정 금지(도넛 등 소형 제외).
- SVG 내부 텍스트도 `font-family="var(--font-sans)"`를 지정한다. 최소 14px.
- 의미 있는 그래픽은 `role="img"` + `aria-label`, 장식은 `aria-hidden="true"`.
- 애니메이션은 기본 없음. 필요 시 200ms 이하이며 `prefers-reduced-motion`에서 제거.
- 수치 출처가 불확실하면 그래픽 안에 `추정` 또는 `데이터 없음`을 표기한다.
- 차트 아래 한 줄 해석 캡션(14px, muted)을 붙인다.
