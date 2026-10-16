import concurrent.futures,json
from catalog import inspect,ROOT
slugs=['immersiveengineering','pneumaticcraft-repressurized','cc-tweaked','immersive-aircraft','createaddition','create-diesel-generators','create-new-age','industrial-foregoing','integrated-dynamics']
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: rows=list(pool.map(inspect,[('tech',s) for s in slugs]))
(ROOT/'tech-candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf-8')
for r in rows:print(r['requested'],r['version']['version_number'] if r.get('version') else r['status'])
