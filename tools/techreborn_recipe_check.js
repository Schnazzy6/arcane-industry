// Test server only: a small check of the changed critical path, not a full suite.
var trCheckDelay=40;
ServerEvents.tick(event=>{
 if(trCheckDelay<=0||--trCheckDelay>0)return;
 try {
  var RL=Java.loadClass('net.minecraft.resources.ResourceLocation');
  var Lists=Java.loadClass('java.util.ArrayList');
  var Input=Java.loadClass('net.minecraft.world.item.crafting.CraftingInput');
  var TierInput=Java.loadClass('committee.nova.mods.avaritia.api.common.crafting.TierInput');
  var Ingredient=Java.loadClass('net.minecraft.world.item.crafting.Ingredient');
  var Parser=Java.loadClass('com.google.gson.JsonParser');
  var JsonOps=Java.loadClass('com.mojang.serialization.JsonOps');
  var ops=event.server.registryAccess().createSerializationContext(JsonOps.INSTANCE);
  var passed=[];
  var selected=['reborn_interface','convergence_core','infinity_stabilizer','armor_core_t5','tr_machine_matter_fabricator'];
  AI_PLAN.recipes.filter(row=>selected.includes(row.id.split('/').pop())).forEach(row=>{
   var grid=new Lists();var gate=-1;
   row.json.pattern.forEach(line=>{for(var ch of line){
    if(ch===' '){grid.add(Item.of('minecraft:air'));continue;}
    var ing=Ingredient.CODEC.parse(ops,Parser.parseString(JSON.stringify(row.json.key[ch]))).result().orElseThrow();
    if(ing.stackArray.length===0)throw Error('Empty ingredient '+row.id+' '+ch);
    grid.add(ing.stackArray[0].copy());if(gate<0)gate=grid.size()-1;
   }});
   var recipe=event.server.getRecipeManager().byKey(RL.parse(row.id)).orElseThrow().value();
   var input=TierInput.of(9,9,grid,4);
   if(!recipe.matches(input,event.server.overworld()))throw Error('9x9 mismatch '+row.id);
   var result=recipe.assemble(input,event.server.registryAccess());
   if(result.id!==row.json.result.id)throw Error('Wrong output '+row.id);
   grid.set(gate,Item.of('minecraft:air'));
   if(recipe.matches(TierInput.of(9,9,grid,4),event.server.overworld()))throw Error('Missing ingredient accepted '+row.id);
   passed.push(row.id);
  });
  if(passed.length!==5)throw Error('Missing critical recipes: '+passed.length);
  JsonIO.write('kubejs/techreborn-check.json',{passed:passed,missing_ingredient_rejected:true});
  console.info('[TR MIGRATION CHECK PASS] '+passed.length+' critical 9x9 recipes assemble and reject missing ingredients');
 }catch(e){console.error('[TR MIGRATION CHECK FAIL] '+e);}
});
