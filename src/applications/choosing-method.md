# Where to install applications

The system image is read-only, so programs are not installed into it. There
are three ways to add software, each kept outside the image and untouched by
system updates:

| You want | Use | Kept in |
|---|---|---|
| a desktop application (browser, office, media, games) | **Flatpak**, from Discover or Flathub | `/var` (system-wide) or your home |
| command-line or development tools, or anything that needs a package manager | **Distrobox** | your home |
| a program only offered as an `.AppImage` file | **AppImage** | your home |

Try them in that order: Flatpak first, Distrobox when there is no Flatpak or
the tool is for the terminal, AppImage when it is the only option.

## Flatpak

Flatpak is the main way to install desktop applications. **Discover** (the
Plasma software centre) uses Flathub, which is already set up. Firefox is
installed from Flathub on the first boot with a network connection.

Flatpak applications live outside the image, so they stay installed across
system updates and when you go back to the previous version.

From the terminal:

```sh
flatpak search libreoffice
flatpak install flathub org.libreoffice.LibreOffice
flatpak update
flatpak list --app
flatpak uninstall org.libreoffice.LibreOffice
```

Flatpak applications are updated through Discover or `flatpak update`,
separately from the system's own updates.

**Limitations.** Applications run in a sandbox and see only the folders and
devices they are allowed to. If an application cannot open a folder or a
device, its permissions can be changed with
[Flatseal](https://flathub.org/apps/com.github.tchx84.Flatseal) (also on
Flathub).

## Distrobox

Distrobox gives you a full Linux distribution in a container, with a working
package manager, sharing your files and your display with the system. The
read-only system is never touched. It uses Podman, without root.

A Void container whose home is a separate folder, so its settings stay out of
yours:

```sh
mkdir -p ~/boxes/Void
distrobox create --name void \
  --image ghcr.io/void-linux/void-glibc-full:latest \
  --home ~/boxes/Void \
  --unshare-process
distrobox enter void
```

Inside it, packages install as on a regular Void:

```sh
sudo xbps-install -S htop
```

The first `create` downloads the image and the first `enter` sets the
container up, so both take a while. Any other distribution works too, for
example `docker.io/library/debian` or `quay.io/fedora/fedora`.

A graphical program installed inside the container can be added to the
system's menu by running, inside the container:

```sh
distrobox-export --app <program>
```

| Command | |
|---|---|
| `distrobox list` | the containers and their state |
| `distrobox enter <name>` | a shell inside it |
| `distrobox stop <name>` | stops it |
| `distrobox rm <name>` | removes it (a `--home` folder is kept) |

On d77void Immutable every new container gets its own processes, as with
`--unshare-process`; without that, `distrobox stop` hangs on a system without
systemd. The option is in the recipe so that it works on other systems too.

Containers and their files live in your home, so they are kept across system
updates.

## AppImage

An AppImage is a single file that contains a program. Keep it in your home,
for example in `~/Applications`, make it executable and run it:

```sh
mkdir -p ~/Applications
mv ~/Downloads/Program.AppImage ~/Applications/
chmod +x ~/Applications/Program.AppImage
~/Applications/Program.AppImage
```

The image includes what most AppImages need to start (FUSE 2, with
`libfuse.so.2` and `fusermount`). To get menu entries and keep them tidy,
[Gear Lever](https://flathub.org/apps/it.mijorus.gearlever) (on Flathub)
manages AppImages for you.

> **Not yet verified on an installed system.** The pieces AppImages rely on
> are in the image, but running an AppImage has not been tested on a real
> installation yet. If you try one, please report whether it worked.

AppImages do not update themselves unless the program has its own updater;
Gear Lever can help with that.

## What does not work, and why

- **`sudo xbps-install` on the system.** The system's files and package
  database are read-only, so it fails. Use Distrobox for packages.
- **Copying a program into `/usr`** (for example with `sudo install … /usr/…`
  or `make install`). `/usr` is read-only.
- **Installing into `/opt`.** It is writable, but emptied on every boot.
- **Changing the image for one program.** Anything that must be part of the
  system comes with a new version of the image.
