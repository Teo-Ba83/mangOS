# Known issues and limits (MangOS 0.1.0)

Things that are known not to work, or not to work exactly like macOS. Items
marked **untested on hardware** still need a try on the real MacBook A1181.

## Hardware (MacBook A1181, 2006-2008)

- **32-bit EFI.** MacBook2,1/3,1/4,1 firmware is 32-bit EFI on a 64-bit CPU.
  The ISO ships `BOOTIA32.EFI` and the installer installs `grub-efi-ia32` on
  these machines. Verified in a VM with 32-bit OVMF (live boot, full install,
  installed system starting on its own); **untested on hardware**.
  Fallback: choose **Windows** (legacy BIOS) in the Option-key boot picker.
- **`efi=noruntime` on 32-bit EFI.** The 64-bit kernel crashes when it calls
  32-bit EFI runtime services, so MangOS turns them off on those machines
  (automatically, only there). Consequence: Linux cannot read or change EFI
  variables, so the boot disk is chosen with the Option key or *Startup Disk*
  in macOS, not from Linux. The installer always writes the fallback loader
  `EFI/BOOT/BOOTIA32.EFI`, which the Mac firmware finds by itself.
- **Intel GMA 950 / X3100 graphics** only offer OpenGL 1.4-2.1. The XFCE
  compositor (shadows) is fine on them, but apps that need OpenGL 3+ fall back
  to software rendering (slower). See ArtCraft below.
- **Trackpad gestures.** The 2007 trackpad (appletouch driver) reports only
  basic multi-finger data: tap, two-finger scroll and two-finger click work;
  pinch/four-finger gestures (e.g. to open Launchpad) do not. Use Cmd+Space,
  F4 or the dock icon instead.
- **Fan control** uses `mbpfan`; **brightness keys** use `brightnessctl`.
  **Untested on hardware.**
- **Wi-Fi (Broadcom BCM4321/BCM4328, PCI 14e4:4328 on the MacBook3,1).**
  MangOS uses the proprietary `wl` driver (broadcom-sta-dkms), already
  compiled for the ISO's kernel, so it works offline. `b43`, `b43legacy`,
  `ssb`, `bcma`, `brcmsmac`, `brcm80211` and `b44` are blacklisted because
  they conflict with `wl` (`b44`, Broadcom Ethernet, would load `ssb` and grab
  the Wi-Fi card; it is not used on MacBooks). The open `b43` driver and its
  firmware stay installed as a reserve: choose **MangOS (Wi-Fi: b43 driver)**
  in the boot menu, or run `sudo mangos-wifi-driver b43` (and
  `sudo mangos-wifi-driver wl` to go back). `b43` support for the BCM4321
  (N-PHY) is less mature than `wl`.
  QEMU cannot emulate this card: the driver was built and loaded in a VM, but
  real Wi-Fi traffic is **untested on hardware**. The **Wi-Fi Check** icon on
  the live desktop prints `lspci -nn` and the Wi-Fi state, and saves it to
  `~/mangos-wifi-check.txt`.
- When `wl` loads, the kernel logs "Unpatched return thunk in use" with a
  warning trace: the closed-source part of the driver predates current CPU
  mitigations. It is harmless (Broadcom/Debian note to ignore it on older
  CPUs) and the driver keeps working.
- **Kernel headers and a compiler are installed** (about 200 MB) so DKMS can
  rebuild `wl` when Debian updates the kernel. DKMS signs modules with a key
  it creates on each computer; the key from the build is deleted, never
  shipped. Secure Boot is not relevant on these Macs.

## Look and feel

- Window **bottom corners are square**: the XFCE window manager rounds only the
  title bar. Full rounded corners would need picom, too heavy for GMA graphics.
- With no window focused, the global menu shows "Xfdesktop" where macOS
  shows "Finder".
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
  **without** them (or fails with `MANGOS_REQUIRE_ARTCRAFT=1`). The ISOs built
  by GitHub Actions (release `v0.1.0-build.5` and later) include them; the
  earlier `v0.1.0-build.3` release does **not**, although its notes list the
  downloads (live-build skipped the packages because of their file names).
- ArtCraft apps are egui (Rust) applications using wgpu/OpenGL. On GMA 950 /
  X3100 they will probably run through Mesa's software renderer (llvmpipe),
  which works but is slow on a Core 2 Duo. **Untested on hardware.**
- The launcher installs further Craft apps with `apt` and asks for your
  password.

## Installer

- Under emulation (no KVM) the install took about 30 minutes; on the
  MacBook's SSD it should be much faster, but this is **untested on hardware**.
- The partition page preselects **Erase disk**; *Manual partitioning* is the
  last choice on the same page (Calamares cannot hide it behind a button).
- Installation is offline; updates are fetched after the first boot by the
  automatic security updates.
