// Tier ladder (GEAR-TIERS.md): every craftable armor piece, weapon and tool of tier N
// (II-XI) is crafted from ANY item of tier N-1 in the same group (helmet, chestplate,
// leggings, boots, weapon, pickaxe, axe, shovel, hoe, bow, crossbow, shield) plus the
// item's own material and the parts of that stage of progression. Tiers II-III use the
// ordinary 3x3 table, tier IV and above the Avaritia 9x9 table with a shape per group.
// The 'arcane_armor' result modifier carries enchantments, affixes and name over.
// Runs after progression.js and rework.js.
//
// Kept as they are: tier I (base items), tier XII (Infinity finale), items whose recipes
// use a magic station or the 9x9 table, and items without any recipe (loot/boss finds).
const AI_LADDER = JSON.parse(String(JsonIO.readString('kubejs/config/gear-tiers.json')));
const AI_LADDER_CRAFTING = /^(minecraft:crafting_shaped|minecraft:crafting_shapeless|kubejs:shaped|kubejs:shapeless|minecraft:smithing_transform)$/;
const AI_LADDER_FILLER = /stick|rods\/wooden|string|planks|logs|armor_core|_template/;
// Stage N: plates P, binding L and armor core C of that stage of progression (no core in II-III).
const AI_LADDER_STAGE = {
  2: ['modern_industrialization:bronze_plate', 'minecraft:leather', 'kubejs:armor_core_t1'],
  3: ['modern_industrialization:iron_plate', 'kubejs:ritual_mount', 'kubejs:armor_core_t1'],
  4: ['modern_industrialization:steel_plate', 'kubejs:electrical_focus', 'kubejs:armor_core_t2'],
  5: ['modern_industrialization:stainless_steel_plate', 'kubejs:industrial_focus', 'kubejs:armor_core_t3'],
  6: ['modern_industrialization:titanium_plate', 'kubejs:soul_stabilizer', 'kubejs:armor_core_t4'],
  7: ['kubejs:enchanted_titanium_plate', 'kubejs:ritual_frame', 'kubejs:armor_core_t5'],
  8: ['modern_industrialization:iridium_plate', 'kubejs:convergence_core', 'kubejs:armor_core_t6'],
  9: ['modern_industrialization:iridium_plate', 'kubejs:engineering_matrix', 'kubejs:armor_core_t7'],
  10: ['avaritia:crystal_matrix_ingot', 'kubejs:infinity_stabilizer', 'kubejs:armor_core_t7'],
  11: ['avaritia:neutron_ingot', 'kubejs:boss_seal', 'kubejs:armor_core_t8']
};
// Shapes per group and table (B = base of tier N-1, M = own material, P/L/C = stage parts).
// Every shape follows the item's silhouette; heavy and light weapons have their own.
// Square or taller than wide on the Avaritia tables: they mis-index recipes trimmed wider than tall.
// 3x3 crafting table: tier II and the final assembly of module stations (P = plate / module,
// exactly one P so a module recipe takes one module).
const AI_LADDER_SMALL = {
  head: ['MPM', 'MBM'], chest: ['M M', 'MBM', 'MPM'], legs: ['MPM', 'MBM', 'M M'], feet: ['M M', 'MBM', ' P '],
  weapon: ['M', 'B', 'P'], weapon_heavy: ['MMM', 'MBM', ' P '], weapon_light: [' M', 'B ', 'P '],
  pickaxe: ['MMM', ' B ', ' P '], axe: ['MM', 'MB', ' P'], shovel: ['M', 'B', 'P'], hoe: ['MM', ' B', ' P'],
  bow: [' MB', 'L M', ' P '], crossbow: ['MBM', 'L L', ' P '], shield: ['MPM', 'MBM', ' M ']
};
// 5x5 Nether table: tier III.
const AI_LADDER_SHAPES = {
  head: [' PPP ', 'PMMMP', 'PMBMP', 'L C L', 'M   M'],
  chest: ['MP PM', 'PMBMP', 'LPCPL', 'PMMMP', ' PPP '],
  legs: ['PPPPP', 'PMBMP', 'PLCLP', 'M   M', 'P   P'],
  feet: ['  B  ', 'P C P', 'M   M', 'ML LM', 'PP PP'],
  weapon: ['    M', '   MM', '  MB ', ' LC  ', 'P    '],
  weapon_heavy: ['MMMMM', 'MMBMM', ' LCL ', '  P  ', '  P  '],
  weapon_light: ['   M', '  MB', ' LC ', 'P   '],
  pickaxe: ['MMMMM', 'P B P', '  C  ', '  L  ', '  P  '],
  axe: ['MMP', 'MB ', 'MMC', ' L ', ' P '],
  shovel: [' M ', 'MBM', ' C ', ' L ', ' P '],
  hoe: ['MMP', ' B ', ' C ', ' L ', ' P '],
  bow: ['PMB', 'L C', 'M P'],
  crossbow: ['MBM', 'LCL', ' P '],
  shield: ['PMP', 'MBM', 'LCL']
};
// 7x7 End table: tiers IV-VI.
const AI_LADDER_SHAPES7 = {
  head: ['  PPP  ', ' PMMMP ', 'PM B MP', 'PL C LP', 'M     M', 'P     P', 'P     P'],
  chest: ['PP   PP', 'PM   MP', 'PL B LP', 'P MCM P', ' PM MP ', ' P L P ', '  PPP  '],
  legs: ['PPPPPPP', 'PM B MP', 'P LCL P', 'PM   MP', 'L     L', 'P     P', 'PP   PP'],
  feet: ['   B   ', '   C   ', '  L L  ', 'PM   MP', 'P     P', 'PM   MP', 'PPP PPP'],
  weapon: ['      M', '     MM', '    MM ', '   MB  ', ' L C   ', '  L    ', 'P      '],
  weapon_heavy: [' MMMMM ', 'MM B MM', ' MLCLM ', '   P   ', '   L   ', '   P   ', '   P   '],
  weapon_light: ['     M', '    MM', '   MB ', '  LC  ', ' L    ', 'P     '],
  pickaxe: [' MMMMM ', 'P  B  P', '   C   ', '   L   ', '   L   ', '   P   ', '   P   '],
  axe: ['MMP', 'MMB', ' MC', ' L ', ' L ', ' P ', ' P '],
  shovel: [' M ', 'MBM', 'MCM', ' L ', ' L ', ' P ', ' P '],
  hoe: ['MMP', ' MB', '  C', '  L', '  L', '  P', '  P']
};
// 9x9 Extreme table: tiers VII-XI.
const AI_LADDER_SHAPES9 = {
  head: ['  PPPPP  ', ' PMMMMMP ', 'PM  B  MP', 'PL  C  LP', 'L M   M L', 'P       P', 'PM     MP', 'P       P', 'PP     PP'],
  chest: ['PPP   PPP', 'PM P P MP', 'PL  B  LP', 'LM  C  ML', 'P  MLM  P', ' P  M  P ', ' PM L MP ', ' P     P ', '  PPPPP  '],
  legs: ['PPPPPPPPP', 'PM  B  MP', 'P  LCL  P', 'PM     MP', 'PL     LP', 'PM     MP', 'L       L', 'P       P', 'PP     PP'],
  feet: ['    B    ', '    C    ', '   L L   ', 'PM     MP', 'P       P', 'PM     MP', 'PL     LP', 'PMM   MMP', 'PPPP PPPP'],
  weapon: ['       MM', '      MMM', '     MM  ', '    MM   ', '   MB    ', '  LC     ', ' L L     ', 'P        ', 'P        '],
  weapon_heavy: [' MMMMMMM ', 'MMM B MMM', ' MM C MM ', '  MLPLM  ', '    L    ', '    P    ', '    L    ', '    P    ', '    P    '],
  weapon_light: ['        M', '       MM', '      MB ', '     LC  ', '    L    ', '   L     ', '  P      ', ' P       ', 'P        '],
  pickaxe: ['  MMMMM  ', ' MM   MM ', 'P   B   P', '    C    ', '   LLL   ', '    L    ', '    P    ', '    P    ', '    P    '],
  axe: [' MMM', 'MMMB', 'MM C', ' M L', '   L', '   L', '   P', '   P', '   P'],
  shovel: [' MMM ', 'MMBMM', 'MMCMM', ' MLM ', '  L  ', '  L  ', '  P  ', '  P  ', '  P  '],
  hoe: ['MMMP', '  MB', '   C', '   L', '   L', '   L', '   P', '   P', '   P']
};
// Ladder tier -> Avaritia table tier (2 = 5x5, 3 = 7x7, 4 = 9x9); tier II uses the 3x3 table.
function aiLadderTable(tier) { return tier <= 2 ? 0 : tier === 3 ? 2 : tier <= 6 ? 3 : 4; }const AI_LADDER_MEMBERS = {};   // group -> tier -> [ids]
Object.keys(AI_LADDER.group).forEach(id => {
  let g = AI_LADDER.group[id], t = AI_LADDER.tiers[id];
  AI_LADDER_MEMBERS[g] = AI_LADDER_MEMBERS[g] || {};
  (AI_LADDER_MEMBERS[g][t] = AI_LADDER_MEMBERS[g][t] || []).push(id);
});
function aiLadderTag(group, tier) { return 'arcaneindustry:ladder/' + group + '_' + tier; }
// Nearest lower tier that actually has items, so gaps (no XI chestplate) do not break the chain.
function aiLadderBase(group, tier) {
  for (let t = tier - 1; t >= 1; t--) if (AI_LADDER_MEMBERS[group][t]) return aiLadderTag(group, t);
  return null;
}
function aiLadderMaterial(recipes, id) {
  for (var i = 0; i < recipes.length; i++) {
    var json = recipes[i].json;
    if (/smithing_transform/.test(String(json.type)) && json.addition) {
      var add = Array.isArray(json.addition) ? json.addition[0] : json.addition;
      if ((add.item || add.tag) && !AI_LADDER_FILLER.test(add.item || add.tag) && !AI_LADDER.tiers[add.item]) return add;
    }
  }
  for (var i = 0; i < recipes.length; i++) {
    var json = recipes[i].json, counts = {};
    var take = (ing, n) => {
      if (ing == null) return;
      if (Array.isArray(ing)) ing = ing[0];
      var key = ing.item ? 'i:' + ing.item : ing.tag ? 't:' + ing.tag : null;
      if (key == null || AI_LADDER_FILLER.test(key) || (ing.item && AI_LADDER.tiers[ing.item])) return;
      counts[key] = (counts[key] || 0) + n;
    };
    if (json.key && json.pattern) {
      if (json.key.M) take(json.key.M, 100); // progression armor: M is the specialisation material
      var letters = {};
      json.pattern.forEach(row => row.split('').forEach(ch => { if (ch !== ' ') letters[ch] = (letters[ch] || 0) + 1; }));
      Object.keys(letters).forEach(ch => take(json.key[ch], letters[ch]));
    } else if (json.ingredients) json.ingredients.forEach(ing => take(ing, 1));
    var best = null, n = 0;
    Object.keys(counts).forEach(k => { if (counts[k] > n) { best = k; n = counts[k]; } });
    if (best != null) return best.charAt(0) === 'i' ? {item: best.substring(2)} : {tag: best.substring(2)};
  }
  return null;
}

