# Recovery

Most problems on d77void Immutable are undone without reinstalling: the
previous version is still on the disk, the system's own files cannot be
damaged, and your changes to the configuration can be bypassed or undone one
by one.

Pick the case that matches.

## An update did not start

**What you see:** after restarting for an update, the computer hangs, shows
errors, or never reaches the login screen.

**What to do:** nothing special. If it hangs, hold the power button to switch
it off, then switch it on again.

**What happens:** the new version was started on trial, only once. Because it
never reached the login screen, it was never confirmed, so the next boot
starts the confirmed version again: the one you had before the update. Plasma
then shows **"Update did not start"**. Your files and settings are not
affected.

Check it with [Checking an update](verify-update.md): the running slot and
the confirmed slot are the old one again, and the boot log has a line like
`slot A failed its trial, back on slot B`.

## The new version starts, but something does not work

**What to do:** in the GRUB menu, which shows for 5 seconds when the computer
starts, choose **`d77void (previous version)`**.

This starts the other slot, with the version you had before, and the same
files and settings. It changes nothing on the disk: the next normal boot
starts the confirmed version again. To stay on the previous version, choose
the entry on every boot until a fixed version is published.

The entry only shows when the other slot holds a complete version: after the
first update, and not while a new version is being downloaded into it.

Please report what did not work, with the version numbers from
[Checking an update](verify-update.md).

## A setting stops the system from working

**What you see:** after changing something in `/etc` (a configuration file,
a service, the display manager), the system no longer starts properly, or you
cannot log in to the desktop.

**What to do:**

1. In the GRUB menu, choose
   **`d77void (factory /etc and /var, changes not kept)`**.

   This starts the confirmed version with the image's own `/etc` and `/var`,
   as on a fresh installation, held in memory. Your user accounts and
   passwords, and `sudo` rights, are carried over so that you can log in.
   Nothing you change in this boot is kept, and your real settings on the
   disk are left as they were. Updates do not run in this mode.

2. Log in, open Konsole and list your changes to `/etc`:

   ```sh
   sudo d77-etc-diff
   ```

   This lists what differs between the image and **your real settings on the
   disk**, not the factory ones in use in this boot. Look for the file you
   changed. To read your version of it, look at the copy on the disk, for
   example `sudo cat /run/d77/disk/state/etc/upper/sddm.conf.d/10-d77.conf`
   (in this boot, `/etc` itself shows the image's version).

3. Still in the factory boot, remove your copy of that file from the disk.
   Your changes to `/etc` are stored as files in
   `/run/d77/disk/state/etc/upper`; without your copy, the image's version is
   used again from the next boot on. For example, for
   `/etc/sddm.conf.d/10-d77.conf`:

   ```sh
   sudo rm /run/d77/disk/state/etc/upper/sddm.conf.d/10-d77.conf
   ```

   **Never remove** `passwd`, `group`, `shadow`, `gshadow`, `subuid`,
   `subgid`, `sudoers.d` or `fstab` from that folder: they hold this
   computer's users, passwords and disks, and without them nobody can log in.

4. Restart normally.

On a system that still starts, the same is done more safely with
`sudo d77-etc-diff --reset <path>`, which refuses the accounts and `fstab`;
see [What is kept](persistence.md#seeing-and-undoing-your-changes).

> **Not yet verified on a real installation:** this procedure follows from how
> the factory boot and `d77-etc-diff` are written (the factory boot keeps the
> disk mounted at `/run/d77/disk`, and `d77-etc-diff` reads your changes from
> there), but it has not been tried end to end yet.

## A service misbehaves

Restart it, stop it or disable it with runit; see [Services](../administration/services.md).
Services that are part of the image come back with their image
configuration when you `--reset` their files.

## You keep landing on the previous version

**What you see:** Plasma shows **"Previous version in use"** (versions
published from 18 October 2026 on), or [Checking an update](verify-update.md)
shows a running slot different from the confirmed one, and you did not choose
the previous version in the menu.

This happened when the computer was started by another boot loader that then
loaded d77void's menu, such as the GRUB built into Libreboot. Versions
published from 18 October 2026 on read GRUB's settings correctly from any boot
loader, and fix the menu of an existing installation by themselves once they
have been confirmed. Restarting through the computer's normal boot path
starts the confirmed version.

If it keeps happening on a recent version, please report it with the output
of steps 2, 3 and 7 of [Checking an update](verify-update.md).

## What cannot break

- **The system's own files** (`/usr`) are read-only and come from a signed
  image; nothing on the running system can change them.
- **A download that fails or is corrupted** is thrown away before it is ever
  offered; the slot you are using is never written to by an update.
- **The version you fall back to** is never overwritten: a new version is
  only downloaded while the running version is the confirmed one.
