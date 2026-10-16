"""Generate the first playable medium-high recipe integration, without distribution archives."""
import json, pathlib, copy, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'build/progression-catalog.json').read_text('utf-8'))
items={}; recipes=[]; remove=set(); patches=[]; armor=[]
M='modern_industrialization:'; K='kubejs:'
def part(name,title,texture='minecraft:item/amethyst_shard'):
 items[name]={'title':title,'texture':texture};return K+name
def ing(x):return {'tag':x[1:]} if x.startswith('#') else {'item':x}
def add(name,data):recipes.append({'id':'kubejs:progression/'+name,'json':data})
def shapeless(name,out,inputs,count=1):add(name,{'type':'minecraft:crafting_shapeless','ingredients':[ing(x) for x in inputs],'result':{'id':out,'count':count}})
def shaped(name,out,pattern,key,count=1):add(name,{'type':'minecraft:crafting_shaped','pattern':pattern,'key':{k:ing(v) for k,v in key.items()},'result':{'id':out,'count':count}})
def machine(name,out,inputs,count=1,eu=16,duration=200,type='assembler'):
 assert len(inputs)<=6,(name,'too many input slots')
 add(name,{'type':M+type,'eu':eu,'duration':duration,'item_inputs':[dict(ing(x),amount=n) for x,n in inputs],'item_outputs':[{'item':out,'amount':count}]})
def apparatus(name,out,reagent,pedestals,count=1,source=1000):add(name,{'type':'ars_nouveau:enchanting_apparatus','reagent':ing(reagent),'pedestalItems':[ing(x) for x in pedestals],'result':{'id':out,'count':count},'sourceCost':source,'keepNbtOfReagent':False})
def patch(mod,suffix,fn):
 found=[(p,r) for p,r in D[mod]['recipes'].items() if p.endswith('/'+suffix+'.json')]
 assert found,(mod,suffix)
 for p,r in found:
  x=copy.deepcopy(r);fn(x)
  ns=p.split('/')[1];rid=ns+':'+p.split('/recipe/')[1][:-5]
  patches.append({'id':rid,'json':x})
def result_ids(r):
 out=[]
 for key in ['result','output','output_item','item_outputs']:
  x=r.get(key)
  if isinstance(x,str):out.append(x)
  elif isinstance(x,dict):out.append(x.get('id',x.get('item')))
  elif isinstance(x,list):out.extend(y.get('id',y.get('item')) for y in x if isinstance(y,dict))
 return [x for x in out if isinstance(x,str) and x]
