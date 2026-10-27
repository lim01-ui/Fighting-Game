# Chibi fighter replacement atlases

Rook, Vex, Golem, Sanya, Choom, Saikyo, Renegade, Soldier, Chib and Minamoto
use these new sheets. Iron, Sable, Nova, Jinx, Kestrel, Bramble and Raguel
retain their original artwork and loader specifications.

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

The old source folders remain in place. A separate verified copy, including
the original manifests and loader snapshots, is in
`../backups/pre-style-rework/`; see its README and manifest for restoration.
