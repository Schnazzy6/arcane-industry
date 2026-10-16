"""Narrow upstream data fixes for the additional adventure/enchantment stack."""
import json, zipfile, shutil
from catalog import ROOT

mods=json.loads((ROOT/'pack.lock.json').read_text('utf-8'))['mods']
mod=next(m for m in mods if m['slug']=='extra_enchantments')
name='data/enchants/enchantment/poison_aspect.json'
with zipfile.ZipFile(ROOT/'cache/files'/mod['filename']) as jar:
    raw=jar.read(name).decode('utf-8')
    fixed=raw.replace('"description": {"Poison Aspect"','"description": {"text": "Ядовитый аспект"')
    data=json.loads(fixed)
target=ROOT/'overrides/common/kubejs'/name
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')

# Upstream line wrapping splits one attribute command into two invalid commands.
with zipfile.ZipFile(ROOT/'cache/files'/mod['filename']) as jar:
    name='data/effects/function/tick.mcfunction'
    raw=jar.read(name).decode('utf-8')
    fixed=raw.replace('minecraft:generic.\ngravity','minecraft:generic.gravity')
    target=ROOT/'overrides/common/kubejs'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(fixed,'utf-8')

server_mods=ROOT/'build/server/mods'
with zipfile.ZipFile(next(server_mods.glob('samurai_dynasty-*.jar'))) as jar:
    for statue in ['kawauso_statue','komainu_statue','tanuki_statue']:
        name=f'data/samurai_dynasty/loot_table/blocks/{statue}.json'
        data=json.loads(jar.read(name))
        for pool in data['pools']:
            for entry in pool['entries']:
                entry['name']='samurai_dynasty:'+statue
            for condition in pool.get('conditions',[]):
                if condition['condition']=='minecraft:block_state_property':
                    condition['block']='samurai_dynasty:'+statue
        target=ROOT/'overrides/common/kubejs'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(data,indent=2)+'\n','utf-8')
# Four orphan tables reference factories not registered in Mekanism Extras 1.4.1.
# Empty tables remove invalid item references; no existing factory drop is changed.
for tier in ['absolute','supreme','cosmic','infinite']:
    name=f'data/mekanism_extras/loot_table/blocks/{tier}_chemical_infusing_factory.json'
    target=ROOT/'overrides/common/kubejs'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps({'type':'minecraft:block','pools':[]},indent=2)+'\n','utf-8')
for folder in [ROOT/'build/server',ROOT/'build/prism/Arcane Industry Prototype/minecraft']:
    shutil.copytree(ROOT/'overrides/common',folder,dirs_exist_ok=True)
print('Applied 9 upstream data fixes: enchantment JSON/function, 3 statues, 4 orphan loot tables.')
