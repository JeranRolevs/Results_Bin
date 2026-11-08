"""Offline scale/causality/cache equivalence fixtures; no provider or data requests."""
import tempfile,unittest
from pathlib import Path
import numpy as np
from cap_methods import train_regression
from residual_model import fit,predict
from model_search import TrainingCache,jsonable
import relative_features as rel

class RelativeChecks(unittest.TestCase):
 def test_ratios_are_gain_invariant(self):
  p=np.array([[1.,2.,3.,4.],[1e-5,7.,3.,2.]])
  reference=rel.relative_log_power(p)
  for factor in [1e-12,1e-6,1e6,1e12]:np.testing.assert_allclose(rel.relative_log_power(p*factor),reference,atol=1e-13)
  np.testing.assert_allclose(np.exp(reference).sum(axis=1),1.)
 def test_invalid_energy_is_not_fabricated(self):
  p=np.array([[0,0,0,0],[np.nan,1,2,3],[-1,2,3,4]])
  self.assertTrue(np.isnan(rel.relative_log_power(p)).all())
 def test_cached_regression_matches_direct(self):
  rng=np.random.default_rng(41);x=rng.normal(size=(600,4));y=rng.normal(size=(600,2))
  cache=TrainingCache(x,y)
  for degree in [1,2]:
   for cutoff in [None,.05]:
    a=cache.regression(degree,.1,cutoff);b=train_regression(x,y,degree,.1,cutoff)
    np.testing.assert_allclose(a['coefficients'],b['coefficients'],rtol=1e-10,atol=1e-12)
    np.testing.assert_allclose(a['residual_rms'],b['residual_rms'],rtol=1e-12)
 def test_cached_residual_matches_direct(self):
  rng=np.random.default_rng(43);x=rng.normal(size=(700,3));y=np.c_[x[:,0]+x[:,1]*x[:,2],-.2*x[:,2]+x[:,0]**2]
  cache=TrainingCache(x,y)
  for cutoff in [None,.01,.1,1e6]:
   a=cache.residual(.1,.1,cutoff);b=fit(x,y,.1,.1,cutoff)
   np.testing.assert_allclose(predict(a,x),predict(b,x),rtol=1e-10,atol=1e-12)
  self.assertIsInstance(jsonable(a)['backbone']['coefficients'],list)
 def test_EDF_unknown_units_scale_invariance_and_future_causality(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);(root/'raw').mkdir();fs=64;n=120
   t=np.arange(fs*n)/fs;wave=10*np.sin(2*np.pi*3*t)+3*np.sin(2*np.pi*11*t)
   digital=np.rint((wave+100)/200*65535-32768).astype('<i2')
   def write(name,gain,values,inverted=False):
    def field(s,n):return str(s).encode().ljust(n,b' ')[:n]
    fixed=b''.join([field('0',8),field('fixture',80),field('fixture',80),field('01.01.01',8),field('00.00.00',8),field(512,8),field('',44),field(-1,8),field(1,8),field(1,4)])
    spec=[('C4A1',16),('',80),('',8),(-100*gain,8),(100*gain,8),(32767 if inverted else -32768,8),(-32768 if inverted else 32767,8),('',80),(fs,8),('',32)]
    (root/'raw'/f'{name}.edf').write_bytes(fixed+b''.join(field(v,w) for v,w in spec)+values.tobytes())
   write('base',1,digital);write('scaled',1000,digital);write('inverted',1,digital,True)
   changed=digital.copy();changed[80*fs:]=0;write('future',1,changed)
   old=rel.ROOT;rel.ROOT=root
   try:
    a=rel.extract_relative('base');b=rel.extract_relative('scaled');inv=rel.extract_relative('inverted');rel.extract_relative('future')
   finally:rel.ROOT=old
   def features(r):return np.load(root/'relative-features'/f'{r}.npz')['features']
   np.testing.assert_allclose(features('base')[1:],features('scaled')[1:],atol=1e-9,rtol=1e-10)
   np.testing.assert_allclose(features('base')[1:],features('inverted')[1:],atol=0,rtol=0)
   self.assertLess(inv['signed_calibration_gain'],0);self.assertTrue(inv['digital_endpoints_reversed'])
   with np.load(root/'relative-features/inverted.npz') as z:np.testing.assert_array_equal(z['clipped_fraction'],np.zeros(n))
   np.testing.assert_allclose(features('base')[1:80],features('future')[1:80],atol=0,rtol=0)
   self.assertEqual(a['original_unit_label'],'');self.assertFalse(a['unit_assumed']);self.assertTrue(b['record_count_inferred'])

if __name__=='__main__':unittest.main(verbosity=2)
