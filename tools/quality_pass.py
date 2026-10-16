"""Era-aware loot and gameplay defaults requested in USER-TODO.md."""
import json,zipfile,pathlib
from catalog import ROOT

def gear_helper():
 # Gear tier scale I-XII (GEAR-TIERS.md, tools/build_gear_tiers.js); keep in sync with the
 # deployed progression_security.js files.
 return '''// Gear tier scale I-XII from kubejs/config/gear-tiers.json (GEAR-TIERS.md). Only the
// findable range I-VII is capped, by technology era (start III ... quantum circuits VII)
// plus one tier of slack for mob drops and other loot; VIII+ (boss trophies, craft-only
// gear) is never touched here. Chest loot has its own, stricter filter in gear_loot.js.
const AI_CAP = JSON.parse(String(JsonIO.readString('kubejs/config/gear-tiers.json')));
const AI_CAP_REG = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries');
const AI_CAP_COMPONENTS = Java.loadClass('net.minecraft.core.component.DataComponents');
const AI_CAP_ERA = [3, 4, 5, 6, 7];
function aiCapEquipment(stack, server) {
  if (stack.isEmpty() || server == null) return stack;
  let id = String(AI_CAP_REG.ITEM.getKey(stack.getItem()));
  let tier = AI_CAP.tiers[id];
  if (tier === undefined || tier > 7) return stack;
  let era = server.persistentData.getInt('arcane_era');
  let limit = Math.min(7, AI_CAP_ERA[Math.min(era, AI_CAP_ERA.length - 1)] + 1);
  return tier <= limit ? stack : Item.empty;
}
'''

