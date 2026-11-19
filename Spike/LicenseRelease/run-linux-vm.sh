#!/bin/sh
# The production VM helper accepts the same arguments and environment.
set -eu
root=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
exec sh "$root/Tests/LinuxVM/run.sh" "$@"
