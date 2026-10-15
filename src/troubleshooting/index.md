# Common problems

Problems seen on real installations, with what causes them and what to do.

## The update download is very slow, or keeps stopping

Updates are about 3 GB and come from SourceForge, which often serves them at
a few hundred KB/s and sometimes drops long connections
(`Connection reset by peer` in the update log).

Nothing needs to be done: the download continues from where it stopped, by
itself. It retries for about 5 minutes and, if the connection is still down,
tries again 30 minutes later. Switching the computer off is fine too; the
next boot continues the same download.

A wired connection helps. While a download is running, the computer does
not go to sleep on its own.

To watch it, see step 5 of [Checking an update](../system/verify-update.md#5-whether-a-new-version-is-published-downloading-or-ready).

## No "Update ready" notice appeared

- The first look of each boot waits 10 minutes, then every 6 hours. A
  download then takes a while.
- The notice is shown once per session and stays until you close it. If it
  was closed, `cat /run/d77/update-ready` still shows the waiting version.
- With `POLICY=check`, the notice is **"Update available"** instead, and
  nothing is downloaded until you run `sudo d77-update stage --now`.
- Nothing is downloaded while the previous version is running; see below.

[Checking an update](../system/verify-update.md) shows where things stand.

## Another operating system starts instead of d77void (UEFI)

d77void installs its boot loader in the standard place every UEFI firmware
can start (`EFI/BOOT/BOOTX64.EFI`), without adding an entry of its own to
the firmware's boot list. If another system was installed before, its entry
may still come first.

Change the boot order in the firmware setup (or pick the disk from the
firmware's boot menu), and remove the old system's entry if that system is
gone. Seen on a NovaCustom NV41 with Dasharo.

## The previous version starts without being chosen

Seen on a Lenovo T480s with Libreboot: when the firmware's SeaBIOS did not
find the disk, the computer was started through the GRUB built into
Libreboot, which then loaded d77void's menu. That menu could not read its own
settings in that case and started slot A, which was the previous version.

Fixed in versions published from 18 October 2026 on; existing installations
are fixed by the first such version once it has been confirmed. Those
versions also show **"Previous version in use"** whenever the running slot is
not the confirmed one. See [Recovery](../system/recovery.md#you-keep-landing-on-the-previous-version).

## `xbps-install` fails

Expected: the system's files and package database are read-only. Install the
program with Flatpak or inside a Distrobox container; see
[Where to install applications](../applications/choosing-method.md).

## A program copied into `/usr` or `/opt` does not work or disappears

`/usr` is read-only and `/opt` is emptied on every boot. Keep your own
programs in your home, or use Flatpak, Distrobox or an AppImage.

## A change to a file in `/etc` did not stick

Changes to `/etc` are kept. If one seems lost:

1. Check that the editor really saved the file. In `vi`/`vim`, `:wq` saves
   and quits; `:q!` quits **without** saving.
2. Run `d77-etc-diff`: a file you changed is listed as `changed`. If it is
   not listed, the change was not saved, or it was identical to the image's.

Seen on a Librebox LT1000: a line added to `/etc/fstab` with `vi` was missing
after a restart; the file had never been saved. Writing it again kept it.

## Firefox is not installed

Firefox comes from Flathub and is installed on the **first boot with a
network connection**, in the background, a few minutes after the desktop
appears. Without a network it tries again every minute.

```sh
sudo tail -n 20 /var/log/d77-firstboot-flatpak/current
```

## `distrobox stop` hangs

On a system without systemd, a container that shares the system's processes
cannot be stopped cleanly. d77void Immutable creates every new container with
its own processes, which avoids this. A container created elsewhere, or with
an old configuration, can be recreated with `--unshare-process`; see
[Distrobox](../applications/choosing-method.md#distrobox).

## Reporting a problem

Include:

- the running version: `grep IMAGE_VERSION /etc/os-release`;
- the machine and its firmware (UEFI, Legacy BIOS, coreboot, Libreboot);
- the outputs of steps 2, 3 and 7 of [Checking an update](../system/verify-update.md)
  if it is about updates or booting;
- what you did, what you expected, and what happened.
