ARG UBUNTU_VERSION=20.04
FROM ubuntu:$UBUNTU_VERSION

RUN echo 'Acquire::http::Pipeline-Depth 0;' >> /etc/apt/apt.conf
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y git python3-pip python xz-utils autoconf libtool make nano rsync pkg-config cmake python3 bison flex \
  git libx11-dev libxcursor-dev libxinerama-dev libgl1-mesa-dev libglu-dev libasound2-dev libpulse-dev libxi-dev libxrandr-dev yasm build-essential scons libudev-dev \
  curl xvfb

RUN mkdir /base && cd /base && git clone 'https://github.com/godotengine/godot'
ARG GODOT_MONO_BUILDS_REF=bda87f2
RUN mkdir /mono && cd /mono && git clone 'https://github.com/godotengine/godot-mono-builds' && cd godot-mono-builds && git checkout "$GODOT_MONO_BUILDS_REF"
RUN cd /mono && git clone 'https://github.com/mono/mono'

ARG MONO_VERSION=2020-02
RUN cd /mono/mono && git reset --hard && git checkout $MONO_VERSION
RUN cd /mono/godot-mono-builds && ./patch_mono.py --mono-sources=/mono/mono || true
RUN cd /mono/godot-mono-builds && ./linux.py configure --target=x86_64 --mono-sources=/mono/mono
RUN cd /mono/godot-mono-builds && ./linux.py make --target=x86_64 --mono-sources=/mono/mono

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y mono-complete
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y mono-devel

RUN cd /mono/godot-mono-builds && ./bcl.py make --product=desktop --mono-sources=/mono/mono
RUN cd /mono/godot-mono-builds && ./linux.py copy-bcl --target=x86_64 --mono-sources=/mono/mono

ARG GODOT_VERSION=3.2.4.rc
ARG GODOT_TAG=3.2
RUN cd /base/godot && git fetch && git checkout "$GODOT_TAG"
RUN cd /base/godot && scons -j8 p=x11 tools=yes module_mono_enabled=yes mono_glue=no copy_mono_root=yes mono_prefix="$HOME/mono-installs/desktop-linux-x86_64-release"
RUN cd /base/godot && LD_LIBRARY_PATH='/root/mono-installs/desktop-linux-x86_64-release/lib' xvfb-run ./bin/godot.x11.tools.64.mono --generate-mono-glue modules/mono/glue

RUN curl -L 'https://dot.net/v1/dotnet-install.sh' > /tmp/dotnet-install.sh
RUN chmod +x /tmp/dotnet-install.sh
RUN /tmp/dotnet-install.sh -c Current
ADD scripts/msbuild /usr/local/bin/msbuild