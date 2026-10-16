"""Check release archives and the real Radmin startup script; stop after readiness."""
import pathlib, zipfile, json, subprocess, socket, time, threading
ROOT=pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT/'dist').glob('*0.2.0*.zip'):
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        names=archive.namelist()
        assert not any('/saves/' in n or n.endswith('/servers.dat') or '/accounts.json' in n for n in names)
        assert not any('/world/' in n or '/logs/' in n for n in names)
        for n in names:
            if n.endswith('web_server.json'):
                conf=json.loads(archive.read(n));assert not conf.get('enabled') and not conf.get('auth')
    print('Archive integrity and privacy OK:',path.name,flush=True)
log=(ROOT/'build/friends-server-check.log').open('w',encoding='utf-8')
proc=subprocess.Popen(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'server/Start-Server.ps1')],cwd=ROOT/'server',stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
state={'ready':False,'address':None}
def read():
    for line in proc.stdout:
        log.write(line);log.flush()
        if 'Friends connect to:' in line:
            state['address']=line.split('Friends connect to:',1)[1].strip()
        if 'Done (' in line:
            state['ready']=True;print('Server reached Done; checking VPN listener',flush=True)
threading.Thread(target=read,daemon=True).start()
deadline=time.monotonic()+600
while not state['ready'] and proc.poll() is None and time.monotonic()<deadline:time.sleep(1)
try:
    assert state['ready'],f"Server did not reach Done (exit={proc.poll()}); see build/friends-server-check.log"
    host,port=state['address'].rsplit(':',1)
    with socket.create_connection((host,int(port)),timeout=10):pass
    print('Radmin TCP listener OK; requesting clean shutdown',flush=True)
finally:
    if proc.poll() is None:
        proc.stdin.write('stop\n');proc.stdin.flush()
        proc.wait(timeout=180)
    log.close()
assert proc.returncode==0,proc.returncode
print('PASS: real startup script, world startup, VPN listener and clean shutdown',flush=True)
