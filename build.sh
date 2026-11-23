#!/bin/bash
# MangOS: one reproducible build script that produces the final ISO.
#
#   sudo ./build.sh            build out/MangOS-<version>-amd64.iso (Macs with
#                              64-bit EFI, PCs) and out/MangOS-<version>-efi32.iso
#                              (2006-2007 Macs with 32-bit EFI), + .sha256
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
#   MANGOS_BUILD_ID=build.N     build id appended to the version (CI run number)
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
for t in git curl b43-fwcutter bzip2 rsvg-convert convert sassc glib-compile-resources xmllint xorriso mksquashfs; do
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

log "Extracting b43 firmware (Broadcom Wi-Fi reserve driver)"
"$ROOT/scripts/fetch-b43-firmware.sh" "$OVL" "$CACHE/b43"

log "Fetching ArtCraft packages"
rm -rf "$WORK/config/packages.chroot"; mkdir -p "$WORK/config/packages.chroot"
if [ "${MANGOS_SKIP_ARTCRAFT:-0}" = 1 ]; then
  echo "Skipped (MANGOS_SKIP_ARTCRAFT=1)"
elif ! "$ROOT/scripts/fetch-artcraft.sh" "$CACHE/artcraft"; then
  if [ "${MANGOS_REQUIRE_ARTCRAFT:-0}" = 1 ]; then echo "ArtCraft fetch failed" >&2; exit 1; fi
  echo "WARNING: some ArtCraft packages are missing; the ISO will not include them." >&2
fi
# live-build only installs local packages named name_version_arch.deb; the
# ArtCraft release files are named e.g. wordcraft-0.18.1-linux-x86_64.deb.
EXPECTED_PKGS=""
for deb in "$CACHE"/artcraft/*.deb; do
  [ -e "$deb" ] || continue
  pkg=$(dpkg-deb -f "$deb" Package); ver=$(dpkg-deb -f "$deb" Version); arch=$(dpkg-deb -f "$deb" Architecture)
  cp "$deb" "$WORK/config/packages.chroot/${pkg}_${ver//:/%3a}_${arch}.deb"
  EXPECTED_PKGS="$EXPECTED_PKGS $pkg"
  echo "ArtCraft package: $pkg $ver ($arch)"
done
log "Popularity Contest snapshot (Mango Store apps of the week)"
"$ROOT/scripts/fetch-popcon.sh" "$OVL"

log "Fetching LocalSend (AirDrop-like file sharing)"
if "$ROOT/scripts/fetch-localsend.sh" "$CACHE/localsend"; then
  deb="$CACHE/localsend/localsend.deb"
  pkg=$(dpkg-deb -f "$deb" Package); ver=$(dpkg-deb -f "$deb" Version); arch=$(dpkg-deb -f "$deb" Architecture)
  cp "$deb" "$WORK/config/packages.chroot/${pkg}_${ver//:/%3a}_${arch}.deb"
  install -D -m 644 "$CACHE/localsend/localsend.conf" "$OVL/usr/share/mangos/localsend.conf"
  echo "LocalSend package: $pkg $ver ($arch)"
else
  echo "WARNING: LocalSend could not be fetched and verified; the ISO will not include it." >&2
fi
# The MangOS system package (look, settings, tools, updater): installed in the
# image and published for web updates. Version: <MANGOS_VERSION>+<build id>.
PKG_VERSION="$MANGOS_VERSION+${MANGOS_BUILD_ID:-local$(date -u +%Y%m%d%H%M)}"
log "Building mangos-system $PKG_VERSION"
"$ROOT/scripts/build-system-deb.sh" "$OVL" "$WORK/config/packages.chroot" "$PKG_VERSION" \
  "$WORK/config/package-lists/mangos.list.chroot"
EXPECTED_PKGS="$EXPECTED_PKGS mangos-system"
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

# Every ArtCraft package that was downloaded, and mangos-system, must really be installed.
for pkg in $EXPECTED_PKGS; do
  if chroot chroot dpkg-query -W -f='${Status} ${Version}\n' "$pkg" 2>/dev/null | grep -q '^install ok installed'; then
    v=$(chroot chroot dpkg-query -W -f='${Version}' "$pkg")
    if [ "$pkg" = mangos-system ]; then echo "MangOS system installed: $v"; else echo "ArtCraft installed: $pkg $v"; fi
  else
    echo "ERROR: ArtCraft package $pkg was downloaded but is not installed in the image" >&2; exit 1
  fi
done

log "lb binary"
lb binary

ISO=$(ls -t "$WORK"/*.iso | head -1)
# Two images from the one live-build made: 64-bit EFI Macs (and PCs), and the
# 2006-2007 Macs with 32-bit EFI. Same system inside, different start-up files.
log "Making the amd64 and efi32 editions"
rm -f "$OUT"/MangOS-*.iso "$OUT"/MangOS-*.iso.sha256
"$ROOT/scripts/make-editions.sh" "$ISO" "$OUT" "$MANGOS_VERSION"
rm -f "$ISO"
NAME="MangOS-$MANGOS_VERSION-amd64.iso"
# Web update files (fixed names, so .../releases/latest/download/<name> works)
cp "$WORK/config/packages.chroot/mangos-system_${PKG_VERSION}_all.deb" "$OUT/mangos-system.deb"
echo "$PKG_VERSION" > "$OUT/mangos-system.version"
log "Done: $OUT/$NAME and $OUT/MangOS-$MANGOS_VERSION-efi32.iso"
cat "$OUT"/MangOS-*.iso.sha256
