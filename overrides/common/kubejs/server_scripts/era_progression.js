const AI_ERA_ITEMS = {"modern_industrialization:steel_ingot": 1, "modern_industrialization:analog_circuit": 2, "modern_industrialization:processing_unit": 3, "modern_industrialization:quantum_circuit": 4, "kubejs:reborn_interface": 5, "kubejs:convergence_core": 6, "kubejs:infinity_stabilizer": 7, "avaritia:infinity_ingot": 8};
// Retain era tracking for loot gates. Clear any Ultimine attribute saved by
// older pack versions so the fixed config limit applies to existing players.
const AI_ULTIMINE_ATTRIBUTE = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries').ATTRIBUTE.wrapAsHolder(
  Java.loadClass('dev.ftb.mods.ftbultimine.registry.ModAttributes').MAX_BLOCKS_MODIFIER.get());
let aiEraTimer=0;
ServerEvents.tick(event => {
  if (++aiEraTimer % 100 !== 0) return;
  const server = event.server;
  let era = server.persistentData.getInt('arcane_era');
  server.players.forEach(player => {
    const inventory = player.getInventory();
    for (let i=0;i<inventory.getContainerSize();i++) {
      const item = inventory.getItem(i);
      era = Math.max(era, AI_ERA_ITEMS[String(item.id)] || 0);
    }
  });
  server.persistentData.putInt('arcane_era',era);
  server.players.forEach(player => {
    const attribute = player.getAttribute(AI_ULTIMINE_ATTRIBUTE);
    if (attribute != null && attribute.getBaseValue() !== 0) attribute.setBaseValue(0);
  });
});
