"""안전관리자 신입 채용 브리핑 HTML 생성.

postings.json(공고) · excluded.json(조건 밖 공고)을 읽어 한 파일 HTML을 만든다.
  python3 safety_jobs/newgrad/build.py [YYYY-MM-DD]   # 기본: 오늘(KST)
출력: docs/안전관리자_신입_채용_브리핑_YYYY-MM-DD.html
마감일이 지난 공고와 사용자가 '제외 확정'한 공고(user_excluded.json, 아티팩트 db의 excluded 컬렉션 사본)는 빼고, first_seen이 오늘인 공고는 '신규'(파란 글씨)로 표시한다.
"""
import datetime, html, json, os, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
E = html.escape
KST = datetime.timezone(datetime.timedelta(hours=9))

GROUPS = [('big', '대기업·그룹 계열사'), ('foreign', '외국계 (한국 근무)'), ('con', '종합건설'),
          ('pub', '공공기관·협회'), ('etc', '상장사·중견')]
BNF_KEYS = ['기숙사', '사택', '자녀학자금', '주택대출', '주거지원']


def dleft(dl, today):
    try:
        return (datetime.date.fromisoformat(dl) - today).days
    except ValueError:
        return None


def meta(p):
    if p.get('search_firm'):
        return ('<div class="meta"><span class="mi"><span class="ml">초봉</span>고객사 비공개</span>'
                '<span class="mi"><span class="ml">직원 수</span>고객사 비공개</span></div>')

    def item(lab, v, b, u):
        if not v:
            return f'<span class="mi none2"><span class="ml">{lab}</span>확인 못 함</span>'
        old = ' old' if re.search(r'20(1\d|2[0-2])', b or '') else ''
        vv = f'<a href="{E(u)}" target="_blank" rel="noopener">{E(v)}</a>' if u else E(v)
        return f'<span class="mi{old}"><span class="ml">{lab}</span><b>{vv}</b><small>{E(b or "")}</small></span>'
    s, m = p.get('starter') or {}, p.get('employees') or {}
    return ('<div class="meta">' + item('신입 초봉', s.get('pay'), s.get('basis'), s.get('url'))
            + item('직원 수', m.get('count'), m.get('basis'), m.get('url')) + '</div>')


def empfmt(p):
    e = p['employment']
    if '계약' in e:
        return f'<b class=ow>{E(e)}</b>' + (' <span class=conv>(정규직 전환 가능)</span>' if p.get('conv') else '')
    return f'<b>{E(e)}</b>'


def row(p, rid, today):
    n = dleft(p['deadline'], today)
    urgent = n is not None and 0 <= n <= 3
    tag = ('D-day' if n == 0 else f'D-{n}') if n is not None else '상시'
    pills = ''.join(f'<a class="bp {E(b["kind"])}" href="{E(b["url"])}" target="_blank" rel="noopener" title="{E(b["title"])}">{E(b["label"])}</a>'
                    for b in p.get('benefits', [])) or '<span class="none">복지 정보 없음</span>'
    new = p.get('first_seen') == today.isoformat() and not p.get('baseline')
    note = f'<small>{E(p["note"])}</small>' if p.get('note') else ''
    return (f'<tr id="{rid}" class="{"new" if new else ""}" data-url="{E(p["url"])}" data-co="{E(p["company"])}" data-title="{E(p["title"])}">'
            f'<td class="pick"><input type="checkbox" class="sel" aria-label="{E(p["company"])} 선택"></td>'
            f'<td class="corp"><a class="co" href="{E(p["company_url"])}" target="_blank" rel="noopener" title="기업정보 보기">{E(p["company"])}</a>{"<span class=newtag>신규</span>" if new else ""}<small>{E(p.get("who", ""))}</small></td>'
            f'<td class="ttl"><a href="{E(p["url"])}" target="_blank" rel="noopener">{E(p["title"])}</a>{note}{meta(p)}</td>'
            f'<td class="emp">{empfmt(p)}<small>{E(p.get("level", ""))}</small><div class="bnf" aria-label="복지">{pills}</div></td>'
            f'<td class="q">{E(p.get("qualification") or "원문 확인")}</td>'
            f'<td class="dl{" urgent" if urgent else ""}" data-dl="{E(p["deadline"])}"><span class="d">{E(p["deadline"])}</span><span class="tag">{tag}</span></td>'
            f'<td class="src"><a href="{E(p["url"])}" target="_blank" rel="noopener">{E(p["source"])}</a></td></tr>')


