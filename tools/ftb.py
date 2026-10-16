import concurrent.futures,hashlib,json,subprocess,urllib.request,xml.etree.ElementTree as ET
from catalog import ROOT
def fetch(name):
    base='https://maven.ftb.dev/releases/dev/ftb/mods/'+name+'-neoforge/'
    xml=ET.fromstring(subprocess.check_output(['curl.exe','-fLsS','--retry','3',base+'maven-metadata.xml']))
    versions=[x.text for x in xml.findall('.//version') if x.text.startswith('21.1.' if name=='ftb-xmod-compat' else '2101.')]
    version='21.1.11' if name=='ftb-xmod-compat' else max(versions,key=lambda s:tuple(int(p) for p in s.split('.')))
    filename=name+'-neoforge-'+version+'.jar'
    url=base+version+'/'+filename
    dest=ROOT/'cache/files'/filename
    subprocess.run(['curl.exe','-fLsS','--retry','3','-o',str(dest),url],check=True)
    expected=subprocess.check_output(['curl.exe','-fLsS','--retry','3',url+'.sha1']).decode().strip().split()[0]
    assert hashlib.sha1(dest.read_bytes()).hexdigest()==expected
    import shutil
    for p in [ROOT/'build/server/mods',ROOT/'build/prism/Arcane Industry Prototype/minecraft/mods']:
        for stale in p.glob(name+'-neoforge-*.jar'):
            if stale.name!=filename:
                assert stale.resolve().is_relative_to((ROOT/'build').resolve())
                stale.unlink()
        shutil.copy2(dest,p/filename)
    print(name,version,flush=True)
    return {'slug':name,'version':version,'filename':filename,'url':url,'sha1':expected,'sha512':hashlib.sha512(dest.read_bytes()).hexdigest(),'client':True,'server':True,'source':'https://www.feed-the-beast.com/','category':'team-and-quests'}
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex: rows=list(ex.map(fetch,['ftb-library','ftb-teams','ftb-quests','ftb-chunks','ftb-ultimine','ftb-xmod-compat']))
    (ROOT/'ftb.lock.json').write_text(json.dumps(rows,indent=2),'utf-8')
