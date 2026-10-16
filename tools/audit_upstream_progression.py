"""Conservative item/station reachability using the live server recipe snapshot.

World drops and unmodelled native mechanics are explicit external assumptions.
This is not a complete simulation of chemistry, energy, dimensions or mining tiers.
"""
import json,collections,pathlib,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1];DIR=ROOT/'build/ritual-test'
recipes=json.loads((DIR/'runtime-recipes.json').read_text('utf-8'))
tags=json.loads((DIR/'runtime-tags.json').read_text('utf-8'))
plan=json.loads((ROOT/'build/progression-plan.json').read_text('utf-8'))
custom={'kubejs:'+n for n in plan['items']}
def alternatives(x):
 if isinstance(x,list):return set().union(*(alternatives(v) for v in x))
 if not isinstance(x,dict):return set()
 if x.get('type')=='apotheosis:spawn_egg':return {'native:captured_spawn_egg'}
 if x.get('type')=='apotheosis:gem':return {'native:perfect_apotheosis_gem'}
 if 'items' in x:
  v=x['items'];return {v} if isinstance(v,str) else set(v)
 if 'item' in x:return {x['item']} if isinstance(x['item'],str) else alternatives(x['item'])
 if 'tag' in x:return set(tags.get(x['tag'],[]))
 if 'ingredient' in x:return alternatives(x['ingredient'])
 if 'id' in x and x.get('#t','ae2:i')=='ae2:i':return {x['id']}
 return set()
def groups(x):
 if isinstance(x,list):return [alternatives(v) for v in x]
 if isinstance(x,dict):
  if any(k in x for k in ['item','tag','ingredient','id']):return [alternatives(x)]
  return [alternatives(v) for v in x.values()]
 return []
def outputs(r):
 out=set()
 for key in ['result','output','output_item','item_output','item_outputs']:
  x=r.get(key)
  if isinstance(x,str):out.add(x)
  elif isinstance(x,list):
   for v in x:
    if isinstance(v,dict):
     val=v.get('id',v.get('item'))
     if isinstance(val,str):out.add(val)
  elif isinstance(x,dict):
   if '#t' in x and x['#t']!='ae2:i':continue
   val=x.get('id',x.get('item'))
   if isinstance(val,str):out.add(val)
 return out-{None,'minecraft:air'}
stations={
 'ars_nouveau:enchanting_apparatus':[['ars_nouveau:enchanting_apparatus'],['ars_nouveau:arcane_core'],['ars_nouveau:arcane_pedestal'],['ars_nouveau:source_jar']],
 'ars_nouveau:imbuement':[['ars_nouveau:imbuement_chamber']],
 'malum:spirit_infusion':[['malum:spirit_altar'],['malum:runewood_item_stand']],
 'naturesaura:tree_ritual':[['naturesaura:wood_stand'],['naturesaura:gold_powder']],
 'naturesaura:altar':[['naturesaura:nature_altar']],
 'eidolon_repraised:crucible':[['eidolon_repraised:crucible']],
 'eidolon_repraised:worktable':[['eidolon_repraised:worktable']],
 'occultism:ritual':[['occultism:golden_sacrificial_bowl'],['occultism:chalk_purple'],['occultism:sacrificial_bowl']],
 'goety:ritual':[['goety:dark_altar'],['goety:cursed_cage'],['goety:totem_of_souls'],['goety:pedestal']],
 'evilcraft:blood_infuser':[['evilcraft:blood_infuser']],
 'avaritia:shaped_table':[['avaritia:extreme_crafting_table']],
 'avaritia:shapeless_table':[['avaritia:extreme_crafting_table']],
 'avaritia:compressor':[['avaritia:neutron_compressor']],
 'ae2:inscriber':[['ae2:inscriber']],
 'advanced_ae:reaction':[['advanced_ae:reaction_chamber']],
 'extendedae:crystal_assembler':[['extendedae:crystal_assembler']],
 'extendedae:circuit_cutter':[['extendedae:circuit_cutter']],
}
parsed=[];produced=set();all_items=set();unmodelled=[]
for rid,r in recipes.items():
 if rid in ['mekanism:processing/lategame/polonium_pellet/from_reaction','mekanism:processing/lategame/plutonium_pellet/from_reaction','mekanism:processing/lategame/antimatter_pellet/from_gas']:continue
 out=outputs(r)
 if not out:continue
 req=[]
 for key in ['ingredients','ingredient','input','item_inputs','item_input','input_items','input_item','reagent','pedestalItems','extraInputs','activation_item','sapling','focus_items','pedestal_items','template','base','addition']:
  if key in r:req.extend(groups(r[key]))
 if 'key' in r:req.extend(groups(r['key']))
 if 'steps' in r:
  for step in r['steps']:req.extend(groups(step.get('items',[])))
 typ=r.get('type','');req.extend(set(g) for g in stations.get(typ,[]))
 if typ.startswith('modern_industrialization:'):
  machine=typ.split(':')[1]
  req.append({'modern_industrialization:'+n+machine for n in ['', 'bronze_', 'steel_']})
 if not req:unmodelled.append(rid);continue
 parsed.append((rid,out,req));produced.update(out);all_items.update(out)
 for g in req:all_items.update(g)
