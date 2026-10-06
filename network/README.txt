Direct-IP LAN matches
=====================

One player selects HOST LAN MATCH. The host enters fighter and stage selection,
then shares the displayed IPv4 address with the other player. The other player
selects JOIN LAN MATCH, enters that address, and chooses their fighter.

The host listens on TCP port 47611. Both players must be on a network that
allows local traffic between their computers; a firewall may need to allow
Python Fighters on that port. Public internet matchmaking and relay servers
are not included.

During a match, each computer controls one fighter using its Player 1 controls.
Inputs are exchanged as numbered lockstep frames. The game keeps drawing while
it waits for the matching remote input; simulation advances only when both
players' inputs for that frame are available. This avoids blocking the window
while preserving deterministic combat updates. A slow or disconnected peer can
still pause simulation, and the game reports a disconnect.

Player 1 can hold Q to guard, or hold away from the opponent. Tap guard just
before an attack lands to parry it. The network protocol version is checked
during setup so incompatible game versions do not start a match.

After a match, press Enter or R on either computer to rematch, or Escape to
return both players to the main lobby.

Two-computer playtest checklist
-------------------------------

1. Put both computers on the same LAN and allow Python Fighters through the
   host computer's firewall for TCP port 47611.
2. Host a match, copy the displayed address, and join from the second computer.
3. Confirm both fighters respond to their local Player 1 controls; try moving
   and attacking simultaneously for several rounds.
4. At match over, press Enter on only one computer and confirm both rematch.
5. In another match, press Escape on only one computer and confirm both return
   to the lobby. Close the game abruptly on one side and confirm the other side
   displays a disconnect message instead of hanging.
