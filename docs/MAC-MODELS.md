# MangOS on Intel Macs, 2006-2012

There is **one MangOS image for every model**: it recognises the hardware at
start-up and loads the right drivers. Generated from
`config/includes.chroot/usr/lib/python3/dist-packages/mangos/macmodels.py`
(`python3 -m mangos.macmodels --markdown`); MangOS shows the same status in
**About This Computer**.

- ✅ **Tested**: tried on the real machine. Today only the MacBook (early
  2008, MacBook4,1); the MacBook (late 2007) has the same graphics, Wi-Fi
  and firmware.
- ❔ **Should work**: the drivers are in MangOS, nobody has tried it yet.
- ❌ **Not supported**: the 2006 models with a **Core Duo / Core Solo** have
  a 32-bit processor. MangOS (like Debian 13) is 64-bit only; the boot
  menu says so instead of stopping with a cryptic error
  ([32-bit](screenshots/70-boot-32bit-cpu-refused.png),
  [64-bit](screenshots/71-boot-64bit-cpu-ok.png), tested in QEMU with 32-bit EFI).

## What MangOS does for each kind of hardware

| Hardware | Models | How |
|---|---|---|
| 32-bit EFI firmware | 2006-2007 (MacBook2,1, MacBook Pro 2,x, iMac 5,x / 6,1, Mac mini 2,1, Mac Pro 1,1 / 2,1) | 32-bit GRUB on the USB stick and the installed system, EFI runtime services off (tested in QEMU) |
| Intel graphics (GMA 950, GMA X3100, HD 3000 / 4000) | MacBook, MacBook Air, Mac mini, 13" MacBook Pro 2011-2012 | i915 + xserver-xorg-video-intel (GMA X3100 tested) |
| NVIDIA (GeForce 7300 GT to GT 650M) | most 2008-2010 notebooks, iMacs, Mac minis | nouveau + xserver-xorg-video-nouveau |
| ATI / AMD (Radeon X1600 to HD 6970M) | MacBook Pro 2006 and 2011, iMac 2007-2011 | radeon + xserver-xorg-video-ati + firmware-amd-graphics |
| Broadcom Wi-Fi (BCM4321 / 4322 / 43224 / 4331) | most models from late 2007 | proprietary `wl` (fast), open `b43` as reserve (BCM4321 tested) |
| Atheros Wi-Fi (AR5418, AR9280, AR9380) | 2006-2007 notebooks, iMacs 2007-2011 | ath9k, in the kernel |
| Trackpad | all notebooks | appletouch (to 2007) or bcm5974 (from 2008), libinput, Mac-like settings |
| Fans, keyboard | all | applesmc + mbpfan; Apple keyboard media keys by default |

## Every model

