// Test-only: snapshot the recipes actually loaded after unification and KubeJS.
let aiDumpOnce=false;
ServerEvents.tick(event=>{
 if(aiDumpOnce)return;aiDumpOnce=true;
 try {
  let Recipe=Java.loadClass('net.minecraft.world.item.crafting.Recipe');
  let JsonOps=Java.loadClass('com.mojang.serialization.JsonOps');
  let JsonObject=Java.loadClass('com.google.gson.JsonObject');
  let data=new JsonObject(),errors=new JsonObject();
  let ops=event.server.registryAccess().createSerializationContext(JsonOps.INSTANCE);
  event.server.getRecipeManager().getRecipes().forEach(h=>{
   try {let x=Recipe.CODEC.encodeStart(ops,h.value()).result().orElse(null);if(x!=null)data.add(h.id().toString(),x);else errors.addProperty(h.id().toString(),'codec failed');}
   catch(e){errors.addProperty(h.id().toString(),String(e));}
  });
  JsonIO.write('kubejs/exported_recipes.json',data);
  JsonIO.write('kubejs/exported_recipe_failures.json',errors);
  console.info('[RUNTIME EXPORT] '+data.size()+' recipes, '+errors.size()+' errors');
 }catch(e){console.error('[RUNTIME EXPORT FAIL] '+e);}
});
