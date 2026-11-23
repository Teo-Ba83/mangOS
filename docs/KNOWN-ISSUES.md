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
- **Fan control** uses `mbpfan`. **Brightness keys** (F1/F2) and the Control
  Center slider use the power manager's backlight helper (no password) and
  never go below 10 %, so the screen always stays lit.
- **Wi-Fi (Broadcom BCM4321/BCM4328, PCI 14e4:4328 on the MacBook3,1 and 4,1).**
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
- **Dual-band routers and mesh extenders.** On a network that is on both
  2.4 and 5 GHz under one name (e.g. a Virgin Media hub with an extender),
  `wl` associates on 5 GHz but often gets no address (DHCP), so the Wi-Fi
  icon keeps spinning; on 2.4 GHz it works (seen on the real MacBook4,1).
  After a network connects once, MangOS locks its saved profile to 2.4 GHz
  if that network is also on 2.4 GHz (5 GHz-only networks are left alone).
  Manually: `sudo nmcli connection modify "<name>" 802-11-wireless.band bg`;
  undo with `802-11-wireless.band ""`.
- **Mesh systems with WPA/WPA2 mixed security** (seen with a Tenda Nova
  Wi-Fi 5 mesh): with `wl` the Mac connects only the first time; later the
  WPA handshake is skipped and no address arrives, even on 2.4 GHz and tied
  to one node. With the reserve `b43` driver (`sudo mangos-wifi-driver b43`)
  it reconnects. Setting the mesh to WPA2-only (AES), where the mesh app
  allows it, is the other fix. Switching driver now unties saved networks
  from the old interface name, so they keep working.
- **Speed, measured on the MacBook4,1** (Speedtest, Virgin hub on 2.4 GHz,
  same room): `wl` 80 Mbit/s down, 26 up; `b43` 9 down, 10 up (Tenda mesh
  node with `b43`: about 15). `wl` is much faster; `b43` is the choice only
  for networks `wl` cannot reconnect to (the mixed WPA/WPA2 mesh above).
- **Panel Wi-Fi menu and duplicates.** Clicking a dual-band network in the
  Wi-Fi icon's menu picks its strongest (5 GHz) access point; if the saved
  profile is locked to 2.4 GHz, the menu does not match it, asks the
  password again and saves a copy ("Name 1"). Use **Network** (logo menu,
  Settings or Launchpad) instead: it connects the saved profile, removes
  duplicates, and has Forget and Details (DHCP or manual IP).
- **wl must win at boot.** On the MacBook4,1 b43's ssb (b43-pci-bridge)
  could take the card before wl, dropping Wi-Fi to b43 speed. MangOS keeps
  the Broadcom drivers out of the initramfs, reloads wl at boot if it did not
  bind, never swaps drivers while one holds the card (that froze the Mac),
  and ignores the live stick's `mangos.wifi=` option on an installed system.
  After changing driver, shut down fully (not restart) and power on.
  Verified: back to 82.9 down / 26.2 up with wl (21 Nov).
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
- **Mac-style extras.** Cmd+Space opens **Spotlight** (Launchpad: F4 or the
  dock); **F3** or **Ctrl+Up** open **Mission Control** (F3 no longer means
  "find next" in Firefox: use Cmd+G); the bottom-left corner opens Mission
  Control and the bottom-right shows the desktop (Settings > Hot Corners).
  Mission Control shows minimised windows as their icon.
- **AirDrop** is LocalSend, which must be installed on the other device too;
  it does not talk to Apple's AirDrop. **iPhone & Android** uses KDE Connect,
  installed on request (about 150 MB); its iPhone app has fewer features.
- **Night Shift** follows sunset and sunrise for the time zone's main city.
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

## Updates

- **Two channels.** Every build is published as a *beta*; only builds
  promoted to *stable* reach everyone. Settings > Software Update has
  "Receive beta versions". A build is promoted by changing the number in
  `channels/stable-build` (or from Actions > "Promote a build to stable");
  its already-signed files become the stable release, nothing is rebuilt.
  Only the 6 newest builds (and the stable one) are kept.
