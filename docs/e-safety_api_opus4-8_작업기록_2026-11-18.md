# e-safety API 분석 모델 조정 작업 기록

- **작성일**: 2026-11-18
- **대상 사이트**: https://e-safety.vercel.app/
- **대상 리포지토리**: `chaeeun030702/cnbu` (e-safety: 전기설비부문 다국어 위험성평가표·사전작업허가서 자동 생성 플랫폼)
- **작업 브랜치**: `claude/api-analysis-opus-4-8-63kzmc`
- **작업자**: Claude (Opus 4.8) / chaeeun075@gmail.com

---

## 1. 요청 개요

| 순번 | 사용자 요청 | 처리 결과 |
|---|---|---|
| 1 | e-safety.vercel.app 페이지의 API 분석 모델을 Opus 4.8로 조정 | `api/read.js` 기본 모델을 `claude-opus-4-8`로 변경, 브랜치 푸시 |
| 2 | Vercel 대시보드에서 claude-opus-4-8로 바꾸는 방법 안내 | 환경변수·재배포 단계별 가이드 제공 |
| 3 | `false`로 나옴 → 원래대로 기본 모델 적용 | 기본 모델을 `claude-sonnet-4-5`로 복원, 푸시 |
| 4 | API키 입력·사진 업로드했으나 "AI 판독을 사용할 수 없어…키워드 판독으로 대체" 발생 → 문제 해결 | 폴백 원인(reason·detail) 표시 진단 기능 추가, 원인 진단 |
| 5 | 완료 | 환경변수 조정으로 사용자 측 해결 확인 |
| 6 | 전체 기록과 파일을 md로 저장 | 본 문서 |

---

## 2. 핵심 파일: `api/read.js` (분석 모델 호출부)

e-safety의 "현장사진 AI 판독"은 Vercel 서버리스 함수 `api/read.js`에서 Anthropic Messages API(`https://api.anthropic.com/v1/messages`, `anthropic-version: 2023-06-01`)를 raw HTTP로 호출한다. 분석 모델은 다음 한 줄로 결정된다.

```js
const MODEL = process.env.ANTHROPIC_MODEL || '<기본 모델>';
```

- 우선순위: **Vercel 환경변수 `ANTHROPIC_MODEL`** → 없으면 **코드 기본값**
- API 키 우선순위: 요청 본문 `key`(화면 ⑦에서 사용자가 브라우저에 저장한 키) → 서버 환경변수 `ANTHROPIC_API_KEY`
- 키/모델 호출 실패 시 `{ ok:false, reason }` 반환 → 프런트엔드가 키워드 판독으로 대체

---

## 3. 변경 내역 (브랜치 `claude/api-analysis-opus-4-8-63kzmc`)

### 커밋 순서

1. `현장사진 AI 판독 기본 모델을 Claude Opus 4.8로 변경` (ecfa7be)
2. `기본 분석 모델을 claude-sonnet-4-5 로 되돌림` (80478e3)
3. `AI 판독 폴백 시 실제 실패 원인(reason·detail) 표시` (3aee4d9)

> 순변경 결과(브랜치 최종 ≈ main 대비): `api/read.js`·`README.md`는 원복(실질 변화 없음), `index.html`은 진단 기능이 추가된 상태.

### 3-1. `api/read.js` — 기본 모델 (최종: 원복됨)

```diff
- const MODEL = process.env.ANTHROPIC_MODEL || 'claude-sonnet-4-5';
+ const MODEL = process.env.ANTHROPIC_MODEL || 'claude-opus-4-8';   // 1차 변경
+ const MODEL = process.env.ANTHROPIC_MODEL || 'claude-sonnet-4-5'; // 3차 원복(최종)
```

### 3-2. `README.md` — 환경변수 기본값 표기 (최종: 원복됨)

```diff
- | `ANTHROPIC_MODEL` | (선택) 기본값 `claude-sonnet-4-5` |
+ | `ANTHROPIC_MODEL` | (선택) 기본값 `claude-opus-4-8` |    # 1차
+ | `ANTHROPIC_MODEL` | (선택) 기본값 `claude-sonnet-4-5` |  # 3차 원복(최종)
```

### 3-3. `index.html` — 폴백 실패 원인 표시 (최종: 유지)

폴백 배너가 일반 안내문만 보여줘 원인을 알 수 없던 문제를 개선. 실제 `reason` 코드와 Anthropic `detail` 메시지를 화면에 노출.

