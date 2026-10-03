"""Loop the game's title video until the player presses an input button."""

from pathlib import Path
from bisect import bisect_right
import time

import av
import pygame

import settings


INTRO_END = 7.0
LOOP_START = 8.0
LOOP_END = 9.0

VIDEO_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "video"
    / "title_screen.mp4"
)


def _continue_to_menu_event(event):
    button_events = {
        pygame.KEYDOWN,
        pygame.MOUSEBUTTONDOWN,
        pygame.JOYBUTTONDOWN,
    }
    controller_button = getattr(pygame, "CONTROLLERBUTTONDOWN", None)
    if controller_button is not None:
        button_events.add(controller_button)
    return event.type in button_events


def _video_surface(screen, frame):
    rgb = frame.to_ndarray(format="rgb24").transpose(1, 0, 2)
    image = pygame.surfarray.make_surface(rgb)
    scale = min(
        screen.get_width() / frame.width,
        screen.get_height() / frame.height,
    )
    size = (
        max(1, int(frame.width * scale)),
        max(1, int(frame.height * scale)),
    )
    return pygame.transform.smoothscale(image, size)


def _draw_surface(screen, image):
    screen.fill((0, 0, 0))
    screen.blit(image, image.get_rect(center=screen.get_rect().center))
    pygame.display.flip()


def _frame_timestamp(frame, first_pts, frame_index, rate):
    if frame.pts is not None and first_pts is not None and frame.time_base is not None:
        return float((frame.pts - first_pts) * frame.time_base)
    return frame_index / rate


def _load_loop_frames(path, screen, rate):
    with av.open(str(path)) as container:
        if not container.streams.video:
            raise ValueError(f"Title video has no video stream: {path}")

        stream = container.streams.video[0]
        loop_frames = []
        first_pts = None
        for frame_index, frame in enumerate(container.decode(stream)):
            if frame_index == 0:
                first_pts = frame.pts
            timestamp = _frame_timestamp(frame, first_pts, frame_index, rate)
            if LOOP_START <= timestamp < LOOP_END:
                loop_frames.append(
                    (timestamp - LOOP_START, _video_surface(screen, frame))
                )

    if not loop_frames:
        raise ValueError(
            f"Title video has no frames between {LOOP_START:g}s and {LOOP_END:g}s: {path}"
        )
    return loop_frames


def run_title_video(screen, clock, video_path=VIDEO_PATH):
    """Play the opening once, then loop only the video segment from 8s to 9s."""
    path = Path(video_path)
    if not path.is_file():
        raise FileNotFoundError(f"Title video is missing: {path}")

    with av.open(str(path)) as container:
        if not container.streams.video:
            raise ValueError(f"Title video has no video stream: {path}")
        video = container.streams.video[0]
        rate = float(video.average_rate or settings.FPS)

    loop_frames = _load_loop_frames(path, screen, rate)
    loop_offsets = [offset for offset, _ in loop_frames]

    with av.open(str(path)) as container:
        video = container.streams.video[0]
        frames = iter(container.decode(video))
        try:
            frame = next(frames)
        except StopIteration as error:
            raise ValueError(f"Title video contains no frames: {path}") from error

        first_pts = frame.pts
        playback_started = time.monotonic()
        frame_index = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if _continue_to_menu_event(event):
                    return True

            timestamp = _frame_timestamp(frame, first_pts, frame_index, rate)
            if timestamp >= LOOP_END:
                break
            if INTRO_END <= timestamp < LOOP_START:
                frame_index += 1
                try:
                    frame = next(frames)
                except StopIteration as error:
                    raise ValueError(
                        f"Title video ends before the loop point at {LOOP_END:g}s: {path}"
                    ) from error
                continue

            presentation_timestamp = (
                timestamp
                if timestamp < INTRO_END
                else INTRO_END + timestamp - LOOP_START
            )
            if time.monotonic() - playback_started < presentation_timestamp:
                clock.tick(settings.FPS)
                continue
            _draw_surface(screen, _video_surface(screen, frame))

            frame_index += 1
            try:
                frame = next(frames)
            except StopIteration as error:
                raise ValueError(
                    f"Title video ends before the loop point at {LOOP_END:g}s: {path}"
                ) from error
            clock.tick(settings.FPS)

    loop_started = time.monotonic()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if _continue_to_menu_event(event):
                return True

        elapsed = (time.monotonic() - loop_started) % (LOOP_END - LOOP_START)
        frame_index = bisect_right(loop_offsets, elapsed) - 1
        _draw_surface(screen, loop_frames[frame_index][1])
        clock.tick(settings.FPS)
