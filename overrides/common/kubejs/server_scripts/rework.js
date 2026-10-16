// Recipe rework layered on top of the generated progression plan (RECIPE-REWORK.md).
// Runs after progression.js and reads its AI_PLAN. Every recipe added here uses a
// kubejs:rework/ id, which zz_progression_security.js treats as approved.
const AI_RW_K = 'kubejs:';
const AI_RW_ALL = AI_PLAN.recipes.concat(AI_PLAN.patches);
const AI_RW_BY_ID = {};
AI_RW_ALL.forEach(r => AI_RW_BY_ID[r.id] = r);

function aiRwId(id) { return 'kubejs:rework/' + id.replace(':', '/'); }
function aiRwOut(r) {
  let j = r.json;
  let x = j.result || j.output || (j.item_outputs || [])[0] || {};
  return String(x.id || x.item || '');
}
function aiRwItems(list) { return list.map(x => typeof x === 'string' ? {item: x} : x); }

// Big 9x9 recipes: each mask gives a different silhouette with the same cost.
// '#' = frame material P; '.' = mirrored pairs assigned A..K in reading order; the
// one centre-column '.' = L. Every mask fills the full 9x9 bounding box, because
// Avaritia mis-indexes recipes that are trimmed wider than tall (JEI drops them).
const AI_RW_MASKS = {
  heart:   ['#..   ..#', '#...#...#', ' ... ... ', '  .. ..  ', '   #.#   ', '    #    ', '  .   .  ', '    #    ', '#   #   #'],
  eye:     ['#       #', '  .. ..  ', ' ..   .. ', '.. ### ..', '..# . #..', '.. ### ..', '         ', ' .     . ', '#       #'],
  skull:   ['#... ...#', '.   #   .', '. ## ## .', '.  . .  .', ' .. # .. ', '   ...   ', '  . # .  ', '    #    ', '#       #'],
  quad:    ['#..   ..#', '...   ...', '.. # # ..', '    #    ', '#.. . ..#', '    #    ', '.. # # ..', '         ', '#       #'],
  diamond: ['#  . .  #', '  .   .  ', ' .  #  . ', '. .# #. .', '. # . # .', '. .# #. .', ' .  #  . ', '  .   .  ', '#  . .  #'],
  cross:   ['#  . .  #', '   . .   ', '  #   #  ', '.. . . ..', '...#.#...', '.. . . ..', '  #   #  ', '   # #   ', '#       #'],
  ring:    ['#..   ..#', '.       .', '.  ...  .', '   # #   ', '#. # # .#', '   # #   ', '.  . .  .', '.       .', '#..   ..#']
};
function aiRwMask(mask) {
  let letters = 'ABCDEFGHIJK';
  let next = 0;
  let grid = mask.map(row => row.split(''));
  for (let r = 0; r < 9; r++) for (let c = 0; c < 9; c++) {
    if (grid[r][c] === '#') grid[r][c] = 'P';
    else if (grid[r][c] === '.') {
      if (c === 4) grid[r][c] = 'L';
      else if (c < 4) { grid[r][c] = letters[next]; grid[r][8 - c] = letters[next]; next++; }
    }
  }
  return grid.map(row => row.join(''));
}
// Tool silhouettes use the same A..L/P keys as the generated tool recipes.
const AI_RW_TOOLS = {
  sword:  ['       PP', '      PIP', '     PKP ', '  D PJP  ', '  GBPP   ', '  ACE    ', '  F      ', ' H       ', 'L        '],
  pick:   ['PPPPIPPPP', 'P  JKJ  P', '    A    ', '   DBE   ', '    C    ', '   FGH   ', '    L    ', '    C    ', '    P    '],
  shovel: ['   PPP   ', '  PPIPP  ', '  PJKJP  ', '   PAP   ', '    B    ', '   DCE   ', '   FLG   ', '    H    ', '    C    '],
  bow:    ['  PPJ    ', ' P   K   ', 'P    D   ', 'P   A B  ', 'I    C  E', 'P   F G  ', 'P    H   ', ' P   L   ', '  PPJ    ']
};
const AI_RW_SHAPES = {
  'kubejs:progression/seal_life': 'heart', 'kubejs:progression/seal_mind': 'eye',
  'kubejs:progression/seal_soul': 'skull', 'kubejs:progression/seal_elements': 'quad',
  'kubejs:progression/enchantment_lattice': 'diamond', 'kubejs:progression/expedition_emblem': 'cross',
  'kubejs:progression/convergence_core': 'diamond', 'kubejs:progression/infinity_stabilizer': 'cross',
  'kubejs:progression/mi_quantum_upgrade': 'cross', 'kubejs:progression/infinity_totem': 'heart',
  'kubejs:progression/armor_core_t3': 'ring', 'kubejs:progression/armor_core_t4': 'ring',
  'kubejs:progression/armor_core_t5': 'ring', 'kubejs:progression/armor_core_t6': 'ring',
  'kubejs:progression/armor_core_t7': 'ring', 'kubejs:progression/armor_core_t8': 'ring',
  'kubejs:progression/tool_infinity_sword': 'sword', 'kubejs:progression/tool_upgrade_nanosaber': 'sword',
  'kubejs:progression/mi_quantum_sword': 'sword', 'kubejs:progression/tool_infinity_pickaxe': 'pick',
  'kubejs:progression/tool_infinity_axe': 'pick', 'kubejs:progression/tool_infinity_hoe': 'pick',
  'kubejs:progression/tool_upgrade_omni_tool': 'pick', 'kubejs:progression/tool_infinity_shovel': 'shovel',
  'kubejs:progression/tool_infinity_bow': 'bow', 'kubejs:progression/tool_infinity_crossbow': 'bow'
};

