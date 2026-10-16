"""Snapshot the current tested instance. Never package accounts, worlds or per-world JEI state."""
import os,pathlib,shutil,json,re,hashlib,zipfile,urllib.request,datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
GAME=pathlib.Path(os.environ['APPDATA'])/'PrismLauncher/instances/ArcaneIndustry-0.1.4/minecraft'
VERSION='0.2.0'
STAGE=ROOT/'build/friends-release';CLIENT=STAGE/'ArcaneIndustry-0.2.0';MC=CLIENT/'minecraft'
SERVER=ROOT/'server';DIST=ROOT/'dist';REPO=ROOT/'build/publish-repo'
for p in [MC,SERVER,DIST,REPO]:p.mkdir(parents=True,exist_ok=True)
backup=ROOT/'build/release-settings-backup'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup.mkdir(parents=True)
def copy(src,dst):
    if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True)
    else:dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def request(url):return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ArcaneIndustry-Release'})))
release=request('https://api.github.com/repos/MrCrayfish/Configured/releases/tags/v1.21.1-2.6.3')
asset=next(a for a in release['assets'] if a['name'].startswith('configured-neoforge') and a['name'].endswith('.jar'))
configured=ROOT/'cache/files'/asset['name']
if not configured.exists():urllib.request.urlretrieve(asset['browser_download_url'],configured)
if asset.get('digest'):
    assert hashlib.sha256(configured.read_bytes()).hexdigest()==asset['digest'].split(':')[1]
copy(configured,GAME/'mods'/configured.name)
copy(configured,ROOT/'build/prism/Arcane Industry Prototype/minecraft/mods'/configured.name)
jei=GAME/'config/jei/jei-client.ini';copy(jei,backup/'jei-client.ini')
text=jei.read_text(encoding='utf-8')
for key,value in {'centerSearch':'true','enableRecipesGuiIngredientsSummary':'true','lookupFluidContentsEnabled':'true','drawBackground':'true','recipeGuiHeight':'420'}.items():
    text=re.sub(r'(?m)^(\s*'+key+r'\s*=).*$',r'\g<1> '+value,text)
def section_setting(text,section,key,value):
    pattern=r'(?ms)(^\['+re.escape(section)+r'\].*?)(?=^\[|\Z)'
    return re.sub(pattern,lambda m:re.sub(r'(?m)^(\s*'+key+r'\s*=).*$',r'\g<1> '+str(value),m[1]),text)
text=section_setting(text,'ingredientList','maxColumns',10)
text=section_setting(text,'bookmarkList','maxColumns',5)
text=section_setting(text,'bookmarkList','maxRows',14)
jei.write_text(text,encoding='utf-8')
copy(jei,ROOT/'overrides/client/config/jei/jei-client.ini')
# The working client's per-world UI state stays private; fresh imports start with empty search.
for d in ['mods','resourcepacks','shaderpacks']:
    copy(GAME/d,MC/d)
copy(GAME/'config',MC/'config')
copy(ROOT/'overrides/common',MC);copy(ROOT/'overrides/client',MC)
for rel in ['config/jei/world','config/jei/client']:
    p=(MC/rel).resolve();assert p.is_relative_to(MC.resolve())
    if p.exists():shutil.rmtree(p)
for p in list(MC.rglob('*.disabled')):p.unlink()
for p in [MC/'kubejs/config/web_server.json']:
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'enabled':False,'port':61423,'public_address':'','auth':''}),encoding='utf-8')
options={l.split(':',1)[0]:l.split(':',1)[1] for l in (GAME/'options.txt').read_text(encoding='utf-8').splitlines() if ':' in l}
options.update({'maxFps':'120','renderDistance':'12','simulationDistance':'6','guiScale':'3','lang':'ru_ru','fullscreen':'false','lastServer':''})
# No accounts or computer-specific paths; shader profiles are portable.
(MC/'options.txt').write_text('\n'.join(k+':'+v for k,v in options.items())+'\n',encoding='utf-8')
(MC/'config/iris.properties').write_text('enableShaders=true\nshaderPack=ComplementaryReimagined_r5.9.3.zip\nmaxShadowRenderDistance=8\n',encoding='utf-8')
(MC/'shaderpacks/ComplementaryReimagined_r5.9.3.zip.txt').write_text('SHADOW_QUALITY=0\nshadowDistance=64.0\nBLOCK_REFLECT_QUALITY=1\nWATER_REFLECT_QUALITY=1\nLIGHTSHAFT_QUALI_DEFINE=1\nENTITY_SHADOW=-1\n',encoding='utf-8')
copy(GAME.parent/'mmc-pack.json',CLIENT/'mmc-pack.json')
(CLIENT/'instance.cfg').write_text('[General]\nInstanceType=OneSix\nname=Arcane Industry 0.2.0\niconKey=default\nOverrideMemory=true\nMinMemAlloc=2048\nMaxMemAlloc=8192\nOverrideJavaLocation=false\nAutomaticJava=true\nOverrideJavaArgs=true\nJvmArgs=-XX:+UseG1GC\n',encoding='utf-8')
# Separate production server: never copy the smoke-test world, operators or player identities.
for d in ['mods','libraries','config','defaultconfigs','kubejs']:
    source=ROOT/'build/server'/d
    if source.exists():copy(source,SERVER/d)
