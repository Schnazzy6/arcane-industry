"""Local, version-specific content index for cross-mod recipe design."""
import json,zipfile
from catalog import ROOT
tokens=['eternal','born','cataclysm','relics-','artifacts-','ars_elemental','ars_additions','ars_ocultas','arseng','advancedae','extendedae','croptopia','farmersdelight','simplyswords','mowzies','mekanism_extras']
out={}
for jar in (ROOT/'build/server/mods').glob('*.jar'):
 if not any(t in jar.name.lower() for t in tokens):continue
 with zipfile.ZipFile(jar) as z:
  for path in z.namelist():
   if path.startswith('assets/') and path.endswith('/lang/en_us.json'):
    ns=path.split('/')[1]
    try:lang=json.loads(z.read(path))
    except ValueError:continue
    out[ns]={'jar':str(jar),'items':[k for k in lang if k.startswith(('item.'+ns+'.','block.'+ns+'.')) and k.count('.')==2],
             'recipes':{p:json.loads(z.read(p)) for p in z.namelist() if p.startswith('data/'+ns+'/recipe/') and p.endswith('.json')}}
(ROOT/'build/connected-content.json').write_text(json.dumps(out,ensure_ascii=False),'utf-8')
print('Namespaces:',', '.join(out))
