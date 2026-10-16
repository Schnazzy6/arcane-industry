"""Resolve exact Modrinth files, verify hashes, and stage client/server packs."""
import concurrent.futures, hashlib, json, pathlib, shutil, urllib.request, urllib.parse, zipfile, subprocess
from catalog import ROOT, api, inspect

BUILD = ROOT/'build'
CLIENT = BUILD/'prism'/'Arcane Industry Prototype'/'minecraft'
SERVER = BUILD/'server'
DOWNLOAD = ROOT/'cache'/'files'
for p in [CLIENT/'mods', SERVER/'mods', DOWNLOAD]: p.mkdir(parents=True,exist_ok=True)

# A modest worldgen stack: Terralith + Tectonic, with RU reserved for a later comparison.
EXCLUDE = set('extended-industrialization regions-unexplored relics construction-wand building-gadgets blood-magic botania presence-footsteps moreculling'.split())
EXCLUDE.update('ftb-library ftb-teams ftb-quests ftb-chunks ftb-ultimine twilight-forest cataclysm ars-elemental eidolon-repraised'.split())
EXCLUDE.add('ae2-auto-pattern-upload')  # 2.0.0 loads client Screen on the dedicated server.
EXCLUDE.update('ae-additions expanded-ae ae2-automatic-requester ae2-pattern-restocker inventory-profiles-next'.split())
EXCLUDE.update(['modern-dynamics','falling-leaves','draconic-evolution'])
EXCLUDE.update(['create','create-stock-bridge','storage-drawers-create-compat','iris-flw-compat'])
EXCLUDE.update(['mekanism','mekanism-generators','mekanism-extras','applied-mekanistics','just-enough-mekanism-multiblocks'])
EXCLUDE.add('emi')  # JEI is the selected recipe viewer.
EXCLUDE.add('appleskin')  # Valheim Reforged replaces the hunger bar this mod annotates.
EXCLUDE.update(['mystical-agriculture','mystical-agradditions','mystical-customization','cucumber'])
rows = json.loads((ROOT/'catalog.json').read_text('utf-8'))
rows = [r for r in rows if r.get('version') and r['requested'] not in EXCLUDE]
COMBAT=set('apotheosis apothic-enchanting apothic-attributes apothic-spawners placebo gateways-to-eternity champions-unofficial mowzies-mobs simply-swords better-combat immersive-armors mutant-monsters relics-mod'.split())
if (ROOT/'combat-candidates.json').exists():
    for r in json.loads((ROOT/'combat-candidates.json').read_text('utf-8')):
        if r['requested'] in COMBAT and r.get('version'):
            r['category']='combat'
            rows.append(r)
    for r in json.loads((ROOT/'combat-candidates.json').read_text('utf-8')):
        if r['requested'] in ['extended-industrialization'] and r.get('version'):
            r['category']='industry'
            rows.append(r)
for category, slug in [('world','eternal-starlight'),('performance','blur-plus'),('utility','pipez'),('dependency','epherolib'),('combat','epic-samurais'),('magic','eidolonrepraised'),('world','l_enders-cataclysm'),('foundation','lodestonelib'),('foundation','architectury-api'),('foundation','shatterbyte-lib'),('industry','re-avaritia'),('mi-addon','industrialization-overdrive'),('mi-addon','yet-another-industrialization'),('mi-addon','modern-industrialization-sound-addon'),('mi-addon','mi-utilities'),('food','spice-of-life-valheim-reforged')]:
    r = inspect((category,slug))
    if r.get('version'): rows.append(r)

for category, slug in [('animation','entity-model-features'),('animation','entitytexturefeatures'),('resourcepack','fresh-animations')]:
    r=inspect(('shader' if category=='resourcepack' else category,slug))
    if not r.get('version'): raise RuntimeError('Missing animation file '+slug)
    r['category']=category
    rows.append(r)

for slug in 'cooking-for-blockheads effortless-building chat-heads leaves-be-gone dis-enchanting-table extra_enchantments reliquified-artifacts reliquified-ars-nouveau reliquified-l-ender-s-cataclysm reliquified-twilight-forest more-relics toast-control disableinsecurechattoast almostunified gravestone-mod gravestone-carryables no-recipe-book-system'.split():
    r=inspect(('qol-extra',slug))
    if not r.get('version'): raise RuntimeError('Missing selected QoL '+slug)
    rows.append(r)

# Tech Reborn/Connector versions are pinned in qol.lock.json; Fabric dependencies
# are supplied by Forgified Fabric API rather than the ordinary Fabric API.

chosen = {}
exact = set()
def add(p,v,category='dependency',pinned=False):
    pid=p['id']
    if pid in chosen:
        old=chosen[pid]
        if old['version']['id']==v['id']: return
        if pid in exact and pinned: raise RuntimeError('Conflicting exact dependencies: '+p['slug'])
        if pid in exact or not pinned: return
    chosen[pid]={'project':p,'version':v,'category':category}
    if pinned: exact.add(pid)

