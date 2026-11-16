# Known issues and limits (MangOS 0.1.0)

Things that are known not to work, or not to work exactly like macOS. Items
marked **untested on hardware** still need a try on the real MacBook A1181.

## Hardware (MacBook A1181, 2006-2008)

- **32-bit EFI.** MacBook2,1/3,1/4,1 firmware is 32-bit EFI on a 64-bit CPU.
  The ISO ships `BOOTIA32.EFI` and the installer installs `grub-efi-ia32` on
  these machines. Verified in a VM with 32-bit OVMF; **untested on hardware**.
  Fallback: choose **Windows** (legacy BIOS) in the Option-key boot picker.
- **Intel GMA 950 / X3100 graphics** only offer OpenGL 1.4-2.1. The XFCE
  compositor (shadows) is fine on them, but apps that need OpenGL 3+ fall back
  to software rendering (slower). See ArtCraft below.
- **Trackpad gestures.** The 2007 trackpad (appletouch driver) reports only
  basic multi-finger data: tap, two-finger scroll and two-finger click work;
  pinch/four-finger gestures (e.g. to open Launchpad) do not. Use Cmd+Space,
  F4 or the dock icon instead.
- **Fan control** uses `mbpfan`; **brightness keys** use `brightnessctl`.
  **Untested on hardware.**
- **Wi-Fi.** A1181 Wi-Fi cards are Atheros (ath9k, no firmware needed).
  Some units were upgraded with Broadcom cards; those may need
  `broadcom-sta-dkms` from the internet after installing.

## Look and feel

- Window **bottom corners are square**: the XFCE window manager rounds only the
  title bar. Full rounded corners would need picom, too heavy for GMA graphics.
- The **global menu** shows menus for GTK apps (Thunar, Terminal, settings);
  Firefox, VLC and the ArtCraft apps keep their menus inside the window.
- **Cmd+C in Terminal** sends Ctrl+C (interrupt), as on any Linux; copy with
  Cmd+Shift+C there.
- **Launchpad** is a full-screen rofi grid: it pages with Page Up/Down or the
  scroll wheel, but has no folders or drag-and-drop arranging.
- The San Francisco font is not redistributable; MangOS uses **Inter**.

## ArtCraft (alpha software)

- The ArtCraft `.deb` files are downloaded from GitHub at build time. If the
  build machine cannot reach GitHub, `build.sh` warns and builds the ISO
  **without** them (or fails with `MANGOS_REQUIRE_ARTCRAFT=1`). The test ISO
  built for this release did not include them: see `docs/TESTING.md`.
- ArtCraft apps are egui (Rust) applications using wgpu/OpenGL. On GMA 950 /
  X3100 they will probably run through Mesa's software renderer (llvmpipe),
  which works but is slow on a Core 2 Duo. **Untested on hardware.**
- The launcher installs further Craft apps with `apt` and asks for your
  password.

## Installer

- The partition page preselects **Erase disk**; *Manual partitioning* is the
  last choice on the same page (Calamares cannot hide it behind a button).
- Installation is offline; updates are fetched after the first boot by the
  automatic security updates.
