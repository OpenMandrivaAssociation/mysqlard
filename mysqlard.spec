Summary:	MySQL performance logging daemon
Name:		mysqlard
Version:	1.0.0
Release:	18
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


%changelog
* Thu Mar 17 2011 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-17mdv2011.0
+ Revision: 645844
- relink against libmysqlclient.so.18

* Sat Jan 01 2011 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-16mdv2011.0
+ Revision: 627261
- rebuilt against mysql-5.5.8 libs, again

* Thu Dec 30 2010 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-15mdv2011.0
+ Revision: 626543
- rebuilt against mysql-5.5.8 libs

* Thu Oct 21 2010 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.0.0-13mdv2011.0
+ Revision: 587174
- Do not add shebang in cron.d file
  CCBUG: 57855

* Sun Feb 21 2010 Guillaume Rousse <guillomovitch@mandriva.org> 1.0.0-12mdv2010.1
+ Revision: 509216
- no need to prevent initscript translation
- rely on filetrigger for reloading apache configuration begining with 2010.1, rpm-helper macros otherwise

* Thu Feb 18 2010 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-11mdv2010.1
+ Revision: 507491
- rebuild

* Mon Sep 14 2009 Thierry Vignaud <tv@mandriva.org> 1.0.0-10mdv2010.0
+ Revision: 440176
- rebuild

* Sat Dec 06 2008 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-9mdv2009.1
+ Revision: 311410
- fix deps
- spec file cleanup
- rebuilt against mysql-5.1.30 libs

* Tue Jun 17 2008 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-8mdv2009.0
+ Revision: 222499
- rebuilt against new rrdtool-devel

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas
    - %clean_menus and %%_postun_webapp must be in %%postun, not %%preun

  + Thierry Vignaud <tv@mandriva.org>
    - drop old menu
    - kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Tue Aug 07 2007 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-7mdv2008.0
+ Revision: 59816
- Import mysqlard



* Tue Aug 07 2007 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-7mdv2008.0
- use the www-browser command instead of constructed one
- xdg cleanups

* Mon Sep 04 2006 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-6mdv2007.0
- fix xdg menu

* Mon Sep 04 2006 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-5mdv2007.0
- rebuilt against MySQL-5.0.24a-1mdv2007.0 due to ABI changes

* Sun May 14 2006 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-4mdk
- fix a menuentry
- add mod_rewrite rules to enforce ssl connections
- fix deps

* Sat May 13 2006 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-3mdk
- fix a better initscript (P0)

* Fri May 05 2006 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-2mdk
- fix the cron syntax

* Wed May 03 2006 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-1mdk
- initial Mandriva package
