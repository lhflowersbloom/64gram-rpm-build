# 64gram-rpm-build

把 [64Gram](https://github.com/TDesktop-x64/tdesktop)（Telegram Desktop 的 64 位增强分支）官方 Linux 版本重新打包成 RPM，由 GitHub Actions 自动构建。

上游只发布 `64Gram_<ver>_linux.zip`（裸二进制），没有 deb/rpm，也**没有公开的源码构建通道**
（其 `centos_env` 镜像在 ghcr 上是私有的），所以这里采用发行版常见的 `-bin` 做法：
下载官方发布的二进制，补上桌面集成后打成 RPM。二进制本身把 Qt / OpenSSL / ffmpeg / WebRTC
都静态链进去了，动态依赖只有 15 个系统库（glibc、glib、cairo、pango、fontconfig、freetype），
因此在 RHEL/Rocky/Alma 8+ 与 Fedora 上都能直接装。

## 用现成的包

从 [Releases](../../releases) 下载后：

```bash
sudo dnf install ./64gram-<ver>-1.*.x86_64.rpm
```

装完在应用菜单里是 **64Gram**，命令行是 `64gram`，`tg://` 链接也会指向它。

卸载：

```bash
sudo dnf remove 64gram
```

## 自己触发一次构建

Actions → **Build 64Gram RPM** → *Run workflow*，`version` 填 `1.2.11` 或留 `latest`
（自动查上游最新 release）。

产物在 workflow 的 artifact 里；勾选 `publish`（默认开）会额外建一个 GitHub Release。
push `build-*` 形式的 tag 也会触发构建并发布。

## 包内容

| 路径 | 说明 |
| --- | --- |
| `/usr/bin/64gram` | 上游 `Telegram` 二进制 |
| `/usr/share/applications/64gram.desktop` | 菜单项，含 `tg://` / `tonsite://` 处理 |
| `/usr/share/icons/hicolor/{16,32,48,64,128,256,512}/apps/64gram.png` | 图标 |
| `/usr/share/licenses/64gram/LICENSE` | GPLv3 + OpenSSL 例外 |

## 已知取舍

- **不做 strip，也不打包 `Updater`**：保留二进制原样，自动更新在 `/usr/bin` 下本来就写不进去，
  升级请走 `dnf`。因此安装包偏大（约 90 MB），和上游 zip 一个量级。
- **包名与上游冲突面**：二进制叫 `64gram` 而不是 `telegram-desktop`，不会顶掉系统里的官方 Telegram。
  两者会话数据共用 `~/.local/share/TelegramDesktop`，同一时间只建议开一个。
- `Requires` 里显式写了 `libX11` / `libxcb` / `libxkbcommon`，这三个是 Qt 平台插件 dlopen 的，
  不会出现在 ELF 的 `NEEDED` 里；名字取的是 Fedora/RHEL 的包名，openSUSE 上可能需要 `--nodeps`。

## 仓库结构

```
.github/workflows/build-64gram-rpm.yml   # 下载上游 zip → fedora 容器里 rpmbuild → 发布
packaging/64gram.spec                    # RPM spec（版本用 --define "gver x.y.z" 覆盖）
packaging/64gram.desktop                 # 桌面入口（图标在构建时从上游拉取）

```

手动在本地复现：

```bash
# 需要 docker + fedora 镜像
mkdir -p stage dist
unzip -o -q 64Gram_1.2.11_linux.zip -d stage
curl -fLo stage/LICENSE https://raw.githubusercontent.com/TDesktop-x64/tdesktop/dev/LICENSE
cp packaging/64gram.desktop stage/
for sz in 16 32 48 64 128 256 512; do
  curl -fLo "stage/icon${sz}.png" "https://raw.githubusercontent.com/TDesktop-x64/tdesktop/dev/Telegram/Resources/art/icon${sz}.png"
done
tar -C stage -czf stage.tgz .

docker run --rm -u 0 -v "$PWD:/w" -w /w fedora:latest bash -lc '
  dnf -y -q install rpm-build
  mkdir -p /tmp/r/{SOURCES,SPECS,RPMS,BUILD,BUILDROOT}
  tar -C /tmp/r/SOURCES -xzf /w/stage.tgz
  rpmbuild -bb --define "_topdir /tmp/r" --define "gver 1.2.11" /w/packaging/64gram.spec
  cp /tmp/r/RPMS/x86_64/*.rpm /w/dist/'
```

## 许可

打包脚本随本仓库；64Gram 本体为 GPLv3 + OpenSSL 例外，版权归其作者。
本仓库与 64Gram 项目无关，只是第三方打包。
