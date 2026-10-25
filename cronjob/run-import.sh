#!/bin/sh
set -eu
. /run/importer.env
exec /usr/local/bin/python /app/main.py
