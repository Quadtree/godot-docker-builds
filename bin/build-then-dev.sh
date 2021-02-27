#!/bin/bash
set -xe
cp -R /project /build
cd /build && LD_LIBRARY_PATH='/root/mono-installs/desktop-linux-x86_64-release/lib' xvfb-run -a /base/godot/bin/godot.x11.tools.64.mono ${EXPORT_COMMAND} HTML5 /out/index.html
cd /out
python3 /usr/local/bin/devserver.py
