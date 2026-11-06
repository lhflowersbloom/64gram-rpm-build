# 64gram-rpm-build

给 [64Gram](https://github.com/TDesktop-x64/tdesktop)（Telegram Desktop 的非官方 64 位增强分支）做 RPM 包，由 GitHub Actions 自动构建。

定位是**替代官方 `telegram-desktop`**：装完之后系统里只有它这一个 Telegram 客户端，`tg://`、`tonsite://`、`ton://` 全部归它处理。

## 安装

从 [Releases](../../releases) 下最新的包：

```bash
sudo dnf install ./64gram-<ver>-2.*.x86_64.rpm
```

装完在应用菜单里叫 **64Gram**，命令是 `64gram`（另带 `/usr/bin/telegram-desktop` 软链，方便按文件名找客户端的脚本）。

已装官方 `telegram-desktop` 的话，`dnf install` 会把它替换掉（本包 `Obsoletes: telegram-desktop`），
这是刻意的——否则两个客户端都声明 `x-scheme-handler/tg`，点链接到底开谁就变成随机事件了。会话数据仍在
`~/.local/share/TelegramDesktop`，卸载后换回官方版不会丢。

上游发新版本后，本仓库每周一自动构建并发布对应的 RPM；升级时重新下载新包 `dnf install` 覆盖即可。

卸载：

```bash
sudo dnf remove 64gram
```

## 包内容

| 路径 | 说明 |
| --- | --- |
| `/usr/bin/64gram` | 上游 `Telegram` 二进制 |
| `/usr/bin/telegram-desktop` | 指向上面的软链，满足按文件名找客户端的脚本 |
| `/usr/share/applications/io.github.tdesktop_x64.TDesktop.desktop` | 菜单项 + `tg` / `tonsite` / `ton` scheme handler |
| `/usr/share/dbus-1/services/io.github.tdesktop_x64.TDesktop.service` | DBus 激活 |
| `/usr/share/metainfo/io.github.tdesktop_x64.TDesktop.metainfo.xml` | AppStream 数据 |
| `/usr/share/icons/hicolor/{16,32,48,64,128,256,512}/apps/` | 图标 |
| `/usr/share/licenses/64gram/LICENSE` | GPLv3 + OpenSSL 例外 |

## 仓库结构

```
.github/workflows/build-64gram-rpm.yml                    # 构建、冒烟测试、发布
packaging/64gram.spec                                     # RPM spec
packaging/io.github.tdesktop_x64.TDesktop.desktop         # 桌面入口
packaging/io.github.tdesktop_x64.TDesktop.service         # DBus 服务
packaging/io.github.tdesktop_x64.TDesktop.metainfo.xml    # AppStream 元数据
```

## 许可

打包脚本随本仓库；64Gram 本体为 GPLv3 + OpenSSL 例外，版权归其作者。
本仓库与 64Gram 项目无关，只是第三方打包。
