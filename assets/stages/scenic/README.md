# Archived scenic arenas

The active game uses all eight City and eight Ocean backgrounds again.
This archived recreation package contains six scenes:

| Stage ID | Background | Ambient motion |
| --- | --- | --- |
| sword_grotto | 01-moonblade-grotto.png | Fireflies, reflected water, swaying foliage, mist, falling leaves |
| sakura_relic | 02-sakura-relic.png | Falling petals, moving clouds, waterfalls, ripples, cyan lanterns |
| moonlit_shrine | 03-moonlit-shrine.png | Warm lantern flicker, blue fireflies, stream ripples, foliage, stars |
| aurora_lake | 04-aurora-lake.png | Moving aurora curtain, twinkling stars, shooting star, water, fireflies |
| ronin_heights | 05-ronin-heights.png | Maple leaves, swaying canopy, fluttering banners, clouds, lanterns |
| angkor_sanctuary | 06-angkor-sanctuary.png | Tree canopy, falling leaves, clouds, birds, grass, light motes |

The online reference pictures had no local source files. These six backgrounds
were recreated using the built-in `image_gen` tool, then saved here. Exact
prompts are in `../../../design/stage-concepts/2026-10-27/generation-prompts.json`;
`generation-sources.json` records the generated source files.

`stages/catalog.py` defines the scene regions. `stages/ambient.py` renders
localized water and aurora distortion, canopy/cloth sway, moving clouds,
waterfalls, fireflies, lantern light, leaves, stars and grass at runtime.
All motion is computed from elapsed time, independent of gameplay randomness.
Backgrounds are cached at 640x360 and ambient frames at 20 fps; combat and
input keep their normal update rate. The arena platform remains fixed.

The default arena is City 01, and menus use the night-city background.
These six scenic recreations are no longer selectable. Their preview renderer
is preserved in `stages/scenic_preview.py` for regenerating archived captures.

Run `python -B tools/preview_scenic_update.py` from the project root to capture
the arena gallery, animated GIFs, startup menu, stage selector and result screens.
