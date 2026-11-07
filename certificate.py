#!/usr/bin/env python3
"""Independent exact endgame proof construction and strategy-tree verification."""
import functools,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
LINES=[]
for r in range(9):
 for c in range(9):
  for dc,dr in [(1,0),(0,1),(1,1),(1,-1)]:
   cells=[(c+i*dc,r+i*dr) for i in range(4)]
   if all(0<=x<9 and 0<=y<9 for x,y in cells):LINES.append(sum(1<<(y*9+x) for x,y in cells))
def won(p):return any(p&line==line for line in LINES)
def legal(h):return [c for c in range(9) if h[c]<9]
def move(a,b,h,c):
 assert c in legal(h)
 bit=1<<(9*h[c]+c);h=list(h);h[c]+=1
 return b,a|bit,tuple(h)
def replay(seq):
 a=b=0;h=(0,)*9
 for c in map(lambda x:int(x)-1,seq):
  assert not won(a) and not won(b),'play continued after a win'
  a,b,h=move(a,b,h,c)
 return a,b,h
@functools.lru_cache(None)
def value(a,b,h):
 if won(b):return -1
 if sum(h)==81:return 0
 best=-1
 for c in legal(h):
  v=-value(*move(a,b,h,c));best=max(best,v)
  if best==1:break
 return best
def make(a,b,h,root_turn,turn):
 if won(b):
  assert turn!=root_turn
  return {'terminal':'root_player_wins'}
 assert sum(h)<81
 cols=legal(h)
 if turn==root_turn:cols=[next(c for c in cols if -value(*move(a,b,h,c))==1)]
 return {'moves':[{'column':c+1,'child':make(*move(a,b,h,c),root_turn,1-turn)} for c in cols]}
def verify(a,b,h,node,root_turn,turn):
 if won(b):
  assert turn!=root_turn and node=={'terminal':'root_player_wins'}
  return 1,1,0
 assert not won(a) and sum(h)<81
 assert set(node)=={'moves'}
 children=node['moves'];cols=[x['column']-1 for x in children]
 assert len(cols)==len(set(cols)) and all(c in legal(h) for c in cols)
 if turn==root_turn:assert len(cols)==1
 else:assert sorted(cols)==legal(h),'opponent reply missing'
 count,leaves,depth=1,0,0
 for child,c in zip(children,cols):
  assert set(child)=={'column','child'}
  n,l,d=verify(*move(a,b,h,c),child['child'],root_turn,1-turn)
  count+=n;leaves+=l;depth=max(depth,1+d)
 return count,leaves,depth
if __name__=='__main__':
 target=BASE/'endgame-certificate.json'
 if len(sys.argv)>1:
  target=Path(sys.argv[1]);doc=json.loads(target.read_text())
 else:
  fixtures=[json.loads(x) for x in (BASE/'fixtures-9x9.jsonl').read_text().splitlines()]
  fixture=next(x for x in fixtures if x['side_to_move_value']==1)
  seq=fixture['moves'];state=replay(seq);assert value(*state)==1
  doc={'rules':'standard gravity 9x9 connect-four','opening_moves_1_based':seq,'winning_player':1+len(seq)%2,'proof':make(*state,len(seq)%2,len(seq)%2)}
  target.write_text(json.dumps(doc,indent=2)+'\n')
 seq=doc['opening_moves_1_based'];turn=len(seq)%2
 assert doc['rules']=='standard gravity 9x9 connect-four' and doc['winning_player']==turn+1
 n,l,d=verify(*replay(seq),doc['proof'],turn,turn)
 print(json.dumps({'status':'VERIFIED','root_ply':len(seq),'winning_player':doc['winning_player'],'proof_nodes':n,'winning_leaves':l,'maximum_additional_plies':d,'certificate':str(target)}))
