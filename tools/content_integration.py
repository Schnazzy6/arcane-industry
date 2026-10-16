"""Integrate native world-port gear and nutrition with the existing progression."""
import copy,json,pathlib,zipfile,shutil,os
from catalog import ROOT

def nutrition():
 jar=next((ROOT/'build/server/mods').glob('appleseed-3*.jar'))
 effects={
 'fruits':['71-80:attribute(minecraft:generic.attack_speed,0.05)','81-100:attribute(minecraft:generic.attack_speed,0.1)'],
 'grains':['81-100:effect(minecraft:haste,0)'],
 'proteins':['71-80:attribute(minecraft:generic.attack_damage,0.5)','81-100:attribute(minecraft:generic.attack_damage,1.0)'],
 'vegetables':['71-80:attribute(minecraft:generic.armor_toughness,0.5)','81-100:attribute(minecraft:generic.armor_toughness,1.0)'],
 'sugars':['61-80:attribute(minecraft:generic.movement_speed,0.003)','81-100:attribute(minecraft:generic.movement_speed,0.005)']}
 with zipfile.ZipFile(jar) as z:
  for group,bonus in effects.items():
   rel='data/appleseed/diet/groups/'+group+'.json';r=json.loads(z.read(rel));r['effects']=bonus
   p=ROOT/'overrides/common/kubejs'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(r,indent=2),'utf-8')
 config='[General_Settings]\nignore_hunger = true\nentrance_visibility = "ftb_compact"\n'
 config+='\n[Effects_Override]\n'+''.join(group+'_ranges = '+json.dumps(bonus)+'\n' for group,bonus in effects.items())
 for base in [ROOT/'overrides/common',ROOT/'build/server',ROOT/'build/prism/Arcane Industry Prototype/minecraft',pathlib.Path(os.environ['APPDATA'])/'PrismLauncher/instances/ArcaneIndustry-0.1.4/minecraft']:
  p=base/'config/appleseed-common.toml';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(config,'utf-8')

def integrate(c):
 if not (ROOT/'build/content-expansion.json').exists():return
 armor=c['armor'];patches=c['patches'];remove=c['remove'];m=c['M'];slots=['helmet','chestplate','leggings','boots'];tiers={}
 families=[('betternether','cincinnasite',2,'immersive_armors:bone_','cincinnasite_ingot'),
 ('betternether','nether_ruby',3,'betternether:cincinnasite_','nether_ruby'),
 ('betterend','thallasium',3,'immersive_armors:warrior_','thallasium_forged_plate'),
 ('betterend','terminite',4,'betterend:thallasium_','terminite_forged_plate')]
 for ns,family,t,base,material in families:
  for slot in slots:
   out=f'{ns}:{family}_{slot}';remove.add(out);tiers[out]=t
   armor.append({'id':'kubejs:progression/armor/'+ns+'_'+family+'_'+slot,'out':out,'base':base+slot,'core':'kubejs:armor_core_t'+str(t),'material':ns+':'+material,'plate':m+('steel_plate' if t==2 else 'stainless_steel_plate' if t==3 else 'titanium_plate'),'binding':'minecraft:leather','tier':t,'reinforce':False})
 native=[]
 for ns,mask in [('betterend','BetterEnd-*.jar'),('betternether','BetterNether-*.jar')]:
  jar=next((ROOT/'build/server/mods').glob(mask))
  with zipfile.ZipFile(jar) as z:
   for path in z.namelist():
    if not path.startswith('data/'+ns+'/recipe/') or not path.endswith('.json'):continue
    r=json.loads(z.read(path));result=r.get('result',{})
    if not isinstance(result,dict):continue
    out=result.get('id',result.get('item',''))
    if not isinstance(out,str):continue
    name=out.split(':')[-1];t=None
    if ns=='betterend' and name.startswith('aeternium_') and any(name.endswith('_'+s) for s in slots):t=5
    elif ns=='betternether' and name.startswith('flaming_ruby_') and any(name.endswith('_'+s) for s in slots):t=4
    if t and r['type']=='minecraft:smithing_transform':
     r['template']={'item':'kubejs:armor_core_t'+str(t)};tiers[out]=t
    elif ns=='betterend' and name.startswith('crystalite_') and any(name.endswith('_'+s) for s in slots) and r['type']=='betterend:infusion':
     position=next(s for s in ['south','north_east','south_east','south_west','north_west','north','east','west'] if s not in r['catalysts'])
     r['catalysts'][position]={'item':{'item':'kubejs:armor_core_t4'}};tiers[out]=4
    elif any(name.endswith('_'+s) for s in ['sword','pickaxe','axe','shovel','hoe','hammer']) and r['type'] in ['minecraft:crafting_shaped','minecraft:smithing_transform']:
     gate='convergence_core' if 'aeternium' in name else 'ritual_frame' if any(x in name for x in ['terminite','flaming_ruby']) else 'industrial_focus' if any(x in name for x in ['thallasium','ruby','diamond']) else 'electrical_focus'
     if r['type']=='minecraft:smithing_transform':r['template']={'item':'kubejs:'+gate}
     else:
      pattern=[list(row) for row in r['pattern']];y,x=next((y,x) for y,row in enumerate(pattern) for x,ch in enumerate(row) if ch!=' ')
      pattern[y][x]='@';r['pattern']=[''.join(row) for row in pattern];used=set(''.join(r['pattern']))
      r['key']={k:v for k,v in r['key'].items() if k in used};r['key']['@']={'item':'kubejs:'+gate}
    else:continue
    rid=ns+':'+path.split('/recipe/')[1][:-5];patches.append({'id':rid,'json':r});native.append(rid)
 # Every new T4 can continue to MekaSuit; the T5 family can reach Infinity.
 for a in armor:
  if a['out'].startswith('mekanism:mekasuit_') or a['tier']==6:
   slot=next((s for s in slots if a['out'].endswith('_'+s)),None)
   if a['out']=='mekanism:mekasuit_bodyarmor':slot='chestplate'
   if a['out']=='mekanism:mekasuit_pants':slot='leggings'
   if slot:
    choices=[out for out,t in tiers.items() if t==(4 if a['out'].startswith('mekanism:') else 5) and out.endswith('_'+slot)]
    if choices:
     if not isinstance(a['base'],list):a['base']=[a['base']]
     a['base']+=choices
 (ROOT/'build/content-armor-tiers.json').write_text(json.dumps(tiers,indent=2),'utf-8')
 (ROOT/'build/content-recipe-integration.json').write_text(json.dumps({'armor':tiers,'native_patches':native},indent=2),'utf-8')
 nutrition()
 print('Content integration:',len(tiers),'armor pieces,',len(native),'native recipes; Valheim retained, Diet health stacking disabled.')
