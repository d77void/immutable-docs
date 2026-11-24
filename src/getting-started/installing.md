# Installing

> **No ISO to download yet.** Until the Technology Preview, the ISO is built
> from the [d77-immutable](https://github.com/d77void/d77-immutable)
> repository; its `INSTALL.md` explains how. Installed systems then update
> themselves every week.

## What the machine needs

| | Minimum (the installer refuses less) | Recommended |
|---|---|---|
| Processor | x86_64 | |
| Firmware | UEFI or Legacy BIOS | |
| Memory | 2 GB | 4 GB |
| Disk | 16 GB | 24 GB or more |

- Plan for the **whole disk**: the supported choice in the installer is
  **Erase disk**, which wipes it entirely. Installing next to another system
  on the same disk is not supported.
- On UEFI, **Secure Boot must be off**: the boot loader is not signed yet.
- No network connection is needed to install.

## Steps

1. Write the ISO to a USB stick, for example:

   ```sh
   sudo dd if=d77void-live-x86_64-<date>-plasma.iso of=/dev/sdX bs=4M status=progress
   ```

   Check twice that `/dev/sdX` is the stick (`lsblk` lists the disks):
   everything on it is erased.
2. Boot the machine from the stick. The live session opens Plasma as user
   `anon` (password `voidlinux`). You can try the system there first;
   nothing is written to the disk until the installer runs.
3. Double-click **Install d77void** on the desktop.
4. Follow the steps: language, location and time zone, keyboard, disk
   (choose **Erase disk**; on an empty disk it is the only choice), and your
   user and password.
5. When the installer says **All done.**, restart and remove the stick.

The live session has no package manager, and the installed system does not
either: see [What d77void Immutable is](overview.md).

## What the installer does

- **Partitions:** created automatically. GPT with an EFI partition on UEFI;
  MBR on Legacy BIOS. Installing on Legacy BIOS to a GPT disk needs an
  existing `bios_grub` partition.
- **Not offered:** encryption, LVM, a swap partition, extra partitions.
- **Swap:** compressed in RAM (zram, half of the RAM, at most 8 GB). There is
  therefore no hibernation.
- **The system:** copied into slot A, ready to receive updates in slot B. See
  [A/B slots and updates](../system/slots-ab.md).
- **The installer itself and Firefox** belong to the live session only; they
  are not copied to the disk.

## After the first boot

- On UEFI the system boots from the firmware's default path
  (`EFI/BOOT/BOOTX64.EFI`) and does not add a boot entry of its own. If
  another system still starts first, change the boot order in the firmware
  settings.
- With a network connection, Firefox is installed from Flathub on the first
  boot. Other programs: [Where to install applications](../applications/choosing-method.md).
- Updates need nothing from you: three minutes after boot, and then every
  6 hours, the system looks for a newer image and downloads it in the
  background. See [A/B slots and updates](../system/slots-ab.md).

---

*Checked on 24 November 2026 against the code of version 20261124.1, and by
installing that version in a UEFI virtual machine on an empty disk.*
