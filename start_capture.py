"""
start_capture.py
Reads config.json and launches FFmpeg to capture from the webcam,
encode with H.264, and produce a live DASH stream into output_folder.

Usage:  python start_capture.py
Stop with Ctrl+C (single press; let FFmpeg finalize cleanly).
"""

import json
import os
import subprocess
import sys


def main():
    # Load config
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"ERROR: {config_path} not found in current directory.")
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    camera_name = config["camera_name"]
    output_folder = config["output_folder"]
    framerate = config["framerate"]
    seg_duration = config["segment_duration"]
    window_size = config["window_size"]
    extra_window_size = config["extra_window_size"]

    # GOP must equal framerate * segment_duration so that each segment
    # starts with a keyframe and is independently decodable.
    gop = framerate * seg_duration

    # Make sure the output folder exists
    os.makedirs(output_folder, exist_ok=True)


    ffmpeg_cmd = [
        "ffmpeg",
        # ---- input ----
        "-f", "dshow",
        "-rtbufsize", "100M",
        "-r", str(framerate),
        "-i", f"video={camera_name}",
        # ---- video encoding ----
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-g", str(gop),
        "-keyint_min", str(gop),
        # ---- DASH muxer ----
        "-seg_duration", str(seg_duration),
        "-use_template", "1",
        "-use_timeline", "1",
        "-window_size", str(window_size),
        "-extra_window_size", str(extra_window_size),
        "-streaming", "1",
        "manifest.mpd",
    ]

    print("Launching FFmpeg with the following command:\n")
    print("  " + " ".join(ffmpeg_cmd) + "\n")
    print(f"Manifest will be written to: {os.path.join(output_folder, 'manifest.mpd')}")
    print(f"GOP = framerate * seg_duration = {framerate} * {seg_duration} = {gop}")
    print("Press Ctrl+C ONCE to stop (let FFmpeg finalize cleanly).\n")

    try:
        subprocess.run(ffmpeg_cmd, cwd=output_folder)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