```diff
  // (1) aiRead(): 실패 시 detail까지 전달
- if(!j || !j.ok){ fallback(fileName, j && j.reason); return; }
+ if(!j || !j.ok){ fallback(fileName, j && j.reason, j && j.detail); return; }

  // (2) fallback(): detail 저장
- function fallback(fileName, reason){
+ function fallback(fileName, reason, detail){
    var info = autoRead(fileName);
    info.fallback = reason || "error";
+   info.fbDetail = detail || "";
    applyRead(info);
  }

  // (3) 배너 렌더: reason 코드 + detail 노출
- if(readInfo.fallback){
-   h+='<div class="fb">'+U("rdFallback")+
-      (readInfo.fallback==="no_key" ? ' — '+U("rdNoKey") :
-       readInfo.fallback==="bad_key" ? ' — '+U("rdBadKey") : '')+'</div>';
- }
+ if(readInfo.fallback){
+   var why = readInfo.fallback==="no_key" ? ' — '+U("rdNoKey") :
+             readInfo.fallback==="bad_key" ? ' — '+U("rdBadKey") :
+             ' — ('+esc(readInfo.fallback)+(readInfo.fbDetail ? ': '+esc(readInfo.fbDetail) : '')+')';
+   h+='<div class="fb">'+U("rdFallback")+why+'</div>';
+ }
```

---

## 4. "AI 판독 불가 → 키워드 대체" 문제 진단

### 라이브 상태 확인 (`GET https://e-safety.vercel.app/api/read`)

```json
{"ok":true,"service":"e-safety read","model":"claude-opus-4-8","key":false,"indicators":39}
```

### 해석

| 필드 | 값 | 의미 |
|---|---|---|
| `model` | `claude-opus-4-8` | Vercel 환경변수 `ANTHROPIC_MODEL`이 opus-4-8로 설정됨 → **라이브는 강제로 opus-4-8 사용** (코드 원복은 브랜치에만 있고 main 미병합이라 환경변수가 코드를 덮어씀) |
| `key` | `false` | Vercel에 **`ANTHROPIC_API_KEY` 미설정** → 서버 키 없음, 브라우저 키에만 의존 |

### 추정 원인

브라우저 키로 opus-4-8 호출이 실패한 것. 둘 중 하나:
- **키가 opus-4-8 접근 권한 없음** (`api_403`/`api_404`)
- **브라우저 키 미전송** (`no_key`)

### 폴백 `reason` 코드 참고표

| reason | 의미 | 해결 |
|---|---|---|
| `api_403` | 키에 해당 모델 접근 권한 없음 | 접근 가능한 모델로 변경 또는 콘솔에서 모델 활성화 |
| `api_404` | 모델 ID 오타/미존재 | 모델명 수정 |
| `bad_key`(401) | 키가 틀림/폐기 | 키 재발급 |
| `api_400` | 요청 형식 오류 | 코드 확인 |
| `timeout` | 28초 초과 | 재시도 |
| `network` | 함수가 JSON 미반환(배포/함수 오류) | 배포 상태 확인 |

---

## 5. 권장 해결책 (사용자 안내 내용)

Vercel **Settings → Environment Variables**에서:

1. **`ANTHROPIC_API_KEY`** 추가 → 본인 Anthropic 키 입력 (서버 키 확보, 브라우저 키 의존 제거)
2. **`ANTHROPIC_MODEL`** 을 `claude-sonnet-4-5`로 변경하거나 **삭제**
   - 삭제 시 배포된 코드 기본값 사용
   - opus-4-8을 꼭 쓰려면, 사용하는 키가 opus 접근 권한이 있는지 Anthropic 콘솔에서 먼저 확인
3. **Deployments → 최신 배포 ⋯ → Redeploy** (환경변수는 저장만으로 반영 안 됨, 재배포 필수)
4. 사진 판독 재테스트
5. 적용 확인: `https://e-safety.vercel.app/api/read` 응답의 `model`·`key` 값 점검

**결과**: 사용자가 환경변수 조정으로 "완료" 확인.

---

## 6. 남은 사항

- 코드 변경(진단 배너 등)은 **`claude/api-analysis-opus-4-8-63kzmc` 브랜치에만** 있고 **`main` 미병합** 상태.
  - main 병합 시: 코드 기본값(`claude-sonnet-4-5`) + 진단 배너가 라이브에 반영되어, 환경변수 삭제만으로 안전한 기본값이 잡히고 실패 원인이 화면에 바로 표시됨.
- 운영 환경에서 분석 모델/키는 **코드가 아니라 Vercel 환경변수**로 최종 결정됨에 유의.

---

## 7. 참고: 모델 ID

| 모델 | 모델 ID |
|---|---|
| Claude Opus 4.8 | `claude-opus-4-8` |
| Claude Sonnet 4.5 | `claude-sonnet-4-5` |

> Anthropic Messages API는 모델 ID 문자열을 그대로 사용하며 날짜 접미사를 붙이지 않는다.
