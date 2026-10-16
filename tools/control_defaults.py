"""Apply reviewed client controls without resetting personal audio or UI preferences."""
import os
from pathlib import Path

root = Path(__file__).resolve().parents[1]
active = Path(os.environ['APPDATA'])/'PrismLauncher/instances/ArcaneIndustry-0.1.4/minecraft/options.txt'
staged = root/'build/prism/Arcane Industry Prototype/minecraft/options.txt'

bindings = {
    # Core magic and equipment actions stay near movement keys.
    'key_key.irons_spellbooks.spellbook_cast': 'key.keyboard.v',
    'key_key.irons_spellbooks.spell_wheel': 'key.keyboard.r',
    'key_key.ars_nouveau.open_book': 'key.keyboard.c',
    'key_key.ars_nouveau.selection_hud': 'key.keyboard.v:ALT',
    'key_key.ars_nouveau.head_curio_hotkey': 'key.keyboard.g:CONTROL',
    'key_key.ars_nouveau.open_documentation': 'key.keyboard.c:CONTROL',
    'key_key.curios.open.desc': 'key.keyboard.g',
    'key_key.sophisticatedbackpacks.open_backpack': 'key.keyboard.b',
    'key_key.sophisticatedbackpacks.inventory_interaction': 'key.keyboard.b:ALT',
    'key_key.occultism.backpack': 'key.keyboard.b:CONTROL',
    'key_key.occultism.ender_bag': 'key.keyboard.b:SHIFT',
    'key_key.appleseed.diet': 'key.keyboard.i:CONTROL',
    # Engineering controls keep their own combinations.
    'key_key.modern_industrialization.toggle_flight': 'key.keyboard.f6',
    'key_key.industrialization_overdrive.terminal_mode_switch': 'key.keyboard.v:CONTROL',
    'key_key.buildinggadgets2.settings_menu': 'key.keyboard.g:ALT',
    'key_key.buildinggadgets2.range': 'key.keyboard.r:CONTROL',
    'key_key.modularrouters.configure': 'key.keyboard.c:ALT',
    'key_key.effortlessbuilding.undo.desc': 'key.keyboard.z',
    'key_key.effortlessbuilding.redo.desc': 'key.keyboard.y',
    'key_key.ars_nouveau.previous_slot': 'key.keyboard.z:ALT',
    'key_key.ars_nouveau.next_slot': 'key.keyboard.x:ALT',
    # Shared keys here previously activated two or more world actions.
    'key_key.cataclysm.ability': 'key.keyboard.f7',
    'key_key.cataclysm.boots_ability': 'key.keyboard.f8',
    'key_key.cataclysm.helmet_ability': 'key.keyboard.h:ALT',
    'key_key.hexerei.broomActivate': 'key.keyboard.g:SHIFT',
    'key_key.goety.activate_curio': 'key.keyboard.h:CONTROL',
    'key_key.goety.ceaseFire': 'key.keyboard.h:SHIFT',
    'key_key.trashslot.toggle': 'key.keyboard.delete:CONTROL',
    'key_iris.keybind.reload': 'key.keyboard.f10',
    'key_iris.keybind.toggleShaders': 'key.keyboard.k',
    'key_iris.keybind.shaderPackSelection': 'key.keyboard.o',
    'key_key.evilcraft.fart': 'key.keyboard.unknown',
    # Equipment Compare provides the active Shift comparison overlay.
    'key_key.apotheosis.compare_equipment': 'key.keyboard.unknown',
    # Equipment and world actions must not fire when using common keys.
    'key_key.techreborn.quantumSuitSprint': 'key.keyboard.r:ALT',
    'key_key.techreborn.suitNightVision': 'key.keyboard.n:ALT',
    'key_key.avaritia.neutron_ring': 'key.keyboard.n:SHIFT',
    'key_key.avaritia.filter': 'key.keyboard.f12:SHIFT',
    'key_key.avaritia.config': 'key.keyboard.o:SHIFT',
    'key_key.goety.bag': 'key.keyboard.f11:SHIFT',
    'key_key.goety.focusCircle': 'key.keyboard.x:SHIFT',
    'key_key.goety.lich.magnet': 'key.keyboard.r:SHIFT',
    'key_key.goety.mount.roar': 'key.keyboard.f9:SHIFT',
    'key_key.goety.lich.lichForm': 'key.keyboard.l:ALT',
    'key_key.goety.lich.laugh': 'key.keyboard.l:SHIFT',
    'key_key.goety.lich.nightVision': 'key.keyboard.n:CONTROL',
    'key_key.goety.wand': 'key.keyboard.f11:CONTROL',
    'key_key.goety.witch.robe': 'key.keyboard.v:SHIFT',
    'key_key.goety.witch.extractPotions': 'key.keyboard.p:ALT',
    'key_key.goety.witch.brewBag': 'key.keyboard.f11:ALT',
    'key_key.goety.witch.brewCircle': 'key.keyboard.f12:CONTROL',
    'key_key.goety.mount.freeRoam': 'key.keyboard.f8:SHIFT',
    'key_key.apotheosis.toggle_radial_mining': 'key.keyboard.o:ALT',
    'key_key.buildinggadgets2.undo': 'key.keyboard.u:ALT',
    'key_key.buildinggadgets2.anchor': 'key.keyboard.f12:ALT',
    'key_key.modularrouters.moduleInfo': 'key.keyboard.i:ALT',
    'key_key.modern_industrialization.toggle_3x3': 'key.keyboard.f6:SHIFT',
    'key_key.cataclysm.chestplate_ability': 'key.keyboard.f7:SHIFT',
    'key_key.twilightforest.swap_hotbar': 'key.keyboard.f8:CONTROL',
    'key_key.ars_elemental.open_pouch': 'key.keyboard.j:ALT',
    'key_key.advancedmemorycard.switch': 'key.keyboard.f9:CONTROL',
    'key_key.sophisticatedbackpacks.toggle_upgrade_1': 'key.keyboard.f1:ALT',
    'key_key.sophisticatedbackpacks.toggle_upgrade_2': 'key.keyboard.f2:ALT',
    'key_key.evilcraft.exaltedCrafting': 'key.keyboard.c:SHIFT',
    'key_key.journeymap.create_waypoint': 'key.keyboard.w:ALT',
    'key_key.journeymap.toggle_entity_names': 'key.keyboard.e:ALT',
    'key_key.journeymap.map_toggle_alt': 'key.keyboard.m:ALT',
    'key_key.presencefootsteps.settings': 'key.keyboard.f10:ALT',
    'key_key.craftingtweaks.compress_stack': 'key.keyboard.k:ALT',
    'key_key.guideme.guide': 'key.keyboard.f10:CONTROL',
    'key_key.moreoverlays.lightoverlay.desc': 'key.keyboard.f7:ALT',
    'key_key.moreoverlays.chunkbounds.desc': 'key.keyboard.f9:ALT',
    'key_key.yet_another_industrialization.toggle_industrialists_goggles': 'key.keyboard.keypad.3:ALT',
    'key_supplementaries.keybind.quiver': 'key.keyboard.q:ALT',
    'key_crafting_on_a_stick.key.open_curios': 'key.keyboard.u:SHIFT',
    'key_key.kubejs.kubedex': 'key.keyboard.f4:ALT',
    'key_key.hexerei.glasses_zoom': 'key.keyboard.z:SHIFT',
    'key_key.twilightforest.zoom': 'key.keyboard.f10:SHIFT',
    'key_key.twilightforest.item_display_map_cycle': 'key.keyboard.m:SHIFT',
    'key_key.findme.search': 'key.keyboard.y:ALT',
}

settings = {'maxFps':'120', 'renderDistance':'12', 'simulationDistance':'6',
            'entityDistanceScaling':'0.75', 'enableVsync':'false'}

def apply(path, baseline):
    lines = path.read_text('utf-8').splitlines() if path.exists() else []
    positions = {line.split(':',1)[0]:i for i,line in enumerate(lines) if ':' in line}
    if path == staged:
        for key, value in baseline.items():
            if key.startswith('key_') and key not in positions:
                positions[key] = len(lines)
                lines.append(key+':'+value)
    for key,value in {**settings, **bindings}.items():
        if key in positions:
            lines[positions[key]] = key+':'+value
        elif key.startswith('key_') and key in baseline:
            lines.append(key+':'+value)
        elif not key.startswith('key_'):
            lines.append(key+':'+value)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(lines)+'\n','utf-8')
    return len(lines)

baseline=dict(line.split(':',1) for line in active.read_text('utf-8').splitlines() if ':' in line)
print('active options',apply(active,baseline))
print('staged options',apply(staged,baseline))
