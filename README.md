# Python Fighters

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

- **15 fighters**, each with their own archetype, stats, weapon, and signature
  special/ultimate behavior:
  Rook, Vex, Golem, Sable, Nova, Iron, Jinx, Kestrel, Bramble, Ash, Ryoko,
  Volt, Saikyo, Renegade, and Soldier.
- **Different attack options:** light and heavy attacks, crouching and aerial
  attacks, character-specific special moves, and a unique ultimate for every
  fighter.
- **Defense and counterplay:** block by holding the block key or moving away
  from the opponent. Blocking reduces damage; a well-timed block can parry and
  interrupt an incoming attack.
- **Combos and meter:** chain hits before the combo window expires, build
  ultimate meter by dealing and taking damage, and spend a full meter on your
  fighter's ultimate.
- **Best-of-three matches** with round countdowns, health and meter displays,
  round wins, and match-end screens.
- **Combat feedback:** hit and block callouts, combo and damage displays,
  hit sparks, projectiles, screen shake, hit pause, knockdowns, KO effects,
  and victory poses.
- **Fighter animation:** idle breathing, attack lunges, guard poses, and
  block/parry effects.

### Stages, presentation, and settings

- **Three stages:** Sunset, Dojo, and Neon.
- **Seven palettes per stage:** Classic, Night, Snow, Fire, Ice, Storm, and
  Golden — 21 stage-and-palette combinations.
- Animated title video, music, sound effects, stage atmosphere, and parallax
  backgrounds.
- Settings for master/music/effects volume, fullscreen, and Player 1 key
  rebinding. Preferences are saved between launches.
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

Player 1 bindings can be changed from **Settings → Player 1 Controls**. The
in-game controls overlay shows the active bindings.
In LAN matches, Escape leaves the match instead of opening the pause menu.

## LAN matches

Both players need to be able to reach one another over the same local network.
The host shares the displayed IPv4 address; the joining player enters it from
**Join LAN Match**. The host listens on TCP port `47611`. A firewall may need
to allow the game through on that port. More details and a playtest checklist
are in [`network/README.txt`](./network/README.txt).
