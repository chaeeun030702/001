# 임시: 기업별 신입 연봉 정보 소스 확인 (결과는 probe/sal/*.txt)
import re, pathlib, httpx
from bs4 import BeautifulSoup
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
     "Accept-Language": "ko-KR,ko;q=0.9"}
c = httpx.Client(headers=H, follow_redirects=True, timeout=30)
out = pathlib.Path("probe/sal"); out.mkdir(parents=True, exist_ok=True)
log = []
def get(name, url):
    try:
        r = c.get(url); t = r.text
        (out / f"{name}.html").write_text(t, encoding="utf-8")
        txt = re.sub(r"\s+", " ", BeautifulSoup(t, "html.parser").get_text(" "))
        snips = [txt[max(0, m.start()-80):m.end()+120] for m in re.finditer(r"초봉|신입\s*(?:연봉|초임)|평균\s*연봉|대졸\s*초임", txt)][:12]
        (out / f"{name}.txt").write_text("\n---\n".join(snips), encoding="utf-8")
        log.append(f"{name} {r.status_code} {len(t)} {r.url} snips={len(snips)}")
        return t
    except Exception as e:
        log.append(f"{name} ERR {e}"); return ""
import urllib.parse as U
for nm in ("현대로템", "코레일테크", "(주)케이씨씨건설", "한국드레가"):
    q = U.quote(re.sub(r"\(주\)|㈜|주식회사", "", nm).strip())
    for k, url in (("corp", f"https://www.jobkorea.co.kr/Search/?stext={q}&tabType=corp"),
                   ("corpapi", f"https://www.jobkorea.co.kr/Search/api/corp?stext={q}")):
        t = get(f"jk_search_{k}_{q[:12]}", url)
        links = re.findall(r'href="(?:https://www\.jobkorea\.co\.kr)?(/company/\d+)[^"]*"[^>]*>(.{0,120}?)</a>', t, re.S)
        pairs = [(a, re.sub(r"<[^>]+>|\s+", " ", b).strip()[:30]) for a, b in links[:6]]
        log.append(f"  {nm} {k} links {pairs}")
        ids = sorted(set(re.findall(r"/company/(\d+)", t)))[:8]
        log.append(f"  ids {ids}")
get("jk_co_small", "https://www.jobkorea.co.kr/company/1842322/salary")
(out / "status.txt").write_text("\n".join(log), encoding="utf-8")
print("\n".join(log))
