from .features import compute
DEFAULT_WEIGHTS={'frequency':.25,'gap':.18,'momentum':.12,'trend':.08,'repeat':.08,'transition':.12,'network':.08,'stability':.09}
def score(draws,weights=None):
 w={**DEFAULT_WEIGHTS,**(weights or {})}; rows=compute(draws)
 for r in rows:
  gap=min(r['gap'],30)/30
  comps={'frequency':r['frequency'],'gap':gap,'momentum':r['momentum']+.25,'trend':r['trend']+.25,
    'repeat':r['repeat'],'transition':r['transition'],'network':r['network'],'stability':r['stability']}
  r['components']=comps;r['score']=sum(w[k]*comps[k] for k in w);r['positive']=[k for k,v in sorted(comps.items(),key=lambda x:-x[1])[:3]];r['negative']=[k for k,v in sorted(comps.items(),key=lambda x:x[1])[:3]]
 return sorted(rows,key=lambda r:(-r['score'],r['number']))
def forecast(draws,weights=None):
 ranking=score(draws,weights); frame=[r['number'] for r in ranking[:20]];by={r['number']:r for r in ranking}
 A=[];B=[];sa=sb=0
 for n in frame:
  if len(A)==10:B.append(n);continue
  if len(B)==10:A.append(n);continue
  if sa<=sb:A.append(n);sa+=by[n]['score']
  else:B.append(n);sb+=by[n]['score']
 return {'frame':sorted(frame),'A':sorted(A),'B':sorted(B),'ranking':ranking,'weights':weights or DEFAULT_WEIGHTS}
