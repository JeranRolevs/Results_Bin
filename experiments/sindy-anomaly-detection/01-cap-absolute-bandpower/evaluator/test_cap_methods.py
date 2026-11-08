"""Offline mathematical/format fixtures; never call a provider or fetch data."""
import unittest,json,tempfile
from pathlib import Path
import numpy as np
from scipy.signal import butter,sosfilt
import audit_cap as audit
import cap_methods as m

class CapChecks(unittest.TestCase):
 def test_midnight_and_epoch_clipping(self):
  h={'start_time':'23.59.58','record_count':10,'record_duration_seconds':1}
  text='S2\tP\t23:59:58\tSLEEP-S2\t10\tX\nS2\tP\t00:00:01\tMCAP-A1\t3\tX\nW\tP\t00:00:07\tSLEEP-S0\t30\tX'
  e=audit.annotations(text,h)
  self.assertEqual([x['onset'] for x in e],[0,3,9]);self.assertTrue(e[-1]['record_edge_clipped']);self.assertEqual(e[-1]['available_duration'],1)
 def test_tied_AP_and_AUC(self):
  y=[True,False,True,False]
  tied=m.ranking_metrics(y,[0,0,0,0]);self.assertAlmostEqual(tied['average_precision'],.5);self.assertAlmostEqual(tied['roc_auc'],.5)
  perfect=m.ranking_metrics(y,[1,0,1,0]);self.assertEqual(perfect['average_precision'],1.);self.assertEqual(perfect['roc_auc'],1.)
  self.assertAlmostEqual(m.ranking_metrics(y,[0,1,0,1])['roc_auc'],0)
 def test_no_credit_for_preexisting_alert(self):
  n=30;r={'valid':np.ones(n,dtype=bool),'target':np.zeros(n,dtype=bool),'events':[{'label':'MCAP-A1','onset':10,'duration':10,'record_edge_clipped':False}]}
  r['target'][10:20]=True;s=np.zeros(n);s[7:20]=2
  result=m.alarm_metrics(r,s,1)
  self.assertEqual(result['newly_detected_phase_a_events'],0);self.assertEqual(result['new_false_alerts'],1)
  s[:]=0;s[11:16]=2;result=m.alarm_metrics(r,s,1)
  self.assertEqual(result['newly_detected_phase_a_events'],1);self.assertEqual(result['median_delay_seconds_given_new_detection'],3)
 def test_sparse_regression(self):
  rng=np.random.default_rng(29);x=rng.normal(size=(500,3));y=np.c_[2*x[:,0],-.5*x[:,1]]
  model=m.train_regression(x,y,2,1e-6,.05)
  phi=(m.design(x,2)-model['feature_mean'])/model['feature_scale'];prediction=phi@model['coefficients']
  self.assertLess(np.mean((prediction-y)**2),1e-8)
  self.assertLessEqual(int(model['retained_nonzero_terms'].max()),2)
 def test_independent_EDF_demux_and_causal_chunk_features(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'raw').mkdir();duration=120;fs=64;ns=2;headerbytes=256+256*ns
   def field(s,n):return str(s).encode().ljust(n,b' ')[:n]
   fixed=b''.join([field('0',8),field('fixture',80),field('fixture',80),field('01.01.01',8),field('00.00.00',8),field(headerbytes,8),field('',44),field(duration,8),field(1,8),field(ns,4)])
   arrays=[(['C4-A1','other'],16),(['',''],80),(['uV','uV'],8),([-100,-100],8),([100,100],8),([-32768,-32768],8),([32767,32767],8),(['',''],80),([fs,8],8),(['',''],32)]
   header=fixed+b''.join(b''.join(field(v,w) for v in values) for values,w in arrays)
   parsed=audit.edf_header_bytes(header);self.assertEqual(parsed['channels'][1]['sample_offset'],fs)
   t=np.arange(duration*fs)/fs;physical=10*np.sin(2*np.pi*3*t)+2*np.sin(2*np.pi*10*t)
   dig=np.rint((physical+100)/200*65535-32768).astype('<i2')
   with (root/'raw/fixture.edf').open('wb') as f:
    f.write(header)
    for i in range(duration):f.write(dig[i*fs:(i+1)*fs].tobytes());f.write(np.full(8,123,dtype='<i2').tobytes())
   previous=m.ROOT;m.ROOT=root
   try:
    info=m.extract_features('fixture');features=np.load(root/'features/fixture.npz')['features']
   finally:m.ROOT=previous
   actual=dig.astype(float)*(200/65535)+(-100+200*32768/65535)
   energies=np.stack([np.mean(sosfilt(butter(2,b,btype='bandpass',fs=fs,output='sos'),actual).reshape(-1,fs)**2,axis=1) for b in m.BANDS],axis=1)
   expected=np.log(np.maximum((energies[1:]+energies[:-1])/2,1e-12))
   np.testing.assert_allclose(features[1:],expected,rtol=1e-10,atol=1e-10)
   self.assertTrue(info['causal'])

if __name__=='__main__':unittest.main(verbosity=2)
