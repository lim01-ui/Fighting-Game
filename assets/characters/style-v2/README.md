# Shared chibi fighter artwork

All seventeen fighters use the same transparent-sprite loader and a 72-pixel
reference body height. Statistics and collision dimensions are preserved.
Weapons, effects and display names follow the approved character designs.

## Active concept replacements

| Stable slot | Display name | Atlas | Equipment |
| --- | --- | --- | --- |
| rook | Oni | `oni-chibi.png` | Compact twin cyan/violet energy blades; animated head flame |
| vex | Angelix | `angelix-chibi.png` | Small crescent-orb staff and cyan wings; no pet |
| sable | Phoenix | `phoenix-chibi.png` | Compact golden geometric sword, small shield and gold wings |
| chib | PO | `po-chibi.png` | Short straight pale-jade samurai katana |
| golem | Golem | `golem-moss-chibi.png` | Small rectangular stone hammer, moss and cyan crystal details |
| sanya | Sanya | `sanya-mecha-chibi.png` | Short mint fork-tipped sword and forearm blade/shield; faces opponent |
| soldier | NULL | `null-chibi.png` | Compact flaming cleaver polearm and hooked chain |
| choom | Glacier | `glacier-chibi.png` | Bare ice fists; no projectile weapon |

The current eight use Raguel's large-head/tiny-body proportions. Golem and
Glacier follow Renegade's round head, small torso and short limbs. Their body
height remains the same 72-pixel reference used by the older roster. Wings
and weapons are reduced so faces remain readable in selection cards.

Selection cards, the large selection preview and the VS portraits now scale
by body height and a shared foot baseline. Wide equipment does not shrink
the character. `blit_preview` clips only content outside its portrait area.
Earlier, taller designs are preserved in `../backups/pre-chibi-proportions/`.

These sheets each contain 24 poses in four columns and six rows: four idle,
four movement, guard/jump/crouch/hurt, four light, four heavy, and special
anticipation/contact/follow-through plus knockdown. Combat playback follows
the actual attack startup, active and recovery windows. Low attacks reuse
their weapon motion at crouch height; airborne attacks play above the floor.

Angelix and Phoenix hover 24 pixels above their normal baseline and bob by
six pixels. Their idle wings, hair and cloth move, and their movement cycles
use gliding poses. Knockdown returns them to the floor. This is visual flight;
the normal collision and jump rules still apply. The lobby also shows hovering.

Manifests measure the body independently of extended wings, flames, antennae
and weapons. Per-pose anchors stabilize the body position; idle frames share
one canvas. `tools/register_concept_roster.py` rebuilds the eight manifests.

Oni, NULL and Sanya use measured boot origins for their four idle poses.
Their drawings are not evenly centred inside atlas columns; using column
centres made the whole body jump sideways. The loader also aligns the final
rasterized foot baseline after scaling. These three use a gentler 240ms
idle cadence, and the player renderer skips the extra whole-body bob.
Breathing, flames, hair and energy ribbons keep their four animation frames.
`tools/preview_idle_stability.py` captures the current three loops.

Artwork was generated with the built-in `image_gen` tool. Exact prompts are
in `../../../design/character-concepts/2026-10-27/roster-integration-generation.json`.
`concept-integration-sources.json` and `concept-integration-revisions.json`
record generated source paths and the fist/hammer refinements.
The current proportion revision prompts are in
`../../../design/character-concepts/2026-10-27/chibi-proportion-revision-prompts.json`;
`chibi-proportion-sources.json` records their generated sources.

`tools/preview_concept_roster.py` saves the roster PNG and animated GIF in
the character-concepts folder, plus the real selection screen and a comparison
with Raguel, Nova and Renegade. `tools/smoke_concept_matches.py` exercises
four real training matches and saves idle/combat captures there.
Previous active images, manifests, roster metadata and SHA-256 hashes are
archived in `../backups/pre-concept-integration/`.

## Earlier ten-character update

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

Saikyo, Minamoto, and Raguel retain their existing atlases and separate
four-frame idle strips. Earlier generation prompts remain
in `generation.json`, `idle-generation.json`, `raguel-generation.json`, and
`raguel-idle-generation.json`. Their pose manifests use the same runtime API.

Previous image files remain intact. Verified copies of the older sources are
in `../backups/pre-style-rework/`, `../backups/pre-raguel-rework/`, and
`../backups/pre-roster-diversity/`, each with SHA-256 hashes. The latest backup
also records the previous roster data and the four replaced human atlases.
