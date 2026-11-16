#!/bin/bash
# Builds the WhiteSur GTK/xfwm4/Plank theme, icons and cursors from pinned
# sources and installs them into the given chroot overlay directory.
#   usage: fetch-themes.sh <overlay-root> <cache-dir>
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
. "$HERE/versions.env"
DEST=$1; CACHE=$2
mkdir -p "$CACHE" "$DEST/usr/share/themes" "$DEST/usr/share/icons" "$DEST/usr/share/plank/themes"

checkout() { # repo ref dir
  if [ ! -d "$3/.git" ]; then git clone -q "$1" "$3"; fi
  git -C "$3" fetch -q --depth 1 origin "$2" 2>/dev/null || git -C "$3" fetch -q origin
  git -C "$3" checkout -q --force "$2"
}

checkout "$WHITESUR_GTK_REPO"    "$WHITESUR_GTK_REF"    "$CACHE/WhiteSur-gtk-theme"
checkout "$WHITESUR_ICON_REPO"   "$WHITESUR_ICON_REF"   "$CACHE/WhiteSur-icon-theme"
checkout "$WHITESUR_CURSOR_REPO" "$WHITESUR_CURSOR_REF" "$CACHE/WhiteSur-cursors"

# The WhiteSur installer insists on a user name and on sudo existing.
export HOME=${HOME:-/root} USER=${USER:-root} SUDO_USER=${SUDO_USER:-root}

TMP=$(mktemp -d)
( cd "$CACHE/WhiteSur-gtk-theme" && ./install.sh -d "$TMP/themes" -c light -c dark --black >/dev/null )
for t in WhiteSur-Light WhiteSur-Dark; do
  rm -rf "$DEST/usr/share/themes/$t"
  cp -a "$TMP/themes/$t" "$DEST/usr/share/themes/"
  # Unused desktops: keep the image lean.
  rm -rf "$DEST/usr/share/themes/$t"/{cinnamon,gnome-shell,unity,labwc}
  # Plank theme shipped with WhiteSur
  if [ -d "$DEST/usr/share/themes/$t/plank" ]; then
    rm -rf "$DEST/usr/share/plank/themes/$t"
    cp -a "$DEST/usr/share/themes/$t/plank" "$DEST/usr/share/plank/themes/$t"
  fi
done

( cd "$CACHE/WhiteSur-icon-theme" && ./install.sh -d "$TMP/icons" -t default >/dev/null )
for t in WhiteSur WhiteSur-light WhiteSur-dark; do
  rm -rf "$DEST/usr/share/icons/$t"; cp -a "$TMP/icons/$t" "$DEST/usr/share/icons/"
done

rm -rf "$DEST/usr/share/icons/WhiteSur-cursors"
cp -a "$CACHE/WhiteSur-cursors/dist" "$DEST/usr/share/icons/WhiteSur-cursors"

rm -rf "$TMP"
echo "WhiteSur themes installed into $DEST"
