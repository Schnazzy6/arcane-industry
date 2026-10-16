"""Final migration of the established progression to Tech Reborn.

Runs after the school/armor passes so the same milestones and rituals survive.
Legacy Mekanism-only machines/chemicals are removed, never renamed to fake IDs.
"""
import copy,json,zipfile

OLD={'mekanism','mekanismgenerators','mekanism_extras','appmek'}
def old(value):return isinstance(value,str) and value.split(':')[0] in OLD

def migrate(c):
    root=c['ROOT'];m=c['M'];recipes=c['recipes'];patches=c['patches'];armor=c['armor'];remove=c['remove']
    tr='techreborn:';interface='kubejs:reborn_interface'
    mapping={
      'kubejs:mekanism_interface':interface,
      'mekanism:pellet_polonium':tr+'uu_matter',
      'mekanism:pellet_antimatter':tr+'iridium_alloy_ingot',
      'mekanism:elite_control_circuit':tr+'industrial_circuit',
      'mekanism:ultimate_control_circuit':tr+'data_storage_chip',
      'mekanism_extras:absolute_control_circuit':tr+'data_storage_chip',
      'mekanism_extras:alloy_radiance':tr+'superconductor',
      'c:ingots/osmium':'c:ingots/iridium',
      'croptopia:fruit_salad':'farmersdelight:fruit_salad',
      'croptopia:potato_soup':'farmersdelight:pumpkin_soup',
      'c:advanced_alloy_plates':'c:plates/advanced_alloy',
      'c:iridium_alloy_plates':'c:plates/iridium_alloy',
      **{'mekanism:mekasuit_'+a:tr+'quantum_'+b for a,b in [('helmet','helmet'),('bodyarmor','chestplate'),('pants','leggings'),('boots','boots')]},
    }
    def walk(value):
        if isinstance(value,str):return mapping.get(value,value.replace('mekanism_interface','reborn_interface').replace('mekasuit_','tr_quantum_'))
        if isinstance(value,list):return [walk(v) for v in value]
        if isinstance(value,dict):return {k:walk(v) for k,v in value.items()}
        return value
    retired=[]
    for rows in [recipes,patches]:
        kept=[]
        for r in rows:
            if old(r['id']) or any(old(x) for x in c['result_ids'](r['json'])) or r['id']=='megacells:crafting/radioactive_cell_component' or any(('"modid": "'+ns+'"') in json.dumps(r['json']) for ns in OLD):
                retired.append(r['id']);continue
            kept.append(walk(r))
        rows[:]=kept
    armor[:]=walk(armor)
    remove.intersection_update(x for x in list(remove) if not old(x))
    remove.discard('kubejs:mekanism_interface')
    remove.update(a['out'] for a in armor if a['out'].startswith(tr))
    data=c['items'].pop('mekanism_interface');data['title']='Квантовый интерфейс Tech Reborn · P5'
    data['texture']=data['texture'].replace('mekanism_interface','reborn_interface');c['items']['reborn_interface']=data
    c['interface']=interface
    # At T5 quantum armor keeps the previous T4 options. Nano armor is a late T4 bridge.
    for slot in c['slots']:
        quantum=next(a for a in armor if a['out']==tr+'quantum_'+slot)
        bases=copy.deepcopy(quantum['base'])
        c['upgrade']('tr_nano_'+slot,tr+'nano_'+slot,bases,4,tr+'carbon_plate')
        nano=armor[-1];nano['binding']=interface
        quantum['base']=bases+[tr+'nano_'+slot]
        quantum['material']=tr+'iridium_alloy_plate'
    # Native armor below nano remains subject to the same tier economy.
    for family,tier,mat in [('steel',2,m+'steel_plate'),('silver',2,'#c:ingots/silver'),('ruby',3,tr+'ruby_gem'),('sapphire',3,tr+'sapphire_gem'),('peridot',3,tr+'peridot_gem')]:
        for slot in c['slots']:
            c['upgrade']('tr_'+family+'_'+slot,tr+family+'_'+slot,'minecraft:'+('chainmail' if tier==2 else 'iron')+'_'+slot,tier,mat if not mat.startswith('#') else 'occultism:silver_ingot')
    # Shared components are batched in MI. Late circuits carry the four-school gate.
    components={
      'electronic_circuit':([(m+'processing_unit',2),(interface,1),(m+'copper_fine_wire',8)],4,32),
      'advanced_circuit':([(tr+'electronic_circuit',2),(m+'quantum_circuit',1),(c['seals'][1],1)],4,64),
      'industrial_circuit':([(tr+'advanced_circuit',2),(tr+'advanced_alloy_plate',2),('kubejs:engineering_matrix',1)],4,64),
      'data_storage_chip':([(tr+'industrial_circuit',2),(tr+'silicon_plate',4),(m+'iridium_plate',2),(c['seals'][1],1)],4,128),
    }
    for name,(inputs,count,eu) in components.items():
        remove.add(tr+name);c['machine']('tr_'+name,tr+name,inputs,count,eu,400)
    # Avoid new processing duplicates: MI makes the common alloys and plates.
    for name,inputs,eu,kind in [
      ('advanced_alloy_ingot',[(m+'stainless_steel_ingot',4),(m+'aluminum_ingot',2),(c['element'],1)],32,'mixer'),
      ('iridium_alloy_ingot',[(m+'iridium_ingot',4),(tr+'advanced_alloy_ingot',2),('minecraft:diamond',2),(c['seals'][3],1)],128,'mixer'),
      ('advanced_alloy_plate',[(tr+'advanced_alloy_ingot',1)],16,'compressor'),
      ('iridium_alloy_plate',[(tr+'iridium_alloy_ingot',1)],64,'compressor')]:
        remove.add(tr+name);c['machine']('tr_'+name,tr+name,inputs,1 if name.endswith('_plate') else 4,eu,400,type=kind)
    # Every ordinary native TR crafting recipe for a machine/tool has a gated circuit
    # or an explicit interface. Matter production stays native and consumes power.
    gates={}
    with zipfile.ZipFile(root/'cache/files/TechReborn-5.11.19.jar') as jar:
        blocks={p.split('/blockstates/')[1][:-5] for p in jar.namelist() if '/blockstates/' in p and p.endswith('.json')}
        for path in jar.namelist():
            if '/recipe/' not in path or not path.endswith('.json'):continue
            r=json.loads(jar.read(path));outs=c['result_ids'](r)
            if r.get('type') not in ['minecraft:crafting_shaped','minecraft:crafting_shapeless'] or len(outs)!=1:continue
            out=outs[0];name=out.split(':')[-1]
            if out in remove or not out.startswith(tr):continue
            # Construction blocks, wood, storage blocks and decorative geometry remain ordinary.
            machine=name in blocks and any(k in name for k in ['generator','furnace','grinder','centrifuge','electrolyzer','compressor','extractor','machine','fabricator','freezer','reactor','mill','pump','recycler','storage_unit','tank_unit','_su','solar_panel','transformer','charge','scrapboxinator','distillation'])
            tool=name in ['omni_tool','nanosaber','rock_cutter','industrial_drill','industrial_chainsaw','industrial_jackhammer','lapotronic_orbpack']
            if not (machine or tool):continue
            gate=c['convergence'] if name in ['fusion_control_computer','quantum_solar_panel','quantum_storage_unit','omni_tool'] else interface
            remove.add(out);gates[out]=gate
            advanced=any(k in name for k in ['industrial','fusion','quantum','matter','plasma','lapotronic'])
            if (advanced or len(r.get('key',{}))>4) and r.get('pattern'):
                # Retain every native ingredient, including fusion coils and coolers.
                symbols={ch:str(i) for i,ch in enumerate(r['key'])}
                pattern=['    H    ','  P   P  ','    C    ']
                for row in r['pattern']:
                    pattern.append('   '+''.join(symbols.get(ch,' ') for ch in row).ljust(3)+'   ')
                while len(pattern)<6:pattern.append('         ')
                pattern+=['    C    ','  P   P  ','    G    ']
                key={symbols[k]:v for k,v in r['key'].items()}
                key.update(H=c['ing'](m+'quantum_machine_hull'),P=c['ing'](m+'titanium_plate'),C=c['ing'](tr+'industrial_circuit'),G=c['ing'](gate))
                c['add']('tr_machine_'+name,{'type':'avaritia:shaped_table','tier':4,'pattern':pattern,'key':key,'result':{'id':out,'count':r['result'].get('count',1)}})
            else:
                # Smaller machines keep native ingredients in an MI assembler (six input slots).
                inputs=[]
                for group in list(r.get('key',{}).values()) if r.get('key') else r.get('ingredients',[]):
                    if isinstance(group,dict) and ('item' in group or 'tag' in group):
                        ident=group.get('item','#'+group['tag'] if 'tag' in group else '')
                        n=sum(row.count(k) for row in r['pattern'] for k,v in r['key'].items() if v==group) if r.get('pattern') else 1
                        if not any(x[0]==ident for x in inputs):inputs.append((ident,n))
                if len(inputs)>4:
                    # Retain the native recipe and inject one gate into an empty space.
                    x=copy.deepcopy(r)
                    if x.get('pattern') and any(' ' in row for row in x['pattern']):
                        for i,row in enumerate(x['pattern']):
                            if ' ' in row:x['pattern'][i]=row.replace(' ','Z',1);break
                        x['key']['Z']=c['ing'](gate)
                        c['add']('tr_machine_'+name,x);continue
                    raise RuntimeError('Machine recipe needs explicit layout: '+out)
                inputs += [(gate,1),(m+'stainless_steel_plate',4)]
                c['machine']('tr_machine_'+name,out,inputs,1,32,600)
    # Matter fabricator must precede the core that consumes UU, never depend on it.
    assert gates.get(tr+'matter_fabricator')==interface
    # Advanced Reborn ships several 1.20-style result/ingredient fields.
    # Correct them here, then gate its machines as well as the base mod's machines.
    ar='advanced_reborn:'
    with zipfile.ZipFile(root/'cache/files/AdvancedReborn-1.21.1-1.3.4.jar') as jar:
        for path in jar.namelist():
            if '/recipe/' not in path or not path.endswith('.json'):continue
            r=json.loads(jar.read(path))
            if r.get('type') not in ['minecraft:crafting_shaped','minecraft:crafting_shapeless']:continue
            result=r.get('result',{})
            if 'item' in result:result['id']=result.pop('item')
            def ingredient(x):
                if isinstance(x,str):return c['ing'](x)
                if isinstance(x,list):return [ingredient(i) for i in x]
                return x
            if 'key' in r:r['key']={k:ingredient(v) for k,v in r['key'].items()}
            if 'ingredients' in r:r['ingredients']=[ingredient(v) for v in r['ingredients']]
            r=walk(r);result=r['result']
            out=result.get('id','');name=out.split(':')[-1]
            gated=out.startswith(ar) and any(k in name for k in ['generator','solar_panel','machine','extractor','furnace','grinder','charge_pad','enchantment_extractor','logging','farming','freq_trans'])
            rid=path.split('/')[1]+':'+path.split('/recipe/')[1][:-5]
            if gated:
                remove.add(out);gates[out]=interface
                # Native 3x3 is retained in the center of a 9x9 assembly.
                if r.get('pattern'):
                    symbols={ch:str(i) for i,ch in enumerate(r['key'])};pattern=['    H    ','  P   P  ','    C    ']
                    pattern += ['   '+''.join(symbols.get(ch,' ') for ch in row).ljust(3)+'   ' for row in r['pattern']]
                    while len(pattern)<6:pattern.append('         ')
                    pattern += ['    C    ','  P   P  ','    G    ']
                    key={symbols[k]:v for k,v in r['key'].items()};key.update(H=c['ing'](m+'advanced_machine_hull'),P=c['ing'](m+'titanium_plate'),C=c['ing'](tr+'advanced_circuit'),G=c['ing'](interface))
                    c['add']('ar_'+rid.split(':')[1].replace('/','_'),{'type':'avaritia:shaped_table','tier':4,'pattern':pattern,'key':key,'result':result})
                elif len(r.get('ingredients',[]))<9:
                    r['ingredients'].append(c['ing'](interface));c['add']('ar_'+rid.split(':')[1].replace('/','_'),r)
                else:raise RuntimeError('Unhandled addon machine '+rid)
            else:patches.append({'id':rid,'json':r})
            native=copy.deepcopy(r)
            if gated:native['neoforge:conditions']=[{'type':'neoforge:false'}]
            dest=root/'overrides/common/kubejs'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(native,indent=2),'utf-8')
    # Unique materials still use real native TR machines: superconductor, carbon,
    # silicon, energy crystals and UU matter are not replaced by free handcrafts.
    compat=root/'tools/data/techreborn-compat-recipes.json'
    if compat.exists():
        for row in json.loads(compat.read_text('utf-8')):
            patches.append(row)
            ns,suffix=row['id'].split(':');dest=root/'overrides/common/kubejs/data'/ns/'recipe'/(suffix+'.json');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(row['json'],indent=2),'utf-8')
    for row in patches:
        if row['json'].get('type')=='betterend:infusion':
            # This port's infusion stack codec conflicts with KubeJS. Keep the
            # materials and armor attributes in a real, supported magical altar.
            original=row['json'];result=original['result'];output={'id':result.get('id',result.get('item')),'count':result.get('count',1)}
            if result.get('nbt'):output['components']=result['nbt']
            def unwrap(value):
                while isinstance(value,dict) and isinstance(value.get('item'),dict):value=value['item']
                return value
            row['json']={'type':'ars_nouveau:enchanting_apparatus','reagent':unwrap(original['input']),
              'pedestalItems':[unwrap(v) for v in original['catalysts'].values()],
              'result':output,'sourceCost':10000,'keepNbtOfReagent':False}
    c['integration']=walk(c['integration'])
    def prune(v):
        if isinstance(v,list):return [prune(x) for x in v if not any(old(s) for s in strings(x))]
        if isinstance(v,dict):return {k:prune(x) for k,x in v.items()}
        return v
    def strings(v):
        if isinstance(v,str):yield v
        elif isinstance(v,dict):
            for x in v.values():yield from strings(x)
        elif isinstance(v,list):
            for x in v:yield from strings(x)
    c['integration']=prune(c['integration'])
    (root/'build/recipe-integration.json').write_text(json.dumps(c['integration'],ensure_ascii=False,indent=2),'utf-8')
    unmapped=sorted({s for s in strings([recipes,patches,armor,list(remove)]) if old(s)})
    assert not unmapped, 'Unmapped Mekanism prerequisite: '+str(unmapped)
    (root/'build/techreborn-migration.json').write_text(json.dumps({'retired_recipe_ids':retired,'mapped_items':mapping,'gated_machines':gates,'armor_path':'T4 alternatives -> nano (late T4) -> quantum T5 -> Infinity T6','native_materials':['uu_matter','superconductor','carbon_plate','energy_crystal','lapotron_crystal']},ensure_ascii=False,indent=2),'utf-8')

