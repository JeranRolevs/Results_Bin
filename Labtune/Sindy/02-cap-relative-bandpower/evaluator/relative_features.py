"""Causal dimensionless log-relative bandpowers; no missing-unit assumptions."""
from pathlib import Path
import json
import numpy as np
from scipy.signal import butter,sosfilt
from audit_cap import ROOT,edf_header_bytes
from cap_methods import channel_for,BANDS

def relative_log_power(energies):
 e=np.asarray(energies,dtype=float)
 if e.ndim!=2 or e.shape[1]!=4:raise ValueError('Expected four band energies')
 total=e.sum(axis=1,keepdims=True)
 valid=np.isfinite(e).all(axis=1)&(e>=0).all(axis=1)&np.isfinite(total[:,0])&(total[:,0]>0)
 ratio=np.full_like(e,np.nan)
 np.divide(e,total,out=ratio,where=valid[:,None])
 return np.log(np.maximum(ratio,1e-10))

def extract_relative(record):
 p=ROOT/'raw'/f'{record}.edf'
 with p.open('rb') as f:
  fixed=f.read(256);f.seek(0);h=edf_header_bytes(f.read(int(fixed[184:192])),p.stat().st_size)
 if p.stat().st_size!=h['expected_file_bytes']:raise ValueError('EDF length mismatch')
 c=channel_for(h);fs=int(round(c['sampling_hz']));rd=h['record_duration_seconds']
 if fs!=c['sampling_hz'] or int(rd)!=rd or fs<=60:raise ValueError('Unsupported rate/record duration')
 numbers=[c[k] for k in ('physical_min','physical_max','digital_min','digital_max')]
 if not np.isfinite(numbers).all() or c['physical_max']==c['physical_min'] or c['digital_max']==c['digital_min']:raise ValueError('Nonfinite or degenerate numerical EDF calibration')
 gain=(c['physical_max']-c['physical_min'])/(c['digital_max']-c['digital_min']);offset=c['physical_min']-gain*c['digital_min']
 # Preserve the declared endpoint mapping, even when it yields negative gain.
 # n12 has reversed digital endpoints: flag this metadata irregularity, do not
 # silently swap the affine calibration. Squared band energies ignore polarity.
 digital_low,digital_high=sorted((c['digital_min'],c['digital_max']))
 # No unit conversion or guessed uV: constant channel gain cancels in the ratios.
 mm=np.memmap(p,dtype='<i2',mode='r',offset=h['header_bytes'],shape=(h['record_count'],h['samples_per_edf_record']))
 filters=[butter(2,b,btype='bandpass',fs=fs,output='sos') for b in BANDS];states=[np.zeros((len(s),2)) for s in filters]
 powers=[];clipping=[];step=max(1,int(60/rd))
 for start in range(0,h['record_count'],step):
  raw=np.asarray(mm[start:start+step,c['sample_offset']:c['sample_offset']+c['samples_per_record']]).reshape(-1)
  clipping.append(np.mean(((raw<=digital_low)|(raw>=digital_high)).reshape(-1,fs),axis=1))
  x=raw.astype(float)*gain+offset;bands=[]
  for i,sos in enumerate(filters):
   y,states[i]=sosfilt(sos,x,zi=states[i]);bands.append(np.mean((y*y).reshape(-1,fs),axis=1))
  powers.append(np.stack(bands,axis=1))
 del mm
 energy=np.concatenate(powers);features=np.full_like(energy,np.nan);features[1:]=relative_log_power((energy[1:]+energy[:-1])/2)
 out=ROOT/'relative-features';out.mkdir(mode=0o700,exist_ok=True)
 np.savez_compressed(out/f'{record}.npz',features=features,clipped_fraction=np.concatenate(clipping))
 meta={'record':record,'channel':c['label'],'sampling_hz':fs,'original_unit_label':c['unit'],'unit_assumed':False,'unit_conversion_applied':False,'representation':'log relative band energy; dimensionless floor 1e-10','seconds':len(features),'finite_feature_seconds':int(np.isfinite(features).all(axis=1).sum()),'clipped_sample_fraction':float(np.mean(np.concatenate(clipping))),'prefilter':c['prefilter'],'record_count_inferred':h['record_count_inferred'],'signed_calibration_gain':gain,'digital_endpoints_reversed':c['digital_max']<c['digital_min'],'calibration_endpoint_values_preserved':True,'causal':True}
 (out/f'{record}.json').write_text(json.dumps(meta,indent=2));return meta