mount=part('ritual_mount','Бронзовая ритуальная оправа','minecraft:item/copper_ingot')
resin=part('arcane_resin','Арканная пропитка','minecraft:item/glow_ink_sac')
electric=part('electrical_focus','Электрический фокус · M2','minecraft:item/echo_shard')
life=part('alchemical_catalyst','Алхимический катализатор · M2','minecraft:item/fermented_spider_eye')
industrial=part('industrial_focus','Промышленный фокус · M3','minecraft:item/ender_eye')
soul=part('soul_stabilizer','Стабилизатор душ · M3','minecraft:item/phantom_membrane')
ritual=part('ritual_frame','Титановая ритуальная рама · M4','minecraft:item/nautilus_shell')
element=part('elemental_insulator','Стихийный изолятор · M3','minecraft:item/prismarine_crystals')
seals=[part('seal_'+n,'Мастерская печать: '+ru,'minecraft:item/'+tex) for n,ru,tex in [('life','жизнь и материя','heart_of_the_sea'),('mind','разум и пространство','ender_eye'),('soul','души и тьма','ghast_tear'),('elements','стихии и древние знания','fire_charge')]]
interface=part('mekanism_interface','Квантовый интерфейс Mekanism · P5','minecraft:item/nether_star')
convergence=part('convergence_core','Ядро объединения · P5','minecraft:item/ender_pearl')
stabilizer=part('infinity_stabilizer','Стабилизатор бесконечности · P7','minecraft:item/dragon_breath')
cores=[None]+[part('armor_core_t'+str(t),'Каркас улучшения брони · T'+str(t),'minecraft:item/'+('netherite_upgrade_smithing_template' if t>=4 else 'amethyst_shard')) for t in range(1,7)]
# Initial magic never needs electricity. One small apparatus batch supports several MI crafts.
shaped('ritual_mount',mount,['BCB',' S ',' L '],{'B':M+'bronze_plate','C':M+'copper_plate','S':'ars_nouveau:source_gem','L':'minecraft:lapis_lazuli'},4)
apparatus('arcane_resin',resin,'minecraft:slime_ball',['ars_nouveau:source_gem',M+'bronze_plate','minecraft:redstone','minecraft:lapis_lazuli'],4,500)
remove.add(M+'analog_circuit_board')
shaped('analog_board_manual',M+'analog_circuit_board',['RCR',' R ',' A '],{'R':M+'rubber_sheet','C':M+'copper_plate','A':resin},2)
machine('analog_board_batch',M+'analog_circuit_board',[(M+'rubber_sheet',8),(M+'copper_plate',4),(resin,1)],4,8,160)
machine('electrical_focus',electric,[(M+'analog_circuit',2),(mount,2),('ars_nouveau:source_gem',2),(M+'gold_plate',1)],4,8,200)
shapeless('alchemical_catalyst',life,['theurgy:mercury_shard','naturesaura:infused_iron','occultism:spirit_attuned_gem',M+'steel_plate'],4)
machine('industrial_focus',industrial,[(M+'digital_circuit',2),(electric,2),(M+'stainless_steel_plate',4),(life,1)],4,16,240)
shapeless('soul_stabilizer',soul,['malum:arcane_spirit','eidolon_repraised:soul_shard',M+'stainless_steel_plate','ars_nouveau:source_gem'],4)
machine('ritual_frame',ritual,[(M+'processing_unit',2),(M+'titanium_plate',4),(soul,2),(industrial,1)],4,32,300)
apparatus('elemental_insulator',element,industrial,['ars_nouveau:fire_essence','ars_nouveau:water_essence','ars_nouveau:air_essence','ars_nouveau:earth_essence'],4,2000)
shapeless('seal_life',seals[0],[life,'naturesaura:infused_iron','theurgy:mercury_shard',ritual],2)
shapeless('seal_mind',seals[1],['occultism:spirit_attuned_gem','ars_nouveau:magebloom_fiber','irons_spellbooks:arcane_essence',ritual],2)
shapeless('seal_soul',seals[2],['malum:soul_stained_steel_ingot','eidolon_repraised:soul_shard','evilcraft:dark_power_gem','goety:mystic_core',ritual],2)
shapeless('seal_elements',seals[3],[element,'forbidden_arcanus:deorum_ingot','hexerei:moon_dust',ritual],2)
machine('mekanism_interface',interface,[(M+'quantum_circuit',1)]+[(s,1) for s in seals],8,64,400)
machine('convergence_core',convergence,[(s,1) for s in seals]+[('mekanism:pellet_polonium',2),(M+'quantum_circuit',1)],4,64,400)
machine('infinity_stabilizer',stabilizer,[(s,1) for s in seals]+[('mekanism:pellet_antimatter',1),('minecraft:nether_star',1)],4,128,600)
# Preserve native school crafting/ritual serializers whenever possible.
patch('hex','mixing_cauldron',lambda r:(r['key'].update({'F':ing(mount)}),r.update(pattern=['TFT','#C#','###'])))
patch('iron','inscription_table',lambda r:(r['key'].update({'F':ing(mount)}),r.update(pattern=['F B','TTT','L L'])))
for suffix in ['calcination_oven','liquefaction_cauldron']:
 patch('theurgy',suffix,lambda r:(r['key'].update({'F':ing(electric)}),r.update(pattern=[' F ',r['pattern'][1],r['pattern'][2]])))
for suffix,bowl in [('golden_sacrificial_bowl','occultism:sacrificial_bowl'),('dark_golden_sacrificial_bowl','occultism:dark_sacrificial_bowl')]:
 patch('occult',suffix,lambda r,b=bowl:r.update(pattern=['gFg','gbg','ggg'],key={'g':ing('minecraft:gold_ingot'),'b':ing(b),'F':ing(electric)}))
