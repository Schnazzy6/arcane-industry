// Disables native gear recipes that KubeJS cannot parse (so rework_ladder.js cannot remove
// them) by overriding them with a recipe whose NeoForge condition is false.
// Input: overrides/common/kubejs/config/ladder-leftovers.json (written by the audit
// tools/kubejs/zzzz_ladder_audit.js) and a list of registered item ids.
// Usage: node tools/build_ladder_disables.js <known-items.txt>
// A recipe is disabled only when the ladder can replace it: the output is tiered gear
// (II-XI) and a material can be guessed from its name, mirroring aiLadderGuess().
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..');
const kjs = path.join(root, 'overrides/common/kubejs');
const table = JSON.parse(fs.readFileSync(path.join(kjs, 'config/gear-tiers.json'), 'utf8'));
const leftovers = JSON.parse(fs.readFileSync(path.join(kjs, 'config/ladder-leftovers.json'), 'utf8')).entries || [];
const known = new Set(fs.readFileSync(process.argv[2], 'utf8').split(/\r?\n/).filter(Boolean));
const HINT = {runic: 'simplyswords:runic_tablet', crystalite: 'betterend:eternal_crystal'}; // keep in sync with rework_ladder.js
const SUFFIX = /_(sword|longsword|pickaxe|axe|shovel|spade|hoe|helmet|chestplate|leggings|boots|bow|crossbow|shield|knife|scythe|hammer|katana|spear|dagger|sai|glaive|warglaive|halberd|claymore|greataxe|greathammer|cutlass|rapier|twinblade|chakram)$/;
function guess(id) {
  const [ns, name] = id.split(':'), mat = name.replace(SUFFIX, '');
  if (mat === name) return null;
  if (HINT[mat]) return HINT[mat];
  return [ns + ':' + mat + '_ingot', ns + ':' + mat + '_gem', ns + ':' + mat, 'minecraft:' + mat + '_ingot', 'minecraft:' + mat,
    ns + ':' + mat + '_plate', 'modern_industrialization:' + mat + '_ingot', 'techreborn:' + mat + '_ingot']
    .find(c => !table.tiers[c] && known.has(c)) || null;
}
let written = 0, kept = [];
for (const e of leftovers) {
  const tier = table.tiers[e.out];
  const ok = !e.id.startsWith('kubejs:') && table.group[e.out] && tier >= 2 && tier <= 11 && guess(e.out);
  if (!ok) { kept.push(e.id); continue; }
  const [ns, p] = e.id.split(':');
  const file = path.join(kjs, 'data', ns, 'recipe', p + '.json');
  fs.mkdirSync(path.dirname(file), {recursive: true});
  // A condition-only file is rejected as 'not a json object' and the original comes back,
  // so the override carries a complete (inert) recipe body next to the false condition.
  fs.writeFileSync(file, JSON.stringify({'neoforge:conditions': [{type: 'neoforge:false'}], type: 'minecraft:crafting_shapeless',
    ingredients: [{item: 'minecraft:barrier'}], result: {id: 'minecraft:barrier', count: 1}}, null, 2) + '\n');
  written++;
}
console.log('disabled', written, 'kept', kept.length + ':', kept.join(', '));
