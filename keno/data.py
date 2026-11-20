import csv, hashlib, shutil
from pathlib import Path
from datetime import datetime
HEADERS=['date']+[f'n{i}' for i in range(1,21)]
def sha256(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def backup(path,folder):
 folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);src=Path(path)
 dst=folder/f'{src.stem}_{datetime.now():%Y%m%d_%H%M%S}{src.suffix}';shutil.copy2(src,dst);return dst
def load_draws(path):
 out=[];errs=[]
 with open(path,encoding='utf-8-sig',newline='') as f:
  rd=csv.DictReader(f)
  if rd.fieldnames!=HEADERS: raise ValueError('Hibás CSV fejléc')
  for rn,r in enumerate(rd,2):
   try:
    d=datetime.strptime(r['date'],'%Y-%m-%d').date(); ns=[int(r[f'n{i}']) for i in range(1,21)]
    if len(set(ns))!=20 or any(n<1 or n>80 for n in ns) or ns!=sorted(ns): raise ValueError('20 egyedi, rendezett, 1-80 közötti szám szükséges')
    out.append((d,ns))
   except Exception as e: errs.append((rn,str(e)))
 if errs: raise ValueError(f'{len(errs)} hibás sor, első: {errs[0]}')
 out.sort(); return out
