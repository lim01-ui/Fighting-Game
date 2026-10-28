# Roster balance — 2026-10-28

This pass gives every design a strength and a cost. It is a starting balance
pass, not a claim of equal competitive win rates; human matchup playtesting is
still needed. Character IDs, artwork, weapons and move identities are retained.

The shared baseline is 100 HP, movement speed 6 pixels per simulation frame,
and multipliers of 1.0. Special and ultimate attacks share a five-second
cooldown starting when an ability begins, including recovery and hitstop.
Pause and LAN waiting freeze it; each round/reset begins charging for five
seconds from FIGHT (the intro does not count). A full
ultimate meter is preserved if the ability is still on cooldown.
An interrupted special still spends its cooldown. Unarmored interruptions
cancel the old hitbox, and the next accepted move starts fresh projectile
and effect flags.
Attack recovery is a separate property: slower fighters still recover more
slowly from their swings. Hovering remains cosmetic and does not remove a
flying character's grounded collision box.

The Special key in the keybind overlay shows `READY` or the seconds remaining,
with a recharge bar and a dimmed key while unavailable. Regular attacks and
movement remain available while it recharges. Multi-hit specials divide one
damage budget across their hits; normal attacks do not inherit special-only
extra hits. Projectile abilities deal damage through their projectiles only,
avoiding an additional invisible melee hit. Timeouts compare health
percentages instead of raw HP. Walking carries fractional pixels so speed
stats behave equally in both directions.

## Stats

Defense is damage received: a lower number is stronger armor. Durability is
`health / defense` relative to baseline, before integer damage rounding. The
previous very large health **and** armor bonuses have been narrowed to keep
durability differences manageable. Sanya is uniquely fastest and has the
lowest health and effective durability.

| Fighter | HP | Speed | Jump | Damage | Damage received | Durability | Visual size |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ONI | 102 | 1.08 | 0.95 | 1.00 | 0.98 | 1.04 | 1.00 |
| ANGELIX | 88 | 1.10 | 1.25 | 0.88 | 1.04 | 0.85 | 1.00 |
| GOLEM | 124 | 0.72 | 0.78 | 1.20 | 0.92 | 1.35 | 1.12 |
| PHOENIX | 96 | 0.88 | 1.18 | 1.12 | 1.00 | 0.96 | 1.00 |
| NOVA | 92 | 1.14 | 1.10 | 0.90 | 1.02 | 0.90 | 1.00 |
| IRON | 116 | 0.84 | 0.84 | 0.92 | 0.90 | 1.29 | 1.00 |
| JINX | 85 | 1.27 | 1.20 | 0.84 | 1.04 | 0.82 | 1.00 |
| KESTREL | 92 | 1.08 | 1.28 | 0.96 | 1.02 | 0.90 | 1.00 |
| BRAMBLE | 108 | 0.94 | 0.94 | 0.88 | 0.96 | 1.13 | 1.00 |
| RAGUEL | 97 | 1.06 | 1.04 | 1.04 | 1.00 | 0.97 | 1.00 |
| SANYA | 78 | 1.40 | 1.18 | 0.85 | 1.06 | 0.74 | 1.00 |
| GLACIER | 120 | 0.78 | 0.80 | 1.15 | 0.94 | 1.28 | 1.10 |
| SAIKYO | 100 | 1.08 | 1.10 | 1.04 | 1.02 | 0.98 | 1.00 |
| RENEGADE | 122 | 0.80 | 0.84 | 1.08 | 0.93 | 1.31 | 1.10 |
| NULL | 110 | 0.83 | 0.86 | 1.22 | 0.98 | 1.12 | 1.05 |
| PO | 108 | 0.98 | 1.04 | 1.02 | 0.98 | 1.10 | 1.00 |
| MINAMOTO | 90 | 1.02 | 1.03 | 0.96 | 1.02 | 0.88 | 1.00 |

Golem, Glacier and Renegade also have wider, taller collision bodies. Their
extra toughness therefore comes with a larger target, reduced movement and
jump height, and longer swing recovery. NULL is a smaller bruiser with the
strongest individual hits but less durability than those three tanks.
Visual size multipliers apply during matches; selection portraits retain their
shared readable framing and head proportions.

## Strengths and tradeoffs

