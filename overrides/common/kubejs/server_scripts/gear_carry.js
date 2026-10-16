// Carries enchantments, affixes, name, trim and wear from the tier N-1 item to the crafted
// tier N item for tables whose recipes cannot use KubeJS result modifiers (the Avaritia
// 5x5-9x9 tables). Uses the crafting event, while the grid still holds the ingredients.
// Recipes that already ran the 'arcane_armor' modifier are marked and skipped.
const AI_CARRY = JSON.parse(String(JsonIO.readString('kubejs/config/gear-tiers.json')));
const AI_CARRY_REG = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries');
const AI_CARRY_DC = Java.loadClass('net.minecraft.core.component.DataComponents');
const AI_CARRY_DATA = Java.loadClass('net.minecraft.world.item.component.CustomData');
const AI_CARRY_TAG = Java.loadClass('net.minecraft.nbt.CompoundTag');
const AI_CARRY_KEEP = ['minecraft:enchantments', 'minecraft:custom_name', 'minecraft:lore', 'minecraft:trim',
  'minecraft:dyed_color', 'minecraft:repair_cost'];

ItemEvents.crafted(event => {
  let out = event.item;
  if (out == null || out.isEmpty()) return;
  let outId = String(out.id), group = AI_CARRY.group[outId];
  if (!group) return;
  let marked = out.get(AI_CARRY_DC.CUSTOM_DATA);
  if (marked != null && marked.copyTag().getBoolean('arcane_progression_crafted')) return;
  let inv = event.inventory, base = null;
  for (let i = 0; i < inv.getContainerSize(); i++) {
    let s = inv.getItem(i);
    if (!s.isEmpty() && AI_CARRY.group[String(s.id)] === group) { base = s; break; }
  }
  if (base == null) return;
  out.set(base.componentMap.filter(type => {
    let id = String(AI_CARRY_REG.DATA_COMPONENT_TYPE.getKey(type));
    return AI_CARRY_KEEP.indexOf(id) >= 0 || id.startsWith('apotheosis:');
  }));
  if (base.isDamageableItem() && out.isDamageableItem())
    out.setDamageValue(Math.min(out.getMaxDamage() - 1, Math.floor(base.getDamageValue() / base.getMaxDamage() * out.getMaxDamage())));
  let tag = new AI_CARRY_TAG();
  tag.putBoolean('arcane_progression_crafted', true);
  out.set(AI_CARRY_DC.CUSTOM_DATA, AI_CARRY_DATA.of(tag));
});
