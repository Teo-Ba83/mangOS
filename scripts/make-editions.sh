#!/bin/bash
# Makes the two MangOS images from the one live-build produces (which can
# start on every Intel Mac):
#   MangOS-<v>-amd64.iso   Macs with 64-bit EFI (late 2007 onwards) and PCs:
#                          64-bit EFI loader + BIOS, no 32-bit EFI parts
#   MangOS-<v>-efi32.iso   Macs with 32-bit EFI (2006-2007: MacBook2,1,
#                          MacBook Pro 2,x, iMac 5,x / 6,1, Mac mini 2,1,
#                          Mac Pro 1,1 / 2,1): 32-bit EFI loader + BIOS only
# Same system inside (the installed MangOS and its updates are identical);
# only the start-up files differ. xorriso replays the original boot setup
# (El Torito BIOS + EFI, isohybrid MBR, GPT, APM) with the edited EFI image.
#   usage: make-editions.sh <universal.iso> <out-dir> <version>
set -euo pipefail
SRC=$1; OUT=$2; VER=$3
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
mkdir -p "$OUT"

xorriso -osirrox on -indev "$SRC" -extract /boot/grub/efi.img "$T/efi.img" >/dev/null 2>&1
chmod u+w "$T/efi.img"
echo "EFI loaders in the universal image:"; mdir -b -i "$T/efi.img" ::EFI/boot

edition() { # name volume-suffix efi-files-to-drop iso-paths-to-drop
  local name=$1 suffix=$2 drop_efi=$3 drop_iso=$4
  cp "$T/efi.img" "$T/$name.img"
  for f in $drop_efi; do mdel -i "$T/$name.img" "::EFI/boot/$f" 2>/dev/null || true; done
  local rm_args=()
  for p in $drop_iso; do rm_args+=(-rm_r "$p" --); done
  local iso="$OUT/MangOS-$VER-$name.iso"
  rm -f "$iso"
  # (-return_with FAILURE: loaders absent from this image, e.g. no shim, are fine)
  xorriso -return_with FAILURE 32 -indev "$SRC" -outdev "$iso" -boot_image any replay \
    "${rm_args[@]}" -map "$T/$name.img" /boot/grub/efi.img \
    -volid "MangOS $VER$suffix" -commit >"$T/$name.log" 2>&1 ||
    { cat "$T/$name.log" >&2; exit 1; }
  echo "$(basename "$iso"): $(du -h "$iso" | cut -f1); EFI loaders: $(mdir -b -i "$T/$name.img" ::EFI/boot | xargs -n1 basename | tr '\n' ' ')"
  (cd "$OUT" && sha256sum "$(basename "$iso")" > "$(basename "$iso").sha256")
}

# 64-bit EFI and BIOS: drop the 32-bit EFI loader and its GRUB modules
edition amd64 "" "bootia32.efi" "/EFI/boot/bootia32.efi /boot/grub/i386-efi"
# 32-bit EFI Macs: only the 32-bit EFI loader (BIOS kept for Boot Camp starts)
edition efi32 " EFI32" "bootx64.efi grubx64.efi mmx64.efi" \
  "/EFI/boot/bootx64.efi /EFI/boot/grubx64.efi /EFI/boot/mmx64.efi /boot/grub/x86_64-efi"
