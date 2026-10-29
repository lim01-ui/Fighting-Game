# LAN input prediction and rollback

Both machines must run the same game revision and protocol **7**. A host chooses
the match configuration, but gameplay is input-authoritative peer rollback: each
player owns its own input history, and both machines simulate the same combat.
The host does not stream authoritative character positions.

## What changed

The old loop waited for the other player's input before simulating each frame.
Even a packet arriving just after the once-per-render poll could cost a whole
display frame. The match now runs fixed **60 Hz simulation ticks** from an
accumulator independently of rendering. Network reads and writes happen on a
separate thread, and the main loop does not block for a remote input.
LAN rendering and input polling target 120 Hz (`settings.LAN_RENDER_FPS`) while
combat and input transmission remain at 60 Hz. This reduces event and packet
polling delay when the hardware can sustain it; it does not speed up attacks or
timers. Short attack/jump taps are retained until the next unsent input tick.
Inputs are sampled only when their tick is about to simulate, so a faster render
loop never freezes a future tick's input early.

Enqueuing input wakes the transport's `select` through a nonblocking socketpair,
so sending does not wait for a periodic polling timeout. The main loop also
drains replies after background rendering, allowing packets arriving during that
work to correct the fighters before the same display frame is presented.

The local input takes effect on the next simulation tick, normally within
16.7 ms plus input sampling/render time, while remote input is predicted from its
last known action. Actual inputs replace predictions when they arrive. A wrong
prediction restores the saved state before the earliest affected tick and
replays the stored inputs. Hitboxes, hurtboxes, health, timers, and attack frame
data come from that corrected simulation, never interpolated render positions.

The rollback session retains **180 ticks** of history and permits at most
**8 unconfirmed simulated ticks**. That is about 133 ms of simulation lead, not
an RTT threshold. Reaching the limit pauses further simulation while networking,
rendering, and Escape remain responsive. A sustained gap cannot produce unlimited
speculation or an unbounded replay. When one player's intro ends earlier, its
first inputs remain queued until the other machine begins gameplay; a 15-second
absence of actual remote input is treated as a stalled connection.

## Wire format

After the JSON lobby setup, all gameplay records use `struct.Struct("!IH")`:

| Bytes | Field | Meaning |
| --- | --- | --- |
| 4 | Unsigned tick, network byte order | Input's simulation tick |
| 2 | Unsigned action mask | One bit per entry in `ACTIONS` |

This is **6 bytes per input tick**, or 360 bytes/s in each direction at 60 Hz,
before TCP/IP framing. There are no JSON strings, character snapshots, or full
game states in the gameplay stream. TCP can combine multiple records in one
network segment or split a record across reads; the parser handles both.

A repeated submission for the **same tick** is suppressed. The same held action
on a **new tick** is still transmitted: that record confirms the new tick's input.
Suppressing unchanged masks without an explicit run length or a confirmation
watermark would make "still holding right" indistinguishable from "packet missing"
and would prevent rollback confirmation. At six bytes, correctness is preferable
to an ambiguous change-only protocol.

Reserved tick values `0xFFFFFFFF` and `0xFFFFFFFE` carry ping and pong records.
Their 16-bit mask field is an echoed nonce. Each peer initiates a ping twice per
second and responds to the other's pings: normally 24 additional application
bytes/s sent per peer, excluding TCP/IP overhead. RTT is measured from a local
monotonic clock, so clocks do not have to be synchronized.

## Rendering smoothing

Real-time presentation is the default: both fighters draw the latest corrected
simulation state with **no intentional remote display delay** or extrapolation.
Local actions start on the next 60 Hz tick without waiting for a reply. A new
remote action becomes knowable only when its packet arrives; this mode cannot
remove physical network transit time, OS scheduling, or attack startup frames.

Press **F4** to opt into smoother remote position presentation: three tick-tagged
samples draw two ticks behind the render timeline (about 33 ms). Samples are
interpolated in tick order. Corrections replace replayed samples; gaps use at
most one tick of extrapolation and then hold. Press F4 again to return to the
latest state. The overlay displays the intentional view delay, not measured RTT.

