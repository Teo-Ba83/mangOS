# Writing MangOS to a USB stick and booting the MacBook

## 1. Check the download

```sh
sha256sum -c MangOS-0.2.0-amd64.iso.sha256
```
It must print `MangOS-0.2.0-amd64.iso: OK`.

## 2. Write the ISO to a USB stick (4 GB or bigger, it will be erased)

**Linux**
```sh
lsblk                                   # find the stick, e.g. /dev/sdb (not a partition like sdb1)
sudo dd if=MangOS-0.2.0-amd64.iso of=/dev/sdX bs=4M status=progress conv=fsync
```

**macOS**
```sh
diskutil list                           # find the stick, e.g. /dev/disk4
diskutil unmountDisk /dev/disk4
sudo dd if=MangOS-0.2.0-amd64.iso of=/dev/rdisk4 bs=4m
```

**Windows / any system:** use [balenaEtcher](https://etcher.balena.io) or
Rufus in "DD image" mode.

## 3. Boot the MacBook (A1181, 2006-2008)

1. Plug in the stick and switch the Mac on while holding **Option (⌥)**.
2. The boot picker shows the stick as **EFI Boot** and sometimes also as
   **Windows** (the legacy BIOS path).
   - Try **EFI Boot** first: MangOS ships a 32-bit EFI loader (`BOOTIA32.EFI`)
     for these Macs.
   - If that shows a black screen or returns to the picker, restart and choose
     **Windows** instead.
3. The MangOS logo appears, then the live desktop starts (user `mangos`,
   no password).
4. Check the Wi-Fi: double-click **Wi-Fi Check** on the desktop. It prints
   `lspci -nn` and the Wi-Fi state and saves them to `~/mangos-wifi-check.txt`
   (the same check also runs at boot: `journalctl -u mangos-wifi-check`).
   If the Broadcom card shows no wireless interface, restart and choose
   **MangOS (Wi-Fi: b43 driver)** in the boot menu.
5. To install, double-click **Install MangOS** on the desktop. The driver
   choice is kept: on the installed system switch with
   `sudo mangos-wifi-driver b43` or `sudo mangos-wifi-driver wl`.

The installer works out which firmware the Mac booted with (BIOS, 32-bit EFI,
64-bit EFI) and installs the matching GRUB, including the fallback file
`/EFI/BOOT/BOOTIA32.EFI` that 32-bit Mac firmware looks for. After
installing, the Mac should start MangOS on its own; if it does not, hold
Option and pick **EFI Boot** once, then set it as the default in macOS/rEFInd
or with *Startup Disk*.