// Bottleneck components are swapped for branch-specific parts in chosen groups.
function aiRwSwap(r) {
  let id = r.id, out = aiRwOut(r), ns = out.split(':')[0];
  // The generator wrote Ars Elemental's essence under a wrong namespace.
  let s = {'sauce:anima_essence': 'ars_elemental:anima_essence'};
  if (id.indexOf('tr_machine_') >= 0) {
    if (/storage_unit|tank_unit/.test(out)) s['kubejs:reborn_interface'] = AI_RW_K + 'iesnium_plate';
    else if (/solar/.test(out)) s['kubejs:reborn_interface'] = AI_RW_K + 'sky_plate';
  }
  if (id.indexOf('ar_crafting_generator_') >= 0)
    s['kubejs:reborn_interface'] = /solar/.test(out) ? AI_RW_K + 'sky_plate' : AI_RW_K + 'arcane_lens';
  if (id.indexOf('ar_crafting_machine_') >= 0) s['kubejs:reborn_interface'] = AI_RW_K + 'hallowed_circuit';
  if (['ae2', 'ae2wtlib', 'extendedae', 'advanced_ae', 'ae2peat'].indexOf(ns) >= 0) {
    s['kubejs:ritual_frame'] = AI_RW_K + 'resonance_core';
    s['kubejs:industrial_focus'] = AI_RW_K + 'iesnium_plate';
  }
  if (['extended_industrialization', 'modern_industrialization', 'yet_another_industrialization', 'industrialization_overdrive'].indexOf(ns) >= 0)
    s['kubejs:ritual_frame'] = AI_RW_K + 'enchanted_titanium_plate';
  if (ns === 'irons_spellbooks') s['kubejs:ritual_frame'] = AI_RW_K + 'mithril_mesh';
  if (ns === 'storagedrawers') s['kubejs:industrial_focus'] = AI_RW_K + 'iesnium_plate';
  if (ns === 'betterend' || ns === 'betternether') {
    s['kubejs:ritual_frame'] = AI_RW_K + 'deorum_plate';
    s['kubejs:industrial_focus'] = 'malum:soul_stained_steel_plating';
  }
  return s;
}

