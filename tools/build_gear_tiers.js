// Builds the 12-tier equipment table (GEAR-TIERS.md) from in-game stats.
// Usage: node tools/build_gear_tiers.js
// Inputs:  build/server/kubejs/config/gear-stats.json (dumped by zzz_gear_dump.js),
//          build/gear-registry.json, overrides/.../loot-gear-policy.json (old T0-T8),
//          overrides/.../progression_craft_only.json
// Output:  overrides/common/kubejs/config/gear-tiers.json + a summary on stdout.
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..');
const kjs = path.join(root, 'overrides/common/kubejs');
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const stats = read('build/server/kubejs/config/gear-stats.json');
const registry = read('build/gear-registry.json');
const policy = read('overrides/common/kubejs/config/loot-gear-policy.json');
const craftOnly = new Set(read('overrides/common/kubejs/data/arcaneindustry/tags/item/progression_craft_only.json').values.map(v => typeof v === 'string' ? v : v.id));

const NAMES = ['', 'Примитив', 'Бронза', 'Железо', 'Сталь', 'Алмаз', 'Незерит', 'Ритуал', 'Нано', 'Объединение', 'Квант', 'Реликвия', 'Бесконечность'];
const COLORS = ['', '#9A9A9A', '#C58A4B', '#E8E8E8', '#8FD16A', '#5CD6E0', '#B07CFF', '#F2C14E', '#FF9A3C', '#FF5A5A', '#3BE8C5', '#FF6EC7', '#FFFFFF'];
const ROMAN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'];
// Progression baseline from the old craft-gated tiers.
const BASE = {0: 1, 1: 2, 2: 3, 3: 5, 4: 6, 5: 7, 6: 9, 7: 10, 8: 12};
const armorRow = {};
registry.armor.forEach(a => armorRow[a.id] = a);

// Attribute values arrive as floats (-2.4000000953...); round before banding.
function band(value, limits) { value = Math.round(value * 100) / 100; let t = 1; while (t <= limits.length && value >= limits[t - 1]) t++; return t; }
function weaponTier(s) {
  const power = (s.dmg + 1) * Math.sqrt(Math.max(0.25, 4 + s.spd) / 1.6);
  return band(power, [4.5, 5.5, 6.5, 7, 7.5, 8.5, 9.5, 10.5, 12, 14, 20]);
}
function toolTier(s) {
  const speed = band(s.mine, [3, 5, 6.5, 7.5, 8.5, 9.5, 11, 13, 16, 20, 40]);
  const dur = band(s.dur, [60, 200, 400, 900, 1700, 2200, 3000, 5000, 8000, 12000, 50000]);
  return Math.min(speed, dur + 1);
}
const SLOT_WEIGHT = {head: 0.15, chest: 0.4, legs: 0.3, feet: 0.15};
function armorTier(a) {
  if (!SLOT_WEIGHT[a.slot]) return 0;
  const score = (a.defense + 1.5 * a.toughness + 10 * (a.knockback_resistance || 0)) / SLOT_WEIGHT[a.slot];
  if (score <= 0) return 0;
  return band(score, [9, 13, 16, 20, 28, 34, 40, 48, 58, 70, 90]);
}

