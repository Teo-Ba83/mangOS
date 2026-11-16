#!/bin/bash
# Step 1.1: creates a Debian 13 (trixie) build environment with everything
# build.sh needs, then (optionally) runs the build inside it.
#
#   sudo scripts/buildenv.sh            create/update /srv/mangos-buildenv
#   sudo scripts/buildenv.sh build      ... and run ./build.sh inside it
#   sudo scripts/buildenv.sh build --clean
#
# On a Debian trixie host you can skip the chroot: install BUILD_PACKAGES
# below with apt and run ./build.sh directly.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
ENV=${MANGOS_BUILDENV:-/srv/mangos-buildenv}
MIRROR=${DEBIAN_MIRROR:-https://deb.debian.org/debian}
BUILD_PACKAGES="live-build debootstrap dctrl-tools xorriso git ca-certificates curl wget rsync
 cpio zstd squashfs-tools mtools dosfstools
 grub-common grub-pc-bin grub-efi-amd64-bin grub-efi-ia32-bin grub-efi-amd64-signed shim-signed
 syslinux syslinux-common isolinux syslinux-efi
 librsvg2-bin imagemagick gtk-update-icon-cache b43-fwcutter bzip2 sassc libglib2.0-dev-bin libxml2-utils sudo python3"

[ "$(id -u)" = 0 ] || { echo "run as root" >&2; exit 1; }
command -v debootstrap >/dev/null || { echo "install debootstrap first" >&2; exit 1; }

if [ ! -x "$ENV/usr/bin/apt-get" ]; then
  debootstrap --variant=minbase --include=ca-certificates trixie "$ENV" "$MIRROR"
fi
echo "deb $MIRROR trixie main contrib non-free non-free-firmware" > "$ENV/etc/apt/sources.list"
cp -L /etc/resolv.conf "$ENV/etc/resolv.conf"
if [ -n "${MANGOS_BUILD_CA:-}" ]; then
  install -D -m644 "$MANGOS_BUILD_CA" "$ENV/usr/local/share/ca-certificates/mangos-build-ca.crt"
  chroot "$ENV" update-ca-certificates >/dev/null
  cp "$MANGOS_BUILD_CA" "$ENV/build-ca.crt"
fi

mounts=()
cleanup() { for ((i=${#mounts[@]}-1; i>=0; i--)); do umount -l "${mounts[$i]}" 2>/dev/null || true; done; }
trap cleanup EXIT
for d in proc sys dev dev/pts; do
  mountpoint -q "$ENV/$d" || { mount --bind "/$d" "$ENV/$d"; mounts+=("$ENV/$d"); }
done
mkdir -p "$ENV/mangos"
mountpoint -q "$ENV/mangos" || { mount --bind "$ROOT" "$ENV/mangos"; mounts+=("$ENV/mangos"); }

PROXY_ENV="http_proxy=${http_proxy:-} https_proxy=${https_proxy:-} HTTPS_PROXY=${HTTPS_PROXY:-}"
chroot "$ENV" env $PROXY_ENV DEBIAN_FRONTEND=noninteractive sh -c \
  "apt-get update -q && apt-get install -y -q --no-install-recommends $(echo $BUILD_PACKAGES)"

if [ "${1:-}" = build ]; then
  shift
  CA_ENV=""; [ -n "${MANGOS_BUILD_CA:-}" ] && CA_ENV="MANGOS_BUILD_CA=/build-ca.crt"
  chroot "$ENV" env $PROXY_ENV $CA_ENV \
    MANGOS_APT_PROXY="${MANGOS_APT_PROXY:-}" MANGOS_SKIP_ARTCRAFT="${MANGOS_SKIP_ARTCRAFT:-0}" MANGOS_REQUIRE_ARTCRAFT="${MANGOS_REQUIRE_ARTCRAFT:-0}" \
    MANGOS_WORK=/mangos/build /mangos/build.sh "$@"
fi
