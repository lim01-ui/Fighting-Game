# Fighter sprite audit

Updated 2026-10-27. All 17 fighters use pixel sprites. The style rework replaces
only the ten fighters outside the requested reference group.

## Reference fighters: unchanged

| Fighter | Original pack |
| --- | --- |
| Iron | Knight |
| Sable | Swordsman |
| Nova | Wizard |
| Jinx | Musketeer |
| Kestrel | Archer |
| Bramble | Enchantress |
| Raguel | Battle_maid |

## Replacement fighters

Rook, Vex, Golem, Sanya, Choom, Saikyo, Renegade, Soldier, Chib and Minamoto
use the [style-v2 atlases](style-v2/README.md). Each has twelve poses, a two-step
walk cycle, light/heavy windup and strike poses, guard, jump, crouch, special and
hurt artwork. Knockdown rotates the hurt pose; ultimate uses the special pose.
These are compact pose atlases rather than full high-frame-count animations.
All ten also have separate four-frame idle breathing strips. The character
select cards and large preview, VS screen and combat idle state cycle those
frames on a shared canvas with a stable foot baseline. Their exact generation
prompts are in [idle-generation.json](style-v2/idle-generation.json).

The built-in image_gen tool generated every replacement sheet separately,
using the original Knight/Swordsman sprites and the simplified new Rook sheet
as style references. [generation.json](style-v2/generation.json) records the
exact final prompts and provenance. Each PNG has a matching JSON manifest
with measured source rectangles and a common 72-pixel native body height.

The loader preserves body scale between poses and aligns light/heavy strike
poses with active attack frames. Crouching uses its own pose with the existing
hurtbox height ratio. Character select and VS use these same sprites so old
portraits cannot conflict with the new combat artwork. Gameplay stats, combat
rules, keys and projectile behavior are unchanged.

## Original artwork and restoration

All original source folders remain in place. An additional independent copy
of the ten replaced fighters is in
[backups/pre-style-rework](backups/pre-style-rework/README.md). Its manifest
records the original roster entries, loader specifications, source commit and
SHA-256 file hashes. Source attribution files, old generated prompts, atlas
manifests and loader snapshots are included.

## Verification

Run `python -m unittest discover -s tests -v` from the repository root. Sprite
checks cover all 17 fighters, both facing directions, all combat states and
attack variants, populated transparent frames, atlas bounds and cell overlap,
walk cycles, attack-phase selection, crouching proportions, reference fighter
mappings and original sprite backup hashes. Visual checks compare the full
roster and individual pose sheets and render the selection, VS and fight UI.
