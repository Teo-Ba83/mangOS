#!/bin/bash
# Builds the mangos-system package from the generated chroot overlay and
# leaves only the live-session/installer files in the overlay.
#   usage: build-system-deb.sh <overlay> <out-dir> <version> <package-list>
# The package holds everything that makes the system "MangOS" (themes,
# settings, tools, Wi-Fi setup, updater) and depends on the Debian packages
# of the image, so a web update can also bring in new packages.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
. "$HERE/versions.env"
OVL=$1; OUT=$2; VER=$3; LIST=$4
STAGE=$(mktemp -d); trap 'rm -rf "$STAGE"' EXIT

# Installer / live-only files stay in the overlay (they are owned by other
# packages or removed from the installed system).
LIVE_ONLY='etc/calamares usr/lib/calamares usr/bin/install-mangos usr/share/applications/install-mangos.desktop'
rsync -a "$OVL/" "$STAGE/"
for p in $LIVE_ONLY; do rm -rf "$STAGE/$p"; done
rm -f "$STAGE"/usr/lib/mangos/calamares-*

mkdir -p "$STAGE/etc/mangos"
cat > "$STAGE/etc/mangos/updates.conf" <<CONF
# MangOS web updates (managed by the mangos-system package).
# Stable channel: the release marked "latest" (only builds promoted to stable).
MANGOS_UPDATES_URL=https://github.com/$MANGOS_UPDATES_REPO/releases/latest/download
# Beta channel: every build (rolling "beta" release). Chosen per computer in
# /etc/mangos/update-channel (Settings > Software Update).
MANGOS_UPDATES_BETA_URL=https://github.com/$MANGOS_UPDATES_REPO/releases/download/beta
# Each build's own release (tag v<version>-build.<n>), for going back one version.
MANGOS_RELEASES_URL=https://github.com/$MANGOS_UPDATES_REPO/releases/download
# Only packages signed by this GitHub Actions workflow are installed.
MANGOS_SIGNER_IDENTITY_REGEX='^https://github\\.com/$MANGOS_SOURCE_REPO/\\.github/workflows/build-iso\\.yml@refs/heads/'
MANGOS_SIGNER_ISSUER=https://token.actions.githubusercontent.com
# Set to "no" to stop automatic installation (Settings > Software Update still works).
MANGOS_AUTO_UPDATE=yes
CONF

# When this build was made: "What's new" after an update shows the changes
# written after the build the computer had before.
printf 'VERSION=%s\nBUILD_TIME=%s\n' "$VER" "$(date -u +%Y-%m-%dT%H:%M:%S)" > "$STAGE/usr/share/mangos/build-info"

# Depends: the image's packages, minus the live-session and installer tools
# that the installer removes from the installed system.
EXCLUDE=' live-boot live-config live-config-systemd live-tools user-setup calamares calamares-settings-debian squashfs-tools '
deps=$(grep -hv '^\s*#' $LIST | awk 'NF{print $1}' | sort -u | while read -r p; do
  case "$p" in qml6-*) continue;; esac
  case "$EXCLUDE" in *" $p "*) ;; *) echo "$p";; esac; done | paste -sd, - | sed 's/,/, /g')

mkdir -p "$STAGE/DEBIAN"
cat > "$STAGE/DEBIAN/control" <<CTL
Package: mangos-system
Version: $VER
Architecture: all
Maintainer: MangOS project <mangos@users.noreply.github.com>
Section: misc
Priority: optional
Depends: $deps
Description: MangOS system: look, settings, tools and web updates
 Everything that turns Debian into MangOS: WhiteSur themes, logo and
 wallpapers, desktop defaults, Launchpad, Mac keyboard and trackpad
 settings, Broadcom Wi-Fi setup, and the signed web updater.
CTL
install -m755 "$HERE/../packaging/mangos-system/postinst" "$STAGE/DEBIAN/postinst"
install -m755 "$HERE/../packaging/mangos-system/preinst" "$STAGE/DEBIAN/preinst"

mkdir -p "$OUT"
DEB="$OUT/mangos-system_${VER}_all.deb"
dpkg-deb --root-owner-group -Zxz -b "$STAGE" "$DEB" >/dev/null
echo "mangos-system $VER: $(du -h "$DEB" | cut -f1)"

# Leave only the live-only files in the overlay.
KEEP=$(mktemp -d)
for p in $LIVE_ONLY; do
  [ -e "$OVL/$p" ] && { mkdir -p "$KEEP/$(dirname "$p")"; cp -a "$OVL/$p" "$KEEP/$p"; }
done
mkdir -p "$KEEP/usr/lib/mangos"; cp -a "$OVL"/usr/lib/mangos/calamares-* "$KEEP/usr/lib/mangos/" 2>/dev/null || true
rm -rf "$OVL"; mv "$KEEP" "$OVL"; chmod 755 "$OVL"