# Native items with no encoded production are external drops/world mechanics.
# Common natural resources also have recipes (recycling/transmutation), so seed
# those explicitly instead of incorrectly turning such loops into hard gates.
external=all_items-produced-custom
external.difference_update({'mekanism:pellet_polonium','mekanism:pellet_plutonium','mekanism:pellet_antimatter','avaritia:neutron_pile','avaritia:singularity'})
world=set()
for tag,values in tags.items():
 if tag in ['c:ores','minecraft:logs','minecraft:leaves','minecraft:flowers','minecraft:saplings','c:raw_materials']:
  world.update(values)
world.update('minecraft:'+s for s in ['stone','cobblestone','dirt','sand','gravel','clay_ball','flint','coal','charcoal','iron_ingot','gold_ingot','copper_ingot','diamond','emerald','lapis_lazuli','redstone','quartz','amethyst_shard','amethyst_block','obsidian','glowstone_dust','netherite_scrap','ancient_debris','ender_pearl','blaze_rod','blaze_powder','ghast_tear','slime_ball','magma_cream','nether_star','echo_shard','bone','rotten_flesh','leather','string','feather','ink_sac','glow_ink_sac','gunpowder','honey_bottle','wheat','potato','carrot','beetroot','sugar_cane','wheat_seeds','pumpkin','melon_slice','apple','brown_mushroom','red_mushroom','kelp','egg','milk_bucket','water_bucket','lava_bucket','snowball','prismarine_shard','prismarine_crystals','nautilus_shell','heart_of_the_sea','soul_sand','soul_soil','netherrack','end_stone','dragon_breath','dragon_egg','shulker_shell','nether_wart','cocoa_beans','sweet_berries','bamboo','cactus','lily_pad','vine','rabbit_hide','rabbit_foot','turtle_scute','armadillo_scute','porkchop','beef','chicken','mutton','rabbit','cod','salmon','pufferfish','tropical_fish'])
world.update(['minecraft:chorus_fruit','evilcraft:dark_gem','minecraft:spider_eye','minecraft:wither_skeleton_skull','ars_nouveau:wilden_horn','ars_nouveau:starbuncle_shards',
 'ars_nouveau:source_gem','ars_nouveau:magebloom','irons_spellbooks:arcane_essence','irons_spellbooks:cinder_essence','irons_spellbooks:common_ink',
 'theurgy:mercury_shard','eidolon_repraised:soul_shard','malum:arcane_spirit','malum:aerial_spirit','malum:wicked_spirit','malum:earthen_spirit',
 'twilightforest:naga_scale','twilightforest:fiery_blood','mowziesmobs:naga_fang','born_in_chaos_v1:dark_metal_ingot','simplyswords:runic_tablet','artifacts:umbrella',
 'eternal_starlight:thioquartz_shard','cataclysm:ignitium_ingot','eternal_starlight:amaramber_ingot',
 'ae2:logic_processor_press','ae2:engineering_processor_press','ae2:calculation_processor_press','ae2:silicon_press',
 'ae2:charged_certus_quartz_crystal','ae2:certus_quartz_crystal','ae2:sky_stone_block'])
# Verify additional exploration materials against this installed pack's loot.
loot_needed={'cataclysm:cursium_ingot','forbidden_arcanus:stellarite_piece','goety:shadow_essence',
 'twilightforest:arctic_fur','twilightforest:steeleaf_ingot','irons_spellbooks:blank_rune','minecraft:elytra','minecraft:skeleton_skull'}
loot_sources={x:[] for x in loot_needed}
for jar in (ROOT/'build/server/mods').glob('*.jar'):
 with zipfile.ZipFile(jar) as z:
  for path in z.namelist():
   if '/loot_table/' not in path or not path.endswith('.json'):continue
   text=z.read(path).decode('utf-8')
   for item in loot_needed:
    if item in text:loot_sources[item].append(jar.name+'!'+path)
