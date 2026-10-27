# Original fighter artwork

This backup preserves the ten fighters replaced during the chibi sprite style
rework: Rook, Vex, Golem, Sanya, Choom, Saikyo, Renegade, Soldier, Chib and Minamoto.
The seven style reference fighters are unchanged.

Each original source folder is copied intact, including animation sheets,
portraits, attribution files and any generation manifests/prompts. `manifest.json`
records the source commit, original roster entries, sprite specifications and
SHA-256 hashes of the copied files. `loaders/` contains the original Python sources
as restoration references; these copies are not imported by the game.

New artwork is stored separately in `assets/characters/style-v2/`. Original asset
folders also remain in place. To restore a fighter, use its entry in
`manifest.json` and the matching original loader configuration; do not copy an
old loader over the active one without reviewing newer changes.
