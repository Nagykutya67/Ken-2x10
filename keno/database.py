import sqlite3, json
from pathlib import Path
from .model import DEFAULT_WEIGHTS
SCHEMA="""
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS draws(draw_date TEXT PRIMARY KEY,numbers_json TEXT NOT NULL,input_sha256 TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS model_configs(version TEXT PRIMARY KEY,status TEXT NOT NULL,weights_json TEXT NOT NULL,created_at TEXT NOT NULL,parent_version TEXT,reason TEXT);
CREATE TABLE IF NOT EXISTS forecasts(id INTEGER PRIMARY KEY AUTOINCREMENT,forecast_for TEXT UNIQUE NOT NULL,sealed_at TEXT NOT NULL,model_version TEXT NOT NULL,training_start TEXT NOT NULL,training_end TEXT NOT NULL,input_sha256 TEXT NOT NULL,seed INTEGER NOT NULL,frame_json TEXT NOT NULL,a_json TEXT NOT NULL,b_json TEXT NOT NULL,ranking_json TEXT NOT NULL,weights_json TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'SEALED');
CREATE TABLE IF NOT EXISTS evaluations(id INTEGER PRIMARY KEY AUTOINCREMENT,forecast_id INTEGER UNIQUE NOT NULL,actual_json TEXT NOT NULL,frame_hits INTEGER,a_hits INTEGER,b_hits INTEGER,best_row_hits INTEGER,precision20 REAL,evaluated_at TEXT NOT NULL,FOREIGN KEY(forecast_id) REFERENCES forecasts(id));
CREATE TABLE IF NOT EXISTS missed_winners(id INTEGER PRIMARY KEY AUTOINCREMENT,evaluation_id INTEGER NOT NULL,number_value INTEGER NOT NULL,original_rank INTEGER NOT NULL,threshold_gap REAL NOT NULL,score REAL NOT NULL,gap_value INTEGER,return_class TEXT,gap_class TEXT,supporters_json TEXT,opponents_json TEXT,transition_origin REAL,network_origin REAL,uncertainty REAL,displaced_number INTEGER,error_types_json TEXT,FOREIGN KEY(evaluation_id) REFERENCES evaluations(id));
CREATE TABLE IF NOT EXISTS selected_misses(id INTEGER PRIMARY KEY AUTOINCREMENT,evaluation_id INTEGER NOT NULL,number_value INTEGER NOT NULL,original_rank INTEGER NOT NULL,score REAL NOT NULL,supporters_json TEXT,opponents_json TEXT,counterfactual_number INTEGER,FOREIGN KEY(evaluation_id) REFERENCES evaluations(id));
CREATE TABLE IF NOT EXISTS evidence(id INTEGER PRIMARY KEY AUTOINCREMENT,evaluation_id INTEGER NOT NULL,evidence_type TEXT NOT NULL,class_key TEXT NOT NULL,support_count INTEGER NOT NULL,impact REAL NOT NULL,strength REAL NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(evaluation_id) REFERENCES evaluations(id));
CREATE TABLE IF NOT EXISTS promotion_runs(id INTEGER PRIMARY KEY AUTOINCREMENT,challenger_version TEXT,champion_version TEXT,sample_size INTEGER,uplift REAL,ci_low REAL,ci_high REAL,positive_periods INTEGER,seeds_positive INTEGER,lower_tail_delta REAL,ab_balance_delta REAL,decision TEXT,reasons_json TEXT,created_at TEXT);
CREATE TABLE IF NOT EXISTS rollback_log(id INTEGER PRIMARY KEY AUTOINCREMENT,from_version TEXT,to_version TEXT,reason TEXT,created_at TEXT);
"""
class Database:
 def __init__(self,path): self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True);self.init()
 def connect(self):
  c=sqlite3.connect(self.path);c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');return c
 def init(self):
  with self.connect() as c:
   c.executescript(SCHEMA);c.execute("INSERT OR IGNORE INTO model_configs VALUES('champion-1','CHAMPION',?,datetime('now'),NULL,'Stabil alapmodell')",(json.dumps(DEFAULT_WEIGHTS),))
 def execute(self,sql,args=()):
  with self.connect() as c:return c.execute(sql,args).lastrowid
 def rows(self,sql,args=()):
  with self.connect() as c:return [dict(x) for x in c.execute(sql,args).fetchall()]
