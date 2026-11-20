# UniFlash Tool — Complete User Guide & Manual 📖

**Developed by:** Tejas Jadhav ([@vik4sx](https://github.com/vik4sx))  
**Version:** 1.0 (Black & Orange Cyber Edition)

---

## 📑 Table of Contents
1. [Introduction](#introduction)
2. [First-Time Setup & Prerequisites](#first-time-setup--prerequisites)
3. [Installing Drivers](#installing-drivers)
4. [Connecting Your Phone](#connecting-your-phone)
5. [Reboot & ADB Controls](#reboot--adb-controls)
6. [Flashing Firmware & ROMs](#flashing-firmware--roms)
7. [Device Backup & Partition Pull](#device-backup--partition-pull)
8. [Device Diagnostics & Info](#device-diagnostics--info)
9. [Customizing Themes (Dark & Light)](#customizing-themes-dark--light)
10. [Troubleshooting & FAQs](#troubleshooting--faqs)

---

## 1. Introduction

**UniFlash Tool** is an all-in-one desktop GUI utility designed for Android enthusiasts, developers, and technicians. It provides a visual interface for managing devices via ADB (Android Debug Bridge) and Fastboot protocols, eliminating the need to type complex terminal commands manually.

---

## 2. First-Time Setup & Prerequisites

### Requirements:
- **Operating System:** Windows 10 or Windows 11 (64-bit)
- **USB Cable:** High-quality OEM data cable (avoid charge-only cables)
- **USB Port:** Direct motherboard/laptop USB port (prefer USB 2.0 or USB 3.0 ports; avoid unpowered USB hubs)

---

## 3. Installing Drivers

If your computer doesn't recognize your phone when connected, drivers are required:

1. Open **UniFlash Tool** and click on **🔧 Drivers** in the sidebar.
2. In the top featured card, click **🚀 RUN INSTALLER NOW**.
3. The bundled **15-Second ADB & Driver Installer** will launch:
   - Type `Y` and press `Enter` to install ADB & Fastboot system-wide.
   - Type `Y` and press `Enter` to install device drivers.
4. If your brand uses a proprietary chipset protocol (such as Qualcomm 9008 EDL or Samsung Odin), click the corresponding OEM driver card in the list to download the official manufacturer package.
5. Use the **💻 Open Device Manager** button to verify that your phone appears under *Android Device* or *Ports (COM & LPT)* without any yellow warning triangles.

---

## 4. Connecting Your Phone

### Step 1: Enable Developer Options
1. On your phone, go to **Settings ➔ About Phone**.
2. Tap **Build Number** 7 times until you see the message: *"You are now a developer!"*

### Step 2: Enable USB Debugging
1. Go to **Settings ➔ System (or Additional Settings) ➔ Developer Options**.
2. Turn on **USB Debugging**.
3. (Optional for Xiaomi devices): Enable **USB Debugging (Security Settings)**.

### Step 3: Authorize PC
1. Connect your phone to your computer via USB.
2. A pop-up prompt will appear on your phone screen: *"Allow USB debugging?"*
3. Check **"Always allow from this computer"** and tap **Allow**.
4. In UniFlash Tool, the top status bar will change from 🔴 to 🟢 **ADB Online**, displaying your device's brand, model, and serial number.

---

## 5. Reboot & ADB Controls

Navigate to **🔄 Reboot** in the sidebar to execute immediate state transitions:

| Tile | What it does | When to use |
|---|---|---|
| **📱 Reboot Normal** | Restarts your device back into standard Android OS | After completing maintenance or flashing |
| **🔧 Reboot Bootloader** | Reboots phone into Fastboot / Bootloader mode | Needed for partition flashing & unlocking |
| **🛠️ Reboot Recovery** | Boots directly into Stock or Custom Recovery (TWRP / OrangeFox) | To wipe cache, factory reset, or flash ZIPs |
| **⚡ Reboot Fastbootd** | Boots into user-space Fastboot (Android 10+ dynamic partitions) | For flashing system, vendor, or product partitions on modern phones |
| **🏭 Reboot EDL Mode** | Forces Qualcomm Snapdragon devices into Emergency Download 9008 mode | Unbricking devices with authorized loaders |
| **📡 Reboot Sideload** | Boots device straight into Recovery Sideload mode | Ready for `adb sideload` OTA updates |
| **🔌 Kill ADB Server** | Terminates any hanging background ADB processes | When ADB is unresponsive |
| **🔁 Restart ADB Server** | Restarts the local ADB daemon service | Fixes connection drops or state mismatches |
| **📲 Open ADB Shell** | Launches an interactive command prompt directly connected to your phone | For advanced command-line diagnostics |

---

## 6. Flashing Firmware & ROMs

Navigate to **⚡ Flash** in the sidebar:

### A. 1-Click ROM / Firmware Flash
1. Click **📂 Browse** and choose your firmware file (`.zip`, `.img`, `.tar.md5`, or `.ozip`).
2. Select your device manufacturer from the **Brand** dropdown (or leave as Auto-Detect).
3. Choose your flash options:
   - **Wipe Data**: Performs factory data wipe before flashing (recommended for clean ROM installs).
   - **Wipe Cache & Dalvik**: Clears cache partitions to prevent bootloops.
   - **Flash as Sideload**: Uses recovery sideload mode.
4. Click **🚀 START FLASH OPERATION**.
5. Confirm the warning dialog to proceed. Monitor real-time logs in the bottom console.

### B. Partition Flashing (Advanced)
1. Expand the **Advanced Partitions** section.
2. Browse individual partition images:
   - `boot.img` (Kernel / Magisk patched boot)
   - `recovery.img` (TWRP / custom recoveries)
   - `system.img` (System OS / Generic System Images - GSI)
   - `vendor.img`, `vbmeta.img`, `dtbo.img`, `userdata.img`
3. Click the flash icon next to the partition you wish to write.

---

## 7. Device Backup & Partition Pull

Navigate to **📦 Backup** in the sidebar:

* **Full Device Backup:** Creates an `.ab` archive of installed applications, shared storage, and app data.
* **Restore Backup:** Selects an existing `.ab` file and restores it to any connected device.
* **Partition Pull:** Dumps raw partition images (`boot`, `recovery`, `system`, etc.) directly from your device storage block to your PC.

---

## 8. Device Diagnostics & Info

Navigate to **📊 Device Info** to inspect over 29 hardware and system properties:
- Detailed model code, bootloader version, CPU architecture, board chipset, verified boot state, and build fingerprint.
- **[📋 Copy All Info]**: Copies all device properties formatted for forums or support tickets.
- **[💾 Export to TXT]**: Saves the diagnostic report to a text file.

---

## 9. Customizing Themes (Dark & Light)

Navigate to **⚙️ Settings ➔ Application Theme**:
- **Dark (Black & Orange):** Cyber dark aesthetic with deep black surfaces and orange glowing accents.
- **Light (White & Orange):** Clean, bright slate aesthetic with pure white surfaces and orange highlights.
- Switches instantly without restarting and remembers your preference automatically.

---

## 10. Troubleshooting & FAQs

### Q: Device says "Unauthorized" in status bar?
**Solution:** Check your phone's screen, unlock it, and accept the *"Allow USB Debugging"* popup. Check the box *"Always allow from this computer"*.

### Q: Device is stuck on "Waiting for device" in Fastboot mode?
**Solution:** Your PC is missing the Google Fastboot driver. Go to **🔧 Drivers**, run the bundled installer, and ensure your phone is listed under *Android Device ➔ Android Bootloader Interface* in Windows Device Manager.

### Q: How do I flash a Samsung `.tar.md5` file?
**Solution:** Samsung utilizes its proprietary Odin / Download mode protocol for raw `.tar.md5` archives. For non-Odin flashing, use Recovery Sideload for standard update `.zip` packages.

---

## ⚠️ Disclaimer
Flashing custom firmware, modifying partitions, and unlocking bootloaders carries inherent risks. Always ensure your device battery is charged above 50% and critical personal data is backed up before initiating flashing operations.
