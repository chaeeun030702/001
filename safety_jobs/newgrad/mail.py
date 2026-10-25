"""메일 본문(인라인 스타일 HTML) 생성: 숫자 요약 · 신규 공고 · 3일 이내 마감 · 아티팩트 링크.

  python3 safety_jobs/newgrad/mail.py [YYYY-MM-DD]
출력: safety_jobs/newgrad/out/mail_YYYY-MM-DD.html (Gmail htmlBody로 그대로 사용)
"""
import datetime, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape
ART = 'https://claude.ai/artifact/6o7keJV5TZ5rTWA77iKfpw'
KST = datetime.timezone(datetime.timedelta(hours=9))


def dleft(dl, today):
    try:
        return (datetime.date.fromisoformat(dl) - today).days
    except ValueError:
        return None


def table(rows, today, red, new=()):
    if not rows:
        return '<p style="color:#737373;font-size:13px;margin:4px 0 0">해당 공고가 없습니다.</p>'
    tr = ''
    for p in rows:
        n = dleft(p['deadline'], today)
        dc = '#E63B3B' if (n is not None and 0 <= n <= 3) else '#303030'
        ec = '#FE6F3F' if '계약' in p['employment'] else '#1C1C1C'
        nc = '#0F6FFF' if (red == 'new' or p in new) else '#1C1C1C'
        st, em = p.get('starter') or {}, p.get('employees') or {}
        sub = ' · '.join(x for x in [('초봉 ' + st['pay']) if st.get('pay') else '', ('직원 ' + em['count']) if em.get('count') else ''] if x)
        tr += (f'<tr><td style="padding:8px;border-bottom:1px solid #E9EBEF"><b style="color:{nc}">{E(p["company"])}</b><br><span style="color:#737373;font-size:12px">{E(p.get("who", ""))}</span></td>'
               f'<td style="padding:8px;border-bottom:1px solid #E9EBEF"><a href="{E(p["url"])}" style="color:{nc};text-decoration:none">{E(p["title"])}</a>{('<br><span style="color:#737373;font-size:12px">' + E(sub) + '</span>') if sub else ''}</td>'
               f'<td style="padding:8px;border-bottom:1px solid #E9EBEF;color:{ec};white-space:nowrap">{E(p["employment"])}</td>'
               f'<td style="padding:8px;border-bottom:1px solid #E9EBEF;color:{dc};white-space:nowrap;font-weight:700">{E(p["deadline"])}</td></tr>')
    return f'<table style="border-collapse:collapse;width:100%;font-size:13px">{tr}</table>'


def build(today):
    d = json.load(open(os.path.join(HERE, 'postings.json')))
    uxp = os.path.join(HERE, 'user_excluded.json')
    uxu = {x['url'] for x in json.load(open(uxp))['items']} if os.path.exists(uxp) else set()
    live = [p for p in d['postings'] if p['url'] not in uxu and (dleft(p['deadline'], today) is None or dleft(p['deadline'], today) >= 0)]
    new = [p for p in live if p.get('first_seen') == today.isoformat() and not p.get('baseline')]
    urg = sorted([p for p in live if (lambda n: n is not None and 0 <= n <= 3)(dleft(p['deadline'], today))], key=lambda p: p['deadline'])
    cnt = {g: sum(1 for p in live if p['group'] == g) for g in ['big', 'foreign', 'con', 'pub', 'etc']}
    tiles = [('전체', len(live), '#000'), ('신규', len(new), '#0F6FFF'), ('3일 이내 마감', len(urg), '#E63B3B'),
             ('대기업 계열', cnt['big'], '#000'), ('외국계', cnt['foreign'], '#000'), ('종합건설', cnt['con'], '#000'), ('공공기관·협회', cnt['pub'], '#000')]
    tl = ''.join(f'<td style="padding:10px;border:1px solid #E2E4E9;border-radius:8px;text-align:center"><div style="font-size:12px;color:#737373">{l}</div><div style="font-size:22px;font-weight:700;color:{c}">{v}</div></td>' for l, v, c in tiles)
    names = [('big', '대기업·그룹 계열사'), ('foreign', '외국계'), ('con', '종합건설'), ('pub', '공공기관·협회'), ('etc', '상장사·중견')]
    key = lambda p: (0 if p['deadline'][:4].isdigit() else 1, p['deadline'])
    groups = ''.join(f'<h3 style="margin:18px 0 4px">{n} {cnt[g]}건</h3>' + table(sorted([p for p in live if p['group'] == g], key=key), today, 'all', new) for g, n in names)
    body = f'''<div style="font-family:'Apple SD Gothic Neo','Noto Sans KR',sans-serif;color:#1C1C1C;max-width:760px">
<h2 style="margin:0 0 4px">안전관리자 신입 채용 브리핑 ChatGPT · {today.isoformat()}</h2>
<p style="margin:0 0 12px;color:#737373;font-size:13px">ChatGPT 웹 검색 + 수집분 대조 · 전체 내용(신입 초봉·직원 수·복지·선택 삭제)은 <a href="{ART}" style="color:#0F6FFF">브리핑 아티팩트</a>에서 보세요.</p>
<table style="border-collapse:separate;border-spacing:6px;width:100%"><tr>{tl}</tr></table>
<h3 style="margin:16px 0 4px;color:#0F6FFF">신규 공고 {len(new)}건</h3>{table(new, today, 'new')}
<h3 style="margin:16px 0 4px;color:#E63B3B">3일 이내 마감 {len(urg)}건</h3>{table(urg, today, 'urg')}
{groups}
<p style="margin:16px 0 0;font-size:12px;color:#737373">파란 글씨 = 오늘 새로 찾은 공고 · 빨간 날짜 = 3일 이내 마감 · 주황 = 계약직. 지원 전 원문을 확인하세요.</p></div>'''
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    out = os.path.join(HERE, 'out', f'mail_{today.isoformat()}.html')
    open(out, 'w').write(body)
    print(out, 'new', len(new), 'urgent', len(urg))


if __name__ == '__main__':
    build(datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.datetime.now(KST).date())