The buffer smooths the local rollback simulation's remote positions; the network
itself exchanges inputs rather than snapshots. The local fighter is always drawn
immediately. Delayed presentation never writes back to gameplay positions or
changes collision detection. Remote attack poses and effects follow simulation,
so the optional mode smooths position rather than a fully delayed animation
timeline.

## Debugging a two-computer match

The LAN overlay starts enabled. Press **F3** to hide or show it. **F4** switches
between the default real-time view and optional smoothing.

| Metric | Interpretation |
| --- | --- |
| RTT | Smoothed ping/pong round trip, including transport scheduling |
| FPS | Rendering speed; low FPS with low RTT suggests CPU/render workload |
| Input age | Time since the last actual remote input record |
| Input/s TX and RX | Input records over the last second, usually near 60; these are not IP segment counts |
| Loss N/A (TCP) | TCP hides loss/retransmissions; unavailable does **not** mean zero |
| Prediction depth | How many simulated ticks await actual peer inputs; sustained 8/8 causes a bounded wait |
| Corrections | Number of batches that required replay after a wrong prediction |
| Replay | Total ticks replayed by those corrections |
| View delay | 0 ms in real-time mode; 33 ms in optional smooth mode; independent of RTT |

High RTT/input age and a growing prediction depth point toward the connection,
peer scheduling, or a slow peer. Low FPS on either computer can also reduce its
input production even when the network is fast. Corrections alone are expected
when a remote player changes direction or starts an attack; they are not a packet
loss measurement. Compare the overlay on both machines using the same stage and
fighters before assuming bandwidth is the bottleneck.

## Why TCP remains, and when UDP would help

TCP with `TCP_NODELAY` remains in this change. Prediction removes the request/reply
dependency without replacing connection setup, reliable delivery, or firewall
behavior at the same time. TCP restores lost bytes and presents records in order,
but a missing segment can delay later inputs behind it (head-of-line blocking).
Prediction hides short gaps; it cannot fix a long TCP retransmission stall.

A future UDP transport is a good fit if testing shows frequent retransmission
stalls. It must preserve the rollback API while adding:

1. A session identifier, datagram sequence number, and tick-tagged action masks.
2. Several recent input ticks redundantly included in each small datagram, so
   losing one datagram does not immediately lose a unique input.
3. An acknowledged tick/sequence window and bounded retransmission for missing
   inputs. Old input must still eventually arrive for deterministic confirmation.
4. A bounded reorder/replay window: accept late usable ticks, ignore identical
   duplicates and stale records, and reject conflicting inputs or unreasonable
   future ticks. Never process datagrams in arrival order as simulation order.
5. Loss/jitter measurement from sequence and ACK data, plus connection liveness,
   setup validation, and a clear timeout. UDP by itself supplies none of these.

## Code entry points and limits

- `LanPeer.submit_input(tick, values)`: enqueue one immutable tick without waiting.
- `LanPeer.receive_inputs()`: drain new actual inputs as `{tick: action_dict}`.
- `LanPeer.get_stats()`: transport diagnostics; `dropped_packets` is `None` for TCP.
- `RollbackSession`: input histories, prediction, state restoration, and replay.
- `RenderInterpolator`: visual-only position buffering.
- `poll_inputs()`: retained compatibility path for legacy tests/callers; active
  matches use the asynchronous API.

Transport queues and deduplication histories are bounded to 2,048 input records;
future input is bounded separately, and rollback uses its smaller 180-tick window.
The game must remain deterministic across peers, with matching assets, combat
rules, and simulation state. This implementation does not yet exchange periodic
state hashes or host state snapshots, so an unrelated determinism bug cannot be
detected and repaired by authoritative host reconciliation. A next step is
confirmed-tick state hashes plus a controlled resynchronization path. For a
fighting game, that extends the rollback foundation already implemented rather
than returning to per-frame network waits.
