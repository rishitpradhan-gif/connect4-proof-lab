#!/usr/bin/env python3
"""Check the finite arithmetic and the newly generalized obstruction examples.

This is a reproducibility aid, not a proof-assistant formalization.
All dependencies are from the Python standard library.
"""
from functools import lru_cache
import itertools
import json
from pathlib import Path

DRAW='391312592458742532275685278998225892717344155499998768414433753463371118176668666'
ENDGAME='39421491566662378229414344134332195837825578331151769764866818772488699279'

@lru_cache(None)
def lines(height):
    masks=[];touch=[[] for _ in range(9*height)]
    for r in range(height):
        for c in range(9):
            for dc,dr in [(1,0),(0,1),(1,1),(1,-1)]:
                if 0<=c+3*dc<9 and 0<=r+3*dr<height:
                    ids=[9*(r+k*dr)+c+k*dc for k in range(4)]
                    m=sum(1<<i for i in ids);masks.append(m)
                    for i in ids:touch[i].append(m)
    return masks,touch

def replay(history,height=9):
    masks,touch=lines(height);h=[0]*9;boards=[0,0]
    for ply,ch in enumerate(history):
        c=int(ch)-1;assert 0<=c<9 and h[c]<height
        assert not any(boards[p]&m==m for p in [0,1] for m in masks)
        cell=9*h[c]+c;h[c]+=1;boards[ply%2]|=1<<cell
    return boards,h

def matchings(xs):
    if not xs:yield [];return
    for j in range(1,len(xs)):
        for rest in matchings(xs[1:j]+xs[j+1:]):yield [(xs[0],xs[j])]+rest

def attack(height,q,columns,prefix,actions):
    _,touch=lines(height)
    pairs=[(9*r+q,9*(r+1)+q) for r in range(1,height,2)]
    for (a,b),k in zip(columns,prefix):
        pairs.extend((9*r+a,9*r+b) for r in range(k))
        for c in (a,b):pairs.extend((9*r+c,9*(r+1)+c) for r in range(k,height,2))
    partner={u:v for u,v in pairs for u,v in ((u,v),(v,u))}
    assert len(partner)==9*height-1
    boards=[1<<q,0];h=[0]*9;h[q]=1
    def move(cell,who):
        c=cell%9;r=cell//9
        assert h[c]==r and r<height
        h[c]+=1;boards[who]|=1<<cell
        return any(boards[who]&m==m for m in touch[cell])
    for turn,c in enumerate(actions,1):
        cell=9*h[c]+c
        if move(cell,1):return 2*turn
        assert not move(partner[cell],0), 'responder won first'
    raise AssertionError('counterattack failed')

def generalized_cases(height):
    count=0;max_ply=0
    for q in range(5):
        for columns in matchings([c for c in range(9) if c!=q]):
            for orientation in itertools.product([0,1],repeat=4):
                own={q}|{pair[1-bit] for pair,bit in zip(columns,orientation)}
                if not any(set(range(c,c+4))<=own for c in range(6)):break
            else:raise AssertionError('union-bound witness absent')
            for prefix in itertools.product(range(1,height+1,2),repeat=4):
                if max(prefix)==1:
                    actions=[pair[bit] for pair,bit in zip(columns,orientation)]+[0,1,2,3]
                else:
                    j=next(i for i,k in enumerate(prefix) if k>=3);actions=[columns[j][0]]*4
                max_ply=max(max_ply,attack(height,q,columns,prefix,actions));count+=1
    expected=5*105*((height+1)//2)**4
    assert count==expected and max_ply<=16
    return {'height':height,'representative_openings':5,'configurations':count,'max_counterattack_ply':max_ply}

def main():
    masks,_=lines(9);assert len(masks)==180
    boards,h=replay(DRAW);X,O=boards
    assert len(DRAW)==81 and h==[9]*9 and [X.bit_count(),O.bit_count()]==[41,40]
    assert X==int('25889bb7746b8ab96655',16) and O==int('1da7764488b94754699aa',16)
    for d,text in [(1,'3f1f8fc7e3f1f8fc7e3f'),(9,'3fffffffffffff'),(10,'7e3f1f8fc7e3f'),(8,'3f1f8fc7e3f1f8')]:
        for z in boards:assert int(text,16)&z&(z>>d)&(z>>(2*d))&(z>>(3*d))==0
    boards,h=replay(ENDGAME);assert len(ENDGAME)==74 and h==[9,8,9,9,5,9,8,9,8]
    assert not any(boards[p]&m==m for p in [0,1] for m in masks)
    boards1=boards.copy();boards1[0]|=1<<(9*8+1);h1=h.copy();h1[1]+=1
    assert [c for c in range(9) if h1[c]<9]==[4,6,8]
    for reply in [4,6,8]:
        bb=boards1.copy();hh=h1.copy();bb[1]|=1<<(9*hh[reply]+reply);hh[reply]+=1
        assert not any(bb[1]&m==m for m in masks)
        bb[0]|=1<<(9*hh[4]+4)
        assert any(bb[0]&m==m for m in masks)
    results={'draw_integer_certificate':'PASS','three-ply_endgame':'PASS','generalized_obstruction_checks':[generalized_cases(H) for H in [5,7]]}
    Path('audit_results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
