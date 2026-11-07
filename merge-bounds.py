#!/usr/bin/env python3
"""Merge sound WDL bounds, reject contradictions, and retain converged exact values."""
import json
from pathlib import Path
base=Path(__file__).resolve().parent
files=sorted(set((base/'runs').glob('opening-*/data/table-9x9.csv'))|set((base/'continuation').glob('*/data/table-9x9.csv')))
by={};records=0
for path in files:
 for line in path.read_text().splitlines():
  if not line.strip():continue
  hi,lo,move,kind,score,work=map(int,line.split(','));assert kind in (1,2,3) and score in (-1,0,1)
  key=(hi,lo);d=by.setdefault(key,{'lower':-1,'upper':1,'rows':[]});d['rows'].append((hi,lo,move,kind,score,work));records+=1
  if kind in (1,3):d['lower']=max(d['lower'],score)
  if kind in (2,3):d['upper']=min(d['upper'],score)
  assert d['lower']<=d['upper'],f'contradictory cached bounds for {key}'
output=[];exact=0;earliest=81
for key,d in by.items():
 row=max(d['rows'],key=lambda x:x[5]);hi,lo,move,kind,score,work=row
 if d['lower']==d['upper']:
  score=d['lower'];kind=3;exact+=1
  lower=[r for r in d['rows'] if r[3] in (1,3) and r[4]==score]
  if lower:move=max(lower,key=lambda x:x[5])[2]
 output.append((hi,lo,move,kind,score,work))
 k=(hi<<64)|lo;ply=sum(((k>>(10*c))&1023).bit_length()-1 for c in range(9));earliest=min(earliest,ply)
# Store larger-work entries last, giving them first choice of colliding buckets.
output.sort(key=lambda x:x[5])
(base/'continuation/merged-bounds.csv').write_text(''.join(','.join(map(str,r))+'\n' for r in output))
result={'input_files':len(files),'input_records':records,'unique_position_keys':len(output),'converged_exact_values':exact,'earliest_cached_ply':earliest,'contradictions':0}
(base/'continuation/merged-bounds-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
