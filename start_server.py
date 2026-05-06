"""
start_server.py
Reads config.json and starts a Python HTTP server in the output_folder
so that the DASH manifest, segment files, and index.html are reachable
at http://localhost:<server_port>/.

Usage:  python start_server.py
Stop with Ctrl+C.
"""

import json
import os
import shutil
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler


def main():
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"ERROR: {config_path} not found in current directory.")
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    output_folder = config["output_folder"]
    port = config["server_port"]

    if not os.path.isdir(output_folder):
        print(f"ERROR: output folder '{output_folder}' does not exist.")
        print("Run start_capture.py first to create it and start FFmpeg.")
        sys.exit(1)

    # Copy the page assets (index.html and dash.all.min.js) into the
    # output folder so the browser can fetch them from the same origin
    # as the manifest. This is required because the page references the
    # manifest with a relative URL.
    for asset in ("index.html", "dash.all.min.js"):
        if os.path.exists(asset):
            dst = os.path.join(output_folder, asset)
            shutil.copyfile(asset, dst)
        else:
            print(f"WARNING: {asset} not found in current directory; "
                  f"the browser will not be able to load the page.")

    os.chdir(output_folder)

    server = ThreadingHTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"Serving {output_folder} at http://localhost:{port}/")
    print(f"Open http://localhost:{port}/index.html in your browser.")
    print("Press Ctrl+C to stop.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
