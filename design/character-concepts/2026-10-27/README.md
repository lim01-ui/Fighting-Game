# Character concepts and playable replacements

These standalone transparent PNGs reinterpret the supplied references in
the game's chibi pixel style. Eight approved concepts now have separate
24-pose animation atlases integrated into the playable roster. The concept
PNGs remain preserved as design references.

## Integrated designs

Oni replaces Rook, Angelix replaces Vex, Phoenix replaces Sable, PO replaces
Chib, the moss-crystal Golem replaces Golem, the mint mecha replaces Sanya,
NULL replaces Soldier, and Glacier replaces Choom. Sanya keeps her name.
The other concepts remain unintegrated candidates.

Active sprite sheets and manifests are in `../../../assets/characters/style-v2/`.
The stable internal slot IDs are retained for saved selections and LAN packets.
See that folder's README for weapons, hovering and animation details.

- [Roster preview](integrated-roster-preview.png)
- [Actual selection screen](chibi-selection-preview.png)
- [Proportion comparison with Raguel, Nova and Renegade](chibi-reference-comparison.png)
- [Animated idle, movement and combat preview](integrated-roster-animation.gif)
- [Current chibi revision prompts](chibi-proportion-revision-prompts.json),
  generated with the built-in `image_gen` tool. All eight have larger heads,
  shorter bodies and smaller equipment; the two flyers have small wings.
- [Exact integration prompts](roster-integration-generation.json), generated
  with the built-in `image_gen` tool.

| File | Design | Preserved weapon / key details |
| --- | --- | --- |
| [01-obsidian-flame-robot.png](01-obsidian-flame-robot.png) | Dark armored robot | Twin blue/pink energy blades, horned helmet, ghost flame |
| [02-ivory-gold-dragon-robot.png](02-ivory-gold-dragon-robot.png) | White/gold dragon robot | Cyan energy-claw gauntlet, dragon mask, pale mane |
| [03-moss-crystal-golem.png](03-moss-crystal-golem.png) | Moss/crystal stone golem | Huge stone fists, blue crystals, cyan chest core, hanging roots |
| [04-glacier-crystal-golem.png](04-glacier-crystal-golem.png) | Ice golem | Giant ice fists, crystalline crown and shoulder/back shards |
| [05-royal-armored-golem.png](05-royal-armored-golem.png) | Royal armored guardian | Massive rectangular greatsword, gold helmet crest, blue cape |
| [06-round-panda-ninja.png](06-round-panda-ninja.png) | Round samurai-era panda ninja | Conical hat, red tassels, green ribbons, sheathed katana |
| [07-ember-oni-golem.png](07-ember-oni-golem.png) | Ember oni golem | Fiery halberd/cleaver, hooked chain, horns and white mane |
| [08-ivory-amber-horned-mecha.png](08-ivory-amber-horned-mecha.png) | Ivory/amber mecha | Orange helmet crest, black shoulder horns, silver hair, amber power sockets |
| [09-mint-twinblade-mecha.png](09-mint-twinblade-mecha.png) | Mint twin-blade mecha | Fork-tipped mint sword and forearm blade/shield, ivory armor, long antenna horns |
| [10-golden-winged-valkyrie.png](10-golden-winged-valkyrie.png) | Flying female valkyrie | Red hair, gold energy-feather wings, golden sword, dark kite shield |
| [11-cyan-winged-raven-mage.png](11-cyan-winged-raven-mage.png) | Flying female raven mage | Blonde hair, cyan wings and crescent-orb staff; no pet companion |

## Proportion targets

- Robots: the normal roster's standing height and compact chibi proportions.
- Active Golem and Glacier: Renegade's body size and large round head, with
  small torsos and short limbs. They use the shared roster body scale.
- Panda: normal standing height, with a rounder face and belly, short limbs,
  and a samurai-era ninja silhouette.
- All designs keep readable dark outlines and simplified pixel shading.
- The two female winged candidates are shown airborne, with hovering poses and
  complete wingspans; the mecha candidates use standing ready poses.
- Source PNG canvas sizes are export dimensions, not gameplay scale settings.

## Creation

Created with the built-in `image_gen` tool. The existing Raguel/Rook/Vex roster
preview is the rendering/proportion reference. `generation.json` stores the
exact per-design prompts, output filenames, and generation provenance.
`additional-generation.json` records the four later mecha/flying concepts and
their direct user-reference/style-reference roles.
`flying-proportion-revisions.json` records the final compact chibi proportions
applied to both airborne female concepts.
`mage-no-pet-revision.json` records removal of the separate bird companion.

The approved eight have animated idle, movement, guard, jump, crouch, hurt,
light/heavy attacks, special moves and knockdown poses. Phoenix uses a compact
golden geometric sword; Golem carries a small moss-themed stone warhammer;
PO uses a short straight pale-jade katana; Glacier uses ice fists.
All other carried equipment follows each concept. Angelix has no pet.

`assets/characters/backups/pre-concept-integration/` contains verified copies
of the previous eight active designs and their metadata.