// event.remove cannot remove recipes that progression.js adds in the same event, so
// plan recipes are rewritten or dropped here, at load time, before its handler runs.
// Plan "patches" replace native recipes: dropping one leaves the native recipe, which
// the event handler below then removes normally.
const AI_RW_DROP = {
  'kubejs:progression/tr_machine_matter_fabricator': 1, 'kubejs:progression/tr_machine_industrial_electrolyzer': 1,
  'kubejs:progression/tr_machine_plasma_generator': 1, 'kubejs:progression/ar_crafting_machine_charge_pad': 1,
  'kubejs:progression/ar_crafting_generator_ray_generator': 1, 'kubejs:progression/ar_crafting_generator_ray_generator_5_2': 1,
  'ars_nouveau:basic_spell_turret': 1, 'ars_nouveau:relay': 1, 'malum:spirit_altar': 1,
  'occultism:crafting/storage_controller': 1, 'occultism:crafting/storage_controller_dark': 1
};
['knife', 'axe', 'hoe', 'pickaxe', 'shovel', 'sword'].forEach(t => AI_RW_DROP['kubejs:progression/late_tool/malum/soul_stained_steel_' + t] = 1);
function aiRwPrepare(list) {
  var n = 0;
  for (var i = list.length - 1; i >= 0; i--) {
    var r = list[i];
    if (AI_RW_DROP[r.id]) { list.splice(i, 1); n++; continue; }
    var swaps = aiRwSwap(r), shape = AI_RW_SHAPES[r.id];
    var text = JSON.stringify(r.json), touched = false;
    Object.keys(swaps).forEach(from => {
      if (text.indexOf('"' + from + '"') >= 0) { text = text.split('"' + from + '"').join('"' + swaps[from] + '"'); touched = true; }
    });
    var json = JSON.parse(text);
    if (shape) {
      var keys = Object.keys(json.key).sort().join('');
      if (keys === 'ABCDEFGHIJKLP') { json.pattern = AI_RW_TOOLS[shape] || aiRwMask(AI_RW_MASKS[shape]); touched = true; }
      else console.warn('[Arcane Rework] unexpected keys ' + keys + ' in ' + r.id);
    }
    if (touched) { r.json = json; n++; }
  }
  return n;
}
const AI_RW_PREPARED = aiRwPrepare(AI_PLAN.recipes) + aiRwPrepare(AI_PLAN.patches);

