# Python Fighters hello

Python Fighters is a keyboard-controlled 2D fighting game built with
Pygame-CE. Choose a fighter and stage, battle a CPU opponent, practice in
training mode, or connect to another player over a local network.

## Features

### Game modes

- **Local vs CPU** — Fight a CPU opponent with Easy, Normal, or Hard
  difficulty.
- **Training mode** — Practice against a dummy that can stand, block, or
  attack. Track your current damage and best combo, reset the round, and open
  an in-game move list.
- **Direct-IP LAN matches** — Host or join a two-player match over a local
  network. Matches support rematches and report when the other player
  disconnects. Public matchmaking and internet relay servers are not included.
- **How to play** — Browse the in-game field guide for movement, attacks,
  ultimates, blocking, and training tips.

### Fighting and match features

- **17 fighters**, each with their own archetype, stats, weapon, and signature
  special/ultimate behavior:
  Oni, Angelix, Golem, Phoenix, Nova, Iron, Jinx, Kestrel, Bramble, Raguel, Sanya,
  Glacier, Saikyo, Renegade, NULL, PO, and Minamoto.
- **Different attack options:** light and heavy attacks, crouching and aerial
  attacks, character-specific special moves, and a unique ultimate for every
  fighter.
- **Five-second special cooldown:** special and ultimate attacks share a
  timer, shown on Special in the keybind overlay. Every round begins with a
  five-second lockout starting at FIGHT. Afterward it starts when the move begins,
  counts during recovery and hitstop, and pauses when the match pauses or
  waits for a LAN peer. Normal attacks remain available during the cooldown.
- **Roster tradeoffs:** Golem, Glacier and Renegade are larger, slower tanks;
  Sanya is the fastest fighter with the lowest health. Every fighter has
  strengths and weaknesses in movement, durability, damage, range and recovery.
  See the [full balance table](design/balance/roster-balance.md).
- **Defense and counterplay:** block by holding the block key or moving away
  from the opponent. Blocking reduces damage; a well-timed block can parry and
  interrupt an incoming attack.
- **Combos and meter:** chain hits before the combo window expires, build
  ultimate meter by dealing and taking damage, and spend a full meter on your
  fighter's ultimate.
- **Best-of-three matches** with round countdowns, health and meter displays,
  round wins, and match-end screens.
  Timeouts compare the percentage of health remaining, so larger health pools
  do not automatically win.
- **Combat feedback:** hit and block callouts, combo and damage displays,
  hit sparks, projectiles, screen shake, hit pause, knockdowns, KO effects,
  and victory poses.
- **Fighter animation:** idle breathing, attack lunges, guard poses, and
  block/parry effects.
- **Sprite artwork:** all fighters use pixel sprites. Ten fighters have chibi
  replacement atlases styled after Iron, Sable, Nova, Jinx, Kestrel, Bramble,
  and Raguel. The original artwork is preserved in a dedicated backup. See the
  [sprite audit](assets/characters/SPRITE_AUDIT.md) for coverage and prompts.

### Stages, presentation, and settings

- **16 restored arenas:** all eight City and all eight Ocean backgrounds,
  with the original rooftop/dock floors, camera parallax and stage selector.
- Animated night-city startup and menu backgrounds.
- Bold startup menus and animated KO/victory banners with impact lettering,
  sparks, a winner crown and gold confetti. See the
  [presentation previews](design/stage-concepts/2026-10-27/README.md).
- Music, sound effects, stage atmosphere, and camera parallax.
- Settings for master/music/effects volume, fullscreen, and Player 1 key
  rebinding. Preferences are saved between launches.
- **Scalable display:** resize or maximize the window from a minimum of
  **1280 × 720**, or enable **Options → Fullscreen** to fit the current display.
  The game retains its 16:9 proportions with borders when needed, sharp pixel
  graphics and correctly aligned mouse controls. Fullscreen also fits displays
  smaller than the minimum window size. Combat coordinates stay consistent
  across screen sizes, including LAN matches.
- In-match controls/help overlay and fitted, readable HUD/menu text.

## Getting started

### Requirements

- Python
- Dependencies listed in [`requirements.txt`](./requirements.txt)

Install dependencies and start the game from the project directory:

```bash
python -m pip install -r requirements.txt
python main.py
```

The game uses the included files in `assets/` for its title video, music,
sound effects, fighter sprites, and portraits. Keep that directory alongside
the Python source when running the game.

For instructions to create a Windows build, see
[`BUILD_WINDOWS.md`](./BUILD_WINDOWS.md).

## Controls

### Player 1 (default)

| Action | Key |
| --- | --- |
| Move left / right | A / D |
| Jump / crouch | W / S |
| Block / parry | Q |
| Light / heavy / special | J / K / L |

### Player 2 defaults

| Action | Key |
| --- | --- |
| Move left / right | Left / Right arrows |
| Jump / crouch | Up / Down arrows |
| Block / parry | Right Alt |
| Light / heavy / special | Enter / Right Shift / Right Ctrl |

Player 2 defaults are used by the CPU opponent and are also displayed in the
in-match controls overlay. A LAN player uses their local Player 1 controls.

### Match and training controls

| Action | Key |
| --- | --- |
| Pause / resume | P (Escape also pauses offline matches) |
| Reset round | R |
| Show / hide controls | H |
| Cycle training dummy (stand, block, attack) | T |
| Show / hide training move list | V |
| Rematch after a local match | Enter, Space, or R |
| Return to menu after a local match | Escape |

From the start menu, click **Options → Player 1 Controls**, click a key box,
and press any keyboard key to bind it. Press **Escape while a box is listening**
to unbind that action; Escape otherwise returns to the previous menu. Changes
save automatically. Assigning a key already in use swaps the two bindings.
Choose **Restore Default Controls** to reset just the bindings.

The in-game controls overlay shows active bindings and labels cleared actions
as **UNBOUND**. When P, R, H, T, or V is assigned to a combat action, that action
takes priority over the corresponding shortcut; Escape still opens pause.
In LAN matches, Escape leaves the match instead of opening the pause menu.

## LAN matches

Both players need to be able to reach one another over the same local network.
The host shares the displayed IPv4 address; the joining player enters it from
**Join LAN Match**. The host listens on TCP port `47611`. A firewall may need
to allow the game through on that port. More details and a playtest checklist
are in [`network/README.txt`](./network/README.txt).
