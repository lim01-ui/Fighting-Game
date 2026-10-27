# Chibi fighter replacement atlases

Rook, Vex, Golem, Sanya, Choom, Saikyo, Renegade, Soldier, Chib and Minamoto
use these new sheets. Iron, Sable, Nova, Jinx, Kestrel and Bramble
retain their original artwork and loader specifications.

Raguel now uses `raguel.png` and `raguel.json` to match the roster's chibi
proportions, 72-pixel reference height, and action-pose rendering. The original
Battle_maid strips remain available. Generation details and the exact prompt
are recorded in `raguel-generation.json`.

The built-in `image_gen` tool generated the transparent PNGs. Exact prompts,
reference paths and generation provenance are recorded in `generation.json`.
The style targets large heads, compact bodies, simple two-tone shading and
thin dark pixel outlines. Rook is the approved style anchor for this set.

Each sheet contains twelve distinct poses in four columns and three rows:

| Row | Poses, left to right |
| --- | --- |
| 1 | Idle, left walk step, right walk step, guard |
| 2 | Jump, crouch, light windup, light strike |
| 3 | Heavy windup, heavy strike, special, hurt |

The JSON manifests record actual source rectangles, selected at clear alpha
gutters rather than assuming the requested grid dimensions. `body_height`
measures the visible idle body at alpha >= 16; `pixel_height` sets a shared
72-pixel reference body height. The loader samples with nearest-neighbor
scaling before fitting the fighter to its unchanged gameplay dimensions.

Walking alternates two frames. Light/heavy attacks select their windup during
startup and strike during active/recovery frames. Ultimate uses the special
pose, and knockdown uses the rotated hurt pose. Crouching uses its own pose
with a height matched to the existing hurtbox ratio. These are compact pose
atlases, not full high-frame-count animation packs.

Each fighter also has a separate `<fighter>-idle.png` four-frame breathing
strip, generated from its matching action atlas with the built-in `image_gen`
tool. Exact prompts are in `idle-generation.json`. The manifest's
`idle_animation` records this strip's frame bounds and reference body height.
The loader aligns each frame at its feet on one shared canvas, then cycles at
180 ms per frame. Character select (both cards and the large preview), VS and
in-game idle states use this loop. Constant canvas dimensions keep preview
fitting from cancelling the breathing motion or changing the character scale.
The original twelve-pose sheets and earlier backups remain intact.

The old source folders remain in place. A separate verified copy, including
the original manifests and loader snapshots, is in
`../backups/pre-style-rework/`; see its README and manifest for restoration.