copy(ROOT/'overrides/common',SERVER)
for p in (SERVER/'kubejs/config').glob('*'):
    if p.name in ['recipe-dump.json','recipe-audit.json','gear-stats.json','item-usage.json']:p.unlink()
(SERVER/'kubejs/config/web_server.json').write_text(json.dumps({'enabled':False,'port':61423,'public_address':'','auth':''}),encoding='utf-8')
java=next((ROOT/'runtime/java21').glob('*/bin/java.exe')).parent.parent
copy(java,SERVER/'runtime/java21')
(SERVER/'eula.txt').write_text('eula=true\n',encoding='ascii')
(SERVER/'server.properties').write_text('server-ip=\nserver-port=25565\nonline-mode=true\nenforce-secure-profile=false\nlevel-name=world\ndifficulty=normal\ngamemode=survival\nmax-players=4\nview-distance=10\nsimulation-distance=6\nallow-flight=true\nspawn-protection=0\npvp=true\nwhite-list=false\nenable-rcon=false\nmotd=Arcane Industry 0.2.0\n',encoding='ascii')
(SERVER/'user_jvm_args.txt').write_text('-Xms2G\n-Xmx8G\n-XX:+UseG1GC\n',encoding='ascii')
for name in ['Start-Server.cmd','Start-Server.ps1','Configure-Firewall.cmd','Configure-Firewall.ps1','Backup-World.cmd','Backup-World.ps1']:
    copy(ROOT/'release-scripts'/name,SERVER/name)
copy(ROOT/'SERVER-GUIDE.md',SERVER/'SERVER-GUIDE.md')
copy(ROOT/'FRIENDS-README.md',CLIENT/'README.md')
def manifest(base):
    return [{'file':str(p.relative_to(base)).replace('\\','/'),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for d in ['mods','resourcepacks','shaderpacks'] for p in sorted((base/d).glob('*')) if p.is_file()]
files=manifest(MC)
(CLIENT/'FILES-SHA256.json').write_text(json.dumps(files,ensure_ascii=False,indent=2),encoding='utf-8')
def pack(base,target,exclude=()):
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for p in sorted(base.rglob('*')):
            rel=p.relative_to(base)
            if p.is_file() and not any(part in exclude for part in rel.parts):z.write(p,pathlib.Path(base.name)/rel)
    print('Archive:',target.name,round(target.stat().st_size/1024**2),'MiB',flush=True)
pack(CLIENT,DIST/'ArcaneIndustry-0.2.0-Prism.zip')
pack(SERVER,DIST/'ArcaneIndustry-0.2.0-Server.zip',('world','logs','crash-reports','backups'))
for name in ['FRIENDS-README.md','SERVER-GUIDE.md']:copy(ROOT/name,REPO/('README.md' if name.startswith('FRIENDS') else name))
for d in ['overrides','tools','release-scripts']:
    copy(ROOT/d,REPO/d)
# Never publish local web-server credentials, caches, machine addresses or saved progress.
for p in REPO.rglob('web_server.json'):p.write_text(json.dumps({'enabled':False,'port':61423,'public_address':'','auth':''}),encoding='utf-8')
for p in list(REPO.rglob('__pycache__')):
    assert p.resolve().is_relative_to(REPO.resolve());shutil.rmtree(p)
for p in list(REPO.rglob('*.pyc')):p.unlink()
for name in ['pack.lock.json','curse.lock.json','ftb.lock.json']:copy(ROOT/name,REPO/name)
(REPO/'release-manifest.json').write_text(json.dumps({'version':VERSION,'minecraft':'1.21.1','neoforge':'21.1.259','files':files},ensure_ascii=False,indent=2),encoding='utf-8')
(REPO/'.gitignore').write_text('build/\ncache/\ndist/\nserver/\n__pycache__/\n*.log\n*.pyc\n',encoding='utf-8')
print('Prepared',len(list((MC/'mods').glob('*.jar'))),'client mods;',len(list((SERVER/'mods').glob('*.jar'))),'server mods',flush=True)
