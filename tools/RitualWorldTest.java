package arcane.test;

import java.util.*;
import java.util.function.*;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.LecternBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.phys.AABB;
import com.hollingsworth.arsnouveau.common.block.tile.*;
import com.sammy.malum.common.block.curiosities.spirit_altar.SpiritAltarBlockEntity;
import com.sammy.malum.common.block.storage.stand.ItemStandBlockEntity;
import alexthw.eidolon_repraised.common.tile.CrucibleTileEntity;
import com.klikli_dev.occultism.common.blockentity.*;
import com.Polarice3.Goety.common.blocks.entities.DarkAltarBlockEntity;
import com.Polarice3.Goety.common.blocks.entities.CursedCageBlockEntity;
import com.Polarice3.Goety.common.blocks.entities.PedestalBlockEntity;

@Mod("arcane_ritual_test")
public class RitualWorldTest {
    static ServerLevel world;
    static int age;
    static boolean reported;
    static final List<Case> tests=new ArrayList<>();
    static final String MI="modern_industrialization:";
    static final int[][] RING={{-3,-3},{0,-3},{3,-3},{-3,0},{3,0},{-3,3},{0,3},{3,3}};
    public RitualWorldTest(){NeoForge.EVENT_BUS.addListener(this::tick);}
    static ResourceLocation id(String s){return ResourceLocation.parse(s);}
    static ItemStack item(String s,int n){ItemStack v=new ItemStack(BuiltInRegistries.ITEM.get(id(s)),n);if(v.isEmpty())throw new IllegalStateException("Unknown item "+s);return v;}
    static ItemStack item(String s){return item(s,1);}
    static void put(BlockPos p,String s){world.setBlockAndUpdate(p,BuiltInRegistries.BLOCK.get(id(s)).defaultBlockState());}
    static <T> T tile(BlockPos p,Class<T> t){return t.cast(world.getBlockEntity(p));}
    static void check(boolean ok,String msg){if(!ok)throw new IllegalStateException(msg);}
    static void log(String s){System.out.println("[RITUAL WORLD] "+s);}
    static class Case {
        String name,out;int expected,start;BlockPos p;boolean done,passed;Runnable step;Supplier<String> detail=()->"";BooleanSupplier consumed=()->true;
        Case(String n,String o,int amount,int x){name=n;out=o;expected=amount;p=new BlockPos(x,200,1000);start=age;tests.add(this);
            for(int cx=(x-10)>>4;cx<=(x+10)>>4;cx++)for(int cz=990>>4;cz<=1010>>4;cz++)world.setChunkForced(cx,cz,true);
            for(int dx=-9;dx<=9;dx++)for(int dz=-9;dz<=9;dz++){
                put(p.offset(dx,-1,dz),"minecraft:stone");
                for(int y=0;y<=8;y++)put(p.offset(dx,y,dz),"minecraft:air");
            }
            world.getEntitiesOfClass(ItemEntity.class,new AABB(p).inflate(12)).forEach(ItemEntity::discard);
            log("SETUP "+name+" at "+p);
        }
        int count(){return world.getEntitiesOfClass(ItemEntity.class,new AABB(p).inflate(10)).stream().filter(e->e.getItem().is(BuiltInRegistries.ITEM.get(id(out)))).mapToInt(e->e.getItem().getCount()).sum();}
        int outputCount(){return count();}
        void run(){if(done)return;try{if(step!=null)step.run();int n=outputCount();if(n>=expected){check(n==expected,"wrong count "+n);check(consumed.getAsBoolean(),"ingredients not consumed");done=true;passed=true;log("PASS "+name+" => "+expected+" "+out+"; "+detail.get());}else if(age-start>3200){done=true;log("FAIL "+name+" timeout; "+detail.get());}}catch(Throwable e){done=true;log("FAIL "+name+" "+e);e.printStackTrace();}}
    }
    void tick(ServerTickEvent.Post e){
        age++;if(age==100){world=e.getServer().overworld();world.setDayTime(6000);try{exportRecipes();setupArs();setupMalum();setupNature();setupEidolon();setupOccult();setupGoety();setupEvilBootstrap();}catch(Throwable t){log("SETUP FAIL "+t);t.printStackTrace();}}
        if(age>100){tests.forEach(Case::run);if(age%200==0)for(Case c:tests)if(!c.done)log("WAIT "+c.name+" "+c.detail.get());
            if(!reported&&!tests.isEmpty()&&tests.stream().allMatch(c->c.done)){reported=true;log("COMPLETE passed="+tests.stream().filter(c->c.passed).count()+"/"+tests.size());}}
    }
    static void exportRecipes() throws Exception {
        var arr=new com.google.gson.JsonObject();var failed=new com.google.gson.JsonObject();
        var ops=world.registryAccess().createSerializationContext(com.mojang.serialization.JsonOps.INSTANCE);
        for(var h:world.getRecipeManager().getRecipes())try{arr.add(h.id().toString(),net.minecraft.world.item.crafting.Recipe.CODEC.encodeStart(ops,h.value()).result().orElseThrow());}catch(Throwable t){failed.addProperty(h.id().toString(),t.toString());}
        var gson=new com.google.gson.Gson();java.nio.file.Files.writeString(java.nio.file.Path.of("../ritual-test/runtime-recipes.json"),gson.toJson(arr));
        var tags=new com.google.gson.JsonObject();BuiltInRegistries.ITEM.getTags().forEach(pair->{var values=new com.google.gson.JsonArray();pair.getSecond().forEach(v->values.add(BuiltInRegistries.ITEM.getKey(v.value()).toString()));tags.add(pair.getFirst().location().toString(),values);});
        java.nio.file.Files.writeString(java.nio.file.Path.of("../ritual-test/runtime-tags.json"),gson.toJson(tags));
        java.nio.file.Files.writeString(java.nio.file.Path.of("../ritual-test/runtime-export-failures.json"),gson.toJson(failed));
        log("EXPORTED recipes="+arr.size()+" unencoded="+failed.size()+" tags="+tags.size());
    }
    static void setupArs(){
        String[][] ped={
            {"ars_nouveau:source_gem",MI+"bronze_plate","minecraft:redstone","minecraft:lapis_lazuli"},
            {"theurgy:mercury_shard","theurgy:mercury_shard","naturesaura:infused_iron","naturesaura:infused_iron",MI+"steel_plate",MI+"steel_plate","ars_nouveau:magebloom_fiber","ars_nouveau:magebloom_fiber"},
            {"ars_nouveau:fire_essence","ars_nouveau:water_essence","ars_nouveau:earth_essence","ars_nouveau:air_essence","hexerei:moon_dust","naturesaura:infused_iron","theurgy:mercury_shard","irons_spellbooks:arcane_essence"}};
        String[] outs={"arcane_resin","alchemical_catalyst","elemental_insulator"};String[] reagents={"minecraft:slime_ball","occultism:spirit_attuned_gem","kubejs:industrial_focus"};int[] costs={500,2500,4000};
        for(int k=0;k<3;k++){
            final int i=k;Case c=new Case("Ars/"+outs[i],"kubejs:"+outs[i],4,i*40){int outputCount(){return super.outputCount()+tile(p,EnchantingApparatusTile.class).getStack().getCount()*(tile(p,EnchantingApparatusTile.class).getStack().is(BuiltInRegistries.ITEM.get(id(out)))?1:0);}};
            put(c.p.below(),"ars_nouveau:arcane_core");put(c.p,"ars_nouveau:enchanting_apparatus");
            var a=tile(c.p,EnchantingApparatusTile.class);List<ArcanePedestalTile> ps=new ArrayList<>();
            for(int n=0;n<ped[i].length;n++){BlockPos pp=c.p.offset(RING[n][0],0,RING[n][1]);put(pp,"ars_nouveau:arcane_pedestal");var t=tile(pp,ArcanePedestalTile.class);t.setStack(item(ped[i][n]));ps.add(t);}
            BlockPos jp=c.p.offset(0,0,5);put(jp,"ars_nouveau:source_jar");var jar=tile(jp,SourceJarTile.class);
            a.setStack(item(reagents[i]));check(!a.attemptCraft(a.getStack(),null),"Ars crafts without Source");jar.addSource(10000);
            var last=ps.getLast();ItemStack saved=last.getStack();last.setStack(ItemStack.EMPTY);check(!a.attemptCraft(a.getStack(),null),"Ars crafts without pedestal ingredient");last.setStack(saved);
            check(a.attemptCraft(a.getStack(),null),"Ars refused "+outs[i]);log("NEGATIVE PASS Ars/"+outs[i]+" missing Source and ingredient rejected");
            c.consumed=()->ps.stream().allMatch(t->t.getStack().isEmpty())&&jar.getSource()==10000-costs[i];
            c.detail=()->"source="+jar.getSource()+" crafting="+a.isCrafting;
        }
    }
    static void setupMalum(){
        Case c=new Case("Malum/soul_stabilizer","kubejs:soul_stabilizer",4,120);put(c.p,"malum:spirit_altar");var a=tile(c.p,SpiritAltarBlockEntity.class);
        a.inventory.setStackInSlot(0,item("eidolon_repraised:soul_shard"));a.spiritInventory.setStackInSlot(0,item("malum:arcane_spirit",4));a.spiritInventory.setStackInSlot(1,item("malum:aerial_spirit",2));
        String[] ids={MI+"stainless_steel_plate","ars_nouveau:source_gem","occultism:spirit_attuned_gem","irons_spellbooks:arcane_essence"};int[] counts={2,2,1,2};List<ItemStandBlockEntity> ps=new ArrayList<>();
        for(int i=0;i<4;i++){BlockPos pp=c.p.offset(RING[i][0],0,RING[i][1]);put(pp,"malum:runewood_item_stand");var t=tile(pp,ItemStandBlockEntity.class);t.inventory.setStackInSlot(0,item(ids[i],counts[i]));ps.add(t);}
        c.consumed=()->a.inventory.getStackInSlot(0).isEmpty()&&a.spiritInventory.getStackInSlot(0).isEmpty()&&a.spiritInventory.getStackInSlot(1).isEmpty()&&ps.stream().allMatch(t->t.inventory.getStackInSlot(0).isEmpty());
        c.detail=()->"progress="+a.progress+" recipe="+a.recipe+" extras="+a.extrasInventory;
    }
    static void setupNature(){
        Case c=new Case("Nature/industrial_focus","kubejs:industrial_focus",4,160);
        String[] pattern={"    W    "," W     W ","   GGG   ","  GG GG  ","W G 0 G W","  GG GG  ","   GGG   "," W     W ","    W    "};
        String[] ingredients={MI+"digital_circuit",MI+"digital_circuit","kubejs:electrical_focus","kubejs:electrical_focus",MI+"stainless_steel_plate",MI+"stainless_steel_plate","kubejs:alchemical_catalyst","naturesaura:gold_leaf"};
        List<de.ellpeck.naturesaura.blocks.tiles.BlockEntityWoodStand> stands=new ArrayList<>();int idx=0;
        for(int z=0;z<9;z++)for(int x=0;x<9;x++){char ch=pattern[z].charAt(x);BlockPos pp=c.p.offset(x-4,0,z-4);if(ch=='G')put(pp,"naturesaura:gold_powder");if(ch=='W'){put(pp,"naturesaura:wood_stand");var t=tile(pp,de.ellpeck.naturesaura.blocks.tiles.BlockEntityWoodStand.class);t.items.setStackInSlot(0,item(ingredients[idx++]));stands.add(t);}}
        put(c.p.below(),"minecraft:dirt");put(c.p,"naturesaura:ancient_sapling");
        BlockPos gap=c.p.offset(0,0,-2);put(gap,"minecraft:air");check(!de.ellpeck.naturesaura.blocks.multi.Multiblocks.TREE_RITUAL.isComplete(world,c.p),"Nature accepts broken ring");put(gap,"naturesaura:gold_powder");check(de.ellpeck.naturesaura.blocks.multi.Multiblocks.TREE_RITUAL.isComplete(world,c.p),"Nature ring invalid");log("NEGATIVE PASS Nature missing gold powder rejected");
        c.step=()->{if(age-c.start==10){var b=(de.ellpeck.naturesaura.blocks.BlockAncientSapling)world.getBlockState(c.p).getBlock();b.performBonemeal(world,world.random,c.p,world.getBlockState(c.p));b.performBonemeal(world,world.random,c.p,world.getBlockState(c.p));}};
        c.consumed=()->stands.stream().allMatch(t->t.items.getStackInSlot(0).isEmpty());c.detail=()->"center="+world.getBlockState(c.p);
    }
    static void setupEidolon(){
        Case c=new Case("Eidolon/ritual_frame","kubejs:ritual_frame",4,200);put(c.p.below(),"minecraft:campfire");put(c.p,"eidolon_repraised:crucible");var a=tile(c.p,CrucibleTileEntity.class);a.fill();
        int[] fed={-1};
        c.step=()->{int phase=a.getSteps().size();if(phase!=fed[0]&&a.hasWater){fed[0]=phase;if(phase==0)a.setItem(0,item(MI+"titanium_plate",4));if(phase==1){a.setItem(0,item(MI+"processing_unit",2));a.setItem(1,item("kubejs:industrial_focus"));}if(phase==2){a.setItem(0,item("kubejs:soul_stabilizer",2));a.setItem(1,item("kubejs:enchantment_lattice"));}}
            if(phase>0&&phase<=2&&a.getStirTicks()==0&&a.getStirs()<(phase==1?2:3))a.stir(c.p);};
        c.consumed=()->!a.hasWater&&a.isEmpty();c.detail=()->"water="+a.hasWater+" steps="+a.getSteps().size()+" stirs="+a.getStirs();
    }
    static void setupOccult(){
        Case c=new Case("Occultism/relic_research","kubejs:relic_research",8,240);
        String[] p={"_________","__WXXXW__","_WW1_1WW_","_X1W_W1X_","_X__0__X_","_X1W_W1X_","_WW1_1WW_","__WXXXW__","_________"};
        for(int z=0;z<9;z++)for(int x=0;x<9;x++){char ch=p[z].charAt(x);String b=switch(ch){case 'W'->"occultism:chalk_glyph_white";case 'X'->"occultism:chalk_glyph_purple";case '1'->"minecraft:candle";case '0'->"occultism:golden_sacrificial_bowl";default->null;};if(b!=null)put(c.p.offset(x-4,0,z-4),b);}
        var a=tile(c.p,GoldenSacrificialBowlBlockEntity.class);String[] ids={"artifacts:umbrella","minecraft:paper","kubejs:alchemical_catalyst","irons_spellbooks:arcane_essence"};List<SacrificialBowlBlockEntity> bowls=new ArrayList<>();
        for(int i=0;i<4;i++){BlockPos pp=c.p.offset(i*2-3,0,5);put(pp,"occultism:sacrificial_bowl");var t=tile(pp,SacrificialBowlBlockEntity.class);t.itemStackHandler.setStackInSlot(0,item(ids[i]));bowls.add(t);}
        ServerPlayer player=FakePlayerFactory.getMinecraft(world);player.setItemInHand(InteractionHand.MAIN_HAND,item("occultism:book_of_binding_bound_foliot"));
        BlockPos gap=c.p.offset(0,0,-3);put(gap,"minecraft:air");a.activate(world,c.p,player,InteractionHand.MAIN_HAND,Direction.UP);check(a.getCurrentRitualRecipe()==null,"Occultism accepts broken pentacle");put(gap,"occultism:chalk_glyph_purple");log("NEGATIVE PASS Occultism broken pentacle rejected");
        check(a.activate(world,c.p,player,InteractionHand.MAIN_HAND,Direction.UP)&&a.getCurrentRitualRecipe()!=null,"Occultism activation rejected");
        c.consumed=()->bowls.stream().allMatch(t->t.itemStackHandler.getStackInSlot(0).isEmpty());c.detail=()->"active="+a.ritualActive+" time="+a.currentTime+" remaining="+a.remainingAdditionalIngredients;
    }
    static void setupGoety(){
        Case c=new Case("Goety/boss_seal","kubejs:boss_seal",8,280){int outputCount(){var s=tile(p,DarkAltarBlockEntity.class).itemStackHandler.getStackInSlot(0);return super.outputCount()+(s.is(BuiltInRegistries.ITEM.get(id(out)))?s.getCount():0);}};
        put(c.p.below(),"goety:cursed_cage");put(c.p,"goety:dark_altar");var a=tile(c.p,DarkAltarBlockEntity.class);var cage=tile(c.p.below(),CursedCageBlockEntity.class);ItemStack totem=item("goety:totem_of_souls");totem.set(net.minecraft.core.component.DataComponents.CUSTOM_DATA,net.minecraft.world.item.component.CustomData.of(new net.minecraft.nbt.CompoundTag()));net.minecraft.world.item.component.CustomData.update(net.minecraft.core.component.DataComponents.CUSTOM_DATA,totem,t->t.putInt("Souls",2000));cage.setItem(totem);
        for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++)if(Math.abs(x)==4||Math.abs(z)==4)put(c.p.offset(x,0,z),"minecraft:bookshelf");
        put(c.p.offset(1,0,2),"minecraft:enchanting_table");put(c.p.offset(-1,0,2),"minecraft:lectern");tile(c.p.offset(-1,0,2),LecternBlockEntity.class).setBook(item("minecraft:book"));
        String[] ids={"cataclysm:ignitium_ingot","twilightforest:fiery_ingot","eternal_starlight:amaramber_ingot","goety:mystic_core","eidolon_repraised:soul_shard","hexerei:moon_dust","malum:arcane_spirit"};List<PedestalBlockEntity> ped=new ArrayList<>();
        for(int i=0;i<ids.length;i++){BlockPos pp=c.p.offset(RING[i][0],0,RING[i][1]);put(pp,"goety:pedestal");var t=tile(pp,PedestalBlockEntity.class);t.itemStackHandler.setStackInSlot(0,item(ids[i]));ped.add(t);}
        var player=FakePlayerFactory.getMinecraft(world);player.setItemInHand(InteractionHand.MAIN_HAND,item("kubejs:ritual_frame"));
        var lectern=tile(c.p.offset(-1,0,2),LecternBlockEntity.class);lectern.setBook(ItemStack.EMPTY);a.activate(world,c.p,player,InteractionHand.MAIN_HAND,Direction.UP);check(a.getCurrentRitualRecipe()==null,"Goety accepts incomplete magic structure");lectern.setBook(item("minecraft:book"));log("NEGATIVE PASS Goety empty lectern rejected");
        check(a.activate(world,c.p,player,InteractionHand.MAIN_HAND,Direction.UP)&&a.getCurrentRitualRecipe()!=null,"Goety activation rejected");
        c.consumed=()->ped.stream().allMatch(t->t.itemStackHandler.getStackInSlot(0).isEmpty())&&cage.getSouls()==1000;
        c.detail=()->"time="+a.currentTime+" souls="+cage.getSouls()+" remaining="+a.remainingAdditionalIngredients;
    }
    static void setupEvilBootstrap(){
        Case c=new Case("EvilCraft/first_dark_power_gem","evilcraft:dark_power_gem",1,320);
        List<BlockPos> sources=List.of(c.p,c.p.north(),c.p.south(),c.p.east(),c.p.west());
        // Shallow stone basin, five source blocks, normal dropped-item update.
        for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++)if(Math.abs(x)==2||Math.abs(z)==2)put(c.p.offset(x,0,z),"minecraft:stone");
        for(var p:sources)put(p,"evilcraft:blood");
        var gem=new ItemEntity(world,c.p.getX()+0.5,c.p.getY()+0.2,c.p.getZ()+0.5,item("evilcraft:dark_gem"));gem.setDeltaMovement(0,0,0);world.addFreshEntity(gem);
        c.consumed=()->gem.getItem().isEmpty()&&sources.stream().noneMatch(p->world.getFluidState(p).isSource());
        c.detail=()->"native dropped-gem conversion, no blood infuser placed";
    }
}