// Material from the item's own name when no recipe says it: techreborn:ruby_sword -> ruby gem.
// Registry lookup: Item.of() on an unknown id throws and would abort the whole script.
const AI_LADDER_ITEMS = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries').ITEM;
const AI_LADDER_RL = Java.loadClass('net.minecraft.resources.ResourceLocation');
// Materials whose item is not named after them.
const AI_LADDER_HINT = {runic: 'simplyswords:runic_tablet', crystalite: 'betterend:eternal_crystal'};
const AI_LADDER_SUFFIX = /_(sword|longsword|pickaxe|axe|shovel|spade|hoe|helmet|chestplate|leggings|boots|bow|crossbow|shield|knife|scythe|hammer|katana|spear|dagger|sai|glaive|warglaive|halberd|claymore|greataxe|greathammer|cutlass|rapier|twinblade|chakram)$/;
function aiLadderGuess(id) {
  var ns = id.split(':')[0], mat = id.split(':')[1].replace(AI_LADDER_SUFFIX, '');
  if (mat === id.split(':')[1]) return null;
  if (AI_LADDER_HINT[mat]) return {item: AI_LADDER_HINT[mat]};
  var tries = [ns + ':' + mat + '_ingot', ns + ':' + mat + '_gem', ns + ':' + mat, 'minecraft:' + mat + '_ingot',
    'minecraft:' + mat, ns + ':' + mat + '_plate', 'modern_industrialization:' + mat + '_ingot', 'techreborn:' + mat + '_ingot'];
  for (var i = 0; i < tries.length; i++) {
    if (!AI_LADDER.tiers[tries[i]] && AI_LADDER_ITEMS.containsKey(AI_LADDER_RL.parse(tries[i]))) return {item: tries[i]};
  }
  return null;
}
// Per-item base tag (tools/build_gear_tiers.js 'base'): items of the nearest lower tier in
// the same group that are not stronger than the result, so each upgrade is a real gain.
function aiLadderItemTag(id) { return 'arcaneindustry:ladder_base/' + id.replace(':', '/'); }
function aiLadderBaseFor(id, group, tier) { return AI_LADDER.base && AI_LADDER.base[id] ? aiLadderItemTag(id) : aiLadderBase(group, tier); }
ServerEvents.tags('item', event => {
  Object.keys(AI_LADDER_MEMBERS).forEach(g => Object.keys(AI_LADDER_MEMBERS[g]).forEach(t =>
    event.add(aiLadderTag(g, t), AI_LADDER_MEMBERS[g][t])));
  Object.keys(AI_LADDER.base || {}).forEach(id => event.add(aiLadderItemTag(id), AI_LADDER.base[id]));
});

