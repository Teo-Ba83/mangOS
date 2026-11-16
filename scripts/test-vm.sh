#!/bin/bash
# Boots the ISO in QEMU before trying it on the Mac (section 6).
#   scripts/test-vm.sh bios   [iso]   legacy BIOS (Mac Boot Camp/CSM path)
#   scripts/test-vm.sh uefi   [iso]   64-bit UEFI (OVMF)
#   scripts/test-vm.sh uefi32 [iso]   32-bit UEFI, like the 2007 MacBook firmware
#   scripts/test-vm.sh install [iso]  64-bit UEFI with an empty 20 GB disk
# Extra QEMU options can be appended through QEMU_EXTRA.
set -euo pipefail
mode=${1:-uefi}; iso=${2:-$(ls -t "$(dirname "$0")"/../out/*.iso | head -1)}
disk=${DISK:-/var/tmp/mangos-test.qcow2}
common=(-m 4096 -smp 2 -cpu core2duo -vga std -device intel-hda -device hda-duplex
        -netdev user,id=n0 -device e1000,netdev=n0 -usb -device usb-tablet
        -cdrom "$iso" -boot d)
find_fw() { for f in "$@"; do [ -e "$f" ] && { echo "$f"; return; }; done; echo "missing firmware: $*" >&2; exit 1; }
case "$mode" in
  bios)   exec qemu-system-x86_64 -enable-kvm "${common[@]}" ${QEMU_EXTRA:-} 2>/dev/null || \
          exec qemu-system-x86_64 "${common[@]}" ${QEMU_EXTRA:-} ;;
  uefi|install)
    code=$(find_fw /usr/share/OVMF/OVMF_CODE_4M.fd /usr/share/OVMF/OVMF_CODE.fd)
    vars=/var/tmp/mangos-ovmf-vars.fd; [ -e "$vars" ] || cp "$(dirname "$code")/OVMF_VARS_4M.fd" "$vars" 2>/dev/null || cp "$(dirname "$code")/OVMF_VARS.fd" "$vars"
    extra=()
    if [ "$mode" = install ]; then
      [ -e "$disk" ] || qemu-img create -f qcow2 "$disk" 20G >/dev/null
      extra=(-drive file="$disk",if=virtio)
    fi
    exec qemu-system-x86_64 -machine q35 "${common[@]}" "${extra[@]}" \
      -drive if=pflash,format=raw,readonly=on,file="$code" -drive if=pflash,format=raw,file="$vars" ${QEMU_EXTRA:-} ;;
  uefi32)
    # 32-bit OVMF (Debian package ovmf-ia32) running a 64-bit CPU = Mac EFI32
    code=$(find_fw /usr/share/OVMF/OVMF32_CODE_4M.fd)
    vars=/var/tmp/mangos-ovmf32-vars.fd; [ -e "$vars" ] || cp /usr/share/OVMF/OVMF32_VARS_4M.fd "$vars"
    exec qemu-system-x86_64 -machine q35 "${common[@]}" \
      -drive if=pflash,format=raw,readonly=on,file="$code" -drive if=pflash,format=raw,file="$vars" ${QEMU_EXTRA:-} ;;
  *) echo "usage: $0 bios|uefi|uefi32|install [iso]" >&2; exit 2 ;;
esac
