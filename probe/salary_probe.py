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
for rec in ("55158724", "55178333"):
    t = get(f"sr_post_{rec}", f"https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx={rec}")
    m = re.search(r"csn=([A-Za-z0-9=%]+)", t)
    log.append(f"  csn {m.group(1) if m else None}")
    if m:
        csn = m.group(1)
        get(f"sr_co_{rec}", f"https://www.saramin.co.kr/zf_user/company-info/view?csn={csn}")
        get(f"sr_co_salary_{rec}", f"https://www.saramin.co.kr/zf_user/company-info/view-inner-salary?csn={csn}")
for gi in ("50077074", "50076771"):
    t = get(f"jk_post_{gi}", f"https://www.jobkorea.co.kr/Recruit/GI_Read/{gi}?Oem_Code=C1")
    ms = sorted(set(re.findall(r'href="(/(?:Recruit/Co_Read/[^"]+|company/\d+[^"]*))"', t)))
    log.append(f"  co links {ms[:5]}")
    m = re.search(r"/company/(\d+)", t) or re.search(r"Co_Read/C/(\w+)", t)
    if m:
        cid = m.group(1)
        get(f"jk_co_{gi}", f"https://www.jobkorea.co.kr/company/{cid}")
        get(f"jk_co_salary_{gi}", f"https://www.jobkorea.co.kr/company/{cid}/salary")
get("kreditjob", "https://kreditjob.com/")
get("jobplanet", "https://www.jobplanet.co.kr/companies?query=%ED%98%84%EB%8C%80%EB%A1%9C%ED%85%9C")
(out / "status.txt").write_text("\n".join(log), encoding="utf-8")
print("\n".join(log))