// Plan recipes (progression armor upgrades, generated crafts) cannot be removed with
// event.remove once progression.js has added them, so the ladder decision for them is
// made here at load time and they are dropped from AI_PLAN before its handler runs.
// Native mod recipes are still removed in the event below.
// Native recipes KubeJS cannot parse (so forEachRecipe misses them) are listed by the audit
// (tools/kubejs/zzzz_ladder_audit.js) and disabled by data overrides in kubejs/data;
// their outputs still get a ladder step here.
const AI_LADDER_UNPARSED = {};
try {
  (JSON.parse(String(JsonIO.readString('kubejs/config/ladder-leftovers.json'))).entries || []).forEach(e => AI_LADDER_UNPARSED[e.out] = true);
} catch (err) { }
const AI_LADDER_STATS = {};
const AI_LADDER_PLAN = {};      // id -> material for outputs taken over from the plan
const AI_LADDER_PLAN_SPECIAL = {};
(function () {
  // Every plan recipe (crafting, 9x9 or station) of a tier II-XI item is replaced by its ladder
  // step, so no item keeps a recipe whose base is several tiers lower (nanosaber from a
  // netherite sword). Items whose recipe progression removed outright also get a step.
  var removed = {};
  AI_PLAN.remove.forEach(x => removed[x] = true);
  var planArmor = {}, planCrafting = {}, planSpecial = {};
  AI_PLAN.armor.forEach(a => (planArmor[a.out] = planArmor[a.out] || []).push(a));
  AI_PLAN.recipes.concat(AI_PLAN.patches).forEach(r => {
    var res = r.json.result || r.json.output || {};
    var out = String(res.id || res.item || '');
    if (!out) return;
    var bucket = AI_LADDER_CRAFTING.test(String(r.json.type)) ? planCrafting : planSpecial;
    (bucket[out] = bucket[out] || []).push({id: r.id, json: r.json});
  });
  Object.keys(planSpecial).forEach(out => AI_LADDER_PLAN_SPECIAL[out] = true);
  Object.keys(AI_LADDER.group).forEach(id => {
    var tier = AI_LADDER.tiers[id], group = AI_LADDER.group[id];
    if (tier < 2 || tier > 11 || aiLadderBase(group, tier) == null) return;
    var material = null;
    if (planArmor[id]) material = {item: planArmor[id][0].material};
    else if (planCrafting[id]) material = aiLadderMaterial(planCrafting[id], id) || aiLadderGuess(id);
    else if (planSpecial[id]) material = aiLadderMaterial(planSpecial[id], id) || aiLadderGuess(id);
    else if (removed[id]) material = aiLadderGuess(id);
    if (material != null) AI_LADDER_PLAN[id] = material;
  });
  var outOf = r => r.out ? r.out : String((r.json.result || r.json.output || {}).id || (r.json.result || r.json.output || {}).item || '');
  var drop = list => { for (var i = list.length - 1; i >= 0; i--) if (AI_LADDER_PLAN[outOf(list[i])]) list.splice(i, 1); };
  drop(AI_PLAN.armor); drop(AI_PLAN.recipes); drop(AI_PLAN.patches);
})();

