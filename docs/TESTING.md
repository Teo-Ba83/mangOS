# MangOS test log

Every step of the spec needs evidence before it counts as done. This file
records what was tested, how, and the result. Screenshots are in
[`screenshots/`](screenshots/).

**Final ISO tested:** `MangOS-0.1.0-amd64.iso`, 1.45 GB, sha256
`3c2d1e2bfc73275b8f9172879088294a0cfd5bf04241813b51faccc013b7742e`
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
| 3.3 | Two-finger scroll speed on the real trackpad | ✅ on hardware | default libinput speed scrolled ~5 lines for a tiny movement; `ScrollPixelDistance 50` tested good on the MacBook4,1, now the default |
| 3.3 | Mac shortcuts (keyd) and trackpad | ⏳ | keyd service starts at boot; key behaviour and trackpad need the real keyboard/trackpad |
| 3.4 | Defaults for every new user | ✅ | the user created by the installer got the full look and the welcome window |
| Wi-Fi | `wl` (broadcom-sta-dkms) built for the ISO kernel during the build, offline | ✅ | build fails if `wl.ko` is missing; in the VM `modprobe wl` loads it ([log](screenshots/36-wl-loaded-warning.png): "Unpatched return thunk" warning is harmless) |
| Wi-Fi | Conflicting drivers blacklisted (b43, b43legacy, ssb, bcma, brcmsmac, brcm80211, b44) | ✅ | [check output](screenshots/33-wifi-check-lspci.png) |
| Wi-Fi | b43 + firmware as reserve (boot entry, `mangos-wifi-driver`) | ✅ | [boot menu](screenshots/32-wifi-boot-menu-b43.png) → b43/bcma/ssb loaded at boot, 155 firmware files ([state](screenshots/34-wifi-check-state-b43.png)); runtime switch both ways ([terminal](screenshots/35-wifi-driver-switch.png)) |
| Wi-Fi | Live check printing `lspci -nn` and the Wi-Fi state | ✅ | [desktop icon](screenshots/38-live-desktop-wifi-icon.png) · [report](screenshots/33-wifi-check-lspci.png) · [runs at boot](screenshots/37-wifi-check-at-boot.png) |
| Wi-Fi | Real BCM4321 association with an access point | ⚠️ on hardware | MacBook4,1 (early 2008) with `wl`: phone hotspot always works; Virgin hub (dual-band) works on 2.4 GHz only, 5 GHz associates but gets no DHCP address; fixed by the 2.4 GHz lock (build 13/14) and removing duplicate saved profiles. Mesh extender: connects only the first time, not solved |
| Store | MangOS Store with the real Debian catalog (2,100 apps, icons, Italian descriptions) | ✅ | tested on the image's system with a virtual display: [Discover](screenshots/40-store-discover.png) · [Create](screenshots/41-store-create.png) · [search](screenshots/42-store-search.png) · [app page, Italian](screenshots/44-store-app-page-it.png) · [Updates](screenshots/43-store-updates.png) · [icon](screenshots/39-store-icon.png) |
| Store | Mango Store redesign: logo + name, uniform rounded icon tiles, GET/OPEN pills with a progress ring, sliding banner (ArtCraft + 3 apps of the week, auto-advance, pauses under the pointer) | ✅ in VM (real Debian catalog; popcon blocked in the sandbox, so the fallback suggestions were shown) | [Discover](screenshots/55-mango-store-discover-it.png) · [banner on an app of the week](screenshots/56-mango-store-week-banner-it.png) · [app page](screenshots/57-mango-store-app-page-it.png) · [GET, ring, OPEN](screenshots/58-mango-store-get-ring.png) |
| Store | Flathub: turn on, catalog (4,159 apps) in the Store, "most downloaded this month" from Flathub's statistics, badges, Debian app pages offer the Flathub version | ✅ in VM (real Flathub catalog) | [Flathub section](screenshots/59-mango-store-flathub-it.png); helper refuses invalid ids and reports flatpak errors. Installing a Flathub app (runtime download): to try on the Mac |
| Store | One catalog: Debian (1,876) + Flathub-only (2,705) = 4,581 apps in sections and search; Source switch on app pages; prefer-Flathub option; Flathub's most downloaded on Discover | ✅ in VM | [Play section](screenshots/61-mango-store-unified-play-it.png) · [GIMP, Debian/Flathub switch](screenshots/62-mango-store-source-switch-it.png) |
| Updates | Channels (beta every build, stable when promoted), Software Update panel with beta switch and manual 'go back' | ⚠️ panel and updater logic in VM | [panel](screenshots/63-software-update-it.png); channel switch, status and rollback paths run (network blocked in the build chroot); real download/rollback: on the Mac |
| Store | Labels: On this Mac Light / Medium / Heavy; "Not compatible with this Mac" from the requirements list and the machine's OpenGL / CPU / memory | ✅ in VM (machine facts set to the MacBook's: OpenGL 2.1, no AVX, 4 GB) | [Blender: OpenGL 4.3 needed](screenshots/67-mango-store-not-compatible-it.png); Blender / OBS / RPCS3 / Alpaca refused for the right reason, GIMP medium, Geany light |
| Apps | Notes: folders, list, editor with title line and checklists, autosave to plain files | ✅ in VM | [Notes](screenshots/65-notes-it.png); typed note saved to ~/Documents/Note; external changes reload |
| Apps | Passwords: keyring items (libsecret), password check with unix_chkpwd before showing, Wi-Fi tab (nmcli), QR share | ⚠️ keyring and password check in VM | [Passwords](screenshots/66-passwords-it.png); right password accepted, wrong one refused (exit 7); Wi-Fi tab needs NetworkManager: on the Mac |
| Apps | Notification Center from the clock: history, remove, Clear All, Do Not Disturb, marks read | ✅ in VM | [panel](screenshots/64-notification-center-it.png) with 3 notifications logged by xfce4-notifyd; existing users get the clock command at login |
| Apps | Calendar / Contacts with Internet Accounts (Google, iCloud CalDAV/CardDAV) | ⚠️ packages and panel only | [Internet Accounts](screenshots/68-internet-accounts-it.png); real accounts: on the Mac |
| Backup | Backup panel, helper (setup, list parsing, snapshot before updates with 6 h guard and keep-3), hourly timer | ⚠️ panel and parsing in VM | [panel](screenshots/60-backup-panel-it.png); real snapshots need the installed system's disk (the build chroot has none): to try on the Mac |
| Store | Install / remove through the root helper | ✅ | `store-helper install gnome-mines` with progress; removing a MangOS component (firefox-esr) refused; invalid names refused. The Get button → password dialog → install path needs a real session (polkit agent), not yet tried |
| Store | Screenshots on app pages | ⏳ | come from appstream.debian.org, blocked in the build sandbox; to check on the Mac |
| Network | MangOS Network panel (join, disconnect, forget, details: auto-join, preferred, band, password, DHCP/manual IP, router, DNS) | ✅ in VM with simulated nmcli | [panel](screenshots/45-network-panel-it.png) · [details](screenshots/46-network-details-it.png); OK in Details ran `nmcli connection modify` + removed the duplicate profile + reapplied. Real NetworkManager on the Mac: to check |
| Settings | MangOS System Settings: sidebar with coloured icons, Xfce dialogs embedded, gear icon in the dock | ✅ in VM | [Wi-Fi pane](screenshots/47-settings-network-it.png) · [Mouse and trackpad pane](screenshots/48-settings-mouse-it.png); switching panes stops the previous one. On the Mac: to check |
| Mac | Spotlight (Cmd+Space): apps, files in the home folder, calculator (Italian decimal comma), web search | ✅ in VM | [files](screenshots/49-spotlight-files-it.png) · [calculator](screenshots/50-spotlight-calculator-it.png) |
| Mac | Control Center (top-bar icon): Wi-Fi, Bluetooth, AirDrop, Do Not Disturb, Dark Mode, Night Shift, brightness, volume | ✅ in VM (no backlight or sound card there: sliders hidden) | [panel](screenshots/51-control-center-it.png) |
| Mac | Mission Control (F3, Ctrl+Up, hot corner) | ✅ in VM | [windows](screenshots/52-mission-control.png); hot corner bottom-left opened it |
| Mac | Quick Look: Space in the Finder; typing a space in the path bar is not affected | ✅ in VM | [preview](screenshots/53-quick-look-space.png) |
| Mac | Hot Corners settings; Night Shift (redshift, location from the time zone) on/off | ✅ in VM | [settings](screenshots/54-hot-corners-it.png); colour change itself: to see on the Mac |
| Mac | Screenshots on the Desktop (Cmd+Shift+3/4/5); AirDrop (LocalSend) and iPhone/Android (KDE Connect) install from Settings | ⏳ | to try on the Mac (LocalSend download is verified against GitHub's SHA-256 at build time) |
| 4.1 | Firefox ESR, VLC, Thunar, terminal, NetworkManager, PipeWire, CUPS, unattended-upgrades | ✅ | in the image; dock and Launchpad entries |
| 4.2 | ArtCraft `.deb`s downloaded, SHA-256 checked and installed | ✅ | GitHub Actions build #5: launcher 0.19.2, WordCraft 0.18.1, PdfCraft 0.21.1, PhotoCraft 0.23.1 installed (build stops if one is missing); release `v0.1.0-build.5`, 1.82 GB |
| 4.3 | WordCraft, PdfCraft, PhotoCraft start | ⚠️ partly, on hardware | MacBook4,1 (GMA X3100, OpenGL 2.1): PhotoCraft starts, says it cannot use the GPU and runs on the CPU (expected, see KNOWN-ISSUES). WordCraft and PdfCraft: to try |
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
| Other Macs | Model table (67 Intel Macs 2006-2012) with status in About This Computer; System Report (model, CPU, EFI, GPU / Wi-Fi with driver, brightness, trackpad, sound, fans, battery) | ✅ in VM | [System Report](screenshots/72-system-report-it.png); lspci parsing checked with MacBook GM965 + GeForce 9400M + BCM4321 output; [table](MAC-MODELS.md) |
| Other Macs | Boot menu refuses 32-bit processors (Core Duo 2006) with a clear message | ✅ in QEMU, 32-bit EFI | [qemu32 CPU: message](screenshots/70-boot-32bit-cpu-refused.png) · [Core 2 Duo: starts](screenshots/71-boot-64bit-cpu-ok.png) |
| Other Macs | NVIDIA / ATI graphics, Atheros Wi-Fi on real machines | ⚠️ not tried | drivers in the image (nouveau, radeon + firmware, ath9k); waiting for testers' System Reports |
| Updates | What's New after an update: preinst records the replaced build, postinst writes last-update and shows the window to logged-in users, autostart shows it once at login | ✅ in VM (scripts run with a build 38 → new build upgrade) | [window](screenshots/73-whats-new-it.png): only the 3 change sets after build 38; a second `--pending` shows nothing |
| Images | Two images from one build (scripts/make-editions.sh, xorriso replay of the boot setup): amd64 (64-bit EFI + BIOS) and efi32 (32-bit EFI + BIOS) | ✅ in QEMU (made from the 0.1.0 ISO) | [efi32 on 32-bit EFI: menu](screenshots/74-efi32-image-on-efi32.png) · [amd64 on 64-bit EFI: menu](screenshots/75-amd64-image-on-efi64.png) · [amd64 on 32-bit EFI: not started, as intended](screenshots/76-amd64-image-on-efi32-no-boot.png) · [amd64 on BIOS: menu](screenshots/77-amd64-image-on-bios.png); efi32 on 64-bit EFI not started, as intended |