for r in rows: add(r['project'],r['version'],r['category'])
# Metadata pins in small addons can name old JEI builds despite a broad runtime range.
# JEI 19.32 preserves the EMI JEMI API; pin matching AE2 terminal and FTB compat.
for slug,vid in [('jei','MAi4uKUF'),('ae2-fluid-crafting-terminal','rYtyJ2jT'),('iris','KduFYu4t'),('azurelib','U0XjCPrV')]:
    p=api('project/'+slug);v=api('version/'+vid)
    chosen[p['id']]={'project':p,'version':v,'category':'qol-extra' if slug=='jei' else 'performance'}
    exact.add(p['id'])
while True:
    before={k:v['version']['id'] for k,v in chosen.items()}
    for row in list(chosen.values()):
        for d in row['version']['dependencies']:
            if d['dependency_type']!='required': continue
            # Samurai metadata names a Curios fork; the existing Curios supplies the same mod ID.
            if d.get('project_id')=='BaqCltvf' and any(x['project']['slug']=='curios' for x in chosen.values()): continue
            if d['version_id']:
                v=api('version/'+d['version_id']); p=api('project/'+v['project_id'])
                if '1.21.1' not in v['game_versions'] or 'neoforge' not in v['loaders']:
                    raise RuntimeError('Incompatible exact dependency '+p['slug'])
                if p['slug']=='jei': continue
                add(p,v,pinned=True)
            elif d['project_id'] and d['project_id'] not in chosen:
                r=inspect(('dependency',d['project_id']))
                if not r.get('version'): raise RuntimeError('Missing required dependency '+d['project_id'])
                add(r['project'],r['version'])
    if before=={k:v['version']['id'] for k,v in chosen.items()}: break

def download(row):
    p,v=row['project'],row['version']
    f=next((x for x in v['files'] if x['primary']),v['files'][0])
    dest=DOWNLOAD/f['filename']
    def valid(): return dest.exists() and hashlib.sha512(dest.read_bytes()).hexdigest()==f['hashes']['sha512']
    if not valid():
        subprocess.run(['curl.exe','--fail','--location','--silent','--show-error','--retry','3','--output',str(dest),f['url']],check=True)
    if not valid(): raise RuntimeError('Hash mismatch '+f['filename'])
    shader=row['category']=='shader'
    resourcepack=row['category']=='resourcepack'
    client=p.get('client_side')!='unsupported' or p['slug'] in ['smartbrainlib','lithostitched','baguettelib']
    server=p.get('server_side')!='unsupported' and not shader and not resourcepack and p['slug']!='shulkerboxtooltip'
    # Server-side profiling/pregeneration need no client installation.
    if client:
        target=CLIENT/('shaderpacks' if shader else 'resourcepacks' if resourcepack else 'mods')/f['filename']
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(dest,target)
    if server: shutil.copy2(dest,SERVER/'mods'/f['filename'])
    result={'slug':p['slug'],'title':p['title'],'project_id':p['id'],'version_id':v['id'],
        'version':v['version_number'],'filename':f['filename'],'sha512':f['hashes']['sha512'],
        'sha1':f['hashes']['sha1'],'url':f['url'],'size':f['size'],'client':client,'server':server,
        'category':row['category'],'license':p['license']['id'],'source':'https://modrinth.com/'+p['project_type']+'/'+p['slug']}
    print(p['slug'],v['version_number'],flush=True)
    return result

if __name__=='__main__':
    print('Resolved',len(chosen),'projects',flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: lock=list(pool.map(download, chosen.values()))
    # Preserve explicitly selected CurseForge/GitHub and pinned QoL additions.
    if (ROOT/'qol.lock.json').exists():
        extras=json.loads((ROOT/'qol.lock.json').read_text('utf-8'))
        names={x['slug'] for x in extras}
        lock=[x for x in lock if x['slug'] not in names]+extras
        for row in extras:
            src=DOWNLOAD/row['filename']
            if not src.exists():
                subprocess.run(['curl.exe','-fLsS','--retry','3','-o',str(src),row['url']],check=True)
            assert hashlib.sha512(src.read_bytes()).hexdigest()==row['sha512']
            for target,side in [(CLIENT,'client'),(SERVER,'server')]:
                if row[side]:shutil.copy2(src,target/'mods'/src.name)
    lock.sort(key=lambda x:x['slug'])
    for directory in [CLIENT/'mods',SERVER/'mods']:
        side='client' if directory==CLIENT/'mods' else 'server'
        expected={x['filename'] for x in lock if x[side]}
        if (ROOT/'custom.lock.json').exists(): expected.update(x['filename'] for x in json.loads((ROOT/'custom.lock.json').read_text('utf-8')) if x[side])
        if (ROOT/'curse.lock.json').exists(): expected.update(x['filename'] for x in json.loads((ROOT/'curse.lock.json').read_text('utf-8')) if x[side])
        for path in directory.glob('*.jar'):
            if path.name not in expected and not path.name.startswith('ftb-'):
                assert path.resolve().is_relative_to((ROOT/'build').resolve())
                path.unlink()
    (ROOT/'pack.lock.json').write_text(json.dumps({'minecraft':'1.21.1','neoforge':'21.1.259','mods':lock},ensure_ascii=False,indent=2),'utf-8')
    print('Staged',len(lock),'projects',flush=True)

