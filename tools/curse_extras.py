import concurrent.futures,json,hashlib,shutil,subprocess,zipfile,urllib.parse
from catalog import ROOT
FILES=[('born-in-chaos',686437,8268280,'born_in_chaos_[Neoforge]_1.21.1_1.7.6.jar','1.7.6'),('twilight-forest',227639,7797302,'twilightforest-1.21.1-4.8.3345-universal.jar','4.8.3345'),('apothic-compats',1188699,8996735,'apothic_compats-0.2.5.5.jar','0.2.5.5'),('ars-elemancy',1153666,8349780,'ars_elemancy-1.21.1-1.18.3.jar','1.18.3'),('ae2-jei-integration',1074338,7727898,'ae2jeiintegration-1.2.1.jar','1.2.1'),('ars-elemental',561470,9057244,'ars_elemental-1.21.1-0.7.10.4.jar','0.7.10.4')]
def fetch(row):
    slug,pid,fid,filename,version=row
    url=f'https://edge.forgecdn.net/files/{fid//1000}/{fid%1000:03d}/{urllib.parse.quote(filename,safe='')}'
    dest=ROOT/'cache/files'/filename
    if not dest.exists():subprocess.run(['curl.exe','-fLsS','--retry','3','-o',str(dest),url],check=True)
    with zipfile.ZipFile(dest) as z: assert z.testzip() is None
    for p in [ROOT/'build/server/mods',ROOT/'build/prism/Arcane Industry Prototype/minecraft/mods']:
        if slug=='mi-multiblock-emi' and p==ROOT/'build/server/mods':continue
        shutil.copy2(dest,p/filename)
    print(slug,version,flush=True)
    return {'slug':slug,'title':slug,'curseforge_project_id':pid,'curseforge_file_id':fid,'version':version,'filename':filename,'url':url,'sha512':hashlib.sha512(dest.read_bytes()).hexdigest(),'sha1':hashlib.sha1(dest.read_bytes()).hexdigest(),'client':True,'server':slug!='mi-multiblock-emi','category':'integration','source':f'https://www.curseforge.com/minecraft/mc-mods/{slug}/files/{fid}'}
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex: rows=list(ex.map(fetch,FILES))
    (ROOT/'curse.lock.json').write_text(json.dumps(rows,indent=2),'utf-8')
