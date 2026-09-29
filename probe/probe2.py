# 임시 탐침: 신규 사이트 응답 구조 확인 (확인 후 삭제)
import json, pathlib, httpx
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8"}
out = pathlib.Path("probe/r3"); out.mkdir(parents=True, exist_ok=True)
c = httpx.Client(headers=UA, follow_redirects=True, timeout=40)
status = []
def save(name, r):
    (out / f"{name}.txt").write_bytes(r.content[:3_000_000])
    status.append(f"{name} {r.status_code} {len(r.content)} {r.url}")
def get(name, url, **kw):
    try: save(name, c.get(url, **kw))
    except Exception as e: status.append(f"{name} ERR {type(e).__name__}: {e}"[:200])
def post(name, url, body):
    try: save(name, c.post(url, json=body, headers={**UA, "Content-Type": "application/json", "Accept": "application/json"}))
    except Exception as e: status.append(f"{name} ERR {type(e).__name__}: {e}"[:200])
# 피플앤잡
get("pnj_search_hse", "https://www.peoplenjob.com/jobs?field=all&q=HSE")
get("pnj_search_ehs", "https://www.peoplenjob.com/jobs?q=EHS")
get("pnj_search_safety", "https://www.peoplenjob.com/jobs?q=%EC%95%88%EC%A0%84")
get("pnj_detail", "https://www.peoplenjob.com/jobs/4663756")
# 원티드
get("wanted_api_search", "https://www.wanted.co.kr/api/chaos/search/v1/results?query=%EC%95%88%EC%A0%84%EA%B4%80%EB%A6%AC%EC%9E%90&tab=position&country=kr&job_sort=job.latest_order&years=0&limit=20&offset=0")
get("wanted_api_v4", "https://www.wanted.co.kr/api/v4/jobs?country=kr&query=%EC%95%88%EC%A0%84%EA%B4%80%EB%A6%AC%EC%9E%90&years=0&limit=20&offset=0&job_sort=job.latest_order")
get("wanted_search_html", "https://www.wanted.co.kr/search?query=%EC%95%88%EC%A0%84%EA%B4%80%EB%A6%AC%EC%9E%90&tab=position")
# 캐치
get("catch_search", "https://www.catch.co.kr/NCS/RecruitSearch?Keyword=%EC%95%88%EC%A0%84")
get("catch_list", "https://www.catch.co.kr/NCS/RecruitList")
get("catch_home", "https://www.catch.co.kr/")
# Workday 후보 (tenant, wd, site)
WD = [("3m","wd1","Search"),("amat","wd1","External"),("micron","wd1","External"),("lamresearch","wd1","LAM"),
      ("lamresearch","wd1","Careers"),("equinix","wd1","External"),("airliquidehr","wd3","AirLiquideExternalCareer"),
      ("linde","wd3","External"),("linde","wd3","linde_careers"),("airproducts","wd5","AP0001"),("airproducts","wd1","AP0001"),
      ("asml","wd3","ASMLCareers"),("basf","wd3","BASF_External"),("basf","wd3","External")]
for t, w, site in WD:
    post(f"wd_{t}_{site}", f"https://{t}.{w}.myworkdayjobs.com/wday/cxs/{t}/{site}/jobs",
         {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": "Korea"})
# 비 Workday 후보
get("basf_jobs", "https://basf.jobs/search/?q=&locationsearch=Korea")
get("basf_careers", "https://www.basf.com/global/en/careers/jobs")
get("linde_jobs", "https://www.linde.com/careers/job-search")
get("ap_jobs", "https://careers.airproducts.com/search/?q=&locationsearch=Korea")
get("asml_jobs", "https://www.asml.com/en/careers/find-your-job?job_location=Korea")
get("asml_api", "https://www.asml.com/api/job-search?country=South%20Korea")
(out / "status.txt").write_text("\n".join(status))
print("\n".join(status))
