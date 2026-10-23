# Fighter sprite audit

Reviewed 2026-10-23. Initially, 12 fighters had no sprite sheets and rendered
procedurally. Only Saikyo, Renegade, and Soldier had imported sprite sets.
Rook also had a portrait depicting a different outfit and face from the new
sword fighter. Selection and VS now use the generated sprite preview for
generated fighters, keeping their appearance consistent with combat.

## Current coverage

| Fighter | Combat artwork | Status |
| --- | --- | --- |
| Rook | Blue/gold swordsman | Generated v1 integrated |
| Vex | Red/orange dual-dagger fighter | Generated v1 integrated |
| Golem | Stone/bronze hammer fighter | Generated v1 integrated |
| Sable | Procedural whip fighter | Needs sprite sheet |
| Nova | Procedural orb fighter | Needs sprite sheet |
| Iron | Procedural shield fighter | Needs sprite sheet |
| Jinx | Procedural knife fighter | Needs sprite sheet |
| Kestrel | Procedural spear fighter | Needs sprite sheet |
| Bramble | Procedural club fighter | Needs sprite sheet |
| Ash | Procedural katana fighter | Needs sprite sheet |
| Ryoko | Procedural gauntlet fighter | Needs sprite sheet |
| Volt | Procedural baton fighter | Needs sprite sheet |
| Saikyo | Imported CC0 pixel art | Guard and ultimate pose selection fixed |
| Renegade | Imported CC0 pixel art | Guard and knockdown scaling fixed |
| Soldier | Imported CC0 pixel art | Guard and knockdown scaling fixed |

The three imported sets use different pixel densities and art styles from the
generated set. Their source artwork remains available and its existing CC0
documentation is in README.txt and saikyo/README.txt.

## First generated batch

Generated with the built-in image_gen tool. Each transparent PNG contains
eight poses: idle, walk, block, jump, light, heavy, special, and hit. These are
single poses per state, not full multi-frame walk or attack cycles. Existing
bobbing, attack lunges, crouch/aerial transforms, and mirrored facing remain;
knockdown uses a rotated hit pose and ultimate uses the special pose.

| Fighter | Sheet | Frame manifest | Exact generation and revision prompts |
| --- | --- | --- | --- |
| Rook | [PNG](rook/fighter-v1.png) | [JSON](rook/fighter-v1.json) | [Prompts](rook/fighter-v1.prompt.json) |
| Vex | [PNG](vex/fighter-v1.png) | [JSON](vex/fighter-v1.json) | [Prompts](vex/fighter-v1.prompt.json) |
| Golem | [PNG](golem/fighter-v1.png) | [JSON](golem/fighter-v1.json) | [Prompts](golem/fighter-v1.prompt.json) |

Manifests contain source-pixel rectangles and a reference body height. The
loader trims transparent padding, flips facing, and uses one body scale per
fighter so large weapons/effects do not shrink the body. Rectangles were
checked against the actual output dimensions rather than assuming generated
images exactly match the requested dimensions or grid.

## Continuing the batch

Use Rook's final sheet as the style reference. Keep each remaining fighter's
existing weapon, palette, and silhouette from characters/character_data.py.
Generate each sheet separately with transparent alpha and ample space between
all poses. Inspect the actual output before writing its manifest, particularly
weapon tips, effects, and the gap between atlas rows. Save the exact prompts.
Add the fighter to GENERATED_ASSETS in characters/sprite_fighter.py and set
its roster sprite_asset to its key once the PNG and manifest are ready.

## Verification

Run `python -m unittest discover -s tests -v`. Sprite checks render all 15
fighters in both directions, all combat states, and all attack variants.
Generated poses are checked for transparency, populated frames, facing
flips, and accidental inclusion of another atlas row. Selection, training,
and a contact sheet of all 24 generated poses were also rendered and inspected.
