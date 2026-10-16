"""Install the exact NeoForge release of Eleriom's stacked HUD bars."""
import hashlib
import json
import os
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[1]
with urllib.request.urlopen('https://api.modrinth.com/v2/version/PYRrjTaY', timeout=30) as response:
    version = json.load(response)
file = next(row for row in version['files'] if row['primary'])
data = urllib.request.urlopen(file['url'], timeout=30).read()
assert hashlib.sha512(data).hexdigest() == file['hashes']['sha512']
assert version['loaders'] == ['neoforge'] and '1.21.1' in version['game_versions']
filename = file['filename']
for directory in (
    root / 'build/prism/Arcane Industry Prototype/minecraft/mods',
    Path(os.environ['APPDATA']) / 'PrismLauncher/instances/ArcaneIndustry-0.1.4/minecraft/mods',
):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / filename).write_bytes(data)
lock_path = root / 'pack.lock.json'
lock = json.loads(lock_path.read_text('utf-8'))
record = {
    'slug': 'overflowing-bars', 'title': 'Overflowing Bars',
    'project_id': 'XD7XOrAF', 'version_id': version['id'],
    'version': version['version_number'], 'filename': filename,
    'url': file['url'], 'sha512': file['hashes']['sha512'],
    'sha1': file['hashes']['sha1'], 'size': len(data),
    'client': True, 'server': False, 'category': 'hud',
    'source': 'https://modrinth.com/mod/overflowing-bars',
}
lock['mods'] = sorted([row for row in lock['mods'] if row['slug'] != record['slug']] + [record], key=lambda row: row['slug'])
lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(filename, len(data))
