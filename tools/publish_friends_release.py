"""Publish sanitized source and large archives to a GitHub Release, using Git Credential Manager."""
import os,subprocess,json,pathlib,urllib.request,urllib.error,urllib.parse,http.client,time,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT/'build/publish-repo'
os.environ['GIT_TERMINAL_PROMPT']='0';os.environ['GCM_INTERACTIVE']='never'
r=subprocess.run(['git','credential','fill'],input='protocol=https\nhost=github.com\n\n',text=True,capture_output=True,check=True)
credentials=dict(l.split('=',1) for l in r.stdout.splitlines() if '=' in l)
token=credentials['password']
def api(route,data=None,method=None):
    req=urllib.request.Request('https://api.github.com'+route,data=json.dumps(data).encode() if data is not None else None,
      headers={'Authorization':'Bearer '+token,'User-Agent':'ArcaneIndustry-Release','Accept':'application/vnd.github+json','Content-Type':'application/json'},method=method)
    with urllib.request.urlopen(req,timeout=90) as response:return json.load(response)
login=api('/user')['login'];assert login=='Schnazzy6','Unexpected GitHub account'
name='arcane-industry'
try:
    existing=api('/repos/'+login+'/'+name)
    if existing.get('description')!='Arcane Industry: cooperative Minecraft 1.21.1 modpack for friends':
        name='arcane-industry-modpack'
        try:api('/repos/'+login+'/'+name);raise RuntimeError('Both names already exist; refusing to overwrite unrelated repositories')
        except urllib.error.HTTPError as e:
            if e.code!=404:raise
        existing=None
except urllib.error.HTTPError as e:
    if e.code!=404:raise
    existing=None
if not existing:
    existing=api('/user/repos',{'name':name,'description':'Arcane Industry: cooperative Minecraft 1.21.1 modpack for friends','private':False,'auto_init':False})
url=existing['html_url'];print('Repository:',url,flush=True)
def git(*args):subprocess.run(['git',*args],cwd=REPO,check=True)
if not (REPO/'.git').exists():
    git('init','-b','main');git('config','user.name',login);git('config','user.email','81328276+'+login+'@users.noreply.github.com');git('remote','add','origin',url+'.git')
git('add','.')
if subprocess.run(['git','diff','--cached','--quiet'],cwd=REPO).returncode:
    git('commit','-m','Release Arcane Industry 0.2.0: quests, visual settings and Radmin server')
git('push','-u','origin','main')
route='/repos/'+login+'/'+name
try:release=api(route+'/releases/tags/v0.2.0')
except urllib.error.HTTPError as e:
    if e.code!=404:raise
    release=api(route+'/releases',{'tag_name':'v0.2.0','name':'Arcane Industry 0.2.0 — готовая сборка для друзей','draft':True,
      'body':'Клиент: скачайте Prism.zip и импортируйте в Prism Launcher.\nХост: Server.zip содержит Java 21 и скрипты Radmin VPN.\n557 русских квестов, предметные награды, Configured, JEI, текстурпаки и шейдеры с настройками.\nПолные инструкции находятся в README и SERVER-GUIDE.md.\nСохранения и аккаунты не включены.'})
assets={a['name']:a for a in release['assets']}
for filename in ['ArcaneIndustry-0.2.0-Prism.zip','ArcaneIndustry-0.2.0-Server.zip']:
    file=ROOT/'dist'/filename
    if filename in assets:
        if assets[filename]['size']==file.stat().st_size:
            print('Already uploaded:',filename,flush=True);continue
        raise RuntimeError('Existing release asset differs: '+filename)
    path='/repos/'+login+'/'+name+'/releases/'+str(release['id'])+'/assets?'+urllib.parse.urlencode({'name':filename})
    conn=http.client.HTTPSConnection('uploads.github.com',timeout=180)
    conn.putrequest('POST',path);conn.putheader('Authorization','Bearer '+token);conn.putheader('User-Agent','ArcaneIndustry-Release')
    conn.putheader('Content-Type','application/zip');conn.putheader('Content-Length',str(file.stat().st_size));conn.endheaders()
    sent=0;last=time.monotonic()
    with file.open('rb') as source:
        while chunk:=source.read(1024*1024):
            conn.send(chunk);sent+=len(chunk)
            if time.monotonic()-last>=15:
                print(filename,str(round(sent/file.stat().st_size*100))+'%',flush=True);last=time.monotonic()
    response=conn.getresponse();body=response.read();conn.close()
    if response.status!=201:raise RuntimeError('Asset upload failed: '+str(response.status)+' '+body[:300].decode(errors='replace'))
    print('Uploaded:',json.loads(body)['browser_download_url'],flush=True)
release=api(route+'/releases/'+str(release['id']),{'draft':False},method='PATCH')
result={'repository':url,'release':release['html_url'],'assets':[{'name':a['name'],'url':a['browser_download_url'],'size':a['size']} for a in api(route+'/releases/'+str(release['id']))['assets']]}
(ROOT/'build/published-release.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False),flush=True)
