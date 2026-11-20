from collections import Counter
import math
WINDOWS=(10,20,30,50,90,180,365)
def compute(draws):
 nobs=len(draws); last=set(draws[-1][1]); prev=[set(x[1]) for x in draws[-10:]]
 counts={w:Counter(n for _,ns in draws[-w:] for n in ns) for w in WINDOWS}
 pair=Counter()
 for _,ns in draws[-180:]:
  s=sorted(ns)
  for i,a in enumerate(s):
   for b in s[i+1:]: pair[(a,b)]+=1
 rows=[]
 for n in range(1,81):
  gap=next((i for i,(_,ns) in enumerate(reversed(draws)) if n in ns),nobs)
  fs={w:counts[w][n]/max(1,min(w,nobs)) for w in WINDOWS}
  mean_freq=sum(fs.values())/len(fs); momentum=fs[10]-fs[90]; trend=fs[30]-fs[180]
  repeat=1.0 if n in last else 0.0
  transition=sum(1 for s in prev if n in s)/max(1,len(prev))
  neighbors=sum(pair[tuple(sorted((n,m)))] for m in last if m!=n)/max(1,len(last))
  network=neighbors/max(1,180)
  stability=1-(max(fs.values())-min(fs.values()))
  uncertainty=(1/math.sqrt(max(1,nobs)))+.25*(max(fs.values())-min(fs.values()))
  rows.append({'number':n,'gap':gap,'gap_class':gap_class(gap),'return_class':return_class(gap),
    'frequency':mean_freq,'momentum':momentum,'trend':trend,'repeat':repeat,'transition':transition,
    'network':network,'stability':stability,'uncertainty':uncertainty,**{f'freq_{w}':fs[w] for w in WINDOWS}})
 return rows
def gap_class(g):
 return 'G0_3' if g<=3 else 'G4_7' if g<=7 else 'G8_15' if g<=15 else 'G16_30' if g<=30 else 'G31_PLUS'
def return_class(g): return gap_class(g).replace('G','R',1)