| Model | Identifier | 64-bit CPU | EFI | Graphics | Wi-Fi | Status | Notes |
|---|---|---|---|---|---|---|---|
| MacBook (13-inch, 2006) | `MacBook1,1` | **no** | 32-bit | Intel GMA 950 | Atheros | ❌ Not supported: 32-bit processor |  |
| MacBook (13-inch, late 2006 / mid 2007) | `MacBook2,1` | yes | 32-bit | Intel GMA 950 | Atheros | ❔ Should work, not tried yet | 32-bit EFI firmware: started through MangOS's 32-bit GRUB, with EFI runtime services off. |
| MacBook (13-inch, late 2007) | `MacBook3,1` | yes | 64-bit | Intel GMA X3100 | Broadcom or Atheros | ✅ Same hardware as a tested model |  |
| MacBook (13-inch, early 2008) | `MacBook4,1` | yes | 64-bit | Intel GMA X3100 | Broadcom or Atheros | ✅ Tested |  |
| MacBook (13-inch aluminium, late 2008) | `MacBook5,1` | yes | 64-bit | NVIDIA GeForce 9400M | Broadcom | ❔ Should work, not tried yet |  |
| MacBook (13-inch, early / mid 2009) | `MacBook5,2` | yes | 64-bit | NVIDIA GeForce 9400M | Broadcom | ❔ Should work, not tried yet |  |
| MacBook (13-inch, late 2009) | `MacBook6,1` | yes | 64-bit | NVIDIA GeForce 9400M | Broadcom | ❔ Should work, not tried yet |  |
| MacBook (13-inch, mid 2010) | `MacBook7,1` | yes | 64-bit | NVIDIA GeForce 320M | Broadcom | ❔ Should work, not tried yet |  |
| MacBook Air (2008) | `MacBookAir1,1` | yes | 64-bit | Intel GMA X3100 | Broadcom | ❔ Should work, not tried yet |  |
| MacBook Air (late 2008 / mid 2009) | `MacBookAir2,1` | yes | 64-bit | NVIDIA GeForce 9400M | Broadcom | ❔ Should work, not tried yet |  |
| MacBook Air (11-inch, late 2010) | `MacBookAir3,1` | yes | 64-bit | NVIDIA GeForce 320M | Broadcom | ❔ Should work, not tried yet |  |
| MacBook Air (13-inch, late 2010) | `MacBookAir3,2` | yes | 64-bit | NVIDIA GeForce 320M | Broadcom | ❔ Should work, not tried yet |  |
| MacBook Air (11-inch, mid 2011) | `MacBookAir4,1` | yes | 64-bit | Intel HD Graphics 3000 | Broadcom | ❔ Should work, not tried yet |  |
| MacBook Air (13-inch, mid 2011) | `MacBookAir4,2` | yes | 64-bit | Intel HD Graphics 3000 | Broadcom | ❔ Should work, not tried yet |  |
| MacBook Air (11-inch, mid 2012) | `MacBookAir5,1` | yes | 64-bit | Intel HD Graphics 4000 | Broadcom | ❔ Should work, not tried yet |  |
| MacBook Air (13-inch, mid 2012) | `MacBookAir5,2` | yes | 64-bit | Intel HD Graphics 4000 | Broadcom | ❔ Should work, not tried yet |  |
| MacBook Pro (15-inch, early 2006) | `MacBookPro1,1` | **no** | 32-bit | ATI Radeon X1600 | Atheros | ❌ Not supported: 32-bit processor |  |
| MacBook Pro (17-inch, 2006) | `MacBookPro1,2` | **no** | 32-bit | ATI Radeon X1600 | Atheros | ❌ Not supported: 32-bit processor |  |
| MacBook Pro (17-inch, late 2006) | `MacBookPro2,1` | yes | 32-bit | ATI Radeon X1600 | Atheros | ❔ Should work, not tried yet | 32-bit EFI firmware: started through MangOS's 32-bit GRUB, with EFI runtime services off. |
| MacBook Pro (15-inch, late 2006) | `MacBookPro2,2` | yes | 32-bit | ATI Radeon X1600 | Atheros | ❔ Should work, not tried yet | 32-bit EFI firmware: started through MangOS's 32-bit GRUB, with EFI runtime services off. |
| MacBook Pro (mid / late 2007) | `MacBookPro3,1` | yes | 64-bit | NVIDIA GeForce 8600M GT | Atheros or Broadcom | ❔ Should work, not tried yet |  |
| MacBook Pro (early 2008) | `MacBookPro4,1` | yes | 64-bit | NVIDIA GeForce 8600M GT | Atheros or Broadcom | ❔ Should work, not tried yet |  |
| MacBook Pro (15-inch, late 2008) | `MacBookPro5,1` | yes | 64-bit | NVIDIA GeForce 9400M + 9600M GT | Broadcom | ❔ Should work, not tried yet | Two NVIDIA graphics chips: MangOS uses the one chosen in macOS's Energy Saver (9400M by default). |
| MacBook Pro (17-inch, 2009) | `MacBookPro5,2` | yes | 64-bit | NVIDIA GeForce 9400M + 9600M GT | Broadcom | ❔ Should work, not tried yet | Two NVIDIA graphics chips: MangOS uses the one chosen in macOS's Energy Saver (9400M by default). |
| MacBook Pro (15-inch, mid 2009) | `MacBookPro5,3` | yes | 64-bit | NVIDIA GeForce 9400M + 9600M GT | Broadcom | ❔ Should work, not tried yet | Two NVIDIA graphics chips: MangOS uses the one chosen in macOS's Energy Saver (9400M by default). |
| MacBook Pro (15-inch, mid 2009) | `MacBookPro5,4` | yes | 64-bit | NVIDIA GeForce 9400M | Broadcom | ❔ Should work, not tried yet |  |
| MacBook Pro (13-inch, mid 2009) | `MacBookPro5,5` | yes | 64-bit | NVIDIA GeForce 9400M | Broadcom | ❔ Should work, not tried yet |  |
| MacBook Pro (17-inch, mid 2010) | `MacBookPro6,1` | yes | 64-bit | Intel HD + NVIDIA GeForce GT 330M | Broadcom | ❔ Should work, not tried yet | Switchable graphics (Intel + NVIDIA): the screen is driven by the chip active at startup. |
| MacBook Pro (15-inch, mid 2010) | `MacBookPro6,2` | yes | 64-bit | Intel HD + NVIDIA GeForce GT 330M | Broadcom | ❔ Should work, not tried yet | Switchable graphics (Intel + NVIDIA): the screen is driven by the chip active at startup. |
| MacBook Pro (13-inch, mid 2010) | `MacBookPro7,1` | yes | 64-bit | NVIDIA GeForce 320M | Broadcom | ❔ Should work, not tried yet |  |
| MacBook Pro (13-inch, 2011) | `MacBookPro8,1` | yes | 64-bit | Intel HD Graphics 3000 | Broadcom | ❔ Should work, not tried yet |  |
| MacBook Pro (15-inch, 2011) | `MacBookPro8,2` | yes | 64-bit | Intel HD 3000 + AMD Radeon HD 6490M / 6750M / 6770M | Broadcom | ❔ Should work, not tried yet | The AMD graphics chip of these models often fails with age (a hardware fault). If the screen freezes or stays black, start with 'MangOS (safe graphics)'. |
| MacBook Pro (17-inch, 2011) | `MacBookPro8,3` | yes | 64-bit | Intel HD 3000 + AMD Radeon HD 6750M / 6770M | Broadcom | ❔ Should work, not tried yet | The AMD graphics chip of these models often fails with age (a hardware fault). If the screen freezes or stays black, start with 'MangOS (safe graphics)'. |
| MacBook Pro (15-inch, mid 2012) | `MacBookPro9,1` | yes | 64-bit | Intel HD 4000 + NVIDIA GeForce GT 650M | Broadcom | ❔ Should work, not tried yet | Switchable graphics (Intel + NVIDIA): the screen is driven by the chip active at startup. |
| MacBook Pro (13-inch, mid 2012) | `MacBookPro9,2` | yes | 64-bit | Intel HD Graphics 4000 | Broadcom | ❔ Should work, not tried yet |  |
| MacBook Pro (Retina, 15-inch, mid 2012) | `MacBookPro10,1` | yes | 64-bit | Intel HD 4000 + NVIDIA GeForce GT 650M | Broadcom | ❔ Should work, not tried yet | Switchable graphics (Intel + NVIDIA): the screen is driven by the chip active at startup. |
| MacBook Pro (Retina, 13-inch, late 2012) | `MacBookPro10,2` | yes | 64-bit | Intel HD Graphics 4000 | Broadcom | ❔ Should work, not tried yet |  |
| iMac (early 2006) | `iMac4,1` | **no** | 32-bit | ATI Radeon X1600 | Atheros | ❌ Not supported: 32-bit processor |  |
| iMac (17-inch, mid 2006) | `iMac4,2` | **no** | 32-bit | Intel GMA 950 | Atheros | ❌ Not supported: 32-bit processor |  |
| iMac (late 2006) | `iMac5,1` | yes | 32-bit | ATI Radeon X1600 or NVIDIA GeForce 7300 GT / 7600 GT | Atheros | ❔ Should work, not tried yet | 32-bit EFI firmware: started through MangOS's 32-bit GRUB, with EFI runtime services off. |
| iMac (17-inch, late 2006) | `iMac5,2` | yes | 32-bit | Intel GMA 950 | Atheros | ❔ Should work, not tried yet | 32-bit EFI firmware: started through MangOS's 32-bit GRUB, with EFI runtime services off. |
| iMac (24-inch, late 2006) | `iMac6,1` | yes | 32-bit | NVIDIA GeForce 7300 GT / 7600 GT | Atheros | ❔ Should work, not tried yet | 32-bit EFI firmware: started through MangOS's 32-bit GRUB, with EFI runtime services off. |
| iMac (mid 2007) | `iMac7,1` | yes | 64-bit | ATI Radeon HD 2400 XT / 2600 Pro | Atheros | ❔ Should work, not tried yet |  |
| iMac (early 2008) | `iMac8,1` | yes | 64-bit | ATI Radeon HD 2400 / 2600 or NVIDIA GeForce 8800 GS | Atheros or Broadcom | ❔ Should work, not tried yet |  |
| iMac (early / mid 2009) | `iMac9,1` | yes | 64-bit | NVIDIA GeForce 9400M / GT 120 / GT 130 | Atheros or Broadcom | ❔ Should work, not tried yet |  |
| iMac (late 2009) | `iMac10,1` | yes | 64-bit | NVIDIA GeForce 9400M or ATI Radeon HD 4670 | Atheros | ❔ Should work, not tried yet |  |
| iMac (27-inch, late 2009) | `iMac11,1` | yes | 64-bit | ATI Radeon HD 4850 | Atheros | ❔ Should work, not tried yet |  |
| iMac (21.5-inch, mid 2010) | `iMac11,2` | yes | 64-bit | ATI Radeon HD 4670 | Atheros | ❔ Should work, not tried yet |  |
| iMac (27-inch, mid 2010) | `iMac11,3` | yes | 64-bit | ATI Radeon HD 5670 / 5750 | Atheros | ❔ Should work, not tried yet |  |
| iMac (21.5-inch, mid 2011) | `iMac12,1` | yes | 64-bit | AMD Radeon HD 6750M / 6770M | Atheros | ❔ Should work, not tried yet |  |
| iMac (27-inch, mid 2011) | `iMac12,2` | yes | 64-bit | AMD Radeon HD 6770M / 6970M | Atheros | ❔ Should work, not tried yet |  |
| iMac (21.5-inch, late 2012) | `iMac13,1` | yes | 64-bit | NVIDIA GeForce GT 640M / 650M | Broadcom | ❔ Should work, not tried yet |  |
| iMac (27-inch, late 2012) | `iMac13,2` | yes | 64-bit | NVIDIA GeForce GTX 660M / 675MX / 680MX | Broadcom | ❔ Should work, not tried yet |  |
| Mac mini (early 2006) | `Macmini1,1` | **no** | 32-bit | Intel GMA 950 | Atheros | ❌ Not supported: 32-bit processor |  |
| Mac mini (mid 2007) | `Macmini2,1` | yes | 32-bit | Intel GMA 950 | Atheros | ❔ Should work, not tried yet | 32-bit EFI firmware: started through MangOS's 32-bit GRUB, with EFI runtime services off. |
| Mac mini (early / late 2009) | `Macmini3,1` | yes | 64-bit | NVIDIA GeForce 9400M | Atheros or Broadcom | ❔ Should work, not tried yet |  |
| Mac mini (mid 2010) | `Macmini4,1` | yes | 64-bit | NVIDIA GeForce 320M | Broadcom | ❔ Should work, not tried yet |  |
| Mac mini (mid 2011) | `Macmini5,1` | yes | 64-bit | Intel HD Graphics 3000 | Broadcom | ❔ Should work, not tried yet |  |
| Mac mini (mid 2011) | `Macmini5,2` | yes | 64-bit | AMD Radeon HD 6630M | Broadcom | ❔ Should work, not tried yet |  |
| Mac mini (server, mid 2011) | `Macmini5,3` | yes | 64-bit | Intel HD Graphics 3000 | Broadcom | ❔ Should work, not tried yet |  |
| Mac mini (late 2012) | `Macmini6,1` | yes | 64-bit | Intel HD Graphics 4000 | Broadcom | ❔ Should work, not tried yet |  |
| Mac mini (late 2012) | `Macmini6,2` | yes | 64-bit | Intel HD Graphics 4000 | Broadcom | ❔ Should work, not tried yet |  |
| Mac Pro (2006) | `MacPro1,1` | yes | 32-bit | NVIDIA GeForce 7300 GT or ATI Radeon X1900 XT | Atheros or Broadcom (option) | ❔ Should work, not tried yet | 32-bit EFI firmware: started through MangOS's 32-bit GRUB, with EFI runtime services off. |
| Mac Pro (2007) | `MacPro2,1` | yes | 32-bit | NVIDIA / ATI (various) | Atheros or Broadcom (option) | ❔ Should work, not tried yet | 32-bit EFI firmware: started through MangOS's 32-bit GRUB, with EFI runtime services off. |
| Mac Pro (early 2008) | `MacPro3,1` | yes | 64-bit | ATI Radeon HD 2600 XT or NVIDIA GeForce 8800 GT | Broadcom or Atheros (option) | ❔ Should work, not tried yet |  |
| Mac Pro (2009) | `MacPro4,1` | yes | 64-bit | NVIDIA GeForce GT 120 or ATI Radeon HD 4870 | Atheros or Broadcom (option) | ❔ Should work, not tried yet |  |
| Mac Pro (2010 / 2012) | `MacPro5,1` | yes | 64-bit | ATI Radeon HD 5770 / 5870 | Atheros or Broadcom (option) | ❔ Should work, not tried yet |  |

## Trying MangOS on another Mac

Start it from the USB stick (Option key at power-on), open **About This
Computer > System Report**, press **Copy** and send the text: it says which
graphics and Wi-Fi drivers were used, and whether brightness, trackpad,
sound and fan control were found. That is what turns a ❔ into a ✅.
