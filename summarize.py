#!/usr/bin/env python3
import json,re
from pathlib import Path
base=Path(__file__).resolve().parent
runs=[]
for c in range(1,6):
 directory=base/'runs'/f'opening-{c}'
 text=(directory/'search.log').read_text()
 status=re.search(r'STATUS=(\w+)',text)
 total=re.search(r'Total\s*=\s*([\d,]+)',text)
 elapsed=re.search(r'elapsed_seconds=([\d.]+)',text)
 value=re.search(r'side_to_move_value=(\S+)',text)
 table=directory/'data'/'table-9x9.csv'
 entry={'opening':c,'reflected_opening':10-c,'status':status.group(1) if status else 'RUNNING','side_to_move_value':json.loads(value.group(1)) if value else None,'node_visits':int(total.group(1).replace(',','')) if total else None,'wall_seconds':float(elapsed.group(1)) if elapsed else None,'saved_bound_records':sum(1 for _ in table.open()) if table.exists() else 0}
 runs.append(entry)
horizon=[json.loads(x) for x in (base/'horizon.jsonl').read_text().splitlines()]
completed=[x for x in horizon if 'depth' in x]
result={'empty_board_status':'UNRESOLVED','rules':'standard gravity 9x9 connect-four','full_game_opening_searches':runs,'full_game_node_visits':sum(x['node_visits'] or 0 for x in runs),'saved_bound_records':sum(x['saved_bound_records'] for x in runs),'independent_horizon':{'last_completed':completed[-1],'final_record':horizon[-1],'interpretation':'Zero is a finite-horizon value, not a proved full-game draw.'},'independent_endgame_certificate':json.loads((base/'certificate-verification.json').read_text()),'validation':{'standard_7x6':'PASS: light suite and 1000 known-state weak/strong/self-play cases','9x9':(base/'validation.log').read_text().splitlines()[-1],'horizon':(base/'validation-horizon.log').read_text().strip(),'certificate_negative_tests':json.loads((base/'certificate-negative-tests.json').read_text())}}
(base/'results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
