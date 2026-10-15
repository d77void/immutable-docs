# What is kept, and what an update changes

The system you see at boot is put together from two layers: the **image** of
the version being started, which is read-only, and the **persistent data**
on the disk, which is the same for both slots.

## Path by path

| Path | Where it comes from | After a restart | After an update |
|---|---|---|---|
| `/usr` | the image, read-only | unchanged | replaced by the new image |
| `/etc` | the image, plus your changes on the disk | your changes are kept | your changes are kept; files you never changed follow the new image |
| `/var` | the image, plus your changes on the disk | kept | kept |
| `/var/db/xbps` | the image, read-only | unchanged | the new image's package list |
| `/home` | the disk | kept | kept |
| `/root` | the disk | kept | kept |
| anything else under `/`, such as `/opt` | the image, plus a layer in memory | **back to the image's** | **back to the image's** |

Your changes to `/etc` and `/var` are stored in `/run/d77/disk/state/etc/upper`
and `/run/d77/disk/state/var/upper`; your home in `/run/d77/disk/home`. You
never need to touch these folders directly.

## Where common things live

| What | Where | Kept? |
|---|---|---|
| your documents, settings and dotfiles | `/home/<you>` | yes |
| Flatpak applications installed for the whole system (Discover's default) | `/var/lib/flatpak` | yes |
| Flatpak applications installed for your user only | `~/.local/share/flatpak` | yes |
| Distrobox containers (Podman, without root) | your home | yes |
| Wi-Fi networks and other network settings | `/etc/NetworkManager` | yes |
| logs of d77void's own services | `/var/log/d77-*` | yes |
| user accounts and passwords | `/etc/passwd`, `/etc/shadow`, … | yes |
| the computer's own identity (`machine-id`) | `/var/lib/dbus/machine-id` | yes; made on the first boot, unique to each installation |

## How `/etc` follows new versions

`/etc` starts from the image's files, with your changes on top:

- A file you **changed** keeps your version, in every later version too. Your
  copy hides the image's copy, so a fix the new image brings to that file
  does not reach you.
- A file you **never changed** always follows the current image. On every
  boot, copies identical to the image's are dropped, so editing a file and
  then putting it back exactly as it was also lets it follow the image again.
- A file you **added** stays.
- A file you **deleted** stays deleted.
- **User accounts:** new system accounts and groups that a new version brings
  are added to your `passwd`, `group`, `shadow` and `gshadow`. Existing
  entries, including your users and passwords, are never changed.

### Seeing and undoing your changes

```sh
d77-etc-diff
```

lists every file in `/etc` that differs from the image, one per line:

| Word | Meaning |
|---|---|
| `changed` | you changed this file; the image's copy is hidden |
| `added` | the image does not have this file |
| `deleted` | the image has it; it was removed here |

Run it with `sudo` to also see the files only root can read.

To see what differs in one file (the image's version first, then this
system's):

```sh
d77-etc-diff sddm.conf.d/10-d77.conf
```

To put a file back exactly as the image has it (a changed or deleted file is
copied back, an added one is removed):

```sh
sudo d77-etc-diff --reset sddm.conf.d/10-d77.conf
```

Paths can be relative to `/etc`, as above, or absolute
(`/etc/sddm.conf.d/10-d77.conf`). `--reset` refuses the user accounts
(`passwd`, `group`, `shadow`, `gshadow`, …) and `/etc/fstab`, which the
installer wrote for this machine.

## Going back to the previous version

Both slots use the same `/etc`, `/var`, `/home` and `/root`. Starting the
previous version keeps your files, your applications and your settings.

One consequence: a setting you change while running the new version is still
there if you go back. If a change made with the new version stops the previous
one from working, undo it with `d77-etc-diff --reset`, or use the factory
boot described in [Recovery](recovery.md).
