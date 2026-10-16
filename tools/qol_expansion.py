"""Install the selected QoL expansion incrementally, without rebuilding or launching."""
import hashlib,json,os,pathlib,shutil,subprocess,zipfile,tomllib
from catalog import ROOT,api

CLIENT=ROOT/'build/prism/Arcane Industry Prototype/minecraft'
SERVER=ROOT/'build/server'
LOCAL=pathlib.Path(os.environ['APPDATA'])/'PrismLauncher/instances/ArcaneIndustry-0.1.4/minecraft'
SPECS=[
 ('lootjs','5AZDyUSn',True,True),
 ('morejs','kyNrtsUY',True,True),
 ('pf-neoforge','f3SxKzof',True,False),
 ('reactive-music','bqvWqBAp',True,False),
 ('particle-core','2QF4NhZD',True,False),
 ('tiny-item-animations','mSJPeo1D',True,False),
 ('simple-backups','6JQL4qSR',False,True),
 ('more-overlays-updated','Kq8xaqKi',True,False),
 ('modular-routers','6qMDJ0mn',True,True),
]

def fetch(row):
 dest=ROOT/'cache/files'/row['filename']
 if not dest.exists():
  subprocess.run(['curl.exe','-fLsS','--retry','3','-o',str(dest),row['url']],check=True)
 data=dest.read_bytes()
 if row.get('sha512'):assert hashlib.sha512(data).hexdigest()==row['sha512'],row['slug']
 with zipfile.ZipFile(dest) as z:
  assert z.testzip() is None
  path=next((p for p in ['META-INF/neoforge.mods.toml','META-INF/mods.toml'] if p in z.namelist()),None)
  if path:meta=tomllib.loads(z.read(path).decode())
  else:
   assert row['slug']=='gml' and 'META-INF/services/net.neoforged.neoforgespi.language.IModLanguageLoader' in z.namelist(),row['slug']
   meta={}
  row['mod_ids']=[m['modId'] for m in meta.get('mods',[])]
  print(row['slug'],row['version'],json.dumps(meta.get('dependencies',{})),flush=True)
 row.update(sha512=hashlib.sha512(data).hexdigest(),sha1=hashlib.sha1(data).hexdigest(),size=len(data),category='qol-expansion')
 for target,enabled in [(CLIENT,row['client']),(SERVER,row['server']),(LOCAL,row['client'])]:
  if enabled:
   (target/'mods').mkdir(parents=True,exist_ok=True)
   shutil.copy2(dest,target/'mods'/dest.name)
 return row

def install():
 rows=[]
 for slug,vid,client,server in SPECS:
  p=api('project/'+slug);v=api('version/'+vid)
  assert '1.21.1' in v['game_versions'] and 'neoforge' in v['loaders']
  f=next((f for f in v['files'] if f['primary']),v['files'][0])
  rows.append(fetch(dict(slug=slug,title=p['title'],project_id=p['id'],version_id=vid,version=v['version_number'],filename=f['filename'],url=f['url'],sha512=f['hashes']['sha512'],client=client,server=server,source='https://modrinth.com/mod/'+slug)))
 for slug,pid,fid,name,version in [
  ('building-gadgets',298187,6850515,'buildinggadgets2-1.3.9.jar','1.3.9'),
  ('mob-grinding-utils',254241,6804869,'mob_grinding_utils-1.1.10+mc1.21.1.jar','1.1.10')]:
  url=f'https://edge.forgecdn.net/files/{fid//1000}/{fid%1000:03d}/{name}'
  rows.append(fetch(dict(slug=slug,title=slug,curseforge_project_id=pid,curseforge_file_id=fid,version=version,filename=name,url=url,client=True,server=True,source=f'https://www.curseforge.com/minecraft/mc-mods/{slug}/files/{fid}')))
 for slug,pid,fid,name,version in [
  ('eating-animation-forge',570544,5567664,'eatinganimation-1.21.0-6.0.1.jar','6.0.1'),
  ('gml',661517,5902913,'gml-6.0.2.jar','6.0.2')]:
  url=f'https://edge.forgecdn.net/files/{fid//1000}/{fid%1000:03d}/{name}'
  rows.append(fetch(dict(slug=slug,title=slug,curseforge_project_id=pid,curseforge_file_id=fid,version=version,filename=name,url=url,client=True,server=False,source=f'https://www.curseforge.com/minecraft/mc-mods/{slug}/files/{fid}')))
 name='cosmeticarmorreworked-1.21.1-v1-neoforge.jar'
 rows.append(fetch(dict(slug='cosmetic-armor-reworked',title='Cosmetic Armor Reworked',version='1.21.1-v1-neoforge',filename=name,url='https://github.com/zlainsama/CosmeticArmorReworked/releases/download/1.21.1-v1-neoforge/'+name,client=True,server=True,source='https://github.com/zlainsama/CosmeticArmorReworked/releases/tag/1.21.1-v1-neoforge')))
 if (ROOT/'qol.lock.json').exists():
  names={r['slug'] for r in rows}
  rows += [r for r in json.loads((ROOT/'qol.lock.json').read_text('utf-8')) if r['slug'] not in names]
 lockpath=ROOT/'pack.lock.json';lock=json.loads(lockpath.read_text('utf-8'))
 names={r['slug'] for r in rows};lock['mods']=[r for r in lock['mods'] if r['slug'] not in names]+rows
 lock['mods'].sort(key=lambda r:r['slug'])
 lockpath.write_text(json.dumps(lock,ensure_ascii=False,indent=2),'utf-8')
 (ROOT/'build/qol-expansion.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf-8')
 (ROOT/'qol.lock.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf-8')
 print('Installed selected expansion:',len(rows))

if __name__=='__main__':install()