patch('nature','nature_altar',lambda r:r['ingredients'].append(ing(electric)))
patch('malum','spirit_altar',lambda r:(r['key'].update({'F':ing(industrial)}),r.update(pattern=['FYF','ZXZ','XXX'])))
patch('eidolon','crucible',lambda r:(r['key'].update({'F':ing(industrial)}),r.update(pattern=['xFx','x x','xxx'])))
patch('evil','blood_infuser',lambda r:(r['key'].update({'F':ing(ritual)}),r.update(pattern=['CFC','CIC','CCC'])))
patch('goety','dark_altar',lambda r:(r['key'].update({'F':ing(ritual)}),r.update(pattern=['tFt','scs'])))
patch('iron','arcane_anvil',lambda r:(r['key'].update({'F':ing(industrial)}),r.update(pattern=['AFA',' D ','SVS'])))
patch('ars','apprentice_book_upgrade',lambda r:r['ingredients'].__setitem__(2,ing(electric)))
patch('ars','archmage_book_upgrade',lambda r:r['ingredients'].__setitem__(4,ing(ritual)))
# These assembler boards define the one-way dependencies between chapters.
for suffix,extra in [('digital_circuit_board',life),('processing_unit_board',soul)]:
 patch('mi',suffix,lambda r,x=extra:r['item_inputs'].append({'item':x,'amount':1}))
patch('mi','quantum_circuit_board',lambda r:r['item_inputs'].append({'item':seals[3],'amount':1}))
# Forbidden forge activation dust: keep its normal ingredients and add a late ritual frame.
for path,r in D['forbidden']['recipes'].items():
 if 'forbidden_arcanus:mundabitur_dust' in result_ids(r):
  x=copy.deepcopy(r)
  if isinstance(x.get('ingredients'),list) and len(x['ingredients'])<9:x['ingredients'].append(ing(ritual))
  elif x.get('type')=='minecraft:crafting_shaped':
   found=False
   for y,row in enumerate(x['pattern']):
    if ' ' in row:
     pos=row.index(' ');x['pattern'][y]=row[:pos]+'F'+row[pos+1:];x['key']['F']=ing(ritual);found=True;break
   assert found,path
  else:raise RuntimeError('Unhandled forbidden forge recipe '+path)
  patches.append({'id':path.split('/')[1]+':'+path.split('/recipe/')[1][:-5],'json':x})
# Most duplicated Mekanism components now come from MI, in practical batches.
mek_components={
 'basic_control_circuit':([(M+'processing_unit',1),(interface,1),(M+'osmium_plate',2)],4,32),
 'advanced_control_circuit':([('mekanism:basic_control_circuit',2),('mekanism:alloy_infused',2),(seals[1],1)],4,32),
 'elite_control_circuit':([('mekanism:advanced_control_circuit',2),('mekanism:alloy_reinforced',2),(M+'quantum_circuit',1)],4,64),
 'ultimate_control_circuit':([('mekanism:elite_control_circuit',2),('mekanism:alloy_atomic',2),(seals[3],1)],4,64),
 'alloy_infused':([(M+'iron_plate',4),('minecraft:redstone',8),(interface,1)],8,16),
 'alloy_reinforced':([('mekanism:alloy_infused',4),('minecraft:diamond',2),(element,1)],4,32),
 'alloy_atomic':([('mekanism:alloy_reinforced',4),('minecraft:obsidian',4),(seals[2],1)],4,64),
 'steel_casing':([(M+'advanced_machine_hull',1),(M+'stainless_steel_plate',4),(interface,1)],2,32),
 'hdpe_sheet':([('mekanism:hdpe_pellet',3)],3,16),
 'hdpe_rod':([('mekanism:hdpe_sheet',2)],2,16),
 'enriched_iron':([(M+'iron_dust',4),(M+'carbon_dust',1)],4,16),
}
# Osmium plates are not a MI material in every version: use the shared osmium ingot tag.
mek_components['basic_control_circuit'][0][2]=('#c:ingots/osmium',2)
for item,(inputs,count,eu) in mek_components.items():
 remove.add('mekanism:'+item);machine('mek_'+item,'mekanism:'+item,inputs,count,eu,240,type='mixer' if item=='enriched_iron' else 'assembler')
# Material processing alternatives in MI; unique Mekanism chemical/radiation machinery remains native.
for material in ['iron','gold','copper','tin','lead','uranium','osmium']:
 if any(r.get('type')==M+'macerator' and 'c:ingots/'+material+'"' in json.dumps(r) for r in D['mi']['recipes'].values()):continue
 machine('mek_dust_'+material,'mekanism:dust_'+material,[('#c:ingots/'+material,1)],1,2,100,type='macerator')
