import unittest,tempfile,shutil,json
from pathlib import Path
from keno.data import load_draws
from keno.model import forecast
from keno.service import Service
from keno.backtest import bootstrap,gate
ROOT=Path(__file__).parents[1]
class Core(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.draws=load_draws(ROOT/'data/draws.csv')
 def test_data(self):self.assertEqual(len(self.draws),9475)
 def test_forecast_invariants(self):
  p=forecast(self.draws);self.assertEqual(len(p['frame']),20);self.assertEqual(len(set(p['frame'])),20);self.assertEqual(len(p['A']),10);self.assertEqual(len(p['B']),10);self.assertFalse(set(p['A'])&set(p['B']));self.assertEqual(set(p['frame']),set(p['A'])|set(p['B']))
 def test_deterministic(self):self.assertEqual(forecast(self.draws),forecast(self.draws))
 def test_chronology(self):
  p1=forecast(self.draws[:-1]);p2=forecast(self.draws[:-1]);self.assertEqual(p1,p2)
 def test_bootstrap(self):self.assertEqual(bootstrap([0]*100,100),(0.0,0.0))
 def test_gate_rejects_no_signal(self):
  rows=[(str(i),(5,3,2),(5,3,2)) for i in range(1000)];self.assertEqual(gate(rows)['decision'],'REJECT')
 def test_database_and_freeze(self):
  with tempfile.TemporaryDirectory() as td:
   r=Path(td);(r/'data').mkdir();shutil.copy(ROOT/'data/draws.csv',r/'data/draws.csv');s=Service(r);p=s.create_forecast();self.assertEqual(len(p['ranking']),80);self.assertTrue((r/'data/keno_v21.sqlite').exists())
if __name__=='__main__':unittest.main()
