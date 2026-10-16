execute as @e[type=minecraft:arrow,tag=shootwindburst,nbt={inGround:true}] at @s run function effects:shoot_wind_charge
execute as @a if predicate enchants:not_flying run attribute @s minecraft:generic.gravity modifier remove minecraft:glide
execute as @a unless predicate enchants:flying_1 unless predicate enchants:flying_2 unless predicate enchants:flying_3 run attribute @s minecraft:generic.gravity modifier remove minecraft:glide
