#!/usr/bin/env python3
"""CEGIS for static gravity-compatible response pairings (sufficient, incomplete)."""
import argparse,itertools,json,time
from pathlib import Path
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint
from scipy.sparse import coo_matrix

def lines(w,h):
 out=[]
 for c in range(w):
  for r in range(h):
   for dc,dr in [(1,0),(0,1),(1,1),(1,-1)]:
    cells=[(c+i*dc,r+i*dr) for i in range(4)]
    if all(0<=x<w and 0<=y<h for x,y in cells):out.append(frozenset(y*w+x for x,y in cells))
 return out

def legality(pairs,occupied,w,h):
 partner={u:v for u,v in pairs for u,v in [(u,v),(v,u)]}
 which={u:i for i,p in enumerate(pairs) for u in p}
 below=lambda u:set(r*w+u%w for r in range(u//w))-occupied
 pre=[set(which[x] for u in p for x in below(u) if which[x]!=i) for i,p in enumerate(pairs)]
 # Find a cycle in the contracted support graph.
 color=[0]*len(pairs);stack=[]
 def visit(i):
  if color[i]==1:return set(stack[stack.index(i):])
  if color[i]==2:return None
  color[i]=1;stack.append(i)
  for j in pre[i]:
   bad=visit(j)
   if bad:return bad
  stack.pop();color[i]=2
  return None
 for i in range(len(pairs)):
  bad=visit(i)
  if bad:return bad,'support_cycle'
 def closure(ids):
  todo=list(ids);out=set(ids)
  while todo:
   for j in pre[todo.pop()]:
    if j not in out:out.add(j);todo.append(j)
  return out
 for i,(u,v) in enumerate(pairs):
  if u%w==v%w:
   if abs(u-v)!=w:return {i},'nonconsecutive_vertical'
   continue
  for a,b in [(u,v),(v,u)]:
   completed=closure(which[x] for x in below(a))
   if i in completed:return completed,'self_dependency'
   cells=occupied|set(x for j in completed for x in pairs[j])
   if not below(b)<=cells:return completed|{i},'unplayable_response'
 return None,'valid'

def run(w,h,opening,defender,seconds):
 assert defender=='first', 'This model starts after the first player opening; only first-player response strategies have the correct turn order.'
 start=time.monotonic();occupied={opening};own=occupied
 cells=[x for x in range(w*h) if x not in occupied]
 if len(cells)%2:raise ValueError('remaining cells must be even')
 # Nonconsecutive same-column pairs can never be legal responses.
 pairs=[p for p in itertools.combinations(cells,2) if p[0]%w!=p[1]%w or abs(p[1]-p[0])==w]
 groups=[g for g in lines(w,h) if not g&own]
 rows=[];low=[];high=[]
 for x in cells:rows.append({i:1 for i,p in enumerate(pairs) if x in p});low.append(1);high.append(1)
 for g in groups:
  row={}
  for i,(u,v) in enumerate(pairs):
   vertical=u%w==v%w and v-u==w
   if (vertical and v in g) or (u in g and v in g):row[i]=1
  rows.append(row);low.append(1);high.append(np.inf)
 cuts=0
 while time.monotonic()-start<seconds:
  rr=[];cc=[];data=[]
  for i,row in enumerate(rows):
   for j,v in row.items():rr.append(i);cc.append(j);data.append(v)
  mat=coo_matrix((np.array(data,dtype=float),(np.array(rr,dtype=np.int32),np.array(cc,dtype=np.int32))),shape=(len(rows),len(pairs))).tocsc()
  remain=seconds-(time.monotonic()-start)
  res=milp(np.zeros(len(pairs)),integrality=np.ones(len(pairs)),bounds=Bounds(0,1),constraints=LinearConstraint(mat,np.array(low),np.array(high)),options={'time_limit':max(1,min(30,remain)),'mip_rel_gap':0.0,'presolve':True})
  if res.x is None:
   status='NO_STATIC_PAIRING_IN_MODEL' if res.status==2 else 'UNKNOWN_MILP_LIMIT'
   return dict(status=status,solver_status=int(res.status),message=res.message,cuts=cuts,seconds=time.monotonic()-start,pair_variables=len(pairs),winning_groups=len(groups))
  chosen=[i for i,x in enumerate(res.x) if x>.5];selected=[pairs[i] for i in chosen]
  # Independently check integer feasibility before using a candidate.
  assert sorted(x for p in selected for x in p)==cells
  for g in groups:assert any((u%w==v%w and v-u==w and v in g) or (u in g and v in g) for u,v in selected)
  bad,reason=legality(selected,occupied,w,h)
  if bad is None:
   return dict(status='VERIFIED_STATIC_NONLOSS_STRATEGY',defender=defender,opening=opening,width=w,height=h,pairs=selected,cuts=cuts,seconds=time.monotonic()-start)
  forbidden=[chosen[j] for j in bad];rows.append({i:1 for i in forbidden});low.append(-np.inf);high.append(len(forbidden)-1);cuts+=1
  print(json.dumps({'iteration':cuts,'reason':reason,'cut_size':len(forbidden),'seconds':time.monotonic()-start}),flush=True)
 return dict(status='UNKNOWN_CEGIS_TIMEOUT',cuts=cuts,seconds=time.monotonic()-start)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--width',type=int,default=9);p.add_argument('--height',type=int,default=9);p.add_argument('--opening',type=int,default=5);p.add_argument('--defender',choices=['first'],default='first');p.add_argument('--seconds',type=int,default=180);p.add_argument('--output',default='continuation/pairing-result.json');a=p.parse_args()
 result=run(a.width,a.height,a.opening-1,a.defender,a.seconds);Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
