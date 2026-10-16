"""Isolated Connector trial. Never changes the production instance or worlds."""
import os, pathlib, shutil, json, subprocess, threading, time, sys, zipfile
from catalog import ROOT
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = ROOT / 'build/techreborn-test'
INSTANCE = pathlib.Path(os.environ['APPDATA']) / 'PrismLauncher/instances/ArcaneIndustry-TechReborn-Test'
SERVER = BASE / 'server'

def patch_recipes():
    patched = []
    with zipfile.ZipFile(BASE/'AdvancedReborn-1.21.1-1.3.4.jar') as jar:
        for name in jar.namelist():
            if '/recipe/' not in name or not name.endswith('.json'): continue
            data = json.loads(jar.read(name))
            if data.get('type') not in ['minecraft:crafting_shaped', 'minecraft:crafting_shapeless']: continue
            result = data.get('result', {})
            if 'item' in result: result['id'] = result.pop('item')
            def ingredient(value):
                if isinstance(value, str): return {'tag': value[1:]} if value.startswith('#') else {'item': value}
                if isinstance(value, list): return [ingredient(x) for x in value]
                return value
            if 'key' in data: data['key'] = {k:ingredient(v) for k,v in data['key'].items()}
            if 'ingredients' in data: data['ingredients'] = [ingredient(v) for v in data['ingredients']]
            for folder in [SERVER, INSTANCE/'minecraft']:
                dest = folder/'kubejs'/name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(json.dumps(data, indent=2), 'utf-8')
            patched.append(name)
    (BASE/'recipe-patches.json').write_text(json.dumps(patched, indent=2), 'utf-8')
    print('Updated Advanced Reborn crafting result format:', len(patched))

def prepare():
    original = INSTANCE.parent / 'ArcaneIndustry-0.1.4'
    INSTANCE.mkdir(exist_ok=True)
    for name in ['mmc-pack.json', 'instance.cfg']:
        shutil.copy2(original/name, INSTANCE/name)
    cfg = INSTANCE/'instance.cfg'
    cfg.write_text(cfg.read_text('utf-8').replace('name=Arcane Industry Prototype 0.1.4', 'name=Arcane Industry - Tech Reborn TEST'), 'utf-8')
    for source, target in [(original/'minecraft', INSTANCE/'minecraft'), (ROOT/'build/server', SERVER)]:
        target.mkdir(parents=True, exist_ok=True)
        for name in ['mods', 'config', 'defaultconfigs', 'kubejs', 'resourcepacks', 'shaderpacks', 'libraries']:
            if (source/name).exists(): shutil.copytree(source/name, target/name, dirs_exist_ok=True)
        for name in ['options.txt']:
            if (source/name).exists(): shutil.copy2(source/name, target/name)
        pins=ROOT/'tools/data/techreborn-pins.json'
        if pins.exists():
            for row in json.loads(pins.read_text('utf-8')):
                shutil.copy2(ROOT/'cache/files'/row['filename'],target/'mods'/row['filename'])
    (SERVER/'eula.txt').write_text('eula=true\n')
    (SERVER/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25576\nonline-mode=false\nlevel-name=techreborn-test-world\nlevel-seed=739142568\nview-distance=6\nsimulation-distance=4\nmax-players=4\nallow-flight=true\nenable-rcon=false\nspawn-protection=0\n', 'ascii')
    print('Prepared isolated client and server', flush=True)

def run():
    java = next((ROOT/'runtime/java21').glob('*/bin/java.exe'))
    proc = subprocess.Popen([str(java), '-Xms2G', '-Xmx10G', '@libraries/net/neoforged/neoforge/21.1.259/win_args.txt', 'nogui'], cwd=SERVER, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
    (BASE/'server.pid').write_text(str(proc.pid))
    queue = BASE/'commands.txt'; queue.write_text('')
    def reader():
        with (BASE/'server-console.log').open('w', encoding='utf-8') as out:
            for line in proc.stdout:
                out.write(line);out.flush()
                if 'Done (' in line or 'ERROR' in line: print(line.rstrip(), flush=True)
    threading.Thread(target=reader, daemon=True).start()
    sent = 0
    while proc.poll() is None:
        commands = queue.read_text('utf-8').splitlines()
        for command in commands[sent:]:
            proc.stdin.write(command+'\n');proc.stdin.flush()
        sent = len(commands)
        time.sleep(1)
    print('SERVER EXIT', proc.returncode, flush=True)

if __name__ == '__main__':
    if '--prepare' in sys.argv: prepare()
    elif '--patch-recipes' in sys.argv: patch_recipes()
    else: run()
