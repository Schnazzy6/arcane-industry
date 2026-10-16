"""Second expert pass requested in USER-TODO.md. Uses actual registry equipment."""
import copy,json,re,zipfile,collections

def apply(c):
 root=c['ROOT'];m=c['M'];tr='techreborn:';k='kubejs:';remove=c['remove'];recipes=c['recipes'];patches=c['patches'];armor=c['armor'];ing=c['ing']
 registry=json.loads((root/'build/gear-registry.json').read_text('utf-8'))
 # Extra late epochs distinguish master magic, nano technology and quantum equipment.
 c['part']('armor_core_t7','Квантовый каркас брони · T7','kubejs:item/progression/armor_core_t5')
 c['part']('armor_core_t8','Каркас бесконечности · T8','kubejs:item/progression/armor_core_t6')
 c['items']['armor_core_t6']['title']='Мастерский каркас брони · T6'
 recipes[:]=[r for r in recipes if r['id']!='kubejs:progression/armor_core_t6']
 def table(name,out,key,count=1):
  pattern=['PP     PP','P A B C P','  D E F  ',' G H I J ','  K L K  ',' G I H J ','  F E D  ','P C B A P','PP     PP']
  c['add'](name,{'type':'avaritia:shaped_table','tier':4,'pattern':pattern,'key':{ch:ing(value) for ch,value in key.items()},'result':{'id':out,'count':count}})
 table('armor_core_t6',k+'armor_core_t6',dict(P=m+'iridium_plate',A=k+'armor_core_t5',B=k+'engineering_matrix',C=k+'convergence_core',D=tr+'uu_matter',E=tr+'iridium_alloy_plate',F=tr+'industrial_circuit',G=k+'seal_life',H=k+'seal_mind',I=k+'seal_soul',J=k+'seal_elements',K=k+'boss_seal',L=k+'enchantment_lattice'),4)
 table('armor_core_t7',k+'armor_core_t7',dict(P=tr+'iridium_alloy_plate',A=k+'armor_core_t6',B=tr+'lapotronic_orb',C=k+'convergence_core',D=tr+'uu_matter',E=tr+'superconductor',F=tr+'data_storage_chip',G=k+'seal_life',H=k+'seal_mind',I=k+'seal_soul',J=k+'seal_elements',K=k+'boss_seal',L=k+'engineering_matrix'),4)
 table('armor_core_t8',k+'armor_core_t8',dict(P='avaritia:infinity_ingot',A=k+'armor_core_t7',B='avaritia:crystal_matrix_ingot',C=k+'infinity_stabilizer',D='avaritia:neutron_ingot',E=tr+'superconductor',F=tr+'data_storage_chip',G=k+'seal_life',H=k+'seal_mind',I=k+'seal_soul',J=k+'seal_elements',K=k+'boss_seal',L=k+'engineering_matrix'),4)
 slots={'head':'helmet','chest':'chestplate','legs':'leggings','feet':'boots'}
 tiers={a['out']:a['tier'] for a in armor}
 tiers.update(json.loads((root/'build/content-armor-tiers.json').read_text('utf-8')))
 # Known final families have explicit placement; unknown armor gets a conservative
 # defense/toughness classification, then a recipe in the same upgrade economy.
 def tier_of(row):
  item=row['id'];name=item.split(':')[1];ns=item.split(':')[0]
  if ns=='avaritia' and 'infinity' in name:return 8
  if (ns in ['modern_industrialization','extended_industrialization'] and any(s in name for s in ['quantum','nyano','gravi'])) or ns=='techreborn' and name.startswith('quantum_'):return 7
  if ns=='techreborn' and name.startswith('nano_'):return 6
  if ns=='advanced_ae' and 'quantum' in name:return 7
  if ns=='forbidden_arcanus' and name.startswith(('tyr_','draco_')):return 7
  if ns=='cataclysm' and name.startswith('cursium_'):return 7
  if item in tiers:return 6 if tiers[item]==5 else tiers[item]
  if ns=='minecraft' and name.startswith('leather_'):return 0
  if row['slot']=='body':return 3 if row['defense']>=10 else 1
  score=row['defense']/{'head':.15,'chest':.4,'legs':.3,'feet':.15}[row['slot']]
  t=0 if score<=8 else 1 if score<=12 else 2 if score<=16 else 3 if score<=21 else 4 if score<=28 else 5
  if row['toughness']>=6:t=max(t,6)
  elif row['toughness']>=4:t=max(t,5)
  elif row['toughness']>=3:t=max(t,4)
  if ns in ['goety','malum','eternal_starlight','ars_elemental','irons_spellbooks']:t=max(t,2)
  return min(t,7)
 tiers={row['id']:tier_of(row) for row in registry['armor']}
 itemdata={r['id']:r for r in registry['armor']}
 native_armor={out for row in patches for out in c['result_ids'](row['json']) if out in itemdata}
 native_armor.update('forbidden_arcanus:'+r['name'] for r in c['integration']['data_resources'] if 'forbidden_arcanus:'+r['name'] in itemdata)
 for row in patches:
  out=next((x for x in c['result_ids'](row['json']) if x in native_armor),None)
  if out and row['json'].get('type')=='minecraft:smithing_transform':row['json']['template']={'item':k+'armor_core_t'+str(tiers[out])}
 existing={a['out'] for a in armor}
 for a in armor:
  if a['out'] not in tiers:continue
  t=tiers[a['out']];a['tier']=t;a['core']=k+'armor_core_t'+str(max(t,1))
  a['plate']=m+('bronze_plate' if t<=1 else 'steel_plate' if t==2 else 'stainless_steel_plate' if t==3 else 'titanium_plate' if t<=5 else 'iridium_plate')
  if t==7:a['binding']=k+'infinity_stabilizer'
 canonical={0:'minecraft:leather_',1:'minecraft:chainmail_',2:'minecraft:iron_',3:'minecraft:diamond_',4:'minecraft:netherite_',5:'minecraft:netherite_',6:tr+'nano_',7:tr+'quantum_'}
 for row in registry['armor']:
  item=row['id'];t=tiers[item]
  if item in existing or item in native_armor or row['slot']=='body' or t<=1:continue
  slot=slots[row['slot']];base=canonical[t-1]+slot
  if base==item:base='minecraft:netherite_'+slot
  armor.append({'id':'kubejs:progression/armor/all_'+item.replace(':','_'),'out':item,'base':base,'core':k+'armor_core_t'+str(t),'material':k+'enchantment_lattice' if t>=5 else k+'industrial_focus' if t>=3 else k+'electrical_focus','plate':m+('iridium_plate' if t>=6 else 'titanium_plate' if t>=4 else 'stainless_steel_plate' if t>=3 else 'steel_plate'),'binding':k+'infinity_stabilizer' if t>=7 else k+'convergence_core' if t>=6 else k+'ritual_frame' if t>=4 else k+'industrial_focus' if t>=3 else k+'electrical_focus','tier':t,'reinforce':False});remove.add(item)
 # MI's final equipment returns to the pre-Infinity economy and needs TR gear.
 for slot in c['slots']:
  out=m+'quantum_'+slot;remove.add(out)
  recipes[:]=[r for r in recipes if r['id']!='kubejs:progression/mi_quantum_'+slot]
  if out not in {a['out'] for a in armor}:raise RuntimeError('Missing MI armor '+out)
 # The finale is an AND of major final sets, never an OR of interchangeable bases.
 final_manifest={}
 for slot in c['slots']:
  old=next(a for a in armor if a['out']=='avaritia:infinity_'+('pants' if slot=='leggings' else slot))
  index=c['slots'].index(slot)
  # Two final sets: MI Quantum (tech, left) and the mage path finale (magic, right),
  # each flanked by its own branch's endgame components.
  tech_set=m+'quantum_'+slot;magic_set=c['paths']['mage'][5][index]
  final_manifest[slot]=[tech_set,magic_set]
  key={x:ing(v) for x,v in dict(A=tech_set,B=magic_set,C=k+'armor_core_t8',S=k+'infinity_stabilizer',
    X='avaritia:infinity_catalyst',I='avaritia:infinity_ingot',N='avaritia:neutron_ingot',M='avaritia:crystal_matrix_ingot',
    P=tr+'superconductor',O=tr+'lapotronic_orb',U=tr+'uu_matter',D=tr+'data_storage_chip',Q=m+'quantum_upgrade',E=k+'engineering_matrix',
    L=k+'seal_life',H=k+'seal_mind',V=k+'seal_soul',W=k+'seal_elements',Z=k+'enchantment_lattice',K=k+'boss_seal').items()}
  # Corners must stay filled: Avaritia trims empty edges and then indexes the
  # trimmed grid out of bounds, so JEI drops the recipe.
  pattern=['IM  X  MI','MPO   LHM',' DU   VW ','  Q   Z  ','X EACBK X','  Q   Z  ',' DU   VW ','NPO   LHN','IN  S  NI']
  c['add']('armor/infinity_'+slot,{'type':'avaritia:shaped_table','tier':4,'pattern':pattern,'key':key,'result':{'id':old['out'],'count':1}})
  recipes[-1]['copy_armor']=True
 armor[:]=[a for a in armor if not a['out'].startswith('avaritia:infinity_')]
 # Circuits need MI chemistry. These run before UU and remain independent of it.
 for r in recipes:
  if r['id'].split('/')[-1] in ['tr_electronic_circuit','tr_advanced_circuit','tr_industrial_circuit','tr_data_storage_chip']:
   r['json']['fluid_inputs']=[{'fluid':m+'soldering_alloy','amount':144 if 'data_storage' in r['id'] else 72}]
  elif r['id'].split('/')[-1] in ['tr_advanced_alloy_ingot','tr_iridium_alloy_ingot']:
   r['json']['fluid_inputs']=[{'fluid':m+'nitrogen','amount':250}]
 # MI and TR both supply a late quantum upgrade, with no circular first circuit.
 remove.add(m+'quantum_upgrade')
 table('mi_quantum_upgrade',m+'quantum_upgrade',dict(P=m+'iridium_plate',A=tr+'data_storage_chip',B=tr+'superconductor',C=tr+'uu_matter',D=k+'seal_life',E=k+'seal_mind',F=k+'seal_soul',G=k+'seal_elements',H=k+'engineering_matrix',I=k+'convergence_core',J=tr+'lapotronic_orb',K=k+'boss_seal',L=k+'ritual_frame'))
 # AE2's three processors remain pre-Reborn to avoid a matrix/interface cycle.
 for name in ['logic','calculation','engineering']:
  out='ae2:'+name+'_processor';remove.add(out)
  c['machine']('ae2_'+name+'_processor',out,[('ae2:printed_'+name+'_processor',2),('ae2:printed_silicon',2),(m+'digital_circuit',1),(k+'industrial_focus',1)],2,16,300)
  recipes[-1]['json']['fluid_inputs']=[{'fluid':m+'soldering_alloy','amount':72}]
 # Tool tiers are independent of requiring a manual wood->stone upgrade ladder.
 tool_tiers={}
 for row in registry['tools']:
  item=row['id'];name=item.split(':')[1];ns=item.split(':')[0]
  t=8 if ns=='avaritia' and 'infinity' in name else 7 if any(x in name for x in ['quantum','omni_tool','supremium','awakened']) else 6 if any(x in name for x in ['nano','ignitium','cursium','soul_stained','tyr_','draco_']) else 5 if any(x in name for x in ['aeternium','industrial_','imperium','runic_']) else 4 if any(x in name for x in ['netherite','terminite','advanced_']) else 3 if any(x in name for x in ['diamond','steel','tertium']) else 2 if any(x in name for x in ['iron','prudentium']) else 1 if any(x in name for x in ['bronze','copper','stone','gold']) else 2 if ns!='minecraft' else 0
  if ns=='simplyswords' and not any(name.startswith(p+'_') for p in ['wooden','stone','iron','gold','diamond','netherite','runic']):t=6
  if ns=='cataclysm':t=3 if 'black_steel' in name else 7
  if 'creative' in name:t=8
  if item in ['minecraft:mace','minecraft:trident','minecraft:elytra']:t=4
  tool_tiers[item]=t
 # Runic Simply Swords weapons otherwise skip the late-tool gate: their
 # native smithing recipes ask for only a tablet and one diamond.
 with zipfile.ZipFile(next((root/'build/server/mods').glob('SimplySwords-*.jar'))) as jar:
  for path in jar.namelist():
   if not path.startswith('data/simplyswords/recipe/runic_') or not path.endswith('.json'):continue
   original=json.loads(jar.read(path))
   if original.get('type')!='minecraft:smithing_transform':continue
   out=original.get('result',{}).get('id','')
   if tool_tiers.get(out,0)<5:continue
   revised=copy.deepcopy(original)
   revised['addition']=ing(k+'armor_core_t5')
   patches.append({'id':'simplyswords:'+path.split('/recipe/')[1][:-5],'json':revised})
 # The last weapon inherits its own weapon class; a bow never consumes a drill
 # and a tool never consumes a sword merely to make the grid look complex.
 for row in registry['tools']:
  item=row['id'];name=item.split(':')[1]
  if not (item.startswith('avaritia:infinity_') and tool_tiers[item]==8):continue
  kind=name.removeprefix('infinity_')
  if kind not in ['sword','pickaxe','shovel','axe','hoe','bow','crossbow']:continue
  remove.add(item)
  predecessor='avaritia:crystal_'+kind if kind!='crossbow' else 'minecraft:crossbow'
  branch={'sword':m+'quantum_sword','pickaxe':tr+'omni_tool',
          'shovel':tr+'iridium_alloy_plate','axe':tr+'superconductor',
          'hoe':k+'seal_life','bow':k+'seal_elements',
          'crossbow':tr+'data_storage_chip'}[kind]
  table('tool_'+name,item,dict(P='avaritia:infinity_ingot',A=predecessor,B=branch,C=k+'armor_core_t8',D=k+'seal_life',E=k+'seal_mind',F=k+'seal_soul',G=k+'seal_elements',H=k+'boss_seal',I=k+'engineering_matrix',J='avaritia:infinity_catalyst',K=k+'infinity_stabilizer',L='avaritia:neutron_ingot'))
 # The native Infinity Totem is a cheap extreme-smithing path to a final item.
 remove.add('avaritia:infinity_totem')
 table('infinity_totem','avaritia:infinity_totem',dict(P='avaritia:infinity_ingot',A='minecraft:totem_of_undying',B=k+'armor_core_t8',C='avaritia:infinity_catalyst',D=k+'seal_life',E=k+'seal_mind',F=k+'seal_soul',G=k+'seal_elements',H=k+'boss_seal',I=k+'engineering_matrix',J=k+'infinity_stabilizer',K='minecraft:beacon',L='avaritia:neutron_ingot'))
 # High native tech tools now require a real previous tool; early tools stay native.
 for out,base,gate in [(tr+'omni_tool',tr+'industrial_drill',k+'armor_core_t7'),(tr+'nanosaber','minecraft:netherite_sword',k+'armor_core_t6')]:
  recipes[:]=[r for r in recipes if out not in c['result_ids'](r['json'])];remove.add(out)
  table('tool_upgrade_'+out.split(':')[1],out,dict(P=m+'iridium_plate',A=base,B=tr+'industrial_circuit',C=gate,D=k+'seal_life',E=k+'seal_mind',F=k+'seal_soul',G=k+'seal_elements',H=k+'engineering_matrix',I=tr+'iridium_alloy_plate',J=tr+'energy_crystal',K=k+'boss_seal',L=k+'convergence_core'))
 # Other craftable late tools retain their native ingredients inside a 9x9
 # upgrade. Unique boss-only loot stays a reward, not a cheaply replicated craft.
 source={}
 active=set(json.loads((root/'tools/data/progression-active-recipes.json').read_text('utf-8')))
 for jar_path in sorted((root/'build/server/mods').glob('*.jar')):
  with zipfile.ZipFile(jar_path) as jar:
   for path in jar.namelist():
    if not path.startswith('data/') or '/recipe/' not in path or not path.endswith('.json'):continue
    rid=path.split('/')[1]+':'+path.split('/recipe/')[1][:-5]
    if rid not in active:continue
    original=json.loads(jar.read(path))
    if original.get('type')=='minecraft:crafting_shaped':source[rid]=original
 source.update({r['id']:r['json'] for r in patches})
 done=set()
 for rid,r in list(source.items()):
  if rid.startswith('kubejs:') or r.get('type')!='minecraft:crafting_shaped':continue
  out=next((x for x in c['result_ids'](r) if tool_tiers.get(x,0)>=5),None)
  if not out or out in done or out.startswith('avaritia:') or out in [tr+'omni_tool',tr+'nanosaber']:continue
  name=out.split(':')[1];ns=out.split(':')[0];t=tool_tiers[out]
  if name=='infusion_crystal':continue  # Crafting catalyst, not held equipment.
  kind=next((x for x in ['pickaxe','shovel','crossbow','bow','axe','hoe','sword'] if x in name),None)
  if kind is None:
   kind='hoe' if any(x in name for x in ['sickle','scythe']) else 'pickaxe' if any(x in name for x in ['paxel','drill']) else 'crossbow' if 'gatling' in name else 'trident' if 'spear' in name else 'shield' if 'shield' in name else 'sword'
  possible=[out.replace('industrial_','advanced_'),out.replace('runic_','diamond_'),out.replace('quantum_','nano_'),
            out.replace('awakened_supremium_','supremium_'),out.replace('supremium_','imperium_'),out.replace('imperium_','tertium_')]
  fallback='minecraft:'+kind if kind in ['bow','crossbow','trident','shield'] else 'minecraft:netherite_'+kind
  base=next((x for x in possible if x!=out and x in tool_tiers and tool_tiers[x]<t),fallback)
  if base not in tool_tiers:base=fallback
  symbols={ch:str(i) for i,ch in enumerate(r['key'])};pattern=['    U    ','  P   P  ','    C    ']
  pattern+=['   '+''.join(symbols.get(ch,' ') for ch in row).ljust(3)+'   ' for row in r['pattern']]
  while len(pattern)<6:pattern.append('         ')
  pattern+=['    G    ','  P   P  ','    C    ']
  key={symbols[ch]:v for ch,v in r['key'].items()};key.update(U=ing(base),P=ing(m+'titanium_plate' if t<=5 else m+'iridium_plate'),C=ing(k+'armor_core_t'+str(t)),G=ing(k+'convergence_core'))
  recipes[:]=[x for x in recipes if out not in c['result_ids'](x['json'])];patches[:]=[x for x in patches if out not in c['result_ids'](x['json'])]
  remove.add(out);c['add']('late_tool/'+out.replace(':','/'),{'type':'avaritia:shaped_table','tier':4,'pattern':pattern,'key':key,'result':copy.deepcopy(r['result'])});recipes[-1]['copy_armor']=True;done.add(out)
 # A quantum sword is a late predecessor, not an Infinity-ingot shortcut.
 out=m+'quantum_sword';recipes[:]=[r for r in recipes if out not in c['result_ids'](r['json'])];remove.add(out)
 table('mi_quantum_sword',out,dict(P=m+'iridium_plate',A=tr+'nanosaber',B=m+'quantum_upgrade',C=k+'armor_core_t7',D=k+'seal_life',E=k+'seal_mind',F=k+'seal_soul',G=k+'seal_elements',H=k+'engineering_matrix',I=tr+'superconductor',J=tr+'uu_matter',K=k+'boss_seal',L=k+'infinity_stabilizer'))
 recipes[-1]['copy_armor']=True
 # Armor from different mods often has the same five generic ingredients.
 # Add one visible textile accent and rotate its position for each competing
 # design. The required base armor and the tier core remain unchanged.
 dyes=['white','orange','magenta','light_blue','yellow','lime','pink','gray',
       'light_gray','cyan','purple','blue','brown','green','red','black']
 groups=collections.defaultdict(list)
 for a in armor:
  signature=json.dumps([a['base'],a['core'],a['material'],a['plate'],a['binding']],sort_keys=True)
  groups[signature].append(a)
 for group in groups.values():
  if len(group)<2:continue
  for i,a in enumerate(sorted(group,key=lambda row:row['out'])):
   a['accent']='minecraft:'+dyes[i%len(dyes)]+'_dye'
   a['accent_side']='right' if i<len(dyes) else 'left'
   item=a['out']
   if item.startswith('samurai_dynasty:light_samurai_'):
    a['accent']='samurai_dynasty:jade'
   elif item.startswith('immersive_armors:robe_'):
    a['accent']='ars_nouveau:magebloom_fiber'
   elif item.startswith('ars_elemancy:'):
    name=item.split(':')[1];element=name.split('_')[0]
    if element in ['cinder','tempest','vapor','mire','lava','silt']:
     heavy=any(name.endswith(x) for x in ['helmet','chestplate','leggings_heavy','boots_heavy'])
     light=any(name.endswith(x) for x in ['hood','tunic','pants','shoes'])
     a['accent']='ars_elemancy:'+element+('_focus' if heavy else '_essence')
     a['accent_side']='left' if light else 'right'
 # Master and quantum armor receive a distinct nine-slot-wide assembly.
 # The school seal keeps these sets tied to their source branch.
 for a in armor:
  if a['tier']<6:continue
  a.setdefault('accent','minecraft:'+dyes[sum(map(ord,a['out']))%len(dyes)]+'_dye')
  ns=a['out'].split(':')[0]
  a['school']=k+('engineering_matrix' if ns in ['modern_industrialization','extended_industrialization','techreborn','advanced_ae'] else 'boss_seal' if ns in ['samurai_dynasty','cataclysm'] else 'seal_elements')
  a['large']=True
 c['equipment_tiers']={'armor':tiers,'tools':tool_tiers,'finale_required_sets':final_manifest}
 (root/'build/equipment-tiers.json').write_text(json.dumps(c['equipment_tiers'],ensure_ascii=False,indent=2),'utf-8')
 # Keep changed recipe output filtering and loot guards on the same tier map.
 (root/'build/content-armor-tiers.json').write_text(json.dumps(tiers,indent=2),'utf-8')
 tooltip="// Generated equipment epochs. Early tools retain their ordinary recipes.\nItemEvents.modifyTooltips(event => {\n"
 names=['Начало','Бронзовый век','Электричество','Промышленность','Ритуальные сплавы','Высшая промышленность','Мастерство школ','Квантовая эпоха','Бесконечность']
 for t,label in enumerate(names):
  ids=sorted({item for item,tier in {**tiers,**tool_tiers}.items() if tier==t})
  tooltip+='  event.add('+json.dumps(ids)+', [Text.of('+json.dumps('§8Тир '+str(t)+' · '+label,ensure_ascii=False)+')]);\n'
 tooltip+='});\n'
 (root/'overrides/common/kubejs/server_scripts/equipment_tiers.js').write_text(tooltip,'utf-8')
