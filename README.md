# music-to-colors-visualizer
analyze beats and frequencies of a song and produce animated visuals

As i was working on this project, i discovered that i was mapping the analyzed song data linearly across the visualizer bars, because only 1/3 of the bars were moving properly and i was wondering why that happens and discovered that most of the energy of music is in low frequencies like bass and mid ~(~50-2500 Hz). High frequencies like treble usually have much less amplitude, so those bars barely move. That’s why the first 1/3 of the bars that rappresent bass and partially mid are jumping a lot and the last 2/3 that rappresent higher Hz, mid and high frequencies barely move.

example of the code i used for linear mapping:
```
bins_per_bar = len(spec) // NUM_BARS
for b in range(NUM_BARS):
    start_bin = b * bins_per_bar
    end_bin = start_bin + bins_per_bar
    spectrum[i, b] = np.mean(spec[start_bin:end_bin])
```

