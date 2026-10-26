# -*- coding: utf-8 -*-
import json, html, re, collections, datetime, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
MAIN_JSON = os.environ.get("MAIN_JSON", HERE + "/latest_main.json")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auto, corp_rule
import mlib
from mlib import score as m_score, dday, TODAY
e = lambda s: html.escape(str(s), quote=True)

GATE_LABEL = {"none": "지금 지원 가능", "cert": "산업안전기사 필요", "maybe": "자격 언급(확인)", "other": "다른 자격 필요", "env": "환경 직무", "exp": "경력 요구", "chk": "직무 확인 필요", "thin": "근거 부족"}
GATE_ORDER = ["none", "cert", "maybe", "other", "env", "exp", "chk", "thin"]
GATE_PILL = {"none": "ok", "cert": "keep", "maybe": "keep", "other": "keep", "env": "bad", "exp": "bad", "chk": "", "thin": ""}


NOT_MGR = re.compile(r"생산직|비파괴|홍보|캠페인|콘텐츠|응급구조|화생방|안전\s*시설물|안전시설|시설물\s*설치|조공|보조공|신호수|유도원|지킴이|감시자|안전감시|안전\s*감독자|패트롤|순찰|안전\s*대원|안전\s*요원|통제원|서무|총무|사무\s*보조|경리|행정직|조경|교통안전|신호등|가로등|안전망|추락\s*방지|가설재|안전성\s*약리|식품|위생|세스코|플랫폼|개발자|연구실안전|재난안전|상황실|셔틀|동승|밸브|압력조정기|작업환경측정|전기전자제품|RI\s*(?:면허|안전)|사무직|구조물진단|계측|정밀안전|지하안전|소방점검|소방시설|소방\s*안전관리|안전점검\s*및\s*진단|시험\s*엔지니어|사고처리|선탑|차량통제|방사선|토질|구조해석|건물\s*관리사|단순")
MGR_EVID = re.compile(r"안전\s*(?:관리자|담당자?|보건|환경|팀|직|업무|보호관|Staff|책임)|안전.{0,8}관리자|안전\s*관리\s*(?:자|원|직|담당|팀|실)|보건\s*관리자|EHS|HSE|SHE|환경\s*안전|안전\s*환경|Safety|산업\s*안전|건설\s*안전|안전\s*기사|공개\s*채용|공채|인재\s*(?:POOL|Pool|pool)|안전\s*,|안전/|안전\s*관리|안전\s*(?:신입|경력)", re.I)

def not_manager(p):
    t = p.get("title") or ""
    return bool(NOT_MGR.search(t)) or not MGR_EVID.search(t)

def cls(x): return "ok" if x >= 80 else ("keep" if x >= 60 else "bad")

def build(broad_path, main_path, region_fallback=True):
    B = json.load(open(broad_path))["postings"]
    M = json.load(open(main_path))["postings"]
    MANUAL, MANUAL_THIN, _s, _n, _d = mlib.load_scores(M)
    manual_by_url = {}
    for i, p in enumerate(M):
        if i in MANUAL:
            s = MANUAL[i]
            manual_by_url[p["url"]] = dict(gate=s["gate"], now=m_score(s, p), aft=m_score(s, p, True),
                                           req=[(l, v, a) for l, v, a in s["req"]], pref=[(l, v, a) for l, v, a in s["pref"]], thin=False, manual=True)
        elif i in MANUAL_THIN:
            manual_by_url[p["url"]] = dict(gate="thin", thin=True, manual=True, req=[], pref=[], why=MANUAL_THIN[i])
    rows, dropped = [], []
    scope_dropped = []
    for p in B:
        _why = corp_rule.drop_reason(p)
        if _why:
            scope_dropped.append((p, _why)); continue
        a = auto.analyze_posting(p)
        o = manual_by_url.get(p["url"])
        if o:
            a.update(o); a["region"] = auto.region_of(p)
        dl, dd = dday(p)
        if dd is not None and dd < 0: continue
        a["chk"] = bool(not a.get("manual") and not_manager(p))
        a["thin"] = a.get("thin") or a["gate"] == "thin"
        g = "chk" if a["chk"] else ("thin" if a["thin"] else a["gate"])
        rows.append(dict(p=p, a=a, g=g, dl=dl, dd=dd))
    def key(r):
        a = r["a"]
        sc = a.get("aft", 0) if r["g"] in ("cert", "maybe") else a.get("now", 0)
        return (GATE_ORDER.index(r["g"]), bool(a.get("brief")) and not a.get("manual"), -sc, r["dl"] or "9999")
    rows.sort(key=key)
    build.dropped = dropped
    build.scope_dropped = scope_dropped
    return rows