// ---- Stations -------------------------------------------------------------------------
// Each item is upgraded at one station. Magic mods use their own altar, tech uses the MI
// assembler, everything else the 3x3-9x9 tables; about a third of magic items move to the
// MI assembler and a third of non-electric tech items (and a fifth of the rest) to a magic
// altar, so the two sides cross over. A station is only used from the tier where it is
// reachable in progression; otherwise the item falls back to the tables.
// Direct stations keep the base item's data themselves (Ars keepNbtOfReagent, Malum
// carryOverComponentData, Eidolon keep_nbt_of_reagent). Module stations (MI, Goety,
// Occultism, Nature's Aura) make a tier module, combined with the base on a crafting table.
const AI_LADDER_HOME = {
  ars_nouveau: 'ars', ars_elemental: 'ars', ars_elemancy: 'ars', ars_additions: 'ars', irons_spellbooks: 'ars',
  malum: 'malum', eidolon_repraised: 'eidolon', hexerei: 'eidolon',
  goety: 'goety', evilcraft: 'goety', forbidden_arcanus: 'goety',
  occultism: 'occultism', naturesaura: 'aura',
  techreborn: 'mi', modern_industrialization: 'mi', extended_industrialization: 'mi', ae2: 'mi',
  advanced_ae: 'mi', advanced_reborn: 'mi', industrialization_overdrive: 'mi'
};
const AI_LADDER_MIN = {table: 2, ars: 2, eidolon: 4, occultism: 4, aura: 4, mi: 4, malum: 5, goety: 7};
const AI_LADDER_MAGIC = ['ars', 'eidolon', 'occultism', 'aura', 'malum', 'goety'];
const AI_LADDER_ELECTRIC = /drill|chainsaw|jackhammer|omni_tool|nano|quantum|gravi|rock_cutter|electric|steam_mining/;
const AI_LADDER_MODULE = {mi: 'tech_module', goety: 'dark_essence', occultism: 'spirit_contract', aura: 'aura_seed'};
const AI_LADDER_SPIRITS = {
  weapon: ['malum:wicked', 'malum:infernal'], head: ['malum:earthen', 'malum:sacred'], chest: ['malum:earthen', 'malum:sacred'],
  legs: ['malum:earthen', 'malum:sacred'], feet: ['malum:aerial', 'malum:earthen'], pickaxe: ['malum:earthen', 'malum:arcane'],
  axe: ['malum:earthen', 'malum:infernal'], shovel: ['malum:earthen', 'malum:arcane'], hoe: ['malum:sacred', 'malum:earthen'],
  bow: ['malum:aerial', 'malum:arcane'], crossbow: ['malum:aerial', 'malum:arcane'], shield: ['malum:earthen', 'malum:arcane']
};
function aiLadderHash(s) { var h = 7; for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % 1000003; return h; }
function aiLadderStation(id, tier) {
  var ns = id.split(':')[0], home = AI_LADDER_HOME[ns] || 'table', h = aiLadderHash(id), pick;
  var ok = st => tier >= AI_LADDER_MIN[st];
  var magicFor = () => { var list = AI_LADDER_MAGIC.filter(ok); return list.length ? list[(h >> 3) % list.length] : 'table'; };
  if (home === 'mi') pick = AI_LADDER_ELECTRIC.test(id) ? 'mi' : (h % 3 === 0 ? magicFor() : 'mi');
  else if (home !== 'table') pick = h % 3 === 0 ? 'mi' : home;
  else pick = h % 5 === 0 ? magicFor() : 'table';
  return ok(pick) ? pick : (home !== 'table' && home !== pick && ok(home) ? home : 'table');
}
function aiLadderOccultSpirit(tier) { return tier <= 5 ? 'foliot' : tier <= 8 ? 'djinni' : tier <= 10 ? 'afrit' : 'marid'; }
function aiLadderCount(ing, n) { var out = {count: n}; Object.keys(ing).forEach(k => out[k] = ing[k]); return out; }

