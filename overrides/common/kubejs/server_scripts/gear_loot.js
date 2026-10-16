// Exploration loot (GEAR-TIERS.md): chests roll equipment by the player's Apotheosis
// world tier and the pack's technology era, with Apotheosis affixes.
const AI_GEAR = JSON.parse(String(JsonIO.readString('kubejs/config/gear-tiers.json')));
const AI_GEAR_WORLD = Java.loadClass('dev.shadowsoffire.apotheosis.tiers.WorldTier');
const AI_GEAR_GEN = Java.loadClass('dev.shadowsoffire.apotheosis.tiers.GenContext');
const AI_GEAR_RARITY = Java.loadClass('dev.shadowsoffire.apotheosis.loot.LootRarity');
const AI_GEAR_CTRL = Java.loadClass('dev.shadowsoffire.apotheosis.loot.LootController');
const AI_GEAR_CATEGORY = Java.loadClass('dev.shadowsoffire.apotheosis.loot.LootCategory');
const AI_GEAR_PARAMS = Java.loadClass('net.minecraft.world.level.storage.loot.parameters.LootContextParams');
const AI_GEAR_PLAYER = Java.loadClass('net.minecraft.world.entity.player.Player');
const AI_GEAR_MAX = 7;                      // VIII (Nano) and above are craft-only
const AI_GEAR_ERA_CAP = [3, 4, 5, 6, 7];     // arcane_era 0..4+ -> ceiling III..VII
const AI_GEAR_DANGER = /cataclysm|born_in_chaos|ancient_city|stronghold|bastion|end_city|nether_bridge|fortress|twilightforest|eternal_starlight|dungeon|mansion|trial_chambers|monument/;
const AI_GEAR_KINDS = [['armor', 45], ['weapon', 30], ['tool', 15], ['ranged', 8], ['shield', 2]];
const AI_GEAR_DEBUG = {count: 0}; // logs the first few rolls after each start
const AI_GEAR_POOL = {};
Object.keys(AI_GEAR.loot).forEach(t => {
  AI_GEAR_POOL[t] = {};
  AI_GEAR.loot[t].forEach(id => {
    let kind = AI_GEAR.kind[id];
    (AI_GEAR_POOL[t][kind] = AI_GEAR_POOL[t][kind] || []).push(id);
  });
});

function aiGearCap(context) {
  let level = context.getLevel();
  let era = level.getServer().persistentData.getInt('arcane_era');
  let cap = AI_GEAR_ERA_CAP[Math.min(era, AI_GEAR_ERA_CAP.length - 1)];
  let entity = context.getParamOrNull(AI_GEAR_PARAMS.THIS_ENTITY);
  let player = entity instanceof AI_GEAR_PLAYER ? entity : null;
  if (player != null) cap = Math.min(cap, 3 + AI_GEAR_WORLD.getTier(player).ordinal());
  else cap = Math.min(cap, 3);
  let table = String(context.getQueriedLootTableId());
  let dimension = String(level.dimension);
  let danger = dimension !== 'minecraft:overworld' || AI_GEAR_DANGER.test(table);
  return {cap: Math.min(AI_GEAR_MAX, cap + (danger ? 1 : 0)), danger: danger};
}

function aiGearPick(random, cap) {
  // Ceiling is rare; one or two tiers below are common.
  let weights = [1, 3, 3, 1];
  let total = 0;
  let options = [];
  for (let d = 0; d < weights.length; d++) {
    let tier = cap - d;
    if (tier < 1 || !AI_GEAR_POOL[tier]) continue;
    options.push([tier, weights[d]]);
    total += weights[d];
  }
  if (total === 0) return null;
  let roll = random.nextInt(total), tier = options[0][0];
  for (let i = 0; i < options.length; i++) { if (roll < options[i][1]) { tier = options[i][0]; break; } roll -= options[i][1]; }
  let pool = AI_GEAR_POOL[tier];
  let kinds = AI_GEAR_KINDS.filter(k => pool[k[0]]);
  let kindTotal = 0;
  kinds.forEach(k => kindTotal += k[1]);
  let kindRoll = random.nextInt(kindTotal), kind = kinds[0][0];
  for (let i = 0; i < kinds.length; i++) { if (kindRoll < kinds[i][1]) { kind = kinds[i][0]; break; } kindRoll -= kinds[i][1]; }
  let ids = pool[kind];
  return ids[random.nextInt(ids.length)];
}

function aiGearAffix(stack, context) {
  try {
    let gen = AI_GEAR_GEN.forLoot(context);
    if (gen == null) {
      // forLoot needs a player in the context; LootR and chest openings provide one.
      let entity = context.getParamOrNull(AI_GEAR_PARAMS.THIS_ENTITY);
      if (!(entity instanceof AI_GEAR_PLAYER)) return stack;
      gen = AI_GEAR_GEN.forPlayer(context.getRandom(), entity);
    }
    let rarity = AI_GEAR_RARITY.random(gen);
    let category = AI_GEAR_CATEGORY.forItem(stack);
    if (rarity == null || category == null || category.isNone()) return stack;
    let result = AI_GEAR_CTRL.createLootItem(stack, category, rarity, gen);
    return result == null || result.isEmpty() ? stack : result;
  } catch (err) {
    console.warn('[Arcane Gear] affix failed for ' + stack.id + ': ' + err);
    return stack;
  }
}

LootJS.modifiers(event => {
  event.addTableModifier(LootType.CHEST).customAction((context, loot) => {
    let limits = aiGearCap(context);
    // Native chest loot above the current ceiling is removed, not downgraded.
    loot.modifyItems(stack => {
      let tier = AI_GEAR.tiers[String(stack.id)];
      return tier !== undefined && tier > limits.cap ? Item.empty : stack;
    });
    let random = context.getRandom();
    if (random.nextFloat() >= (limits.danger ? 0.4 : 0.25)) return;
    let id = aiGearPick(random, limits.cap);
    if (id == null) return;
    let stack = aiGearAffix(Item.of(id), context);
    loot.addItem(stack);
    if (AI_GEAR_DEBUG.count++ < 5) console.info('[Arcane Gear] ' + context.getQueriedLootTableId() + ' cap ' + limits.cap + ' -> ' + id +
      ' tier ' + AI_GEAR.tiers[id] + (stack.getComponents().keySet().toString().indexOf('apotheosis') >= 0 ? ' +affixes' : ''));
  });
});
