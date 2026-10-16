"""Resolve the requested NeoForge ports, their dependencies, and replace Croptopia."""
import concurrent.futures,hashlib,json,os,pathlib,subprocess,urllib.request,zipfile
from catalog import ROOT,api,inspect
from qol_expansion import fetch,CLIENT,SERVER,LOCAL

SELECTED='diet-appleseed-edition betterend-neoforge betternether-neoforge endrem factory-blocks held-item-info-neoforge 3dskinlayers trash-cans framedblocks macaws-doors macaws-fences-and-walls oceans-delight ends-delight my-nethers-delight cultural-delights brewin-and-chewin farmers-respite-unofficial-port'.split()
CLIENT_ONLY={'held-item-info-neoforge','3dskinlayers'}
removed={'croptopia'}

def ranged_download(f):
 dest=ROOT/'cache/files'/f['filename']
 if dest.exists() and hashlib.sha512(dest.read_bytes()).hexdigest()==f['hashes']['sha512']:return
 if f['size']<20*1024*1024:return
 data=bytearray(f['size']);step=4*1024*1024
 def part(bounds):
  a,b=bounds;req=urllib.request.Request(f['url'],headers={'Range':f'bytes={a}-{b-1}'})
  with urllib.request.urlopen(req,timeout=120) as r:
   assert r.status==206
   chunk=r.read();assert len(chunk)==b-a
  return a,b,chunk
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  for a,b,chunk in pool.map(part,[(a,min(a+step,len(data))) for a in range(0,len(data),step)]):data[a:b]=chunk
 assert hashlib.sha512(data).hexdigest()==f['hashes']['sha512']
 dest.write_bytes(data)

def install():
 lock=json.loads((ROOT/'pack.lock.json').read_text('utf-8'))
 existing={r.get('project_id'):r for r in lock['mods'] if r.get('project_id')}
 selected={}
 pins_path=ROOT/'tools/data/content-expansion-pins.json'
 pins=json.loads(pins_path.read_text('utf-8')) if pins_path.exists() else {}
 def resolve(slug,vid=None):
  p=api('project/'+slug)
  if p['id'] in selected:return
  if p['id'] in existing and p['slug'] not in SELECTED:return
  vid=vid or pins.get(p['slug'])
  v=api('version/'+vid) if vid else inspect(('content-expansion',slug)).get('version')
  assert v and '1.21.1' in v['game_versions'] and 'neoforge' in v['loaders'],slug
  selected[p['id']]=(p,v)
  for d in v['dependencies']:
   if d['dependency_type']=='required':resolve(d['project_id'],d.get('version_id'))
 for slug in SELECTED:resolve(slug)
 (ROOT/'tools/data/content-expansion-pins.json').write_text(json.dumps({p['slug']:v['id'] for p,v in selected.values()},indent=2),'utf-8')
 def download(pair):
  p,v=pair;f=next((x for x in v['files'] if x['primary']),v['files'][0])
  ranged_download(f)
  side=p['slug'] not in CLIENT_ONLY
  return fetch(dict(slug=p['slug'],title=p['title'],project_id=p['id'],version_id=v['id'],version=v['version_number'],filename=f['filename'],url=f['url'],sha512=f['hashes']['sha512'],client=True,server=side,source='https://modrinth.com/mod/'+p['slug']))
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(download,selected.values()))
 # Remove only the exact Croptopia file from known destinations; keep worlds.
 curse=json.loads((ROOT/'curse.lock.json').read_text('utf-8'))
 for row in lock['mods']+curse:
  if row['slug'] in removed:
   for base in [CLIENT,SERVER,LOCAL]:
    p=base/'mods'/row['filename'];assert p.resolve().is_relative_to((base/'mods').resolve());p.unlink(missing_ok=True)
 curse=[r for r in curse if r['slug'] not in removed]
 (ROOT/'curse.lock.json').write_text(json.dumps(curse,ensure_ascii=False,indent=2),'utf-8')
 names={r['slug'] for r in rows}|removed
 lock['mods']=[r for r in lock['mods'] if r['slug'] not in names]+rows
 lock['mods'].sort(key=lambda r:r['slug'])
 (ROOT/'pack.lock.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2),'utf-8')
 q=json.loads((ROOT/'qol.lock.json').read_text('utf-8'));q=[r for r in q if r['slug'] not in names]+rows
 (ROOT/'qol.lock.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),'utf-8')
 (ROOT/'build/content-expansion.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf-8')
 print('Installed',len(rows),'new projects/dependencies. Removed Croptopia; kept Valheim Reforged.',flush=True)

if __name__=='__main__':install()
