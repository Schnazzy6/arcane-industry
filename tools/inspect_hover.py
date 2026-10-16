import zipfile,json,re
from catalog import ROOT
lock=json.loads((ROOT/'pack.lock.json').read_text('utf-8'))['mods']
for slug in ['guideme','inventory-profiles-next','legendary-tooltips','inventory-essentials','iceberg']:
    z=zipfile.ZipFile(ROOT/'cache/files'/next(x['filename'] for x in lock if x['slug']==slug))
    print('\n',slug)
    for n in z.namelist():
        if n.endswith('.class') and any(v in n.lower() for v in ['hover','highlight','config','tooltip']):print(n)
        if n.endswith('/en_us.json'):
            t=json.loads(z.read(n))
            for k,v in t.items():
                if any(word in (k+' '+str(v)).lower() for word in ['highlight','hover','delay']):print(k,v)