// knavesneeds:<mod>/<material>/<type> and simplymore:<material>_<type> -> tier of that
// material's existing gear (computed earlier in the loop, since old items come first).
function materialAnchor(id) {
  const [ns, name] = id.split(':');
  let candidates = [];
  if (ns === 'knavesneeds') {
    const [mod, mat] = name.split('/');
    candidates = ['sword', 'longsword', 'axe', 'pickaxe', 'chestplate', 'ingot'].map(t => mod + ':' + mat + '_' + t);
  } else if (ns === 'simplymore') {
    const mat = ['wooden', 'stone', 'iron', 'golden', 'gold', 'diamond', 'netherite', 'runic'].find(m => name.startsWith(m + '_'));
    if (mat === 'runic') candidates = ['simplyswords:runic_longsword', 'simplyswords:runic_katana'];
    else if (mat) candidates = ['minecraft:' + (mat === 'gold' ? 'golden' : mat) + '_sword'];
  }
  const hit = candidates.find(c => out.tiers[c]);
  return hit ? out.tiers[hit] : null;
}
const out = {names: NAMES, colors: COLORS, roman: ROMAN, tiers: {}, kind: {}, slot: {}, group: {}, loot: {}};
const why = {};
// Items from mods added later (not in the old policy) are tiered by their stats alone.
const EXTRA = Object.keys(stats).filter(id => policy.tiers[id] === undefined && !stats[id].error);
Object.keys(policy.tiers).concat(EXTRA).forEach(id => {
  const s = stats[id] || {};
  const old = policy.tiers[id];
  const base = old === undefined ? null : BASE[old];
  let kind, stat = 0;
  if (armorRow[id] || s.cls === 'armor') { kind = 'armor'; stat = armorRow[id] ? armorTier(armorRow[id]) : 0; out.slot[id] = (armorRow[id] || {}).slot; }
  else if (['pickaxe', 'shovel', 'hoe', 'tool'].includes(s.cls)) { kind = 'tool'; stat = toolTier(s); }
  else if (s.cls === 'axe') { kind = 'tool'; stat = Math.max(toolTier(s), weaponTier(s) - 1); }
  else if (['sword', 'trident'].includes(s.cls) || (s.dmg > 0.5 && ['tiered', 'other'].includes(s.cls))) { kind = 'weapon'; stat = weaponTier(s); }
  else if (['bow', 'crossbow'].includes(s.cls) || (policy.bows || {})[id]) kind = 'ranged';
  else if (s.cls === 'shield') kind = 'shield';
  else { why[id] = 'utility'; return; } // monocles, chalk, rods: no combat/work stats
  if (/batpack|jetpack|orbpack|bread/.test(id)) { why[id] = 'utility'; return; } // energy packs, food
  // Stats can move an item within its progression band, never far from it.
  let tier = base == null ? stat : stat ? Math.max(base - 1, Math.min(base + 2, stat)) : base;
  // Later weapon addons: the material's existing sword/tool tier anchors the item, stats
  // move it at most one tier (a knightmetal chakram is not "primitive" for its low damage).
  if (base == null) {
    const anchor = materialAnchor(id);
    if (anchor) tier = stat ? Math.max(anchor - 1, Math.min(anchor + 1, stat)) : anchor;
  }
  if (!tier) { why[id] = 'no stats'; return; }
  const name = id.split(':')[1], ns = id.split(':')[0];
  if (/(^|_)nano(_|$)/.test(name)) tier = Math.max(tier, 8);
  if (/quantum|gravi/.test(name) && ['techreborn', 'modern_industrialization', 'extended_industrialization', 'advanced_ae'].includes(ns)) tier = Math.max(tier, 10);
  if (ns === 'avaritia' && /infinity/.test(name)) tier = 12;
  if (/creative/.test(name)) tier = 12;
  tier = Math.max(1, Math.min(12, tier));
  out.tiers[id] = tier;
  out.kind[id] = kind;
  // Ladder group: an item of tier N is upgraded from any item of tier N-1 in its group.
  let group = null;
  if (kind === 'armor') group = ['head', 'chest', 'legs', 'feet'].includes(out.slot[id]) ? out.slot[id] : null;
  // Weapons split by handling, so an upgrade never trades a greathammer for a dagger.
  else if (kind === 'weapon') group = /greathammer|hammer|greataxe|claymore|halberd|scythe|glaive|lance|great_|grandsword|warhammer|mace|longaxe|cleaver/.test(name)
    ? 'weapon_heavy' : /dagger|sai|kunai|knife|rapier|cutlass|chakram|twinblade|sickle|claws|boline|athame|kama|shuko|fang/.test(name) ? 'weapon_light' : 'weapon';
  else if (kind === 'tool') group = ['pickaxe', 'shovel', 'hoe', 'axe'].find(c => s.cls === c || name.includes(c)) || 'pickaxe';
  else if (kind === 'ranged') group = /crossbow/.test(name) || s.cls === 'crossbow' ? 'crossbow' : 'bow';
  else if (kind === 'shield') group = 'shield';
  if (group) out.group[id] = group;
  // Energy packs count as chest armor but are machines, not finds.
  if (tier <= 7 && !craftOnly.has(id) && !/creative|infinity|batpack|jetpack|orbpack/.test(name)) (out.loot[tier] = out.loot[tier] || []).push(id);
});
// Gear whose class is not a vanilla sword/tool/armor, so the dump cannot classify it.
const MANUAL = {'modern_industrialization:quantum_sword': [10, 'weapon', 'weapon']};
Object.keys(MANUAL).forEach(id => {
  const [tier, kind, group] = MANUAL[id];
  out.tiers[id] = tier; out.kind[id] = kind; out.group[id] = group;
});
// Per-item ladder base: the items of the nearest lower tier in the same group that are not
// stronger than the item itself, so every upgrade is a real gain (a bronze sword with high
// damage cannot become a weaker knightmetal sword). Power: weapons damage x speed, tools
// mining speed, armor protection; items without readable stats (energy gear) accept all.
function power(id) {
  const s = stats[id] || {}, a = armorRow[id];
  if (a) return armorTier(a) ? (a.defense + 1.5 * a.toughness) / SLOT_WEIGHT[a.slot] : null;
  if (out.kind[id] === 'tool') return s.mine || null;
  if (out.kind[id] === 'weapon') return s.dmg > 0 ? (s.dmg + 1) * Math.sqrt(Math.max(0.25, 4 + s.spd) / 1.6) : null;
  return null;
}
out.base = {};
const byGroupTier = {};
Object.keys(out.group).forEach(id => {
  const k = out.group[id] + '|' + out.tiers[id];
  (byGroupTier[k] = byGroupTier[k] || []).push(id);
});
Object.keys(out.group).forEach(id => {
  const tier = out.tiers[id], group = out.group[id], p = power(id);
  for (let t = tier - 1; t >= 1; t--) {
    const pool = byGroupTier[group + '|' + t];
    if (!pool) continue;
    const weaker = p == null ? pool : pool.filter(b => { const q = power(b); return q == null || q <= p + 0.01; });
    // Prefer weaker items of the nearest tier; if every one of them is stronger (an item whose
    // value is not in its raw stats), the whole nearest tier is still the base: tiers stay adjacent.
    out.base[id] = (weaker.length ? weaker : pool).slice().sort();
    break;
  }
});
Object.values(out.loot).forEach(list => list.sort());
fs.writeFileSync(path.join(kjs, 'config/gear-tiers.json'), JSON.stringify(out));

