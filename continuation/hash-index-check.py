import json
from pathlib import Path
mask=(1<<23)-1;u64=(1<<64)-1
# Hold outer columns fixed; vary 6 disc colors in middle columns, 3 per side.
import itertools
base=sum(3<<(10*c) for c in range(9))+sum(1<<(10*c) for c in range(9))
positions=[]
for chosen in itertools.combinations([30,31,40,41,50,51],3):positions.append(base+sum(1<<i for i in chosen))
def mixed(k):
 x=((k&u64)^((k>>64)*0x9e3779b97f4a7c15))&u64
 x^=x>>30;x=x*0xbf58476d1ce4e5b9&u64;x^=x>>27;x=x*0x94d049bb133111eb&u64;x^=x>>31
 return x&mask
old={((k&u64)^((k>>64)*0x9e3779b97f4a7c15))&mask for k in positions}
new={mixed(k) for k in positions}
result={'test':'encoded positions with middle-column color variations and fixed occupancy','encoded_positions':len(positions),'old_distinct_buckets':len(old),'mixed_distinct_buckets':len(new),'correctness':'All table hits still require complete position-key equality; this is a performance fix.'}
assert len(old)==1 and len(new)==len(positions)
Path('continuation/hash-index-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