assert all(loot_sources.values()),'A presumed exploration material has no installed loot source'
world.update(loot_needed)
(DIR/'material-loot-sources.json').write_text(json.dumps(loot_sources,indent=2),'utf-8')
# These native right-click transformations are not RecipeManager recipes.
parsed.extend([
 ('native_interaction:naturesaura/bottle_aura',{'naturesaura:aura_bottle'},[{'naturesaura:bottle_two_the_rebottling'}]),
 ('native_interaction:occultism/name_foliot',{'occultism:book_of_binding_bound_foliot'},[{'occultism:book_of_binding_foliot'},{'minecraft:book'}]),
 ('native_interaction:occultism/name_djinni',{'occultism:book_of_binding_bound_djinni'},[{'occultism:book_of_binding_djinni'},{'minecraft:book'}]),
 ('native_interaction:occultism/name_marid',{'occultism:book_of_binding_bound_marid'},[{'occultism:book_of_binding_marid'},{'minecraft:book'}]),
 ('native_interaction:evilcraft/dark_gem_in_five_blood_sources',{'evilcraft:dark_power_gem'},[{'evilcraft:dark_gem'},{'evilcraft:blood_extractor'},{'minecraft:bucket'}]),
 ('native_process:avaritia/neutron_collector',{'avaritia:neutron_pile'},[{'avaritia:neutron_collector'}]),
 ('native_process:avaritia/singularities',{'avaritia:singularity'},[{'avaritia:neutron_compressor'}]+[set(tags.get('c:ingots/'+x,[])) for x in ['iron','copper','gold','tin','lead','silver','nickel','bronze']]),
 ('native_process:apotheosis/capturing',{'native:captured_spawn_egg'},[{'minecraft:enchanting_table'},{'minecraft:diamond_sword'}]),
 ('native_process:apotheosis/perfect_gem',{'native:perfect_apotheosis_gem'},[{'apotheosis:gem_cutting_table'},{'apotheosis:gem'},{'mekanism:pellet_antimatter'}]),
 ('native_process:mekanism/lithium_towers',{'mekanism:dust_lithium'},[{x} for x in ['mekanism:thermal_evaporation_controller',
     'mekanism:thermal_evaporation_block','mekanism:thermal_evaporation_valve','mekanism:rotary_condensentrator','mekanism:chemical_crystallizer','minecraft:water_bucket']]),
])
# Nuclear chemistry is a named native-process abstraction: require all principal
# machines rather than accidentally treating pellets as uncrafted world drops.
# Fluid ratios, waste, reactor heat and SPS power are not simulated by this audit.
reactor=['mekanismgenerators:fission_reactor_casing','mekanismgenerators:fission_reactor_port',
 'mekanismgenerators:fission_fuel_assembly','mekanismgenerators:control_rod_assembly',
 'mekanism:chemical_oxidizer','mekanism:chemical_dissolution_chamber','mekanism:chemical_infuser',
 'mekanism:isotopic_centrifuge','mekanism:pressurized_reaction_chamber',
 'modern_industrialization:uranium_ingot','mekanism:dust_fluorite']
for pellet,machine in [('polonium','solar_neutron_activator'),('plutonium','isotopic_centrifuge')]:
 parsed.append(('native_process:mekanism/fission_to_'+pellet,{'mekanism:pellet_'+pellet},[{x} for x in reactor+['mekanism:'+machine]]))
parsed.append(('native_process:mekanism/polonium_sps_crystallizer',{'mekanism:pellet_antimatter'},
 [{x} for x in ['mekanism:pellet_polonium','mekanism:sps_casing','mekanism:sps_port','mekanism:supercharged_coil','mekanism:chemical_crystallizer']]))
known=external|world;proof={};rounds=0
while True:
 rounds+=1;added=0
 for rid,out,req in parsed:
  if out<=known or not all(g&known for g in req):continue
  for item in out-known:proof[item]={'recipe':rid,'inputs':[sorted(g&known)[0] for g in req],'round':rounds};added+=1
  known.update(out)
 if not added:break
targets=custom|{s for gl in stations.values() for g in gl for s in g}
targets.update(a['out'] for a in plan['armor'])
targets.update(r['out'] for r in plan.get('integration',{}).get('recipes',[]))
for r in plan['recipes']:targets.update(outputs(r['json']))
blocked=sorted(targets-known)
producers=collections.defaultdict(list)
for rid,out,req in parsed:
 for x in out:producers[x].append((rid,req))
diagnostic={}
for x in blocked:
 diagnostic[x]=[{'recipe':rid,'missing':[sorted(g) for g in req if not g&known]} for rid,req in producers[x]][:8]
report={'rounds':rounds,'modeled_recipes':len(parsed),'target_count':len(targets),'external_assumptions':sorted(external),'world_assumptions':sorted(world),
 'unmodelled_output_recipes':unmodelled,'blocked_targets':blocked,'diagnostic':diagnostic,'proof':proof,
 'limits':'Item and workstation reachability only. External native mechanics/drops assumed; fluids, energy, dimensions, mining tiers and quantities not simulated.'}
(DIR/'upstream-reachability.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
print('Modeled recipes:',len(parsed),'rounds:',rounds,'blocked targets:',len(blocked))
for x in blocked:print(x,json.dumps(diagnostic[x],ensure_ascii=False)[:1600])
if blocked:raise SystemExit(1)
