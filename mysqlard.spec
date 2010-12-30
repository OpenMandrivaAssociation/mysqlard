Summary:	MySQL performance logging daemon
Name:		mysqlard
Version:	1.0.0
Release:	%mkrel 15
Group:		System/Servers
License:	GPL
URL:		http://gert.sos.be/en/
Source0:	http://www.sos.be/projects/%{name}/dist/%{name}-%{version}.tar.bz2
Patch0:		mysqlard-1.0.0-mdv_conf.diff
Requires:	apache-mod_php
Requires:	php-mysql
Requires:	mysql
Requires:	rrdtool
Requires(post):   rpm-helper
Requires(preun):   rpm-helper
%if %mdkversion < 201010
Requires(postun):   rpm-helper
%endif
BuildRequires:	mysql-devel
BuildRequires:	rrdtool
BuildRequires:	rrdtool-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}

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
*/5 * * * * root hourly=1 daily=1 weekly=1 monthly=1 %{_bindir}/mysqlar_graph > /dev/null
EOF

install -m0755 %{name}.crond %{buildroot}%{_sysconfdir}/cron.d/%{name}

cat > %{buildroot}/%{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf << EOF

Alias /%{name} /var/lib/%{name}

<Directory /var/lib/%{name}>
    Order allow,deny
    Allow from all
</Directory>
EOF

%post
%_post_service %{name}
%if %mdkversion < 201010
%_post_webapp
%endif

%preun
%_preun_service %{name}

%postun
%if %mdkversion < 201010
%_postun_webapp
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog COPYING INSTALL NEWS README TODO
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/*.cnf
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf
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
