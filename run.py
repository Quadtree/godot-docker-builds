#!/usr/bin/env python3
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('indir')
parser.add_argument('outdir')
parser.add_argument('tag')

args = parser.parse_args()

docker_args = ["docker", "run", "-it", f'-v{args.indir}:/project:ro', f'-v{args.outdir}:/out', args['tag']]
subprocess.run(docker_args, check=True)
