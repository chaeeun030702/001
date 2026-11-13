# 포항 에코빌리지 친환경에너지타운 · 민간투자사업 추진계획 (웹 버전)

첨부 패키지(`Pohang_Ecovillage_Package.zip`: PPTX·PDF·슬라이드 텍스트)의 12장 발표자료를
브라우저에서 바로 보는 HTML 한 파일로 구현했다.

| 파일 | 내용 |
| --- | --- |
| `index.html` | 완성본. 이미지까지 내장한 HTML 한 파일. A4 가로(297×210mm) 12쪽, 편집·HTML 저장·A4 인쇄, 발표 모드(←→ 키) |
| `template.html` | 편집용 원본. 이미지는 `{{IMG_이름}}` 자리표시 |
| `build.py` | `template.html` + `img/*.jpg` → `index.html` |
| `img/` | PPTX에서 추출한 마스터플랜·실적 사진 |
| `slide_text.md` | 원본 슬라이드 텍스트 추출본 |

수정 후 다시 만들기:

```bash
python3 docs/pohang_ecovillage/build.py
```

## 편집과 인쇄

1. `index.html`을 브라우저로 연다.
2. **편집**을 누르고 글자를 바로 고친다. 사진을 누르면 다른 사진으로 바꿀 수 있다. 수정 내용은 브라우저에 자동으로 보관된다.
3. **HTML 저장**을 누르면 편집본이 HTML 한 파일로 저장된다. 저장한 파일도 다시 편집할 수 있다.
4. **A4 인쇄**를 누르면 A4 가로 12쪽으로 인쇄된다. PDF로 저장할 때는 여백을 '없음'으로 둔다.
