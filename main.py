# main.py
"""
Entry point for the arcade lobby, offline modes, and direct-IP LAN matches.
"""

import sys
import random
import pygame

import settings
from ui import (
    menu, character_select, stage_select, settings_menu, intro_video, lan_lobby,
)
from game import fight_scene
from characters import character_data
from audio import music, preferences
from network import lan
from stages import stages


def main():
    pygame.init()
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=512)
    pygame.mixer.init()
    preferences.load()
    from audio import sound_fx as _sfx
    _sfx.init()
    display_flags = pygame.FULLSCREEN if preferences.get("fullscreen") else 0
    screen = pygame.display.set_mode(
        (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), display_flags
    )
    pygame.display.set_caption(settings.WINDOW_TITLE)
    clock = pygame.time.Clock()

    music.play("intro", volume=0.25)
    if not intro_video.run_title_video(screen, clock):
        music.stop()
        pygame.quit()
        return

    while True:
        music.play("intro", volume=0.25)
        choice = menu.run_main_menu(screen, clock)

        if choice == "EXIT":
            break
        if choice == "SETTINGS":
            screen = settings_menu.run_settings_menu(screen, clock)
            if screen is None:
                break
            continue

        if choice == "TUTORIAL":
            tutorial_result = menu.run_tutorial(screen, clock)
            if tutorial_result == "EXIT":
                break
            if tutorial_result == "BACK":
                continue
            choice = tutorial_result

        if choice in ("LAN_HOST", "LAN_JOIN"):
            peer = (
                lan_lobby.run_host_lobby(screen, clock)
                if choice == "LAN_HOST"
                else lan_lobby.run_join_lobby(screen, clock)
            )
            if peer is None:
                continue
            try:
                if choice == "LAN_HOST":
                    p1_key = character_select.run_character_select(
                        screen, clock, title="HOST: CHOOSE YOUR FIGHTER"
                    )
                    if p1_key is None:
                        continue
                    stage_key, palette_key = stage_select.run_stage_select(
                        screen, clock, title="HOST: CHOOSE THE STAGE"
                    )
                    remote_choice = peer.exchange_setup({
                        "role": "host",
                        "protocol": lan.PROTOCOL_VERSION,
                        "p1_character": p1_key,
                        "stage_key": stage_key,
                        "palette_key": palette_key,
                    })
                    p2_key = remote_choice.get("p2_character")
                    if (
                        remote_choice.get("role") != "guest"
                        or remote_choice.get("protocol") != lan.PROTOCOL_VERSION
                        or p2_key not in character_data.ROSTER_ORDER
                    ):
                        raise ValueError("The joining player sent an invalid fighter choice.")
                    setup = {
                        "protocol": lan.PROTOCOL_VERSION,
                        "p1_character": p1_key,
                        "p2_character": p2_key,
                        "stage_key": stage_key,
                        "palette_key": palette_key,
                    }
                    peer.send_setup(setup)
                    local_player = 1
                else:
                    p2_key = character_select.run_character_select(
                        screen, clock, title="GUEST: CHOOSE YOUR FIGHTER"
                    )
                    if p2_key is None:
                        continue
                    host_choice = peer.exchange_setup({
                        "role": "guest",
                        "protocol": lan.PROTOCOL_VERSION,
                        "p2_character": p2_key,
                    })
                    if (
                        host_choice.get("role") != "host"
                        or host_choice.get("protocol") != lan.PROTOCOL_VERSION
                        or host_choice.get("p1_character")
                        not in character_data.ROSTER_ORDER
                    ):
                        raise ValueError("The host sent an invalid lobby selection.")
                    setup = peer.receive_setup()
                    p1_key = setup.get("p1_character")
                    p2_key = setup.get("p2_character")
                    stage_key = setup.get("stage_key")
                    palette_key = setup.get("palette_key")
                    if (
                        setup.get("protocol") != lan.PROTOCOL_VERSION
                        or p1_key not in character_data.ROSTER_ORDER
                        or p2_key not in character_data.ROSTER_ORDER
                        or (stage_key, palette_key) not in stages.all_stage_combos()
                        or p1_key != host_choice.get("p1_character")
                        or stage_key != host_choice.get("stage_key")
                        or palette_key != host_choice.get("palette_key")
                    ):
                        raise ValueError("The host sent an invalid match setup.")
                    if p2_key != host_choice.get("p2_character"):
                        raise ValueError("The host's setup does not match your fighter choice.")
                    local_player = 2

                result = fight_scene.run_fight(
                    screen, clock,
                    p1_character=p1_key,
                    p2_character=p2_key,
                    stage_key=stage_key,
                    palette_key=palette_key,
                    network_peer=peer,
                    local_player=local_player,
                )
                if result == "QUIT":
                    break
            except (ConnectionError, OSError, ValueError) as error:
                lan_lobby.show_lan_message(
                    screen, clock, "LAN MATCH ENDED", str(error)
                )
            finally:
                peer.close()
            continue

        if choice in ("1VBOT", "TRAINING"):
            training_mode = choice == "TRAINING"
            diff = None if training_mode else menu.run_difficulty_menu(screen, clock)
            if not training_mode and diff is None:
                continue

            # Pick a fighter and stage before starting either mode.
            p1_key = character_select.run_character_select(
                screen, clock, title="CHOOSE YOUR FIGHTER"
            )
            if p1_key is None:
                continue

            p2_key = "rook" if training_mode else random.choice(character_data.ROSTER_ORDER)

            stage_key, palette_key = stage_select.run_stage_select(
                screen, clock, title="CHOOSE YOUR STAGE"
            )

            result = fight_scene.run_fight(
                screen, clock,
                difficulty_name=diff,
                p1_character=p1_key,
                p2_character=p2_key,
                stage_key=stage_key,
                palette_key=palette_key,
                training_mode=training_mode,
            )
            if result == "MENU":
                continue
            if result == "QUIT":
                break

    music.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
