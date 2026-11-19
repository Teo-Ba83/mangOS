#!/bin/bash
# Downloads LocalSend (free AirDrop-like file sharing: iPhone, Android, Mac,
# Windows, Linux) from its official GitHub release and checks it against the
# SHA-256 digest GitHub publishes for the release asset.
#   usage: fetch-localsend.sh <dest-dir>
# Writes <dest-dir>/localsend.deb and <dest-dir>/localsend.conf (version, URL,
# SHA-256). MangOS ships localsend.conf so installed systems can install the
# same verified file later (Settings > AirDrop). Exit 1 if anything fails.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
. "$HERE/versions.env"
DEST=$1; mkdir -p "$DEST"; rm -f "$DEST/localsend.deb" "$DEST/localsend.conf"
REPO=localsend/localsend
ver=${LOCALSEND_VERSION:-latest}
if [ "$ver" = latest ]; then
  url=$(curl -fsSIL -o /dev/null -w '%{url_effective}' "https://github.com/$REPO/releases/latest") || exit 1
  case "$url" in */releases/tag/v*) ver=${url##*/tag/v};; *) echo "ERROR: cannot resolve LocalSend version" >&2; exit 1;; esac
fi
asset="LocalSend-$ver-linux-x86-64.deb"
dl="https://github.com/$REPO/releases/download/v$ver/$asset"
want=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/tags/v$ver" |
       python3 -c 'import json,sys; a=[x for x in json.load(sys.stdin)["assets"] if x["name"]==sys.argv[1]]; print((a[0].get("digest") or "").removeprefix("sha256:") if a else "")' "$asset") || want=""
if [ -z "$want" ]; then echo "ERROR: no SHA-256 digest published for $asset" >&2; exit 1; fi
curl -fsSL --retry 3 -o "$DEST/localsend.deb.part" "$dl" || { echo "ERROR: download failed: $dl" >&2; exit 1; }
got=$(sha256sum "$DEST/localsend.deb.part" | cut -d' ' -f1)
if [ "$got" != "$want" ]; then echo "ERROR: LocalSend checksum mismatch (want $want, got $got)" >&2; rm -f "$DEST/localsend.deb.part"; exit 1; fi
mv "$DEST/localsend.deb.part" "$DEST/localsend.deb"
printf 'LOCALSEND_VERSION=%s\nLOCALSEND_URL=%s\nLOCALSEND_SHA256=%s\n' "$ver" "$dl" "$got" > "$DEST/localsend.conf"
echo "LocalSend $ver sha256 OK $got"
