%include	/usr/lib/rpm/macros.java
Summary:	Boot Process Performance Visualization
Summary(pl.UTF-8):	Wizualizacja wydajności procesu startu systemu
Name:		bootchart
Version:	0.9
Release:	4
License:	GPL v2
Group:		Base
Source0:	http://dl.sourceforge.net/bootchart/%{name}-%{version}.tar.bz2
# Source0-md5:	4be91177d19069e21beeb106f2f77dff
Patch0:		%{name}-bash.patch
Patch1:		%{name}-initscript.patch
Patch2:		errors-fd.patch
URL:		http://www.bootchart.org/
BuildRequires:	ant
BuildRequires:	java-commons-cli >= 0:1.0
BuildRequires:	jaxp_parser_impl
BuildRequires:	jdk
BuildRequires:	jpackage-utils >= 0:1.5
BuildRequires:	rpm-javaprov
BuildRequires:	rpmbuild(macros) >= 1.294
Requires:	java-commons-cli >= 0:1.0
Requires:	jpackage-utils >= 0:1.5
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		boottitle Bootchart logging

%description
A tool for performance analysis and visualization of the GNU/Linux
boot process. Resource utilization and process information are
collected during the boot process and are later rendered in a PNG, SVG
or EPS encoded chart.

%description -l pl.UTF-8
Narzędzie do analizy i wizualizacji wydajności procesu startu systemu
GNU/Linux. Podczas startu systemu zbirane są informacje o procesach i
wykorzystaniu zasobów, a następnie są przedstawiane w postaci wykresu
w formacie PNG, SVG lub EPS.

%package javadoc
Summary:	Javadoc for %{name}
Summary(pl.UTF-8):	Dokumentacja Javadoc dla bootcharta
Group:		Documentation
Requires:	jpackage-utils

%description javadoc
Javadoc for %{name}.

%description javadoc -l pl.UTF-8
Dokumentacja Javadoc dla bootcharta.

%package logger
Summary:	Boot logging script for %{name}
Summary(pl.UTF-8):	Skrypt logujący proces startu dla bootcharta
Group:		Base
Requires:	coreutils
Requires:	grep
Requires:	gzip
Requires:	mktemp
Requires:	mount
Requires:	sed
Requires:	tar

%description logger
Boot logging script for %{name}.

%description logger -l pl.UTF-8
Skrypt logujący proces startu dla bootcharta.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

# Remove the bundled commons-cli
rm -rf lib/org/apache/commons/cli lib/org/apache/commons/lang

%build
required_jars="commons-cli"
export CLASSPATH=$(build-classpath $required_jars)
%ant

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_javadir}

# jar
cp -a %{name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
ln -s %{name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}.jar

# script
install -p -D script/%{name} $RPM_BUILD_ROOT%{_bindir}/%{name}

# javadoc
install -d $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} # ghost symlink

# logger
install -p -D script/bootchartd $RPM_BUILD_ROOT/sbin/bootchartd
install -p -D script/bootchartd.conf $RPM_BUILD_ROOT%{_sysconfdir}/bootchartd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post javadoc
ln -nfs %{name}-%{version} %{_javadocdir}/%{name}

%post logger
# Add a new grub/lilo entry
if [ -x /sbin/grubby ]; then
	kernel=$(/sbin/grubby --default-kernel)
	info=$(/sbin/grubby --info=$kernel)
	initrd=$(echo "$info" | sed -n '/^initrd=/{s/^initrd=//;p;q;}')
	init=$(echo "$info" |sed -n '/^args=.*init=/{s/^args=.*init=//;s/"$//;p;q;}')
	[ -n "$initrd" ] && initrd="--initrd=$initrd"
	[ -n "$init" ] && init="bootchart_init=$init"
	/sbin/grubby --remove-kernel TITLE='%{boottitle}'
	/sbin/grubby --copy-default --add-kernel=$kernel $initrd --args="init=/sbin/bootchartd $init" --title='%{boottitle}' || :
else
	%banner -e %{name}-logger <<-EOF
You should adjust your bootloader to boot with
 init=/sbin/bootchartd
EOF
fi

%preun logger
if [ "$1" = 0 ]; then
	# Remove the grub/lilo entry
	if [ -x /sbin/grubby ]; then
		/sbin/grubby --remove-kernel TITLE='%{boottitle}' || :
	fi
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog COPYING INSTALL README TODO lib/LICENSE.cli.txt lib/LICENSE.compress.txt lib/LICENSE.epsgraphics.txt lib/NOTICE.txt
%attr(755,root,root) %{_bindir}/bootchart
%{_javadir}/*.jar

%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{name}-%{version}
%ghost %{_javadocdir}/%{name}

%files logger
%defattr(644,root,root,755)
%doc README.logger
%attr(755,root,root) /sbin/bootchartd
%config(noreplace) %{_sysconfdir}/bootchartd.conf