// Summary
const count = {}; Object.values(out.tiers).forEach(t => count[t] = (count[t] || 0) + 1);
console.log('tiered', Object.keys(out.tiers).length, 'utility skipped', Object.keys(why).length, 'craft-only excluded from loot', craftOnly.size);
for (let t = 1; t <= 12; t++) {
  const ids = Object.keys(out.tiers).filter(i => out.tiers[i] === t);
  const kinds = {}; ids.forEach(i => kinds[out.kind[i]] = (kinds[out.kind[i]] || 0) + 1);
  console.log(ROMAN[t].padEnd(4), NAMES[t].padEnd(14), String(count[t] || 0).padStart(4), 'loot', String((out.loot[t] || []).length).padStart(4), JSON.stringify(kinds));
}
const show = ['minecraft:wooden_sword', 'minecraft:stone_sword', 'minecraft:iron_sword', 'minecraft:diamond_sword', 'minecraft:netherite_sword',
  'minecraft:iron_chestplate', 'minecraft:diamond_chestplate', 'minecraft:netherite_chestplate', 'minecraft:golden_pickaxe', 'minecraft:diamond_pickaxe',
  'twilightforest:ironwood_chestplate', 'twilightforest:knightmetal_sword', 'eternal_starlight:tentacle_spike', 'simplyswords:runic_cutlass',
  'simplyswords:soulstealer', 'techreborn:nano_chestplate', 'extended_industrialization:nano_boots', 'immersive_armors:divine_chestplate',
  'samurai_dynasty:master_samurai_chestplate', 'modern_industrialization:quantum_chestplate', 'cataclysm:cursium_chestplate', 'avaritia:infinity_sword'];
show.forEach(i => console.log('  ', i, out.tiers[i] ? ROMAN[out.tiers[i]] : '-', 'old T' + policy.tiers[i]));
console.log('utility sample:', Object.keys(why).slice(0, 25).join(', '));
