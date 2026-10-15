# Services

d77void Immutable uses **runit**, like Void Linux. There is no systemd:
`systemctl` and `journalctl` do not exist. The general runit documentation in
the [Void Linux Handbook](https://docs.voidlinux.org/config/services/index.html)
applies; this page covers what is specific here.

## Where services are

| Path | What it is |
|---|---|
| `/etc/sv/<name>` | a service's definition (its `run` script) |
| `/var/service/<name>` | a link: the service is **enabled** and runit keeps it running |

`/var/service` leads to `/etc/runit/runsvdir/default`, so enabling or
disabling a service is a change to `/etc`, and is kept across restarts and
updates like any other. See [What is kept](../system/persistence.md).

Only services whose programs are part of the image can be used: there is no
package manager to add new ones. Programs in a Distrobox container are not
system services.

## Everyday commands

The state of every enabled service:

```sh
sudo sv status /var/service/*
```

Restart, stop or start one (until the next boot):

```sh
sudo sv restart NetworkManager
sudo sv down bluetoothd
sudo sv up bluetoothd
```

Enable a service that is in the image but not enabled, permanently:

```sh
sudo ln -s /etc/sv/<name> /var/service/
```

Disable one permanently:

```sh
sudo rm /var/service/<name>
```

A service the image enables and you disabled shows up in `d77-etc-diff` as
`deleted  runit/runsvdir/default/<name>`. To enable it again, create the link
as above.

## Services enabled by default

| Service | What it does |
|---|---|
| `d77-update` | looks for, downloads and prepares new versions; see [A/B slots and updates](../system/slots-ab.md) |
| `d77-boot-ok` | confirms a new version after it started; do not disable |
| `d77-firstboot-flatpak` | installs Firefox from Flathub on the first boot with a network connection, then stays idle |
| `sddm` | the login screen |
| `dbus`, `udevd`, `polkitd` | system plumbing; do not disable |
| `NetworkManager` | network and Wi-Fi |
| `bluetoothd` | Bluetooth |
| `cupsd`, `cups-browsed` | printing |
| `chronyd` | keeps the clock right |
| `power-profiles-daemon` | power profiles in Plasma |
| `zramen` | compressed swap in memory (there is no swap partition) |
| `acpi-gpe-guard` | detects and silences a runaway ACPI interrupt (a firmware bug on some laptops); does nothing on a healthy machine |
| `agetty-tty1` … `agetty-tty6` | the text consoles (Ctrl+Alt+F1 … F6) |

To stop the system from updating, do not disable `d77-update`: set
`POLICY=disabled` (or `check`) as described in
[Update settings](../system/slots-ab.md#update-settings).

## Logs

d77void's own services keep their logs in `/var/log/<name>/current`, with
times in UTC:

```sh
sudo tail -n 20 /var/log/d77-update/current
sudo tail -n 20 /var/log/d77-boot-ok/current
sudo tail -n 20 /var/log/d77-firstboot-flatpak/current
```

Kernel messages:

```sh
sudo dmesg | tail -n 50
```

## Your own service

A service of your own is a folder in `/etc/sv` with an executable `run`
script that starts the program in the foreground. It is kept like the rest of
`/etc`. Its program must be somewhere that survives a restart (your home, or
the script itself), never `/opt` or `/usr`.

```sh
sudo mkdir /etc/sv/my-service
sudo nano /etc/sv/my-service/run
sudo chmod +x /etc/sv/my-service/run
sudo ln -s /etc/sv/my-service /var/service/
```

A minimal `run` script:

```sh
#!/bin/sh
exec 2>&1
exec /home/<you>/bin/my-program
```
