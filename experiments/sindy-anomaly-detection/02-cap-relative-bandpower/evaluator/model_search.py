"""Training-only cached Gram algebra for the frozen ridge/sparsity grid.
Equivalent to our independently tested direct implementations; no external code.
"""
import numpy as np
from cap_methods import design
from residual_model import nonlinear_library

class TrainingCache:
 def __init__(self,lag,target):
  self.lag=np.asarray(lag,dtype=float);self.target=np.asarray(target,dtype=float);self.n=len(lag);self.cache={};self.backbones={}
  if self.n<1 or not np.isfinite(self.lag).all() or not np.isfinite(self.target).all():raise ValueError('Invalid fit data')
 def matrix(self,kind):
  if kind not in self.cache:
   phi=nonlinear_library(self.lag) if kind=='quadratic_only' else design(self.lag,kind)
   mean=phi.mean(axis=0);scale=phi.std(axis=0)
   if kind!='quadratic_only':mean[0]=0;scale[0]=1
   scale=np.maximum(scale,1e-8);x=(phi-mean)/scale
   self.cache[kind]={'mean':mean,'scale':scale,'x':x,'gram':x.T@x/self.n,'cross':x.T@self.target/self.n}
  return self.cache[kind]
 def solve(self,gram,cross,alpha,cutoff,intercept):
  penalty=np.eye(len(gram))*alpha
  if intercept:penalty[0,0]=0
  coef=np.linalg.solve(gram+penalty,cross)
  if cutoff is None:return coef
  for j in range(cross.shape[1]):
   active=np.ones(len(gram),dtype=bool)
   for _ in range(10):
    keep=active&(np.abs(coef[:,j])>=cutoff)
    if intercept:keep[0]=True
    if np.array_equal(keep,active):break
    active=keep;ids=np.flatnonzero(active);coef[:,j]=0
    if not len(ids):break
    p=np.eye(len(ids))*alpha
    if intercept:p[0,0]=0
    coef[ids,j]=np.linalg.solve(gram[np.ix_(ids,ids)]+p,cross[ids,j])
  return coef
 def regression(self,degree,alpha,cutoff=None):
  c=self.matrix(degree);coef=self.solve(c['gram'],c['cross'],alpha,cutoff,True)
  rms=np.maximum(np.sqrt(np.mean((self.target-c['x']@coef)**2,axis=0)),.001)
  return {'kind':'regression','degree':degree,'alpha':alpha,'cutoff':cutoff,'feature_mean':c['mean'],'feature_scale':c['scale'],'coefficients':coef,'residual_rms':rms,'retained_nonzero_terms':np.sum(np.abs(coef)>1e-12,axis=0)}
 def residual(self,linear_alpha,nonlinear_alpha=1.,cutoff=None):
  if linear_alpha not in self.backbones:
   base=self.regression(1,linear_alpha);prediction=self.matrix(1)['x']@base['coefficients'];q=self.matrix('quadratic_only')
   cross=q['x'].T@(self.target-prediction)/self.n
   self.backbones[linear_alpha]=(base,prediction,cross)
  base,prediction,cross=self.backbones[linear_alpha]
  model={'kind':'linear_plus_sparse_quadratic','backbone':base,'linear_alpha':linear_alpha,'nonlinear_alpha':nonlinear_alpha,'cutoff':cutoff,'null_correction':cutoff is None}
  if cutoff is None:model.update(nonlinear_nonzero_terms=0,residual_rms=base['residual_rms'].copy());return model
  q=self.matrix('quadratic_only');coef=self.solve(q['gram'],cross,nonlinear_alpha,cutoff,False)
  error=self.target-prediction-q['x']@coef;rms=np.maximum(np.sqrt(np.mean(error**2,axis=0)),.001)
  model.update(nonlinear_mean=q['mean'],nonlinear_scale=q['scale'],nonlinear_coefficients=coef,nonlinear_nonzero_terms=int(np.count_nonzero(np.abs(coef)>1e-12)),residual_rms=rms)
  return model

def nonlinear_terms(model):
 if model['kind']=='linear_plus_sparse_quadratic':return model['nonlinear_nonzero_terms']
 if model['kind']=='regression' and model['degree']==2:
  # degree-2 column count = 1+k+k(k+1)/2.
  k=next(k for k in range(1,1000) if 1+k+k*(k+1)//2==len(model['feature_mean']))
  return int(np.count_nonzero(np.abs(model['coefficients'][1+k:])>1e-12))
 return 0

def jsonable(value):
 if isinstance(value,np.ndarray):return value.tolist()
 if isinstance(value,np.generic):return value.item()
 if isinstance(value,dict):return {k:jsonable(v) for k,v in value.items()}
 if isinstance(value,(tuple,list)):return [jsonable(v) for v in value]
 return value