// Machine silhouettes (CRAFTING-TODO.md, point 5): the Tech Reborn / Advanced Reborn machine
// recipes all shared one column layout. Each machine now gets a layout by its function; the
// ingredient kinds stay (h hull H, c circuit C, p plate P, g interface G, x = the machine's
// own parts, cycled by their original counts). Every layout is 9 rows and at most 9 wide.
const AI_RW_MACHINE_LAYOUTS = {
  crusher: ['p x   x p', 'px x x xp', ' pxx xxp ', '  pchcp  ', '  pcxcp  ', '   pgp   ', '   ppp   ', '  p   p  ', ' pp   pp '],
  furnace: ['  ppppp  ', ' pc   cp ', 'pc xxx cp', 'p xxhxx p', 'p  xgx  p', 'pc xxx cp', ' pc   cp ', '  ppppp  ', '   p p   '],
  vault: ['ppppppppp', 'pxxxcxxxp', 'px     xp', 'pc  h  cp', 'px  g  xp', 'pc     cp', 'pxxxcxxxp', 'ppppppppp', 'p       p'],
  panel: ['xxxxxxxxx', 'x c x c x', 'xxxxxxxxx', '    p    ', '   php   ', '   pgp   ', '  pcpcp  ', ' pp   pp ', 'pp     pp'],
  tower: ['   ppp   ', '  pcxcp  ', '  pxhxp  ', '  pcxcp  ', '   pgp   ', '  pxxxp  ', '  p x p  ', '  pp pp  ', '  p   p  ']
};
function aiRwMachineLayout(out) {
  if (/grinder|crusher|rock_cutter|extractor|compressor|wire_mill|sawmill|logging/.test(out)) return 'crusher';
  if (/furnace|smelt|blast|plasma|generator(?!_)|fuel|thermal|electrolyzer|distillation|charge/.test(out)) return 'furnace';
  if (/storage_unit|tank_unit|_su$|storage|orbpack/.test(out)) return 'vault';
  if (/solar|ray_/.test(out)) return 'panel';
  return 'tower';
}
function aiRwReshapeMachine(r) {
  if (!/kubejs:progression\/(tr_machine_|ar_crafting_)/.test(r.id) || r.json.type !== 'avaritia:shaped_table') return false;
  var json = r.json, counts = {};
  json.pattern.join('').split('').forEach(ch => { if (ch !== ' ') counts[ch] = (counts[ch] || 0) + 1; });
  // Ingredient amounts stay exactly as before; only their placement changes. Each role's
  // slots are filled centre-out in mirrored pairs, so the silhouette stays symmetric and
  // unused slots stay empty.
  var own = Object.keys(counts).filter(ch => !/[HCPG]/.test(ch)), parts = [];
  own.forEach(ch => { for (var n = 0; n < counts[ch]; n++) parts.push(ch); });
  var supply = {h: counts.H ? ['H'] : [], c: [], p: [], g: counts.G ? ['G'] : [], x: parts};
  for (var n = 0; n < (counts.C || 0); n++) supply.c.push('C');
  for (var n2 = 0; n2 < (counts.P || 0); n2++) supply.p.push('P');
  var out = String((json.result || {}).id || ''), layout = AI_RW_MACHINE_LAYOUTS[aiRwMachineLayout(out)];
  var grid = layout.map(row => row.split('').map(() => ' '));
  ['h', 'g', 'c', 'p', 'x'].forEach(role => {
    var slots = [];
    layout.forEach((row, y) => row.split('').forEach((ch, x) => { if (ch === role) slots.push([y, x]); }));
    slots.sort((a, b) => Math.abs(a[1] - 4) - Math.abs(b[1] - 4) || a[0] - b[0] || a[1] - b[1]);
    var items = supply[role];
    slots.forEach(sl => { if (items.length && grid[sl[0]][sl[1]] === ' ') grid[sl[0]][sl[1]] = items.shift(); });
    // Anything left over (layout has fewer slots of this role) goes to free x/p slots.
    if (items.length) layout.forEach((row, y) => row.split('').forEach((ch, x) => {
      if (items.length && ch !== ' ' && grid[y][x] === ' ') grid[y][x] = items.shift();
    }));
  });
  json.pattern = grid.map(row => row.join(''));
  // Keep the bounding box full height so Avaritia never sees a recipe wider than tall.
  var top = json.pattern.findIndex(row => row.trim()), bottom = json.pattern.length - 1 - json.pattern.slice().reverse().findIndex(row => row.trim());
  var mn = 9, mx = -1;
  json.pattern.forEach(row => row.split('').forEach((ch, x) => { if (ch !== ' ') { mn = Math.min(mn, x); mx = Math.max(mx, x); } }));
  if (mx - mn > bottom - top) return false;   // would be wide: keep the reshaped grid only if safe
  return true;
}AI_PLAN.recipes.forEach(r => {
  var before = r.json.pattern ? r.json.pattern.slice() : null;
  if (before && !aiRwReshapeMachine(r) && r.json.type === 'avaritia:shaped_table') r.json.pattern = before;
});
// Table ladder (GEAR-TIERS.md): the 9x9 table now also needs the 7x7 End table.
AI_PLAN.recipes.forEach(r => {
  if (r.id === 'kubejs:progression/industrial_extreme_table')
    r.json.item_inputs.push({item: 'avaritia:end_crafting_table', amount: 1});
});

