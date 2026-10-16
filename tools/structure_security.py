"""Remove free protected equipment and machines from future structure templates."""
import io,json,pathlib,sys,zlib,gzip,re
from catalog import ROOT
sys.path.insert(0,str(ROOT/'cache/python-tools'))
import nbtlib

def harden(guarded):
 records=[];scanned=0;converted=0;skipped_fixed=0;skipped_details=[];out=ROOT/'overrides/common/kubejs'
 def old_components(stack):
  if 'tag' not in stack:return {}
  tag=stack['tag'].unpack()
  item=str(stack.get('id',''))
  if item=='minecraft:writable_book' and set(tag)=={'pages'}:
   return {'minecraft:writable_book_content':{'pages':list(tag['pages'])}}
  if item=='goety:dark_wand' and tag=={'Soul Cost':0,'cap':{'Size':1,'Items':[]},'Soul Use':0,'Cooldown':0,'Duration':0,'Cast Time':0,'Shots':0}:
   # This structure stores only the wand's default, empty capability values.
   return {}
  if not isinstance(tag,dict) or set(tag)-{'Potion','RepairCost','Damage','Enchantments','display'}:return None
  result={}
  if tag.get('Potion'):result['minecraft:potion_contents']={'potion':tag['Potion']}
  if tag.get('RepairCost',0):result['minecraft:repair_cost']=int(tag['RepairCost'])
  if tag.get('Damage',0):result['minecraft:damage']=int(tag['Damage'])
  if tag.get('Enchantments'):
   result['minecraft:enchantments']={'levels':{e['id']:int(e['lvl']) for e in tag['Enchantments']}}
  if 'display' in tag:
   display=tag['display']
   if not isinstance(display,dict) or set(display)-{'color','Name'}:return None
   if 'color' in display:result['minecraft:dyed_color']={'rgb':int(display['color'])}
   if 'Name' in display:result['minecraft:custom_name']=display['Name']
  return result
 def replacement(item):
  # Keep display stands dressed, without granting a progression upgrade.
  for endings,slot in [(['boots'],'boots'),(['leggings'],'leggings'),(['chestplate','robes'],'chestplate'),(['helmet','hood','hat'],'helmet')]:
   if any(item.endswith('_'+e) for e in endings):return 'minecraft:leather_'+slot
  return 'minecraft:amethyst_shard'
 def unsupported_stack_data(stack):
  extra=set(stack)-{'id','Slot','Count','count','components','tag'}
  if extra=={'ForgeCaps'} and str(stack.get('id',''))=='goety:dark_wand' and stack['ForgeCaps'].unpack()=={'Parent':{'Size':1,'Items':[]}}:
   extra=set()
  return bool(extra) or old_components(stack) is None
 def scrub(v,changes):
  if isinstance(v,nbtlib.Compound):
   if str(v.get('id','')) in guarded:
    before=str(v['id']);after=replacement(before)
    saved_slot=v.get('Slot');old_count='Count' in v
    v.clear();v['id']=nbtlib.String(after)
    v['Count' if old_count else 'count']=nbtlib.Byte(1) if old_count else nbtlib.Int(1)
    if saved_slot is not None:v['Slot']=saved_slot
    changes.append({'kind':'item','from':before,'to':after})
   else:
    for x in list(v.values()):scrub(x,changes)
  elif isinstance(v,nbtlib.List):
   for x in v:scrub(x,changes)
 for jar in sorted((ROOT/'build/server/mods').glob('*.jar')):
  import zipfile
  with zipfile.ZipFile(jar) as z:
   for name in z.namelist():
    if '/structure/' not in name or not name.endswith('.nbt'):continue
    raw=z.read(name);raw=zlib.decompress(raw,31) if raw[:2]==b'\x1f\x8b' else raw
    scanned+=1
    ids={s.decode() for s in re.findall(rb'[a-z0-9_]+:[a-z0-9_/]+',raw)}
    if not ids&guarded and b'Items' not in raw:continue
    nbt=nbtlib.File.parse(io.BytesIO(raw));changes=[];replaced=set()
    palettes=[nbt['palette']] if 'palette' in nbt else list(nbt.get('palettes',[]))
    for palette in palettes:
     for index,state in enumerate(palette):
      if str(state.get('Name','')) in guarded:
       old=str(state['Name']);state.clear();state['Name']=nbtlib.String('minecraft:chiseled_stone_bricks')
       replaced.add(index);changes.append({'kind':'block_palette','from':old,'to':'minecraft:chiseled_stone_bricks'})
    for block in nbt.get('blocks',[]):
     if int(block.get('state',-1)) in replaced:block.pop('nbt',None)
    scrub(nbt,changes)
    namespace=name.split('/')[1];structure=name.split('/structure/',1)[1][:-4]
    for index,block in enumerate(nbt.get('blocks',[])):
     tag=block.get('nbt')
     if not isinstance(tag,nbtlib.Compound) or 'LootTable' in tag:continue
     block_id=str(tag.get('id',''))
     if block_id not in ('minecraft:chest','minecraft:trapped_chest','minecraft:barrel'):continue
     stacks=tag.get('Items')
     if not stacks:continue
     if any(unsupported_stack_data(stack) for stack in stacks):
      skipped_fixed+=1
      skipped_details.append({'path':name,'index':index,'items':[str(stack.get('id','')) for stack in stacks]})
      continue
     pools=[]
     for stack in stacks:
      item=str(stack.get('id',''));count=int(stack.get('count',stack.get('Count',1)))
      if not item or count<1:continue
      entry={'type':'minecraft:item','name':item}
      functions=[]
      if count>1:functions.append({'function':'minecraft:set_count','count':count})
      if 'components' in stack:
       functions.append({'function':'minecraft:set_components','components':stack['components'].unpack()})
      legacy=old_components(stack)
      if legacy:functions.append({'function':'minecraft:set_components','components':legacy})
      if functions:entry['functions']=functions
      pools.append({'rolls':1,'entries':[entry]})
     if not pools:continue
     table='arcane_fixed/'+namespace+'/'+structure+'_'+str(index)
     table_id='kubejs:'+table
     table_path=out/'data/kubejs/loot_table'/(table+'.json')
     table_path.parent.mkdir(parents=True,exist_ok=True)
     table_path.write_text(json.dumps({'type':'minecraft:chest','pools':pools},separators=(',',':')),'utf-8')
     tag.pop('Items',None);tag['LootTable']=nbtlib.String(table_id)
     changes.append({'kind':'fixed_loot_to_personal','table':table_id,'stacks':len(pools)})
     converted+=1
    if not changes:continue
    buffer=io.BytesIO();nbt.write(buffer)
    encoded=gzip.compress(buffer.getvalue(),mtime=0)
    # Read back every changed template before writing it into the pack.
    nbtlib.File.parse(io.BytesIO(gzip.decompress(encoded)))
    p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(encoded)
    records.append({'path':name,'changes':changes})
 report={'structures_scanned':scanned,'fixed_containers_converted':converted,'fixed_containers_skipped_with_special_data':skipped_fixed,'skipped_details':skipped_details,'modified':records,'policy':'New templates only; already generated chunks remain unchanged.'}
 (ROOT/'build/structure-security-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
 return report
