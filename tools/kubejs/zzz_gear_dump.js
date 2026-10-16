// One-off data dump for tools/build_gear_tiers.js. Copy into server_scripts, start the
// server once, then delete it. Writes kubejs/config/gear-stats.json with attack damage,
// speed, durability, mining speed and class for every tiered item plus all weapons,
// tools and armor of AI_DUMP_EXTRA_NS (mods added after the tier table was first built).
const AI_DUMP_REG = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries');
const AI_DUMP_DC = Java.loadClass('net.minecraft.core.component.DataComponents');
const AI_DUMP_ATTR = Java.loadClass('net.minecraft.world.entity.ai.attributes.Attributes');
const AI_DUMP_EXTRA_NS = {simplymore: 1, knavesneeds: 1};
// KubeJS hides getClass(); classify with instanceof instead (subclasses first).
const AI_DUMP_CLASSES = [
  ['sword', 'net.minecraft.world.item.SwordItem'], ['pickaxe', 'net.minecraft.world.item.PickaxeItem'],
  ['axe', 'net.minecraft.world.item.AxeItem'], ['shovel', 'net.minecraft.world.item.ShovelItem'],
  ['hoe', 'net.minecraft.world.item.HoeItem'], ['tool', 'net.minecraft.world.item.DiggerItem'],
  ['crossbow', 'net.minecraft.world.item.CrossbowItem'], ['bow', 'net.minecraft.world.item.BowItem'],
  ['trident', 'net.minecraft.world.item.TridentItem'], ['shield', 'net.minecraft.world.item.ShieldItem'],
  ['armor', 'net.minecraft.world.item.ArmorItem'], ['tiered', 'net.minecraft.world.item.TieredItem']
].map(c => [c[0], Java.loadClass(c[1])]);
function aiDumpClass(item) {
  for (var i = 0; i < AI_DUMP_CLASSES.length; i++) if (item instanceof AI_DUMP_CLASSES[i][1]) return AI_DUMP_CLASSES[i][0];
  return 'other';
}

ServerEvents.loaded(event => {
  const policy = JSON.parse(String(JsonIO.readString('kubejs/config/loot-gear-policy.json')));
  const out = {};
  AI_DUMP_REG.ITEM.keySet().forEach(key => {
    var id = String(key);
    var item = AI_DUMP_REG.ITEM.get(key);
    var cls = aiDumpClass(item);
    // Old policy items plus every armor piece, weapon and tool in the registry.
    if (policy.tiers[id] === undefined && cls === 'other') return;
    try {
      var stack = item.getDefaultInstance();
      var row = {cls: cls, dur: stack.getMaxDamage(), dmg: 0, spd: 0, armor: 0, tough: 0, mine: 0};
      var mods = stack.get(AI_DUMP_DC.ATTRIBUTE_MODIFIERS);
      if (mods != null) mods.modifiers().forEach(e => {
        var a = e.attribute(), v = e.modifier().amount();
        if (a.is(AI_DUMP_ATTR.ATTACK_DAMAGE)) row.dmg += v;
        else if (a.is(AI_DUMP_ATTR.ATTACK_SPEED)) row.spd += v;
        else if (a.is(AI_DUMP_ATTR.ARMOR)) row.armor += v;
        else if (a.is(AI_DUMP_ATTR.ARMOR_TOUGHNESS)) row.tough += v;
      });
      var tool = stack.get(AI_DUMP_DC.TOOL);
      if (tool != null) tool.rules().forEach(r => { if (r.speed().isPresent()) row.mine = Math.max(row.mine, r.speed().get()); });
      out[id] = row;
    } catch (err) {
      out[id] = {error: String(err)};
    }
  });
  JsonIO.write('kubejs/config/gear-stats.json', out);
  console.info('[Arcane Gear Dump] wrote ' + Object.keys(out).length + ' items');
});
