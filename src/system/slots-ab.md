# A/B slots and updates

d77void Immutable keeps **two complete versions of the system** on the disk,
in two *slots* called A and B. One of them is the version you use; the other
holds the previous version, or the new one waiting to be started.

The letters say nothing about age. After an update the newest version can be
in A or in B: what matters is which slot is **running**, which one is
**confirmed**, and whether one is **waiting to be tried**.

## What is on the disk

The installation has one main partition (labelled `d77`), plus an EFI system
partition on UEFI machines. On the running system the `d77` partition is
mounted at `/run/d77/disk`:

```text
/run/d77/disk/
├── slots/
│   ├── A/   root.sqfs  vmlinuz  initramfs  manifest.json
│   └── B/   root.sqfs  vmlinuz  initramfs  manifest.json
├── state/   your /etc, /var and /root changes
├── home/    your /home
└── boot/    GRUB, on Legacy BIOS machines only (on UEFI it is on the EFI partition)
```

Each slot has the system image (`root.sqfs`), its kernel and initramfs, and a
`manifest.json` that records which version it holds. The manifest is the last
file written to a slot, so a slot without one is not complete.

The data in `state/` and `home/` is shared by both slots. See
[What is read-only and what is kept](../getting-started/overview.md#what-is-read-only-and-what-is-kept).

## Three words to keep apart

| Term | Meaning | Where the system keeps it |
|---|---|---|
| **Running slot** | the slot this boot started | `d77.slot=` in `/proc/cmdline` |
| **Confirmed slot** | the version known to work, started by default | `d77_slot` in GRUB's `grubenv` |
| **Slot on trial** | a new version GRUB starts once, on the next boot | `d77_try` in `grubenv`, then `d77_trying` |

Normally the running slot is the confirmed slot. The other slot is the
previous version.

## How an update happens

1. **Looking for a new version.** A system service, `d77-update`, looks for a
   new version 10 minutes after each boot and then every 6 hours (30 minutes
   after a failure, such as no network). Nothing is done in the live session
   or in a factory boot (see [The GRUB menu](#the-grub-menu)).
2. **Downloading into the other slot.** If there is a newer version, it is
   downloaded into the slot that is **not** running. The running system is
   never touched. This only happens while the running slot is the confirmed
   one, so the version you can fall back to is never overwritten.

   The download is about 3 GB. If the connection drops, or you switch the
   computer off, it continues later from where it stopped.
3. **Checking it.** Before the new slot is offered, its signature (minisign),
   size and SHA-256 are checked against what was published. Anything that does
   not match is thrown away.
4. **Getting it ready.** The kernel and initramfs are taken from the new
   image, the manifest is written last, and GRUB is asked to try the new slot
   **once** on the next boot.
5. **The notice.** Plasma shows **"Update ready"**. It stays on the screen
   until you close it. Nothing changes until you restart.
6. **The trial boot.** On the next boot GRUB starts the new version. It
   clears the request before starting it, so the new version is tried only
   once.
7. **Confirmation.** Once the login screen (SDDM) has been up for 15 seconds
   and the system's checks pass, the `d77-boot-ok` service makes the new slot
   the confirmed one. From then on it is the version started by default.

### If the new version does not start

If the new version never reaches the login screen (a broken kernel, a damaged
image, a hang), it is never confirmed. On the next boot (after a forced power
off, if it hung) GRUB starts the confirmed slot again, which is the version
you had. Plasma then shows **"Update did not start"**. Your files and settings
are not affected.

## The GRUB menu

The menu shows for 5 seconds:

| Entry | What it starts |
|---|---|
| `d77void` | the confirmed slot, or the slot on trial when an update is waiting |
| `d77void (factory /etc and /var, changes not kept)` | the confirmed slot with the image's own `/etc` and `/var`, in memory; nothing you change in that boot is kept |
| `d77void (previous version)` | the other slot; shown only when it holds a complete version |

The **factory** entry is for recovering from a setting that stops the system
from working: the image's configuration is used, your user accounts still
work so that you can log in, and your real settings on the disk are left as
they were.

Starting the **previous version** does not change which slot is confirmed:
the next normal boot starts the confirmed one again. In versions published
from 18 October 2026 on, Plasma shows **"Previous version in use"** when the
running slot is not the confirmed one, so that it never happens unnoticed.

## Update settings

The defaults are in `/usr/share/d77/update.conf`. To change them, write the
setting in `/etc/d77/update.conf`, which is kept across versions:

```sh
sudo mkdir -p /etc/d77
echo 'POLICY=check' | sudo tee /etc/d77/update.conf
```

| `POLICY` | Behaviour |
|---|---|
| `stage` (default) | downloads new versions and gets them ready, as described above |
| `check` | only looks; Plasma shows **"Update available"** and nothing is downloaded |
| `disabled` | does nothing |

With `POLICY=check`, download a version when you want it with:

```sh
sudo d77-update stage --now
```

## Where versions come from

Versions are published on SourceForge and signed with
[minisign](https://jedisct1.github.io/minisign/). The system only accepts
files signed with one of its trusted keys, in `/usr/share/d77/`. Only the
three most recent versions stay published. Version numbers look like
`20261015.1`: the date, then a counter for that day.

To check how to see all of this on your own machine, follow
[Checking an update](verify-update.md).
