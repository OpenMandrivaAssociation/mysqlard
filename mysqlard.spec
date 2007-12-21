Summary:	MySQL performance logging daemon
Name:		mysqlard
Version:	1.0.0
Release:	%mkrel 7
Group:		System/Servers
License:	GPL
URL:		http://gert.sos.be/en/
Source0:	http://www.sos.be/projects/%{name}/dist/%{name}-%{version}.tar.bz2
Patch0:		mysqlard-1.0.0-mdv_conf.diff
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre):	apache-mod_php php-mysql
Requires:	apache-mod_php php-mysql
Requires:	mysql
Requires:	rrdtool
BuildRequires:	ImageMagick
BuildRequires:	apache-base >= 2.0.54
BuildRequires:	mysql-devel
BuildRequires:	rrdtool
BuildRequires:	librrdtool-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
mysqlard daemon collects MySQL(TM) performance data in a Round Robin Database.
The package also contains example graphing and php scripts.

%prep

%setup -q
%patch0 -p0

chmod 644 AUTHORS ChangeLog COPYING INSTALL NEWS README TODO

%build
%serverbuild

%configure2_5x \
    --sysconfdir=%{_sysconfdir}/%{name} \
    --localstatedir=/var/run/%{name} \
    --datadir=/var/lib

%make

%install
rm -rf %{buildroot}

# don't fiddle with the initscript!
export DONT_GPRINTIFY=1

%makeinstall_std

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}/%{name}
install -d %{buildroot}%{_sysconfdir}/cron.d
install -d %{buildroot}%{_sysconfdir}/cron.daily
install -d %{buildroot}%{_sysconfdir}/cron.weekly
install -d %{buildroot}%{_sysconfdir}/cron.monthly
install -d %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d
install -d %{buildroot}/var/lib/%{name}/archive
install -d %{buildroot}/var/run/%{name}

mv %{buildroot}/var/lib/%{name}/*.cnf %{buildroot}%{_sysconfdir}/%{name}/
mv %{buildroot}/var/lib/%{name}/*.server %{buildroot}%{_initrddir}/%{name}

mv %{buildroot}/var/lib/%{name}/mysqlar.daily %{buildroot}%{_sysconfdir}/cron.daily/%{name}

mv %{buildroot}/var/lib/%{name}/mysqlar.weekly %{buildroot}%{_sysconfdir}/cron.weekly/%{name}

mv %{buildroot}/var/lib/%{name}/mysqlar.monthly %{buildroot}%{_sysconfdir}/cron.monthly/%{name}

mv %{buildroot}/var/lib/%{name}/mysqlar.php %{buildroot}/var/lib/%{name}/index.php

cat > %{name}.crond << EOF
#!/bin/sh

*/5 * * * * root hourly=1 daily=1 weekly=1 monthly=1 %{_bindir}/mysqlar_graph > /dev/null
EOF

install -m0755 %{name}.crond %{buildroot}%{_sysconfdir}/cron.d/%{name}

cat > %{buildroot}/%{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf << EOF

Alias /%{name} /var/lib/%{name}

<Directory /var/lib/%{name}>
    Order Deny,Allow
    Deny from All
    Allow from 127.0.0.1
    ErrorDocument 403 "Access denied per %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf"
</Directory>

#<LocationMatch /%{name}>
#    Options FollowSymLinks
#    RewriteEngine on
#    RewriteCond %{SERVER_PORT} !^443$
#    RewriteRule ^.*$ https://%{SERVER_NAME}%{REQUEST_URI} [L,R]
#</LocationMatch>

EOF

# Mandriva Icons
install -d %{buildroot}%{_iconsdir}
install -d %{buildroot}%{_miconsdir}
install -d %{buildroot}%{_liconsdir}

convert src/mysql.gif -resize 16x16 %{buildroot}%{_miconsdir}/%{name}.png
convert src/mysql.gif -resize 32x32 %{buildroot}%{_iconsdir}/%{name}.png
convert src/mysql.gif -resize 48x48 %{buildroot}%{_liconsdir}/%{name}.png

# install menu entry.
install -d %{buildroot}%{_menudir}
cat > %{buildroot}%{_menudir}/%{name} << EOF
?package(%{name}): needs=X11 \
section="System/Monitoring" \
title="mysqlard" \
longtitle="mysqlard is a MySQL performance logging daemon." \
command="%{_bindir}/www-browser http://localhost/%{name}/" \
icon="%{name}.png" \
xdg=true
EOF

# XDG menu
install -d %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=mysqlard
Comment=%{summary}
Exec="%{_bindir}/www-browser http://localhost/%{name}/"
Icon=%{name}
Terminal=false
Type=Application
Categories=X-MandrivaLinux-MoreApplications-Databases;
EOF

%post
%_post_service %{name}
%_post_webapp
%update_menus

%preun
%_preun_service %{name}
%_postun_webapp
%clean_menus

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(0755,root,root)
%doc AUTHORS ChangeLog COPYING INSTALL NEWS README TODO
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/*.cnf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf
%attr(0755,root,root) %{_initrddir}/mysqlard
%attr(0755,root,root) %{_sysconfdir}/cron.d/%{name}
%attr(0755,root,root) %{_sysconfdir}/cron.daily/%{name}
%attr(0755,root,root) %{_sysconfdir}/cron.weekly/%{name}
%attr(0755,root,root) %{_sysconfdir}/cron.monthly/%{name}
%{_bindir}/*
%{_sbindir}/*
/var/lib/%{name}
%dir /var/run/%{name}
%{_mandir}/man1/*
%{_mandir}/man8/*
%{_menudir}/%{name}
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{_datadir}/applications/*.desktop