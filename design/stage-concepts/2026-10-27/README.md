# Archived living arena update

The active game has restored all eight City and eight Ocean stages. The
captures below document the earlier scenic experiment, not the current selector.

Six pixel-art arenas previously replaced the City/Ocean selection. They were
recreated from the six online reference images using built-in image generation.
The source pictures were not available as local files.

- [All six arenas](six-arenas.png)
- [Animated arena gallery](living-arenas.gif)
- [Startup title](startup-title.png) and [main menu](startup-menu.png)
- [Stage selection](stage-selection.png)
- [KO animation](ko-animation.gif) and [KO still](ko-preview.png)
- [Victory animation](victory-animation.gif) and [victory still](victory-preview.png)
- [Exact generation prompts](generation-prompts.json)

Saved backgrounds and generated-source records are in
`../../../assets/stages/scenic/`. The PNGs are static source artwork; trees,
water, sky, lanterns, fireflies, stars, grass and leaves animate in the runtime
renderer. Each arena uses effects suited to the scene. The combat platform
and collision rules remain stable.

Startup buttons use larger outlined pixel text over solid panels. KO uses
extruded impact lettering, a sliding banner, radial light and spark particles.
Victory adds a crown and continuously falling gold confetti. Defeat and
time-up results have their own labels and colors, and draw rounds remain supported.