| Fighter | Strength | Cost / opening for the opponent |
| --- | --- | --- |
| ONI | Quick twin-blade pressure and modest armor | Shorter reach, lower jump |
| ANGELIX | High jump, staff reach, orb zoning | Low health and damage; committed recovery |
| GOLEM | Largest health pool, hammer power and knockback | Slowest movement, low jump, large target, slow swings |
| PHOENIX | Longest ordinary sword reach, stronger hits, good jump | Slow walk and longer attack recovery; below-average HP |
| NOVA | Mobile orb zoning and quick attacks | Low durability, lower damage, short melee reach |
| IRON | Best damage reduction, shield reflection, armored special | Slow, low jump, short reach and weaker hits |
| JINX | Fast knife pressure, high jump, fan coverage | Low health, weak damage and short melee reach |
| KESTREL | Best jump, long spear reach, thrust mobility | Below-average health and damage; slower attack recovery |
| BRAMBLE | Moderate armor, health and control | Lower damage, modest reach, slower movement and recovery |
| RAGUEL | Flexible katana range and teleport positioning | Slightly low health; no tank or speed extremes |
| SANYA | Fastest walk and rapid twinblade swings | Lowest HP, weakest durability, light damage and knockback |
| GLACIER | Tanky body, hard punches and freeze control | Shortest attack reach, slow movement and jump, large target |
| SAIKYO | Mobile, quick, well-rounded karate attacks | Short fist reach and slightly weaker defense |
| RENEGADE | Durable bark, strong punches and knockback | Slow movement and recovery, low jump, large target |
| NULL | Highest hit damage, good cleaver reach | Longest recovery, slow walk, low jump, less armor than tanks |
| PO | Sturdy panda duelist, responsive katana, dash special | Average reach, slightly slower walk and recovery |
| MINAMOTO | Bow zoning, reach and arrow stun | Lower health and damage; slower attacks and recovery |

## Derived attacks

These are the actual standing attack blueprints at 60 simulation frames per
second, including integer rounding. Timing columns are
`startup / active / recovery` frames. Reach is the attack box length beyond
the fighter, in collision pixels. Weapon startup and reach multipliers are
now 1.0: the entire ordinary timing/range budget is visible in `attack_mods`,
without multiplying two hidden bonuses together.

Ultimate burst is the nominal total if every allowed melee hit or every
projectile connects, before defense, blocking and combo scaling. It counts
one damage source for projectile moves. Real burst is usually lower because
of spacing, knockback, blocking and projectile spread. The four extreme
inherited budgets were adjusted: Angelix and Golem down, Nova and Jinx up.

| Fighter | Light damage | Light timing | Heavy damage | Heavy timing | Heavy reach | Ultimate burst |
| --- | ---: | --- | ---: | --- | ---: | ---: |
| ONI | 5 | 3/3/5 | 14 | 9/4/15 | 73 | 39 |
| ANGELIX | 4 | 4/3/6 | 12 | 10/4/17 | 85 | 36 |
| GOLEM | 6 | 5/3/7 | 16 | 13/4/20 | 85 | 47 |
| PHOENIX | 5 | 4/3/6 | 15 | 11/4/18 | 95 | 44 |
| NOVA | 4 | 3/3/5 | 12 | 9/4/15 | 74 | 36 |
| IRON | 4 | 4/3/6 | 12 | 11/4/17 | 71 | 36 |
| JINX | 4 | 3/3/5 | 11 | 8/4/14 | 70 | 35 |
| KESTREL | 4 | 4/3/6 | 13 | 10/4/16 | 92 | 40 |
| BRAMBLE | 4 | 4/3/6 | 12 | 10/4/17 | 74 | 33 |
| RAGUEL | 5 | 3/3/6 | 14 | 9/4/16 | 81 | 44 |
| SANYA | 4 | 3/3/5 | 11 | 8/4/14 | 79 | 36 |
| GLACIER | 5 | 4/3/7 | 16 | 11/4/19 | 68 | 40 |
| SAIKYO | 5 | 3/3/5 | 14 | 9/4/15 | 70 | 39 |
| RENEGADE | 5 | 4/3/7 | 15 | 12/4/19 | 81 | 39 |
| NULL | 6 | 5/3/7 | 17 | 12/4/20 | 88 | 48 |
| PO | 5 | 3/3/6 | 14 | 9/4/16 | 78 | 40 |
| MINAMOTO | 4 | 4/3/6 | 13 | 10/4/17 | 82 | 40 |

## Playtesting priorities

Check whether the enlarged tanks can close distance against ranged fighters,
whether Sanya's speed compensates for 78 HP, and whether short-range fighters
can punish Phoenix's sword recovery. Record full matches in both player
positions with the same skill level. Automated cooldown, collision, damage
budget and stat invariant tests catch regressions; they cannot establish
competitive balance by themselves.

## Validation and previews

- 71 unit/regression tests passed, including initial match lockouts, overlay
  countdowns, all 17 cooldown boundaries,
  special/ultimate sharing, interruption, normal-attack availability, bot
  fallback, tank tradeoffs, symmetric walking and fair timeouts.
- `python -B tools/preview_roster_balance.py` exercises 1,260 real match frames.
  Held Special is accepted only on frames 301 and 601 in each match.
- [Cooldown HUD and Golem versus Sanya](2026-10-28/golem-sanya-cooldown.png).
- [Ready HUD and Glacier versus Renegade](2026-10-28/choom-renegade-ready.png).
- [Updated selection stats](2026-10-28/selection-golem.png).