# AE2 storage arrives with the processing-unit stage; presses and basic tools remain preparable.
for mod,suffix,pattern,key in [
 ('ae2','controller',['FPF','PHP','FPF'],{'F':'ae2:fluix_crystal','P':M+'processing_unit','H':M+'advanced_machine_hull'}),
 ('ae2','drive',['SPS','CHC','SPS'],{'S':M+'stainless_steel_plate','P':M+'processing_unit','C':'ae2:chest','H':industrial})]:
 remove.add(mod+':'+suffix);shaped('ae2_'+suffix,mod+':'+suffix,pattern,key)
# Armor upgrade cores: one batch = one set; no piles of intermediate handcrafts.
shaped('armor_core_t1',cores[1],[' B ','LSL',' B '],{'B':M+'bronze_plate','L':'minecraft:leather','S':'ars_nouveau:source_gem'},4)
machine('armor_core_t2',cores[2],[(M+'steel_plate',8),(electric,1),('ars_nouveau:magebloom_fiber',2)],4,8,240)
machine('armor_core_t3',cores[3],[(M+'stainless_steel_plate',8),(industrial,1),(soul,1),('minecraft:diamond',2)],4,16,300)
machine('armor_core_t4',cores[4],[(M+'titanium_plate',8),(ritual,1)]+[(x,1) for x in seals[:3]],4,32,400)
machine('armor_core_t5',cores[5],[(s,1) for s in seals]+[('mekanism:pellet_polonium',2),(M+'quantum_circuit',4)],4,64,500)
shaped('armor_core_t6',cores[6],['III','ISI','III'],{'I':'avaritia:infinity_ingot','S':stabilizer},4)
slots=['helmet','chestplate','leggings','boots']
paths={
 'warrior':[['minecraft:leather_'+s for s in slots]]+[['immersive_armors:'+p+'_'+s for s in slots] for p in ['bone','warrior','heavy','wither','divine']],
 'samurai':[['minecraft:leather_'+s for s in slots]]+[['samurai_dynasty:'+p+'_'+s for s in slots] for p in ['light_samurai','steel_samurai','netherite_samurai','master_samurai','master_samurai']],
 'mage':[['minecraft:leather_'+s for s in slots],['immersive_armors:robe_'+s for s in slots]]+[['ars_nouveau:'+p+'_'+s for s in ['hood','robes','leggings','boots']] for p in ['arcanist','sorcerer','battlemage']]+[['ars_elemancy:elemancer_'+s for s in ['hat','robes','leggings','boots']]],
}
def upgrade(name,out,base,tier,material,special=False):
 remove.add(out)
 plate=[None,M+'bronze_plate',M+'steel_plate',M+'stainless_steel_plate',M+'titanium_plate',M+'iridium_plate','avaritia:crystal_matrix_ingot'][tier]
 binding=[None,'minecraft:leather',electric,industrial,soul,convergence,'avaritia:neutron_ingot'][tier]
 armor.append({'id':'kubejs:progression/armor/'+name,'out':out,'base':base,'core':cores[tier],'material':material,'plate':plate,'binding':binding,'tier':tier,'reinforce':special})
for branch,tiers in paths.items():
 for t in range(1,6):
  for i,slot in enumerate(slots):
   material=([None,'minecraft:bone',M+'steel_plate',M+'stainless_steel_plate',seals[2],seals[0]][t] if branch=='warrior' else
             [None,'minecraft:string',M+'steel_plate',M+'titanium_plate',seals[1],convergence][t] if branch=='samurai' else
             [None,'minecraft:string','ars_nouveau:magebloom_fiber',life,element,'ars_elemancy:elemancer_essence'][t])
   upgrade(branch+'_t'+str(t)+'_'+slot,tiers[t][i],tiers[t-1][i],t,material,branch=='samurai' and t==5)
# Extra magic appearances remain real upgrade paths, rather than cheap original recipes.
for key in D['elemancy']['items']:
 if not key.startswith('item.ars_elemancy.'):continue
 name=key.split('.',2)[2]
 if '.' in name:continue
 family=next((f for f in ['cinder','tempest','vapor','mire','lava','silt','elemancer'] if name.startswith(f+'_')),None)
 if not family:continue
 i=0 if name.endswith(('helmet','hood','hat')) else 1 if name.endswith(('chestplate','robes','tunic')) else 2 if name.endswith(('leggings','leggings_heavy','pants')) else 3 if name.endswith(('boots','boots_heavy','shoes')) else -1
 if i<0:continue
 out='ars_elemancy:'+name;t=5 if family=='elemancer' else 4
 if any(a['out']==out for a in armor):continue
 bases=paths['mage'][t-1][i]
 upgrade('elemancy_'+name,out,bases,t,'ars_elemancy:'+family+'_essence' if family=='elemancer' else element)
