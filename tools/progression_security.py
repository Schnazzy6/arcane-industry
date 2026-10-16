"""Generate conservative craft-only progression rules without launching Minecraft.

Loot, trades and recipes use one protected-item set. Block loot and player death
are deliberately excluded. Preserve native ritual data and boss ingredients.
"""
import collections,copy,json,pathlib,shutil,zipfile
from catalog import ROOT

def outputs(r):
 out=set()
 for k in ['result','output','output_item','item_output','item_outputs','outputs']:
  v=r.get(k)
  for x in v if isinstance(v,list) else [v]:
   if isinstance(x,str) and ':' in x:out.add(x)
   elif isinstance(x,dict):
    s=x.get('id',x.get('item'))
    if isinstance(s,str) and ':' in s and x.get('#t','ae2:i')=='ae2:i':out.add(s)
 return out

def strings(v):
 if isinstance(v,str):yield v
 elif isinstance(v,dict):
  for x in v.values():yield from strings(x)
 elif isinstance(v,list):
  for x in v:yield from strings(x)

def generate():
 plan=json.loads((ROOT/'build/progression-plan.json').read_text('utf-8'))
 qol=json.loads((ROOT/'build/qol-recipe-patches.json').read_text('utf-8'))
 common=ROOT/'overrides/common/kubejs';data=common/'data'
 armor={a['out']:a['tier'] for a in plan['armor']}
 if (ROOT/'build/content-armor-tiers.json').exists():armor.update(json.loads((ROOT/'build/content-armor-tiers.json').read_text('utf-8')))
 guarded=set(plan['remove'])
 for p in plan['patches']+qol:
  # An unpacker returns an earlier hull as a byproduct. Guarding that hull
  # would remove its bootstrap recipes and create a circular progression.
  if 'kubejs:' in json.dumps(p['json']) and p['json'].get('type')!='modern_industrialization:unpacker':guarded.update(outputs(p['json']))
 guarded.update('kubejs:'+n for n in plan['items'])
 # Native Hephaestus rituals are data resources, not ordinary recipe-manager recipes.
 forge=json.loads((ROOT/'build/recipe-integration.json').read_text('utf-8'))['data_resources']
 forge_outputs=set()
 forbidden=next((ROOT/'build/server/mods').glob('forbidden_arcanus-*.jar'))
 with zipfile.ZipFile(forbidden) as z:
  for r in forge:
   for s in strings(json.loads(z.read(r['path']))):
    if s.startswith('forbidden_arcanus:') and s.split(':')[1]==r['name']:forge_outputs.add(s)
 guarded.update(forge_outputs)
 # Low tier affix loot remains useful as an upgrade base.
 gear_file=ROOT/'build/equipment-tiers.json'
 gear_tiers=json.loads(gear_file.read_text('utf-8')) if gear_file.exists() else {}
 equipment={**gear_tiers.get('armor',{}),**gear_tiers.get('tools',{})}
 creative_equipment={i for i in equipment if 'creative' in i}
 loot_guard=guarded-{i for i,t in equipment.items() if t<8}-{i for i,t in armor.items() if t==1}
 loot_guard.update(creative_equipment)
 allowed={r['id'] for r in plan['recipes']+plan['patches']+plan['armor']+qol}
 # Uncrafting stays unavailable even if a recipe is introduced by a later addon.
 guarded.add('twilightforest:uncrafting_table');loot_guard.add('twilightforest:uncrafting_table')
 source={};affix={};tags={};bosses=set()
 for jar in sorted((ROOT/'build/server/mods').glob('*.jar')):
  with zipfile.ZipFile(jar) as z:
   for path in z.namelist():
    if not path.startswith('data/') or not path.endswith('.json'):continue
    recipe='/recipe/' in path;is_affix=any(s in path for s in ['/affix_loot_entries/','/gear_sets/'])
    is_tag='/tags/entity_type/' in path
    if not (recipe or is_affix or is_tag):continue
    try:r=json.loads(z.read(path))
    except ValueError:continue
    if recipe:source[path.split('/')[1]+':'+path.split('/recipe/')[1][:-5]]=r
    if is_affix:affix[path]=r
    if is_tag:
     tid=path.split('/')[1]+':'+path.split('/tags/entity_type/')[1][:-5]
     tags.setdefault(tid,set()).update(v if isinstance(v,str) else v['id'] for v in r.get('values',[]))
 # Include vanilla recipes from the last real server snapshot; do not launch.
 snapshot=ROOT/'build/ritual-test/runtime-recipes.json'
 if snapshot.exists():
  for rid,r in json.loads(snapshot.read_text('utf-8')).items():source.setdefault(rid,r)
 # Respect existing common datapack overrides in the audit.
 for p in data.glob('*/recipe/**/*.json'):
  ns=p.relative_to(data).parts[0];source[ns+':'+p.relative_to(data/ns/'recipe').as_posix()[:-5]]=json.loads(p.read_text('utf-8'))
 for p in data.glob('*/affix_loot_entries/**/*.json'):
  affix['data/'+p.relative_to(data).as_posix()]=json.loads(p.read_text('utf-8'))
 for p in data.glob('*/gear_sets/**/*.json'):
  affix['data/'+p.relative_to(data).as_posix()]=json.loads(p.read_text('utf-8'))
 # Recolouring/resetting an existing item is not a second way to create it.
 # Only accept vanilla recipes requiring the exact same item and producing one.
 safe_identity=[]
 def self_required(r,item):
  if r.get('type') not in ['minecraft:crafting_shaped','minecraft:crafting_shapeless','minecraft:smithing_transform','ars_nouveau:dye']:return False
  if not isinstance(r.get('result'),dict) or r['result'].get('count',1)!=1:return False
  groups=[]
  if isinstance(r.get('key'),dict):groups=list(r['key'].values())
  elif isinstance(r.get('ingredients'),list):groups=r['ingredients']
  elif r.get('base'):groups=[r['base']]
  return any(isinstance(g,dict) and g.get('item')==item for g in groups)
 # Reversible block/part conversions must be guarded together, including loot
 # of the part; otherwise an ungated cable part can become a gated full block.
 pairs={}
 for rid,r in source.items():
  if r.get('type') not in ['minecraft:crafting_shaped','minecraft:crafting_shapeless']:continue
  if not isinstance(r.get('result'),dict) or r['result'].get('count',1)!=1:continue
  ins=r.get('ingredients')
  if r.get('key') is not None:
   ins=[r['key'][ch] for row in r['pattern'] for ch in row if ch!=' ']
  if not isinstance(ins,list) or len(ins)!=1 or not isinstance(ins[0],dict) or not isinstance(ins[0].get('item'),str):continue
  outs=outputs(r)
  if len(outs)==1:
   a=ins[0]['item'];b=next(iter(outs))
   if a!=b and a.split(':')[0]==b.split(':')[0]:pairs.setdefault((a,b),[]).append(rid)
 aliases=set()
 for (a,b),ids in pairs.items():
  if (b,a) in pairs and (a in guarded or b in guarded):
   aliases.update({a,b}-guarded);guarded.update([a,b]);loot_guard.update([a,b])
   allowed.update(ids+pairs[(b,a)])
 # Disassembly cannot create a hull out of nothing. Protect the assembled hatch
 # from loot too, while keeping its useful native dismantling recipe.
 safe_disassembly=[]
 for rid,r in source.items():
  if r.get('type')=='modern_industrialization:unpacker' and outputs(r)&guarded:
   ins=r.get('item_inputs',[])
   if len(ins)==1 and '_hatch' in ins[0].get('item',''):
    loot_guard.add(ins[0]['item']);allowed.add(rid);safe_disassembly.append(rid)
 for rid,r in source.items():
  hit=outputs(r)&guarded
  if hit and rid not in allowed and all(self_required(r,i) for i in hit):
   allowed.add(rid);safe_identity.append(rid)
 alternatives=[]
 for rid,r in source.items():
  hit=outputs(r)&guarded
  if hit and rid not in allowed:alternatives.append({'id':rid,'outputs':sorted(hit),'already_removed_by_output':hit.issubset(set(plan['remove']))})
 effective={rid:r for rid,r in source.items() if not outputs(r)&set(plan['remove'])}
 for row in plan['patches']+plan['recipes']+qol:effective[row['id']]=row['json']
 for row in plan['armor']:effective[row['id']]={'result':{'id':row['out']}}
 effective={rid:r for rid,r in effective.items() if not outputs(r)&guarded or rid in allowed}
 produced=set().union(*(outputs(r) for r in effective.values()))|forge_outputs
 missing_producers=sorted(guarded-produced-{'twilightforest:uncrafting_table'})
 disabled_affix=[]
 for path,r in affix.items():
  # Leave dangerous enemies equipped; final drop filters prevent taking their gear.
  if '/gear_sets/' in path or not (set(strings(r))&loot_guard):continue
  r=copy.deepcopy(r)
  cond={'type':'neoforge:false'}
  if cond not in r.setdefault('neoforge:conditions',[]):r['neoforge:conditions'].append(cond)
  dest=common/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf-8')
  disabled_affix.append(path)
 def tag(ns,kind,name,values):
  p=data/ns/'tags'/kind/(name+'.json');p.parent.mkdir(parents=True,exist_ok=True)
  # Preserve upstream values when supplying a blacklist; no replace=true.
  # Optional entries also preserve upstream optional cross-mod references.
  p.write_text(json.dumps({'replace':False,'values':[{'id':v,'required':False} for v in sorted(values)]},ensure_ascii=False,indent=2),'utf-8')
 tag('arcaneindustry','item','progression_craft_only',loot_guard)
 # Protect existing markers, altar materials and late gear from MI duplication.
 tag('modern_industrialization','item','replicator_blacklist',guarded)
 tag('arcaneindustry','entity_type','progression_bosses',{'#c:bosses','minecraft:ender_dragon','minecraft:wither','#twilightforest:bosses','#goety:bosses'})
 blacklist_tags=[('mob_grinding_utils',n) for n in ['no_swab','no_spawn','no_dirt_spawn','no_dreadful_spawn','no_delightful_spawn']]
 blacklist_tags += [('apothic_spawners','blacklisted_from_spawners'),('ars_additions','source_spawner_denylist'),('ars_nouveau','jar_blacklist'),('ars_nouveau','drygmy_blacklist'),('forbidden_arcanus','boss_catcher_blacklisted'),('supplementaries','capture_blacklist'),('c','capturing_not_supported')]
 for ns,name in blacklist_tags:
  existing=tags.get(ns+':'+name,set())
  tag(ns,'entity_type',name,existing|{'#arcaneindustry:progression_bosses'})
 # Explicit native IDs supplement the output filter for serializers without a KubeJS result reader.
 script='// Generated by tools/progression_security.py. Runs after progression and qol recipes.\n'
 if gear_file.exists():
  from quality_pass import gear_helper
  script+=gear_helper()
 script+='const AI_SEC_GUARDED = '+json.dumps(sorted(guarded))+';\n'
 script+='const AI_SEC_APPROVED = '+json.dumps(dict.fromkeys(sorted(allowed),True))+';\n'
 script+='const AI_SEC_DENIED_IDS = '+json.dumps([a['id'] for a in alternatives])+';\n'
 script+='const AI_SEC_LOOT_OUTPUTS = '+json.dumps(dict.fromkeys(sorted(loot_guard),True))+';\n'
 script+='''ServerEvents.recipes(event => {
  AI_SEC_DENIED_IDS.forEach(id => event.remove({id:id}));
  AI_SEC_GUARDED.forEach(item => {
    const denied = [];
    event.forEachRecipe({output:item}, recipe => {
      const id = String(recipe.getId());
      if (!AI_SEC_APPROVED[id] && !id.startsWith('kubejs:rework/')) denied.push(id);
    });
    denied.forEach(id => event.remove({id:id}));
  });
});
// These final-result modifiers run after NeoForge global loot modifiers.
// Block loot, commands, inventories and player death are outside this filter.
LootJS.modifiers(event => {
  // LootTypes are passed one by one (varargs); an array argument matched nothing, so the
  // old call never ran. Mob drops keep boss trophies (no tier cap).
  event.addTableModifier(LootType.CHEST,LootType.EQUIPMENT,
    LootType.FISHING,LootType.ARCHAEOLOGY,LootType.GIFT,LootType.VAULT,
    LootType.PIGLIN_BARTER,LootType.SHEARING)
    .removeLoot('#arcaneindustry:progression_craft_only')
    .customAction((context, bucket) => bucket.modifyItems(stack => aiCapEquipment(stack, context.getLevel().getServer())));
  event.addTableModifier(LootType.ENTITY).removeLoot('#arcaneindustry:progression_craft_only');
});
MoreJS.villagerTrades(event => event.removeTrades({output:'#arcaneindustry:progression_craft_only'}));
MoreJS.updateOffer(event => {
  if (AI_SEC_LOOT_OUTPUTS[String(event.offer.getResult().id)]) event.cancel();
});
'''
 (common/'server_scripts/zz_progression_security.js').write_text(script,'utf-8')
 # Native hooks run at LOWEST priority, covering gear added outside loot tables.
 native='// Generated by tools/progression_security.py. No inventory deletion or player-death filtering.\n'
 if gear_file.exists():native+=gear_helper()
 native+='const AI_SEC_LOOT_IDS = '+json.dumps(dict.fromkeys(sorted(loot_guard),True))+';\n'
 native+='''const AI_SEC_REG = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries');
const AI_SEC_PLAYER = Java.loadClass('net.minecraft.world.entity.player.Player');
const AI_SEC_TRADER = Java.loadClass('net.minecraft.world.entity.npc.AbstractVillager');
const AI_SEC_DC = Java.loadClass('net.minecraft.core.component.DataComponents');
function aiSecBlocked(stack) {
  return !stack.isEmpty() && AI_SEC_LOOT_IDS[String(AI_SEC_REG.ITEM.getKey(stack.getItem()))] === true;
}
function aiSecCrafted(stack) {
  const data = stack.get(AI_SEC_DC.CUSTOM_DATA);
  return data != null && data.copyTag().getBoolean('arcane_progression_crafted');
}
NativeEvents.onEvent(Java.loadClass('net.neoforged.bus.api.EventPriority').LOWEST,'net.neoforged.neoforge.event.entity.living.LivingDropsEvent',event => {
  if (event.getEntity() instanceof AI_SEC_PLAYER) return;
  event.getDrops().removeIf(drop => aiSecBlocked(drop.getItem()) && !aiSecCrafted(drop.getItem()));
  event.getDrops().forEach(drop => drop.setItem(aiCapEquipment(drop.getItem(),event.getEntity().getServer())));
});
// Sanitize offers already saved in old villagers when their trading UI is opened.
NativeEvents.onEvent('net.neoforged.neoforge.event.entity.player.PlayerInteractEvent$EntityInteract',event => {
  const target = event.getTarget();
  // Offers exist only on the server; reading them on the client crashes the game.
  if (event.getLevel().isClientSide()) return;
  if (target instanceof AI_SEC_TRADER) target.getOffers().removeIf(offer => aiSecBlocked(offer.getResult()));
});
'''
 (common/'startup_scripts/progression_security.js').write_text(native,'utf-8')
 from structure_security import harden
 structures=harden(loot_guard)
 report={'guarded_recipe_outputs':sorted(guarded),'craft_only_loot_items':sorted(loot_guard),'approved_recipe_ids':sorted(allowed),'protected_conversion_aliases':sorted(aliases),'safe_disassembly_recipes':safe_disassembly,'safe_identity_recipes':safe_identity,'removed_native_alternatives':alternatives,'disabled_affix_resources':disabled_affix,'boss_blacklist_tags':[ns+':'+n for ns,n in blacklist_tags],'missing_producers':missing_producers,'modified_structure_templates':len(structures['modified']), 'limits':['No client/server launch requested; hooks and recipes require runtime verification.','Already generated chest contents, chunks and player inventories are not deleted.','Future scripted quest rewards must respect the same progression.']}
 (ROOT/'build/progression-security.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
 import os
 for dest in [ROOT/'build/server',ROOT/'build/prism/Arcane Industry Prototype/minecraft',pathlib.Path(os.environ['APPDATA'])/'PrismLauncher/instances/ArcaneIndustry-0.1.4/minecraft']:
  shutil.copytree(common,dest/'kubejs',dirs_exist_ok=True)
 print('Security:',len(guarded),'guarded outputs;',len(alternatives),'native recipe alternatives;',len(disabled_affix),'affix resources;',len(blacklist_tags),'boss blacklist tags.')
 return report

if __name__=='__main__':generate()
