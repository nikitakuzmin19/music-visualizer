# play audio with miniaudio + draw reactive graphics with pyglet.

import time

import miniaudio
import pyglet
from pyglet import shapes

from utils import decode_to_pcm
from analyzer import analyze_track, get_frame_index_for_time

WIDTH, HEIGHT = 1200, 600

NUM_BARS = 64
BAR_WIDTH = (WIDTH // NUM_BARS)
MARGIN = 40


def _lerp(a, b, t):
    return tuple(int(a[j] + (b[j] - a[j]) * t) for j in range(3))

def bar_color(i):
    # red (bass) -> green (mid) -> blue (treble)
    t = i / (NUM_BARS - 1)
    if t < 0.5:
        return _lerp((255, 60, 30), (50, 210, 80), t * 2)
    return _lerp((50, 210, 80), (30, 140, 255), (t - 0.5) * 2)


def run(file_path: str):
    # load the song and analyze it (bass, mid, treble, spectrum, beats)
    print("Loading and analyzing...")
    pcm = decode_to_pcm(file_path)
    result = analyze_track(pcm)
    times = result["times"]
    spectrum = result["spectrum"]
    duration = float(times[-1])
    print(f"Ready. Duration: {duration:.1f}s")

    playing = False
    start_time = 0.0
    device = None

    def start_playback():
        nonlocal playing, start_time, device
        if playing:
            return
        playing = True
        start_time = time.time()
        stream = miniaudio.stream_file(file_path)
        device = miniaudio.PlaybackDevice()
        device.start(stream)

    def stop_playback():
        nonlocal playing, device
        if not playing:
            return
        playing = False
        if device is not None:
            device.stop()
            device = None

    # create window and bars
    window = pyglet.window.Window(WIDTH, HEIGHT, "Music Visualizer")

    bars = [
        shapes.Rectangle(MARGIN + i * BAR_WIDTH, MARGIN, BAR_WIDTH - 2, 10, color=bar_color(i))
        for i in range(NUM_BARS)
    ]

    @window.event
    def on_key_press(symbol, _):
        if symbol == pyglet.window.key.SPACE:
            if not playing:
                start_playback()
            else:
                stop_playback()
        elif symbol == pyglet.window.key.ESCAPE:
            window.close()

    @window.event
    def on_draw():
        window.clear()
        t = time.time() - start_time if playing else -1.0

        if not playing or t < 0:
            pyglet.text.Label(
                "Press SPACE to play",
                font_size=24,
                x=WIDTH // 2,
                y=HEIGHT // 2,
                anchor_x="center",
                anchor_y="center",
            ).draw()
            return

        t = min(t, duration)

        frame_idx = get_frame_index_for_time(t, times)
        frame = spectrum[frame_idx]

        for i, bar in enumerate(bars):
            prev_height = getattr(bar, "prev_height", bar.height)
            target = 20 + frame[i] * 400
            # ease toward target — avoids the bars snapping too hard between frames
            bar.height = prev_height * 0.7 + target * 0.3
            bar.prev_height = bar.height

        for bar in bars:
            bar.draw()

    pyglet.app.run()
