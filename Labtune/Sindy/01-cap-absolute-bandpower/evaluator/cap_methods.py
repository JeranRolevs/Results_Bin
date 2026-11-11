"""Independent bounded CAP evaluator primitives, using declared NumPy/SciPy only.
No PySINDy, external benchmark implementation or upstream MATLAB is imported.
Discrete polynomial regression is not physical neural-equation identification.
"""
from pathlib import Path
import json
import numpy as np
from scipy.signal import butter,sosfilt
from scipy.stats import rankdata
from audit_cap import ROOT,edf_header_bytes
BANDS=[(0.5,4.0),(4.0,8.0),(8.0,12.0),(12.0,30.0)]
LAGS=(1,2,4,8)

def channel_for(header):
 for label in ('C4-A1','C3-A2'):
  found=[c for c in header['channels'] if c['label']==label]
  if found:return found[0]
 raise ValueError('Frozen central-mastoid channel unavailable')

def extract_features(record):
 p=ROOT/'raw'/f'{record}.edf'
 with p.open('rb') as f:
  fixed=f.read(256);f.seek(0);h=edf_header_bytes(f.read(int(fixed[184:192])))
 if p.stat().st_size!=h['expected_file_bytes']:raise ValueError('EDF size mismatch')
 c=channel_for(h);fs=int(round(c['sampling_hz']));rd=h['record_duration_seconds']
 if fs!=c['sampling_hz'] or int(rd)!=rd or fs<=60:raise ValueError('Unsupported rate/record duration')
 if c['unit'] not in ('uV','mV'):raise ValueError('Unsupported EDF unit')
 unit=1000.0 if c['unit']=='mV' else 1.0
 gain=(c['physical_max']-c['physical_min'])/(c['digital_max']-c['digital_min'])
 offset=c['physical_min']-gain*c['digital_min']
 mm=np.memmap(p,dtype='<i2',mode='r',offset=h['header_bytes'],shape=(h['record_count'],h['samples_per_edf_record']))
 filters=[butter(2,band,btype='bandpass',fs=fs,output='sos') for band in BANDS]
 zi=[np.zeros((len(s),2)) for s in filters]
 energies=[];clipped=[];step=max(1,int(60/rd))
 for start in range(0,h['record_count'],step):
  samples=np.asarray(mm[start:start+step,c['sample_offset']:c['sample_offset']+c['samples_per_record']]).reshape(-1)
  clipped.append(np.mean(((samples<=c['digital_min'])|(samples>=c['digital_max'])).reshape(-1,fs),axis=1))
  x=(samples.astype(np.float64)*gain+offset)*unit
  bands=[]
  for i,sos in enumerate(filters):
   y,zi[i]=sosfilt(sos,x,zi=zi[i]);bands.append(np.mean((y*y).reshape(-1,fs),axis=1))
  energies.append(np.stack(bands,axis=1))
 del mm
 energy=np.concatenate(energies);features=np.full_like(energy,np.nan)
 features[1:]=np.log(np.maximum((energy[1:]+energy[:-1])/2,1e-12))
 out=ROOT/'features';out.mkdir(exist_ok=True,mode=0o700)
 np.savez_compressed(out/f'{record}.npz',features=features,clipped_fraction=np.concatenate(clipped))
 meta={'record':record,'channel':c['label'],'sampling_hz':fs,'unit_conversion_to_uV':unit,'seconds':len(features),'clipped_sample_fraction':float(np.mean(np.concatenate(clipped))),'prefilter':c['prefilter'],'feature_bands_hz':BANDS,'feature_window_seconds':2,'causal':True}
 (out/f'{record}.json').write_text(json.dumps(meta,indent=2));return meta

