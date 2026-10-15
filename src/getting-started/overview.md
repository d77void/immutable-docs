# What d77void Immutable is

d77void Immutable is a variant of d77void where the operating system is a
single **read-only image**. You do not install or update packages one by one:
a new version of the whole system arrives as a new image, and the previous one
stays on the disk so you can go back to it.

"Immutable" means the same here as on Fedora Silverblue: the system files do
not change while it runs, but your settings, your data and your applications
are kept.

- **Base:** Void Linux (glibc, x86_64) with runit. There is no systemd.
- **Desktop:** KDE Plasma.
- **Applications:** Flatpak (Discover and Flathub) for graphical programs,
  Distrobox for command-line and development tools. See
  [Where to install applications](../applications/choosing-method.md).
- **Updates:** automatic, whole-image, signed, with automatic fallback. See
  [A/B slots and updates](../system/slots-ab.md).

## How it differs from a regular Void installation

| | Regular Void | d77void Immutable |
|---|---|---|
| The system | files installed by packages, changed in place | one read-only image per version |
| Installing software | `xbps-install` | Flatpak, Distrobox, AppImage |
| Updating | `xbps-install -Su`, package by package | a whole new image, in the background |
| If an update breaks something | fix it by hand | the previous version is still there |
| Package manager on the installed system | yes | no: `xbps-install` fails on purpose |

`xbps-install` is present in the image, but it cannot change anything: the
system's files and the package database are read-only. That is expected, not
an error. Use the methods in
[Where to install applications](../applications/choosing-method.md) instead.

## What is read-only and what is kept

At boot, the system puts together its root directory from the image of the
version being started and from the persistent data on the disk:

| Path | Behaviour |
|---|---|
| `/usr` | **Read-only.** Comes from the image; a new version replaces it. |
| `/etc` | **Kept.** Your changes are stored on the disk, on top of the image's files. |
| `/var` | **Kept.** System Flatpak applications, logs, network settings and other state live here. |
| `/home` | **Kept.** Your files. |
| `/root` | **Kept.** The root user's home. |
| Everything else under `/` (for example `/opt`) | **Writable, but reset on every boot.** Anything written there is gone after a restart. |

The kept data is the same whichever version you start: going back to the
previous version keeps your files and settings.

### What "kept" means for `/etc`

`/etc` starts from the image's files. When you change a file, your copy is
kept and **hides the image's copy from then on**, including in later
versions. Files you never touched always follow the current image, so they
receive the fixes each new version brings.

To see which files in `/etc` differ from the image:

```sh
d77-etc-diff
```

Each line says `changed`, `added` or `deleted`, then the path. To see the
differences in one file (the image's version first):

```sh
d77-etc-diff sddm.conf.d/10-d77.conf
```

To put one file back as the image has it:

```sh
sudo d77-etc-diff --reset sddm.conf.d/10-d77.conf
```

`--reset` refuses the user accounts (`passwd`, `group`, `shadow`, …) and
`fstab`, which must stay as this installation has them. Run `d77-etc-diff`
with `sudo` to see every file, including the ones only root can read.

## Things that work differently

- **Do not copy programs into `/usr` or `/opt`.** `/usr` is read-only, and
  `/opt` is emptied on every boot. Put them in your home, or use one of the
  methods in [Where to install applications](../applications/choosing-method.md).
- **Changes to the system itself come with a new version**, not by editing
  it on the running machine.
- **Restarting is how an update takes effect.** The new version is
  downloaded in the background and starts on the next boot.
