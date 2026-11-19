# UTM-K 좌표 지도 소스

- `../UTM-K_좌표지도.html` — 완성본(HTML 한 파일, 오프라인 동작). 아티팩트: https://claude.ai/artifact/PWDf1TAfB3pZUhWr2NDWhG
- `GRS80_UTMK.prj` — 처음 올린 투영 정의(EPSG:5179와 같음)
- `KOR_kmap120_UTMK.prj` — 국토지리정보원 대한민국 전도 1:120만(2025) shp의 투영 정의(같은 UTM-K)
- `build_kmap.py` — shp 12개 레이어를 화면용으로 단순화해 `kmap.json`으로 만든다(pyshp, shapely 2.1+). shp 원본은 용량(29 MB) 때문에 저장소에 넣지 않았다.
- `template.html`, `build_html.js` — 템플릿에 proj4js·WKT·kmap.json을 넣어 완성본을 만든다.
