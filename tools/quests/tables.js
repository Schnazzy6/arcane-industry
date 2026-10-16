// Equal-weight supply tables. Only chapter-completion milestones award one roll.
const supplies={
  era0:[['minecraft:bread',4],['minecraft:torch',8],['minecraft:oak_log',8]],
  era1:[['minecraft:iron_ingot',4],['minecraft:coal',12],['minecraft:glass',8]],
  era2:[['minecraft:copper_ingot',8],['minecraft:redstone',8],['minecraft:iron_ingot',4]],
  era3:[['minecraft:gold_ingot',4],['minecraft:redstone',16],['minecraft:glass',16]],
  era4:[['minecraft:diamond',2],['minecraft:gold_ingot',8],['minecraft:obsidian',8]],
  era5:[['minecraft:diamond',3],['minecraft:gold_ingot',12],['minecraft:quartz',16]],
  magic0:[['minecraft:lapis_lazuli',8],['minecraft:paper',16],['minecraft:amethyst_shard',8]],
  magic1:[['minecraft:lapis_lazuli',12],['minecraft:paper',24],['minecraft:gold_ingot',4]],
  explore:[['minecraft:cooked_beef',8],['minecraft:arrow',32],['minecraft:torch',16]],
};

module.exports = [
  {
    "k": "era0",
    "t": "Ящик: начало пути"
  },
  {
    "k": "era1",
    "t": "Ящик: эра пара"
  },
  {
    "k": "magic0",
    "t": "Ящик: ученик мага"
  },
  {
    "k": "era2",
    "t": "Ящик: электричество"
  },
  {
    "k": "magic1",
    "t": "Ящик: алхимик"
  },
  {
    "k": "era3",
    "t": "Ящик: промышленность"
  },
  {
    "k": "era4",
    "t": "Ящик: поздний MI"
  },
  {
    "k": "era5",
    "t": "Ящик: Tech Reborn"
  },
  {
    "k": "explore",
    "t": "Ящик: трофеи путешественника"
  }
].map(table => ({...table, items: supplies[table.k].map(item => [...item, 1])}));
