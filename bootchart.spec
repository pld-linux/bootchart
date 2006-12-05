Summary:	Boot Process Performance Visualization
Summary(pl):	Wizualizacja wydajno¶ci procesu startu systemu
Name:		bootchart
Version:	0.9
Release:	1
Epoch:		0
License:	GPL
Group:		Base
Source0:	http://dl.sourceforge.net/bootchart/%{name}-%{version}.tar.bz2
# Source0-md5:	4be91177d19069e21beeb106f2f77dff
URL:		http://www.bootchart.org/
BuildRequires:	ant
BuildRequires:	jakarta-commons-cli >= 0:1.0
BuildRequires:	jpackage-utils >= 0:1.5
Requires:	jakarta-commons-cli >= 0:1.0
Requires:	jpackage-utils >= 0:1.5
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define boottitle "Bootchart logging"

%description
A tool for performance analysis and visualization of the GNU/Linux
boot process. Resource utilization and process information are
collected during the boot process and are later rendered in a PNG, SVG
or EPS encoded chart.

%description -l pl
Narzêdzie do analizy i wizualizacji wydajno¶ci procesu startu systemu
GNU/Linux. Podczas startu systemu zbirane s± informacje o procesach i
wykorzystaniu zasobów, a nastêpnie s± przedstawiane w postaci wykresu
w formacie PNG, SVG lub EPS.

%package javadoc
Summary:	Javadoc for %{name}
Summary(pl):	Dokumentacja Javadoc dla bootcharta
Group:		Documentation

%description javadoc
Javadoc for %{name}.

%description javadoc -l pl
Dokumentacja Javadoc dla bootcharta.

%package logger
Summary:	Boot logging script for %{name}
Summary(pl):	Skrypt loguj±cy proces startu dla bootcharta
Group:		Base

%description logger
Boot logging script for %{name}.

%description logger -l pl
Skrypt loguj±cy proces startu dla bootcharta.

%prep
%setup -q

%build
# Remove the bundled commons-cli
rm -rf lib/org/apache/commons/cli lib/org/apache/commons/lang
CLASSPATH=%{_javadir}/commons-cli.jar ant

%install
rm -rf $RPM_BUILD_ROOT

# jar
install -D %{name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
ln -s %{name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}.jar

# script
install -D script/%{name} $RPM_BUILD_ROOT%{_bindir}/%{name}

# javadoc
install -d $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} # ghost symlink

# logger
install -D script/bootchartd $RPM_BUILD_ROOT/sbin/bootchartd
install -D script/bootchartd.conf $RPM_BUILD_ROOT%{_sysconfdir}/bootchartd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{version} %{_javadocdir}/%{name}

%postun javadoc
if [ "$1" = "0" ]; then
	rm -f %{_javadocdir}/%{name}
fi

%post logger
# Add a new grub/lilo entry
if [ -x /sbin/grubby ]; then
	kernel=$(/sbin/grubby --default-kernel)
	initrd=$(/sbin/grubby --info=$kernel | sed -n '/^initrd=/{s/^initrd=//;p;q;}')
	[ ! -z $initrd ] && initrd="--initrd=$initrd"
	/sbin/grubby --remove-kernel TITLE=%{boottitle}
	/sbin/grubby --copy-default --add-kernel=$kernel $initrd --args="init=/sbin/bootchartd" --title=%{boottitle}
fi

%preun logger
# Remove the grub/lilo entry
if [ -x /sbin/grubby ]; then
	/sbin/grubby --remove-kernel TITLE=%{boottitle}
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog COPYING INSTALL README TODO lib/LICENSE.cli.txt lib/LICENSE.compress.txt lib/LICENSE.epsgraphics.txt lib/NOTICE.txt
%{_javadir}/*
%dir %{_bindir}/bootchart

%files javadoc
%defattr(644,root,root,755)
%doc %{_javadocdir}/%{name}-%{version}
%ghost %doc %{_javadocdir}/%{name}

%files logger
%defattr(644,root,root,755)
%doc README.logger
%attr(755,root,root) /sbin/bootchartd
%config(noreplace) %{_sysconfdir}/bootchartd.conf