def armor_slot(name):
 return next((i for i,endings in enumerate([('helmet','hood','hat'),('chestplate','bodyarmor','robes','tunic'),('leggings','leggings_heavy','pants'),('boots','boots_heavy','shoes')]) if name.endswith(endings)),None)
for a in armor:
 if a['out'].startswith('ars_elemancy:') and a['tier']==5:
  i=armor_slot(a['out'])
  if i is not None:
   a['base']=[paths['mage'][4][i]]+[b['out'] for b in armor if b['tier']==4 and b['out'].startswith('ars_elemancy:') and armor_slot(b['out'])==i]
for i,slot in enumerate(slots):
 # Vanilla equipment follows the same milestones, including smithing to netherite.
 previous='minecraft:leather_'+slot
 for t,material in enumerate(['chainmail','iron','diamond','netherite'],1):
  out='minecraft:'+material+'_'+slot
  upgrade('vanilla_'+material+'_'+slot,out,previous,t,
          ['minecraft:iron_nugget',M+'steel_plate','minecraft:diamond','minecraft:netherite_ingot'][t-1])
  previous=out
 bases=[paths[b][4][i] for b in paths]+['minecraft:netherite_'+slot]
 upgrade('mekasuit_'+slot,'mekanism:mekasuit_'+('bodyarmor' if slot=='chestplate' else 'pants' if slot=='leggings' else slot),bases,5,'mekanism:pellet_polonium')
 bases=[paths[b][5][i] for b in ['warrior','mage']]+['mekanism:mekasuit_'+('bodyarmor' if slot=='chestplate' else 'pants' if slot=='leggings' else slot)]
 bases+=sorted({a['out'] for a in armor if a['tier']==5 and a['out'].startswith('ars_elemancy:') and armor_slot(a['out'])==i})
 # Reinforced Samurai base is matched by its explicit component marker.
 bases.append({'type':'neoforge:components','items':[paths['samurai'][5][i]],'components':{'minecraft:custom_data':{'arcane_armor_tier':'t5'}},'strict':False})
 upgrade('infinity_'+slot,'avaritia:infinity_'+('pants' if slot=='leggings' else slot),bases,6,'avaritia:infinity_ingot')
# High MI equipment and unrestricted replication no longer precede the intended finale.
for slot in slots:
 out=M+'quantum_'+slot;remove.add(out)
 shaped('mi_quantum_'+slot,out,[' I ',' Q ',' C '],{'I':'avaritia:infinity_ingot','Q':M+'quantum_upgrade','C':M+'quantum_circuit'})
