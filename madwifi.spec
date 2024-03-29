#
# TODO: kernel header is additional BR  (whatever it means???)
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)

#
%define		snap_year	2005
%define		snap_month	11
%define		snap_day	25
%define		snap	%{snap_year}%{snap_month}%{snap_day}
%define		snapdate	%{snap_year}-%{snap_month}-%{snap_day}
%define		_rel	0.%{snap}.2
Summary:	Atheros WiFi card driver
Summary(pl.UTF-8):	Sterownik karty radiowej Atheros
Name:		madwifi
Version:	0
Release:	%{_rel}
Epoch:		0
License:	GPL/BSD (partial source)
Group:		Base/Kernel
Source0:	http://madwifi.otaku42.de/%{snap_year}/%{snap_month}/%{name}-cvs-snapshot-%{snapdate}.tar.bz2
# Source0-md5:	edb2791b3c1df2cd5db57d6a52670d62
URL:		http://madwifi.sourceforge.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.308
BuildRequires:	sharutils
%endif
ExclusiveArch:	%{x8664} arm %{ix86} mips ppc xscale
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Atheros WiFi card driver.

%description -l pl.UTF-8
Sterownik karty radiowej Atheros.

%package devel
Summary:	Header files for madwifi
Summary(pl.UTF-8):	Pliki nagłówkowe dla madwifi
Group:		Development/Libraries

%description devel
Header files for madwifi.

%description devel -l pl.UTF-8
Pliki nagłówkowe dla madwifi.

# kernel subpackages.

%package -n kernel%{_alt_kernel}-net-madwifi
Summary:	Linux driver for Atheros cards
Summary(pl.UTF-8):	Sterownik dla Linuksa do kart Atheros
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel%{_alt_kernel}-net-madwifi
This is driver for Atheros card for Linux.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-net-madwifi -l pl.UTF-8
Sterownik dla Linuksa do kart Atheros.

Ten pakiet zawiera moduł jądra Linuksa.

%package -n kernel%{_alt_kernel}-smp-net-madwifi
Summary:	Linux SMP driver for %{name} cards
Summary(pl.UTF-8):	Sterownik dla Linuksa SMP do kart %{name}
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel%{_alt_kernel}-smp-net-madwifi
This is driver for Atheros cards for Linux.

This package contains Linux SMP module.

%description -n kernel%{_alt_kernel}-smp-net-madwifi -l pl.UTF-8
Sterownik dla Linuksa do kart Atheros.

Ten pakiet zawiera moduł jądra Linuksa SMP.

%prep
%setup -q -n %{name}

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
%ifarch ppc ppc64
        install -d include/asm
        [ ! -d %{_kernelsrcdir}/include/asm-powerpc ] || ln -sf %{_kernelsrcdir}/include/asm-powerpc/* include/asm
        [ ! -d %{_kernelsrcdir}/include/asm-%{_target_base_arch} ] || ln -snf %{_kernelsrcdir}/include/asm-%{_target_base_arch}/* include/asm
%else
        ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} o/include/asm
%endif
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
#
#	patching/creating makefile(s) (optional)
#
	%{__make} -j1 -C %{_kernelsrcdir} O=$PWD/o prepare scripts
	ln -sf ../Makefile.inc o/Makefile.inc
	%{__make} -C %{_kernelsrcdir} clean \
		KERNELCONF="%{_kernelsrcdir}/config-$cfg" \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD/o \
		KERNELPATH="%{_kernelsrcdir}" \
		%{?with_verbose:V=1}
	%{__make} \
		TARGET="%{_target_base_arch}-elf" \
		KERNELPATH=%{_kernelsrcdir} \
		KERNELCONF="%{_kernelsrcdir}/config-$cfg" \
		TOOLPREFIX= \
		O=$PWD/o \
		CC="%{__cc}" CPP="%{__cpp}" \
		KERNELRELEASE="%{_kernel_ver}" \
		%{?with_verbose:V=1}

	mv ath/ath_pci{,-$cfg}.ko
	mv ath_hal/ath_hal{,-$cfg}.ko
	mv ath_rate/sample/ath_rate_sample{,-$cfg}.ko
	for i in wlan_wep wlan_xauth wlan_acl wlan_ccmp wlan_tkip wlan; do
		mv net80211/$i{,-$cfg}.ko
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
	BINDIR=%{_bindir}

install -d $RPM_BUILD_ROOT%{_includedir}/madwifi/net80211
install -d $RPM_BUILD_ROOT%{_includedir}/madwifi/include/sys
install net80211/*.h $RPM_BUILD_ROOT%{_includedir}/madwifi/net80211
install include/*.h $RPM_BUILD_ROOT%{_includedir}/madwifi/include
install include/sys/*.h $RPM_BUILD_ROOT%{_includedir}/madwifi/include/sys
%endif

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/net
install ath/ath_pci-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ath_pci.ko
install ath_hal/ath_hal-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ath_hal.ko
install ath_rate/sample/ath_rate_sample-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ath_rate_sample.ko
for i in wlan_wep wlan_xauth wlan_acl wlan_ccmp wlan_tkip wlan; do
	install net80211/$i-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/$i.ko
done
%if %{with smp} && %{with dist_kernel}
install ath/ath_pci-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net/ath_pci.ko
install ath_hal/ath_hal-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net/ath_hal.ko
install ath_rate/sample/ath_rate_sample-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net/ath_rate_sample.ko
for i in wlan_wep wlan_xauth wlan_acl wlan_ccmp wlan_tkip wlan; do
	install net80211/$i-smp.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net/$i.ko
done
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-net-madwifi
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-net-madwifi
%depmod %{_kernel_ver}

%post	-n kernel%{_alt_kernel}-smp-net-madwifi
%depmod %{_kernel_ver}smp

%postun	-n kernel%{_alt_kernel}-smp-net-madwifi
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc COPYRIGHT README
%attr(755,root,root) %{_bindir}/80211*
%attr(755,root,root) %{_bindir}/ath*

%files devel
%defattr(644,root,root,755)
%{_includedir}/madwifi
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-madwifi
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/net/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-net-madwifi
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/net/*.ko*
%endif
%endif
