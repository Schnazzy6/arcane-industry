"""Second recipe pass: reusable 9x9 assemblies connecting the content branches."""
import json

def connect(c):
    root=c['ROOT']; recipes=c['recipes']; items=c['items']; remove=c['remove']
    part=c['part']; ing=c['ing']; machine=c['machine']; shapeless=c['shapeless']
    m=c['M']; seals=c['seals']; cores=c['cores']
    electric=c['electric']; life=c['life']; industrial=c['industrial']; soul=c['soul']
    ritual=c['ritual']; element=c['element']; interface=c['interface']
    convergence=c['convergence']; stabilizer=c['stabilizer']

    food=part('provision_bundle','Алхимический рацион · земледелие','minecraft:item/cooked_beef')
    expedition=part('expedition_emblem','Знак исследователя миров · P4','minecraft:item/compass_16')
    research=part('relic_research','Исследование реликвий · M3','minecraft:item/brush')
    lattice=part('enchantment_lattice','Решётка зачарований · M3','minecraft:item/enchanted_book')
    matrix=part('engineering_matrix','Матрица магической логистики · P5','minecraft:item/comparator')
    boss=part('boss_seal','Печать покорителя · P5','minecraft:item/totem_of_undying')

    def table(name,out,key,count=4):
        """A 35-slot symmetric design: 12 frame pieces and 23 specialist inputs."""
        pattern=['PP     PP','P A B C P','  D E F  ',' G H I J ',
                 '  K L K  ',' G I H J ','  F E D  ','P C B A P','PP     PP']
        assert all(len(row)==9 for row in pattern)
        assert set(''.join(pattern)) - {' '} == set(key), (name,set(key))
        rid='kubejs:progression/'+name
        recipes[:]=[r for r in recipes if r['id']!=rid]
        c['add'](name,{'type':'avaritia:shaped_table','tier':4,'pattern':pattern,
                       'key':{k:ing(v) for k,v in key.items()},'result':{'id':out,'count':count}})

    # Farming has a recurring role without sacrificing rare dishes or unique utensils.
    shapeless('provision_bundle',food,['farmersdelight:beef_stew','farmersdelight:vegetable_soup',
              'croptopia:fruit_salad','croptopia:potato_soup','minecraft:honey_bottle'],8)

    # Spare curios can be researched; all accepted items are optional alternatives.
    content=json.loads((root/'build/connected-content.json').read_text('utf-8'))
    values=[]
    excluded={'mimic_spawn_egg','researching_table','phantom_block','relic_experience_bottle'}
    for ns in ['artifacts','relics','morerelics','reliquified_lenders_cataclysm']:
        for key in content.get(ns,{}).get('items',[]):
            name=key.split('.',2)[2]
            if key.startswith('item.') and name not in excluded and not name.endswith('_spawn_egg'):
                values.append({'id':ns+':'+name,'required':False})
    path=root/'overrides/common/kubejs/data/kubejs/tags/item/research_relic.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({'replace':False,'values':values},indent=2),'utf-8')
    shapeless('relic_research',research,['#kubejs:research_relic','minecraft:paper',life],8)

    # This table is infrastructure at MV, not an endgame prize that would create a loop.
    remove.add('avaritia:extreme_crafting_table')
    machine('industrial_extreme_table','avaritia:extreme_crafting_table',[
        (m+'advanced_machine_hull',1),(m+'stainless_steel_plate',12),(industrial,4),
        ('ars_nouveau:enchanting_apparatus',1),('minecraft:diamond',4)],1,32,800)

    table('enchantment_lattice',lattice,dict(
        P=m+'stainless_steel_plate',A='ars_nouveau:source_gem',B='irons_spellbooks:rare_ink',
        C='apotheosis:gem_dust',D='ars_nouveau:abjuration_essence',E='ars_nouveau:conjuration_essence',
        F='ars_nouveau:manipulation_essence',G='irons_spellbooks:arcane_essence',H=life,
        I=soul,J=research,K='theurgy:mercury_shard',L=industrial),8)
    table('expedition_emblem',expedition,dict(
        P=m+'stainless_steel_plate',A='twilightforest:naga_scale',B='eternal_starlight:deepsilver_ingot',
        C='born_in_chaos_v1:dark_metal_ingot',D='mowziesmobs:naga_fang',
        E='simplyswords:runic_tablet',F='ars_additions:wayfinder',G=food,H=life,
        I='eternal_starlight:thioquartz_shard',J=research,K='ars_nouveau:magebloom_fiber',L=industrial),8)
    shapeless('boss_seal',boss,['cataclysm:ignitium_ingot','twilightforest:fiery_ingot',
              'eternal_starlight:amaramber_ingot','goety:mystic_core',ritual],8)

    # Each school needs products of other schools; all ingredients precede these seals.
    table('seal_life',seals[0],dict(P=m+'titanium_plate',A=life,B='naturesaura:infused_iron',
        C='theurgy:mercury_shard',D='occultism:spirit_attuned_gem',E=food,
        F='ars_nouveau:magebloom_fiber',G=m+'processing_unit',H='hexerei:moon_dust',
        I='irons_spellbooks:arcane_essence',J=expedition,K=ritual,L=lattice),8)
    table('seal_mind',seals[1],dict(P=m+'titanium_plate',A='occultism:spirit_attuned_gem',
        B='ars_nouveau:manipulation_essence',C='ars_nouveau:conjuration_essence',
        D='ars_additions:wayfinder',E='ars_nouveau:magebloom_fiber',F='irons_spellbooks:rare_ink',
        G=m+'processing_unit',H=research,I=life,J=expedition,K=ritual,L=lattice),8)
    table('seal_soul',seals[2],dict(P=m+'titanium_plate',A='malum:soul_stained_steel_ingot',
        B='eidolon_repraised:soul_shard',C='evilcraft:dark_power_gem',D='goety:mystic_core',
        E='sauce:anima_essence',F='malum:arcane_spirit',G=soul,H=research,I=food,
        J=expedition,K=ritual,L=lattice),8)
    table('seal_elements',seals[3],dict(P=m+'titanium_plate',A=element,
        B='forbidden_arcanus:deorum_ingot',C='hexerei:moon_dust',D='ars_elemancy:elemancer_essence',
        E='ars_nouveau:fire_essence',F='ars_nouveau:water_essence',G='ars_nouveau:earth_essence',
        H='ars_nouveau:air_essence',I='irons_spellbooks:arcane_essence',J=expedition,K=ritual,L=lattice),8)

    table('engineering_matrix',matrix,dict(P=m+'titanium_plate',A='ae2:engineering_processor',
        B='ae2:calculation_processor',C='ae2:logic_processor',D='extendedae:concurrent_processor',
        E='advanced_ae:quantum_processor',F='arseng:source_cell_housing',
        G=seals[0],H=seals[1],I=seals[2],J=seals[3],K=m+'processing_unit',L=m+'quantum_circuit'),8)
    table('mekanism_interface',interface,dict(P=m+'titanium_plate',A=m+'quantum_circuit',
        B=matrix,C=seals[0],D=seals[1],E=seals[2],F=seals[3],G='#c:ingots/osmium',
        H=m+'processing_unit',I='arseng:source_cell_housing',J=lattice,K=expedition,L=industrial),8)
    table('convergence_core',convergence,dict(P=m+'iridium_plate',A=seals[0],B=seals[1],
        C=seals[2],D=seals[3],E='mekanism:pellet_polonium',F=m+'quantum_circuit',
        G=matrix,H=boss,I='mekanism:elite_control_circuit',J=expedition,K=lattice,L=interface),4)
    table('infinity_stabilizer',stabilizer,dict(P=m+'iridium_plate',A='mekanism:pellet_antimatter',
        B='mekanism_extras:absolute_control_circuit',C='mekanism_extras:alloy_radiance',
        D=seals[0],E=seals[1],F=seals[2],G=seals[3],H=matrix,I=convergence,J=boss,
        K='minecraft:nether_star',L=lattice),4)

    # Extras' ordinary alloy/circuit duplication also uses MI, its new chemicals stay native.
    for item,inputs in [
        ('alloy_radiance',[('mekanism:alloy_atomic',4),('mekanism_extras:dust_radiance',2),('mekanism:pellet_polonium',1)]),
        ('absolute_control_circuit',[('mekanism:ultimate_control_circuit',2),('mekanism_extras:alloy_radiance',2),(matrix,1)])]:
        remove.add('mekanism_extras:'+item)
        machine('mek_extras_'+item,'mekanism_extras:'+item,inputs,4,64,400)

    # Advanced frame batches are real multi-branch assemblies, not a single MI recipe.
    table('armor_core_t3',cores[3],dict(P=m+'stainless_steel_plate',A=industrial,B=life,
        C=m+'digital_circuit',D='ars_nouveau:source_gem',E='irons_spellbooks:arcane_essence',
        F='apotheosis:gem_dust',G=food,H='malum:arcane_spirit',I='eidolon_repraised:soul_shard',
        J='born_in_chaos_v1:dark_metal_ingot',K=soul,L=cores[2]),4)
    table('armor_core_t4',cores[4],dict(P=m+'titanium_plate',A=ritual,B=expedition,
        C=m+'processing_unit',D='sauce:anima_essence',E='forbidden_arcanus:deorum_ingot',
        F='goety:mystic_core',G='evilcraft:dark_power_gem',H='eidolon_repraised:soul_shard',
        I='malum:soul_stained_steel_ingot',J=food,K=lattice,L=cores[3]),4)
    table('armor_core_t5',cores[5],dict(P=m+'iridium_plate',A=m+'quantum_circuit',B=matrix,
        C=convergence,D='mekanism:pellet_polonium',E='ae2:fluix_pearl',
        F='malum:soul_stained_steel_ingot',G=seals[0],H=seals[1],I=seals[2],J=seals[3],K=boss,L=cores[4]),4)
    table('armor_core_t6',cores[6],dict(P='avaritia:infinity_ingot',A='avaritia:crystal_matrix_ingot',
        B='avaritia:neutron_ingot',C=stabilizer,D=boss,E=matrix,F='mekanism:pellet_antimatter',
        G=seals[0],H=seals[1],I=seals[2],J=seals[3],K='minecraft:nether_star',L=cores[5]),4)

    # Recurrent use of the enchanters' branch in advanced MI construction.
    frame=next(r['json'] for r in recipes if r['id']=='kubejs:progression/ritual_frame')
    frame['item_inputs'].append({'item':lattice,'amount':1})

    # Inter-school products are made in actual magical machinery, not only a table.
    replaced={'alchemical_catalyst','soul_stabilizer','elemental_insulator'}
    recipes[:]=[r for r in recipes if r['id'].split('/')[-1] not in replaced]
    c['apparatus']('alchemical_catalyst',life,'occultism:spirit_attuned_gem',
        ['theurgy:mercury_shard']*2+['naturesaura:infused_iron']*2+
        [m+'steel_plate']*2+['ars_nouveau:magebloom_fiber']*2,4,2500)
    c['add']('soul_stabilizer',{'type':'malum:spirit_infusion',
        'input':{'item':'eidolon_repraised:soul_shard','count':1},
        'extraInputs':[{'item':item,'count':count} for item,count in [
            (m+'stainless_steel_plate',2),('ars_nouveau:source_gem',2),
            ('occultism:spirit_attuned_gem',1),('irons_spellbooks:arcane_essence',2)]],
        'spirits':[{'type':'malum:arcane','count':4},{'type':'malum:aerial','count':2}],
        'result':{'id':soul,'count':4}})
    c['apparatus']('elemental_insulator',element,industrial,
        ['ars_nouveau:fire_essence','ars_nouveau:water_essence',
         'ars_nouveau:earth_essence','ars_nouveau:air_essence','hexerei:moon_dust',
         'naturesaura:infused_iron','theurgy:mercury_shard','irons_spellbooks:arcane_essence'],4,4000)

    for entry in c['patches']:
        rid=entry['id']; r=entry['json']
        if rid.endswith(':apprentice_book_upgrade'):
            r['ingredients'][3]=ing('irons_spellbooks:uncommon_ink')
        elif rid.endswith(':archmage_book_upgrade'):
            r['ingredients'][1]=ing('eidolon_repraised:soul_shard')
            r['ingredients'][2]=ing('malum:soul_stained_steel_ingot')
        elif rid.endswith(':crucible') and rid.startswith('eidolon_repraised:'):
            r['pattern']=['xFx','x x','xMx']
            r['key']['M']=ing('occultism:spirit_attuned_gem')
        elif rid.endswith(':dark_altar') and rid.startswith('goety:'):
            r['pattern'].append('EHE')
            r['key'].update(E=ing('eidolon_repraised:soul_shard'),H=ing('hexerei:moon_dust'))

    # Shared milestones require operating several schools' actual workstations.
    moved={'industrial_focus','ritual_frame','boss_seal','relic_research'}
    recipes[:]=[r for r in recipes if r['id'].split('/')[-1] not in moved]
    c['add']('industrial_focus',{'type':'naturesaura:tree_ritual',
        'ingredients':[ing(x) for x in [m+'digital_circuit',m+'digital_circuit',
            electric,electric,m+'stainless_steel_plate',m+'stainless_steel_plate',life,
            'naturesaura:gold_leaf']],
        'sapling':ing('naturesaura:ancient_sapling'),
        'output':{'id':industrial,'count':4},'time':400})
    c['add']('ritual_frame',{'type':'eidolon_repraised:crucible',
        'steps':[
            {'items':[ing(m+'titanium_plate')]*4},
            {'stirs':2,'items':[ing(m+'processing_unit')]*2+[ing(industrial)]},
            {'stirs':3,'items':[ing(soul)]*2+[ing(lattice)]}],
        'result':{'id':ritual,'count':4}})
    c['add']('relic_research',{'type':'occultism:ritual',
        'activation_item':ing('occultism:book_of_binding_bound_foliot'),
        'duration':30,'pentacle_id':'occultism:craft_foliot','ritual_type':'occultism:craft',
        'ingredients':[ing(x) for x in ['#kubejs:research_relic','minecraft:paper',life,
            'irons_spellbooks:arcane_essence']],
        'result':{'id':research,'count':8},'ritual_dummy':{'id':research,'count':1}})
    c['add']('boss_seal',{'type':'goety:ritual','ritual_type':'goety:craft',
        'activation_item':ing(ritual),'craftType':'magic','soulCost':25,'duration':40,
        'ingredients':[ing(x) for x in ['cataclysm:ignitium_ingot','twilightforest:fiery_ingot',
            'eternal_starlight:amaramber_ingot','goety:mystic_core',
            'eidolon_repraised:soul_shard','hexerei:moon_dust','malum:arcane_spirit']],
        'result':{'id':boss,'count':8}})