def bars(items, cls):
    mx = max([v for _, v, _ in items] + [1])
    return ''.join(f'<div class="br"><span class="bl">{E(l)}</span><span class="track"><i class="{c or cls}" style="width:{v / mx * 100:.0f}%"></i></span><span class="bv">{v}</span></div>'
                   for l, v, c in items)


def quick(rows, today, empty):
    if not rows:
        return f'<p class="foot">{empty}</p>'
    return '<table class="quick">' + ''.join(
        f'<tr class="{"new" if p.get("first_seen") == today.isoformat() and not p.get("baseline") else ""}"><td><a href="#{rid}">{E(p["company"])}</a></td><td><a href="#{rid}">{E(p["title"])}</a></td>'
        f'<td class="d">{E(p["deadline"])}</td></tr>' for p, rid in rows) + '</table>'


def build(today):
    data = json.load(open(os.path.join(HERE, 'postings.json')))
    exc = json.load(open(os.path.join(HERE, 'excluded.json')))['items']
    uxp = os.path.join(HERE, 'user_excluded.json')
    ux = json.load(open(uxp))['items'] if os.path.exists(uxp) else []
    uxu = {x['url'] for x in ux}
    if ux:
        exc = exc + [{'reason': '직접 제외(제외 확정)', 'items': [f"{x.get('company', '')} · {x.get('title', '')}" for x in ux]}]
    css = open(os.path.join(HERE, 'style.css')).read()
    js = open(os.path.join(HERE, 'app.js')).read()
    live = [p for p in data['postings'] if p['url'] not in uxu and (dleft(p['deadline'], today) is None or dleft(p['deadline'], today) >= 0)]
    key = lambda p: (0 if p['deadline'][:4].isdigit() else 1, p['deadline'])
    rid = {p['url']: f'row-{i}' for i, p in enumerate(live)}
    by = {g: sorted([p for p in live if p['group'] == g], key=key) for g, _ in GROUPS}
    urgent = sorted([p for p in live if (lambda n: n is not None and 0 <= n <= 3)(dleft(p['deadline'], today))], key=key)
    new = [p for p in live if p.get('first_seen') == today.isoformat() and not p.get('baseline')]
    nb = sum(1 for p in live if p.get('benefits'))
    exn = sum(len(x['items']) for x in exc)

    secs = ''.join(
        f'<section class="card grp" id="{g}"><div class="sh"><h2>{name}</h2><span class="cnt" data-cnt>{len(by[g])}건</span></div>'
        f'<div class="scroll"><table><thead><tr><th class="pick"><input type="checkbox" class="all" aria-label="{name} 전체 선택"></th>'
        f'<th>업체명</th><th>공고명 · 신입 초봉 · 직원 수</th><th>고용형태 · 복지</th><th>지원 자격</th><th>접수기한</th><th>출처</th></tr></thead>'
        f'<tbody>{"".join(row(p, rid[p["url"]], today) for p in by[g])}</tbody></table></div></section>'
        for g, name in GROUPS)
    tiles = [('전체 공고', len(live), '', '#big'), ('신규', len(new), 'k-new', '#new'), ('3일 이내 마감', len(urgent), 'k-err', '#urgent'),
             ('대기업 계열', len(by['big']), '', '#big'), ('외국계', len(by['foreign']), '', '#foreign'), ('종합건설', len(by['con']), '', '#con'),
             ('공공기관·협회', len(by['pub']), '', '#pub'), ('복지 확인', nb, '', '#bnfchart'), ('조건 밖 제외', exn, 'k-cap', '#exc')]
    kp = ''.join(f'<a class="kpi {c}" href="{h}"><span class="kl">{l}</span><span class="kv"{" id=kv-total" if l == "전체 공고" else ""}>{v}</span><span class="go">목록으로 ↓</span></a>'
                 for l, v, c, h in tiles)
    cnt = [0] * 5
    for p in live:
        n = dleft(p['deadline'], today)
        cnt[4 if n is None else 0 if n <= 3 else 1 if n <= 7 else 2 if n <= 14 else 3] += 1
    dl = bars(list(zip(['3일 이내', '4~7일', '8~14일', '15일 이후', '채용 시 마감'], cnt, ['err', 'warn', 'pri', 'pri2', 'cap'])), '')
    gb = bars([(n.split(' (')[0], len(by[g]), 'pri') for g, n in GROUPS], 'pri')
    bc = Counter(b['label'] for p in live for b in p.get('benefits', []))
    bb = bars([(k, bc.get(k, 0), 'pri2') for k in BNF_KEYS], 'pri2')
    exrows = ''.join(f'<tr><td class="er">{E(x["reason"])}</td><td class="num">{len(x["items"])}</td><td>{E(" · ".join(x["items"]))}</td></tr>' for x in exc)
    rules = ('<table class="rules"><tr><th class="ok">포함</th><td>신입 · 경력무관 · 신입/경력 | 100대 그룹 계열사 | 외국계(한국 근무) | 공공기관·협회 | 종합건설 시평 50위 이내 정규직 · 10위 이내 계약직 | 설계사 10위 이내</td></tr>'
             '<tr><th class="no">제외</th><td>경력직 전용(경력 N년 이상) | 감시단·감시원 | 전기안전관리자 | 전문건설업체 | 안전이 주업무가 아닌 직종</td></tr>'
             '<tr><th>표시</th><td><b style="color:var(--primary)">파란 글씨 = 오늘 새로 찾은 공고</b> · <b class="no">빨간 접수기한 = 3일 이내 마감</b> · <b style="color:var(--orange)">주황 = 계약직</b> · 숫자 타일을 누르면 해당 목록으로 이동</td></tr></table>')
    now = datetime.datetime.now(KST).strftime('%H:%M')
    doc = f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>안전관리자 신입 채용 브리핑</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap">
