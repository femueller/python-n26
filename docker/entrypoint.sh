#!/bin/sh

set -eu
sudo -E -u "#${PUID}" -g "#${PGID}" "$@"
