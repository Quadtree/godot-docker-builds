#!/usr/bin/env python3
import subprocess
import os

BUILDS = {
    # Platforms
    "wasm": {
        "_dockerfile": "wasm.dockerfile",
    },


    # Godot Versions
    "3.2.4": {
        "GODOT_VERSION": "3.2.4.rc",
        "GODOT_TAG": "3.2",
        "MONO_VERSION": "2020-02",
        "UBUNTU_VERSION": "20.04",
        "EMSCRIPTEN_VERSION": "2.0.6",
    },


    # Build Attributes
    "build-type-server": {
        "BUILDER_BUILD_TYPE": "server",
    },

    "threads": {
        "MONO_TARGET": "runtime-threads",
        "GODOT_USE_THREADS": "yes",
    },

    "no-threads": {
        "MONO_TARGET": "runtime",
        "GODOT_USE_THREADS": "no",
    },

    "debug": {
        "GODOT_TARGET": "debug",
    },

    "release": {
        "GODOT_TARGET": "release",
    },

    "threads-release": {
        "_inherits": ["threads", "release"],
        "GODOT_EXPORT_TEMPLATE_NAME": "webassembly_threads_release",
    },

    "no-threads-release": {
        "_inherits": ["no-threads", "release"],
        "GODOT_EXPORT_TEMPLATE_NAME": "webassembly_release",
    },

    "threads-debug": {
        "_inherits": ["threads", "debug"],
        "GODOT_EXPORT_TEMPLATE_NAME": "webassembly_threads_debug",
    },

    "no-threads-debug": {
        "_inherits": ["no-threads", "release"],
        "GODOT_EXPORT_TEMPLATE_NAME": "webassembly_debug",
    },


    # Builds
    "wasm-threads-debug-3.2.4": {
        "_inherits": ["wasm", "3.2.4", "threads-debug"],
    },

    "wasm-release-3.2.4": {
        "_inherits": ["wasm", "3.2.4", "no-threads-release"],
    },

    "wasm-release-server-3.2.4": {
        "_inherits": ["wasm", "3.2.4", "no-threads-release", "build-type-server"],
    },

    "wasm-threads-release-server-3.2.4": {
        "_inherits": ["wasm", "3.2.4", "threads-release", "build-type-server"],
    },
}

def get_build_config(build_name):
    args = {}
    if "_inherits" in BUILDS[build_name]:
        if type(BUILDS[build_name]["_inherits"]) == list:
            inherits = BUILDS[build_name]["_inherits"]
        else:
            inherits = [BUILDS[build_name]["_inherits"]]

        for parent_name in inherits:
            for (k,v) in get_build_config(parent_name).items():
                args[k] = v

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

    print(f"Building with args: {args}")

    docker_args.append('--tag')
    docker_args.append(docker_tag)

    docker_args.append('-f')
    docker_args.append(args['_dockerfile'])

    docker_args.append('--cache-from')
    docker_args.append(docker_tag)
    #docker_args.append(','.join([get_docker_tag(it) for it in sorted(BUILDS.keys(), key=lambda it2: 0 if it2 == build_name else 1)]))

    docker_args.append('.')

    run_env = dict(os.environ)
    run_env["DOCKER_BUILDKIT"] = "1"

    subprocess.run(docker_args, check=True, env=run_env)

    docker_push_args = ['docker', 'push', docker_tag]

    subprocess.run(docker_push_args, check=False if 'ALLOW_PUSH_FAILURE' in os.environ and os.environ['ALLOW_PUSH_FAILURE'] == '1' else True, env=run_env)


for build_name in BUILDS.keys():
    if 'GITHUB_REF' in os.environ and os.environ['GITHUB_REF'].replace('refs/heads/', '') != build_name:
        print(f"NOT running {build_name} on this branch, {os.environ['GITHUB_REF']}")
        continue
    run_build(build_name)
