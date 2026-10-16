"""Post-Infinity creative utilities; none are prerequisites of the main progression."""


def integrate(c):
    ing, add, remove = c['ing'], c['add'], c['remove']
    shared = {
        'I': 'avaritia:infinity_ingot',
        'C': 'avaritia:infinity_catalyst',
        'N': 'avaritia:neutron_ingot',
        'T': 'kubejs:armor_core_t8',
        'S': 'kubejs:infinity_stabilizer',
        'M': 'kubejs:engineering_matrix',
        'L': 'kubejs:seal_life',
        'D': 'kubejs:seal_mind',
        'E': 'kubejs:seal_elements',
        'Q': 'techreborn:uu_matter',
    }
    # The last symbol is a useful, thematic predecessor. All recipes require
    # the existing cross-mod Infinity chain, regardless of the target family.
    outputs = {
        'ae2:creative_storage_cell': 'ae2:item_storage_cell_64k',
        'ae2:creative_energy_cell': 'ae2:dense_energy_cell',
        'ars_nouveau:creative_spell_book': 'ars_nouveau:archmage_spell_book',
        'ars_nouveau:creative_source_jar': 'ars_nouveau:source_jar',
        'evilcraft:creative_blood_drop': 'evilcraft:blood_orb_filled',
        'hexerei:creative_waxing_kit': 'hexerei:mixing_cauldron',
        'modern_industrialization:creative_barrel': 'modern_industrialization:iridium_plate',
        'modern_industrialization:creative_storage_unit': 'modern_industrialization:iridium_plate',
        'modern_industrialization:creative_tank': 'modern_industrialization:iridium_plate',
        'modularrouters:creative_module': 'modularrouters:modular_router',
        'storagedrawers:creative_storage_upgrade': 'minecraft:nether_star',
        'storagedrawers:creative_vending_upgrade': 'minecraft:nether_star',
        'techreborn:creative_solar_panel': 'techreborn:lapotronic_orb',
        'techreborn:creative_storage_unit': 'techreborn:lapotronic_orb',
        'techreborn:creative_tank_unit': 'techreborn:lapotronic_orb',
    }
    pattern = [
        'IIIINIIII',
        'I  L D  I',
        'I C   C I',
        'I   M   I',
        'N E T E N',
        'I   S   I',
        'I C   C I',
        'I  Q P  I',
        'IIIINIIII',
    ]
    for output, predecessor in outputs.items():
        key = dict(shared, P=predecessor)
        remove.add(output)
        add('creative/' + output.replace(':', '_'), {
            'type': 'avaritia:shaped_table', 'tier': 4,
            'pattern': pattern,
            'key': {symbol: ing(item) for symbol, item in key.items()},
            'result': {'id': output, 'count': 1},
        })
