#!/usr/bin/env python3
import subprocess
import concurrent.futures

BUILDS = {
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

def get_docker_tag(build_name):
    return f'ghcr.co/quadtree/godot-builder:{build_name}'

def run_build(build_name):
    docker_tag = get_docker_tag(build_name)
    docker_args = ['docker', 'build']

    args = get_build_config(build_name)

    for (k,v) in args.items():
        if v[0] == '_': continue
        docker_args.append('--build-arg')
        docker_args.append(f'{k}={v}')

    docker_args.append('--tag')
    docker_args.append(docker_tag)

    docker_args.append('-f')
    docker_args.append(args['_dockerfile'])

    docker_args.append('.')

    subprocess.run(docker_args, check=True)

    docker_push_args = ['docker', 'push', docker_tag]

    subprocess.run(docker_push_args, check=True)

def prepare_build(build_name):
    docker_tag = get_docker_tag(build_name)
    docker_pull_args = ['docker', 'pull', docker_tag]
    subprocess.run(docker_pull_args)

for build_name in BUILDS.keys():
    prepare_build(build_name)

with concurrent.futures.ThreadPoolExecutor(8) as ex:
    for _ in ex.map(run_build, BUILDS.keys()): pass