ServerEvents.recipes(event => {
  let made = 0, lootOnly = 0, noMaterial = 0, perStation = {};
  // Unparsed native recipes of items that get a ladder step (see AI_LADDER_UNPARSED).
  try {
    (JSON.parse(String(JsonIO.readString('kubejs/config/ladder-leftovers.json'))).entries || []).forEach(e => {
      if (e.id.indexOf('kubejs:') !== 0 && AI_LADDER.group[e.out] && aiLadderGuess(e.out)) event.remove({id: e.id});
    });
  } catch (err) { }
  let note = (g, kind, id) => { let s = AI_LADDER_STATS[g] = AI_LADDER_STATS[g] || {}; s[kind] = (s[kind] || 0) + 1; if (kind !== 'ladder') { let k = kind + '_eg'; s[k] = s[k] || []; if (s[k].length < 6) s[k].push(id); } };

  let usedModules = {};   // station|tier -> true, filled by the item loop below

  Object.keys(AI_LADDER.group).forEach(id => {
    let tier = AI_LADDER.tiers[id], group = AI_LADDER.group[id];
    if (tier < 2 || tier > 11) return;
    // weapon_heavy / weapon_light share the weapon shapes and spirits.
    let shapeKey = group.indexOf('weapon') === 0 ? 'weapon' : group;
    let natives = [];
    event.forEachRecipe({output: id}, r => natives.push({id: String(r.getId()), json: JSON.parse(String(r.json))}));
    let material = AI_LADDER_PLAN[id];
    if (material == null) {
      // Any native recipe (crafting, smithing or a station) is replaced by the ladder
      // step; items with no recipe at all stay finds.
      // Tech Reborn's bronze and gem gear has its recipes disabled by the mod; it is plain
      // craftable gear, so it still gets a step (material from its name: ruby_sword -> ruby_gem).
      let forced = id.indexOf('techreborn:') === 0 && !AI_LADDER_ELECTRIC.test(id);
      if (natives.length === 0 && !AI_LADDER_UNPARSED[id] && !forced) { lootOnly++; note(group, 'loot', id); return; }
      let crafting = natives.filter(r => AI_LADDER_CRAFTING.test(String(r.json.type)));
      material = aiLadderMaterial(crafting.length ? crafting : natives, id) || aiLadderGuess(id);
    }
    let base = aiLadderBaseFor(id, group, tier);
    if (base == null || material == null) { noMaterial++; note(group, 'nomat', id); return; }
    natives.forEach(r => event.remove({id: r.id}));
    let stage = AI_LADDER_STAGE[tier], B = {tag: base}, M = material, P = {item: stage[0]}, L = {item: stage[1]}, C = {item: stage[2]};
    let rid = 'kubejs:rework/ladder/' + id.replace(':', '/'), res = {id: id, count: 1};
    let station = aiLadderStation(id, tier);
    perStation[station] = (perStation[station] || 0) + 1;
    if (station === 'ars') {
      let arsP = tier >= 7 ? {item: 'kubejs:enchanted_titanium_plate'} : P;
      event.custom({type: 'ars_nouveau:enchanting_apparatus', reagent: B, pedestalItems: [M, M, M, P, arsP, L, C],
        result: res, sourceCost: 500 * tier, keepNbtOfReagent: true}).id(rid);
    } else if (station === 'malum') {
      let sp = AI_LADDER_SPIRITS[shapeKey];
      event.custom({type: 'malum:spirit_infusion', carryOverComponentData: true, input: {tag: base, count: 1},
        extraInputs: [aiLadderCount(M, 3), aiLadderCount(P, 2), aiLadderCount(L, 1), aiLadderCount(C, 1)],
        spirits: [{type: sp[0], count: 2 * tier}, {type: sp[1], count: tier}], result: res}).id(rid);
    } else if (station === 'eidolon') {
      let eidP = tier >= 5 ? {item: 'kubejs:deorum_plate'} : P;
      event.custom({type: 'eidolon_repraised:ritual_brazier_crafting', reagent: B, pedestal_items: [M, M, M, P, eidP, L],
        focus_items: [C], health_requirement: 0.0, keep_nbt_of_reagent: true, result: res}).id(rid);
    } else if (AI_LADDER_MODULE[station]) {
      usedModules[station + '|' + tier] = true;
      // Module station: the module plus base and material meet on a crafting table.
      let small = AI_LADDER_SMALL[group] || AI_LADDER_SMALL[shapeKey], mkey = {};
      let mparts = {B: B, M: M, P: {item: 'kubejs:' + AI_LADDER_MODULE[station] + '_t' + tier}, L: L, C: C};
      small.join('').split('').forEach(ch => { if (ch !== ' ') mkey[ch] = mparts[ch]; });
      event.custom({type: 'kubejs:shaped', pattern: small, key: mkey, result: res}).id(rid).modifyResult('arcane_armor');
    } else {
      let table = aiLadderTable(tier), big = table > 0;
      let shapes = table === 4 ? AI_LADDER_SHAPES9 : table === 3 ? AI_LADDER_SHAPES7 : table === 2 ? AI_LADDER_SHAPES : AI_LADDER_SMALL;
      // Bows, crossbows and shields keep their compact shape on every table.
      let pattern = shapes[group] || shapes[shapeKey] || (big ? AI_LADDER_SHAPES : AI_LADDER_SMALL)[group] || (big ? AI_LADDER_SHAPES : AI_LADDER_SMALL)[shapeKey];
      let parts = {B: B, M: M, P: P, L: L, C: C}, key = {};
      pattern.join('').split('').forEach(ch => { if (ch !== ' ') key[ch] = parts[ch]; });
      let json = big
        ? {type: 'avaritia:shaped_table', tier: table, pattern: pattern, key: key, result: res}
        : {type: 'kubejs:shaped', pattern: pattern, key: key, result: res};
      event.custom(json).id(rid).modifyResult('arcane_armor');
    }
    made++; note(group, 'ladder', id);
  });
  // Module recipes, only for the station tiers some item actually uses. Each module also
  // takes the pack's cross-over parts: magic circuitry in the MI module, deorum and
  // resonance in Goety's essence, iesnium in Occultism's contract, sky plates in the seed.
  let moduleList = [];
  Object.keys(usedModules).forEach(key => {
    let st = key.split('|')[0], tier = parseInt(key.split('|')[1]);
    let s = AI_LADDER_STAGE[tier], name = AI_LADDER_MODULE[st] + '_t' + tier, out = 'kubejs:' + name;
    let rid = 'kubejs:rework/ladder/module/' + st + '_' + tier;
    let P = {item: s[0]}, L = {item: s[1]}, C = {item: s[2]}, json;
    moduleList.push(name);
    if (st === 'mi') {
      let inputs = [{item: s[0], amount: 4}, {item: s[1], amount: 1}, {item: s[2], amount: 1}];
      if (tier >= 6) inputs.push({item: 'kubejs:hallowed_circuit', amount: 1});
      if (tier >= 8) inputs.push({item: 'kubejs:arcane_lens', amount: 1});
      json = {type: 'modern_industrialization:assembler', eu: Math.min(2048, 8 << Math.max(0, tier - 3)), duration: 400,
        item_inputs: inputs, item_outputs: [{item: out, amount: 1}]};
    } else if (st === 'goety') {
      let ings = [P, P, {item: 'kubejs:deorum_plate'}, {item: 'kubejs:deorum_plate'}, C];
      if (tier >= 8) ings.push({item: 'kubejs:resonance_core'});
      json = {type: 'goety:ritual', ritual_type: 'goety:craft', activation_item: L, craftType: 'magic',
        soulCost: 5 * tier, duration: 40, ingredients: ings, result: {id: out, count: 1}};
    } else if (st === 'occultism') {
      let sp = aiLadderOccultSpirit(tier);
      json = {type: 'occultism:ritual', ritual_type: 'occultism:craft', pentacle_id: 'occultism:craft_' + sp,
        activation_item: {item: 'occultism:book_of_binding_bound_' + sp}, duration: 30 + 10 * tier,
        ingredients: [P, P, {item: 'kubejs:iesnium_plate'}, {item: 'kubejs:iesnium_plate'}, L, C],
        result: {id: out, count: 1}, ritual_dummy: {id: out, count: 1}};
    } else json = {type: 'naturesaura:tree_ritual', sapling: {item: 'naturesaura:ancient_sapling'}, time: 150 + 30 * tier,
      ingredients: [P, P, {item: 'kubejs:sky_plate'}, {item: 'kubejs:sky_plate'}, L, C], output: {id: out, count: 1}};
    event.custom(json).id(rid);
  });
  // Read by startup_scripts/gear_modules.js on the next start (copy it into overrides).
  JsonIO.write('kubejs/config/ladder-modules.json', {modules: moduleList.sort()});
  console.info('[Arcane Ladder] ' + made + ' ladder upgrades; ' + lootOnly + ' loot-only, ' + noMaterial +
    ' without a material; stations ' + JSON.stringify(perStation));
  Object.keys(AI_LADDER_STATS).forEach(g => console.info('[Arcane Ladder] ' + g + ': ' + JSON.stringify(AI_LADDER_STATS[g])));
});