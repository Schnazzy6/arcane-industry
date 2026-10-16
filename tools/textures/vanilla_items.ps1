# Vanilla-style 16x16 item textures for every kubejs:* item (CRAFTING-TODO.md, point 3).
# Rules: no anti-aliasing, outline = darkest shade of the material (not black), 4 tones lit
# from the top-left, accents in 3 tones, silhouettes modelled on vanilla items.
# Usage: powershell -File tools/textures/vanilla_items.ps1 -KubeJs overrides/common/kubejs [-Preview sheet.png]
param([string]$KubeJs, [string]$Preview = '')
Add-Type -AssemblyName System.Drawing
$ErrorActionPreference = 'Stop'

function Hex([string]$h) { [System.Drawing.ColorTranslator]::FromHtml('#' + $h) }
function Mix($c, $to, [double]$t) {
  [System.Drawing.Color]::FromArgb(255, [int]($c.R + ($to.R - $c.R) * $t), [int]($c.G + ($to.G - $c.G) * $t), [int]($c.B + ($to.B - $c.B) * $t))
}
function Mul($c, [double]$k) { [System.Drawing.Color]::FromArgb(255, [Math]::Min(255, [int]($c.R * $k)), [Math]::Min(255, [int]($c.G * $k)), [Math]::Min(255, [int]($c.B * $k))) }
$WHITE = [System.Drawing.Color]::White
# Material ramp: o outline, 1 shadow, 2 mid, 3 base, 4 highlight. Accent: b dark, a base, c light.
function Ramp([string]$base, [string]$accent) {
  $b = Hex $base; $a = Hex $accent
  @{ o = (Mul $b 0.32); '1' = (Mul $b 0.58); '2' = (Mul $b 0.8); '3' = $b; '4' = (Mix $b $WHITE 0.38)
     b = (Mul $a 0.62); a = $a; c = (Mix $a $WHITE 0.45); w = (Mix $b $WHITE 0.7) }
}