ServerEvents.recipes(event => {
  let changed = 0;
  function add(name, json) { event.custom(json).id('kubejs:rework/' + name); changed++; }

  // 1. New magic<->tech components.
  [['sky_plate', 'naturesaura:sky_ingot'], ['iesnium_plate', 'occultism:iesnium_ingot'],
   ['deorum_plate', 'forbidden_arcanus:deorum_ingot']].forEach(p =>
    add('component/' + p[0], {type: 'modern_industrialization:compressor', eu: 16, duration: 200,
      item_inputs: [{item: p[1], amount: 1}], item_outputs: [{item: AI_RW_K + p[0], amount: 1}]}));
  add('component/soul_stained_steel_plating', {type: 'modern_industrialization:compressor', eu: 16, duration: 200,
    item_inputs: [{item: 'malum:soul_stained_steel_ingot', amount: 1}],
    item_outputs: [{item: 'malum:soul_stained_steel_plating', amount: 1}]});
  add('component/mithril_mesh', {type: 'modern_industrialization:wiremill', eu: 16, duration: 200,
    item_inputs: [{item: 'irons_spellbooks:mithril_ingot', amount: 1}],
    item_outputs: [{item: AI_RW_K + 'mithril_mesh', amount: 2}]});
  add('component/enchanted_titanium_plate', {type: 'ars_nouveau:enchanting_apparatus',
    reagent: {item: 'modern_industrialization:titanium_plate'},
    pedestalItems: aiRwItems(['ars_nouveau:air_essence', 'ars_nouveau:earth_essence', 'ars_nouveau:fire_essence', 'ars_nouveau:water_essence']),
    result: {id: AI_RW_K + 'enchanted_titanium_plate', count: 2}, sourceCost: 2000, keepNbtOfReagent: false});
  add('component/hallowed_circuit', {type: 'malum:spirit_infusion',
    input: {item: 'techreborn:advanced_circuit', count: 2},
    extraInputs: [{item: 'malum:hallowed_gold_ingot', count: 2}, {item: 'malum:soul_stained_steel_plating', count: 2}],
    spirits: [{type: 'malum:sacred', count: 4}, {type: 'malum:arcane', count: 2}],
    result: {id: AI_RW_K + 'hallowed_circuit', count: 2}});
  add('component/resonance_core', {type: 'goety:ritual', ritual_type: 'goety:craft',
    activation_item: {item: 'modern_industrialization:processing_unit'}, craftType: 'magic', soulCost: 15, duration: 30,
    ingredients: aiRwItems(['goety:resonance_crystal', 'kubejs:soul_stabilizer', 'ae2:fluix_pearl',
      'occultism:spirit_attuned_gem', 'irons_spellbooks:arcane_essence']),
    result: {id: AI_RW_K + 'resonance_core', count: 4}});
  add('component/arcane_lens', {type: 'modern_industrialization:assembler', eu: 32, duration: 300,
    item_inputs: [{item: 'forbidden_arcanus:arcane_crystal', amount: 2}, {item: 'minecraft:ender_eye', amount: 1},
      {item: 'minecraft:glass', amount: 2}],
    item_outputs: [{item: AI_RW_K + 'arcane_lens', amount: 2}]});

  // 2 and 4 (bottlenecks, silhouettes) were applied to AI_PLAN at load time above.
  changed += AI_RW_PREPARED;

  // 3a. Tech machines built on magic stations (their plan recipes were dropped above).
  add('altar/matter_fabricator', {type: 'occultism:ritual', ritual_type: 'occultism:craft', pentacle_id: 'occultism:craft_djinni',
    activation_item: {item: 'occultism:book_of_binding_bound_djinni'}, duration: 120,
    ingredients: aiRwItems(['techreborn:industrial_machine_frame', 'techreborn:lapotronic_orb', 'techreborn:energy_flow_chip',
      'techreborn:energy_flow_chip', 'techreborn:extractor', 'modern_industrialization:quantum_machine_hull',
      'kubejs:reborn_interface', 'kubejs:hallowed_circuit']),
    result: {id: 'techreborn:matter_fabricator', count: 1}, ritual_dummy: {id: 'techreborn:matter_fabricator', count: 1}});
  add('altar/industrial_electrolyzer', {type: 'ars_nouveau:enchanting_apparatus',
    reagent: {item: 'techreborn:advanced_machine_frame'},
    pedestalItems: aiRwItems(['techreborn:extractor', 'techreborn:extractor', 'techreborn:advanced_circuit', 'techreborn:advanced_circuit',
      'kubejs:enchanted_titanium_plate', 'kubejs:enchanted_titanium_plate', 'ars_nouveau:water_essence', 'ars_nouveau:fire_essence']),
    result: {id: 'techreborn:industrial_electrolyzer', count: 1}, sourceCost: 5000, keepNbtOfReagent: false});
  add('altar/plasma_generator', {type: 'malum:spirit_infusion',
    input: {item: 'techreborn:solid_fuel_generator', count: 1},
    extraInputs: [{item: 'techreborn:hv_transformer', count: 1}, {item: 'techreborn:tungstensteel_plate', count: 3},
      {item: 'techreborn:energy_flow_chip', count: 2}, {item: 'modern_industrialization:quantum_machine_hull', count: 1},
      {item: 'techreborn:industrial_circuit', count: 2}],
    spirits: [{type: 'malum:infernal', count: 16}, {type: 'malum:arcane', count: 8}],
    result: {id: 'techreborn:plasma_generator', count: 1}});
  add('altar/charge_pad', {type: 'naturesaura:tree_ritual', sapling: {item: 'naturesaura:ancient_sapling'}, time: 300,
    ingredients: aiRwItems(['techreborn:red_cell_battery', 'techreborn:red_cell_battery', 'techreborn:insulated_hv_cable',
      'techreborn:insulated_hv_cable', 'techreborn:advanced_circuit', 'kubejs:sky_plate', 'kubejs:sky_plate',
      'modern_industrialization:advanced_machine_hull']),
    output: {id: 'advanced_reborn:charge_pad', count: 1}});
  add('altar/ray_generator', {type: 'eidolon_repraised:crucible', steps: [
      {items: aiRwItems(['advanced_reborn:ray_solar_panel', 'techreborn:carbon_plate', 'techreborn:carbon_plate'])},
      {stirs: 1, items: aiRwItems(['minecraft:glowstone', 'minecraft:glowstone', 'kubejs:arcane_lens'])},
      {stirs: 2, items: aiRwItems(['techreborn:advanced_circuit', 'techreborn:advanced_circuit', 'modern_industrialization:advanced_machine_hull'])}],
    result: {id: 'advanced_reborn:ray_generator', count: 1}});

  // BetterEnd's own alloying / infusion / anvil recipes (BCLib types) fail to load in this
  // pack: KubeJS rewrites their {"item": ...} results to {"id": ...}, which BCLib cannot read
  // (PACK-ANALYSIS.md, point 1). Its key materials are made at working stations instead.
  add('betterend/ender_dust', {type: 'modern_industrialization:macerator', eu: 2, duration: 100,
    item_inputs: [{item: 'minecraft:ender_pearl', amount: 1}], item_outputs: [{item: 'betterend:ender_dust', amount: 2}]});
  add('betterend/terminite_ingot', {type: 'modern_industrialization:mixer', eu: 8, duration: 200,
    item_inputs: [{item: 'minecraft:iron_ingot', amount: 1}, {item: 'betterend:ender_dust', amount: 2}],
    item_outputs: [{item: 'betterend:terminite_ingot', amount: 1}]});
  add('betterend/aeternium_ingot', {type: 'modern_industrialization:blast_furnace', eu: 32, duration: 400,
    item_inputs: [{item: 'betterend:terminite_ingot', amount: 1}, {item: 'minecraft:netherite_ingot', amount: 1}],
    item_outputs: [{item: 'betterend:aeternium_ingot', amount: 1}]});
  [['eternal_crystal', 'minecraft:end_crystal', ['betterend:crystal_shards', 'betterend:crystal_shards', 'betterend:crystal_shards', 'betterend:crystal_shards',
      'betterend:ender_shard', 'betterend:ender_shard', 'betterend:ender_shard', 'betterend:ender_shard'], 3000],
   ['enchanted_petal', 'betterend:hydralux_petal', ['betterend:crystal_shards', 'betterend:crystal_shards', 'betterend:crystal_shards', 'betterend:crystal_shards'], 500],
   ['enchanted_membrane', 'minecraft:phantom_membrane', ['betterend:crystal_shards', 'betterend:crystal_shards', 'betterend:crystal_shards', 'betterend:crystal_shards'], 500],
   ['flavolite_runed', 'betterend:flavolite_polished', ['betterend:crystal_shards', 'betterend:crystal_shards', 'betterend:crystal_shards', 'betterend:crystal_shards'], 300]
  ].forEach(r => add('betterend/' + r[0], {type: 'ars_nouveau:enchanting_apparatus', reagent: {item: r[1]}, pedestalItems: aiRwItems(r[2]),
    result: {id: 'betterend:' + r[0], count: 1}, sourceCost: r[3], keepNbtOfReagent: false}));

  // Recipe audit (CRAFTING-TODO.md, point 5): bookshelf -> 2 haunted bookshelves -> 2
  // bookshelves is a cheap bookshelf dupe (2 books instead of 3); drop the way back.
  event.remove({id: 'goety:bookshelf_vanilla'});

  // Avaritia tables by MI stage: 5x5 Nether table in the steam age, 7x7 End table in the
  // electric age (crafted in the 5x5), 9x9 Extreme table in the MI assembler (needs the 7x7).
  event.remove({id: 'avaritia:nether_crafting_table'});
  event.remove({id: 'avaritia:end_crafting_table'});
  add('table/nether_crafting_table', {type: 'minecraft:crafting_shaped', pattern: ['PLP', 'NCN', 'PNP'],
    key: {P: {item: 'modern_industrialization:bronze_plate'}, L: {item: 'kubejs:ritual_mount'},
      N: {item: 'minecraft:nether_bricks'}, C: {item: 'minecraft:crafting_table'}},
    result: {id: 'avaritia:nether_crafting_table', count: 1}});
  add('table/end_crafting_table', {type: 'avaritia:shaped_table', tier: 2,
    pattern: ['PEPEP', 'EOLOE', 'PLTLP', 'EOLOE', 'PEPEP'],
    key: {P: {item: 'modern_industrialization:steel_plate'}, L: {item: 'kubejs:electrical_focus'},
      E: {item: 'minecraft:ender_pearl'}, O: {item: 'minecraft:obsidian'}, T: {item: 'avaritia:nether_crafting_table'}},
    result: {id: 'avaritia:end_crafting_table', count: 1}});

  // 3b. Mid/late magic blocks assembled by MI.
  function assembler(name, out, inputs, eu) {
    add('assembler/' + name, {type: 'modern_industrialization:assembler', eu: eu, duration: 300,
      item_inputs: inputs.map(x => x[0].charAt(0) === '#' ? {tag: x[0].substring(1), amount: x[1]} : {item: x[0], amount: x[1]}),
      item_outputs: [{item: out, amount: 1}]});
  }
  event.remove({id: 'ars_nouveau:basic_spell_turret'});
  assembler('basic_spell_turret', 'ars_nouveau:basic_spell_turret',
    [['#c:gems/source', 3], ['modern_industrialization:gold_plate', 3], ['minecraft:redstone_block', 1], ['kubejs:electrical_focus', 1]], 16);
  event.remove({id: 'ars_nouveau:relay'});
  assembler('relay', 'ars_nouveau:relay',
    [['modern_industrialization:gold_plate', 4], ['#c:storage_blocks/source', 1], ['kubejs:electrical_focus', 1]], 16);
  event.remove({id: 'malum:spirit_altar'});
  assembler('spirit_altar', 'malum:spirit_altar',
    [['#malum:runewood_planks', 4], ['malum:refined_soulstone', 1], ['modern_industrialization:gold_plate', 2], ['kubejs:industrial_focus', 1]], 16);
  [['', 'occultism:storage_controller_base'], ['_dark', 'occultism:storage_controller_base_dark']].forEach(v => {
    event.remove({id: 'occultism:crafting/storage_controller' + v[0]});
    assembler('storage_controller' + v[0], 'occultism:storage_controller' + v[0],
      [[v[1], 1], ['occultism:dimensional_matrix', 1], ['kubejs:alchemical_catalyst', 1], ['kubejs:iesnium_plate', 2]], 32);
  });

  // Malum soul-stained steel tools: their late-tool plan recipes are dropped above and the
  // tier ladder (rework_ladder.js) gives each one a step from the tier below.

  // 5. Armor, weapon and tool upgrades moved to the tier ladder (rework_ladder.js).

  console.info('[Arcane Rework] ' + changed + ' recipes added or rebuilt');
});
