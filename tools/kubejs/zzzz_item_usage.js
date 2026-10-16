// Temporary audit: for every kubejs:* item, how many loaded recipes produce it and how many
// use it as an ingredient (recipes serialised to JSON, the output itself excluded).
// Copy into server_scripts, start the server, delete. Writes kubejs/config/item-usage.json.
const AI_IU_REG = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries');
const AI_IU_RECIPE = Java.loadClass('net.minecraft.world.item.crafting.Recipe');
const AI_IU_JSON = Java.loadClass('com.mojang.serialization.JsonOps');
ServerEvents.loaded(event => {
  let ops = event.server.registryAccess().createSerializationContext(AI_IU_JSON.INSTANCE);
  let items = [];
  AI_IU_REG.ITEM.keySet().forEach(k => { if (String(k.getNamespace()) === 'kubejs') items.push(String(k)); });
  let made = {}, used = {}, examples = {}, failed = 0;
  event.server.getRecipeManager().getRecipes().forEach(h => {
    let text;
    try { text = String(AI_IU_RECIPE.CODEC.encodeStart(ops, h.value()).getOrThrow()); } catch (e) { failed++; return; }
    let out = '';
    try { out = String(AI_IU_REG.ITEM.getKey(h.value().getResultItem(event.server.registryAccess()).getItem())); } catch (e) { }
    items.forEach(id => {
      if (text.indexOf('"' + id + '"') < 0) return;
      if (id === out) { made[id] = (made[id] || 0) + 1; return; }
      used[id] = (used[id] || 0) + 1;
      (examples[id] = examples[id] || []).length < 3 && examples[id].push(String(h.id()));
    });
  });
  let rows = items.map(id => ({id: id, made: made[id] || 0, used: used[id] || 0, eg: examples[id] || []}));
  JsonIO.write('kubejs/config/item-usage.json', {failed: failed, rows: rows});
  console.info('[ItemUsage] items ' + items.length + ', unused ' + rows.filter(r => r.used === 0).length + ', unserialisable recipes ' + failed);
});
