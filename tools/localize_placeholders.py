"""Review format-sensitive labels omitted by the bulk localization pass."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / 'overrides/client/kubejs/assets'
rows = {
'simplyswords': {
'caelestissworditem.tooltip5':'Разлом действует %1$d с и расширяется до радиуса %2$d блоков.',
'caelestissworditem.tooltip8':'За последние %1$d с разлом схлопывается и возвращает призванных существ в их измерение. У каждого разлома есть шанс %2$d%% выпустить Несвязанное существо, которое начнёт охоту на вас.',
'common.showtooltip':'ꭁ     ꭈ','common.showtooltip.config':'ꭉ','common.showtooltip.info':'ꭁ','common.showtooltip.search':'ꭈ',
'dawnquiversworditem.tooltip2':'Малый лук периодически стреляет в самого дальнего видимого врага и с шансом %d%% даёт Зарю хора.',
'dawnquiversworditem.tooltip3':'Оружие хранит до %d зарядов хора.',
'dawnquiversworditem.tooltip5':'Залп рассвета — потратить 1 заряд хора на вторую стрелу. Перезарядка: %s с.',
'dawnquiversworditem.tooltip6':'Солнечное копьё — потратить 2 заряда хора, чтобы пронзить до четырёх врагов. Перезарядка: %s с.',
'dawnquiversworditem.tooltip7':'Серафический хор — потратить 3 заряда хора и призвать три сходящихся лука. Перезарядка: %s с.',
'devourerclaymoreitem.tooltip3':'Масса распространяет Мрак, поражает до %d ближайших врагов, затягивает их в ядро и поглощает.',
'devourerclaymoreitem.tooltip4':'Поглощая врагов, масса растёт; через %.1f с она схлопывается и освобождает пленников.',
'dreadtidesworditem.tooltip2':'Постепенно накапливает Покров Пустоты: каждый заряд ускоряет атаки и снижает получаемый урон на 10%.',
'dreadwhispersworditem.tooltip2':'Цели, поражённые Разрывом тени, получают Порченую рану на %s с.',
'dreadwhispersworditem.tooltip5':'Каждый враг на пути получает удар оружием и Порченую рану, а вы восстанавливаете %s%% отнятого здоровья.',
'emberlashsworditem.tooltip3':'Удары по тлеющим врагам наносят ещё %d урона за каждый заряд эффекта.',
'emberlashsworditem.tooltip6':'Уклоняетесь назад и прижигаете раны, восстанавливая %d%% максимального здоровья.',
'flamewindsworditem.tooltip11':'Распространяется до %d раз.',
'hiveheartsworditem.tooltip5':'Эффект срабатывает не чаще одного раза за %d с.',
'hiveheartsworditem.tooltip8':'⌛ %s',
'magibladesworditem.tooltip5':'После зарядки призывает голову Хранителя: она вращается вокруг вас %s с и периодически выпускает звуковые волны в ближайших врагов. Повторное применение обновляет время действия.',
'magispearsworditem.tooltip2':'',
'ribboncleaversworditem.tooltip2':'С Тесаком лент вы движетесь на 5% медленнее, но получаете на 15% меньше урона.',
'ribboncleaversworditem.tooltip5':'Рывок вперёд: несколько следующих ударов не прервут вас, сопротивление отбрасыванию повышается, а следующая атака по одной цели наносит на 95% больше урона.',
'starsedgesworditem.tooltip2':'Днём ваши атаки наносят дополнительно %s урона.',
'stormscalesworditem.tooltip4':'Каждая ваша атака в ближнем бою повышает урон и радиус импульса на 1%, вплоть до 80%.',
'watchersworditem.claymore.tooltip3':'При максимальном Ужасе враги с запасом здоровья ниже %d%% мгновенно погибают.',
'waxweaversworditem.tooltip8':'Эффект срабатывает не чаще одного раза за %d с. Только в основной руке.',
'wickpiercersworditem.tooltip6':'ударить дважды в течение %d с.',
'wraithmawsworditem.tooltip3':'Собирает до %s абордажных сабель на %s с.',
},
'evilcraft': {
'biome_extract.info.content':'Содержимое: %s',
'blood_container.info.autoSupply':'Автоподача: %s',
'blood_extractor.info.auto_supply':'Автоподача: %s',
'bound_blood_drop.info.auto_supply':'Автоподача: %s',
'bound_blood_drop.info.current_owner':'Текущий владелец: %s',
'creative_blood_drop.info.auto_supply':'Автоподача: %s',
'kineticator.info.area':'Область притяжения: %s',
'kineticator.info.attraction':'Притяжение: %s',
'kineticator_repelling.info.area':'Область отталкивания: %s',
'kineticator_repelling.info.attraction':'Отталкивание: %s',
'primed_pendant.potion':'§7Эффект: %s (%s)',
'resurgence_egg.info.content':'Содержимое: %s',
'vengeance_ring.info.status':'Состояние: %s',
},
'crafting_on_a_stick': {name:'%1$s%2$s%3$s' for name in ('anvil','cartography_table','chipped_anvil','crafting_table','damaged_anvil','grindstone','loom','smithing_table','stonecutter')},
'forbidden_arcanus': {
'hephaestus_forge.slot_unlocked_at':'Открывается на тире %s',
'hephaestus_forge.tier':'Тир %s',
'hephaestus_forge.tier.at_least':'Требуется как минимум тир %s',
'hephaestus_forge.tier.match_exact':'Требуется точно тир %s',
'stored_entity':'Существо: %s',
'stored_entity.with_name':'Существо: %s (%s)',
},
'ftbquests': {
'barrier.invis_when_open':'Невидим после открытия: %s',
'barrier.object.quest_barrier':'Выбранный квест: %s',
'barrier.object.stage_barrier':'Выбранный этап: %s',
'barrier.rightclick':'Нажмите правой кнопкой, чтобы настроить\nНажмите средней кнопкой, чтобы взять копию вместе с настройками',
'barrier.skin':'Внешний вид: %s',
'lootcrate.missing':'ОШИБКА: неизвестный ящик с добычей «%s»!',
},
'mob_grinding_utils': {
'entity_spawner.jei.info':'Создаёт мобов в области 3×3×1.\nРасходует желе опыта.\nМожно улучшать.',
'tank_sink':'Сингулярный резервуар для слива опыта',
'solid_xp_mould_baby':'Маленькое желе из формы твёрдого опыта',
},
'sophisticatedcore': {
'ender_linker.tooltip.linker_target':'Связан с: %s',
'storage.tooltip.linked_storage_endpoint':'Конечная точка связанного хранилища: %s',
'storage.tooltip.linked_storage_group':'Группа связанных хранилищ: %s',
},
'twilightforest': {'maze_map.y_level':'Уровень Y: %s'},
}
for namespace, translations in rows.items():
    path = root / namespace / 'lang/ru_ru.json'
    content = json.loads(path.read_text('utf-8')) if path.exists() else {}
    for suffix, value in translations.items():
        prefix = 'block' if namespace == 'forbidden_arcanus' and suffix.startswith('hephaestus_forge.') else 'block' if namespace == 'mob_grinding_utils' and suffix in ('entity_spawner.jei.info','tank_sink') else 'item'
        content[f'{prefix}.{namespace}.{suffix}'] = value
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print('format-sensitive strings', sum(map(len, rows.values())))
