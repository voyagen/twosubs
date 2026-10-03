# twosubs

Small mpv Lua plugin: primary subtitles at the bottom, secondary subtitles just above them. Uses mpv's native subtitle decoding, timing, seeking, and rendering. No merging, generated subtitle files, or runtime dependencies beyond mpv.

Requires **mpv 0.41 or newer**. No Python or FFmpeg is needed to use the plugin.

## Install

On Linux or macOS:

```sh
git clone https://github.com/voyagen/twosubs.git
cd twosubs
mkdir -p ~/.config/mpv/scripts
cp scripts/twosubs.lua ~/.config/mpv/scripts/
```

Alternatively, download [`scripts/twosubs.lua`](scripts/twosubs.lua) and install it manually.

Copy `scripts/twosubs.lua` into your mpv scripts directory:

- Linux: `~/.config/mpv/scripts/`
- Windows: `%APPDATA%/mpv/scripts/`
- macOS: `~/.config/mpv/scripts/`

Remove or disable the original dualsubtitles script first; it uses the same keys and manages the same tracks. Restart mpv. This does not modify your mpv configuration or media files.

mpv automatically loads scripts from this directory; no `--script` flag is needed. To try it without installing:

```sh
mpv --script=./scripts/twosubs.lua movie.mkv
```

Select your primary track with `j`, then press `k` to select a secondary track. To start with specific tracks:

```sh
mpv --sid=1 --secondary-sid=2 movie.mkv
```

Track IDs appear in mpv's terminal output. External subtitles work through mpv's usual `--sub-file` and `sub-auto` options. Primary language preferences use mpv's existing `slang` option; the script does not auto-select a second language.

For two external subtitle files:

```sh
mpv --sub-file=english.srt --sub-file=spanish.srt --sid=1 --secondary-sid=2 movie.mp4
```

## Keys

| Key | Action |
| --- | --- |
| `j` / `J` | Next / previous primary track (mpv default) |
| `k` / `K` | Next / previous secondary track, including off |
| `u` | Swap primary and secondary tracks |
| `Ctrl+r` / `Ctrl+R` | Move secondary subtitles down / up |
| `v` | Toggle primary visibility (mpv default) |
| `Alt+v` | Toggle secondary visibility (mpv default) |

Bindings are non-forced; your `input.conf` takes precedence. Named actions can be rebound, for example `u script-binding twosubs/swap`.

## Secondary subtitle menu button

With mpv 0.41's built-in bottom bar, add these lines to `~/.config/mpv/script-opts/osc.conf` (the same mpv config directory on other platforms):

```ini
custom_button_1_content=S2
custom_button_1_mbtn_left_command=script-binding select/select-secondary-sid; script-message-to osc osc-hide
custom_button_1_mbtn_right_command=script-binding select/select-secondary-sid; script-message-to osc osc-hide
```

Restart mpv. Click **S2** on the bar's upper-right row to open mpv's native secondary subtitle picker; choose a track with the mouse or arrow keys and Enter. `k` still cycles the secondary track, including off.

If custom button 1 is already used, use the next consecutive unused number for all three options. This configuration keeps the built-in controller; mpv places custom buttons on the upper row, not beside the existing subtitle control. Other controllers have their own configuration.

[`examples/osc.conf`](examples/osc.conf) contains the same settings. Append them to your existing OSC settings rather than replacing that file.

## Positioning

Optional `script-opts/twosubs.conf` in your mpv config directory:

```ini
primary_pos=100
secondary_pos=82
```

Positions range from 0 (top) to 100 (bottom). Lower `secondary_pos` to leave more room for multiline dialogue. Font, size, outline, and margins use your existing mpv `sub-*` settings. Interactive position changes last for the current mpv session.

If the upper subtitle is too high, try `secondary_pos=90` or hold `Ctrl+r` to move it down. [`examples/twosubs.conf`](examples/twosubs.conf) provides this closer-spacing preset; copy it to your mpv `script-opts` directory to make it persistent.

This is deliberately a text-subtitle plugin. Both tracks have ASS styling and placement stripped so dialogue stays in the bottom area; authored signs, animation, and formatting are not preserved. Bitmap subtitles (PGS/VobSub) retain their native placement and are not reliably repositionable by these options. Spacing is fixed, not collision-aware: unusually tall or heavily wrapped cues can overlap; move the secondary track up or reduce the font size.

Native options reference: <https://mpv.io/manual/stable/#subtitles>.

## Check

The runnable smoke check generates temporary media and exercises the real plugin in mpv: two tracks, swapping, cycling, spacing, cue expiry, and seeking. Test dependencies: Python 3, mpv, and FFmpeg (FFmpeg is not needed by the plugin).

```sh
python tests/smoke.py
# With a working graphical session; also captures the actual layout:
python tests/smoke.py --visual /tmp/twosubs.png
```

Verified with mpv 0.41.0. This is an independent implementation, not a fork or a replacement for the original plugin's merging, clipboard, and language-selection features.

GitHub Actions runs the headless smoke check in an Arch Linux container to provide a current mpv with the required subtitle options. The optional visual check needs a graphical Linux session; the smoke harness uses Unix-domain sockets.

## License

[MIT](LICENSE).
