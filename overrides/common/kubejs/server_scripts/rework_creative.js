// Creative items as the finale of their field (CRAFTING-TODO.md, point 4).
// Three steps: the field's apex items -> a field matrix made at a station of that field ->
// a final 9x9 recipe with its own pattern, the item's apex part and two themed singularities.
// The old one-pattern-fits-all plan recipes (kubejs:progression/creative/*) are dropped from
// AI_PLAN at load time, before progression.js adds them.
for (let i = AI_PLAN.recipes.length - 1; i >= 0; i--)
  if (AI_PLAN.recipes[i].id.indexOf('kubejs:progression/creative/') === 0) AI_PLAN.recipes.splice(i, 1);

function aiCrSing(name) {
  return {type: 'avaritia:stack', item: {id: 'avaritia:singularity', count: 1, components: {'avaritia:singularity_id': 'avaritia:' + name}}};
}
// Final patterns (I infinity ingot, X catalyst, N neutron ingot, Z infinity stabilizer,
// Q field matrix, A apex part, 1/2 singularities, U UU-matter, C T8 armor core).
const AI_CR_PATTERNS = {
  grid: ['INNNINNNI', 'NA  1  AN', 'N 2 Q 2 N', 'N  ZXZ  N', 'I1QX X Q1', 'N  ZXZ  N', 'N 2 Q 2 N', 'NA  1  AN', 'INNNINNNI'],
  bolt: ['     IIAN', '    IQ1N ', '   IXZN  ', '  IQ2N   ', ' IIXXII  ', '   N2QI  ', '  NZXI   ', ' N1QI    ', 'NAII     '],
  drop: ['    I    ', '   INI   ', '  IN1NI  ', '  NQ2QN  ', ' IN2X2NI ', ' NQZXZQN ', ' IN1A1NI ', '  INUNI  ', '   III   '],
  pentagram: ['    X    ', '   N N   ', '  1QAQ1  ', 'IIIZ ZIII', ' N2 C 2N ', '  N U N  ', ' N Q Q N ', 'N 1   1 N', 'IX     XI'],
  cross: ['   IAI   ', '   N1N   ', '   NQN   ', 'IN2ZXZ2NI', 'A1QXCXQ1A', 'IN2ZXZ2NI', '   NQN   ', '   N1N   ', '   IAI   ']
};
// id, field, pattern, apex part, singularity 1, singularity 2
const AI_CR_ITEMS = [
  ['ae2:creative_storage_cell', 'storage', 'grid', 'megacells:item_storage_cell_256m', 'iron', 'tin'],
  ['ae2:creative_energy_cell', 'energy', 'bolt', 'ae2:dense_energy_cell', 'gold', 'copper'],
  ['modern_industrialization:creative_barrel', 'storage', 'cross', 'modern_industrialization:quantum_barrel', 'iron', 'nickel'],
  ['modern_industrialization:creative_storage_unit', 'energy', 'grid', 'modern_industrialization:quantum_upgrade', 'copper', 'silver'],
  ['modern_industrialization:creative_tank', 'fluid', 'drop', 'modern_industrialization:quantum_tank', 'lead', 'silver'],
  ['techreborn:creative_storage_unit', 'storage', 'grid', 'techreborn:quantum_storage_unit', 'tin', 'bronze'],
  ['techreborn:creative_tank_unit', 'fluid', 'drop', 'techreborn:quantum_tank_unit', 'lead', 'nickel'],
  ['techreborn:creative_solar_panel', 'energy', 'bolt', 'techreborn:quantum_solar_panel', 'gold', 'bronze'],
  ['storagedrawers:creative_storage_upgrade', 'storage', 'cross', 'storagedrawers:emerald_storage_upgrade', 'iron', 'gold'],
  ['storagedrawers:creative_vending_upgrade', 'storage', 'cross', 'storagedrawers:diamond_storage_upgrade', 'gold', 'copper'],
  ['modularrouters:creative_module', 'storage', 'cross', 'modularrouters:modular_router', 'copper', 'tin'],
  ['ars_nouveau:creative_spell_book', 'arcane', 'pentagram', 'ars_nouveau:archmage_spell_book', 'gold', 'silver'],
  ['ars_nouveau:creative_source_jar', 'arcane', 'pentagram', 'ars_nouveau:source_gem_block', 'silver', 'nickel'],
  ['evilcraft:creative_blood_drop', 'arcane', 'drop', 'evilcraft:blood_orb_filled', 'lead', 'iron'],
  ['hexerei:creative_waxing_kit', 'arcane', 'pentagram', 'hexerei:crystal_ball', 'bronze', 'gold']
];

