"""공고별 매칭도 계산 → private/match.json (커밋하지 않음).

매칭 브리핑(safety_jobs/match)의 채점 방식을 그대로 쓴다: 필수 40 · 우대 20 · 경력 20 · 기업 10(지역 제외, 100으로 환산).
- private/scores.json(직접 채점, 매칭 브리핑 아티팩트 pipeline/에서 받음)에 있는 공고는 그 값을 쓰고,
- 없으면 공고 본문(postings.json의 detail_text)을 match_auto.py로 자동 채점한다.
  python3 safety_jobs/newgrad/match.py
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PRIV = os.path.join(HERE, 'private')
sys.path.insert(0, HERE)
import match_auto as auto  # noqa: E402


def ind_value(p):
    base = {'A': 1.0, 'B': 0.8, 'F': 0.8}.get(p.get('hilite') or '')
    if base is None:
        base = 0.8 if p['group'] in ('big', 'foreign') else 0.6 if (p.get('listed') or p['group'] in ('pub', 'etc')) else 0.4
    e = p.get('employment', '')
    ev = 0.6 if ('계약' in e and p.get('conv')) else 0.4 if '계약' in e else 1.0 if e == '정규직' else 0.5
    return round((base + ev) / 2, 3)


def mean(items, after=False):
    v = [(a if after and a is not None else x) for _, x, a in items]
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def score(req, pref, career, ind, after=False):
    parts = [(40, mean(req, after)), (20, mean(pref, after)), (20, career), (10, ind)]
    num = sum(w * v for w, v in parts if v is not None)
    den = sum(w for w, v in parts if v is not None)
    return round(num / den * 100)


def judgment(gate, now):
    if gate == 'none':
        return '지원 권장' if now >= 70 else '조건부 지원'
    if gate in ('cert', 'maybe'):
        return '조건부 지원'
    return '신중 검토'


def bucket(gate):
    return 'now' if gate == 'none' else 'cert' if gate in ('cert', 'maybe') else 'careful'


def main():
    posts = json.load(open(os.path.join(HERE, 'postings.json')))['postings']
    J = json.load(open(os.path.join(PRIV, 'scores.json')))
    alias = J.get('ALIAS', {})
    pick = lambda t, u: t.get(u, t.get(alias.get(u, ''), None))
    out = {}
    for p in posts:
        u, ind = p['url'], ind_value(p)
        s = pick(J['S'], u)
        if s is not None:
            req = [tuple(x) for x in s.get('req', [])]
            pref = [tuple(x) for x in s.get('pref', [])]
            gate = s.get('gate', 'none')
            now, aft = score(req, pref, s.get('career', 1.0), ind), score(req, pref, s.get('career', 1.0), ind, True)
            out[u] = dict(kind='직접 채점', gate=gate, bucket=bucket(gate), now=now, aft=aft, judgment=judgment(gate, now),
                          req=req, pref=pref, up=s.get('up', ''), gap=s.get('gap', ''), todo=s.get('todo', ''))
            continue
        t = pick(J['THIN'], u)
        if t is not None:
            out[u] = dict(kind='근거 부족', bucket='thin', reason=t)
            continue
        k = pick(J['SKIP'], u)
        if k is not None:
            out[u] = dict(kind='분석 제외', bucket='skip', reason=k)
            continue
        if not (p.get('detail_text') or '').strip():
            out[u] = dict(kind='근거 부족', bucket='thin', reason='공고 본문 미수집 — 원문에서 요건 확인')
            continue
        a = auto.analyze_posting({**p, 'extra': {}, 'employment': '계약직' if '계약' in p['employment'] else p['employment']})
        if a['thin']:
            out[u] = dict(kind='근거 부족', bucket='thin', reason='자동 채점: 요건 미기재')
            continue
        now, aft = score(a['req'], a['pref'], 0.0 if a['gate'] == 'exp' else 1.0, ind), score(a['req'], a['pref'], 0.0 if a['gate'] == 'exp' else 1.0, ind, True)
        out[u] = dict(kind='자동 채점', gate=a['gate'], bucket=bucket(a['gate']), now=now, aft=aft, judgment=judgment(a['gate'], now),
                      req=a['req'], pref=a['pref'], up='', gap='', todo='', brief=a.get('brief', False))
    json.dump(out, open(os.path.join(PRIV, 'match.json'), 'w'), ensure_ascii=False, indent=1)
    from collections import Counter
    print('match', len(out), Counter(v['bucket'] for v in out.values()))


if __name__ == '__main__':
    main()
