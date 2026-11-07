"""Independent exhaustive small-board check of the structural matching lemma."""
import itertools,json,time
from pathlib import Path

def matchings(xs):
 if not xs:yield ();return
 for i in range(1,len(xs)):
  for rest in matchings(xs[1:i]+xs[i+1:]):yield ((xs[0],xs[i]),)+rest

def legal_all(matching,q,w,h):
 partner={u:v for a,b in matching for u,v in ((a,b),(b,a))}
 full=(1<<(w*h))-1;seen={1<<q};todo=[1<<q]
 def playable(cell,occupied):return not(occupied>>cell&1) and (cell<w or occupied>>(cell-w)&1)
 while todo:
  occupied=todo.pop()
  if occupied==full:continue
  for c in range(w):
   r=0
   while r<h and (occupied>>(r*w+c)&1):r+=1
   if r==h:continue
   u=r*w+c;v=partner[u];after=occupied|(1<<u)
   if not playable(v,after):return False
   after|=1<<v
   if after not in seen:seen.add(after);todo.append(after)
 return True

def classified(w,h,q):
 out=set()
 fixed=[(r*w+q,(r+1)*w+q) for r in range(1,h,2)]
 for columns in matchings([c for c in range(w) if c!=q]):
  for lengths in itertools.product(range(1,h+1,2),repeat=len(columns)):
   cells=list(fixed)
   for (a,b),k in zip(columns,lengths):
    cells.extend((r*w+a,r*w+b) for r in range(k))
    for c in (a,b):cells.extend((r*w+c,(r+1)*w+c) for r in range(k,h,2))
   out.add(tuple(sorted(tuple(sorted(p)) for p in cells)))
 return out
results=[]
for w,h,q in [(3,3,0),(3,3,1),(3,5,1),(5,3,2)]:
 start=time.monotonic();accepted=set();tested=0
 for m in matchings([x for x in range(w*h) if x!=q]):
  tested+=1
  if legal_all(m,q,w,h):accepted.add(tuple(sorted(tuple(sorted(p)) for p in m)))
 expected=classified(w,h,q)
 assert accepted==expected,{'width':w,'height':h,'missing':list(accepted-expected)[:1],'extra':list(expected-accepted)[:1]}
 result={'width':w,'height':h,'opening_column':q+1,'all_cell_matchings_tested':tested,'always_legal_matchings':len(accepted),'classification_matches':True,'seconds':time.monotonic()-start};results.append(result);print(json.dumps(result),flush=True)
Path('continuation/pairing-classification-check.json').write_text(json.dumps(results,indent=2)+'\n')
