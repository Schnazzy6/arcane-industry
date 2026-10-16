"""Count untranslated item, block and enchantment names in installed mods."""
import json
import os
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
mods = Path(os.environ['APPDATA']) / 'PrismLauncher/instances/ArcaneIndustry-0.1.4/minecraft/mods'
overrides = root / 'overrides/client/kubejs/assets'
report = []
for jar in mods.glob('*.jar'):
    try:
        with zipfile.ZipFile(jar) as archive:
            names = set(archive.namelist())
            for path in names:
                if not path.startswith('assets/') or not path.endswith('/lang/en_us.json'):
                    continue
                namespace = path.split('/')[1]
                english = json.loads(archive.read(path))
                russian_path = path.replace('/en_us.json', '/ru_ru.json')
                russian = json.loads(archive.read(russian_path)) if russian_path in names else {}
                custom_path = overrides / namespace / 'lang/ru_ru.json'
                custom = json.loads(custom_path.read_text('utf-8')) if custom_path.exists() else {}
                wanted = {key for key in english if key.startswith(('item.', 'block.', 'enchantment.'))}
                missing = sorted(wanted - russian.keys() - custom.keys())
                if missing:
                    report.append({'jar': jar.name, 'namespace': namespace, 'missing': len(missing), 'keys': missing})
    except (zipfile.BadZipFile, ValueError, KeyError):
        continue
report.sort(key=lambda x: x['missing'], reverse=True)
out = root / 'build/translation-audit.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf-8')
print('namespaces', len(report), 'untranslated keys', sum(row['missing'] for row in report))
print([(row['namespace'], row['missing']) for row in report[:25]])
