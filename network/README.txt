Direct-IP LAN matches
=====================

One player selects HOST LAN MATCH and shares the displayed IPv4 address with
the other player. The other player selects JOIN LAN MATCH and enters that
address, either as an IP alone or as IP:port (for example 192.168.1.5:47611).
Once connected, both choose fighters and the host chooses the stage.

The host listens on TCP port 47611. Both players must be on a network that
allows local traffic between their computers; a firewall may need to allow
Python Fighters on that port. Public internet matchmaking and relay servers
are not included.

During a match, each computer controls one fighter using its Player 1 controls.
Inputs are exchanged as numbered lockstep frames. The game keeps drawing while
it waits for the matching remote input; simulation advances only when both
players' inputs for that frame are available. This avoids blocking the window
while preserving deterministic combat updates. A slow or disconnected peer can
still pause simulation. Inputs are frozen when sent so each computer simulates
the same inputs even if a key is released while waiting. After 15 seconds
without the next input, the game reports a connection error. Escape leaves
immediately, including while waiting for a stalled peer.

Joining runs in the background so connection attempts do not freeze the
window; Escape cancels. Setup packets are received incrementally so a partial
packet cannot freeze fighter/stage synchronization. A host port already in
use reports an error instead of allowing competing listeners on Windows.

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
6. Try joining an unreachable address and press Escape during the attempt.
   Confirm the window remains responsive. Try the displayed IP:port format.
7. Stop sending on one peer without closing its socket; confirm the other
   times out after 15 seconds and Escape can leave before that timeout.

Automated loopback checks
-------------------------
Run python -m unittest discover -s tests -v from the project root. These cover
TCP setup fragmentation, connection closure, input snapshots, timeouts, and
host port reuse. A real two-computer playtest is still required to verify the
team's network and firewall configuration.
