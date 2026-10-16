"""Install the verified Connector stack and retire Mekanism without deleting worlds."""
import hashlib,json,os,pathlib,shutil,zipfile,urllib.parse
from catalog import ROOT,api

RETIRED={'mekanism','mekanism-generators','mekanism-extras','applied-mekanistics','just-enough-mekanism-multiblocks'}
TARGETS=[ROOT/'build/server',ROOT/'build/prism/Arcane Industry Prototype/minecraft',pathlib.Path(os.environ['APPDATA'])/'PrismLauncher/instances/ArcaneIndustry-0.1.4/minecraft']

def install():
    trial=ROOT/'build/techreborn-test'
    versions={r['slug']:r['version'] for r in json.loads((trial/'mods.lock.json').read_text('utf-8')) if r['slug']!='reborncore'}
    vs=api('project/mcpitanlibarch/version?'+urllib.parse.urlencode({'game_versions':'["1.21.1"]','loaders':'["fabric"]'}))
    versions['mcpitanlibarch']=next(v for v in vs if v['version_number']=='4.0.9-fabric-1.21.1' or any(f['filename']=='mcpitanlib-4.0.9-1.21.1-fabric.jar' for f in v['files']))
    rows=[]
    for slug,v in versions.items():
        p=api('project/'+v['project_id']);f=next((f for f in v['files'] if f.get('primary')),v['files'][0]);src=trial/f['filename']
        assert hashlib.sha512(src.read_bytes()).hexdigest()==f['hashes']['sha512'],src
        shutil.copy2(src,ROOT/'cache/files'/src.name)
        ids={'techreborn':['techreborn','reborncore','team_reborn_energy'],'advanced-reborn':['advanced_reborn'],'mcpitanlibarch':['mcpitanlib'],'connector':['connector'],'connector-extras':['connectorextras'],'forgified-fabric-api':['fabric_api']}
        row=dict(slug=slug,title=p['title'],project_id=p['id'],version_id=v['id'],version=v['version_number'],filename=f['filename'],url=f['url'],sha512=f['hashes']['sha512'],sha1=f['hashes']['sha1'],size=f['size'],client=True,server=True,source='https://modrinth.com/mod/'+slug,category='industry-late',mod_ids=ids[slug])
        rows.append(row)
    oldrows=json.loads((ROOT/'pack.lock.json').read_text('utf-8'))['mods']+json.loads((ROOT/'curse.lock.json').read_text('utf-8'))
    for i,target in enumerate(TARGETS):
        assert target.resolve() in [t.resolve() for t in TARGETS]
        backup=ROOT/'build/mekanism-before-techreborn/mods'/str(i);backup.mkdir(parents=True,exist_ok=True)
        for r in oldrows:
            if r['slug'] in RETIRED:
                src=target/'mods'/r['filename']
                if src.exists():shutil.move(str(src),str(backup/src.name))
        for r in rows:shutil.copy2(ROOT/'cache/files'/r['filename'],target/'mods'/r['filename'])
    for filename in ['pack.lock.json','qol.lock.json','curse.lock.json']:
        path=ROOT/filename;data=json.loads(path.read_text('utf-8'));entries=data['mods'] if isinstance(data,dict) else data
        entries[:]=[r for r in entries if r['slug'] not in RETIRED and r['slug'] not in versions]
        if filename!='curse.lock.json':entries.extend(rows);entries.sort(key=lambda r:r['slug'])
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf-8')
    (ROOT/'tools/data/techreborn-pins.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf-8')
    print('Installed',len(rows),'projects; retired',len(RETIRED),'Mekanism projects; all worlds preserved')

if __name__=='__main__':install()
