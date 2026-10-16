import concurrent.futures,json,sys
from catalog import ROOT,inspect
sys.stdout.reconfigure(encoding='utf-8')
slugs='industrialization-overdrive yet-another-industrialization modern-industrialization-sound-addon solar-industrialization hostile-neural-industrialization mi-parallel-hatch mi-item-hatch-stack-upgrade mi-item-fluid-combined-hatch mimsf modern-industrialization-cc-tweaked-compat mi-utilities modern-industrial-routers modern-industrialization-explosivity mi-hand-crank-power mi-structure-exporter'
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:rows=list(pool.map(inspect,[('mi-addon',s) for s in slugs.split()]))
(ROOT/'mi-addons.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf-8')
for r in rows:
    print(r['requested'],r['version']['version_number'] if r.get('version') else r['status'],r.get('project',{}).get('description',''),flush=True)
