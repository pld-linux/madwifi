#
# TODO: kernel header is additional BR  (whatever it means???)
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)

%define		snap_year	2006
%define		snap_month	03
%define		snap_day	04
%define		snap	%{snap_year}%{snap_month}%{snap_day}
%define		snapdate	%{snap_year}-%{snap_month}-%{snap_day}
%define		_release		1

#
Summary:	Atheros WiFi card driver
Summary(pl):	Sterownik karty radiowej Atheros
Name:		madwifi-ng
Version:	r1460
Release:	%{_release}
Epoch:		0
License:	GPL/BSD (partial source)
Group:		Base/Kernel
Source0:	http://snapshots.madwifi.org/%{name}/%{name}-%{version}-%{snap}.tar.gz
# Source0-md5:	51d5b9c718a78385f7f525a1ed0120e0
URL:		http://madwifi.sf.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.153
BuildRequires:	sharutils
%endif
ExclusiveArch:	%{x8664} arm %{ix86} mips ppc xscale
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Atheros WiFi card driver.

%description -l pl
Sterownik karty radiowej Atheros.

%package devel
Summary:	Header files for madwifi
Summary(pl):	Pliki nag³ówkowe dla madwifi
Group:		Development/Libraries

%description devel
Header files for madwifi.

%description devel -l pl
Pliki nag³ówkowe dla madwifi.

# kernel subpackages.

%package -n kernel-net-madwifi
Summary:	Linux driver for Atheros cards
Summary(pl):	Sterownik dla Linuksa do kart Atheros
Release:	%{_release}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel-net-madwifi
This is driver for Atheros card for Linux.

This package contains Linux module.

%description -n kernel-net-madwifi -l pl
Sterownik dla Linuksa do kart Atheros.

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel-smp-net-madwifi
Summary:	Linux SMP driver for %{name} cards
Summary(pl):	Sterownik dla Linuksa SMP do kart %{name}
Release:	%{_release}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel-smp-net-madwifi
This is driver for Atheros cards for Linux.

This package contains Linux SMP module.

%description -n kernel-smp-net-madwifi -l pl
Sterownik dla Linuksa do kart Atheros.

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%prep
%setup -q -n %{name}-%{version}-%{snap}

%build
%if %{with userspace}
%{__make} -C tools \
	CC="%{__cc}" \
	CFLAGS="-include include/compat.h -\$(INCS) %{rpmcflags}" \
	KERNELCONF="%{_kernelsrcdir}/config-up" \
	KERNELPATH="%{_kernelsrcdir}"
%endif

%if %{with kernel}
# kernel module(s)

for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf o/
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
	ln -sfn %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
%if %{with dist_kernel}
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif


#
#	patching/creating makefile(s) (optional)
#

       %{__make} -C %{_kernelsrcdir} clean \
                KERNELCONF="%{_kernelsrcdir}/config-$cfg" \
                RCS_FIND_IGNORE="-name '*.ko' -o" \
                M=$PWD O=$PWD \
                %{?with_verbose:V=1}

        %{__make} \
                TARGET="%{_target_base_arch}-elf" \
                KERNELPATH=%{_kernelsrcdir} \
                KERNELCONF="%{_kernelsrcdir}/config-$cfg" \
                TOOLPREFIX= \
                O=$PWD/o \
                CC="%{__cc}" CPP="%{__cpp}" \
                %{?with_verbose:V=1}



	for i in `find . -name "*.ko" ! -name "*-smp.ko" `; do
		mv $i `basename $i .ko`-$cfg.ko
	done
	
done
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_bindir}
install tools/80211debug $RPM_BUILD_ROOT%{_bindir}/80211debug
install tools/80211stats $RPM_BUILD_ROOT%{_bindir}/80211stats
install tools/athchans $RPM_BUILD_ROOT%{_bindir}/athchans
install tools/athctrl $RPM_BUILD_ROOT%{_bindir}/athctrl
install tools/athdebug $RPM_BUILD_ROOT%{_bindir}/athdebug
install tools/athkey $RPM_BUILD_ROOT%{_bindir}/athkey
install tools/athstats $RPM_BUILD_ROOT%{_bindir}/athstats

%{__make} -C tools install \
	KERNELCONF="%{_kernelsrcdir}/config-up" \
	KERNELPATH="%{_kernelsrcdir}" \
	DESTDIR=$RPM_BUILD_ROOT \
	BINDIR=%{_bindir} \
	MANDIR=%{_mandir}	

install -d $RPM_BUILD_ROOT%{_includedir}/madwifi/net80211
install -d $RPM_BUILD_ROOT%{_includedir}/madwifi/include/sys
install net80211/*.h $RPM_BUILD_ROOT%{_includedir}/madwifi/net80211
install include/*.h $RPM_BUILD_ROOT%{_includedir}/madwifi/include
install include/sys/*.h $RPM_BUILD_ROOT%{_includedir}/madwifi/include/sys
%endif

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net
for i in `find . -name "*-up.ko"`; do
	install $i $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/`basename $i -up.ko`.ko
done
%if %{with smp} && %{with dist_kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net
for i in `find . -name "*-smp.ko"`; do
	install $i $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net/`basename $i -smp.ko`.ko
done
%endif
%endif

%clean
# rm -rf $RPM_BUILD_ROOT

%post	-n kernel-net-madwifi
%depmod %{_kernel_ver}

%postun	-n kernel-net-madwifi
%depmod %{_kernel_ver}

%post	-n kernel-smp-net-madwifi
%depmod %{_kernel_ver}smp

%postun	-n kernel-smp-net-madwifi
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc COPYRIGHT README
%attr(755,root,root) %{_bindir}/80211*
%attr(755,root,root) %{_bindir}/ath*
%attr(755,root,root) %{_bindir}/wlan*
%{_mandir}/man8/*

%files devel
%defattr(644,root,root,755)
%{_includedir}/madwifi
%endif

%if %{with kernel}
%files -n kernel-net-madwifi
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/net/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-madwifi
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/net/*.ko*
%endif
%endif
