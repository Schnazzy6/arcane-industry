"""Conservative affix loot caps and explicit MI prerequisites for Apothic world tiers.

This is not the complete expert progression: recipes, native boss drops and team
milestones remain a separate implementation step. Never edit upstream JAR files.
"""
import json, pathlib, zipfile
from catalog import ROOT

OUT=ROOT/'overrides/common/kubejs/data'
TIERS=['haven','frontier','ascent','summit','pinnacle']
records=[]
mods=json.loads((ROOT/'pack.lock.json').read_text('utf-8'))['mods']
mods+=json.loads((ROOT/'curse.lock.json').read_text('utf-8'))

def stacks(value):
    if isinstance(value,dict):
        if isinstance(value.get('id'),str) and ':' in value['id'] and ('count' in value or len(value)<=2):
            yield value['id']
        for v in value.values(): yield from stacks(v)
    elif isinstance(value,list):
        for v in value: yield from stacks(v)

def minimum(item):
    ns,name=item.split(':',1)
    tier_file=ROOT/'build/equipment-tiers.json'
    if tier_file.exists():
        data=json.loads(tier_file.read_text('utf-8'))
        tier=data['armor'].get(item,data['tools'].get(item))
        if tier is not None:return 99 if tier>=8 else 0 if tier<=1 else 1 if tier==2 else 2 if tier==3 else 3 if tier==4 else 4
    # Endgame armour / signature boss equipment must never be global random loot.
    if ns=='avaritia': return 99
    if ns=='immersive_armors' and any(t in name for t in ['divine_','wither_']): return 99
    if ns=='samurai_dynasty' and any(t in name for t in ['master_samurai','netherite_samurai']): return 99
    if ns=='modern_industrialization' and any(t in name for t in ['quantum_','gravichestplate']): return 99
    if ns=='extended_industrialization' and ('nano_quantum' in name or 'nyano' in name): return 99
    if ns=='techreborn' and any(t in name for t in ['nano_','quantum_','nanosaber','omni_tool']): return 99
    if ns=='ars_elemancy' or (ns=='ars_nouveau' and 'battlemage' in name): return 99
    if ns=='cataclysm' and 'black_steel' not in name: return 99
    if ns=='irons_spellbooks' and any(t in name for t in ['netherite_mage','pyromancer','cryomancer','electromancer','shadowwalker','plagued','archevoker']): return 99
    if any(t in name for t in ['netherite','master_samurai','divine_','wither_','fiery_','knightly_','phantom_','yeti_']): return 3
    if any(t in name for t in ['diamond','steel_samurai','steel_ninja','steeleaf','sorcerer','prismarine_']): return 2
    if any(t in name for t in ['iron_','chainmail','warrior_','heavy_','steampunk','ironwood','black_steel']): return 1
    return 0

def write(name,data):
    target=OUT/pathlib.PurePosixPath(name).relative_to('data')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')

def disable(data):
    data.setdefault('neoforge:conditions',[]).append({'type':'neoforge:false'})

for mod in mods:
    if not mod['filename'].endswith('.jar'): continue
    path=ROOT/'cache/files'/mod['filename']
    if not path.exists(): continue
    with zipfile.ZipFile(path) as jar:
        for name in jar.namelist():
            if not name.startswith('data/') or not name.endswith('.json'):continue
            affix='/affix_loot_entries/' in name
            gear='/gear_sets/' in name
            if not affix and not gear:continue
            data=json.loads(jar.read(name))
            items=list(stacks(data))
            level=max([minimum(i) for i in items],default=0)
            if not level:continue
            action=''
            if level==99:
                disable(data);action='craft_or_native_boss_only'
            elif affix:
                weights=data.get('weights',{})
                if 'weight' in weights:
                    data['weights']={t:weights.copy() for t in TIERS[level:]}
                else:
                    data['weights']={k:v for k,v in weights.items() if k in TIERS[level:]}
                    if not data['weights']:disable(data)
                action='minimum_world_tier_'+TIERS[level]
            else:
                tags=data.get('tags',[])
                tier_names=[t for t in TIERS if any(str(tag).startswith(t+'_') for tag in tags)]
                if any(TIERS.index(t)<level for t in tier_names):
                    disable(data);action='excluded_from_lower_tier_gear_set'
            if action:
                write(name,data)
                records.append({'path':name,'items':items,'action':action})

# Low / mid tier gear from the selected packs can gain native Apotheosis affixes.
for material,min_tier in [('warrior',1),('robe',0),('bone',0)]:
    for slot in ['helmet','chestplate','leggings','boots']:
        item=f'immersive_armors:{material}_{slot}'
        write(f'data/arcaneindustry/affix_loot_entries/{material}_{slot}.json',{
            'type':'apotheosis:affix_loot_entry','stack':{'count':1,'id':item},
            'weights':{t:{'weight':4} for t in TIERS[min_tier:]}})
for material,min_tier in [('iron',1),('diamond',2),('runic',3)]:
    write(f'data/arcaneindustry/affix_loot_entries/{material}_katana.json',{
        'type':'apotheosis:affix_loot_entry','stack':{'count':1,'id':f'simplyswords:{material}_katana'},
        'weights':{t:{'weight':3} for t in TIERS[min_tier:]}})

apoth=next(m for m in mods if m['slug']=='apotheosis')
gates={'frontier':'modern_industrialization:analog_circuit',
       'ascent':'modern_industrialization:processing_unit',
       'summit':'modern_industrialization:quantum_circuit',
       'pinnacle':'kubejs:infinity_stabilizer'}
with zipfile.ZipFile(ROOT/'cache/files'/apoth['filename']) as jar:
    for tier,item in gates.items():
        name=f'data/apotheosis/advancement/progression/{tier}.json'
        data=json.loads(jar.read(name))
        old=list(data['criteria'])
        data['criteria']['arcaneindustry_milestone']={
            'trigger':'minecraft:inventory_changed',
            'conditions':{'items':[{'items':[item]}]}}
        data.setdefault('requirements',[[k] for k in old]).append(['arcaneindustry_milestone'])
        data['display']['description']={'text':f'Исходные условия Apotheosis и промышленный этап: {item}. Предмет достаточно получить; он не расходуется.'}
        write(name,data)

for folder in [ROOT/'build/server',ROOT/'build/prism/Arcane Industry Prototype/minecraft']:
    import shutil
    shutil.copytree(ROOT/'overrides/common',folder,dirs_exist_ok=True)
report={'policy':'provisional_affix_loot_caps','overrides':records,'world_tier_milestones':gates,
        'extra_modded_entries':15,
        'limits':['native boss loot and all chest tables are not globally rewritten',
                  'world tier milestones are per player; team sharing is a later quest task',
                  'recipe tiers are implemented for selected armour paths, not every equipment mod']}
(ROOT/'build/loot-policy-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
print('Loot overrides:',len(records),'; added modded entries: 15; gated world tiers:',len(gates))
if (ROOT/'tools/progression_security.py').exists() and (ROOT/'build/qol-recipe-patches.json').exists():
 from progression_security import generate
 generate()