$M = @{}
$M.plate = @(
'................','................','..oooooooooooo..','..o44444333332o.','..o43333333322o.','..o43333333222o.',
'..o43333aa3222o.','..o4333acca222o.','..o3333acca221o.','..o333333aa2211o','..o33333322211o.','..o33332222111o.',
'..o22222221111o.','..oooooooooooo..','................','................')
$M.gem = @(
'................','......oooo......','.....o4433o.....','....o443332o....','...o44333322o...','..o4433332222o..',
'..o3333322221o..','...o33322211o...','....o332211o....','.....o3211o.....','......o11o......','.....obbbbo.....',
'....obaaaacbo...','....obbbbbbbo...','.....ooooooo....','................')
$M.orb = @(
'................','.....oooooo.....','....o443333o....','...o44433332o...','..o4443333322o..','..o443aaaa222o..',
'..o43acccca22o..','..o33acccca21o..','..o333aaaa221o..','..o3333222211o..','...o32222111o...','....o222111o....',
'.....oooooo.....','................','................','................')
$M.medal = @(
'................','.....oooooo.....','....o444333o....','...o4bbbbbb2o...','..o4baaaaaab2o..','..o4baacaaab2o..',
'..o3bacccaab1o..','..o3baacccab1o..','..o3baaacaab1o..','..o3baaaaaab1o..','...o2bbbbbb1o...','....o222111o....',
'.....oooooo.....','................','................','................')
$M.star = @(
'................','.....oooooo.....','....o444333o....','...o4bbbbbb2o...','..o4baacaaab2o..','..o4baacaaab2o..',
'..o3bccccccb1o..','..o3baacaaab1o..','..o3baacaaab1o..','..o3baaaaaab1o..','...o2bbbbbb1o...','....o222111o....',
'.....oooooo.....','................','................','................')
$M.frame = @(
'................','..oooooooooooo..','..o44443333322o.','..o4oooooooo21o.','..o4o......o21o.','..o3o..oo..o21o.',
'..o3o.obao.o11o.','..o3o.obco.o11o.','..o3o..oo..o11o.','..o3o......o11o.','..o3oooooooo11o.','..o32222221111o.',
'..oooooooooooo..','................','................','................')
$M.mount = @(
'................','................','...oooooooooo...','...o44433332o...','...o4oooooo2o...','...o3o....o1o...',
'...o3o....o1o...','...o3o....o1o...','...o3oooooo1o...','...o32222211o...','...oooooooooo...','....o3o..o1o....',
'....o3o..o1o....','...oo2oo.o1oo...','...oooo..oooo...','................')
$M.lens = @(
'................','.....oooooo.....','....o433333o....','...o4aaaaaa2o...','..o4acccaaaa2o..','..o3acaaaaaa2o..',
'..o3aaaaaaaa1o..','..o3aaaaaaaa1o..','..o3aaaaaaba1o..','..o3aaaaabba1o..','...o2aaaaaa1o...','....o222111o....',
'.....oooooo.....','................','................','................')
$M.flask = @(
'................','......oooo......','......o44o......','......o32o......','.......oo.......','......o42o......',
'.....o4cc2o.....','....o4aaaa2o....','...o4acaaaa1o...','...o3aaaaaa1o...','...o3aaaaab1o...','...o3aaaabb1o...',
'....o2bbbb1o....','.....oooooo.....','................','................')
$M.scroll = @(
'................','..oooooooooooo..','.o443333333322o.','.o4oooooooooo1o.','..o4333333332o..','..o3bbbb33322o..',
'..o333333b322o..','..o3bbbbb3322o..','..o33333332221o.','..o3bbb33aa22o..','..o3333aacca1o..','.o44333aacaa1o..',
'.o3oooooooooo1o.','.o22222222211o..','..oooooooooooo..','................')
$M.seed = @(
'................','.......oo.......','......o4bo......','.....o44a2o.....','....o4433a2o....','...o44333322o...',
'...o4333c3322o..','...o333cac221o..','...o3333c32211o.','...o33332222o...','....o3322211o...','.....o22211o....',
'......o111o.....','.......ooo......','................','................')
$M.capsule = @(
'......oooo......','.....o4433o.....','.....obbbbo.....','....o4bccb2o....','....o4aaaa2o....','....o4acaa2o....',
'....o3acaa1o....','....o3aaaa1o....','....o3aaaa1o....','....o3aaab1o....','....o3abbb1o....','....o2bbbb1o....',
'.....obbbbo.....','.....o3211o.....','......oooo......','................')
$M.blob = @(
'................','................','................','.....oooooo.....','....o444333o....','...o44c33332o...',
'..o44cc333322o..','..o433333332o...','..o33333332221o.','..o33333322211o.','...o322222111o..','....oooooooooo..',
'................','................','................','................')
$M.bundle = @(
'................','......o..o......','.....obbbbo.....','......obbo......','.....oo44oo.....','....o4433332o...',
'...o443333322o..','..o4433aa33221o.','..o433acca32211o','..o333aaaa32211o','..o3333aa322211o','..o33333222211o.',
'...o32222221o...','....oooooooo....','................','................')
$M.chip = @(
'................','...1.1.1.1.1....','..oooooooooooo..','.1o4444333332o1.','..o4aaaaaaaa2o..','.1o3abbbbbba2o1.',
'..o3abccccba2o..','.1o3abccccba2o1.','..o3abbbbbba1o..','.1o3aaaaaaaa1o1.','..o32222222211o.','..oooooooooooo..',
'...1.1.1.1.1....','................','................','................')
$M.core = @(
'................','..ooo......ooo..','..o4oo....oo2o..','..o44oooooo22o..','..o4433aa3221o..','..o433acca221o..',
'...o33acca21o...','...o333aa221o...','...o33333221o...','...o33332221o...','...o33322211o...','...o32222111o...',
'....oooooooo....','................','................','................')
$M.drill = @(
'................','...........oo...','..........o44o..','.........o4432o.','........o44322o.','.......o44c22o..',
'......o44322o...','.....o4c322o....','....obb322o.....','...obaabbo......','..obacabo.......','..obaaabo.......',
'...obbbo........','....ooo.........','................','................')

