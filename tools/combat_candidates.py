import concurrent.futures,json
from catalog import inspect,ROOT
slugs=['apotheosis','apothic-enchanting','apothic-attributes','apothic-spawners','placebo','gateways-to-eternity','champions-unofficial','borninchaos','mowzies-mobs','legendary-monsters','simply-swords','simply-more','better-combat','epic-knights-shields-armor-and-weapons','immersive-armors','mutant-monsters','enhanced-celestials','relics-mod','draconic-evolution','bigger-reactors','extreme-reactors','mekanism','oritech','modular-routers','rftools-builder','rftools-dimensions','laser-io','powah','ender-io','create-stuff-additions','building-gadgets2','extended-industrialization','industrialization-overdrive','modern-industrialization-cc-tweaked-compat']
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool: rows=list(pool.map(inspect,[('combat' if i<22 else 'tech',s) for i,s in enumerate(slugs)]))
(ROOT/'combat-candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf-8')
for r in rows:print(r['requested'],r['version']['version_number'] if r.get('version') else r['status'],flush=True)
