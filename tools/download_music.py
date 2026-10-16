"""Resume the large pinned music asset using verified HTTP byte ranges."""
import concurrent.futures,hashlib,pathlib,urllib.request
from catalog import ROOT,api
v=api('version/bqvWqBAp');f=v['files'][0]
dest=ROOT/'cache/files'/f['filename'];data=bytearray(f['size'])
prefix=dest.read_bytes() if dest.exists() else b''
data[:len(prefix)]=prefix
step=8*1024*1024
ranges=[(a,min(a+step,f['size'])) for a in range(len(prefix),f['size'],step)]
def get(pair):
 a,b=pair
 req=urllib.request.Request(f['url'],headers={'Range':f'bytes={a}-{b-1}'})
 with urllib.request.urlopen(req,timeout=90) as r:
  assert r.status==206,(r.status,a,b)
  chunk=r.read();assert len(chunk)==b-a
 return a,b,chunk
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
 for a,b,chunk in pool.map(get,ranges):data[a:b]=chunk
assert hashlib.sha512(data).hexdigest()==f['hashes']['sha512']
dest.write_bytes(data)
print('Music asset downloaded; SHA-512 matches Modrinth.',flush=True)
