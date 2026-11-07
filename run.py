#!/usr/bin/env python3
"""Bounded exact opening searches. Existing subtree bounds are loaded on resume."""
import argparse, concurrent.futures, json, re, subprocess, time
from pathlib import Path
BASE=Path(__file__).resolve().parent

def run(col, seconds):
    directory=BASE/'runs'/f'opening-{col}'
    (directory/'data').mkdir(parents=True,exist_ok=True)
    log=directory/f'search-{time.time_ns()}.log'
    with log.open('w') as f:
        result=subprocess.run([str(BASE/'attempt'),str(seconds),str(col)],cwd=directory,stdout=f,stderr=subprocess.STDOUT)
    text=log.read_text()
    status=re.search(r'STATUS=(\w+)',text)
    nodes=re.search(r'Total\s*=\s*([\d,]+)',text)
    value=re.search(r'side_to_move_value=(\S+)',text)
    entry=dict(opening=col,reflected_opening=10-col,status=status.group(1) if status else 'ERROR',exit_code=result.returncode,nodes=int(nodes.group(1).replace(',','')) if nodes else None,side_to_move_value=json.loads(value.group(1)) if value else None,log=str(log))
    (directory/'latest.json').write_text(json.dumps(entry,indent=2)+'\n')
    print(json.dumps(entry),flush=True)
    return entry

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds',type=int,default=600)
    parser.add_argument('--jobs',type=int,default=1)
    parser.add_argument('--openings',type=int,nargs='+',default=[5,4,3,2,1],choices=range(1,6))
    args=parser.parse_args()
    if args.seconds<=0 or args.jobs<=0:parser.error('seconds and jobs must be positive')
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        entries=list(pool.map(lambda c:run(c,args.seconds),args.openings))
    (BASE/'latest-run.json').write_text(json.dumps(entries,indent=2)+'\n')