def chips(a):
    out = []
    for l, v, af in a.get("req", []):
        if v is None: continue
        if v == 0.0:
            out.append(f'<span class="pill bad">{e(l)}</span>')
    for l, v, af in a.get("req", []):
        if v == 1.0 and l not in ("학력 요건",):
            out.append(f'<span class="pill ok">{e(l)}</span>')
    return "".join(out[:5])

def render(rows, generated_at, stats=None, failures=None, dropped=None, scope_dropped=None):
    n = len(rows)
    stats = stats or {}; failures = failures or []
    def stat_n(site, key):
        m = re.search(key + r" (\d+)", stats.get(site, "")); return int(m.group(1)) if m else 0
    list_n = stat_n("사람인", "목록"); undone = stat_n("사람인", r"상세 미조회\(한도\)")
    deleted = sum(stat_n(k, "사용자 삭제") for k in stats)
    failed = ", ".join(f[0] for f in failures)
    note = (f'종합건설사와 엔지니어링 회사는 상위 15개사만 싣고 전문건설업체와 회사명에 안전·세이프티가 들어간 업체는 뺐습니다({len(scope_dropped)}건, 아래 목록에서 확인). 신입이나 경력무관으로 표기된 공고는 모두 넣었습니다. 제목에 생산직·안전시설물 설치·신호수·소방점검 등이 있어 안전관리자 채용이 아닐 수 있는 공고는 직무 확인 필요로 따로 표시했습니다. 수집 한계: 사람인 목록 {list_n:,}건 중 {undone:,}건은 상세 본문을 읽는 한도를 넘어 목록 정보만으로 판정했습니다. '
            f'{e(failed)}는 접속이 막혀 수집하지 못했습니다. 이전 브리핑에서 삭제한 공고 {deleted}건은 다시 싣지 않았습니다. 워크넷·인크루트 등은 수집 대상이 아닙니다.')
    dropped = dropped or []
    scope_dropped = scope_dropped or []
    cnt = collections.Counter(r["g"] for r in rows)
    emp = collections.Counter((r["p"]["employment"] or "미표기") for r in rows)
    reg = collections.Counter(r["a"]["region"] for r in rows)
    src = collections.Counter(r["p"]["source"] for r in rows)
    def kpi(l, v, s, dot=None):
        d = f'<span class="dot" style="background:var(--{dot})"></span>' if dot else ""
        return f'<div class="kpi"><span class="l">{d}{l}</span><span class="v">{v}</span><span class="s">{s}</span></div>'
    kp = "".join([kpi("국내 신입 안전 공고", n, f"수집 {generated_at[:16].replace('T',' ')} KST", "primary"),
                  kpi("지금 지원 가능", cnt["none"], "자격 요건이 없거나 우대로만 기재", "success"),
                  kpi("산업안전기사 필요", cnt["cert"], "안전관리자 선임 자격 요구", "warning"),
                  kpi("자격 언급(확인)", cnt["maybe"], "본문에 안전 자격 언급, 필수 여부 확인", "warning"),
                  kpi("다른 자격 필요", cnt["other"] + cnt["env"], "건설안전·위험물·소방·환경 등", "warning"),
                  kpi("경력 요구", cnt["exp"], "본문에 경력 요건", "error"),
                  kpi("직무 확인 필요", cnt["chk"], "신입·경력무관 표기, 안전관리자가 아닐 수 있음", "warning"),
                  kpi("근거 부족", cnt["thin"], "요건 본문 없음", None)])
    mx = max(reg.values()) if reg else 1
    regbars = "".join(f'<div class="bar"><span class="k">{e(k)}</span><span class="t"><span class="f" style="width:{max(v/mx*100,2):.0f}%"></span></span><span class="v">{v}</span></div>'
                      for k, v in reg.most_common())
    empbars = "".join(f'<div class="bar"><span class="k">{e(k)}</span><span class="t"><span class="f keep" style="width:{max(v/max(emp.values())*100,2):.0f}%"></span></span><span class="v">{v}</span></div>' for k, v in emp.most_common())
    srcbars = "".join(f'<div class="bar"><span class="k">{e(k)}</span><span class="t"><span class="f ok" style="width:{max(v/max(src.values())*100,2):.0f}%"></span></span><span class="v">{v}</span></div>' for k, v in src.most_common())
    segs = '<button type="button" data-g="all" aria-pressed="true">전체 ' + str(n) + '</button>' + "".join(
        f'<button type="button" data-g="{g}" aria-pressed="false">{GATE_LABEL[g]} {cnt[g]}</button>' for g in GATE_ORDER)
    emp_opts = '<option value="">고용형태 전체</option>' + "".join(f'<option value="{e(k)}">{e(k)} ({v})</option>' for k, v in emp.most_common())
    reg_opts = '<option value="">지역 전체</option>' + "".join(f'<option value="{e(k)}">{e(k)} ({v})</option>' for k, v in reg.most_common())
    body = ""
    for k, r in enumerate(rows, 1):
        p, a, g = r["p"], r["a"], r["g"]
        ex = p.get("extra") or {}
        if g in ("thin", "chk"):
            sc = '<span class="sub">점수 없음</span><small class="sub">' + ("제목상 안전관리자 채용이 아닐 수 있음" if g == "chk" else "요건 본문 없음") + '</small>'
        else:
            now, aft = a["now"], a["aft"]
            if g in ("cert", "maybe") and aft != now:
                sc = f'<span class="big {cls(aft)}">{aft}<small>%</small></span><small class="sub">취득 후 · 현재 {now}%</small>'
            else:
                sc = f'<span class="big {cls(now)}">{now}<small>%</small></span><small class="sub">{"요건 간략 · 참고" if a.get("brief") and not a.get("manual") else ("지원 추천" if now>=80 else ("보완 후 가치" if now>=60 else "신중 검토"))}</small>'
        man = '<span class="pill pai">정밀 채점</span>' if a.get("manual") else ('<span class="pill">자동 채점</span>' if g not in ("thin", "chk") else "")
        if a.get("brief") and not a.get("manual"): man += '<span class="pill pw">요건 간략</span>'
        sal = ex.get("salary") or ""; st = ex.get("starter") or ""
        lv = f'{e(p["employment"] or "미표기")}' + ('' if p["level"] == p["employment"] else f'<small>{e(p["level"])}</small>')
        if sal: lv += f'<small class="sal">{e(sal)}</small>'
        if st:
            u = ex.get("starter_url"); lv += (f'<small class="sal"><a class="starter" href="{e(u)}" target="_blank" rel="noopener">{e(st)}</a></small>' if u else f'<small class="sal">{e(st)}</small>')
        dlc = '<td class="dl">채용 시 마감</td>' if not r["dl"] else (f'<td class="dl{" soon" if r["dd"] is not None and r["dd"] <= 3 else ""}">{e(r["dl"])}<small class="dd">{"D-DAY" if r["dd"]==0 else "D-%d" % r["dd"]}</small></td>')
        grp = "".join(f'<span class="pill pb">{e(x)}</span>' for x in (ex.get("groups") or [])) + (f'<span class="pill pk">{e(ex["listed"])} 상장</span>' if ex.get("listed") else "")
        reasons = a.get("why") or ""
        search = f'{p["company"]} {p["title"]} {a["region"]} {p["employment"]}'.lower()
        body += (f'<tr data-g="{g}" data-url="{e(p["url"])}" data-emp="{e(p["employment"] or "미표기")}" data-r="{e(a["region"])}" data-s="{e(search)}"><td class="rk"><input type="checkbox" class="xsel" data-url="{e(p["url"])}" data-company="{e(p["company"])}" data-title="{e(p["title"])}" aria-label="{e(p["company"])} 선택">{k}</td>'
                 f'<td class="corp"><strong><a class="co" href="{e(p["url"])}" target="_blank" rel="noopener">{e(p["company"])}</a></strong>{grp}'
                 f'<a class="tl" href="{e(p["url"])}" target="_blank" rel="noopener">{e(p["title"])}</a><small class="src2">{e(p["source"])}</small></td>'
                 f'<td>{e(a["region"])}</td><td class="lv">{lv}</td><td class="scc">{sc}<span class="pill {GATE_PILL[g]}">{GATE_LABEL[g]}</span> {man}</td>'
                 f'<td>{chips(a) or ("<small class=sub>" + e(reasons) + "</small>" if reasons else ("<small class=sub>공고에 학력·경력 요건만 기재</small>" if a.get("brief") else ""))}</td>{dlc}</tr>')
    table = ('<div class="scroll"><table class="tb"><thead><tr><th class="rkh"><input type="checkbox" class="pickall" aria-label="전체 선택">#</th><th>업체 · 공고</th><th>지역</th><th>고용형태 · 연봉</th><th>매칭도</th><th>요건</th><th>접수기한</th></tr></thead>'
             f'<tbody id="bt">{body}</tbody></table></div>')
    return f'''<section class="card" id="broad"><h2>국내 전체 신입 안전 채용<span class="n">{n}건 · 산업안전기사 등 자격을 요구하는 공고도 포함</span></h2>
<p class="sub-h">대기업·상장사 제한 없이 신입으로 지원할 수 있는 국내 안전 직무 공고를 모두 모았습니다(경력직 전용·마감·해외 근무 제외). 표 아래 '요건' 칸에서 빨간 칸은 지금 갖추지 못한 요건, 초록 칸은 충족한 요건입니다.</p>
<p class="note" style="margin:0 0 12px">{note}</p>
<div class="kpis">{kp}</div>
<div class="cols2" style="margin-top:16px"><div><h3 style="font-size:14px;margin:0 0 8px">지역별</h3><div class="bars wide">{regbars}</div></div>
<div><h3 style="font-size:14px;margin:0 0 8px">고용형태별</h3><div class="bars wide">{empbars}</div><h3 style="font-size:14px;margin:16px 0 8px">출처별</h3><div class="bars wide">{srcbars}</div></div></div>
<div class="tools" style="margin:16px 0 8px"><input id="bq" type="search" placeholder="회사·공고·지역 검색" aria-label="전체 공고 검색">
<select id="bemp" aria-label="고용형태">{emp_opts}</select><select id="breg" aria-label="지역">{reg_opts}</select></div>
<div class="seg" id="bseg" style="margin-bottom:8px">{segs}</div>
<p class="note" id="bcount" role="status" style="margin:0 0 8px"></p>
{table}

<p style="text-align:center;margin:12px 0 0"><button type="button" id="bmore" class="more" hidden>더 보기</button></p></section>'''