remove.update([M+'replicator',M+'quantum_sword',M+'gravichestplate'])
machine('post_infinity_replicator',M+'replicator',[(M+'quantum_machine_hull',1),('avaritia:infinity_ingot',2),(stabilizer,1)],1,128,1200)
shaped('post_infinity_quantum_sword',M+'quantum_sword',[' I ',' Q ',' S '],{'I':'avaritia:infinity_ingot','Q':M+'quantum_upgrade','S':'minecraft:netherite_sword'})
shapeless('post_infinity_gravichestplate',M+'gravichestplate',[M+'quantum_chestplate','avaritia:infinity_ingot',stabilizer])
# Avaritia: production challenge, not 81-slot manual bulk crafting for every basic component.
remove.update(['avaritia:crystal_matrix_ingot','avaritia:neutron_collector','avaritia:neutron_compressor','avaritia:infinity_catalyst','avaritia:infinity_ingot'])
machine('crystal_matrix','avaritia:crystal_matrix_ingot',[('avaritia:diamond_lattice',4),('minecraft:nether_star',1),(convergence,1),('mekanism:pellet_antimatter',1)],4,128,800)
machine('neutron_collector','avaritia:neutron_collector',[(M+'quantum_machine_hull',1),('avaritia:crystal_matrix_ingot',4),('mekanism:ultimate_control_circuit',2),('minecraft:quartz_block',8)],1,128,800)
machine('neutron_compressor','avaritia:neutron_compressor',[(M+'quantum_machine_hull',1),('avaritia:crystal_matrix_ingot',4),('avaritia:neutron_ingot',2),('mekanism:ultimate_control_circuit',2)],1,128,800)
machine('infinity_ingot','avaritia:infinity_ingot',[('avaritia:neutron_ingot',16),('avaritia:crystal_matrix_ingot',8),('avaritia:infinity_catalyst',2),(stabilizer,1)],4,128,1200)
shapeless('unpack_matrix','avaritia:crystal_matrix_ingot',['avaritia:crystal_matrix'],9)
shapeless('unpack_infinity','avaritia:infinity_ingot',['avaritia:infinity'],9)
# Eight ordinary industrial singularities, all available in this pack.
sg=['iron','copper','gold','tin','lead','silver','nickel','bronze']
key={c:{'type':'avaritia:stack','item':{'id':'avaritia:singularity','count':1,'components':{'avaritia:singularity_id':'avaritia:'+m}}} for c,m in zip('12345678',sg)}
key.update({'C':ing(convergence),'S':ing(stabilizer),'N':ing('avaritia:neutron_ingot'),'M':ing('avaritia:cosmic_meatballs'),'V':ing('avaritia:ultimate_stew'),'E':ing('avaritia:endest_pearl'),'X':ing('avaritia:crystal_matrix_ingot')})
key.update({c:ing(s) for c,s in zip('LIOA',seals)})
catalyst_pattern=['1   X   2',' N     N ','  L   I  ','   C C   ','3 X S X 4','   C C   ','  O   A  ',' N M V N ','5  6E7  8']
assert all(len(row)==9 for row in catalyst_pattern)
add('infinity_catalyst',{'type':'avaritia:shaped_table','tier':4,'pattern':catalyst_pattern,'key':key,'result':{'id':'avaritia:infinity_catalyst','count':1}})
# A mid-high target: 4096 units per ordinary singularity, not many tens of thousands.
with zipfile.ZipFile(pathlib.Path(D['avaritia']['jar'])) as z:
 for material in sg:
  path='data/avaritia/singularities/'+material+'.json';r=json.loads(z.read(path));r['count']=4096
  p=ROOT/'overrides/common/kubejs'/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(r,indent=2),'utf-8')
# Prevent shared circuit tags and cheap standalone generators from bypassing late MI.
circuits={f'c:circuits/{tier}':'mekanism:'+name+'_control_circuit' for tier,name in [('basic','basic'),('advanced','advanced'),('elite','elite'),('ultimate','ultimate')]}
def circuit_inputs(x):
 if isinstance(x,list):return [circuit_inputs(v) for v in x]
 if isinstance(x,dict):
  if x.get('tag') in circuits:return {'item':circuits[x['tag']]}
  return {k:circuit_inputs(v) for k,v in x.items()}
 return x
for jar in (ROOT/'build/server/mods').glob('Mekanism*.jar'):
 with zipfile.ZipFile(jar) as z:
  for path in z.namelist():
   if '/recipe/' not in path or not path.endswith('.json'):continue
   original=json.loads(z.read(path));r=circuit_inputs(original)
   outputs=result_ids(r)
   if any(x in remove for x in outputs):continue
   if any(x in ['mekanismgenerators:heat_generator','mekanismgenerators:solar_generator','mekanismgenerators:wind_generator','mekanismgenerators:bio_generator'] for x in outputs) and 'pattern' in r:
    row=list(r['pattern'][1]);row[1]='Z';r['pattern'][1]=''.join(row);r['key']['Z']=ing(interface)
    used=set(''.join(r['pattern']));r['key']={k:v for k,v in r['key'].items() if k in used}
   if r!=original:
    rid=path.split('/')[1]+':'+path.split('/recipe/')[1][:-5]
    if not any(p['id']==rid for p in patches):patches.append({'id':rid,'json':r})
