const fs = require('fs'), path = require('path');
const early = require('./early');
module.exports = function load() {
  const chapters = fs.readdirSync(__dirname).filter(f => /^ch_.*\.js$/.test(f)).map(f => {
    delete require.cache[require.resolve('./' + f)];
    return require('./' + f);
  }).sort((a,b) => a.order - b.order);
  for (const ch of chapters) {
    if (early[ch.k]) early[ch.k](ch);
    if (ch.k === 'gear') require('./gear-guide')(ch);
  }
  require('./polish')(chapters);
  require('./deduplicate')(chapters);
  require('./rewards')(chapters);
  require('./design')(chapters);
  return chapters;
};
