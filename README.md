# 64gram-rpm-build

给 [64Gram](https://github.com/TDesktop-x64/tdesktop)（Telegram Desktop 的非官方 64 位增强分支）做 RPM 包，由 GitHub Actions 自动构建。

定位是**替代官方 `telegram-desktop`**：装完之后系统里只有它这一个 Telegram 客户端，`tg://`、`tonsite://`、`ton://` 全部归它处理。

## 安装

从 [Releases](../../releases) 下最新的包：

```bash
sudo dnf install ./64gram-<ver>-2.*.x86_64.rpm
```

装完在应用菜单里叫 **64Gram**，命令是 `64gram`（另带 `/usr/bin/telegram-desktop` 软链，方便按文件名找客户端的脚本）。

卸载：

```bash
sudo dnf remove 64gram
```

已装官方 `telegram-desktop` 的话，`dnf install` 会把它替换掉（本包 `Obsoletes: telegram-desktop`），
这是刻意的——否则两个客户端都声明 `x-scheme-handler/tg`，点链接到底开谁就变成随机事件了。会话数据仍在
`~/.local/share/TelegramDesktop`，卸载后换回官方版不会丢。

## 为什么是重打包而不是源码编译

上游只发 `64Gram_<ver>_linux.zip`（裸二进制 + Updater），没有 deb/rpm，**也没有公开的源码构建通道**——
它自己的 Linux CI 依赖 `ghcr.io/tdexktop-x64/tdesktop/centos_env`，那个镜像是私有的。

所以走发行版常见的 `-bin` 路线：拿官方发布的二进制，补齐桌面集成后打成 RPM。这个二进制把 Qt / OpenSSL /
ffmpeg / WebRTC 全部静态链进去了，ELF 动态依赖只有 15 个系统库（glibc、glib、cairo、pango、fontconfig、
freetype），也没有调试段，因此 RHEL/Rocky/Alma 8+ 与 Fedora 都能直接装。

## 包内容

| 路径 | 说明 |
| --- | --- |
| `/usr/bin/64gram` | 上游 `Telegram` 二进制 |
| `/usr/bin/telegram-desktop` | 指向上面的软链，满足按文件名找客户端的脚本 |
| `/usr/share/applications/io.github.tdesktop_x64.TDesktop.desktop` | 菜单项 + `tg` / `tonsite` / `ton` scheme handler |
| `/usr/share/dbus-1/services/io.github.tdesktop_x64.TDesktop.service` | DBus 激活（`DBusActivatable=true` 需要） |
| `/usr/share/metainfo/io.github.tdesktop_x64.TDesktop.metainfo.xml` | AppStream 数据 |
| `/usr/share/icons/hicolor/{16,32,48,64,128,256,512}/apps/` | `64gram.png`，另外 256/512 各带一个 app-id 别名的软链 |
| `/usr/share/licenses/64gram/LICENSE` | GPLv3 + OpenSSL 例外 |

### 为什么文件名是 `io.github.tdesktop_x64.TDesktop.*`

二进制里写死了 `QGuiApplication::setDesktopFileName("io.github.tdesktop_x64.TDesktop")`
（`Telegram/SourceFiles/platform/linux/specific_linux.cpp`）。Wayland 下窗口的 `app_id` 就是它，
桌面环境拿它去匹配同名的 `.desktop` 才能对上图标、dock 分组和通知归属。四件套（desktop / dbus service /
metainfo / app_id）必须同名，缺一个就会掉成通用图标。

图标名刻意保留 `64gram` 而不是跟着上游用 `org.telegram.desktop`——后者会和发行版官方 `telegram-desktop`
包的文件路径撞车。

## 自己触发一次构建

Actions → **Build 64Gram RPM** → *Run workflow*，`version` 填 `1.2.11` 或留 `latest`
（自动查上游最新 release）。产物在 workflow 的 artifact 里；勾选 `publish`（默认开）会额外建一个
GitHub Release。push `build-*` 形式的 tag 也会触发构建并发布。

构建完会自动跑一次**冒烟测试**：在干净的 almalinux:9 容器里真装一遍，断言依赖能解、`mimeinfo.cache` 里
`x-scheme-handler/tg` 指向本包。也就是说"tg:// 会不会跳到 64Gram"是每次构建都验过的，不靠猜。

## 已知取舍

- **不做 strip，也不打包 `Updater`**：保留二进制原样，自动更新在 `/usr/bin` 下本来就写不进去，
  升级请走 `dnf`。因此安装包偏大（约 77 MB），和上游 zip 一个量级。
- **两个版本号**：包版本是 64Gram 自己的 `1.2.11`，`Provides` 声明的是它基于的 Telegram Desktop 版本
  `7.3.5`（构建时从上游 release 提交信息 `Upstream version: X` 里自动解析，解析不到就用 spec 默认值）。
- `Requires` 里显式写了 `libX11` / `libxcb` / `libxkbcommon`，这三个是 Qt 平台插件 dlopen 的，
  不会出现在 ELF 的 `NEEDED` 里；名字取的是 Fedora/RHEL 的包名，openSUSE 上可能需要 `--nodeps`。

## 仓库结构

```
.github/workflows/build-64gram-rpm.yml                    # 下载上游 zip → rpmbuild → 冒烟测试 → 发布
packaging/64gram.spec                                     # RPM spec（gver / uver 用 --define 覆盖）
packaging/io.github.tdesktop_x64.TDesktop.desktop         # 桌面入口
packaging/io.github.tdesktop_x64.TDesktop.service         # DBus 服务
packaging/io.github.tdesktop_x64.TDesktop.metainfo.xml    # AppStream 元数据
```

图标不放在仓库里，构建时从上游 `Telegram/Resources/art/` 拉取。

手动在本地复现：

```bash
# 需要 docker
mkdir -p stage dist
unzip -o -q 64Gram_1.2.11_linux.zip -d stage
curl -fLo stage/LICENSE https://raw.githubusercontent.com/TDesktop-x64/tdesktop/dev/LICENSE
cp packaging/io.github.tdesktop_x64.TDesktop.* stage/
for sz in 16 32 48 64 128 256 512; do
  curl -fLo "stage/icon${sz}.png" "https://raw.githubusercontent.com/TDesktop-x64/tdesktop/dev/Telegram/Resources/art/icon${sz}.png"
done
tar -C stage -czf stage.tgz .

docker run --rm -u 0 -v "$PWD:/w" -w /w almalinux:8 bash -lc '
  dnf -y -q install rpm-build
  mkdir -p /tmp/r/{SOURCES,SPECS,RPMS,BUILD,BUILDROOT}
  tar -C /tmp/r/SOURCES -xzf /w/stage.tgz
  rpmbuild -bb --define "_topdir /tmp/r" --define "gver 1.2.11" --define "uver 7.3.5" /w/packaging/64gram.spec
  cp /tmp/r/RPMS/x86_64/*.rpm /w/dist/'
```

## 许可

打包脚本随本仓库；64Gram 本体为 GPLv3 + OpenSSL 例外，版权归其作者。
本仓库与 64Gram 项目无关，只是第三方打包。
