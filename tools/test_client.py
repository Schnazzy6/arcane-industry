import os,pathlib,shutil,json
from catalog import ROOT
source=ROOT/'build/prism/Arcane Industry Prototype'
target=pathlib.Path(os.environ['APPDATA'])/'PrismLauncher/instances/ArcaneIndustry-0.1.4'
target.mkdir(exist_ok=True)
for p in (target/'minecraft/mods').glob('*.jar'):
    if not (source/'minecraft/mods'/p.name).exists():
        assert p.resolve().is_relative_to(target.resolve());p.unlink()
shutil.copytree(source,target,dirs_exist_ok=True)
shutil.copytree(ROOT/'overrides/client',target/'minecraft',dirs_exist_ok=True)
cfg=(source/'instance.cfg').read_text('utf-8').replace('Prototype 0.1.0','Prototype 0.1.4')
(target/'instance.cfg').write_text(cfg,'utf-8')
options=target/'minecraft/options.txt'
option_map={line.split(':',1)[0]:line.split(':',1)[1] for line in options.read_text('utf-8').splitlines() if ':' in line}
option_map['version']='3955'
mods=json.loads((ROOT/'pack.lock.json').read_text('utf-8'))['mods']
fresh=next(x for x in mods if x['slug']=='fresh-animations')
option_map['resourcePacks']=json.dumps(['vanilla','file/'+fresh['filename'],'file/ArcaneIndustry-HUD.zip'])
options.write_text('\n'.join(k+':'+v for k,v in option_map.items())+'\n','utf-8')
iris=target/'minecraft/config/iris.properties'
iris.write_text('enableShaders=true\nshaderPack=ComplementaryReimagined_r5.9.3.zip\n','utf-8')
profile='''SHADOW_QUALITY=0
shadowDistance=96.0
WATER_REFLECT_QUALITY=2
BLOCK_REFLECT_QUALITY=1
LIGHTSHAFT_QUALI_DEFINE=1
SSAO_QUALI_DEFINE=2
FXAA_DEFINE=1
DETAIL_QUALITY=2
CLOUD_QUALITY=2
ANISOTROPIC_FILTER=0
COLORED_LIGHTING=0
WORLD_SPACE_REFLECTIONS=-1
ENTITY_SHADOW=-1
RAIN_PUDDLES=0
'''
(target/'minecraft/shaderpacks/ComplementaryReimagined_r5.9.3.zip.txt').write_text(profile,'utf-8')
print('Updated client staged separately: ArcaneIndustry-0.1.4; shaders enabled for test.')