# Procedural shapes
function Mesh($r) {
  $bmp = New-Object System.Drawing.Bitmap 16, 16
  for ($y = 2; $y -le 13; $y++) { for ($x = 2; $x -le 13; $x++) {
    $edge = ($x -eq 2 -or $y -eq 2 -or $x -eq 13 -or $y -eq 13)
    $wire = (($x + $y) % 3 -eq 0) -or (($x - $y + 30) % 3 -eq 0)
    if ($edge) { $bmp.SetPixel($x, $y, $r.o) }
    elseif ($wire) { $t = $(if ($x + $y -lt 13) { '4' } elseif ($x + $y -lt 19) { '3' } else { '2' }); $bmp.SetPixel($x, $y, $r[$t]) } } }
  $bmp
}
function Lattice($r) {
  $bmp = New-Object System.Drawing.Bitmap 16, 16
  for ($y = 0; $y -lt 16; $y++) { for ($x = 0; $x -lt 16; $x++) {
    $d = [Math]::Abs($x - 7.5) + [Math]::Abs($y - 7.5)
    if ($d -gt 7.5) { continue }
    if ($d -gt 6.5) { $bmp.SetPixel($x, $y, $r.o); continue }
    $line = (($x + $y) % 3 -eq 0) -or (($x - $y + 30) % 3 -eq 0)
    if ($line) { $bmp.SetPixel($x, $y, $(if ($y -lt 8) { $r['4'] } else { $r['3'] })) }
    elseif ((($x * 7 + $y * 3) % 11) -eq 0) { $bmp.SetPixel($x, $y, $r.c) } } }
  $bmp
}
function FromMask([string[]]$mask, $r) {
  $bmp = New-Object System.Drawing.Bitmap 16, 16
  for ($y = 0; $y -lt 16; $y++) {
    $row = $mask[$y].PadRight(16, '.').Substring(0, 16)
    for ($x = 0; $x -lt 16; $x++) { $ch = [string]$row[$x]; if ($ch -ne '.' -and $r.ContainsKey($ch)) { $bmp.SetPixel($x, $y, $r[$ch]) } } }
  $bmp
}
# Small tier gem in the bottom-right corner (modules): 2x2 in the tier colour with outline.
function TierPip($bmp, [string]$hex) {
  $c = Hex $hex; $o = Mul $c 0.35
  foreach ($p in @(@(12, 12), @(13, 12), @(12, 13), @(13, 13))) { $bmp.SetPixel($p[0], $p[1], $c) }
  $bmp.SetPixel(12, 12, (Mix $c $WHITE 0.5))
  foreach ($p in @(@(11, 12), @(11, 13), @(14, 12), @(14, 13), @(12, 11), @(13, 11), @(12, 14), @(13, 14))) { $bmp.SetPixel($p[0], $p[1], $o) }
}