# Higher-complexity 9x9 cross-mod assemblies requested after the first playable pass.
from progression_crosslinks import connect
connect(globals())
from progression_integration import integrate
integrate(globals())
from content_integration import integrate as integrate_content
integrate_content(globals())
from techreborn_progression import migrate
migrate(globals())
from todo_progression import apply as apply_todo
apply_todo(globals())
from endgame_quarry import integrate as integrate_endgame_quarry
integrate_endgame_quarry(globals())
from creative_finale import integrate as integrate_creative_finale
integrate_creative_finale(globals())
from quality_pass import configure as configure_quality
configure_quality()
patches[:]=[p for p in patches if not any(x in remove for x in result_ids(p['json']))]
# Write generated definitions; scripts use native schemas and a single armor-copy callback.
for name,row in items.items():
 if (ROOT/'overrides/client/kubejs/assets/kubejs/textures/item/progression'/(name+'.png')).exists():
  row['texture']='kubejs:item/progression/'+name
plan={'items':items,'recipes':recipes,'patches':patches,'remove':sorted(remove),'armor':armor,'paths':paths,'integration':integration}
assert len({r['id'] for r in recipes+armor})==len(recipes)+len(armor),'Duplicate generated recipe ID'
p=ROOT/'build/progression-plan.json';p.write_text(json.dumps(plan,ensure_ascii=False,indent=2),'utf-8')
startup="// Generated by tools/progression.py.\nStartupEvents.registry('item', event => {\n"
for name,row in items.items():startup+=f"  event.create({json.dumps(name)}).displayName({json.dumps(row['title'],ensure_ascii=False)}).texture({json.dumps(row['texture'])});\n"
startup+='});\n'
p=ROOT/'overrides/common/kubejs/startup_scripts/progression.js';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(startup,'utf-8')
js='// Generated data; armor callback is maintained separately.\nconst AI_PLAN = '+json.dumps(plan,ensure_ascii=False,separators=(',',':'))+';\n'
js+='''ServerEvents.recipes(event => {
  ['avaritia:infinity_catalyst','avaritia:infinity_catalyst_eternal'].forEach(id => event.remove({id:id}));
  AI_PLAN.remove.forEach(id => event.remove({output:id}));
  AI_PLAN.patches.forEach(r => {
    event.remove({id:r.id});
    let nativeRecipe = event.custom(r.json).id(r.id);
  });
  AI_PLAN.recipes.forEach(r => {
    let recipe = event.custom(r.json).id(r.id);
    if (r.copy_armor) recipe.modifyResult('arcane_armor');
  });
  AI_PLAN.armor.forEach(a => {
    function ingredient(x) { return typeof x === 'string' ? {item:x} : x; }
    let base = Array.isArray(a.base) ? a.base.map(ingredient) : ingredient(a.base);
    let output = {id:a.out,count:1};
    if (a.reinforce) output.components = {'minecraft:custom_data':{arcane_armor_tier:"t5"}};
    let key={C:{item:a.core},B:base,M:{item:a.material},P:{item:a.plate},L:{item:a.binding}};
    if (a.accent) key.X={item:a.accent};
    if (a.school) key.S={item:a.school};
    let pattern;
    if (a.large) pattern=a.accent_side === 'left' ?
      ['P   C   P',' P  S  P ','  L X L  ','   PMP   ','C X B X C','   PMP   ','  L X L  ',' P  S  P ','P   C   P'] :
      ['P   C   P',' P  X  P ','  L S L  ','   PMP   ','C X B X C','   PMP   ','  L S L  ',' P  X  P ','P   C   P'];
    else pattern=a.accent ? (a.accent_side === 'left' ? ['PCP','XBL','PMP'] : ['PCP','LBX','PMP']) : ['PCP','LBL','PMP'];
    let armorRecipe={type:a.large ? 'avaritia:shaped_table' : 'kubejs:shaped',pattern:pattern,key:key,result:output};
    if (a.large) armorRecipe.tier=4;
    event.custom(armorRecipe)
      .id(a.id).modifyResult(a.reinforce ? 'arcane_armor_t5' : 'arcane_armor');
  });
  console.info('[Arcane Progression] '+AI_PLAN.recipes.length+' new recipes, '+AI_PLAN.patches.length+' native patches, '+AI_PLAN.armor.length+' armor upgrades');
});
'''
p=ROOT/'overrides/common/kubejs/server_scripts/progression.js';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(js,'utf-8')
print('Generated',len(items),'items,',len(recipes),'recipes,',len(patches),'native patches and',len(armor),'armor upgrades.')
if '--skip-security' not in __import__('sys').argv and (ROOT/'tools/progression_security.py').exists() and (ROOT/'build/qol-recipe-patches.json').exists():
 from progression_security import generate
 generate()