def label_arrays(record,n):
 events=json.loads((ROOT/'metadata'/f'{record}.events.json').read_text())
 stage=np.full(n,-1,dtype=np.int8);cap=np.zeros(n,dtype=bool);blocked=np.zeros(n,dtype=bool)
 for e in events:
  a=max(0,int(np.ceil(e['onset']-.5)));b=min(n,int(np.ceil(e['onset']+e['duration']-.5)))
  if e['label'] in ('SLEEP-S0','SLEEP-S1','SLEEP-S2','SLEEP-S3','SLEEP-S4','SLEEP-REM'):
   stage[a:b]=5 if e['label']=='SLEEP-REM' else int(e['label'][-1])
  elif e['label'].startswith('MCAP-A'):
   cap[a:b]=True
   lo=max(0,int(np.ceil(e['onset']-15-.5)));hi=min(n,int(np.ceil(e['onset']+e['duration']+15-.5)))
   blocked[lo:hi]=True
 return stage,cap,blocked,events

def record_arrays(record,mean=None,scale=None):
 raw=np.load(ROOT/'features'/f'{record}.npz')['features']
 stage,cap,blocked,events=label_arrays(record,len(raw))
 z=raw if mean is None else (raw-mean)/scale
 n,k=z.shape;lag=np.zeros((n,k*len(LAGS)))
 valid=np.isfinite(z).all(axis=1);valid[:60]=False
 for i,d in enumerate(LAGS):
  lag[d:,i*k:(i+1)*k]=z[:-d];valid[:d]=False
  finite=np.zeros(n,dtype=bool);finite[d:]=np.isfinite(z[:-d]).all(axis=1);valid&=finite
 nrem=(stage>=1)&(stage<=4);valid&=nrem
 return {'record':record,'state':z,'lags':lag,'valid':valid,'normal':valid&~cap,'fit_normal':valid&~cap&~blocked,'target':cap,'events':events,'stage':stage}

def design(x,degree):
 n,k=x.shape;parts=[np.ones((n,1)),x]
 if degree==2:parts.extend((x[:,i]*x[:,j])[:,None] for i in range(k) for j in range(i,k))
 return np.concatenate(parts,axis=1)

def ridge(x,y,alpha):
 gram=x.T@x/len(x);cross=x.T@y/len(x)
 penalty=np.eye(x.shape[1])*alpha;penalty[0,0]=0
 return np.linalg.solve(gram+penalty,cross)

def train_regression(lag,y,degree,alpha,cutoff=None):
 phi=design(lag,degree);pm=phi.mean(axis=0);ps=phi.std(axis=0)
 pm[0]=0;ps[0]=1;ps=np.maximum(ps,1e-8);x=(phi-pm)/ps
 coeff=ridge(x,y,alpha)
 if cutoff is not None:
  gram=x.T@x/len(x);cross=x.T@y/len(x)
  for j in range(y.shape[1]):
   active=np.ones(x.shape[1],dtype=bool)
   for _ in range(10):
    keep=active&(np.abs(coeff[:,j])>=cutoff);keep[0]=True
    if np.array_equal(keep,active):break
    active=keep;ids=np.flatnonzero(active);g=gram[np.ix_(ids,ids)].copy()
    penalty=np.eye(len(ids))*alpha;penalty[0,0]=0
    w=np.linalg.solve(g+penalty,cross[ids,j]);coeff[:,j]=0;coeff[ids,j]=w
 residual=y-x@coeff;rms=np.maximum(np.sqrt(np.mean(residual**2,axis=0)),.001)
 return {'kind':'regression','degree':degree,'alpha':alpha,'cutoff':cutoff,'feature_mean':pm,'feature_scale':ps,'coefficients':coeff,'residual_rms':rms,'retained_nonzero_terms':np.sum(np.abs(coeff)>1e-12,axis=0)}

def train_auxiliary(state,all_features,labels):
 cov=np.cov(state,rowvar=False);cov=.9*cov+.1*np.diag(np.diag(cov))+np.eye(state.shape[1])*1e-6
 static={'kind':'static','mean':state.mean(axis=0),'precision':np.linalg.inv(cov)}
 a=all_features[labels];b=all_features[~labels]
 if len(a)<20 or len(b)<20:raise ValueError('Insufficient supervised-reference labels')
 ac=a-a.mean(axis=0);bc=b-b.mean(axis=0)
 pooled=(ac.T@ac+bc.T@bc)/(len(a)+len(b)-2)
 pooled=.9*pooled+.1*np.diag(np.diag(pooled))+np.eye(len(pooled))*1e-6
 lda={'kind':'lda','weights':np.linalg.solve(pooled,a.mean(axis=0)-b.mean(axis=0))}
 return static,lda