<style>{css}</style></head><body>
<header class="top"><h1>안전관리자 신입 채용 브리핑</h1><span class="when">{today.isoformat()} {now} KST · ChatGPT 웹 검색 + 수집분 대조</span>
<div class="tools"><span class="selmsg" id="selmsg" role="status"></span><button type="button" id="del" class="danger" disabled>선택 삭제</button><span id="cfm" role="group" aria-label="제외 확인" hidden><button type="button" id="yes" class="danger">제외 확정</button> <button type="button" id="no">취소</button></span><button type="button" id="print">A4 인쇄</button>
<button type="button" class="icon" id="theme" aria-label="라이트/다크 테마 전환" title="테마 전환"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button></div></header>
<main>
<div class="kpis">{kp}</div>
<div class="viz">
<section class="card"><h2>접수 마감 분포</h2>{dl}</section>
<section class="card"><h2>구분별 공고</h2>{gb}</section>
<section class="card" id="bnfchart"><h2>주요 복지 확인 건수</h2>{bb}<div class="legend" style="margin-top:8px"><a class="bp post">공고 명시</a><a class="bp web">인터넷 조사</a><span>배지를 누르면 근거가 열립니다</span></div></section>
</div>
<div class="viz">
<section class="card" id="new"><div class="sh"><h2>신규 공고</h2><span class="cnt">{len(new)}건 · 오늘 ChatGPT로 새로 찾음</span></div>{quick([(p, rid[p['url']]) for p in new], today, '오늘 새로 찾은 공고가 없습니다.')}</section>
<section class="card" id="urgent"><div class="sh"><h2>3일 이내 마감</h2><span class="cnt">{len(urgent)}건</span></div>{quick([(p, rid[p['url']]) for p in urgent], today, '3일 이내 마감 공고가 없습니다.')}</section>
</div>
<section class="card"><h2 style="font-size:18px;margin:0 0 8px">선별 조건</h2>{rules}</section>
{secs}
<section class="card"><details class="xl"><summary>제외한 공고 (직접 선택) <b id="xcnt" style="margin-left:6px">0</b>건 · 되돌리기</summary><ul id="xitems"></ul></details></section>
<section class="card" id="exc"><div class="sh"><h2>조건 밖이라 뺀 공고</h2><span class="cnt">{exn}건</span></div><div class="scroll"><table class="rules ex"><thead><tr><th>사유</th><th class="num">건수</th><th>공고</th></tr></thead><tbody>{exrows}</tbody></table></div>
<p class="foot">신입 초봉·직원 수는 공시·알리오·잡코리아·캐치·자소설닷컴 등에서 기준 시점과 함께 확인(값을 누르면 근거). 신규 공고는 ChatGPT(gpt-5-search-api) 웹 검색으로 찾아 내용을 채웠습니다. 지원 전 원문 확인.</p></section>
</main>
<script>{js}</script></body></html>'''
    out = os.path.join(ROOT, 'docs', f'안전관리자_신입_채용_브리핑_{today.isoformat()}.html')
    open(out, 'w').write(doc)
    print(out, len(live), 'new', len(new), 'urgent', len(urgent))
    return out


if __name__ == '__main__':
    d = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.datetime.now(KST).date()
    build(d)
