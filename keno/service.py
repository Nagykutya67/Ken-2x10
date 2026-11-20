import json, hashlib, random, statistics
from pathlib import Path
from datetime import datetime,timedelta
from .data import load_draws,sha256,backup
from .model import forecast,DEFAULT_WEIGHTS
from .database import Database
class Service:
 def __init__(self,root):
  self.root=Path(root);self.data=self.root/'data/draws.csv';self.db=Database(self.root/'data/keno_v21.sqlite')
 def import_draws(self):
  draws=load_draws(self.data);h=sha256(self.data)
  with self.db.connect() as c:
   for d,ns in draws:c.execute('INSERT OR REPLACE INTO draws VALUES(?,?,?)',(str(d),json.dumps(ns),h))
  return draws
 def champion(self):
  r=self.db.rows("SELECT * FROM model_configs WHERE status='CHAMPION' ORDER BY created_at DESC LIMIT 1")[0];r['weights']=json.loads(r['weights_json']);return r
 def create_forecast(self,force=False):
  draws=self.import_draws(); target=str(draws[-1][0]+timedelta(days=1));m=self.champion();p=forecast(draws,m['weights']);now=datetime.now().isoformat(timespec='seconds')
  ranking=json.dumps(p['ranking'],ensure_ascii=False,separators=(',',':'))
  with self.db.connect() as c:
   old=c.execute('SELECT id FROM forecasts WHERE forecast_for=?',(target,)).fetchone()
   if old and not force:return self.get_forecast(old['id'])
   if old:c.execute('DELETE FROM forecasts WHERE id=?',(old['id'],))
   fid=c.execute('''INSERT INTO forecasts(forecast_for,sealed_at,model_version,training_start,training_end,input_sha256,seed,frame_json,a_json,b_json,ranking_json,weights_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',(target,now,m['version'],str(draws[0][0]),str(draws[-1][0]),sha256(self.data),20261120,json.dumps(p['frame']),json.dumps(p['A']),json.dumps(p['B']),ranking,json.dumps(m['weights']))).lastrowid
  return self.get_forecast(fid)
 def get_forecast(self,fid):
  r=self.db.rows('SELECT * FROM forecasts WHERE id=?',(fid,))[0]
  for k in ['frame_json','a_json','b_json','ranking_json','weights_json']:r[k[:-5] if k.endswith('_json') else k]=json.loads(r[k])
  return r
 def evaluate_pending(self):
  draws=self.import_draws();actual={str(d):ns for d,ns in draws};done=[]
  for f in self.db.rows("SELECT * FROM forecasts WHERE status='SEALED'"):
   if f['forecast_for'] not in actual:continue
   p=self.get_forecast(f['id']);s=set(actual[f['forecast_for']]);F=set(p['frame']);A=set(p['a']);B=set(p['b'])
   with self.db.connect() as c:
    eid=c.execute('INSERT OR IGNORE INTO evaluations(forecast_id,actual_json,frame_hits,a_hits,b_hits,best_row_hits,precision20,evaluated_at) VALUES(?,?,?,?,?,?,?,?)',(f['id'],json.dumps(sorted(s)),len(F&s),len(A&s),len(B&s),max(len(A&s),len(B&s)),len(F&s)/20,datetime.now().isoformat(timespec='seconds'))).lastrowid
    if not eid:continue
    rank={r['number']:(i+1,r) for i,r in enumerate(p['ranking'])};selected=sorted(F-s,key=lambda n:rank[n][1]['score'])
    misses=sorted(s-F,key=lambda n:rank[n][0]);
    for i,n in enumerate(misses):
     rk,r=rank[n];disp=selected[i] if i<len(selected) else None;types=[]
     if rk<=25:types.append('THRESHOLD_MISS')
     if r['gap']>=8:types.append('RETURN_MISS')
     if r['freq_365']>=.26 and r['freq_10']<.2:types.append('STRONG_LONG_TERM_MISS')
     if r['transition']>=.3:types.append('TRANSITION_MISS')
     if r['momentum']>0.05:types.append('LATE_MOMENTUM_MISS')
     if not types:types=['LOW_SIGNAL_MISS']
     c.execute('''INSERT INTO missed_winners(evaluation_id,number_value,original_rank,threshold_gap,score,gap_value,return_class,gap_class,supporters_json,opponents_json,transition_origin,network_origin,uncertainty,displaced_number,error_types_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(eid,n,rk,r['score']-p['ranking'][19]['score'],r['score'],r['gap'],r['return_class'],r['gap_class'],json.dumps(r['positive']),json.dumps(r['negative']),r['transition'],r['network'],r['uncertainty'],disp,json.dumps(types)))
     for t in types:c.execute('INSERT INTO evidence(evaluation_id,evidence_type,class_key,support_count,impact,strength,created_at) VALUES(?,?,?,?,?,?,?)',(eid,'MISSED_WINNER',t,1,1.0,max(.05,1-rk/80),datetime.now().isoformat(timespec='seconds')))
    for n in selected:
     rk,r=rank[n];cf=misses[0] if misses else None;c.execute('INSERT INTO selected_misses(evaluation_id,number_value,original_rank,score,supporters_json,opponents_json,counterfactual_number) VALUES(?,?,?,?,?,?,?)',(eid,n,rk,r['score'],json.dumps(r['positive']),json.dumps(r['negative']),cf))
    c.execute("UPDATE forecasts SET status='EVALUATED' WHERE id=?",(f['id'],));done.append(eid)
  return done
 def latest_misses(self,limit=100):return self.db.rows('''SELECT mw.*,f.forecast_for FROM missed_winners mw JOIN evaluations e ON e.id=mw.evaluation_id JOIN forecasts f ON f.id=e.forecast_id ORDER BY mw.id DESC LIMIT ?''',(limit,))
 def error_catalog(self):return self.db.rows("SELECT class_key error_type,COUNT(*) cases,ROUND(AVG(strength),3) avg_strength FROM evidence GROUP BY class_key ORDER BY cases DESC")
 def generate_challenger(self):
  cat={r['error_type']:r for r in self.error_catalog()};base=self.champion()['weights'];w=dict(base);reason=[];step=.03
  if cat.get('RETURN_MISS',{}).get('cases',0)>=10:w['gap']=min(.30,w['gap']+step);reason.append('RETURN_MISS evidencia')
  if cat.get('TRANSITION_MISS',{}).get('cases',0)>=10:w['transition']=min(.25,w['transition']+step);reason.append('TRANSITION_MISS evidencia')
  total=sum(w.values());w={k:v/total for k,v in w.items()};ver='challenger-'+datetime.now().strftime('%Y%m%d%H%M%S')
  self.db.execute("INSERT INTO model_configs VALUES(?, 'CHALLENGER', ?, datetime('now'), ?, ?)",(ver,json.dumps(w),self.champion()['version'],'; '.join(reason) or 'Nincs elegendő specifikus evidencia'))
  return {'version':ver,'weights':w,'reason':reason}
