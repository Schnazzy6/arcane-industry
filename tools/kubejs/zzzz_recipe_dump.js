// Temporary: dumps every loaded recipe (after all KubeJS changes) as serialised JSON for the
// quest generator. Copy into server_scripts, start the server, delete.
// Writes kubejs/config/recipe-dump.json: {"<recipe id>": {"type": ..., "json": {...}}}
const AI_RD_REG = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries');
const AI_RD_RECIPE = Java.loadClass('net.minecraft.world.item.crafting.Recipe');
const AI_RD_JSON = Java.loadClass('com.mojang.serialization.JsonOps');
const AI_RD_SKIP = /^(chipped|chisel|rechiseled|rechiseledae2|framedblocks|mcw[a-z]+|handcrafted|supplementaries|amendments|storagedrawers|sophisticated[a-z]+|culturaldelights|farmersrespite|mynethersdelight|oceansdelight|ends_delight|brewinandchewin|cookingforblockheads|betterend|betternether|twilightforest|eternal_starlight|cataclysm|samurai_dynasty|immersive_armors|simplyswords|simplymore|knavesneeds):/;
ServerEvents.loaded(event => {
  let reg = event.server.registryAccess(), ops = reg.createSerializationContext(AI_RD_JSON.INSTANCE);
  let out = {}, n = 0, failed = 0;
  event.server.getRecipeManager().getRecipes().forEach(h => {
    let id = String(h.id());
    if (AI_RD_SKIP.test(id) && !/kubejs/.test(id)) return;
    let r = h.value();
    try {
      let enc = AI_RD_RECIPE.CODEC.encodeStart(ops, r).getOrThrow();
      out[id] = {type: String(AI_RD_REG.RECIPE_TYPE.getKey(r.getType())), json: JSON.parse(String(enc.toString()))};
      n++;
    } catch (e) { failed++; }
  });
  JsonIO.write('kubejs/config/recipe-dump.json', out);
  console.info('[RecipeDump] dumped ' + n + ', failed ' + failed);
});
