#!/bin/bash
set -xe

if [ ! -d "/out" ]; then
    echo '/out directory must be mounted with a docker volume command like -v/some_host_dir:/out'
    false
fi

if [ ! -d "/project" ]; then
    echo '/project directory must be mounted with a docker volume command like -v/some_host_dir:/out:ro'
    false
fi

mkdir /build
cp -R /project/* /build/
cd /build && LD_LIBRARY_PATH='/root/mono-installs/desktop-linux-x86_64-release/lib' xvfb-run -a /base/godot/bin/godot*tools.64.mono ${EXPORT_COMMAND:---export} HTML5 /out/index.html
cd /out
python3 /usr/local/bin/devserver.py
