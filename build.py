#!/usr/bin/env python3
import subprocess
import os

BUILDS = {
    "very_short": {
        "_inherits": "wasm-threads-release-3.2.4",
        "_dockerfile": "very_short.dockerfile",
    },
    "short": {
        "_inherits": "wasm-threads-release-3.2.4",
        "_dockerfile": "short.dockerfile",
    },
    "wasm-threads-release-3.2.4": {
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
    "wasm-threads-debug-3.2.4": {
        "_inherits": "wasm-threads-release-3.2.4",
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

def get_docker_tag(build_name):
    return f'ghcr.io/quadtree/godot-builder:{build_name}'

def run_build(build_name):
    print(f'********** BUILDING {build_name} **********')
    docker_tag = get_docker_tag(build_name)
    docker_args = ['docker', 'build']

    args = get_build_config(build_name)

    args['BUILDKIT_INLINE_CACHE'] = 1

    for (k,v) in args.items():
        if k[0] == '_': continue
        docker_args.append('--build-arg')
        docker_args.append(f'{k}={v}')

    docker_args.append('--tag')
    docker_args.append(docker_tag)

    docker_args.append('-f')
    docker_args.append(args['_dockerfile'])

    docker_args.append('--cache-from')
    docker_args.append(','.join([get_docker_tag(it) for it in sorted(BUILDS.keys(), key=lambda it2: 0 if it2 == build_name else 1)]))

    docker_args.append('.')

    run_env = dict(os.environ)
    run_env["DOCKER_BUILDKIT"] = "1"

    subprocess.run(docker_args, check=True, env=run_env)

    docker_push_args = ['docker', 'push', docker_tag]

    subprocess.run(docker_push_args, check=False if 'ALLOW_PUSH_FAILURE' in os.environ and os.environ['ALLOW_PUSH_FAILURE'] == '1' else True, env=run_env)


for build_name in BUILDS.keys():
    run_build(build_name)
