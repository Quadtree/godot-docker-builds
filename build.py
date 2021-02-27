#!/bin/bash
import subprocess

BUILDS = {
    "threads-release": {
        "_dockerfile": "wasm.dockerfile",
        "GODOT_VERSION": "3.2.4.rc",
        "GODOT_TAG": "3.2",
        "MONO_VERSION": "2020-02",
        "UBUNTU_VERSION": "20.04",
        "EMSCRIPTEN_VERSION": "2.0.6",
        "MONO_TARGET": "runtime-threads",
        "GODOT_TARGET": "release",
        "GODOT_EXPORT_TEMPLATE_NAME": "webassembly_threads_release",
        "GODOT_USE_THREADS": "yes",
    },
    "threads-debug": {
        "_inherits": "threads-release",
        "GODOT_TARGET": "debug",
        "GODOT_EXPORT_TEMPLATE_NAME": "webassembly_threads_debug",
    },
}

def get_build_config(build_name):
    args = {}
    if "_inherits" in BUILDS[build_name]:
        args = get_build_config(BUILDS[build_name]["_inherits"])

    for (k,v) in BUILDS[build_name].items():
        args[k] = v

    return args

for build_name in BUILDS.keys():
    docker_args = ['docker', 'build']

    args = get_build_config(build_name)

    for (k,v) in args.items():
        if v[0] == '_': continue
        docker_args.append('--build-arg')
        docker_args.append(f'{k}={v}')

    docker_args.append('--tag')
    docker_args.append(f'ghcr.co/quadtree/godot-{build_name}')

    docker_args.append('-f')
    docker_args.append(args['_dockerfile'])

    docker_args.append('.')

    subprocess.run(docker_args, check=True)
