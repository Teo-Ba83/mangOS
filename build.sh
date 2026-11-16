#!/bin/bash
# MangOS: one reproducible build script that produces the final ISO.
#
#   sudo ./build.sh            build out/MangOS-<version>-amd64.iso (+ .sha256)
#   sudo ./build.sh --clean    wipe the work directory first (full rebuild)
#
# Must run as root on Debian 13 (trixie) with live-build installed. On any
# other Linux host use scripts/buildenv.sh, which creates a Debian chroot and
# runs this script inside it.
#
# Environment:
#   MANGOS_WORK=dir             work directory (default: ./build)
#   MANGOS_SKIP_ARTCRAFT=1      build without the ArtCraft packages
#   MANGOS_REQUIRE_ARTCRAFT=1   fail if any ArtCraft package cannot be fetched
#   MANGOS_APT_PROXY=url        HTTP proxy for apt during the build only
#   MANGOS_BUILD_CA=file.crt    extra CA trusted only *during* the build
#                               (TLS-intercepting proxies); never shipped
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
. "$ROOT/scripts/versions.env"
export MANGOS_APT_PROXY="${MANGOS_APT_PROXY:-}" MANGOS_VERSION MANGOS_CODENAME DEBIAN_SUITE DEBIAN_MIRROR DEBIAN_SECURITY_MIRROR

WORK=${MANGOS_WORK:-$ROOT/build}
OUT=$ROOT/out
CACHE=$WORK/cache-src
log() { printf '\n\033[1;33m==> %s\033[0m\n' "$*"; }

[ "$(id -u)" = 0 ] || { echo "build.sh must run as root" >&2; exit 1; }
command -v lb >/dev/null || { echo "live-build missing: apt install live-build (see scripts/buildenv.sh)" >&2; exit 1; }
for t in git curl rsvg-convert convert sassc glib-compile-resources xmllint xorriso mksquashfs; do
  command -v $t >/dev/null || { echo "missing tool: $t (see scripts/buildenv.sh for the package list)" >&2; exit 1; }
done

if [ "${1:-}" = --clean ] && [ -d "$WORK" ]; then
  log "Cleaning $WORK"
  (cd "$WORK" && lb clean --purge >/dev/null 2>&1 || true)
  rm -rf "$WORK"
fi
mkdir -p "$WORK" "$OUT" "$CACHE"

log "Staging live-build configuration"
rsync -a --delete --exclude cache --exclude chroot --exclude binary --exclude 'cache-src' \
      --exclude '.build' --exclude '*.iso' --exclude 'config/packages.chroot' \
      "$ROOT/auto" "$ROOT/config" "$WORK/"
OVL=$WORK/config/includes.chroot

log "Rendering logo, icons and wallpapers"
"$ROOT/branding/logo/make-logo.sh" "$OVL"
"$ROOT/scripts/make-wallpapers.sh" "$OVL/usr/share/backgrounds/mangos"
# Boot menu background (GRUB + isolinux): dark, mango logo at the top.
mkdir -p "$WORK/config/bootloaders"
{ echo '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">'
  echo '<rect width="800" height="600" fill="#1d1d1f"/>'
  echo '<svg x="352" y="40" width="96" height="96" viewBox="0 0 512 512">'
  sed -n '/<defs>/,/<\/svg>/p' "$ROOT/branding/logo/mangos-logo.svg" | sed '$d'
  echo '</svg></svg>'; } > "$WORK/config/bootloaders/splash.svg"

log "Building WhiteSur themes"
"$ROOT/scripts/fetch-themes.sh" "$OVL" "$CACHE"

log "Fetching ArtCraft packages"
rm -rf "$WORK/config/packages.chroot"; mkdir -p "$WORK/config/packages.chroot"
if [ "${MANGOS_SKIP_ARTCRAFT:-0}" = 1 ]; then
  echo "Skipped (MANGOS_SKIP_ARTCRAFT=1)"
elif ! "$ROOT/scripts/fetch-artcraft.sh" "$CACHE/artcraft"; then
  if [ "${MANGOS_REQUIRE_ARTCRAFT:-0}" = 1 ]; then echo "ArtCraft fetch failed" >&2; exit 1; fi
  echo "WARNING: some ArtCraft packages are missing; the ISO will not include them." >&2
fi
cp "$CACHE"/artcraft/*.deb "$WORK/config/packages.chroot/" 2>/dev/null || true
ls "$WORK/config/packages.chroot"

cd "$WORK"
log "lb config"
lb config >/dev/null

log "lb bootstrap"
lb bootstrap

if [ -n "${MANGOS_BUILD_CA:-}" ]; then
  log "Installing temporary build CA"
  install -D -m644 "$MANGOS_BUILD_CA" chroot/usr/local/share/ca-certificates/mangos-build-ca.crt
  cat "$MANGOS_BUILD_CA" >> chroot/etc/ssl/certs/ca-certificates.crt
fi

log "lb chroot"
lb chroot
# The temporary CA is removed by the 9990 hook; make sure it is really gone.
if [ -e chroot/usr/local/share/ca-certificates/mangos-build-ca.crt ]; then
  echo "ERROR: build CA still present in chroot" >&2; exit 1
fi

log "lb binary"
lb binary

ISO=$(ls -t "$WORK"/*.iso | head -1)
NAME="MangOS-$MANGOS_VERSION-amd64.iso"
mv "$ISO" "$OUT/$NAME"
(cd "$OUT" && sha256sum "$NAME" > "$NAME.sha256")
log "Done: $OUT/$NAME"
cat "$OUT/$NAME.sha256"
