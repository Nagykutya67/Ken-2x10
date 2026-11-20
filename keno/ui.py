import tkinter as tk,json,statistics,threading,sys,os
from tkinter import ttk,messagebox,filedialog
from pathlib import Path
from .service import Service
from .data import load_draws
from .backtest import run,gate
DISCLAIMER='A program historikus adatok statisztikai elemzését és modellek visszatesztelését végzi. A sorsolás véletlenszerű, ezért a találat vagy nyeremény nem garantálható.'
class App(tk.Tk):
 def __init__(self,root):
  super().__init__();self.rootp=Path(root);self.s=Service(root);self.title('Kenó 2x10 Analytics v2.1.0');self.geometry('1440x900');self.minsize(1100,720)
  st=ttk.Style(self);st.theme_use('clam');st.configure('Title.TLabel',font=('Segoe UI',22,'bold'),foreground='#17365D');st.configure('KPI.TLabel',font=('Segoe UI',15,'bold'),foreground='#2F5597');st.configure('Treeview',rowheight=25)
  h=ttk.Frame(self,padding=12);h.pack(fill='x');ttk.Label(h,text='KENÓ 2x10 ANALYTICS',style='Title.TLabel').pack(side='left');self.status=ttk.Label(h,text='v2.1.0 | Champion');self.status.pack(side='right')
  self.nb=ttk.Notebook(self);self.nb.pack(fill='both',expand=True,padx=12)
  self.tabs={};
  for key,title in [('forecast','Előrejelzés'),('eval','Értékelés'),('miss','Kimaradt nyertesek'),('catalog','Hibakatalógus'),('gov','Governance'),('bt','Walk-forward')]:
   self.tabs[key]=ttk.Frame(self.nb,padding=12);self.nb.add(self.tabs[key],text=title)
  self.build_forecast();self.build_eval();self.build_miss();self.build_catalog();self.build_gov();self.build_bt();ttk.Label(self,text=DISCLAIMER,wraplength=1350,foreground='#555',padding=8).pack(fill='x');self.after(100,self.refresh_all)
 def tree(self,parent,cols,height=18):
  t=ttk.Treeview(parent,columns=[x[0] for x in cols],show='headings',height=height)
  for k,n,w in cols:t.heading(k,text=n);t.column(k,width=w,anchor='center')
  t.pack(fill='both',expand=True,pady=8);return t
 def build_forecast(self):
  f=self.tabs['forecast'];ttk.Button(f,text='Lezárt előrejelzés készítése',command=self.make_forecast).pack(anchor='w');self.fm=ttk.Label(f,text='');self.fm.pack(anchor='w',pady=8)
  row=ttk.Frame(f);row.pack(fill='x');self.fa=ttk.LabelFrame(row,text='A sor');self.fa.pack(side='left',fill='x',expand=True,padx=5);self.fb=ttk.LabelFrame(row,text='B sor');self.fb.pack(side='left',fill='x',expand=True,padx=5)
  self.la=ttk.Label(self.fa,font=('Consolas',16,'bold'),padding=20);self.la.pack();self.lb=ttk.Label(self.fb,font=('Consolas',16,'bold'),padding=20);self.lb.pack();self.ft=self.tree(f,[('rank','#',45),('n','Szám',60),('score','Pont',85),('gap','Gap',60),('ret','Return osztály',110),('pos','Támogatja',220),('neg','Ellene',220),('unc','Bizonytalanság',110)],16)
 def build_eval(self):
  f=self.tabs['eval'];ttk.Button(f,text='Új húzások automatikus értékelése',command=self.evaluate).pack(anchor='w');self.em=ttk.Label(f,text='');self.em.pack(anchor='w',pady=8);self.et=self.tree(f,[('date','Dátum',110),('frame','Keret',70),('a','A',60),('b','B',60),('best','Legjobb sor',100),('model','Modell',140)],22)
 def build_miss(self):
  self.mt=self.tree(self.tabs['miss'],[('date','Dátum',100),('n','Szám',55),('rank','Eredeti rang',90),('gap','Küszöbrés',90),('ret','Return',90),('types','Hibatípusok',260),('disp','Kiszorító szám',100),('sup','Támogatók',180),('opp','Ellenzők',180)],24)
 def build_catalog(self):self.ct=self.tree(self.tabs['catalog'],[('type','Hibatípus',300),('cases','Esetszám',100),('strength','Átlagos evidencia',140)],25)
 def build_gov(self):
  f=self.tabs['gov'];ttk.Button(f,text='Evidence-alapú challenger létrehozása',command=self.challenger).pack(anchor='w');self.gm=ttk.Label(f,text='');self.gm.pack(anchor='w',pady=8);self.gt=self.tree(f,[('version','Verzió',210),('status','Státusz',120),('parent','Szülő',150),('reason','Indok',500),('created','Létrehozva',180)],18)
 def build_bt(self):
  f=self.tabs['bt'];ttk.Button(f,text='1000 húzásos promotion gate futtatása',command=self.run_bt).pack(anchor='w');self.bm=ttk.Label(f,text='');self.bm.pack(anchor='w',pady=8);self.bt=self.tree(f,[('metric','Kapumulató',300),('value','Érték',350)],15)
 def make_forecast(self):
  try:self.s.create_forecast();self.refresh_all()
  except Exception as e:messagebox.showerror('Hiba',str(e))
 def evaluate(self):
  try:n=len(self.s.evaluate_pending());self.em.config(text=f'{n} új lezárt előrejelzés értékelve.');self.refresh_all()
  except Exception as e:messagebox.showerror('Hiba',str(e))
 def challenger(self):
  r=self.s.generate_challenger();self.gm.config(text=f"Létrejött: {r['version']} | {', '.join(r['reason']) or 'nincs elég evidencia, stabil súlyok'}");self.refresh_all()
 def run_bt(self):
  mods=self.s.db.rows("SELECT * FROM model_configs WHERE status='CHALLENGER' ORDER BY created_at DESC LIMIT 1")
  if not mods:return messagebox.showinfo('Nincs challenger','Előbb hozz létre challengert.')
  self.bm.config(text='Teszt fut...');self.update_idletasks()
  try:
   import json;draws=load_draws(self.s.data);ch=self.s.champion();qw=json.loads(mods[0]['weights_json']);rows=run(draws,ch['weights'],qw,1000);g=gate(rows)
   self.s.db.execute('''INSERT INTO promotion_runs(challenger_version,champion_version,sample_size,uplift,ci_low,ci_high,positive_periods,seeds_positive,lower_tail_delta,ab_balance_delta,decision,reasons_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))''',(mods[0]['version'],ch['version'],g['n'],g['uplift'],g['ci_low'],g['ci_high'],g['positive_periods'],0,g['lower_tail_delta'],g['ab_balance_delta'],g['decision'],json.dumps(g['reasons'])))
   self.bm.config(text=f"Döntés: {g['decision']}");
   for x in self.bt.get_children():self.bt.delete(x)
   for k,v in g.items():self.bt.insert('', 'end',values=(k,json.dumps(v,ensure_ascii=False) if isinstance(v,list) else v))
  except Exception as e:messagebox.showerror('Hiba',str(e))
 def refresh_all(self):
  try:
   p=self.s.create_forecast();self.fm.config(text=f"Célhúzás: {p['forecast_for']} | Modell: {p['model_version']} | Lezárva: {p['sealed_at']} | SHA-256: {p['input_sha256'][:16]}...");self.la.config(text='  '.join(f'{n:02d}' for n in p['a']));self.lb.config(text='  '.join(f'{n:02d}' for n in p['b']))
   for x in self.ft.get_children():self.ft.delete(x)
   for i,r in enumerate(p['ranking'][:35],1):self.ft.insert('', 'end',values=(i,r['number'],f"{r['score']:.4f}",r['gap'],r['return_class'],', '.join(r['positive']),', '.join(r['negative']),f"{r['uncertainty']:.3f}"))
   for x in self.et.get_children():self.et.delete(x)
   for r in self.s.db.rows('''SELECT f.forecast_for,e.frame_hits,e.a_hits,e.b_hits,e.best_row_hits,f.model_version FROM evaluations e JOIN forecasts f ON f.id=e.forecast_id ORDER BY e.id DESC LIMIT 100'''):self.et.insert('', 'end',values=tuple(r.values()))
   for x in self.mt.get_children():self.mt.delete(x)
   for r in self.s.latest_misses():self.mt.insert('', 'end',values=(r['forecast_for'],r['number_value'],r['original_rank'],f"{r['threshold_gap']:.4f}",r['return_class'],', '.join(json.loads(r['error_types_json'])),r['displaced_number'],', '.join(json.loads(r['supporters_json'])),', '.join(json.loads(r['opponents_json']))))
   for x in self.ct.get_children():self.ct.delete(x)
   for r in self.s.error_catalog():self.ct.insert('', 'end',values=(r['error_type'],r['cases'],r['avg_strength']))
   for x in self.gt.get_children():self.gt.delete(x)
   for r in self.s.db.rows('SELECT version,status,parent_version,reason,created_at FROM model_configs ORDER BY created_at DESC'):self.gt.insert('', 'end',values=tuple(r.values()))
  except Exception as e:messagebox.showerror('Indítási hiba',str(e))
def main():
 root=Path(__file__).resolve().parents[1];App(root).mainloop()
