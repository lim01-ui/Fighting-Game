# Shared chibi fighter artwork

All seventeen fighters use the same transparent-sprite loader and a 72-pixel
reference body height. Gameplay names, statistics, collision dimensions, moves,
and damage are preserved. Raguel is the proportion/style reference for the
latest roster update.

## Latest ten-character update

- Sable, Nova, Jinx, Kestrel, Bramble, and Iron use `<name>-chibi.png`.
- Sanya uses `sanya-slime.png`: a blue jelly creature.
- Choom uses `choom-robot.png`: a compact silver/cyan robot.
- Renegade uses `renegade-treeman.png`: a bark-and-moss tree creature.
- Chib uses `chib-panda.png`: a black-and-white panda sword fighter.

These sheets contain four columns and four rows:

1. Four distinct idle breathing frames.
2. Two walk steps, guard, jump.
3. Crouch, light windup, light strike, heavy windup.
4. Heavy strike, special, hurt, knockdown.

The JSON manifests store source rectangles at measured alpha gutters. Idle
frames share a canvas and foot baseline. Dedicated knockdown poses do not get
rotated a second time. Combat frames are scaled relative to the idle body,
so attack effects do not resize the fighter. `tools/register_roster_atlases.py`
rebuilds the latest manifests without modifying source images.

`roster-diversity-generation.json` records the exact prompts and built-in
image_gen provenance. `roster-diversity-preview.png` shows the updated fighters.

## Earlier artwork

Rook, Vex, Golem, Saikyo, Soldier, Minamoto, and Raguel retain their existing
atlases and separate four-frame idle strips. Earlier generation prompts remain
in `generation.json`, `idle-generation.json`, `raguel-generation.json`, and
`raguel-idle-generation.json`. Their pose manifests use the same runtime API.

Previous image files remain intact. Verified copies of the older sources are
in `../backups/pre-style-rework/`, `../backups/pre-raguel-rework/`, and
`../backups/pre-roster-diversity/`, each with SHA-256 hashes. The latest backup
also records the previous roster data and the four replaced human atlases.
