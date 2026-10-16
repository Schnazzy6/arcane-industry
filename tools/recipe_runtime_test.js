// Installed into the test server only. Runs after each reload.
let aiTestDelay = 80;
ServerEvents.tick(event => {
  if (aiTestDelay <= 0 || --aiTestDelay > 0) return;
  try {
    var AiTestRegistry = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries');
    var AiTestRL = Java.loadClass('net.minecraft.resources.ResourceLocation');
    var AiTestInput = Java.loadClass('net.minecraft.world.item.crafting.CraftingInput');
    var AiTestList = Java.loadClass('java.util.ArrayList');
    var AiTestSockets = Java.loadClass('dev.shadowsoffire.apotheosis.socket.SocketHelper');
    var AiTestAffix = Java.loadClass('dev.shadowsoffire.apotheosis.affix.AffixInstance');
    var AiTestAffixRegistry = Java.loadClass('dev.shadowsoffire.apotheosis.affix.AffixRegistry');
    var AiTestRarityRegistry = Java.loadClass('dev.shadowsoffire.apotheosis.loot.RarityRegistry');
    var AiTestAffixHelper = Java.loadClass('dev.shadowsoffire.apotheosis.affix.AffixHelper');
    let missing = [];
    var check = function(id) {
      if (!AiTestRegistry.ITEM.containsKey(AiTestRL.parse(id))) missing.push(id);
    }
    var inspect = function(x) {
      if (x == null) return;
      if (Array.isArray(x)) { x.forEach(inspect); return; }
      if (typeof x !== 'object') return;
      Object.keys(x).forEach(k => {
        if ((k === 'item' || k === 'id') && typeof x[k] === 'string') check(x[k]);
        else inspect(x[k]);
      });
    }
    AI_PLAN.recipes.forEach(r => inspect(r.json));
    AI_PLAN.armor.forEach(a => {
      check(a.out); check(a.core); check(a.material);check(a.plate);check(a.binding);
      (Array.isArray(a.base) ? a.base : [a.base]).forEach(b => { if (typeof b === 'string') check(b); });
    });
    if (missing.length) throw new Error('Unknown items: '+Array.from(new Set(missing)).join(', '));
    var AiTestTfConfig=Java.loadClass('twilightforest.config.TFConfig');
    if(!AiTestTfConfig.disableEntireTable || !AiTestTfConfig.disableUncraftingOnly) throw new Error('Twilight uncrafting remains enabled');
    if(!Ingredient.of('#c:hidden_from_recipe_viewers').test(Item.of('twilightforest:uncrafting_table'))) throw new Error('Uncrafting table is visible to recipe viewers');
    if(event.server.getRecipeManager().byKey(AiTestRL.parse('twilightforest:uncrafting_table')).isPresent()) throw new Error('Uncrafting table recipe remains');
    AI_PLAN.recipes.concat(AI_PLAN.patches).forEach(row => {
      if(!event.server.getRecipeManager().byKey(AiTestRL.parse(row.id)).isPresent()) throw new Error('Recipe missing '+row.id);
    });
    let bypasses = [];
    event.server.getRecipeManager().getRecipes().forEach(holder => {
      if (String(holder.id()).indexOf('spirit_repair/')>=0) return;
      if (String(holder.id()).endsWith('_smithing_trim')) return;
      let out = holder.value()['getResultItem(net.minecraft.core.HolderLookup$Provider)'](event.server.registryAccess());
      if (AI_PLAN.remove.indexOf(String(out.id)) >= 0 && !String(holder.id()).startsWith('kubejs:progression/')) bypasses.push(String(holder.id())+' -> '+out.id);
    });
    if (bypasses.length) throw new Error('Original recipe bypasses: '+bypasses.join(', '));
    let n = 0;
    AI_PLAN.armor.forEach(a => {
      let base = Array.isArray(a.base) ? a.base[0] : a.base;
      if (typeof base !== 'string') return;
      let previous = Item.of(base).withCustomName(Text.of('Armor progression test'));
      previous.enchant('minecraft:protection',3);
      AiTestSockets.setSockets(previous,2);
      AiTestAffixHelper.setRarity(previous,AiTestRarityRegistry.INSTANCE.getValue(AiTestRL.parse('apotheosis:rare')));
      AiTestAffixHelper.applyAffix(previous,new AiTestAffix(
        AiTestAffixRegistry.INSTANCE.holder(AiTestRL.parse('apotheosis:armor/attribute/ironforged')),
        0.5,AiTestRarityRegistry.INSTANCE.holder(AiTestRL.parse('apotheosis:rare')),previous));
      if (previous.isDamageableItem()) previous.setDamageValue(Math.floor(previous.getMaxDamage()/3));
      let stacks = new AiTestList();
      for (let i=0;i<9;i++) stacks.add(Item.of('minecraft:air'));
      stacks.set(1,Item.of(a.core));stacks.set(4,previous);stacks.set(7,Item.of(a.material));
      [0,2,6,8].forEach(i=>stacks.set(i,Item.of(a.plate)));
      [3,5].forEach(i=>stacks.set(i,Item.of(a.binding)));
      let input = AiTestInput.of(3,3,stacks);
      let recipe = event.server.getRecipeManager().byKey(AiTestRL.parse(a.id)).orElseThrow().value();
      if (!recipe.matches(input,event.server.overworld())) throw new Error('Does not match '+a.id);
      let result = recipe.assemble(input,event.server.registryAccess());
      if (result.id !== a.out) throw new Error('Wrong result '+a.id+': '+result.id);
      if (String(result.getHoverName().getString()) !== 'Armor progression test') throw new Error('Name lost '+a.id);
      if (!result.hasEnchantment('minecraft:protection',3)) throw new Error('Enchantment lost '+a.id);
      if (AiTestSockets.getSockets(result)!==2) throw new Error('Sockets lost '+a.id);
      if (AiTestAffixHelper.getAffixes(result).size()!==1) throw new Error('Affix lost '+a.id);
      if (!AiTestAffixHelper.getRarity(result).equals(AiTestAffixHelper.getRarity(previous))) throw new Error('Rarity lost '+a.id);
      if (previous.isDamageableItem() && result.isDamageableItem()) {
        let expected = Math.min(result.getMaxDamage()-1,Math.floor(previous.getDamageValue()/previous.getMaxDamage()*result.getMaxDamage()));
        if (result.getDamageValue() !== expected) throw new Error('Damage fraction lost '+a.id);
      }
      if(a.reinforce && result.customData.getString('arcane_armor_tier')!=='t5') throw new Error('T5 marker missing '+a.id);
      stacks.set(0,Item.of('minecraft:air'));
      if(recipe.matches(AiTestInput.of(3,3,stacks),event.server.overworld())) throw new Error('Incomplete upgrade accepted '+a.id);
      n++;
    });
    var AiTestTierInput=Java.loadClass('committee.nova.mods.avaritia.api.common.crafting.TierInput');
    let large=0;
    AI_PLAN.recipes.filter(row=>row.json.type==='avaritia:shaped_table').forEach(row=>{
      let recipe=event.server.getRecipeManager().byKey(AiTestRL.parse(row.id)).orElseThrow().value();
      let grid=new AiTestList();
      recipe.getIngredients().forEach(ingredient => grid.add(ingredient.isEmpty() ? Item.of('minecraft:air') : ingredient.stackArray[0].copy()));
      let input=AiTestTierInput.of(9,9,grid,4);
      if(!recipe.matches(input,event.server.overworld())) throw new Error('9x9 recipe does not match '+row.id);
      let result=recipe.assemble(input,event.server.registryAccess());
      if(result.id!==row.json.result.id || result.count!==row.json.result.count) throw new Error('Wrong 9x9 result '+row.id);
      large++;
    });
    ['helmet','chestplate','leggings','boots'].forEach(slot => {
      let a=AI_PLAN.armor.find(row => row.id==='kubejs:progression/armor/infinity_'+slot);
      let r=event.server.getRecipeManager().byKey(AiTestRL.parse(a.id)).orElseThrow().value();
      let stacks=new AiTestList();for(let i=0;i<9;i++) stacks.add(Item.of('minecraft:air'));
      stacks.set(1,Item.of(a.core));stacks.set(7,Item.of(a.material));
      [0,2,6,8].forEach(i=>stacks.set(i,Item.of(a.plate)));
      [3,5].forEach(i=>stacks.set(i,Item.of(a.binding)));
      let base=Item.of('samurai_dynasty:master_samurai_'+slot);stacks.set(4,base);
      if(r.matches(AiTestInput.of(3,3,stacks),event.server.overworld())) throw new Error('T4 Samurai bypasses T5: '+slot);
      base.customData={arcane_armor_tier:'t5'};
      if(!r.matches(AiTestInput.of(3,3,stacks),event.server.overworld())) throw new Error('T5 Samurai cannot upgrade: '+slot);
    });
    console.info('[AI TEST PASS] all items and recipes exist; '+n+' armor upgrades preserve name, enchants, rarity, affix, sockets and damage; '+large+' recipes assemble in 9x9; tier bypasses rejected.');
  } catch (e) { console.error('[AI TEST FAIL] '+e); }
});





