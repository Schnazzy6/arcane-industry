// Isolated test server only. Export actual registered equipment, not guessed lang keys.
var aiGearExportDelay=80;
ServerEvents.tick(event=>{
 if(aiGearExportDelay<=0||--aiGearExportDelay>0)return;
 try{
  var Registries=Java.loadClass('net.minecraft.core.registries.BuiltInRegistries');
  var Armor=Java.loadClass('net.minecraft.world.item.ArmorItem');
  var Tiered=Java.loadClass('net.minecraft.world.item.TieredItem');
  var Projectile=Java.loadClass('net.minecraft.world.item.ProjectileWeaponItem');
  var data={armor:[],tools:[]};
  Registries.ITEM.forEach(item=>{
   var stack=item.getDefaultInstance();var id=String(Registries.ITEM.getKey(item));
   if(item instanceof Armor){item=Java.cast(Armor,item);data.armor.push({id:id,slot:String(item.getEquipmentSlot()).toLowerCase(),defense:item.getDefense(),toughness:item.getToughness(),durability:stack.getMaxDamage(),name_key:item.getDescriptionId()});}
   else if(item instanceof Tiered||item instanceof Projectile||stack.getMaxDamage()>0)data.tools.push({id:id,durability:stack.getMaxDamage(),name_key:item.getDescriptionId(),class_name:item instanceof Tiered?'TieredItem':item instanceof Projectile?'ProjectileWeaponItem':'UsableItem'});
  });
  JsonIO.write('kubejs/gear-registry.json',data);
  console.info('[GEAR REGISTRY] '+data.armor.length+' armor pieces, '+data.tools.length+' tools/usable equipment');
 }catch(e){console.error('[GEAR REGISTRY FAIL] '+e);}
});