JS = '''<script>
(function(){
  var rows=[].slice.call(document.querySelectorAll('#bt tr')), seg=document.getElementById('bseg');
  if(!rows.length) return;
  var g='all', limit=60, q=document.getElementById('bq'), emp=document.getElementById('bemp'), reg=document.getElementById('breg'), cnt=document.getElementById('bcount'), more=document.getElementById('bmore');
  function run(reset){
    if(reset) limit=60;
    var s=q.value.trim().toLowerCase(), n=0, shown=0;
    rows.forEach(function(r){
      var ok=!r.classList.contains('xd')&&(g==='all'||r.dataset.g===g)&&(!emp.value||r.dataset.emp===emp.value)&&(!reg.value||r.dataset.r===reg.value)&&(!s||r.dataset.s.indexOf(s)>=0);
      if(ok) n++;
      r.hidden=!ok||n>limit; if(!r.hidden) shown++;
    });
    cnt.textContent='조건에 맞는 공고 '+n+'건 중 '+shown+'건 표시 · 전체 '+rows.length+'건';
    more.hidden=n<=limit; more.textContent='더 보기 ('+Math.min(60,n-limit)+'건)';
  }
  seg.addEventListener('click',function(ev){var b=ev.target.closest('button'); if(!b) return; g=b.dataset.g;
    [].forEach.call(seg.querySelectorAll('button'),function(x){x.setAttribute('aria-pressed',String(x===b))}); run(true);});
  q.addEventListener('input',function(){run(true)}); emp.addEventListener('change',function(){run(true)}); reg.addEventListener('change',function(){run(true)});
  more.addEventListener('click',function(){limit+=60; run(false)}); document.addEventListener('match-refilter',function(){run(false)}); run(true);
})();
</script>'''

if __name__ == "__main__":
    bp = sys.argv[1]
    rows = build(bp, MAIN_JSON)
    J = json.load(open(bp)); gen = J["generated_at"]
    out = render(rows, gen, J.get("stats"), J.get("failures"), build.dropped, build.scope_dropped) + JS
    cc = collections.Counter(r["g"] for r in rows)
    json.dump({"n": len(rows), "cnt": cc, "rule_dropped": len(build.scope_dropped)}, open(HERE + "/broad_stats.json", "w"))
    open(HERE + "/broad.html", "w").write(out)
    print(len(rows), collections.Counter(r["g"] for r in rows))
