#!/usr/bin/env python3
"""Exhaust fixed reply pairings with unconditional gravity legality, after P1 opens."""
import itertools,json
from pathlib import Path
W=H=9
LINES=[];TOUCH=[[] for _ in range(81)]
for r in range(9):
 for c in range(9):
  for dc,dr in [(1,0),(0,1),(1,1),(1,-1)]:
   cells=[(r+i*dr)*9+c+i*dc for i in range(4)]
   if 0<=r+3*dr<9 and 0<=c+3*dc<9:
    mask=sum(1<<x for x in cells);LINES.append(mask)
    for x in cells:TOUCH[x].append(mask)
def matchings(xs):
 if not xs:yield [];return
 a=xs[0]
 for i,b in enumerate(xs[1:],1):
  for tail in matchings(xs[1:i]+xs[i+1:]):yield [(a,b)]+tail

def verify(opening,pairs,attacks):
 partner={u:v for a,b in pairs for u,v in [(a,b),(b,a)]}
 assert len(partner)==80 and set(partner)==set(range(81))-{opening}
 occupied=1<<opening;discs=[1<<opening,0];heights=[0]*9;heights[opening]=1;history=str(opening+1)
 def play(cell,who):
  nonlocal occupied,history
  c=cell%9;r=cell//9
  assert heights[c]==r and not(occupied>>cell&1),'unplayable prescribed response'
  heights[c]+=1;occupied|=1<<cell;discs[who]|=1<<cell;history+=str(c+1)
  return any(discs[who]&m==m for m in TOUCH[cell])
 for c in attacks:
  cell=heights[c]*9+c
  if play(cell,1):return history
  assert cell in partner
  assert not play(partner[cell],0),'defender won before counterattack'
 raise AssertionError('attack did not win')

def pairs_for(opening,columns,ks):
 result=[(9*r+opening,9*(r+1)+opening) for r in range(1,9,2)]
 for (a,b),k in zip(columns,ks):
  result += [(9*r+a,9*r+b) for r in range(k)]
  for c in (a,b):result += [(9*r+c,9*(r+1)+c) for r in range(k,9,2)]
 return result

if __name__=='__main__':
 all_certificates=[];types=0;vertical_cases=0;bottom_cases=0
 for opening in range(5):
  for columns in matchings([c for c in range(9) if c!=opening]):
   # k=1: choose bottom-pair orientation so P1 never connects four in row 1.
   for orientation in itertools.product([0,1],repeat=4):
    defender={opening}|{p[1-bit] for p,bit in zip(columns,orientation)}
    if not any(set(range(c,c+4))<=defender for c in range(6)):break
   else:raise AssertionError('no safe bottom orientation')
   attacks=[p[bit] for p,bit in zip(columns,orientation)]+[0,1,2,3]
   pairs=pairs_for(opening,columns,[1]*4)
   history=verify(opening,pairs,attacks)
   all_certificates.append({'opening_column':opening+1,'column_pairs':columns,'cross_prefix_lengths':[1]*4,'attack_columns':[c+1 for c in attacks],'verified_history':history,'response_pairs_cells':pairs})
   bottom_cases+=1
   # Other prefix choices: an opponent can stack four in a column with k>=3.
   for ks in itertools.product([1,3,5,7,9],repeat=4):
    types+=1
    if max(ks)==1:continue
    j=next(i for i,k in enumerate(ks) if k>=3);c=columns[j][0]
    # Verify every structural type, not only a representative sample.
    verify(opening,pairs_for(opening,columns,ks),[c]*4)
    vertical_cases+=1
 result={'status':'ALL_CLASSIFIED_ALWAYS_LEGAL_FIXED_PAIRINGS_REFUTED','opening_orbits':5,'column_matchings_per_opening':105,'prefix_length_options':[1,3,5,7,9],'classified_strategy_types':types,'vertical_counterattacks':vertical_cases,'explicit_bottom_then_second_row_certificates':bottom_cases,'max_counterattack_game_plies':max(len(x['verified_history']) for x in all_certificates),'scope':'First-player fixed perfect matchings that prescribe an immediately legal partner reply for every gravity-consistent pair-completed state, even if terminal rules are ignored. Structural classification is proved in pairing-theorem.md. This does not rule out adaptive strategies or determine the game value.'}
 Path('continuation/pairing-refutation-certificates.json').write_text(json.dumps(all_certificates)+'\n')
 Path('continuation/pairing-refutation-result.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result),flush=True)
