"""Local-only server smoke test; never opens the firewall or changes production worlds."""
import pathlib,subprocess,time,threading,json,sys
from catalog import ROOT
SERVER=ROOT/'build/server'
JAVA=next((ROOT/'runtime/java21').glob('*/bin/java.exe'))
args=[str(JAVA),'-Xms2G','-Xmx8G','@libraries/net/neoforged/neoforge/21.1.259/win_args.txt','nogui']
(SERVER/'eula.txt').write_text('eula=true\n','ascii')
(SERVER/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25575\nonline-mode=true\nlevel-name=smoke-test-world\nlevel-seed=739142568\nview-distance=8\nsimulation-distance=6\nmax-players=4\nallow-flight=true\nenable-rcon=false\nmotd=Arcane Industry local smoke test\n','ascii')
if '--offline-auth' in sys.argv:
    prop=SERVER/'server.properties'
    prop.write_text(prop.read_text().replace('online-mode=true','online-mode=false'),'ascii')
if '--ritual-world' in sys.argv:
    prop=SERVER/'server.properties'
    prop.write_text(prop.read_text().replace('level-name=smoke-test-world','level-name=ritual-test-world'),'ascii')
logpath=ROOT/'build/server-smoke.log'
lines=[]
proc=subprocess.Popen(args,cwd=SERVER,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',bufsize=1)
(ROOT/'build/server-test.pid').write_text(str(proc.pid))
def reader():
    with logpath.open('w',encoding='utf-8') as log:
        for line in proc.stdout:
            log.write(line);log.flush();lines.append(line)
t=threading.Thread(target=reader,daemon=True);t.start()
start=time.time();ready=False
while time.time()-start<360:
    if any('Done (' in s for s in lines):ready=True;break
    if proc.poll() is not None:break
    time.sleep(1)
if ready:
    print('SERVER READY after',round(time.time()-start,1),'seconds',flush=True)
    for command in ['list','execute in minecraft:overworld run forceload add 0 0 31 31','execute in minecraft:the_nether run forceload add 0 0 15 15','execute in minecraft:the_end run forceload add 0 0 15 15']:
        proc.stdin.write(command+'\n');proc.stdin.flush();time.sleep(2)
    if '--stay' in sys.argv:
        print('Server waiting for client test ('+('until stop command' if '--keep-running' in sys.argv else 'up to 20 minutes')+')',flush=True)
        commandfile=ROOT/'build/server-commands.txt'
        commandfile.write_text('','utf-8')
        sent=0
        deadline=float('inf') if '--keep-running' in sys.argv else time.time()+1200
        while time.time()<deadline and proc.poll() is None:
            commands=commandfile.read_text('utf-8').splitlines()
            for command in commands[sent:]:
                proc.stdin.write(command+'\n');proc.stdin.flush()
            sent=len(commands)
            time.sleep(2)
    else:time.sleep(15)
if proc.poll() is None:
    proc.stdin.write('stop\n');proc.stdin.flush()
    try:proc.wait(90)
    except subprocess.TimeoutExpired:proc.terminate();proc.wait(30)
t.join(timeout=5)
print('Exit',proc.returncode,'ready',ready,flush=True)
print(''.join(lines[-35:]))
sys.exit(0 if ready and proc.returncode==0 else 1)
