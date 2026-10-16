"""One late EU-powered drill for MI's existing electric quarry."""


def integrate(c):
    mi = c['M']
    tr = 'techreborn:'
    drill = c['part']('quantum_quarry_drill', 'Квантовый карьерный бур · P6')
    c['machine'](
        'quantum_quarry_drill', drill,
        [(mi + 'titanium_drill', 4),
         (tr + 'industrial_drill', 1),
         (mi + 'iridium_plate', 8),
         (tr + 'superconductor', 4),
         ('kubejs:convergence_core', 1),
         (tr + 'uu_matter', 4)],
        1, 512, 1200,
    )
    c['add']('quantum_quarry_resources', {
        'type': mi + 'quarry',
        'eu': 512,
        'duration': 600,
        'item_inputs': {'item': drill, 'amount': 1, 'probability': 0.001},
        'item_outputs': [
            {'item': mi + 'uranium_ore', 'amount': 1, 'probability': 0.3},
            {'item': mi + 'iridium_ore', 'amount': 1, 'probability': 0.08},
            {'item': mi + 'titanium_ore', 'amount': 1, 'probability': 0.25},
            {'item': mi + 'tungsten_ore', 'amount': 1, 'probability': 0.25},
            {'item': mi + 'platinum_ore', 'amount': 1, 'probability': 0.15},
            {'item': mi + 'monazite_ore', 'amount': 1, 'probability': 0.2},
            {'item': 'minecraft:diamond_ore', 'amount': 1, 'probability': 0.2},
        ],
    })