def configure():
 common=ROOT/'overrides/common';data=common/'kubejs/data';cfg=common/'config';cfg.mkdir(parents=True,exist_ok=True)
 base=ROOT/'build/techreborn-verification/server/config'
 text=(base/'ftbultimine-server.snbt').read_text('utf-8')
 for old,new in [('max_blocks: 64','max_blocks: 16'),('max_blocks: 8','max_blocks: 16'),('require_tool: false','require_tool: true'),('require_valid_tool_for_block: false','require_valid_tool_for_block: true'),('ultimine_cooldown: 0L','ultimine_cooldown: 10L'),('exhaustion_per_block: 20.0d','exhaustion_per_block: 0.6d'),('prevent_tool_break: 0','prevent_tool_break: 1')]:text=text.replace(old,new)
 (cfg/'ftbultimine-server.snbt').write_text(text,'utf-8')
 stages={'modern_industrialization:steel_ingot':1,'modern_industrialization:analog_circuit':2,'modern_industrialization:processing_unit':3,'modern_industrialization:quantum_circuit':4,'kubejs:reborn_interface':5,'kubejs:convergence_core':6,'kubejs:infinity_stabilizer':7,'avaritia:infinity_ingot':8}
 stagejs='const AI_ERA_ITEMS = '+json.dumps(stages)+';\n'
 stagejs+='''// Retain era tracking for loot gates. Clear any Ultimine attribute saved by
// older pack versions so the fixed config limit applies to existing players.
const AI_ULTIMINE_ATTRIBUTE = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries').ATTRIBUTE.wrapAsHolder(
  Java.loadClass('dev.ftb.mods.ftbultimine.registry.ModAttributes').MAX_BLOCKS_MODIFIER.get());
let aiEraTimer=0;
ServerEvents.tick(event => {
  if (++aiEraTimer % 100 !== 0) return;
  const server = event.server;
  let era = server.persistentData.getInt('arcane_era');
  server.players.forEach(player => {
    const inventory = player.getInventory();
    for (let i=0;i<inventory.getContainerSize();i++) {
      const item = inventory.getItem(i);
      era = Math.max(era, AI_ERA_ITEMS[String(item.id)] || 0);
    }
  });
  server.persistentData.putInt('arcane_era',era);
  server.players.forEach(player => {
    const attribute = player.getAttribute(AI_ULTIMINE_ATTRIBUTE);
    if (attribute != null && attribute.getBaseValue() !== 0) attribute.setBaseValue(0);
  });
});
'''
 (common/'kubejs/server_scripts/era_progression.js').write_text(stagejs,'utf-8')
 with zipfile.ZipFile(next((ROOT/'build/server/mods').glob('Apotheosis-*.jar'))) as jar:
  name='data/apotheosis/data_maps/dimension_type/invader_spawn_rules.json';rules=json.loads(jar.read(name))
  for value in rules['values'].values():
   for tier,chance in list(value['spawn_chances'].items()):value['spawn_chances'][tier]=round(.0025 if tier=='haven' else min(.08,chance*1.4),5)
  out=common/'kubejs'/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(rules,indent=2),'utf-8')
 out=cfg/'apotheosis/apotheosis.cfg';out.parent.mkdir(exist_ok=True);out.write_text((base/'apotheosis/apotheosis.cfg').read_text('utf-8').replace('I:"Boss Spawn Cooldown"=3600','I:"Boss Spawn Cooldown"=3200'),'utf-8')
 for kind,chance in [('affix',.55),('gem',.32)]:
  out=data/'apotheosis/loot_modifiers'/(kind+'_loot_injection.json');out.parent.mkdir(parents=True,exist_ok=True)
  out.write_text(json.dumps({'type':'apotheosis:affix_loot' if kind=='affix' else 'apotheosis:gems','conditions':[],'entries':[{'chance':chance,'pattern':{'path_regex':'.*(chests|structures|treasure|dungeon).*'}}]},indent=2),'utf-8')
 text=(base/'lootr-common.toml').read_text('utf-8').replace('team_loot = true','team_loot = false').replace('convert_elytras_to_chests = false','convert_elytras_to_chests = true').replace('convert_elytras_to_item_frames = true','convert_elytras_to_item_frames = false')
 (cfg/'lootr-common.toml').write_text(text,'utf-8')
 gear=json.loads((ROOT/'build/equipment-tiers.json').read_text('utf-8'));registry=json.loads((ROOT/'build/gear-registry.json').read_text('utf-8'))
 tiers={**gear['armor'],**gear['tools']};slots={r['id']:r['slot'] for r in registry['armor']};bows={r['id']:True for r in registry['tools'] if r['class_name']=='ProjectileWeaponItem'}
 out=common/'kubejs/config/loot-gear-policy.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps({'tiers':tiers,'slots':slots,'bows':bows},separators=(',',':')),'utf-8')
 names=['haven','frontier','ascent','summit','pinnacle'];created=[]
 invalid=set(json.loads((ROOT/'tools/data/apotheosis-invalid-affix-items.json').read_text('utf-8')))
 for item in invalid:
  stale=data/'arcaneindustry/affix_loot_entries/equipment'/(item.replace(':','/')+'.json')
  if stale.exists():stale.unlink()
 for namespace in ('mysticalagriculture','mysticalagradditions'):
  stale_dir=data/'arcaneindustry/affix_loot_entries/equipment'/namespace
  if stale_dir.exists():
   for stale in stale_dir.glob('*.json'):stale.unlink()
   stale_dir.rmdir()
 for row in registry['armor']+registry['tools']:
  item=row['id'];t=tiers[item]
  if t>=8 or 'creative' in item or item in invalid or item.startswith(('minecraft:','apothic_compats:')) or row.get('slot')=='body' or row.get('class_name')=='UsableItem':continue
  if item.startswith(('ars_elemancy:','ars_elemental:')) and any(s in item for s in ['_heavy','_tunic','_shoes','_pants','_helmet','_hood']):continue
  minimum=0 if t<=1 else 1 if t==2 else 2 if t==3 else 3 if t==4 else 4
  maximum=1 if t<=1 else 2 if t==2 else 3 if t==3 else 4
  weights={name:{'weight':6 if i==minimum else 2} for i,name in enumerate(names) if minimum<=i<=maximum}
  out=data/'arcaneindustry/affix_loot_entries/equipment'/(item.replace(':','/')+'.json');out.parent.mkdir(parents=True,exist_ok=True)
  out.write_text(json.dumps({'type':'apotheosis:affix_loot_entry','stack':{'id':item,'count':1},'weights':weights},indent=2),'utf-8');created.append(item)
 (ROOT/'build/quality-pass.json').write_text(json.dumps({'ultimine_max_blocks':16,'shared_progression':True,'additional_affix_equipment':len(created),'invader_spawn_multiplier':1.4,'initial_haven_chance':.0025,'cooldown_ticks':3200,'limits':['Existing personal Lootr inventories are preserved; only unopened/new loot changes.','Player-placed storage is never globally converted.']},indent=2),'utf-8')
 print('Quality defaults written; additional affix equipment:',len(created))

if __name__=='__main__':configure()
