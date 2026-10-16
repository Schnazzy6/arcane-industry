// Colours each tiered item's name by its equipment tier (GEAR-TIERS.md).
// A player's own rename (custom_name) still wins over this default.
const AI_TIER_TABLE = JSON.parse(String(JsonIO.readString('kubejs/config/gear-tiers.json')));
const AI_TIER_COMPONENTS = Java.loadClass('net.minecraft.core.component.DataComponents');
const AI_TIER_TEXT = Java.loadClass('net.minecraft.network.chat.Component');

// A failure here must never abort startup: startup script errors stop the game loading.
ItemEvents.modification(event => {
  let failed = 0;
  Object.keys(AI_TIER_TABLE.tiers).forEach(id => {
    let color = parseInt(AI_TIER_TABLE.colors[AI_TIER_TABLE.tiers[id]].substring(1), 16);
    event.modify(id, mod => {
      try {
        let item = mod.item();
        let name = AI_TIER_TEXT.translatable(item.getDescriptionId()).withColor(color);
        try { mod.setItemName(name); } catch (e1) { mod.itemName = name; }
      } catch (err) {
        if (failed++ === 0) console.warn('[Arcane Tiers] name colour failed: ' + err);
      }
    });
  });
});
