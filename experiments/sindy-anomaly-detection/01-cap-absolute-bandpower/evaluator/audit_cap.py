"""Independent CAP metadata audit. Reads public data, never upstream implementation.
EDF fixed/variable ASCII header parsing and REMlogic TSV annotation parsing are
implemented here from their file structure. No external research code is imported.
"""
from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import json,re,urllib.request,os
ROOT=Path(__file__).resolve().parent
BASE='https://physionet.org/files/capslpdb/1.0.0/'
RECORDS=[f'n{i}' for i in range(1,9)]

def fetch_small(name,limit=2000000):
 p=ROOT/'metadata'/name;p.parent.mkdir(exist_ok=True,mode=0o700)
 if p.exists():return p.read_bytes()
 with urllib.request.urlopen(BASE+name,timeout=60) as r:
  b=r.read(limit+1)
 if len(b)>limit:raise ValueError('Metadata exceeds declared bound')
 p.write_bytes(b);p.chmod(0o600);return b

def edf_header_bytes(b):
 if len(b)<256:raise ValueError('Short EDF fixed header')
 ns=int(b[252:256]);header_len=int(b[184:192])
 if ns<1 or ns>128 or header_len!=256+256*ns:raise ValueError('Unsupported EDF header layout')
 if len(b)<header_len:raise ValueError('Short variable header')
 offset=256;fields={}
 for name,width in [('label',16),('transducer',80),('unit',8),('physical_min',8),('physical_max',8),('digital_min',8),('digital_max',8),('prefilter',80),('samples_per_record',8),('reserved',32)]:
  fields[name]=[b[offset+i*width:offset+(i+1)*width].decode('ascii',errors='replace').strip() for i in range(ns)]
  offset+=ns*width
 channels=[];sample_offset=0
 for i in range(ns):
  c={k:fields[k][i] for k in ('label','unit','prefilter')}
  c.update(index=i,physical_min=float(fields['physical_min'][i]),physical_max=float(fields['physical_max'][i]),digital_min=int(fields['digital_min'][i]),digital_max=int(fields['digital_max'][i]),samples_per_record=int(fields['samples_per_record'][i]),sample_offset=sample_offset)
  c['sampling_hz']=c['samples_per_record']/float(b[244:252]);sample_offset+=c['samples_per_record'];channels.append(c)
 return {'header_bytes':header_len,'record_count':int(b[236:244]),'record_duration_seconds':float(b[244:252]),'start_date':b[168:176].decode().strip(),'start_time':b[176:184].decode().strip(),'channels':channels,'samples_per_edf_record':sample_offset,'expected_file_bytes':header_len+2*int(b[236:244])*sample_offset}

def get_header(name):
 cache=ROOT/'metadata'/f'{name}.header.bin'
 if cache.exists():return edf_header_bytes(cache.read_bytes())
 req=urllib.request.Request(BASE+name+'.edf',headers={'Range':'bytes=0-255'})
 with urllib.request.urlopen(req,timeout=60) as r:fixed=r.read(256)
 size=int(fixed[184:192])
 if size>40000:raise ValueError('Unexpected EDF header size')
 req=urllib.request.Request(BASE+name+'.edf',headers={'Range':f'bytes=0-{size-1}'})
 with urllib.request.urlopen(req,timeout=60) as r:b=r.read(size)
 cache.write_bytes(b);cache.chmod(0o600);return edf_header_bytes(b)

def seconds(clock):
 h,m,s=[int(x) for x in clock.replace('.',':').split(':')];return h*3600+m*60+s

def annotations(text,header):
 start=seconds(header['start_time']);duration=header['record_count']*header['record_duration_seconds']
 events=[];prev=None;day=0
 for line in text.splitlines():
  parts=line.split('\t')
  ti=next((i for i,s in enumerate(parts) if re.fullmatch(r'\d{1,2}:\d{2}:\d{2}',s.strip())),None)
  if ti is None:continue
  if ti+2>=len(parts):raise ValueError('Incomplete annotation event row')
  clock=seconds(parts[ti].strip())
  if prev is not None and clock<prev-43200:day+=86400
  if prev is None and clock<start:day=86400
  onset=day+clock-start;prev=clock
  label=parts[ti+1].strip();length=float(parts[ti+2].strip())
  if length<=0 or onset<0 or onset+length>duration+60:raise ValueError('Annotation alignment exceeds one-epoch edge tolerance: '+str((onset,length,duration,label)))
  if label.startswith('SLEEP-') or label.startswith('MCAP-A'):
   events.append({'onset':onset,'duration':length,'label':label,'stage_text':parts[0].strip(),'location':parts[ti+3].strip() if len(parts)>ti+3 else '', 'record_edge_clipped':onset+length>duration,'available_duration':max(0,min(length,duration-onset))})
 if not events:raise ValueError('No annotations parsed')
 return events

def audit_record(record):
 h=get_header(record);raw=fetch_small(record+'.txt');ev=annotations(raw.decode('utf-8-sig',errors='replace'),h)
 cap=[e for e in ev if e['label'].startswith('MCAP-A')]
 stage=[e for e in ev if e['label'].startswith('SLEEP-')]
 rows={'record':record,'header':h,'annotations_sha256':sha256(raw).hexdigest(),'duration_hours':h['record_count']*h['record_duration_seconds']/3600,'cap_event_count':len(cap),'cap_subtypes':dict(Counter(e['label'] for e in cap)),'stage_counts':dict(Counter(e['label'] for e in stage)),'first_annotation_seconds':min(e['onset'] for e in ev),'last_annotation_seconds':max(e['onset']+e['duration'] for e in ev),'edge_clipped_events':sum(e['record_edge_clipped'] for e in ev),'metadata_only':True}
 (ROOT/'metadata'/f'{record}.events.json').write_text(json.dumps(ev,indent=2));return rows

if __name__=='__main__':
 fetch_small('RECORDS');fetch_small('SHA256SUMS.txt')
 with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(audit_record,RECORDS))
 common=set(c['label'] for c in rows[0]['header']['channels'])
 for row in rows:common&={c['label'] for c in row['header']['channels']}
 result={'audited_at':datetime.now(timezone.utc).isoformat(),'source':BASE,'records_selected_before_outcomes':RECORDS,'record_selection':'First eight numerically ordered healthy-control IDs, not selected for model success or small file size. Metadata feasibility only.','rows':rows,'common_exact_channel_labels':sorted(common),'total_expected_edf_bytes':sum(r['header']['expected_file_bytes'] for r in rows),'data_license':'Open Data Commons Attribution License v1.0, as stated by the official PhysioNet page. Preserve attribution and source terms.','upstream_implementation_used':False}
 (ROOT/'metadata-audit.json').write_text(json.dumps(result,indent=2))
 for r in rows:print(r['record'],round(r['duration_hours'],2),'h',r['cap_event_count'],'A events',[(c['label'],c['sampling_hz']) for c in r['header']['channels'] if c['label'] in common])
 print('Common channels:',sorted(common));print('Total EDF bytes:',result['total_expected_edf_bytes'])