def score(model,record):
 state=record['state'];lag=record['lags'];valid=record['valid'];out=np.full(len(state),np.nan)
 x=lag[valid];y=state[valid]
 if model['kind']=='regression':
  d=(design(x,model['degree'])-model['feature_mean'])/model['feature_scale'];res=y-d@model['coefficients']
  values=np.mean((res/model['residual_rms'])**2,axis=1)
 elif model['kind']=='persistence':values=np.mean(((y-x[:,:state.shape[1]])/model['residual_rms'])**2,axis=1)
 elif model['kind']=='static':
  z=y-model['mean'];values=np.einsum('ij,jk,ik->i',z,model['precision'],z)
 elif model['kind']=='lda':values=np.concatenate([y,x],axis=1)@model['weights']
 else:raise ValueError('Unknown model')
 if not np.isfinite(values).all():raise ValueError('Non-finite model score; do not exclude failing samples')
 out[valid]=values;return out

def ranking_metrics(y,s):
 y=np.asarray(y,dtype=bool);s=np.asarray(s,dtype=float)
 if not len(y) or not y.any() or y.all():return {'average_precision':None,'roc_auc':None,'prevalence':float(y.mean()) if len(y) else None}
 order=np.argsort(-s,kind='stable');yy=y[order];ss=s[order];ends=np.r_[np.flatnonzero(ss[:-1]!=ss[1:]),len(ss)-1]
 tp=np.cumsum(yy)[ends];precision=tp/(ends+1);recall=tp/y.sum();ap=np.sum(np.diff(np.r_[0,recall])*precision)
 ranks=rankdata(s,method='average');p=int(y.sum());q=len(y)-p;auc=(ranks[y].sum()-p*(p+1)/2)/(p*q)
 return {'average_precision':float(ap),'roc_auc':float(auc),'prevalence':float(y.mean())}

def alarm_metrics(record,scores,threshold):
 v=record['valid'];target=record['target'];n=len(v)
 raw=v&(scores>threshold);alarm=raw&np.r_[False,raw[:-1]]
 edges=alarm&~np.r_[False,alarm[:-1]]
 tp=int(np.sum(alarm&v&target));fp=int(np.sum(alarm&v&~target));fn=int(np.sum(~alarm&v&target))
 normal=int(np.sum(v&~target));positives=int(np.sum(v&target))
 detected=0;delays=[];eligible=0
 for e in record['events']:
  if not e['label'].startswith('MCAP-A') or e.get('record_edge_clipped'):continue
  start=e['onset'];end=start+e['duration'];ix=int(np.ceil(start-.5))
  if ix<0 or ix>=n or not v[ix]:continue
  eligible+=1
  candidates=np.flatnonzero(edges[max(0,int(np.ceil(start-.5))):min(n,int(np.ceil(end-.5)))])+max(0,int(np.ceil(start-.5)))
  candidates=candidates[(candidates+1>=start)&(candidates+1<end)]
  if len(candidates):detected+=1;delays.append(float(candidates[0]+1-start))
 result=ranking_metrics(target[v],scores[v])
 result.update(scored_seconds=int(v.sum()),normal_seconds=normal,phase_a_seconds=positives,
  precision=tp/(tp+fp) if tp+fp else 0.,recall=tp/(tp+fn) if tp+fn else 0.,f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.,
  normal_false_positive_time_fraction=fp/normal if normal else None,new_false_alerts=int(np.sum(edges&v&~target)),new_false_alerts_per_normal_hour=float(np.sum(edges&v&~target)*3600/normal) if normal else None,
  eligible_phase_a_events=eligible,newly_detected_phase_a_events=detected,new_event_recall=detected/eligible if eligible else None,median_delay_seconds_given_new_detection=float(np.median(delays)) if delays else None)
 return result

def json_model(m):
 return {k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in m.items()}
