"""Content-wide milestone pass. Keep native mechanics, gate meaningful capabilities."""
import copy,json,zipfile,collections

def integrate(c):
 root=c['ROOT'];m=c['M'];ing=c['ing'];patches=c['patches'];remove=c['remove'];armor=c['armor']
 # Freeze pre-integration active IDs: a later validation snapshot intentionally
 # lacks replaced native recipes and must not make regeneration erase upgrades.
 live=set(json.loads((root/'tools/data/progression-active-recipes.json').read_text('utf-8')))
 source={}
 for jar in sorted((root/'build/server/mods').glob('*.jar')):
  with zipfile.ZipFile(jar) as z:
   for p in z.namelist():
    if p.startswith('data/') and '/recipe/' in p and p.endswith('.json'):
     rid=p.split('/')[1]+':'+p.split('/recipe/')[1][:-5]
     if rid in live:
      try:source[rid]=json.loads(z.read(p))
      except ValueError:pass
 index={r['id']:r for r in patches}
 gates={};categories={};manifest=[];missing=[]
 def group(ns,names,gate,category):
  for name in names.split():gates[ns+':'+name]=gate;categories[ns+':'+name]=category
 electric=c['electric'];life=c['life'];industrial=c['industrial'];soul=c['soul'];ritual=c['ritual'];element=c['element']
 sl,sm,ss,se=c['seals'];matrix='kubejs:engineering_matrix';lattice='kubejs:enchantment_lattice';research='kubejs:relic_research';boss='kubejs:boss_seal'
 conv=c['convergence'];inf=c['stabilizer'];mount=c['mount']
 # Starter source production stays independent of MI electricity.
 group('ars_nouveau','enchanting_apparatus ritual_brazier',mount,'Ars: основы')
 group('ars_nouveau','starbuncle_charm relay basic_spell_turret',electric,'Ars: ранняя автоматизация')
 group('ars_nouveau','wixie_charm whirlisprig_charm mycelial_sourcelink',life,'Ars: алхимия и растения')
 group('ars_nouveau','drygmy_charm vitalic_sourcelink volcanic_sourcelink alchemical_sourcelink rotating_spell_turret',industrial,'Ars: промышленная автоматизация')
 group('ars_nouveau','spell_prism mob_jar',soul,'Ars: души')
 group('ars_nouveau','ritual_flight ritual_disintegration ritual_containment ritual_conjure_island_plains ritual_conjure_island_desert',ritual,'Ars: старшие ритуалы')
 group('ars_nouveau','repository_controller void_prism',sm,'Ars: мастерская логистика')
 group('ars_elemental','advanced_prism ritual_tesla_coil ritual_flight',element,'Ars Elemental')
 group('ars_additions','wayfinder',life,'Ars Additions: исследование')
 group('ars_additions','advanced_dominion_wand handy_haversack xp_jar',industrial,'Ars Additions: инструменты')
 group('irons_spellbooks','copper_spell_book',mount,'Книги заклинаний: I')
 group('irons_spellbooks','iron_spell_book gold_spell_book',electric,'Книги заклинаний: II')
 group('irons_spellbooks','diamond_spell_book ice_spell_book druidic_spell_book',soul,'Книги заклинаний: III')
 group('irons_spellbooks','netherite_spell_book dragonskin_spell_book cursed_doll_spell_book',ritual,'Книги заклинаний: IV')
 group('irons_spellbooks','scroll_forge',industrial,'Мастерская заклинаний')
 group('irons_spellbooks','shriving_stone',soul,'Мастерская заклинаний')
 group('irons_spellbooks','upgrade_orb lesser_spell_slot_upgrade',lattice,'Усиление заклинаний')
 group('irons_spellbooks','mana_ring cast_time_ring cooldown_ring',industrial,'Магические аксессуары')
 group('irons_spellbooks','concentration_amulet affinity_ring greater_conjurers_talisman',ritual,'Магические аксессуары')
 group('occultism','storage_controller storage_controller_dark storage_stabilizer_tier0 storage_stabilizer_tier0_dark',life,'Occultism: раннее хранилище')
 group('occultism','book_of_calling_foliot_cleaner book_of_calling_foliot_farmer book_of_calling_foliot_lumberjack book_of_calling_foliot_transport_items',electric,'Occultism: работники')
 group('occultism','book_of_calling_djinni_manage_machine',industrial,'Occultism: машинный дух')
 group('occultism','storage_stabilizer_tier1',industrial,'Occultism: хранилище II')
 group('occultism','storage_stabilizer_tier2',ritual,'Occultism: хранилище III')
 group('occultism','storage_stabilizer_tier3',sm,'Occultism: хранилище IV')
 group('naturesaura','offering_table oak_generator flower_generator',life,'Аура: устойчивая генерация')
 group('naturesaura','auto_crafter placer item_distributor powder_placer potion_generator animal_generator',industrial,'Аура: автоматизация')
 group('naturesaura','animal_spawner rf_converter time_changer weather_changer',ritual,'Аура: старшие механизмы')
 group('naturesaura','chunk_loader ender_access generator_limit_remover',sm,'Аура: пространственная ветка')
 group('malum','spirit_crucible soul_warding_ring',soul,'Malum: развитие духов')
 group('malum','spirit_catalyzer spirit_resonator',ritual,'Malum: ускорение')
 group('eidolon_repraised','worktable wooden_altar',mount,'Eidolon: основы')
 group('eidolon_repraised','brazier scriptorium research_table',industrial,'Eidolon: исследования')
 group('eidolon_repraised','soul_enchanter',lattice,'Eidolon: зачарование')
 group('eidolon_repraised','necrotic_focus lesser_soul_gem',soul,'Eidolon: души')
 group('evilcraft','blood_chest purifier sanguinary_pedestal_0',ritual,'EvilCraft: кровь и очистка')
 group('evilcraft','spirit_furnace spirit_reanimator sanguinary_environmental_accumulator',ss,'EvilCraft: духи')
 group('evilcraft','colossal_blood_chest exalted_crafter',matrix,'EvilCraft: автоматизация')
 group('evilcraft','promise_tier_1',industrial,'EvilCraft: улучшения I')
 group('evilcraft','promise_tier_2',ritual,'EvilCraft: улучшения II')
 group('evilcraft','promise_tier_3',ss,'EvilCraft: улучшения III')
 group('goety','soul_absorber soul_healer soul_mender animator',soul,'Goety: механизмы душ')
 group('goety','arca',ss,'Goety: хранилище душ')
 group('goety','wither_skull_focus blackguard_focus vanguard_focus vexing_focus',ss,'Goety: старший призыв')
 group('goety','thunderstorm_focus blizzard_focus sonic_boom_focus void_flash_focus',se,'Goety: старшие стихии')
 group('goety','void_staff nether_staff',conv,'Goety: высшая магия')
 group('forbidden_arcanus','clibano_core quantum_core soul_extractor',ritual,'Forbidden & Arcanus: машины')
 # Eternal Stella is a dynamic forge ritual, handled as a data resource below;
 # ore pieces and block unpacking stay ordinary material recipes.
 group('hexerei','willow_altar witch_hazel_altar book_of_shadows_altar',life,'Hexerei: ритуальная ветка')
 # Processors, inscriber, reaction chamber and crystal assembler are deliberately
 # below the engineering matrix: they supply its own ingredients.
 group('ae2','annihilation_core formation_core',life,'AE2: магические ядра')
 group('ae2','chest crafting_unit molecular_assembler',soul,'AE2: хранение и автокрафт')
 group('ae2','pattern_provider cable_pattern_provider interface cable_interface',industrial,'AE2: машинная логистика')
 group('ae2','cell_component_16k cell_component_64k',soul,'AE2: ячейки среднего объёма')
 group('ae2','cell_component_256k 64k_crafting_storage 256k_crafting_storage',ritual,'AE2: старшие ячейки и CPU')
 group('ae2','quantum_ring quantum_link spatial_io_port spatial_pylon spatial_anchor',sm,'AE2: пространство')
 group('ae2','wireless_access_point wireless_crafting_terminal',industrial,'AE2: беспроводная сеть')
 group('extendedae','machine_frame crystal_assembler',industrial,'ExtendedAE: производственная база')
 group('extendedae','ex_pattern_provider ex_pattern_provider_part ex_interface ex_interface_part pattern_provider_upgrade interface_upgrade',ritual,'ExtendedAE: расширенная логистика')
 group('extendedae','assembler_matrix_frame assembler_matrix_wall assembler_matrix_glass',matrix,'ExtendedAE: матрица автокрафта')
 group('advanced_ae','reaction_chamber',ritual,'AdvancedAE: реакционная камера')
 group('advanced_ae','quantum_unit quantum_core quantum_structure quantum_crafter quantum_accelerator',matrix,'AdvancedAE: квантовые вычисления')
 group('advanced_ae','adv_pattern_provider adv_pattern_provider_part adv_pattern_provider_upgrade small_adv_pattern_provider small_adv_pattern_provider_part',matrix,'AdvancedAE: логистика')
 group('advanced_ae','quantum_storage_component quantum_storage_128 quantum_storage_256',conv,'AdvancedAE: квантовое хранение')
 group('advanced_ae','quantum_upgrade_base',conv,'AdvancedAE: экипировка')
 group('advanced_ae','quantum_helmet quantum_chestplate quantum_leggings quantum_boots',conv,'AdvancedAE: квантовая броня')
 group('advanced_ae','flight_card regeneration_card strength_card hp_buffer_card',boss,'AdvancedAE: боевые модули')
 group('arseng','source_acceptor cable_source_acceptor',soul,'Ars Energistique')
 group('mekanism','digital_miner quantum_entangloporter',matrix,'Mekanism: пространственные машины')
 group('mekanism','sps_port supercharged_coil',conv,'Mekanism: вход в SPS')
 group('mekanism','atomic_disassembler',ritual,'Mekanism: инструменты')
 group('mekanism','meka_tool',conv,'Mekanism: MekaTool')
 group('mekanismgenerators','fusion_reactor_controller',conv,'Mekanism: термоядерная ветка')
 group('mekanism_extras','naquadah_reactor_controller',conv,'Mekanism Extras: реактор')
 group('mekanism_extras','qio_drive_gamma qio_drive_black_hole',matrix,'Mekanism Extras: QIO')
 group('mekanism_extras','qio_drive_singularity qio_drive_collapse',inf,'Mekanism Extras: старшее QIO')
 group('apotheosis','simple_reforging_table salvaging_table',industrial,'Apotheosis: ранняя перековка')
 group('apotheosis','reforging_table gem_cutting_table sigil_of_socketing sigil_of_withdrawal',lattice,'Apotheosis: мастерская')
 group('apotheosis','augmenting_table sigil_of_enhancement sigil_of_rebirth',ritual,'Apotheosis: усиление')
 group('apotheosis','frontier_spawner_upgrade_rune ascent_spawner_upgrade_rune',soul,'Apotheosis: спавнеры')
 group('apotheosis','summit_spawner_upgrade_rune pinnacle_spawner_upgrade_rune ignore_players_spawner_rune no_ai_spawner_rune',ss,'Apotheosis: старшие спавнеры')
 group('apothic_enchanting','apothic_enchanting_table hellshelf seashelf',life,'Зачарование: начальная магическая мастерская')
 group('apothic_enchanting','glowing_hellshelf blazing_hellshelf crystal_seashelf heart_seashelf geode_shelf library',lattice,'Зачарование: промышленная мастерская')
 group('apothic_enchanting','endshelf soul_touched_deepshelf soul_touched_sculkshelf',ritual,'Зачарование: старшие полки')
 group('apothic_enchanting','treasure_shelf echoing_deepshelf echoing_sculkshelf',sm,'Зачарование: древние знания')
 group('apothic_enchanting','draconic_endshelf pearl_endshelf',boss,'Зачарование: трофейные полки')
 group('apothic_enchanting','alexandrian_library',conv,'Зачарование: высшая библиотека')
 group('storagedrawers','controller controller_io compacting_drawers_3 compacting_half_drawers_3',electric,'Drawers: автоматизация')
 group('storagedrawers','diamond_storage_upgrade emerald_storage_upgrade',industrial,'Drawers: ёмкость')
 group('storagedrawers','netherite_storage_upgrade remote_upgrade remote_group_upgrade',ritual,'Drawers: старшие улучшения')
 for ns in ['sophisticatedbackpacks','sophisticatedstorage']:
  group(ns,'stack_upgrade_tier_2',electric,'Контейнеры: ёмкость II')
  group(ns,'stack_upgrade_tier_3',industrial,'Контейнеры: ёмкость III')
  group(ns,'stack_upgrade_tier_4 inception_upgrade',ritual,'Контейнеры: ёмкость IV')
  group(ns,'stack_upgrade_tier_5 stack_upgrade_omega_tier everlasting_upgrade',conv,'Контейнеры: старшие улучшения')

 # Second content pass: industrial farming, wireless power and AE capacity.
 group('extended_industrialization','steam_farmer steam_chainsaw',mount,'Extended MI: паровые инструменты')
 group('extended_industrialization','electric_farmer electric_honey_extractor electric_composter electric_brewery',life,'Extended MI: промышленная ферма')
 group('extended_industrialization','electric_chainsaw electric_mining_drill large_electric_furnace large_electric_macerator',industrial,'Extended MI: электрические машины')
 group('extended_industrialization','processing_array machine_chainer_relay tesla_coil tesla_tower tesla_receiver tesla_handheld_receiver',ritual,'Extended MI: массивы и Tesla')
 group('extended_industrialization','hv_tesla_receiver_hatch ev_tesla_receiver_hatch lethal_tesla_coil hv_solar_panel',se,'Extended MI: старшая энергетика')
 group('extended_industrialization','ultimate_laser_drill electric_beacon',conv,'Extended MI: поздняя добыча')
 group('extended_industrialization','superconductor_tesla_receiver_hatch',inf,'Extended MI: сверхпроводящая передача')
 group('industrialization_overdrive','pyrolyse_oven terminal',industrial,'Overdrive: промышленная база')
 group('industrialization_overdrive','upgrade_stacker',ritual,'Overdrive: пакетные улучшения')
 group('industrialization_overdrive','multi_processing_array',matrix,'Overdrive: массив производства')
 group('yet_another_industrialization','arboreous_greenhouse',life,'YAI: выращивание ресурсов')
 group('yet_another_industrialization','cryogenic_precipitator nuclear_rod_irradiator',ritual,'YAI: промышленная химия')
 group('yet_another_industrialization','pulse_detonation_generator',se,'YAI: импульсная энергетика')
 group('yet_another_industrialization','demon_core flight_pylon',conv,'YAI: поздние устройства')
 group('yet_another_industrialization','dragon_egg_energy_siphon',inf,'YAI: финальная энергетика')
 group('theurgy','distiller fermentation_vat mercurial_wand',life,'Theurgy: алхимический цикл')
 group('theurgy','digestion_vat sulfuric_flux_emitter',industrial,'Theurgy: промышленная алхимия')
 group('theurgy','incubator incubator_mercury_vessel incubator_salt_vessel incubator_sulfur_vessel mercury_catalyst',soul,'Theurgy: трансмутация')
 group('theurgy','reformation_source_pedestal reformation_target_pedestal reformation_result_pedestal',ritual,'Theurgy: реформация')
 group('ars_ocultas','altar',soul,'Ars Ocultas: объединение школ')
 group('megacells','mega_interface cable_mega_interface mega_pattern_provider cable_mega_pattern_provider mega_crafting_unit mega_crafting_accelerator',matrix,'MegaCells: промышленная сеть')
 group('megacells','cell_component_1m cell_component_4m 1m_crafting_storage 4m_crafting_storage',matrix,'MegaCells: ёмкость I')
 group('megacells','cell_component_16m 16m_crafting_storage mega_energy_cell',conv,'MegaCells: ёмкость II')
 group('megacells','cell_component_64m 64m_crafting_storage',inf,'MegaCells: ёмкость III')
 group('megacells','cell_component_256m 256m_crafting_storage','avaritia:infinity_ingot','MegaCells: финальная ёмкость')
 group('megacells','radioactive_cell_component mega_chemical_cell_housing',c['interface'],'MegaCells: химия и радиация')
 group('appmek','chemical_cell_housing',c['interface'],'Applied Mekanistics: химическая сеть')
 group('appflux','flux_accessor part_flux_accessor core_1k core_4k',electric,'Applied Flux: общая энергетика')
 group('appflux','core_16k core_64k induction_card',soul,'Applied Flux: промышленное хранение')
 group('appflux','core_256k core_1m core_4m',matrix,'Applied Flux: крупное хранение')
 group('appflux','core_16m',conv,'Applied Flux: позднее хранение')
 group('appflux','core_64m',inf,'Applied Flux: сверхъёмкость')
 group('appflux','core_256m','avaritia:infinity_ingot','Applied Flux: финальная ёмкость')
 group('ae2wtlib','quantum_bridge_card',sm,'AE2: беспроводные мосты')
 group('ae2wtlib','wireless_pattern_access_terminal wireless_pattern_encoding_terminal',ritual,'AE2: беспроводная автоматизация')
 group('ae2peat','pattern_encoding_access_terminal wireless_pattern_encoding_access_terminal',ritual,'AE2: управление шаблонами')

 def references(x):
  if isinstance(x,str):yield x
  elif isinstance(x,list):
   for v in x:yield from references(v)
  elif isinstance(x,dict):
   for v in x.values():yield from references(v)
 def inject(r,gate):
  # Add into a free slot; on a full grid replace ONE repeated ordinary input,
  # retaining at least one original occurrence and every unique native component.
  if 'pattern' in r and 'key' in r:
   width=max(3,max(map(len,r['pattern'])));rows=[s.ljust(width) for s in r['pattern']]
   while len(rows)<3:rows.append(' '*width)
   symbol=next(x for x in 'ZQJVUY' if x not in r['key'])
   positions=[(y,x) for y,row in enumerate(rows) for x,ch in enumerate(row) if ch==' ']
   if not positions:
    counts=collections.Counter(''.join(rows));candidates=[ch for ch,n in counts.items() if n>=2]
    if not candidates:return False
    # Most repeated material first; changing one of eight frame pieces is cheap
    # to automate and does not erase the machine's unique functional components.
    ch=max(candidates,key=lambda ch:counts[ch]);positions=[(y,x) for y,row in enumerate(rows) for x,v in enumerate(row) if v==ch]
   y,x=positions[0];rows[y]=rows[y][:x]+symbol+rows[y][x+1:];r['pattern']=rows;r['key'][symbol]=ing(gate)
   used=set(''.join(rows)+''.join(r.get('reagents',[])));r['key']={k:v for k,v in r['key'].items() if k in used};return True
  if isinstance(r.get('ingredients'),list) and r.get('type') in ['minecraft:crafting_shapeless','occultism:ritual','goety:ritual','naturesaura:tree_ritual']:
   limit=8 if r['type']=='naturesaura:tree_ritual' else 9 if r['type']=='minecraft:crafting_shapeless' else 24
   if len(r['ingredients'])>=limit:return False
   r['ingredients'].append(ing(gate));return True
  if r.get('type')=='ars_nouveau:enchanting_apparatus':
   if len(r.get('pedestalItems',[]))<8:r['pedestalItems'].append(ing(gate));return True
   counts=collections.Counter(json.dumps(v,sort_keys=True) for v in r['pedestalItems'])
   pos=next((i for i,v in enumerate(r['pedestalItems']) if counts[json.dumps(v,sort_keys=True)]>=2),None)
   if pos is None:pos=next((i for i,v in enumerate(r['pedestalItems']) if v.get('item')=='minecraft:oak_sapling'),None)
   if pos is not None:r['pedestalItems'][pos]=ing(gate);return True
  if r.get('type')=='extendedae:crystal_assembler' and len(r.get('input_items',[]))<6:
   r['input_items'].append({'ingredient':ing(gate),'amount':1});return True
  if r.get('type','').startswith(m) and 'item_inputs' in r:
   if len(r['item_inputs'])<6:r['item_inputs'].append({'item':gate,'amount':1});return True
   # The six-slot assembler cannot take a seventh input. A compiled magic
   # component replaces the control circuit, while casing, motors and all other
   # mechanical inputs and fluids stay native.
   for v in r['item_inputs']:
    if v.get('item','').endswith(('_circuit','processing_unit')):
     v.pop('tag',None);v['item']=gate;return True
  if r.get('type')=='malum:spirit_infusion':r.setdefault('extraInputs',[]).append({'item':gate,'count':1});return True
  if r.get('type')=='eidolon_repraised:crucible':r['steps'][-1]['items'].append(ing(gate));return True
  return False

 for rid,original in source.items():
  r=copy.deepcopy(index[rid]['json'] if rid in index else original)
  outs=c['result_ids'](r);out=next((s for s in outs if s in gates and s not in remove),None)
  if not out:continue
  # Recipes that convert one already gated representation into another don't
  # charge a second milestone component (e.g. provider block <-> cable part).
  inputs={k:v for k,v in r.items() if k not in ['result','output','output_item','item_outputs']}
  same=[x for x in references(inputs) if x in gates and gates[x]==gates[out] and x.split(':')[0]==out.split(':')[0]]
  if same:continue
  gate=gates[out]
  if gate in set(references(inputs)):continue
  handled=False
  if rid=='extended_industrialization:machines/electric_beacon/assembler':
   # The compiled optical core replaces emerald plates; star, glass and the
   # advanced casing retain the beacon's native identity within six inputs.
   v=next(v for v in r['item_inputs'] if v.get('tag')=='c:plates/emerald')
   v.clear();v.update(item=gate,amount=1);handled=True
  elif rid=='extended_industrialization:machines/farmer/assembler/electric':
   # Steam farmer and pipe casing remain; the extra plain casing becomes the
   # alchemical agronomy catalyst. Motors, pumps and robot arms stay intact.
   v=next(v for v in r['item_inputs'] if v.get('item')==m+'steel_machine_casing')
   v['item']=gate;handled=True
  if not handled and not inject(r,gate):missing.append({'id':rid,'out':out,'type':r.get('type'),'reason':'unsupported shape'});continue
  entry={'id':rid,'json':r}
  if rid in index:index[rid]['json']=r
  else:patches.append(entry);index[rid]=entry
  manifest.append({'id':rid,'out':out,'gate':gate,'category':categories[out],'type':r.get('type')})

 # Extra Mek tiers use the same MI assembly line, with explicit late milestones.
 for name,previous,alloy,gate,eu in [
  ('supreme','absolute','thermonuclear',conv,128),('cosmic','supreme','shining',inf,256),
  ('infinite','cosmic','spectrum','avaritia:infinity_ingot',512)]:
  out='mekanism_extras:'+name+'_control_circuit';remove.add(out)
  c['machine']('mek_extras_'+name+'_control_circuit',out,[('mekanism_extras:'+previous+'_control_circuit',2),
      ('mekanism_extras:alloy_'+alloy,2),(gate,1),(sm,1)],4,eu,600)
 for alloy,previous,catalyst,gate,eu in [('thermonuclear','radiance','mekanism:pellet_polonium',conv,128),
    ('shining','thermonuclear','mekanism:pellet_antimatter',inf,256),('spectrum','shining','avaritia:infinity_ingot',inf,512)]:
  out='mekanism_extras:alloy_'+alloy;remove.add(out)
  c['machine']('mek_extras_alloy_'+alloy,out,[('mekanism_extras:alloy_'+previous,4),(catalyst,1),(gate,1),(se,1)],8,eu,600)

 # Specialised armor belongs to the same upgrade economy and copy callback.
 slot=c['armor_slot'];paths=c['paths'];upgrade=c['upgrade'];new_armor=[]
 families={'wandering_magician':2,'wizard':2,'pumpkin':2,'pyromancer':3,'cryomancer':3,'electromancer':3,
  'priest':3,'cultist':3,'archevoker':3,'plagued':3,'shadowwalker':4,'infernal_sorcerer':4,'paladin':4}
 materials={2:'irons_spellbooks:magic_cloth',3:'irons_spellbooks:arcane_essence',4:element}
 available={s for r in source.values() for s in c['result_ids'](r)}
 for out in sorted(available):
  if not out.startswith('irons_spellbooks:') or slot(out) is None:continue
  name=out.split(':')[1];family=next((f for f in sorted(families,key=len,reverse=True) if name.startswith(f+'_')),None)
  if not family:continue
  t=families[family];i=slot(out)
  upgrade('iron_spells_'+name,out,paths['mage'][t-1][i],t,materials[t]);new_armor.append(out)
 # Trophy materials continue to matter; sets are alternatives at their tier.
 for family,t,mat in [('ironwood',2,'ironwood_ingot'),('steeleaf',3,'steeleaf_ingot'),('naga',3,'naga_scale'),
     ('fiery',4,'fiery_ingot'),('knightmetal',4,'knightmetal_ingot'),('arctic',2,'arctic_fur'),('yeti',4,'alpha_yeti_fur')]:
  for out in sorted(available):
   if out.startswith('twilightforest:'+family+'_') and slot(out) is not None:
    i=slot(out);base='minecraft:'+['','chainmail','chainmail','iron','diamond'][t]+'_'+c['slots'][i]
    upgrade('twilight_'+out.split(':')[1],out,base,t,'twilightforest:'+mat);new_armor.append(out)
 for family in ['ignitium','cursium']:
  for out in sorted(available):
   if out.startswith('cataclysm:'+family+'_') and slot(out) is not None:
    upgrade('cataclysm_'+out.split(':')[1],out,'minecraft:netherite_'+c['slots'][slot(out)],5,'cataclysm:'+family+'_ingot');new_armor.append(out)
 for family,t,mat in [('slime',2,'minecraft:slime_ball'),('prismarine',3,'minecraft:prismarine_crystals'),('steampunk',3,m+'stainless_steel_plate')]:
  for out in sorted(available):
   if out.startswith('immersive_armors:'+family+'_') and slot(out) is not None:
    upgrade('immersive_'+out.split(':')[1],out,paths['warrior'][t-1][slot(out)],t,mat);new_armor.append(out)
 for family,t in [('steel',2),('steel_ninja',2),('netherite_ninja',3),('ninja',2)]:
  for out in sorted(available):
   if not out.startswith('samurai_dynasty:'+family+'_') or slot(out) is None:continue
   # A longer family is handled by its own tier below.
   name=out.split(':')[1]
   if family=='steel' and not name[len(family)+1:] in c['slots']:continue
   i=slot(out);base='samurai_dynasty:steel_ninja_'+c['slots'][i] if t==3 else paths['samurai'][1][i]
   upgrade('samurai_alternative_'+name,out,base,t,m+('titanium_plate' if t==3 else 'steel_plate'));new_armor.append(out)
 # Optional appearances feed back into the main branches at the next tier.
 for a in armor:
  if a['id'].split('/')[-1].startswith(('warrior_t3_','warrior_t4_','samurai_t3_','samurai_t4_')):
   branch='samurai' if 'samurai_t' in a['id'] else 'warrior';i=slot(a['out'])
   ns='samurai_dynasty:' if branch=='samurai' else 'immersive_armors:'
   alternatives=sorted({b['out'] for b in armor if b['out'] in new_armor and b['tier']==a['tier']-1 and slot(b['out'])==i and b['out'].startswith(ns)})
   if alternatives:a['base']=[a['base']]+alternatives
 # Every optional T4 can continue to MekaSuit. Optional T5 can continue to Infinity.
 for a in armor:
  if a['id'].split('/')[-1].startswith('mekasuit_'):
   i=slot(a['out']);a['base']+=sorted({b['out'] for b in armor if b['out'] in new_armor and b['tier']==4 and slot(b['out'])==i})
  elif a['tier']==6:
   i=slot(a['out']);a['base']+=sorted({b['out'] for b in armor if b['out'] in new_armor and b['tier']==5 and slot(b['out'])==i})
 # Weapons keep their original identity; only stronger crafted families get gates.
 # This separate pass catches all variants of runic weapons without touching loot.
 for rid,original in source.items():
  outs=c['result_ids'](original)
  out=next((s for s in outs if (s.startswith('simplyswords:runic_') or s.startswith('samurai_dynasty:') and any(x in s for x in ['netherite_katana','netherite_naginata','netherite_odachi']))),None)
  if not out or out in remove or original.get('type') not in ['minecraft:crafting_shaped','minecraft:crafting_shapeless']:continue
  r=copy.deepcopy(original)
  if inject(r,soul):
   if rid in index:index[rid]['json']=r
   else:patches.append({'id':rid,'json':r});index[rid]=patches[-1]
   manifest.append({'id':rid,'out':out,'gate':soul,'category':'Оружие: руническая ковка','type':r['type']})
 for rid,original in source.items():
  outs=c['result_ids'](original)
  # Keep vanilla smithing's component copying, using the elemental insulator as
  # the consumed magical template; steel weapon and netherite ingot stay intact.
  if original.get('type')=='minecraft:smithing_transform':
   output=next((s for s in outs if s.startswith('samurai_dynasty:') and s.endswith('_netherite')),None)
   if output and output not in remove:
    r=copy.deepcopy(original);r['template']=ing(element)
    if rid in index:index[rid]['json']=r
    else:patches.append({'id':rid,'json':r});index[rid]=patches[-1]
    manifest.append({'id':rid,'out':output,'gate':element,'category':'Оружие: нетеритовая ковка','type':r['type']})
 resources=[]
 forge_gates={'upgrade_tier_2':lattice,'upgrade_tier_3':se,'upgrade_tier_4':conv,'upgrade_tier_5':inf,
  'eternal_stella':conv,'boss_catcher':inf,'quantum_catcher':ritual,'quantum_injector':matrix,
  'soul_binding_crystal':ss,'sea_prism':se,'smelter_prism':industrial,'terrastomp_prism':ritual,'whirlwind_prism':se}
 for slot_name in c['slots']:
  forge_gates['draco_arcanus_'+slot_name]=c['cores'][5]
  forge_gates['tyr_'+slot_name]=inf
 jar=c['D']['forbidden']['jar']
 with zipfile.ZipFile(jar) as z:
  for name,gate in forge_gates.items():
   path='data/forbidden_arcanus/forbidden_arcanus/hephaestus_forge/ritual/'+name+'.json'
   r=json.loads(z.read(path));inputs=r['inputs']
   # The forge has eight pedestals. Retain every original ingredient type when
   # making room for a progression catalyst in an already full ritual.
   if sum(x['amount'] for x in inputs)>=8:
    donor=max(inputs,key=lambda x:x['amount']);assert donor['amount']>1,path;donor['amount']-=1
   inputs.append({'amount':1,'ingredient':ing(gate)})
   assert sum(x['amount'] for x in inputs)<=8,path
   dest=root/'overrides/common/kubejs'/path;dest.parent.mkdir(parents=True,exist_ok=True)
   dest.write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf-8')
   resources.append({'path':path,'gate':gate,'name':name,'pedestals':sum(x['amount'] for x in inputs)})
 # Native forge transmutation keeps equipment components; either T5 family can
 # be upgraded into the finale through our existing armor-copy recipe.
 for a in armor:
  if a['tier']==6:
   s=c['slots'][slot(a['out'])]
   a['base']+=['forbidden_arcanus:draco_arcanus_'+s,'forbidden_arcanus:tyr_'+s]
 c['integration']={'recipes':manifest,'data_resources':resources,'unsupported':missing,'armor':new_armor,
  'scope':'Capabilities and special gear; ordinary building blocks, food, basic tools and native loot remain native.'}
 (root/'build/recipe-integration.json').write_text(json.dumps(c['integration'],ensure_ascii=False,indent=2),'utf-8')
 print('Integration pass:',len(manifest),'gated native recipes,',len(resources),'forge rituals,',len(new_armor),'additional armor upgrades;',len(missing),'unsupported')
