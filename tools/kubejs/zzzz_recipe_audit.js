// Temporary audit of every loaded recipe (CRAFTING-TODO.md point 5). Copy into
// server_scripts, start the server, delete. Writes kubejs/config/recipe-audit.json:
//  emptyIngredient - recipes with an ingredient that matches no item (dead end)
//  duplicates      - same result from the same serialised inputs (different ids)
//  loops           - A -> B and B -> A on crafting tables where a round trip gains items
const AI_RA_REG = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries');
const AI_RA_RECIPE = Java.loadClass('net.minecraft.world.item.crafting.Recipe');
const AI_RA_JSON = Java.loadClass('com.mojang.serialization.JsonOps');
ServerEvents.loaded(event => {
  let reg = event.server.registryAccess(), ops = reg.createSerializationContext(AI_RA_JSON.INSTANCE);
  let empty = [], bySig = {}, edges = {}, total = 0;
  event.server.getRecipeManager().getRecipes().forEach(h => {
    total++;
    let r = h.value(), id = String(h.id()), type = String(AI_RA_REG.RECIPE_TYPE.getKey(r.getType()));
    let res = null;
    try { res = r.getResultItem(reg); } catch (e) { }
    let out = res && !res.isEmpty() ? String(AI_RA_REG.ITEM.getKey(res.getItem())) : '';
    let ings = [];
    try { ings = r.getIngredients().toArray(); } catch (e) { }
    let names = [];
    ings.forEach(ing => {
      if (ing.isEmpty()) return;
      let stacks = [];
      try { stacks = ing.getItems(); } catch (e) { try { stacks = ing.stackArray; } catch (e2) { } }
      if (stacks.length === 0) { empty.push(id + ' (' + type + ')'); return; }
      names.push(String(AI_RA_REG.ITEM.getKey(stacks[0].getItem())));
    });
    if (!out) return;
    if (names.length) {
      let sig = type + '|' + out + '|' + names.slice().sort().join(',');
      (bySig[sig] = bySig[sig] || []).push(id);
    }
    if (type === 'minecraft:crafting' && names.length) {
      let counts = {};
      names.forEach(n => counts[n] = (counts[n] || 0) + 1);
      Object.keys(counts).forEach(n => { (edges[n] = edges[n] || []).push({out: out, need: counts[n], get: res.getCount(), id: id}); });
    }
  });
  let duplicates = Object.keys(bySig).filter(s => bySig[s].length > 1).map(s => bySig[s]);
  let loops = [];
  Object.keys(edges).forEach(a => edges[a].forEach(e1 => (edges[e1.out] || []).forEach(e2 => {
    if (e2.out !== a) return;
    // a*need1 -> out*get1 ; out*need2 -> a*get2. Gain if (get1/need1)*(get2/need2) > 1
    let ratio = (e1.get / e1.need) * (e2.get / e2.need);
    if (ratio > 1.001) loops.push(a + ' <-> ' + e1.out + ' x' + ratio.toFixed(2) + ' (' + e1.id + ' / ' + e2.id + ')');
  })));
  JsonIO.write('kubejs/config/recipe-audit.json', {total: total, emptyIngredient: empty, duplicates: duplicates, loops: loops});
  console.info('[RecipeAudit] recipes ' + total + ', empty-ingredient ' + empty.length + ', duplicate groups ' + duplicates.length + ', gain loops ' + loops.length);
});
