#!/bin/sh
# Generates the MangOS logo PNG sizes, the Launchpad icon, installer slides,
# and installs everything into the image. Artwork: a glossy mango with a bite,
# a stem and a leaf (mangos-logo-full-source.png, see import-logo.py).
set -e
cd "$(dirname "$0")"
# mangos-logo.svg, mangos-logo-mono-*.svg and mangos-logo-symbolic.svg are made
# from the artwork mangos-logo-full-source.png by import-logo.py (committed).
rm -rf png; mkdir -p png
for s in 16 22 24 32 48 64 128 256 512; do
  for v in mangos-logo mangos-logo-mono-dark mangos-logo-mono-light; do
    rsvg-convert -w $s -h $s $v.svg -o png/$v-$s.png
  done
done

# ---------------------------------------------------------------------------
# Launchpad icon: rounded square with a 3x3 app grid, the mango in the middle.
MANGO_INNER=$(sed -n '/<defs>/,/<\/svg>/p' mangos-logo.svg | sed '$d' | sed 's/id="fruit"/id="lpfruit"/; s/url(#fruit)/url(#lpfruit)/; s/id="shine"/id="lpshine"/; s/url(#shine)/url(#lpshine)/; s/id="leaf"/id="lpleaf"/; s/url(#leaf)/url(#lpleaf)/; s/id="bite"/id="lpbite"/; s/url(#bite)/url(#lpbite)/')
tile() { echo "<rect x=\"$1\" y=\"$2\" width=\"92\" height=\"92\" rx=\"24\" fill=\"$3\"/>"; }
cat > mangos-launchpad.svg <<EOF
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <title>Launchpad</title>
  <defs>
    <linearGradient id="lpbg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#5E5E66"/><stop offset="1" stop-color="#2C2C30"/>
    </linearGradient>
  </defs>
  <rect x="24" y="24" width="464" height="464" rx="104" fill="url(#lpbg)"/>
  $(tile 98 98 '#FF6B3D') $(tile 210 98 '#FFD23F') $(tile 322 98 '#34C759')
  $(tile 98 210 '#0A84FF')                         $(tile 322 210 '#AF52DE')
  $(tile 98 322 '#FF9F1C') $(tile 210 322 '#5AC8FA') $(tile 322 322 '#FF375F')
  <svg x="198" y="198" width="116" height="116" viewBox="0 0 512 512">
  $MANGO_INNER
  </svg>
</svg>
EOF

# Installer slideshow pictures.
cat > slide-artcraft.svg <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <g font-family="Inter, sans-serif" font-weight="700" font-size="64" text-anchor="middle" fill="#fff">
    <rect x="20" y="120" width="110" height="110" rx="26" fill="#2B7CFF"/><text x="75" y="198">W</text>
    <rect x="145" y="120" width="110" height="110" rx="26" fill="#E5383B"/><text x="200" y="198">P</text>
    <rect x="270" y="120" width="110" height="110" rx="26" fill="#7B4DFF"/><text x="325" y="198">Ph</text>
  </g>
  <g font-family="Inter, sans-serif" font-size="20" text-anchor="middle" fill="#6E6E73">
    <text x="75" y="262">WordCraft</text><text x="200" y="262">PdfCraft</text><text x="325" y="262">PhotoCraft</text>
  </g>
</svg>
EOF
cat > slide-appearance.svg <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <defs><clipPath id="l"><rect x="0" y="0" width="200" height="400"/></clipPath>
        <clipPath id="r"><rect x="200" y="0" width="200" height="400"/></clipPath></defs>
  <circle cx="200" cy="200" r="150" fill="#FFF3DE" clip-path="url(#l)" stroke="#E5E5EA" stroke-width="4"/>
  <circle cx="200" cy="200" r="150" fill="#1D1D2E" clip-path="url(#r)"/>
  <circle cx="130" cy="150" r="34" fill="#FFB020"/>
  <path d="M290 120 a44 44 0 1 0 30 74 a36 36 0 1 1 -30 -74z" fill="#F5F5F7"/>
</svg>
EOF
cat > slide-secure.svg <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <defs><linearGradient id="s" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FFB547"/><stop offset="1" stop-color="#F2542D"/></linearGradient></defs>
  <path d="M200 40 L330 90 V190 C330 280 270 335 200 362 C130 335 70 280 70 190 V90 Z" fill="url(#s)"/>
  <path d="M140 200 L185 245 L265 160" fill="none" stroke="#fff" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
EOF

# ---------------------------------------------------------------------------
# Install into a chroot overlay when one is given (used by build.sh).
DEST=${1:-}
[ -n "$DEST" ] || exit 0
L=$DEST/usr/share/mangos/logo
mkdir -p "$L"
cp mangos-logo*.svg mangos-launchpad.svg mangos-logo-full.png "$L/"
cp png/*.png "$L/"
for s in 16 22 24 32 48 64 128 256 512; do
  d=$DEST/usr/share/icons/hicolor/${s}x${s}/apps; mkdir -p "$d"
  cp png/mangos-logo-$s.png "$d/mangos-logo.png"
  cp png/mangos-logo-$s.png "$d/install-mangos.png"
  rsvg-convert -w $s -h $s mangos-launchpad.svg -o "$d/mangos-launchpad.png"
  rsvg-convert -w $s -h $s mangos-store.svg -o "$d/mangos-store.png"
done
d=$DEST/usr/share/icons/hicolor/scalable/apps; mkdir -p "$d"
cp mangos-logo.svg "$d/mangos-logo.svg"
cp mangos-logo.svg "$d/install-mangos.svg"
cp mangos-launchpad.svg "$d/mangos-launchpad.svg"
cp mangos-store.svg "$d/mangos-store.svg"
cp mangos-logo-symbolic.svg "$d/mangos-logo-symbolic.svg"
mkdir -p "$DEST/usr/share/pixmaps"
cp png/mangos-logo-128.png "$DEST/usr/share/pixmaps/mangos-logo.png"
cp png/mangos-logo-128.png "$DEST/usr/share/pixmaps/install-mangos.png"

# Plymouth boot splash
P=$DEST/usr/share/plymouth/themes/mangos; mkdir -p "$P"
rsvg-convert -w 160 -h 160 mangos-logo.svg -o "$P/logo.png"
convert -size 220x6 xc:none -fill '#3A3A3E' -draw 'roundrectangle 0,0 219,5 3,3' "$P/progress-bg.png"
convert -size 220x6 xc:none -fill '#F5F5F7' -draw 'roundrectangle 0,0 219,5 3,3' "$P/progress-fg.png"
convert -size 10x10 xc:none -fill '#F5F5F7' -draw 'circle 5,5 5,1' "$P/bullet.png"
convert -size 260x34 xc:none -fill '#2C2C30' -stroke '#4A4A50' -draw 'roundrectangle 0,0 259,33 10,10' "$P/entry.png"

# Calamares branding images
C=$DEST/etc/calamares/branding/mangos; mkdir -p "$C"
cp png/mangos-logo-128.png "$C/logo.png"
cp png/mangos-logo-64.png "$C/icon.png"
cp png/mangos-logo-512.png "$C/welcome.png"
for s in slide-artcraft slide-appearance slide-secure; do
  rsvg-convert -w 400 -h 400 $s.svg -o "$C/$s.png"
done
echo "Logo assets installed into $DEST"
