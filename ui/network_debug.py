"""Read-only LAN diagnostics; never affects simulation timing or input."""
import pygame
from ui import retro
from ui.text_layout import draw_text_fit


def draw_network_debug(screen, transport, rollback, render_fps=0, smooth_remote=False):
    panel = pygame.Rect(20, 154, 470, 142)
    pygame.draw.rect(screen, (10, 16, 28), panel, border_radius=6)
    pygame.draw.rect(screen, (55, 100, 130), panel, 1, border_radius=6)
    ping = transport['ping_ms']
    ping_text = 'MEASURING' if ping is None else f'{ping:.1f} MS'
    age = transport['last_received_age']
    age_text = '--' if age is None else f'{age * 1000:.0f} MS'
    lines = (
        ('LAN / ROLLBACK 60 HZ    F3: HIDE', (100, 220, 250)),
        (f'RTT {ping_text}  FPS {render_fps:.0f}  INPUT AGE {age_text}', (225, 235, 245)),
        (f"INPUT/S TX {transport['sent_rate']:.0f} RX {transport['received_rate']:.0f}  LOSS N/A (TCP)", (225, 235, 245)),
        (f"PRED {rollback['prediction_depth']}/8  CORRECTIONS {rollback['corrections']}  REPLAY {rollback['rollback_frames']}", (255, 210, 115)),
        ('VIEW DELAY: 33 MS  F4: REALTIME' if smooth_remote
         else 'VIEW DELAY: 0 MS  F4: SMOOTH', (100, 220, 250)),
    )
    font = retro.font('Arial', 15)
    for index, (text, color) in enumerate(lines):
        draw_text_fit(screen, font, text, color,
                      pygame.Rect(panel.x + 10, panel.y + 7 + index * 26,
                                  panel.width - 20, 22), align='left')
