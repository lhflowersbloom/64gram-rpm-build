%global debug_package %{nil}
%global __os_install_post %{nil}
%global _binary_payload w6.xzdio
%global _build_id_links none
%global _missing_build_ids_terminate_build 0

# Overridden by the workflow: rpmbuild --define "gver 1.2.11" --define "uver 7.3.5"
%{!?gver:%global gver 1.2.11}
%{!?uver:%global uver 7.3.5}

# XDG identity. The binary calls QGuiApplication::setDesktopFileName() with this
# exact string (Telegram/SourceFiles/platform/linux/specific_linux.cpp), so the
# desktop file, the D-Bus service and the AppStream id must all carry it or the
# shell cannot map the running window back to this entry.
%global appid io.github.tdesktop_x64.TDesktop

Name:       64gram
Version:    %{gver}
# Deliberately no dist tag: a single package serves RHEL/Alma/Rocky 8+, Fedora
# and openSUSE, so the release must not encode the build host.
Release:    2
Summary:    64Gram - unofficial Telegram Desktop build with extra features

License:    GPL-3.0-or-later with exceptions
URL:        https://github.com/TDesktop-x64/tdesktop
Source0:    Telegram
Source1:    LICENSE
Source2:    %{appid}.desktop
Source3:    %{appid}.service
Source4:    %{appid}.metainfo.xml
Source5:    icon16.png
Source6:    icon32.png
Source7:    icon48.png
Source8:    icon64.png
Source9:    icon128.png
Source10:   icon256.png
Source11:   icon512.png

# Prebuilt upstream binary, nothing is compiled here.
BuildArch:  x86_64

# Drop-in replacement for the official client: this package owns the tg://
# handler, so the two clients must not coexist (two entries claiming
# x-scheme-handler/tg would make the target of a tg:// click undefined).
Provides:   telegram-desktop = %{uver}
Obsoletes:  telegram-desktop <= %{uver}

# Runtime libraries the binary itself links against are picked up automatically
# from its ELF header. These three are dlopen()ed by the statically linked Qt
# platform plugin, so they never show up as NEEDED entries.
Requires:   libX11
Requires:   libxcb
Requires:   libxkbcommon

%description
64Gram is an unofficial fork of Telegram Desktop that ships a native x86_64
build with a number of extra options on top of the official client.

This package installs the Linux binary published by the 64Gram project and
registers it as the system handler for tg://, tonsite:// and ton:// links. It
is a repack of the upstream release, no source code is compiled here.

%prep
%build

%install
umask 022
install -d %{buildroot}%{_bindir} \
           %{buildroot}%{_datadir}/applications \
           %{buildroot}%{_datadir}/dbus-1/services \
           %{buildroot}%{_datadir}/metainfo \
           %{buildroot}%{_datadir}/licenses/%{name} \
           %{buildroot}%{_datadir}/icons/hicolor/{16x16,32x32,48x48,64x64,128x128,256x256,512x512}/apps

install -m 0755 %{SOURCE0} %{buildroot}%{_bindir}/64gram
ln -s 64gram %{buildroot}%{_bindir}/telegram-desktop

install -m 0644 %{SOURCE1} %{buildroot}%{_datadir}/licenses/%{name}/LICENSE
install -m 0644 %{SOURCE2} %{buildroot}%{_datadir}/applications/%{appid}.desktop
install -m 0644 %{SOURCE3} %{buildroot}%{_datadir}/dbus-1/services/%{appid}.service
install -m 0644 %{SOURCE4} %{buildroot}%{_datadir}/metainfo/%{appid}.metainfo.xml

install -m 0644 %{SOURCE5}  %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/64gram.png
install -m 0644 %{SOURCE6}  %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/64gram.png
install -m 0644 %{SOURCE7}  %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/64gram.png
install -m 0644 %{SOURCE8}  %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/64gram.png
install -m 0644 %{SOURCE9}  %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/64gram.png
install -m 0644 %{SOURCE10} %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/64gram.png
install -m 0644 %{SOURCE11} %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/64gram.png

# The tray icon and the PulseAudio stream are looked up by app id, not by the
# "64gram" icon name, so expose the two sizes under both names.
ln -s 64gram.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/%{appid}.png
ln -s 64gram.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/%{appid}.png

%post
[ -x /usr/bin/gtk-update-icon-cache ] && /usr/bin/gtk-update-icon-cache -q -t -f %{_datadir}/icons/hicolor 2>/dev/null || :
[ -x /usr/bin/update-desktop-database ] && /usr/bin/update-desktop-database -q %{_datadir}/applications 2>/dev/null || :

%postun
[ -x /usr/bin/gtk-update-icon-cache ] && /usr/bin/gtk-update-icon-cache -q -t -f %{_datadir}/icons/hicolor 2>/dev/null || :
[ -x /usr/bin/update-desktop-database ] && /usr/bin/update-desktop-database -q %{_datadir}/applications 2>/dev/null || :

%files
%license %{_datadir}/licenses/%{name}/LICENSE
%{_bindir}/64gram
%{_bindir}/telegram-desktop
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/dbus-1/services/%{appid}.service
%{_datadir}/metainfo/%{appid}.metainfo.xml
%{_datadir}/icons/hicolor/16x16/apps/64gram.png
%{_datadir}/icons/hicolor/32x32/apps/64gram.png
%{_datadir}/icons/hicolor/48x48/apps/64gram.png
%{_datadir}/icons/hicolor/64x64/apps/64gram.png
%{_datadir}/icons/hicolor/128x128/apps/64gram.png
%{_datadir}/icons/hicolor/256x256/apps/64gram.png
%{_datadir}/icons/hicolor/512x512/apps/64gram.png
%{_datadir}/icons/hicolor/256x256/apps/%{appid}.png
%{_datadir}/icons/hicolor/512x512/apps/%{appid}.png

%changelog
* Fri Nov 06 2026 CI <ci@localhost> - 1.2.11-2
- Register the real XDG app id (io.github.tdesktop_x64.TDesktop) so the shell
  can map the window to this entry; add D-Bus service and AppStream data.
- Declare the tg:// scheme handlers and take over telegram-desktop 7.3.5.

* Fri Nov 06 2026 CI <ci@localhost> - 1.2.11-1
- Repackage the upstream 64Gram 1.2.11 Linux release for RPM based systems.
