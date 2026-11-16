#!/bin/bash
# Downloads the Broadcom firmware for the b43 driver, checks its SHA-512 and
# extracts it with b43-fwcutter into the chroot overlay (usr/lib/firmware/b43).
#   usage: fetch-b43-firmware.sh <overlay-root> <cache-dir>
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
. "$HERE/versions.env"
DEST=$1; CACHE=$2
command -v b43-fwcutter >/dev/null || { echo "b43-fwcutter missing on the build host" >&2; exit 1; }
mkdir -p "$CACHE"
TAR="$CACHE/broadcom-wl-$B43_FW_VERSION.tar.bz2"
if ! echo "$B43_FW_SHA512  $TAR" | sha512sum -c --status 2>/dev/null; then
  curl -fsSL --retry 3 -o "$TAR.part" "$B43_FW_URL"
  mv "$TAR.part" "$TAR"
fi
echo "$B43_FW_SHA512  $TAR" | sha512sum -c --status || { echo "b43 firmware: SHA-512 mismatch" >&2; rm -f "$TAR"; exit 1; }
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
tar xjf "$TAR" -C "$TMP" "broadcom-wl-$B43_FW_VERSION.wl_apsta.o"
mkdir -p "$DEST/usr/lib/firmware"
rm -rf "$DEST/usr/lib/firmware/b43"
b43-fwcutter -w "$DEST/usr/lib/firmware" "$TMP/broadcom-wl-$B43_FW_VERSION.wl_apsta.o" >/dev/null
# b43-fwcutter creates the directory as 0750; make it readable like other firmware
chmod 755 "$DEST/usr/lib/firmware/b43"; chmod 644 "$DEST/usr/lib/firmware/b43"/*
n=$(ls "$DEST/usr/lib/firmware/b43" | wc -l)
[ "$n" -gt 10 ] || { echo "b43 firmware: extraction produced only $n files" >&2; exit 1; }
echo "b43 firmware $B43_FW_VERSION: $n files, SHA-512 OK"
