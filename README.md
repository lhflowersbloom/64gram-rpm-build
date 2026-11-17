# 64Gram RPM for Fedora, RHEL and openSUSE

[![Build 64Gram RPM](https://github.com/lhflowersbloom/64gram-rpm-build/actions/workflows/build-64gram-rpm.yml/badge.svg)](https://github.com/lhflowersbloom/64gram-rpm-build/actions/workflows/build-64gram-rpm.yml)

Unofficial **RPM packaging of [64Gram](https://github.com/TDesktop-x64/tdesktop)**, the x86_64 fork of Telegram Desktop.
One package for Fedora, RHEL 8+, AlmaLinux, Rocky Linux and openSUSE — built to **replace `telegram-desktop`**,
not to sit next to it fighting over `tg://` links.

## Install

Grab the newest `.rpm` from [Releases](../../releases/latest), then:

```bash
sudo dnf install ./64gram-<ver>-<rel>.x86_64.rpm
```

Command is `64gram`, menu entry is **64Gram**. There is no repository to add — upgrading means installing a newer file,
removing means `sudo dnf remove 64gram`.

Dropping the official client is deliberate: the package declares `Obsoletes: telegram-desktop`, because two clients
claiming `x-scheme-handler/tg` make the target of a clicked link undefined.

64Gram 1.2.13 moved its profile to `~/.local/share/64Gram` (earlier 64Gram releases and the official client use
`~/.local/share/TelegramDesktop`). Coming from an older build, rename the folder **after quitting 64Gram completely**,
otherwise the client starts signed out:

```bash
mv ~/.local/share/TelegramDesktop ~/.local/share/64Gram
```

## Package contents

| Path | Purpose |
| --- | --- |
| `/usr/bin/64gram` | upstream `64Gram` binary |
| `/usr/bin/telegram-desktop` | symlink, for scripts that look the client up by that name |
| `/usr/share/applications/io.github.tdesktop_x64.TDesktop.desktop` | menu entry + `tg` / `tonsite` / `ton` handlers |
| `/usr/share/dbus-1/services/io.github.tdesktop_x64.TDesktop.service` | D-Bus activation |
| `/usr/share/metainfo/io.github.tdesktop_x64.TDesktop.metainfo.xml` | AppStream data |
| `/usr/share/icons/hicolor/{16,32,48,64,128,256,512}/apps/` | icons |
| `/usr/share/licenses/64gram/LICENSE` | GPLv3 + OpenSSL exception |

Runtime dependencies are only `libX11`, `libxcb` and `libxkbcommon`; the binary already carries Qt, OpenSSL, ffmpeg
and WebRTC. The release carries **no dist tag**, so the same RPM serves RHEL-family 8+ and openSUSE as well as Fedora.

## How it is built

A [workflow](.github/workflows/build-64gram-rpm.yml) polls the upstream release feed **every Monday at 06:00 UTC** and
publishes only when the version is new. 64Gram ships Linux as a raw `.zip` from a CI image that is not publicly
pullable, so there is no source-build path: the published binary is repackaged the way distro `-bin` packages are.
Before a release, the RPM is installed with `dnf` in a clean Fedora container and its `Provides:`, `Obsoletes:` and
handler registration are checked — a broken package fails the build instead of reaching you.

## Layout

```
.github/workflows/build-64gram-rpm.yml                    # build, smoke test, publish
packaging/64gram.spec                                     # RPM spec
packaging/io.github.tdesktop_x64.TDesktop.desktop         # desktop entry
packaging/io.github.tdesktop_x64.TDesktop.service         # D-Bus service
packaging/io.github.tdesktop_x64.TDesktop.metainfo.xml    # AppStream metadata
docs/index.html                                           # landing page (GitHub Pages)
```

## 中文速览

- 给 64Gram 做 RPM，定位是**替代官方 `telegram-desktop`**：`tg://`、`tonsite://`、`ton://` 全部归它处理。
- 装：从 Releases 下最新的包，`sudo dnf install ./64gram-<ver>-<rel>.x86_64.rpm`；卸：`sudo dnf remove 64gram`。
- 无 dist tag，一个包覆盖 Fedora 与 RHEL 系 8+、openSUSE；依赖只有 `libX11`/`libxcb`/`libxkbcommon`。
- 每周一自动跟随上游发版；会话数据自 1.2.13 起在 `~/.local/share/64Gram`（旧版升级需手动改名，见上文）。

## License

Packaging lives in this repository. 64Gram itself is GPLv3 with an OpenSSL exception, copyright its authors.
This project is unaffiliated with 64Gram and Telegram.
