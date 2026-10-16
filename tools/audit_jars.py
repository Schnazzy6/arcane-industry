import pathlib,zipfile,tomllib,json
from catalog import ROOT
mods={}
deps=[]
def scan(data,filename):
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for n in ['META-INF/neoforge.mods.toml','META-INF/mods.toml']:
            if n not in z.namelist(): continue
            try: t=tomllib.loads(z.read(n).decode('utf-8'))
            except Exception as e: print('PARSE',filename,str(e));continue
            for m in t.get('mods',[]):
                mid=m['modId']
                if mid in mods and mods[mid]!=filename and '!' not in mods[mid] and '!' not in filename: raise RuntimeError('Duplicate mod ID '+mid+': '+mods[mid]+' / '+filename)
                mods[mid]=filename
            dependency_table=t.get('dependencies',{})
            if not isinstance(dependency_table,dict): dependency_table={}
            for owner, entries in dependency_table.items():
                for d in entries:
                    if str(d.get('type','')).lower()=='required' or d.get('mandatory') or d.get('required'):
                        deps.append((owner,d['modId'],d.get('versionRange'),d.get('side'),filename))
            break
        if 'META-INF/jarjar/metadata.json' in z.namelist():
            for j in json.loads(z.read('META-INF/jarjar/metadata.json')).get('jars',[]):
                if j['path'] in z.namelist(): scan(z.read(j['path']),filename+'!'+j['path'])

for p in (ROOT/'build/prism/Arcane Industry Prototype/minecraft/mods').glob('*.jar'):
    try: scan(p.read_bytes(),p.name)
    except zipfile.BadZipFile: print('BAD ZIP',p.name)
for d in sorted(set(deps)):
    if d[1] not in mods and d[1] not in ['minecraft','neoforge','java']:
        print('MISSING',*d)
print('Top level jars',len(list((ROOT/'build/prism/Arcane Industry Prototype/minecraft/mods').glob('*.jar'))),'mod ids',len(mods))
