# MangOS test log

Every step of the spec needs evidence before it counts as done. This file
records what was tested, how, and the result. Screenshots are in
[`screenshots/`](screenshots/).

**Final ISO tested:** `MangOS-0.1.0-amd64.iso`, 1.37 GB, sha256
`8a354916e1add11d0933e9c93d1c4982c270bbe05922822f2226ff64d4e18ec4`
(built without ArtCraft, see 4.2). The full installation test (5.1/5.2) ran
on an earlier build. Changes since then (language switch, polkit agent,
look fixes, and removing the "Install MangOS" launcher in the installer's
last step) were tested in the live session but not through another full
install.

**Test environment:** QEMU 8.2 (software emulation, no KVM), `-cpu core2duo`,
4 GB RAM, `-vga std`. Firmware: OVMF **32-bit** (`OVMF32_CODE_4M.fd`, same
firmware class as the MacBook A1181), OVMF 64-bit, and SeaBIOS (legacy BIOS).
**Nothing in this file was tested on the real MacBook yet.**

Legend: ✅ passed in VM · ⚠️ passed with a known limit · ❌ not working ·
⏳ not tested yet (needs the real Mac or the ArtCraft packages)

| Step | What | Result | Evidence |
|---|---|---|---|
| 1.1 | Build environment (Debian 13 chroot, live-build 20250505) | ✅ | `scripts/buildenv.sh`; full builds 8-14 succeeded |
| 1.2 | ISO boots from 64-bit UEFI | ✅ | [live desktop](screenshots/30-uefi64-live-desktop.png) |
| 1.2 | ISO boots from legacy BIOS (Mac "Windows" boot entry) | ✅ | [boot menu](screenshots/02-bios-boot-menu.png) · [live desktop, final ISO](screenshots/29-final-bios-live-desktop.png) |
| 1.2 | Boot from USB on the MacBook (Option key) | ⏳ | needs hardware |
| 1.3 | 32-bit EFI loader (`EFI/boot/bootia32.efi`) on the ISO | ✅ | [32-bit EFI boot menu](screenshots/01-efi32-boot-menu.png) |
| 1.3 | Live system starts on 32-bit EFI | ✅ | needs `efi=noruntime`, added automatically (see below) · [splash](screenshots/03-boot-splash.png) · [desktop, final ISO](screenshots/27-final-efi32-live-desktop.png) |
| 2.1 | English default, Italian included | ✅ | [installer in Italian](screenshots/10-installer-welcome-it.png) |
| 2.2 | Change language without reinstalling | ✅ | final ISO on 32-bit EFI: [Settings](screenshots/31-settings.png) > Language > Italiano, log out/in → [desktop in Italian](screenshots/28-final-language-italian.png) |
| 3.1 | XFCE + Plank + WhiteSur | ✅ | [desktop](screenshots/05-live-desktop-v1.png) |
| 3.2 | Top bar, logo menu, global menu | ✅ | [logo menu](screenshots/07-logo-menu.png) · [global menu](screenshots/25-global-menu.png) |
| 3.3 | Launchpad (dock icon, Cmd+Space/F4) | ✅ | [light](screenshots/06-launchpad-v1.png) · [dark, apps only](screenshots/24-launchpad-dark.png) |
| 3.3 | Mac shortcuts (keyd) and trackpad | ⏳ | keyd service starts at boot; key behaviour and trackpad need the real keyboard/trackpad |
| 3.4 | Defaults for every new user | ✅ | the user created by the installer got the full look and the welcome window |
| 4.1 | Firefox ESR, VLC, Thunar, terminal, NetworkManager, PipeWire, CUPS, unattended-upgrades | ✅ | in the image; dock and Launchpad entries |
| 4.2 | ArtCraft `.deb`s downloaded and SHA-256 checked | ⏳ | `scripts/fetch-artcraft.sh` is in place, but the build machine could not reach GitHub releases, so the test ISOs were built **without** ArtCraft |
| 4.3 | WordCraft, PdfCraft, PhotoCraft start | ⏳ | needs an ISO built with network access to GitHub |
| 5.1 | Calamares install in a VM (32-bit EFI, empty 20 GB disk) | ✅ | [welcome](screenshots/11-installer-1-welcome.png) → [location](screenshots/12-installer-2-location.png) → [keyboard](screenshots/13-installer-3-keyboard.png) → [disk](screenshots/14-installer-4-disk.png) → [user](screenshots/15-installer-5-user.png) → [summary](screenshots/16-installer-6-summary.png) → [confirm](screenshots/17-installer-7-confirm.png) → [slideshow](screenshots/18-installer-8-slideshow.png) → [done](screenshots/19-installer-9-done.png) |
| 5.2 | Installed system starts by itself | ✅ in VM | 32-bit EFI with empty NVRAM boots `EFI/boot/bootia32.efi` → [login](screenshots/21-installed-efi32-login.png) · [ESP contents](screenshots/20-installed-esp-bootia32.png) |
| 5.2 | Installation on the real MacBook | ⏳ | needs hardware |
| 5   | First start: light/dark + network check | ✅ | [welcome](screenshots/22-first-start-welcome.png) · [dark](screenshots/23-dark-mode.png) |
| 5.3 | Installer theme, English and Italian | ✅ | [EN](screenshots/09-installer-welcome-en.png) · [IT](screenshots/10-installer-welcome-it.png) |
| 5b.1 | Logo SVG + variants 16-512 px | ✅ | [variants](screenshots/00-logo-variants.png) |
| 5b.2 | Logo in top bar, installer, Plymouth, login, About, Launchpad, boot menu | ✅ | see screenshots above · [About](screenshots/08-about.png) · [login](screenshots/26-login-dark.png) |

## Problems found by testing, and what was done

| Found | Fix |
|---|---|
| live-build puts no `bootia32.efi` on amd64 ISOs unless signed GRUB is used, and even then its check reads out-of-scope variables | `config/hooks/live/0500-mangos-efi-ia32.hook.binary` builds and adds it |
| On 32-bit EFI the 64-bit kernel panics at once ("kernel tried to execute NX-protected page") when calling the firmware's runtime services (EFI mixed mode) | `efi=noruntime` is added automatically when GRUB runs on 32-bit EFI (live ISO), and to the installed system's GRUB config on 32-bit EFI |
| Debian's Calamares helper always installs `grub-efi` (64-bit) | `usr/lib/mangos/calamares-bootloader-config` installs `grub-efi-ia32`, `grub-efi-amd64` or `grub-pc` from `.debs` on the ISO, offline; no NVRAM writes on EFI32 |
| Live user not created (`user-setup` is only a Recommends) | added `user-setup`, `live-tools` |
| `firmware-b43legacy-installer` (pulled by automatic firmware detection) needs internet during the build | explicit firmware list instead |
| Light theme: white top-bar text on a light bar | WhiteSur built with `--black` |
| Language choice overwritten at login | normalized locale name, no language picker on the greeter, `~/.xsessionrc` |
| `pkexec` asked for the password in a terminal | mate-polkit agent autostarted |
| Live session locked itself during a long install | no lock/blank in the live session |
| OVMF kept stale boot entries and preferred its EFI shell over the new disk | test artefact of the VM's saved NVRAM; with empty NVRAM it boots the disk. Macs have no EFI shell |

## How to repeat the tests

```sh
sudo scripts/buildenv.sh build                 # builds out/MangOS-*.iso
scripts/test-vm.sh uefi32                      # 32-bit EFI (apt install ovmf-ia32)
scripts/test-vm.sh bios
DISK=/var/tmp/t.qcow2 scripts/test-vm.sh install
```
