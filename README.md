# Video Surveillance over IP

A live video surveillance system that captures webcam input on the server,
encodes it as H.264, packages it into MPEG-DASH segments, serves them over
HTTP, and plays the live stream in a browser using `dash.js` and HTML5 Media
Source Extensions (MSE).

## Pipeline

```
Webcam  →  FFmpeg (capture + H.264 + DASH muxer)  →  HTTP server  →  Browser (dash.js)
```

## Project Files

| File | Purpose |
|------|---------|
| `config.json`       | All system-specific parameters (camera name, paths, port, framerate, segment duration). |
| `start_capture.py`  | Reads the config and launches FFmpeg to capture and segment the stream. |
| `start_server.py`   | Reads the config and serves the DASH content + web page over HTTP. |
| `index.html`        | The custom HTML5 player page (uses dash.js). |
| `dash.all.min.js`   | The dash.js library (downloaded once from <https://cdn.dashjs.org/>). |
| `report.pdf`        | Project report. |

## Prerequisites

- **FFmpeg** on PATH (Windows DirectShow build).
  Verify with `ffmpeg -version`.
- **Python 3.8+** on PATH.
  Verify with `python --version`.
- A modern desktop or Android browser. **iOS Safari does not support DASH.**
- A webcam (built-in or USB).

## One-Time Setup

### 1. Find your webcam's name

DirectShow identifies cameras by name. Run:

```
ffmpeg -list_devices true -f dshow -i dummy
```

Look in the output for a line like:

```
[dshow @ 000001f5...] "HD Camera" (video)
```

Copy the exact name (including spaces) into `config.json` under `camera_name`.

### 2. Find your webcam's framerate

Run a one-second probe:

```
ffmpeg -f dshow -i video="HD Camera" -t 1 probe.mp4
```

In the FFmpeg output look for a line like `Stream #0:0: Video: ... 30 fps`.
That number is your camera's native framerate. Put it in `config.json`
under `framerate`. Common values are 10, 15, 25, or 30 fps.

> **Why this matters.** The DASH muxer requires a keyframe at the start
> of every segment. We therefore set the GOP (keyframe interval) to
> `framerate × segment_duration`. If `framerate` is wrong, segments will
> not be aligned to keyframes and the player will glitch.

### 3. Edit `config.json`

```json
{
  "camera_name": "HD Camera",
  "output_folder": "./dash_output",
  "server_port": 8000,
  "framerate": 30,
  "segment_duration": 4,
  "window_size": 15,
  "extra_window_size": 60
}
```

| Key | Meaning |
|-----|---------|
| `camera_name`        | DirectShow device name (Step 1). |
| `output_folder`      | Folder where FFmpeg writes manifest + segments. Created automatically. |
| `server_port`        | Port for the HTTP server. |
| `framerate`          | Camera's native framerate (Step 2). |
| `segment_duration`   | DASH segment length in seconds (project measured 2, 4, and 6). |
| `window_size`        | Segments listed in the manifest at any time. With 4-second segments and `window_size = 15`, that is 60 seconds of segments visible to the player. |
| `extra_window_size`  | Additional segments kept on disk past the manifest window for time-shifted seeking. With `extra_window_size = 60` and 4-second segments, that adds 240 seconds, giving roughly 5 minutes of total seekable history. |

## Running

Two terminals, both started from the project root.

### Terminal 1 — start the capture pipeline

```
python start_capture.py
```

This reads `config.json` and launches FFmpeg. You should see log lines like
`frame= 450 fps= 30 ...` updating continuously. Keep this running.

### Terminal 2 — start the HTTP server

```
python start_server.py
```

This serves `output_folder` (and copies `index.html` + `dash.all.min.js`
into it so the browser can load them).

### Open the player in a browser

Navigate to:

```
http://localhost:8000/index.html
```

The first segment becomes available a few seconds after FFmpeg starts. If
the page loads while FFmpeg is still warming up, refresh after ~10 seconds.

### Stop

- Ctrl+C in Terminal 2 to stop the server.
- Ctrl+C **once** in Terminal 1 to stop FFmpeg cleanly. (Multiple
  presses can leave a malformed manifest.)

## UI Controls

| Control | Behavior |
|---------|----------|
| Play / pause / native seek bar | Standard HTML5 video controls. |
| **Jump to Live**   | Seeks to the live edge minus the configured `liveDelay` (16 s). |
| **Rewind to time** | Pick a wall-clock time (HH:MM:SS); the player seeks to that moment in the recorded buffer. Bounded by the seekable window. |
| **Take Screenshot** | Captures the current frame as a PNG and downloads it. Works whether playing or paused. |
| Toast notifications | Inline confirmations and error messages for each action. |

## Notes on Configuration

- **`liveDelay`** (in `index.html`, currently 16 seconds) is a player-side
  setting that controls how far behind the live edge the player sits.
  Lower values = lower latency, but more risk of stalling. It is not in
  `config.json` because it is a tuning parameter, not a system parameter.
- The HTML page references the manifest with a **relative URL**
  (`manifest.mpd?t=<timestamp>`), so it is portable across hosts and ports
  without modification.

## Tested Configuration

- Windows 10
- FFmpeg (any recent build)
- Python 3.x
- Chrome / Firefox / Edge
- 30 fps 720p USB webcam
- Segment durations 2, 4, and 6 seconds (see report for latency
  measurements)

## Resources Used

- FFmpeg DASH muxer documentation:
  <https://ffmpeg.org/ffmpeg-formats.html#dash-2>
- dash.js: <https://dashjs.org/>
- dash.js live streaming docs:
  <https://dashif.org/dash.js/pages/usage/live-streaming.html>
- MDN, *DASH Adaptive Streaming for HTML5 Video*:
  <https://developer.mozilla.org/en-US/docs/Web/HTML/DASH_Adaptive_Streaming_for_HTML_5_Video>
