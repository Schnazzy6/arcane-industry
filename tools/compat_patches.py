"""Repair upstream data format issues without changing progression or costs."""
import zipfile,json,pathlib,shutil
from catalog import ROOT
OUT=ROOT/'overrides/common/kubejs/data'
def write(path,data):
    out=OUT/path
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
def load(slug):
    lock=json.loads((ROOT/'pack.lock.json').read_text('utf-8'))['mods']
    row=next(x for x in lock if x['slug']==slug)
    return zipfile.ZipFile(ROOT/'cache/files'/row['filename'])
with load('malum') as z:
    for n in z.namelist():
        if n.startswith('data/malum/recipe/malum/spirit_repair/') and n.endswith('.json'):
            data=json.loads(z.read(n))
            if 'validItems' not in data:
                data['validItems']=data.pop('inputs',[])
                write(pathlib.Path(n).relative_to('data'),data)
    n='data/malum/recipe/create/milling/grim_talc.json'
    data=json.loads(z.read(n))
    for result in data['results']:result['id']=result.pop('item')
    write(pathlib.Path(n).relative_to('data'),data)
with load('hexerei') as z:
    n='data/hexerei/loot_table/blocks/willow_vines.json'
    data=json.loads(z.read(n))
    def fix(obj):
        if isinstance(obj,dict):
            if obj.get('condition')=='forge:can_tool_perform_action':
                obj['condition']='neoforge:can_item_perform_ability'
                obj['ability']=obj.pop('action')
            for v in obj.values():fix(v)
        elif isinstance(obj,list):
            for v in obj:fix(v)
    fix(data);write(pathlib.Path(n).relative_to('data'),data)
with load('extended-ae') as z:
    n='data/extendedae/loot_table/blocks/ex_emc_interface.json'
    data=json.loads(z.read(n))
    data['neoforge:conditions']=[{'type':'neoforge:mod_loaded','modid':'projecte'}]
    write(pathlib.Path(n).relative_to('data'),data)
# AE Additions has been removed; remove only our four obsolete resource overrides.
for base in [ROOT/'overrides/common',ROOT/'build/server',ROOT/'build/prism/Arcane Industry Prototype/minecraft']:
    for size in ['1024','4096','16384','65536']:
        path=base/f'kubejs/assets/ae2additions/models/block/crafting/{size}k_storage_formed.json'
        if path.exists():
            assert path.resolve().is_relative_to(ROOT.resolve())
            path.unlink()
with load('dungeons-and-taverns') as z:
    for leaf in ['give_quest_trader_trade','wander_add_map']:
        n=f'data/minecraft/advancement/{leaf}.json'
        data=json.loads(z.read(n));data.pop('parent',None)
        write(pathlib.Path(n).relative_to('data'),data)
with load('eidolonrepraised') as z:
    for leaf in ['tracking','hailing']:
        n=f'data/eidolon_repraised/affixes/ability/{leaf}.json'
        data=json.loads(z.read(n))
        definition=data.get('definition',{})
        definition['exclusive_set']=[v.replace('eidolon_repraised:hailing','eidolon_repraised:ability/hailing').replace('eidolon_repraised:tracking','eidolon_repraised:ability/tracking') for v in definition.get('exclusive_set',[])]
        write(pathlib.Path(n).relative_to('data'),data)
for target in [ROOT/'build/server',ROOT/'build/prism/Arcane Industry Prototype/minecraft']:
    shutil.copytree(ROOT/'overrides/common',target,dirs_exist_ok=True)
print('Compatibility data overrides:',len(list(OUT.rglob('*.json'))))