# id, shape, base, accent, folder
$items = @(
  @('sky_plate', 'plate', 'A9C8E8', 'FFF2A8', 'rework'), @('iesnium_plate', 'plate', '4FB3A8', 'C8FFF6', 'rework'),
  @('deorum_plate', 'plate', 'D9A13A', 'FFF0C0', 'rework'), @('enchanted_titanium_plate', 'plate', 'B8BCC8', 'B070FF', 'rework'),
  @('mithril_mesh', 'mesh', '9FE0FF', '9FE0FF', 'rework'), @('hallowed_circuit', 'chip', '2E6B3A', 'F2D27A', 'rework'),
  @('resonance_core', 'orb', '6A3FC0', 'D7B8FF', 'rework'), @('arcane_lens', 'lens', 'B08A3A', '7FD8FF', 'rework'),
  @('infinite_storage_matrix', 'chip', '2A2A36', 'FF6EC7', 'rework'), @('infinite_energy_matrix', 'orb', '2A2A36', 'FFD84A', 'rework'),
  @('infinite_fluid_matrix', 'orb', '2A2A36', '3BB0FF', 'rework'), @('infinite_arcane_matrix', 'lattice', 'B07CFF', 'FF6EC7', 'rework'),
  @('ritual_mount', 'mount', 'C58A4B', 'C58A4B', 'progression'), @('arcane_resin', 'blob', '8A5FD0', 'E0C8FF', 'progression'),
  @('electrical_focus', 'gem', 'FFD84A', 'C87533', 'progression'), @('alchemical_catalyst', 'flask', 'D8E6EE', '66D17A', 'progression'),
  @('industrial_focus', 'gem', '4FC8E8', '9AA4AE', 'progression'), @('soul_stabilizer', 'capsule', '8E96A0', '5FE0D8', 'progression'),
  @('ritual_frame', 'frame', 'B8BCC8', '9A6BFF', 'progression'), @('elemental_insulator', 'capsule', '6A6A72', 'E07A3A', 'progression'),
  @('seal_life', 'medal', 'D9B44A', '5FBF4A', 'progression'), @('seal_mind', 'medal', 'C0C8D8', '3A6BD0', 'progression'),
  @('seal_soul', 'medal', '6A6478', '9A4AD0', 'progression'), @('seal_elements', 'medal', 'C58A4B', 'E05A3A', 'progression'),
  @('convergence_core', 'orb', 'E0A83A', 'FFF6D0', 'progression'), @('infinity_stabilizer', 'capsule', '3A3A48', 'FF6EC7', 'progression'),
  @('armor_core_t1', 'core', 'C58A4B', '8FD16A', 'progression'), @('armor_core_t2', 'core', 'C8C8C8', '5CD6E0', 'progression'),
  @('armor_core_t3', 'core', '8FA0B0', 'E05A3A', 'progression'), @('armor_core_t4', 'core', 'B0B8D0', 'B07CFF', 'progression'),
  @('armor_core_t5', 'core', 'D9B44A', 'FF5A5A', 'progression'), @('armor_core_t6', 'core', '9A6BD0', 'F2C14E', 'progression'),
  @('armor_core_t7', 'core', '3BC8B0', 'FFFFFF', 'progression'), @('armor_core_t8', 'core', 'E8E8F0', 'FF6EC7', 'progression'),
  @('provision_bundle', 'bundle', 'B08A5A', '5FBF4A', 'progression'), @('expedition_emblem', 'star', 'C58A4B', 'F2E2B8', 'progression'),
  @('relic_research', 'scroll', 'E8D8A8', '6A3A9A', 'progression'), @('enchantment_lattice', 'lattice', 'B07CFF', 'E0C8FF', 'progression'),
  @('engineering_matrix', 'chip', '3A3F6A', '5FD0FF', 'progression'), @('boss_seal', 'medal', '8A2A2A', 'F2C14E', 'progression'),
  @('reborn_interface', 'chip', '4A5560', '3BE8C5', 'progression'), @('quantum_quarry_drill', 'drill', '3BC8B0', '6A7480', 'progression')
)
$tierColors = @('', '9A9A9A', 'C58A4B', 'E8E8E8', '8FD16A', '5CD6E0', 'B07CFF', 'F2C14E', 'FF9A3C', 'FF5A5A', '3BE8C5', 'FF6EC7')
$moduleStyle = @{ tech_module = @('chip', '6A7280', '3BE8C5'); dark_essence = @('flask', '8A7AA0', '7A2AC0');
                  spirit_contract = @('scroll', 'E8D8A8', 'B03030'); aura_seed = @('seed', '3E9A4E', 'F2C14E') }
foreach ($k in $moduleStyle.Keys) { $min = $(if ($k -eq 'dark_essence') { 7 } else { 4 }); for ($t = $min; $t -le 11; $t++) { $items += , @("$k`_t$t", $moduleStyle[$k][0], $moduleStyle[$k][1], $moduleStyle[$k][2], 'modules', $t) } }

$written = @()
foreach ($it in $items) {
  $r = Ramp $it[2] $it[3]
  $bmp = switch ($it[1]) { 'mesh' { Mesh $r } 'lattice' { Lattice $r } default { FromMask $M[$it[1]] $r } }
  if ($it.Count -gt 5) { TierPip $bmp $tierColors[$it[5]] }
  $dir = Join-Path $KubeJs ('assets/kubejs/textures/item/' + $it[4]); New-Item -ItemType Directory -Force $dir | Out-Null
  $file = Join-Path $dir ($it[0] + '.png'); $bmp.Save($file, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose(); $written += $file
}
"wrote $($written.Count) textures"
if ($Preview) {
  $cols = 10; $cell = 64; $rows = [Math]::Ceiling($written.Count / $cols)
  $sheet = New-Object System.Drawing.Bitmap ($cols * $cell), ($rows * $cell); $g = [System.Drawing.Graphics]::FromImage($sheet)
  $g.InterpolationMode = 'NearestNeighbor'; $g.PixelOffsetMode = 'Half'; $g.Clear([System.Drawing.Color]::FromArgb(255, 139, 139, 139))
  for ($i = 0; $i -lt $written.Count; $i++) { $im = [System.Drawing.Image]::FromFile($written[$i]); $g.DrawImage($im, ($i % $cols) * $cell, [Math]::Floor($i / $cols) * $cell, $cell, $cell); $im.Dispose() }
  $sheet.Save($Preview)
}
