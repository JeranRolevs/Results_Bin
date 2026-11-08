"""Offline synthetic regression/metadata tests; no provider/data requests."""
import unittest
import numpy as np
from cap_methods import train_regression,design,channel_for
from residual_model import fit,predict,score
from audit_cap import edf_header_bytes

class ResidualChecks(unittest.TestCase):
 def setUp(self):
  rng=np.random.default_rng(17);self.x=rng.normal(size=(1000,3));self.y=np.c_[1.2*self.x[:,0]+.8*self.x[:,0]*self.x[:,1],-.5*self.x[:,2]+.4*self.x[:,1]**2]
 def test_null_is_exact_linear_backbone(self):
  m=fit(self.x,self.y,.1,.1,None);base=train_regression(self.x,self.y,1,.1)
  expected=((design(self.x,1)-base['feature_mean'])/base['feature_scale'])@base['coefficients']
  np.testing.assert_array_equal(predict(m,self.x),expected)
  np.testing.assert_array_equal(m['residual_rms'],base['residual_rms'])
  self.assertEqual(m['nonlinear_nonzero_terms'],0)
 def test_huge_cutoff_returns_linear(self):
  m=fit(self.x,self.y,.1,.1,1e6);null=fit(self.x,self.y,.1,.1,None)
  self.assertEqual(m['nonlinear_nonzero_terms'],0)
  np.testing.assert_allclose(predict(m,self.x),predict(null,self.x),rtol=0,atol=0)
 def test_recovers_a_synthetic_nonlinear_correction(self):
  baseline=fit(self.x,self.y,1e-6,1e-6,None);corrected=fit(self.x,self.y,1e-6,1e-6,.01)
  before=np.mean((self.y-predict(baseline,self.x))**2);after=np.mean((self.y-predict(corrected,self.x))**2)
  self.assertLess(after,before*.05);self.assertGreater(corrected['nonlinear_nonzero_terms'],0)
 def test_honors_regularization_argument_and_score_mask(self):
  low=fit(self.x,self.y,.1,.001,.01);high=fit(self.x,self.y,.1,10,.01)
  self.assertLess(np.linalg.norm(high['nonlinear_coefficients']),np.linalg.norm(low['nonlinear_coefficients']))
  valid=np.ones(len(self.x),dtype=bool);valid[:5]=False
  values=score(low,{'valid':valid,'state':self.y,'lags':self.x})
  self.assertTrue(np.isnan(values[:5]).all());self.assertTrue(np.isfinite(values[5:]).all())
 def test_alias_does_not_invent_units(self):
  c=channel_for({'channels':[{'label':'C4A1','unit':''}]})
  self.assertEqual(c['label'],'C4A1');self.assertEqual(c['unit'],'')
 def test_unknown_record_count_resolves_exactly(self):
  def field(s,n):return str(s).encode().ljust(n,b' ')[:n]
  fixed=b''.join([field('0',8),field('fixture',80),field('fixture',80),field('01.01.01',8),field('00.00.00',8),field(512,8),field('',44),field(-1,8),field(1,8),field(1,4)])
  vals=[('C4A1',16),('',80),('',8),(-100,8),(100,8),(-32768,8),(32767,8),('',80),(100,8),('',32)]
  header=fixed+b''.join(field(v,n) for v,n in vals)
  h=edf_header_bytes(header,512+5*200)
  self.assertEqual(h['record_count'],5);self.assertTrue(h['record_count_inferred']);self.assertEqual(h['channels'][0]['unit'],'')
  with self.assertRaises(ValueError):edf_header_bytes(header,512+5*200+1)

if __name__=='__main__':unittest.main(verbosity=2)
