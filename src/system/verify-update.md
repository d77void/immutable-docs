# Checking an update

## When to use this

- After restarting for an update, to confirm the new version is the one
  running and that it was confirmed.
- When you expected an update and saw no notice.
- When something looks odd: a version you did not expect, or an update that
  did not start.

Read [A/B slots and updates](slots-ab.md) first if the words *running*,
*confirmed* and *on trial* are new to you.

## What to expect

On a healthy system, the running slot and the confirmed slot are the same,
and `grubenv` has no trial pending. While an update is being downloaded, a
partial file grows in the other slot. After the restart, the other slot is
running and, about 15 seconds after the login screen appears, it becomes the
confirmed one.

## Procedure

Run these in Konsole. The commands with `sudo` ask for your password.

### 1. Which version is running

```sh
grep IMAGE_VERSION /etc/os-release
```

```text
IMAGE_VERSION="20261015.1"
```

### 2. Which slot is running

```sh
cat /proc/cmdline
```

Look for `d77.slot=`. For example, `d77.slot=A` means this boot started
slot A. If the line also contains `d77.pristine`, this is a factory boot.

### 3. Which slot is confirmed, and whether a trial is pending

On a UEFI machine:

```sh
sudo grub-editenv /boot/efi/boot/grub/grubenv list
```

On a Legacy BIOS machine (including coreboot with SeaBIOS):

```sh
sudo grub-editenv /boot/grub/grubenv list
```

```text
d77_slot=A
d77_try=
d77_trying=
```

| Line | Meaning |
|---|---|
| `d77_slot=A` | slot A is the confirmed slot |
| `d77_try=B` | an update in slot B is ready and will be tried on the next boot |
| `d77_trying=B` | slot B was started on trial and is not confirmed yet |
| empty `d77_try=` and `d77_trying=` | nothing pending |

### 4. Which version each slot holds

```sh
jq -r .version /run/d77/disk/slots/A/manifest.json /run/d77/disk/slots/B/manifest.json
```

One version per line, slot A first. A slot that has never held a complete
version has no manifest and gives an error instead.

### 5. Whether a new version is published, downloading or ready

Ask the server whether there is something newer than the running version:

```sh
d77-update check
```

It prints `available <version>`, `current <version>` (you have the latest)
or `disabled` (`POLICY=disabled`).

A version that is downloaded and waiting for a restart is recorded here:

```sh
cat /run/d77/update-ready
```

To see a download in progress, list the partial file; run it again a minute
later and the size should have grown:

```sh
sudo ls -l /run/d77/disk/slots/*/root.sqfs.*.part
```

"No such file" means nothing is downloading: either there is nothing new, the
download has finished, or it has not started yet (the first look of a boot
waits 10 minutes).

### 6. What the update service did

```sh
sudo tail -n 20 /var/log/d77-update/current
```

Each line starts with the time, in UTC. Common lines:

| Line | Meaning |
|---|---|
| `current 20261015.1` | looked; nothing newer |
| `downloading 20261018.1: 2712 MiB` | started downloading (systems on 20261015.1 or newer) |
| `downloading 20261018.1: resuming at 600 of 2712 MiB` | continuing an interrupted download |
| `staged 20261018.1` | downloaded, checked and ready for the next boot |
| `d77-update: slot A is not confirmed yet (d77_slot=B): not staging over the slot to fall back to` | the running slot is not the confirmed one, so nothing is downloaded |
| `d77-update: …` (anything else) | an error, with its reason; the service tries again in 30 minutes |

`sudo tail -f` instead of `sudo tail -n 20` keeps showing new lines as they
arrive; press Ctrl+C to stop it. It never ends by itself.

### 7. What happened at boot

```sh
sudo tail -n 20 /var/log/d77-boot-ok/current
```

| Line | Meaning |
|---|---|
| `slot B on trial, waiting for SDDM` | the new version in B started and is being checked |
| `slot B confirmed` | the new version is now the confirmed one |
| `slot B is the confirmed slot, nothing to do` | a normal boot of the confirmed slot |
| `slot A failed its trial, back on slot B` | the update in A did not start; the system went back to B |
| `slot A booted, not the confirmed slot B (…)` | the previous version was started (systems published from 18 October 2026) |
| `not a normal boot of an installed slot, nothing to do` | a live session or a factory boot |

## How to read the results

| What you see | What it means |
|---|---|
| `d77.slot` equals `d77_slot`, nothing pending | all is well |
| `d77_try` set, "Update ready" on screen | an update is waiting: restart to start it |
| after a restart, `d77.slot` equals `d77_slot`, both the new slot | the update went through and was confirmed |
| `d77_trying` set and equal to `d77.slot` | the new version is still on trial; wait for the login screen and 15 seconds |
| back on the old slot, "Update did not start" | the update failed and the system went back by itself; nothing was lost |
| `d77.slot` differs from `d77_slot`, nothing pending | the previous version is running; restart to go back to the confirmed one |

## If something goes wrong

- **The new version does not start.** Do nothing special: switch the computer
  off and on again if it hung. The next boot goes back to the confirmed
  version on its own.
- **A setting you changed stops the system from working.** Choose
  `d77void (factory /etc and /var, changes not kept)` in the GRUB menu, then
  find and fix the file with `d77-etc-diff`; see
  [What "kept" means for /etc](../getting-started/overview.md#what-kept-means-for-etc).
- **You keep landing on the previous version without choosing it.** Note the
  output of steps 2 and 3 and of step 7, and report it.
