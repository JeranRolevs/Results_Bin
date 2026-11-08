"""Independent linear-backbone + sparse quadratic residual prototype.
Uses our own existing ridge primitives and declared NumPy only. No EEG model fit
is authorized by importing this module. Null correction exactly recovers VAR.
"""
import numpy as np
from cap_methods import train_regression,design

def nonlinear_library(lag):
 lag=np.asarray(lag,dtype=float)
 if lag.ndim!=2:raise ValueError('Expected a 2-D lag matrix')
 return np.stack([lag[:,i]*lag[:,j] for i in range(lag.shape[1]) for j in range(i,lag.shape[1])],axis=1)

def predict_backbone(model,lag):
 base=model['backbone'];phi=design(lag,1)
 return ((phi-base['feature_mean'])/base['feature_scale'])@base['coefficients']

def predict(model,lag):
 baseline=predict_backbone(model,lag)
 if model['null_correction']:return baseline
 q=(nonlinear_library(lag)-model['nonlinear_mean'])/model['nonlinear_scale']
 return baseline+q@model['nonlinear_coefficients']

def fit(lag,y,linear_alpha=1.0,nonlinear_alpha=1.0,cutoff=None,max_iterations=10):
 lag=np.asarray(lag,dtype=float);y=np.asarray(y,dtype=float)
 if lag.ndim!=2 or y.ndim!=2 or len(lag)!=len(y) or not len(lag):raise ValueError('Invalid regression shapes')
 if not np.isfinite(lag).all() or not np.isfinite(y).all():raise ValueError('Non-finite fit input')
 if linear_alpha<=0 or nonlinear_alpha<=0 or max_iterations<1:raise ValueError('Positive regularization/iterations required')
 if cutoff is not None and (not np.isfinite(cutoff) or cutoff<0):raise ValueError('Invalid sparsity cutoff')
 base=train_regression(lag,y,1,linear_alpha)
 model={'kind':'linear_plus_sparse_quadratic','backbone':base,'linear_alpha':linear_alpha,'nonlinear_alpha':nonlinear_alpha,'cutoff':cutoff,'null_correction':cutoff is None}
 baseline=predict_backbone(model,lag)
 if cutoff is None:
  model.update(nonlinear_nonzero_terms=0,residual_rms=base['residual_rms'].copy());return model
 phi=nonlinear_library(lag);mean=phi.mean(axis=0);scale=np.maximum(phi.std(axis=0),1e-8);x=(phi-mean)/scale
 residual=y-baseline;gram=x.T@x/len(x);cross=x.T@residual/len(x)
 coeff=np.linalg.solve(gram+nonlinear_alpha*np.eye(len(gram)),cross)
 for output in range(y.shape[1]):
  active=np.ones(x.shape[1],dtype=bool)
  for _ in range(max_iterations):
   keep=active&(np.abs(coeff[:,output])>=cutoff)
   if np.array_equal(keep,active):break
   active=keep;coeff[:,output]=0
   ids=np.flatnonzero(active)
   if not len(ids):break
   weights=np.linalg.solve(gram[np.ix_(ids,ids)]+nonlinear_alpha*np.eye(len(ids)),cross[ids,output])
   coeff[ids,output]=weights
 model.update(nonlinear_mean=mean,nonlinear_scale=scale,nonlinear_coefficients=coeff,nonlinear_nonzero_terms=int(np.count_nonzero(np.abs(coeff)>1e-12)))
 final_residual=y-predict(model,lag);model['residual_rms']=np.maximum(np.sqrt(np.mean(final_residual**2,axis=0)),.001)
 return model

def score(model,record):
 valid=record['valid'];out=np.full(len(valid),np.nan)
 residual=record['state'][valid]-predict(model,record['lags'][valid])
 values=np.mean((residual/model['residual_rms'])**2,axis=1)
 if not np.isfinite(values).all():raise ValueError('Non-finite prediction score')
 out[valid]=values;return out
