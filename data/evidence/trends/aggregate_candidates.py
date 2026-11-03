import json,glob,csv,statistics as st
from collections import defaultdict
S={}
for f in glob.glob('data/evidence/trends/.cache/*.json'):
    d=json.load(open(f)); k,tf,g,dt=d['key'].split('|')
    if tf=='today 5-y' and dt=='2026-11-03': S[k]=d['series']
niche={};cur=None;order=[]
for l in open('data/evidence/trends/candidates.txt'):
    l=l.strip()
    if l.startswith('# niche:'): cur=l.split(':')[1].strip()
    elif l and not l.startswith('#'): niche[l]=cur; order.append(l)
base={r['keyword']:r for r in csv.DictReader(open('data/evidence/trends/candidates-2026-11-03.csv'))}
def mean(x): return sum(x)/len(x) if x else 0
rows=[]
for k in order:
    s=S[k]; v=[x for _,x in s]; dts=[d for d,_ in s]
    l104=v[-104:]; zero=sum(1 for x in l104 if x==0)/len(l104)
    # post-spike YoY: last 20 weeks vs same 20 weeks a year earlier
    a=mean(v[-20:]); b=mean(v[-72:-52]); yoy=(a-b)/b if b else None
    # spike: mean of weeks dated 2026-04-01..2026-06-30 vs mean of other weeks in last 52
    sp=[x for d,x in s[-52:] if '2026-04-01'<=d<='2026-06-30']; ot=[x for d,x in s[-52:] if not('2026-04-01'<=d<='2026-06-30')]
    spike=mean(sp)/mean(ot) if mean(ot) else None
    # Q4 index: mean Oct15-Dec31 weeks 2021-2025 vs overall mean of 2021-2025 (before 2026)
    hist=[(d,x) for d,x in s if d<'2026-01-01']
    q4=[x for d,x in hist if ('10-15'<=d[5:]<='12-31')]; allm=mean([x for _,x in hist])
    q4i=mean(q4)/allm if allm else None
    r=base[k]
    rows.append(dict(niche=niche[k],keyword=k,mean_12m=float(r['mean_interest_12m']),growth=float(r['growth_12m_vs_prior']) if r['growth_12m_vs_prior'] else None,
      peak=r['peak_months'],seas=float(r['seasonality_ratio']) if r['seasonality_ratio'] else None,zero_share_104w=round(zero,2),
      yoy_last20w=None if yoy is None else round(yoy,2),spike_ratio=None if spike is None else round(spike,2),q4_index=None if q4i is None else round(q4i,2),
      last_8w_mean=round(mean(v[-8:]),1),sparse=zero>=0.25 or float(r['mean_interest_12m'])<10))
with open('data/evidence/trends/candidates-2026-11-03-keyword-metrics.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
def med(x):
    x=[a for a in x if a is not None]; return round(st.median(x),2) if x else None
N=defaultdict(list)
for r in rows:N[r['niche']].append(r)
out=[]
for n,rs in N.items():
    good=[r for r in rs if not r['sparse']]
    pk=defaultdict(int)
    for r in rs:
        for m in r['peak'].split(','):pk[m]+=1
    out.append(dict(niche=n,n_kw=len(rs),n_sparse=len(rs)-len(good),med_mean12m=med([r['mean_12m'] for r in rs]),
      med_growth=med([r['growth'] for r in rs]),share_growing=round(sum(1 for r in rs if r['growth'] and r['growth']>0)/len(rs),2),
      med_growth_nonsparse=med([r['growth'] for r in good]),
      med_yoy_last20w=med([r['yoy_last20w'] for r in rs]),med_yoy_nonsparse=med([r['yoy_last20w'] for r in good]),
      share_yoy_pos=round(sum(1 for r in rs if r['yoy_last20w'] and r['yoy_last20w']>0)/len(rs),2),
      share_yoy_pos_nonsparse=round(sum(1 for r in good if r['yoy_last20w'] and r['yoy_last20w']>0)/len(good),2) if good else None,
      med_seas=med([r['seas'] for r in rs]),med_spike=med([r['spike_ratio'] for r in rs]),med_q4=med([r['q4_index'] for r in rs]),
      top_peaks=";".join(f"{m}:{c}" for m,c in sorted(pk.items(),key=lambda x:-x[1])[:3]),med_zero=med([r['zero_share_104w'] for r in rs])))
with open('data/evidence/trends/candidates-2026-11-03-niche-summary.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=out[0].keys()); w.writeheader(); w.writerows(out)
for o in out:print(o)
print()
for r in rows:print(r['niche'][:8],r['keyword'],r['mean_12m'],r['growth'],r['yoy_last20w'],r['zero_share_104w'],r['spike_ratio'],r['q4_index'],r['sparse'])
