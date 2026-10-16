"""Create portable Prism import and Windows server archives from the verified stages."""
import hashlib,json,pathlib,shutil,zipfile,os
from catalog import ROOT

DIST=ROOT/'dist';DIST.mkdir(exist_ok=True)
lock=json.loads((ROOT/'pack.lock.json').read_text('utf-8'))
mods=(json.loads((ROOT/'custom.lock.json').read_text('utf-8')) if (ROOT/'custom.lock.json').exists() else [])+lock['mods']+json.loads((ROOT/'ftb.lock.json').read_text('utf-8'))+json.loads((ROOT/'curse.lock.json').read_text('utf-8'))
lock['mods']=sorted(mods,key=lambda x:x['slug'])
(DIST/'manifest.lock.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2),'utf-8')
CLIENT=ROOT/'build/prism/Arcane Industry Prototype'
GAME=CLIENT/'minecraft'
SERVER=ROOT/'build/server'
shutil.copytree(ROOT/'overrides/client',GAME,dirs_exist_ok=True)

# Never include playtest worlds, player identities, logs, account data or local Java paths.
portable_cfg='''[General]
InstanceType=OneSix
name=Arcane Industry Prototype 0.1.4
iconKey=default
OverrideMemory=true
MinMemAlloc=2048
MaxMemAlloc=10240
OverrideJavaLocation=false
AutomaticJava=true
OverrideJavaArgs=true
JvmArgs=-XX:+UseG1GC
OverrideWindow=true
LaunchMaximized=false
MinecraftWinWidth=1280
MinecraftWinHeight=720
'''

client_options=(GAME/'options.txt').read_text('utf-8')
bindings={
 'key_iris.keybind.reload':'key.keyboard.f8',
 'key_iris.keybind.toggleShaders':'key.keyboard.f6',
 'key_iris.keybind.shaderPackSelection':'key.keyboard.unknown',
 'key_key.moreoverlays.lightoverlay.desc':'key.keyboard.f7',
 'key_key.moreoverlays.chunkbounds.desc':'key.keyboard.f9',
 'key_key.occultism.backpack':'key.keyboard.b:SHIFT',
 'key_key.goety.ceaseFire':'key.keyboard.b:CONTROL',
}
option_map={line.split(':',1)[0]:line.split(':',1)[1] for line in client_options.splitlines() if ':' in line}
option_map.update(bindings)
option_map['version']='3955'
fresh=next(x for x in mods if x['slug']=='fresh-animations')
option_map['resourcePacks']=json.dumps(['vanilla','file/'+fresh['filename'],'file/ArcaneIndustry-HUD.zip'])
client_options='\n'.join(key+':'+value for key,value in option_map.items())
(GAME/'options.txt').write_text(client_options.strip()+'\n','utf-8')
(GAME/'config/iris.properties').write_text('enableShaders=false\nshaderPack=ComplementaryReimagined_r5.9.3.zip\n','utf-8')
shader_options='''SHADOW_QUALITY=0
shadowDistance=96.0
WATER_REFLECT_QUALITY=2
BLOCK_REFLECT_QUALITY=1
LIGHTSHAFT_QUALI_DEFINE=1
SSAO_QUALI_DEFINE=2
FXAA_DEFINE=1
DETAIL_QUALITY=2
CLOUD_QUALITY=2
ANISOTROPIC_FILTER=0
COLORED_LIGHTING=0
WORLD_SPACE_REFLECTIONS=-1
ENTITY_SHADOW=-1
RAIN_PUDDLES=0
'''
(GAME/'shaderpacks/ComplementaryReimagined_r5.9.3.zip.txt').write_text(shader_options,'utf-8')

readme='''# Arcane Industry — прототип 0.1.4

Minecraft 1.21.1 · NeoForge 21.1.259 · Java 21 · Prism Launcher

Это технический прототип большой сборки. Экспертные рецепты, ограничения доступа
к этапам и русские авторские квесты ещё не добавлены. Сейчас действуют рецепты модов.
В том числе AE2 и дополнительные технологии пока ничем не заблокированы.

В 0.1.4 добавлены Mekanism + Generators 10.7.19.85 и возвращён Immersive Armors.
Draconic Evolution, BrandonsCore и Falling Leaves удалены; добавлен Blur+.
Mekanism ещё не ограничен прогрессией MI: рецепты пока стандартные.
Добавлены Mekanism Extras, Applied Mekanistics, Apothic Compats, дополнительные
зачарования, Dis-Enchanting Table, Born in Chaos, Twilight Forest и Eternal Starlight.
Артефакты расширены More Relics и четырьмя Reliquified. Полная карта — PROGRESSION.md,
результаты и границы проверки — TEST-REPORT.md.
Включён двусторонний адаптер MI EU/FE (1 EU = 10 FE); схема кабелей ещё проверяется.
Кнопка книги скрыта; Valheim Reforged работает с тремя блюдами.
Текстурпак HUD скрывает пустые фоны еды и уменьшает пузырьки воздуха. Raised не установлен.
Мана Iron’s вынесена влево вверх. Руды и обычные металлы унифицируются Almost Unified.

В 0.1.3 Modern Dynamics заменён на Pipez. EU машин MI передаётся кабелями MI.
В 0.1.4 добавлена Croptopia 4.2.4 с EpheroLib; Farmer’s Delight сохранён.
В 0.1.4 добавлены Cooking for Blockheads, Effortless Building, EMI Loot, EMI Ores,
Chat Heads и Leaves Be Gone. По новому запросу добавлены GraveStone Mod и Gravestone Carryables: вещи должны сохраняться в могиле; полный тест смерти/возврата Curios ещё нужен. Сон не менялся.
Samurai Dynasty и Ars Elemancy сохранены вместе с возвращённым Immersive Armors.
В 0.1.2 удалён Epic Knights; добавлены Fresh Animations и EMF/ETF для анимаций мобов.
Not Enough Animations уже отвечает за дополнительные движения игрока; Better Combat — за бой.
Simply Swords содержит катаны и уникальное стихийное оружие: Frostfall, Icewhisper, Emberblade.

В 0.1.1: Extended Industrialization, Industrialization Overdrive, YAI, MI Utilities,
MI Sound Addon, MI-Multiblock-EMI, Draconic Evolution и Re:Avaritia. Добавлены
Apotheosis и его модули, Champions Unofficial, Gateways to Eternity, Mowzie's Mobs,
Mutant Monsters, Simply Swords, Better Combat и Relics.
Lootr установлен на обеих сторонах: персональная добыча в поддерживаемых контейнерах.
Удалены AE Additions, Expanded AE, повторяющиеся дополнения запросов/шаблонов,
Inventory Profiles Next и AppleSkin. Кнопки FTB оставлены одним рядом: квесты,
команда и карта чанков. Зелёная отложенная подсветка IPN больше не используется.

Spice of Life: Valheim Reforged заменяет обычную систему голода. Несколько съеденных
блюд временно увеличивают здоровье и дают регенерацию, пока действуют их таймеры.
Без еды базовое здоровье ниже привычного. Стандартные параметры мода пока сохранены;
совместный баланс питания, Apotheosis, оружия и монстров — следующий этап работы.
Сервер настроен на сложность hard. Снаряжение Avaritia пока доступно
по исходным рецептам: задуманный «грандиозный финал» ещё не связан скриптами с MI.

FTB Ultimine пока использует стандартный лимит 64 блока. Он начисляет обычное
истощение Minecraft, но Valheim держит скрытый уровень еды фиксированным.
Таймеры блюд не уменьшаются от Ultimine автоматически. Специальная цена массовой
добычи и её ограничения по технологическим этапам в этой версии не настроены.

## Клиент

1. В Prism: «Добавить сборку» → «Импорт» → выбрать ArcaneIndustry-0.1.4-Prism.zip.
2. В параметрах экземпляра выбрать Java 21 (64 bit). В Prism можно включить
   автоматический подбор/загрузку Java. Java 17 и 25 для этого прототипа не выбирать.
3. Оставить 10240 МБ памяти. Для остальных компьютеров также начать с 10 ГБ.
4. Первый запуск требует интернета: Prism скачает Minecraft и библиотеки загрузчика.
5. У владельца сервера адрес подключения localhost:25565. Друзья подключаются
   к локальному IPv4 компьютера владельца, порт 25565. Для разных сетей нужна
   отдельно настроенная сеть/VPN или доступ к порту; сборка не меняет настройки сети.

На компьютере автора чата для новой версии создаётся отдельный экземпляр ArcaneIndustry-0.1.4.
Старый ArcaneIndustryPrototype — предыдущий тестовый набор. Тестовый сервер 127.0.0.1:25575 и тестовый мир
не входят в релиз. Рабочий сервер из архива использует порт 25565 и мир world.

## Шейдеры и управление

Complementary Reimagined установлен. Первый запуск — без шейдеров.
F6 — включить/выключить шейдеры; F7 — меню шейдеров; F8 — перезагрузить шейдеры.
Включать шейдеры после загрузки мира. Профиль настроен с приоритетом частоты кадров:
тени 96 блоков, без тяжёлых отражений и цветного освещения.
Цель 90–120 FPS в 1440p не является измеренным результатом этого прототипа.
Загрузка мира и сетевой вход проверены также с этим шейдерпаком: Iris создал
графический конвейер, EMI закончил загрузку рецептов. Визуальная проверка всех
эффектов и замер FPS не выполнены.
Если картинка ломается или происходит вылет, выключить шейдеры и сохранить latest.log.

R и U над предметом — рецепты и применения в EMI; A — закладка EMI.
J — JourneyMap (если переназначено другим модом, проверить «Управление»).
B — Sophisticated Backpacks; Shift+B — рюкзак Occultism.
Средняя кнопка мыши — сортировка там, где её поддерживает контейнер.
R в мире используется боевой магией; перезагрузка шейдеров перенесена на F8.
Есть Controlling для поиска и разрешения остальных конфликтов клавиш.

## Сервер Windows

1. Распаковать ArcaneIndustry-0.1.4-Server-Windows.zip в отдельную папку.
2. Прочитать https://aka.ms/MinecraftEULA; если согласны, изменить eula=false
   на eula=true в server/eula.txt. Архив не принимает соглашение за друзей.
3. Запустить server/Start-Server.cmd. Java 21 уже включена в архив.
4. Дождаться строки Done. Серверу выделено максимум 8 ГБ, клиенту — 10 ГБ.
5. В серверной консоли добавить игроков: whitelist add ИМЯ. Белый список включён.
   Проверка лицензии online-mode=true; режим без проверки в релизе не используется.
6. Для корректного завершения ввести stop и дождаться сохранения мира.

Не запускать два сервера с одним миром. Перед изменением модов делать резервную
копию всего world. Не переносить рабочий мир в папку тестового сервера.
Не обновлять отдельные JAR автоматически: версии подобраны и зафиксированы вместе.

Видимость сервера: view-distance=8, simulation-distance=6, клиент renderDistance=12.
После знакомства с миром можно предварительно сгенерировать территорию через Chunky.
Пример из консоли: chunky radius 2000, затем chunky start. Генерация создаёт нагрузку;
её лучше выполнять отдельно от игры. Финальный seed ещё не выбран.

## Команда и будущие квесты

Создать команду через интерфейс FTB Teams. Установлены FTB Chunks и FTB Quests.
Авторских заданий пока нет. Лимиты загрузки чанков и командные правила ещё стандартные.
Для первого теста не раздавать всем оператора: OP нужен только администратору.

Полный список версий, источников и контрольных сумм — manifest.lock.json.
Границы проверки и известные ограничения — COMPATIBILITY.md.
Архивы предназначены для вашей частной игры; перед публичной публикацией
нужно отдельно проверить условия распространения каждого мода и шейдерпака.
'''
(DIST/'README-RU.md').write_text(readme,'utf-8')

report=(ROOT/'TEST-REPORT.md').read_text('utf-8')+'\n\n## Расширения AE2\n\n'
report+='\n'.join('- '+x['slug']+' — '+x['version'] for x in mods if x['category']=='ae2-addons' or x['slug']=='ae2-jei-integration')+'\n'
(DIST/'COMPATIBILITY.md').write_text(report,'utf-8')
table='| Мод | Версия | Клиент | Сервер | Источник |\n|---|---|---|---|---|\n'
for x in sorted(mods,key=lambda x:x['slug']):
    table+=f"| {x['slug']} | {x['version']} | {'да' if x['client'] else 'нет'} | {'да' if x['server'] else 'нет'} | [страница]({x['source']}) |\n"
(DIST/'MODLIST.md').write_text(table,'utf-8')

def archive(path,entries):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
        for source,name in entries:
            if isinstance(source,bytes):z.writestr(name,source)
            else:z.write(source,name)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
    print(path.name,round(path.stat().st_size/1024**2,1),'MiB',flush=True)

for doc in ['PROGRESSION.md','TEST-REPORT.md']:
    shutil.copy2(ROOT/doc,DIST/doc)

entries=[]
prefix='Arcane Industry Prototype/'
entries.append((portable_cfg.encode('utf-8'),prefix+'instance.cfg'))
entries.append((CLIENT/'mmc-pack.json',prefix+'mmc-pack.json'))
for sub in ['mods','config','shaderpacks','resourcepacks','kubejs','defaultconfigs']:
    directory=GAME/sub
    if directory.exists():
        entries.extend((p,prefix+'minecraft/'+p.relative_to(GAME).as_posix()) for p in directory.rglob('*') if p.is_file())
entries.append((GAME/'options.txt',prefix+'minecraft/options.txt'))
for filename in ['README-RU.md','COMPATIBILITY.md','MODLIST.md','manifest.lock.json','PROGRESSION.md','TEST-REPORT.md']:
    entries.append((DIST/filename,prefix+filename))
archive(DIST/'ArcaneIndustry-0.1.4-Prism.zip',entries)

start='''@echo off
setlocal
cd /d "%~dp0"
"%~dp0runtime\\bin\\java.exe" @user_jvm_args.txt @libraries/net/neoforged/neoforge/21.1.259/win_args.txt nogui
pause
'''
props='''server-port=25565
server-ip=
online-mode=true
enforce-secure-profile=true
white-list=true
enforce-whitelist=true
max-players=4
view-distance=8
simulation-distance=6
level-name=world
level-seed=
gamemode=survival
difficulty=hard
allow-flight=true
enable-command-block=false
enable-rcon=false
motd=Arcane Industry Prototype 0.1.4
spawn-protection=0
max-tick-time=120000
'''
entries=[(start.encode('ascii'),'server/Start-Server.cmd'),
 (b'-Xms2G\n-Xmx8G\n-XX:+UseG1GC\n','server/user_jvm_args.txt'),
 (props.encode('ascii'),'server/server.properties'),
 (b'# Read https://aka.ms/MinecraftEULA before accepting.\neula=false\n','server/eula.txt')]
for sub in ['mods','config','kubejs','defaultconfigs','libraries']:
    directory=SERVER/sub
    if directory.exists():
        for p in directory.rglob('*'):
            if p.is_file() and '21.1.262' not in p.parts and not p.name.endswith('.log'):
                entries.append((p,'server/'+p.relative_to(SERVER).as_posix()))
java=next((ROOT/'runtime/java21').iterdir())
for p in java.rglob('*'):
    if p.is_file():entries.append((p,'server/runtime/'+p.relative_to(java).as_posix()))
for filename in ['README-RU.md','COMPATIBILITY.md','MODLIST.md','manifest.lock.json','PROGRESSION.md','TEST-REPORT.md']:
    entries.append((DIST/filename,'server/'+filename))
archive(DIST/'ArcaneIndustry-0.1.4-Server-Windows.zip',entries)
checksums=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in DIST.glob('*.zip'))
(DIST/'SHA256SUMS.txt').write_text(checksums,'ascii')
print('Client jars',len(list((GAME/'mods').glob('*.jar'))),'Server jars',len(list((SERVER/'mods').glob('*.jar'))),flush=True)