ServerEvents.recipes(event => {
  // Step 2: field matrices, each at a station of its field.
  event.custom({type: 'modern_industrialization:assembler', eu: 2048, duration: 1200,
    item_inputs: [{item: 'megacells:item_storage_cell_256m', amount: 1}, {item: 'techreborn:quantum_storage_unit', amount: 1},
      {item: 'modern_industrialization:quantum_barrel', amount: 1}, {item: 'kubejs:engineering_matrix', amount: 4},
      {item: 'kubejs:iesnium_plate', amount: 8}, {item: 'kubejs:infinity_stabilizer', amount: 1}],
    item_outputs: [{item: 'kubejs:infinite_storage_matrix', amount: 1}]}).id('kubejs:rework/creative/storage_matrix');
  event.custom({type: 'modern_industrialization:assembler', eu: 2048, duration: 1200,
    item_inputs: [{item: 'techreborn:lapotronic_orbpack', amount: 1}, {item: 'ae2:dense_energy_cell', amount: 4},
      {item: 'techreborn:superconductor', amount: 8}, {item: 'kubejs:sky_plate', amount: 8},
      {item: 'kubejs:convergence_core', amount: 2}, {item: 'kubejs:infinity_stabilizer', amount: 1}],
    item_outputs: [{item: 'kubejs:infinite_energy_matrix', amount: 1}]}).id('kubejs:rework/creative/energy_matrix');
  event.custom({type: 'modern_industrialization:assembler', eu: 2048, duration: 1200,
    item_inputs: [{item: 'modern_industrialization:quantum_tank', amount: 1}, {item: 'techreborn:quantum_tank_unit', amount: 1},
      {item: 'ae2:fluid_storage_cell_256k', amount: 1}, {item: 'kubejs:arcane_lens', amount: 4},
      {item: 'kubejs:deorum_plate', amount: 8}, {item: 'kubejs:infinity_stabilizer', amount: 1}],
    item_outputs: [{item: 'kubejs:infinite_fluid_matrix', amount: 1}]}).id('kubejs:rework/creative/fluid_matrix');
  event.custom({type: 'ars_nouveau:enchanting_apparatus', reagent: {item: 'kubejs:infinity_stabilizer'},
    pedestalItems: [{item: 'kubejs:seal_life'}, {item: 'kubejs:seal_mind'}, {item: 'kubejs:seal_soul'}, {item: 'kubejs:seal_elements'},
      {item: 'kubejs:hallowed_circuit'}, {item: 'kubejs:resonance_core'}, {item: 'evilcraft:dark_power_gem_block'}, {item: 'ars_nouveau:source_gem_block'}],
    result: {id: 'kubejs:infinite_arcane_matrix', count: 1}, sourceCost: 50000, keepNbtOfReagent: false}).id('kubejs:rework/creative/arcane_matrix');

  // Step 3: the finale on the 9x9 table.
  AI_CR_ITEMS.forEach(c => {
    let key = {
      I: {item: 'avaritia:infinity_ingot'}, X: {item: 'avaritia:infinity_catalyst'}, N: {item: 'avaritia:neutron_ingot'},
      Z: {item: 'kubejs:infinity_stabilizer'}, Q: {item: 'kubejs:infinite_' + c[1] + '_matrix'}, A: {item: c[3]},
      '1': aiCrSing(c[4]), '2': aiCrSing(c[5]), U: {item: 'techreborn:uu_matter'}, C: {item: 'kubejs:armor_core_t8'}
    };
    let pattern = AI_CR_PATTERNS[c[2]], used = {};
    pattern.join('').split('').forEach(ch => { if (ch !== ' ') used[ch] = key[ch]; });
    event.custom({type: 'avaritia:shaped_table', tier: 4, pattern: pattern, key: used, result: {id: c[0], count: 1}})
      .id('kubejs:rework/creative/' + c[0].replace(':', '/'));
  });
  console.info('[Arcane Creative] ' + AI_CR_ITEMS.length + ' creative finales, 4 field matrices');
});
