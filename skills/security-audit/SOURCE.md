# 출처

- 원본: https://github.com/cloudflare/security-audit-skill (`skills/security-audit/`)
- 가져온 커밋: `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8` (2026-09-14)
- 라이선스: MIT (Cloudflare, Inc.) — `LICENSE` 참고
- 원본 파일은 수정하지 않았다. 갱신할 때는 원본 저장소에서 다시 복사한다.

## 이 저장소에서 쓰는 법
- 설치(본인 PC): `skills/security-audit.zip`을 Claude 스킬로 올리거나, `~/.claude/skills/security-audit/`에 이 폴더를 복사한다.
- 호출 예: "이 코드베이스 보안 감사해줘", "./src 취약점 찾아줘", "보안 리뷰, 결과는 ~/audits/my-project"
- 질문·부분 리뷰는 가이드 모드, 명시적 전체 감사 요청만 6단계 전체 모드로 돈다.
- 검증기 테스트: `node --test validate-findings.test.cjs validate-coverage-ledger.test.cjs` (Node.js 필요)
