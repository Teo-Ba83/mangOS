#!/bin/sh
# Generates the original MangOS wallpapers (light + dark) as SVG, and renders
# PNGs when an output directory is given. Abstract soft waves in mango colours.
set -e
HERE=$(cd "$(dirname "$0")/.." && pwd)
SRC="$HERE/branding/wallpapers"
mkdir -p "$SRC"

wall() { # name bg1 bg2 c1 c2 c3 c4 opacity
cat > "$SRC/$1.svg" <<EOF
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2560 1600" width="2560" height="1600">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="$2"/><stop offset="1" stop-color="$3"/>
    </linearGradient>
    <linearGradient id="w1" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="$4"/><stop offset="1" stop-color="$5"/>
    </linearGradient>
    <linearGradient id="w2" x1="0" y1="0" x2="1" y2="0.4">
      <stop offset="0" stop-color="$5"/><stop offset="1" stop-color="$6"/>
    </linearGradient>
    <linearGradient id="w3" x1="0" y1="1" x2="1" y2="0">
      <stop offset="0" stop-color="$6"/><stop offset="1" stop-color="$7"/>
    </linearGradient>
    <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="28"/></filter>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="160"/></filter>
  </defs>
  <rect width="2560" height="1600" fill="url(#bg)"/>
  <ellipse cx="1900" cy="380" rx="760" ry="420" fill="$5" opacity="0.22" filter="url(#glow)"/>
  <g filter="url(#soft)" opacity="$8">
    <path d="M-500 1050 C 400 820 900 1180 1400 980 C 1850 800 2200 760 3100 900 L 3100 2000 L -500 2000 Z" fill="url(#w1)"/>
    <path d="M-500 1220 C 500 1000 1000 1330 1550 1160 C 1980 1030 2300 1050 3100 1150 L 3100 2000 L -500 2000 Z" fill="url(#w2)" opacity="0.9"/>
    <path d="M-500 1400 C 600 1230 1150 1500 1700 1360 C 2100 1260 2400 1300 3100 1380 L 3100 2000 L -500 2000 Z" fill="url(#w3)" opacity="0.85"/>
  </g>
</svg>
EOF
}
#     name          bg1      bg2      c1       c2       c3       c4       opacity
wall mangos-light  '#FFF8EC' '#FFE3C2' '#FFD23F' '#FF9F1C' '#FF6B3D' '#F2542D' 0.85
wall mangos-dark   '#141428' '#2A1B3D' '#7A3B69' '#FF9F1C' '#EF4A2E' '#6B2D5C' 0.80

if [ -n "$1" ]; then
  mkdir -p "$1"
  for w in mangos-light mangos-dark; do
    # Render oversized and crop the centre: blur filters fade at the canvas edge.
    rsvg-convert -w 2240 -h 1400 "$SRC/$w.svg" -o "$1/$w.tmp.png"
    convert "$1/$w.tmp.png" -crop 1920x1200+160+100 +repage "$1/$w.png"
    rm -f "$1/$w.tmp.png"
  done
fi
