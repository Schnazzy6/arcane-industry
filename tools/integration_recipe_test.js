// Test-only: assemble the changed ordinary crafting recipes and reject missing gates.
let aiIntegrationDelay=100;
ServerEvents.tick(event=>{
 if(aiIntegrationDelay<=0||--aiIntegrationDelay>0)return;
 try{
  let RL=Java.loadClass('net.minecraft.resources.ResourceLocation');
  let List=Java.loadClass('java.util.ArrayList');
  let Input=Java.loadClass('net.minecraft.world.item.crafting.CraftingInput');
  let SmithingInput=Java.loadClass('net.minecraft.world.item.crafting.SmithingRecipeInput');
  let NativeIngredient=Java.loadClass('net.minecraft.world.item.crafting.Ingredient');
  let JsonOps=Java.loadClass('com.mojang.serialization.JsonOps');
  let Parser=Java.loadClass('com.google.gson.JsonParser');
  let ops=event.server.registryAccess().createSerializationContext(JsonOps.INSTANCE);
  let byId={};AI_PLAN.patches.forEach(r=>byId[r.id]=r.json);
  let tested=0,smithing=0;
  AI_PLAN.integration.recipes.forEach(row=>{
   let j=byId[row.id];if(!j)return;
   let grid=new List();let gateSlot=-1;
   function stack(value){let ingredient=NativeIngredient.CODEC.parse(ops,Parser.parseString(JSON.stringify(value))).result().orElseThrow();let a=ingredient.stackArray;if(a.length===0)throw new Error('Empty ingredient '+row.id+' '+JSON.stringify(value));return a[0].copy();}
   if(j.type==='minecraft:smithing_transform'){
    let r=event.server.getRecipeManager().byKey(RL.parse(row.id)).orElseThrow().value();
    let base=stack(j.base).withCustomName(Text.of('Smithing integration test'));base.enchant('minecraft:sharpness',3);
    let input=new SmithingInput(stack(j.template),base,stack(j.addition));
    if(!r.matches(input,event.server.overworld()))throw new Error('Smithing does not match '+row.id);
    let result=r.assemble(input,event.server.registryAccess());
    if(result.id!==row.out||String(result.getHoverName().getString())!=='Smithing integration test'||!result.hasEnchantment('minecraft:sharpness',3))throw new Error('Smithing data lost '+row.id);
    if(r.matches(new SmithingInput(Item.of('minecraft:air'),base,stack(j.addition)),event.server.overworld()))throw new Error('Smithing gate bypass '+row.id);
    smithing++;return;
   }
   if(!(j.type==='minecraft:crafting_shaped'||j.type==='minecraft:crafting_shapeless'||j.type==='mekanism:mek_data'))return;
   if(j.pattern){
    j.pattern.forEach(line=>{for(let ch of line){let v=ch===' '?Item.of('minecraft:air'):stack(j.key[ch]);if(v.id===row.gate)gateSlot=grid.size();grid.add(v);}});
   }else{
    j.ingredients.forEach(value=>{let v=stack(value);if(v.id===row.gate)gateSlot=grid.size();grid.add(v);});
    while(grid.size()<9)grid.add(Item.of('minecraft:air'));
   }
   if(gateSlot<0)throw new Error('No milestone component '+row.id);
   let recipe=event.server.getRecipeManager().byKey(RL.parse(row.id)).orElseThrow().value();
   let input=Input.of(3,3,grid);
   if(!recipe.matches(input,event.server.overworld()))throw new Error('Cannot assemble '+row.id);
   let result=recipe.assemble(input,event.server.registryAccess());
   if(result.id!==row.out||result.count!==(j.result.count||1))throw new Error('Wrong integration result '+row.id+' '+result.id+' x'+result.count);
   grid.set(gateSlot,Item.of('minecraft:air'));
   if(recipe.matches(Input.of(3,3,grid),event.server.overworld()))throw new Error('Milestone bypass '+row.id);
   tested++;
  });
  console.info('[INTEGRATION TEST PASS] '+tested+' changed crafting recipes and '+smithing+' smithing upgrades assemble; outputs/counts and smithing name/enchants preserved; missing milestone rejected.');
 }catch(e){console.error('[INTEGRATION TEST FAIL] '+e);}
});