- **Going back is the user's choice.** Software Update > "Go Back to the
  Previous Version" reinstalls the version you had before (kept on the disk,
  signed; downloaded again if needed); the version left is then skipped
  until a newer one is published. There is no automatic rollback. "Restore a
  Backup…" brings back the whole system (Debian updates included).
- Going back becomes available after the first update installed with this
  updater (0.2.0); the version before it can still be downloaded while its
  build is kept.
- Updates change the system defaults; settings a user already changed
  (theme, dock, panel) stay as the user set them.
- Removing a program from the package list does not uninstall it from
  machines that already have it.

## Store

- The Store shows the apps of Debian's AppStream catalog. The catalog and
  icons (about 25 MB) are downloaded with the package lists: on a fresh
  installation the Store offers a "Download the catalog" button the first
  time, afterwards Debian's daily update keeps it fresh.
- **Apps of the week** (sliding banner and list on Discover) come from the
  Debian Popularity Contest (popcon.debian.org): the most used desktop apps
  among Debian users that are not installed yet, three new ones each ISO
  week. Debian publishes no weekly download counts, so this is "most used",
  not "most downloaded this week". The list is downloaded once a week
  (about 1 MB, first part of the popcon table). If popcon.debian.org cannot
  be reached, the Store uses the snapshot taken when the MangOS build was
  made (/usr/share/mangos/popcon-top.txt), then curated suggestions; the
  reason is written to ~/.cache/mangos-store/popcon.log.
- Each section starts with a curated list of well-known apps, then the rest
  alphabetically.
- Installing needs the administrator password (as on a Mac). Apps that are
  part of MangOS cannot be removed from the Store.
- "App Store" is an Apple trademark, so the MangOS one is called
  **Mango Store**, with its own icon (the MangOS mango on a teal tile).

## Flathub

- The Mango Store is **one catalog**: every Debian app plus the apps only
  Flathub has (about 4,600 in all, e.g. Spotify, Discord, OBS, VS Code), in
  the same sections and search. Flathub is added automatically (from a repo
  file shipped with MangOS); its catalog (about 100 MB of data and icons) is
  downloaded in the background after the update, then refreshed daily.
- When an app exists in both, the Store shows the Debian version (lighter,
  shares the system's libraries) and its page has a **Source** switch:
  Debian (lighter) / Flathub (newer). "Prefer the newest versions
  (Flathub)" at the bottom of the sidebar makes Flathub the default.
- "Most downloaded this month" on Discover uses Flathub's own download
  statistics; LibreOffice and games or launchers that need Vulkan / OpenGL
  3+ are left out, because this Mac's graphics cannot run them.
- The first Flathub app also downloads its runtime (a few hundred MB);
  later apps share it. Flathub apps run in a sandbox; many are built with
  Electron and use software rendering on the GMA X3100.

## Backups

- **Backup** (Settings, Launchpad) uses Timeshift: snapshots of the system
  (programs and settings, not documents) on the same disk, every day (3 kept),
  every week (2 kept) and before MangOS / Debian updates (last 3 kept, at most
  one every 6 hours). Set up automatically when there are at least 8 GB free.
- Flatpak apps and the package cache are not copied (they can be downloaded
  again).
- Restoring opens Timeshift and restarts the Mac. If MangOS does not start,
  boot the MangOS USB stick: Timeshift is there too.
- Backups on the same disk do not protect against a broken disk.

## Installer

- Under emulation (no KVM) the install took about 30 minutes; on the
  MacBook's SSD it should be much faster, but this is **untested on hardware**.
- The partition page preselects **Erase disk**; *Manual partitioning* is the
  last choice on the same page (Calamares cannot hide it behind a button).
- Installation is offline; updates are fetched after the first boot by the
  automatic security updates.
