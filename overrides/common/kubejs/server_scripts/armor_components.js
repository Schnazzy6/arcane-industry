// Preserve player investment without replacing the new armor's base attributes.
const AI_REGISTRIES = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries');
const AI_RESOURCE = Java.loadClass('net.minecraft.resources.ResourceLocation');
const AI_COMPONENT_PATCH = Java.loadClass('net.minecraft.core.component.DataComponentPatch');
const AI_COMPONENTS = Java.loadClass('net.minecraft.core.component.DataComponents');
const AI_ARMOR_CUSTOM_DATA = Java.loadClass('net.minecraft.world.item.component.CustomData');
const AI_ARMOR_TAG = Java.loadClass('net.minecraft.nbt.CompoundTag');
const AI_ATTRIBUTES = Java.loadClass('net.minecraft.world.entity.ai.attributes.Attributes');
const AI_MODIFIER = Java.loadClass('net.minecraft.world.entity.ai.attributes.AttributeModifier');
const AI_OPERATION = Java.loadClass('net.minecraft.world.entity.ai.attributes.AttributeModifier$Operation');
const AI_SLOT_GROUP = Java.loadClass('net.minecraft.world.entity.EquipmentSlotGroup');
function aiUpgradeArmor(event, reinforced) {
  let old = Item.of('minecraft:air');
  for (let i=0;i<event.grid.size();i++) {
    let candidate = event.grid.getItem(i);
    if (!candidate.isEmpty() && candidate.getMaxStackSize()===1) { old=candidate; break; }
  }
  let result = event.item;
  const keep = ['minecraft:enchantments', 'minecraft:stored_enchantments',
    'minecraft:custom_name', 'minecraft:lore', 'minecraft:trim',
    'minecraft:dyed_color', 'minecraft:repair_cost'];
  AI_REGISTRIES.DATA_COMPONENT_TYPE.keySet().forEach(key => {
    let id = String(key);
    if (id === 'ars_nouveau:armor_perks') {
      let perks = old.get(AI_REGISTRIES.DATA_COMPONENT_TYPE.get(key));
      if (perks != null) {
        if (!(result.id.startsWith('ars_nouveau:') || result.id.startsWith('ars_elemancy:')) && !perks.getPerks().isEmpty()) event.success(Item.of('minecraft:air'));
      }
    }
  });
  result.set(old.componentMap.filter(type => {
    let id = String(AI_REGISTRIES.DATA_COMPONENT_TYPE.getKey(type));
    return keep.indexOf(id)>=0 || id.startsWith('apotheosis:') ||
      (id==='ars_nouveau:armor_perks' && (result.id.startsWith('ars_nouveau:') || result.id.startsWith('ars_elemancy:')));
  }));
  if (old.isDamageableItem() && result.isDamageableItem()) {
    result.setDamageValue(Math.min(result.getMaxDamage()-1,
      Math.floor(old.getDamageValue() / old.getMaxDamage() * result.getMaxDamage())));
  }
  if (reinforced) {
    result.customData = {arcane_armor_tier:"t5"};
    let group = result.id.endsWith('_helmet') ? AI_SLOT_GROUP.HEAD :
      result.id.endsWith('_chestplate') ? AI_SLOT_GROUP.CHEST :
      result.id.endsWith('_leggings') ? AI_SLOT_GROUP.LEGS : AI_SLOT_GROUP.FEET;
    let attributes = result.get(AI_COMPONENTS.ATTRIBUTE_MODIFIERS);
    if (attributes != null) {
      let enhanced = attributes.withModifierAdded(AI_ATTRIBUTES.ARMOR_TOUGHNESS,
        new AI_MODIFIER(AI_RESOURCE.parse('kubejs:reinforced_samurai'), 2, AI_OPERATION.ADD_VALUE), group);
      result.patch(AI_COMPONENT_PATCH.builder().set(AI_COMPONENTS.ATTRIBUTE_MODIFIERS, enhanced).build());
    }
  }
  const provenance = result.get(AI_COMPONENTS.CUSTOM_DATA);
  const provenanceTag = provenance == null ? new AI_ARMOR_TAG() : provenance.copyTag();
  provenanceTag.putBoolean('arcane_progression_crafted', true);
  result.set(AI_COMPONENTS.CUSTOM_DATA, AI_ARMOR_CUSTOM_DATA.of(provenanceTag));
  event.item = result;
  return event.success(result);
}
ServerEvents.modifyRecipeResult('arcane_armor', event => aiUpgradeArmor(event, false));
ServerEvents.modifyRecipeResult('arcane_armor_t5', event => aiUpgradeArmor(event, true));


