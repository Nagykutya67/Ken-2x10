import random,statistics,math,json
from .model import forecast
from .data import load_draws
def hits(p,actual):
 s=set(actual);return len(set(p['frame'])&s),len(set(p['A'])&s),len(set(p['B'])&s)
def run(draws,champion,challenger,test_size=1000,min_train=365):
 start=max(min_train,len(draws)-test_size);out=[]
 for i in range(start,len(draws)):
  c=forecast(draws[:i],champion);q=forecast(draws[:i],challenger);hc=hits(c,draws[i][1]);hq=hits(q,draws[i][1]);out.append((str(draws[i][0]),hc,hq))
 return out
def bootstrap(diffs,reps=2000,seed=20261120):
 rng=random.Random(seed);n=len(diffs);means=[]
 for _ in range(reps):means.append(sum(diffs[rng.randrange(n)] for _ in range(n))/n)
 means.sort();return means[int(.025*reps)],means[int(.975*reps)]
def gate(rows):
 diffs=[q[0]-c[0] for _,c,q in rows];uplift=statistics.mean(diffs);lo,hi=bootstrap(diffs)
 chunks=[diffs[i::3] for i in range(3)];periods=sum(statistics.mean(x)>0 for x in chunks if x)
 tailc=sorted(c[0] for _,c,q in rows)[max(0,int(.1*len(rows))-1)];tailq=sorted(q[0] for _,c,q in rows)[max(0,int(.1*len(rows))-1)]
 abd=abs(statistics.mean(c[1]-c[2] for _,c,q in rows)-statistics.mean(q[1]-q[2] for _,c,q in rows))
 reasons=[]
 if len(rows)<1000:reasons.append('minimum 1000 minta hiányzik')
 if uplift<=0:reasons.append('nincs pozitív uplift')
 if lo<=0:reasons.append('bootstrap CI alsó határ nem pozitív')
 if periods<3:reasons.append('nem javul mindhárom időszakban')
 if tailq<tailc:reasons.append('alsó tized romlik')
 if abd>.25:reasons.append('A/B egyensúly romlik')
 return {'n':len(rows),'uplift':uplift,'ci_low':lo,'ci_high':hi,'positive_periods':periods,'lower_tail_delta':tailq-tailc,'ab_balance_delta':abd,'decision':'PASS' if not reasons else 'REJECT','reasons':reasons}
