%global debug_package %{nil}
%global __os_install_post %{nil}
%global _binary_payload w6.xzdio
%global _build_id_links none
%global _missing_build_ids_terminate_build 0

# Overridden by the workflow: rpmbuild --define "gver 1.2.11"
%{!?gver:%global gver 1.2.11}

Name:       64gram
Version:    %{gver}
# Deliberately no %{?dist}: one package serves RHEL/Alma/Rocky 8+, Fedora and openSUSE.
Release:    1
Summary:    64Gram - unofficial Telegram Desktop build with extra features

License:    GPL-3.0-or-later with exceptions
URL:        https://github.com/TDesktop-x64/tdesktop
Source0:    Telegram
Source1:    LICENSE
Source2:    64gram.desktop
Source3:    icon16.png
Source4:    icon32.png
Source5:    icon48.png
Source6:    icon64.png
Source7:    icon128.png
Source8:    icon256.png
Source9:    icon512.png

# Prebuilt upstream binary, nothing is compiled here.
BuildArch:  x86_64

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
adds desktop integration (application menu entry, hicolor icons and the
tg:// URL handler). It is a repack of the upstream release, no source code
is compiled here.

%prep
%build

%install
umask 022
install -d %{buildroot}%{_bindir} \
           %{buildroot}%{_datadir}/applications \
           %{buildroot}%{_datadir}/licenses/%{name}

install -m 0755 %{SOURCE0} %{buildroot}%{_bindir}/64gram
install -m 0644 %{SOURCE1} %{buildroot}%{_datadir}/licenses/%{name}/LICENSE
install -m 0644 %{SOURCE2} %{buildroot}%{_datadir}/applications/64gram.desktop

install -d %{buildroot}%{_datadir}/icons/hicolor/{16x16,32x32,48x48,64x64,128x128,256x256,512x512}/apps
install -m 0644 %{SOURCE3}  %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/64gram.png
install -m 0644 %{SOURCE4}  %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/64gram.png
install -m 0644 %{SOURCE5}  %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/64gram.png
install -m 0644 %{SOURCE6}  %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/64gram.png
install -m 0644 %{SOURCE7}  %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/64gram.png
install -m 0644 %{SOURCE8}  %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/64gram.png
install -m 0644 %{SOURCE9}  %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/64gram.png

%post
[ -x /usr/bin/gtk-update-icon-cache ] && /usr/bin/gtk-update-icon-cache -q -t -f %{_datadir}/icons/hicolor 2>/dev/null || :
[ -x /usr/bin/update-desktop-database ] && /usr/bin/update-desktop-database -q %{_datadir}/applications 2>/dev/null || :

%postun
[ -x /usr/bin/gtk-update-icon-cache ] && /usr/bin/gtk-update-icon-cache -q -t -f %{_datadir}/icons/hicolor 2>/dev/null || :

%files
%license %{_datadir}/licenses/%{name}/LICENSE
%{_bindir}/64gram
%{_datadir}/applications/64gram.desktop
%{_datadir}/icons/hicolor/16x16/apps/64gram.png
%{_datadir}/icons/hicolor/32x32/apps/64gram.png
%{_datadir}/icons/hicolor/48x48/apps/64gram.png
%{_datadir}/icons/hicolor/64x64/apps/64gram.png
%{_datadir}/icons/hicolor/128x128/apps/64gram.png
%{_datadir}/icons/hicolor/256x256/apps/64gram.png
%{_datadir}/icons/hicolor/512x512/apps/64gram.png

%changelog
* Fri Nov 06 2026 CI <ci@localhost> - %{gver}-1
- Repackage the upstream 64Gram %{gver} Linux release for RPM based systems.
